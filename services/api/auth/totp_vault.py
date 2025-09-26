"""Encrypted storage and helpers for TOTP-based two-factor secrets."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional

from cryptography.fernet import Fernet, InvalidToken
import pyotp

from .crypto_utils import derive_encryption_key


VAULT_DIR = Path("artifacts/vault")
SECRET_FILE = VAULT_DIR / "totp_secrets.json.enc"
SALT_FILE = VAULT_DIR / "totp_salt.bin"
DEV_KEY_FILE = VAULT_DIR / "totp_dev.key"
DEFAULT_ISSUER = "Eternia Mission-Control"
ROTATION_GRACE = timedelta(minutes=5)


@dataclass
class TotpStatus:
    enabled: bool
    status: str
    version: int
    pending: bool
    last_verified_at: Optional[str]
    created_at: Optional[str]
    issuer: str


class TotpVault:
    """Persist TOTP secrets encrypted-at-rest with optional rotation support."""

    def __init__(self) -> None:
        self._fernet = self._init_fernet()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def start_enrollment(self, username: str, *, issuer: str = DEFAULT_ISSUER) -> Dict[str, str]:
        """Generate a new secret and mark enrollment as pending."""

        now = self._now()
        secret = pyotp.random_base32()

        store = self._load_store()
        existing = store.get(username)
        version = (existing or {}).get("version", 0) + 1

        entry = {
            "secret": secret,
            "status": "pending",
            "version": version,
            "created_at": now,
            "updated_at": now,
            "last_verified_at": None,
            "issuer": issuer,
            "previous_secret": None,
            "previous_secret_valid_until": None,
        }

        if existing and existing.get("secret"):
            entry["previous_secret"] = existing.get("secret")
            entry["previous_secret_valid_until"] = self._to_iso(
                self._parse_iso(now) + ROTATION_GRACE
            )

        store[username] = entry
        self._write_store(store)

        totp = pyotp.TOTP(secret)
        return {
            "secret": secret,
            "version": str(version),
            "otpauth_url": totp.provisioning_uri(name=username, issuer_name=issuer),
        }

    def verify_and_activate(self, username: str, code: str) -> Optional[int]:
        """Validate a code for enrollment and activate the secret on success."""

        code_norm = self._normalize_code(code)
        if not code_norm:
            return None

        store = self._load_store()
        entry = store.get(username)
        if not entry:
            return None

        if not self._validate_with_entry(entry, code_norm):
            return None

        now = self._now()
        entry["status"] = "active"
        entry["updated_at"] = now
        entry["last_verified_at"] = now
        entry["previous_secret"] = None
        entry["previous_secret_valid_until"] = None

        store[username] = entry
        self._write_store(store)
        return int(entry.get("version", 1))

    def validate(self, username: str, code: str) -> bool:
        """Validate a code for an already-active enrollment."""

        code_norm = self._normalize_code(code)
        if not code_norm:
            return False

        entry = self._load_store().get(username)
        if not entry or entry.get("status") != "active":
            return False

        if not self._validate_with_entry(entry, code_norm):
            return False

        entry["last_verified_at"] = self._now()
        self._update_entry(username, entry)
        return True

    def disable(self, username: str) -> bool:
        """Disable two-factor auth for the user by removing any stored secrets."""

        store = self._load_store()
        if username not in store:
            return False

        del store[username]
        self._write_store(store)
        return True

    def status(self, username: str) -> TotpStatus:
        entry = self._load_store().get(username, {})
        status = entry.get("status", "disabled")
        enabled = status == "active"
        pending = status == "pending"
        return TotpStatus(
            enabled=enabled,
            status=status,
            version=int(entry.get("version", 0)),
            pending=pending,
            last_verified_at=entry.get("last_verified_at"),
            created_at=entry.get("created_at"),
            issuer=entry.get("issuer", DEFAULT_ISSUER),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _update_entry(self, username: str, entry: Dict[str, object]) -> None:
        store = self._load_store()
        store[username] = entry
        self._write_store(store)

    def _validate_with_entry(self, entry: Dict[str, object], code: str) -> bool:
        secret = entry.get("secret")
        if not isinstance(secret, str):
            return False

        totp = pyotp.TOTP(secret)
        if totp.verify(code, valid_window=1):
            return True

        # Allow recently rotated secret during grace period
        previous_secret = entry.get("previous_secret")
        expires_at = entry.get("previous_secret_valid_until")
        if previous_secret and expires_at:
            try:
                if self._parse_iso(expires_at) >= datetime.now(timezone.utc):
                    legacy_totp = pyotp.TOTP(previous_secret)
                    return legacy_totp.verify(code, valid_window=0)
            except ValueError:
                return False

        return False

    def _normalize_code(self, code: str | None) -> Optional[str]:
        if not code:
            return None
        trimmed = code.strip().replace(" ", "")
        return trimmed if trimmed.isdigit() and 5 <= len(trimmed) <= 8 else None

    def _load_store(self) -> Dict[str, Dict[str, object]]:
        if not SECRET_FILE.exists():
            return {}

        try:
            data = SECRET_FILE.read_bytes()
            decoded = self._fernet.decrypt(data)
            payload = json.loads(decoded.decode("utf-8"))
            if not isinstance(payload, dict):
                return {}
            return payload.get("users", {})
        except (InvalidToken, ValueError, json.JSONDecodeError):
            return {}

    def _write_store(self, store: Dict[str, Dict[str, object]]) -> None:
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"users": store}, separators=(",", ":"))
        encrypted = self._fernet.encrypt(payload.encode("utf-8"))

        temp = SECRET_FILE.with_suffix(".tmp")
        temp.write_bytes(encrypted)
        temp.replace(SECRET_FILE)

    def _init_fernet(self) -> Fernet:
        VAULT_DIR.mkdir(parents=True, exist_ok=True)

        password = os.getenv("TOTP_VAULT_PASSWORD") or os.getenv("SECRET_KEY_ENCRYPTION_PASSWORD")

        if password:
            if not SALT_FILE.exists():
                SALT_FILE.write_bytes(os.urandom(16))
            salt = SALT_FILE.read_bytes()
            key = derive_encryption_key(password, salt)
            return Fernet(key)

        if DEV_KEY_FILE.exists():
            key = DEV_KEY_FILE.read_bytes()
        else:
            key = Fernet.generate_key()
            DEV_KEY_FILE.write_bytes(key)

        return Fernet(key)

    @staticmethod
    def _now() -> str:
        return TotpVault._to_iso(datetime.now(timezone.utc))

    @staticmethod
    def _parse_iso(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def _to_iso(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


totp_vault = TotpVault()
