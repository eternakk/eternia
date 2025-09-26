"""Helper utilities for authentication-related cryptography routines."""

from __future__ import annotations

import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_encryption_key(password: str, salt: bytes, *, length: int = 32) -> bytes:
    """Derive a Fernet-compatible key from the provided password and salt."""

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=390_000,
    )

    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

