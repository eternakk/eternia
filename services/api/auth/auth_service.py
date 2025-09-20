import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import base64
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .models import User, UserRole, Permission, Token, TokenData, UserCreate, UserUpdate, UserResponse

# Configure logging
logger = logging.getLogger(__name__)

# Constants
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
USERS_FILE = Path("artifacts/users.json")

# Helpers for secret key encryption
def derive_encryption_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# Environment and secret configuration
ENV = (os.getenv("ETERNIA_ENV") or os.getenv("APP_ENV") or "development").lower()
IS_PROD = ENV in ("prod", "production")

# Support both names for backward compatibility
SECRET_KEY_ENV = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET")

# Files for secrets
SECRET_KEY_FILE = Path("artifacts/jwt_secret.txt")            # Encrypted (prod)
SECRET_KEY_SALT_FILE = Path("artifacts/jwt_secret_salt.bin")  # Salt for encryption (prod)
DEV_SECRET_KEY_FILE = Path("artifacts/dev.jwt_secret.txt")    # Plaintext (dev)

# Optional encryption password (required in prod when not using env secret)
SECRET_KEY_ENCRYPTION_PASSWORD = os.getenv("SECRET_KEY_ENCRYPTION_PASSWORD")

SECRET_KEY = None

if SECRET_KEY_ENV:
    # Highest priority: explicit env var
    SECRET_KEY = SECRET_KEY_ENV
    logger.info("Using JWT secret from environment variable.")
else:
    if not IS_PROD:
        # Development mode: prefer local file. If an encryption password is supplied, allow testing the encrypted flow.
        if SECRET_KEY_ENCRYPTION_PASSWORD:
            # Use encrypted storage even in dev if password provided
            if SECRET_KEY_SALT_FILE.exists():
                with open(SECRET_KEY_SALT_FILE, "rb") as f:
                    salt = f.read()
            else:
                salt = os.urandom(16)
                SECRET_KEY_SALT_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(SECRET_KEY_SALT_FILE, "wb") as f:
                    f.write(salt)
            fernet_key = derive_encryption_key(SECRET_KEY_ENCRYPTION_PASSWORD, salt)
            fernet = Fernet(fernet_key)

            if SECRET_KEY_FILE.exists():
                try:
                    with open(SECRET_KEY_FILE, 'rb') as f:
                        encrypted = f.read()
                        SECRET_KEY = fernet.decrypt(encrypted).decode()
                    logger.info("Using encrypted JWT secret from artifacts/jwt_secret.txt (dev mode).")
                except Exception as e:
                    logger.error(f"Error decrypting JWT secret (dev mode). Generating new. Details: {e}")
                    SECRET_KEY = os.urandom(32).hex()
                    try:
                        SECRET_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
                        encrypted = fernet.encrypt(SECRET_KEY.encode())
                        with open(SECRET_KEY_FILE, 'wb') as f:
                            f.write(encrypted)
                    except Exception as save_e:
                        logger.error(f"Error saving encrypted JWT secret (dev mode): {save_e}")
            else:
                SECRET_KEY = os.urandom(32).hex()
                try:
                    SECRET_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
                    encrypted = fernet.encrypt(SECRET_KEY.encode())
                    with open(SECRET_KEY_FILE, 'wb') as f:
                        f.write(encrypted)
                    logger.info("Created encrypted JWT secret at artifacts/jwt_secret.txt (dev mode).")
                except Exception as e:
                    logger.error(f"Error saving encrypted JWT secret (dev mode): {e}")
        else:
            # Default dev behavior: use a local plaintext file to persist the secret
            try:
                if DEV_SECRET_KEY_FILE.exists():
                    SECRET_KEY = DEV_SECRET_KEY_FILE.read_text(encoding='utf-8').strip()
                    if not SECRET_KEY:
                        raise ValueError("Empty dev secret file")
                    logger.info("Using JWT secret from artifacts/dev.jwt_secret.txt (development).")
                else:
                    SECRET_KEY = os.urandom(32).hex()
                    DEV_SECRET_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
                    DEV_SECRET_KEY_FILE.write_text(SECRET_KEY, encoding='utf-8')
                    logger.info("Created development JWT secret at artifacts/dev.jwt_secret.txt.")
            except Exception as e:
                logger.error(f"Error handling development JWT secret file: {e}")
                # Fallback (dev only): still generate ephemeral in-memory key to avoid blocking
                SECRET_KEY = os.urandom(32).hex()
                logger.warning("Falling back to ephemeral in-memory JWT secret (development).")
    else:
        # Production mode: no ephemeral fallback. Require env secret or encrypted storage with password.
        if not SECRET_KEY_ENCRYPTION_PASSWORD:
            raise RuntimeError(
                "Production requires a JWT secret via JWT_SECRET/JWT_SECRET_KEY env var or set "
                "SECRET_KEY_ENCRYPTION_PASSWORD to manage an encrypted secret file in artifacts/."
            )
        # Load or create salt
        if SECRET_KEY_SALT_FILE.exists():
            with open(SECRET_KEY_SALT_FILE, "rb") as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            SECRET_KEY_SALT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SECRET_KEY_SALT_FILE, "wb") as f:
                f.write(salt)
        fernet_key = derive_encryption_key(SECRET_KEY_ENCRYPTION_PASSWORD, salt)
        fernet = Fernet(fernet_key)

        if SECRET_KEY_FILE.exists():
            try:
                with open(SECRET_KEY_FILE, 'rb') as f:
                    encrypted = f.read()
                    SECRET_KEY = fernet.decrypt(encrypted).decode()
                logger.info("Using encrypted JWT secret from artifacts/jwt_secret.txt (production).")
            except Exception as e:
                raise RuntimeError(f"Failed to decrypt production JWT secret. Ensure the correct SECRET_KEY_ENCRYPTION_PASSWORD is set. Details: {e}")
        else:
            # Create a new secure secret and save it encrypted
            SECRET_KEY = os.urandom(32).hex()
            try:
                SECRET_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
                encrypted = fernet.encrypt(SECRET_KEY.encode())
                with open(SECRET_KEY_FILE, 'wb') as f:
                    f.write(encrypted)
                logger.info("Created encrypted JWT secret at artifacts/jwt_secret.txt (production). Keep your password safe.")
            except Exception as e:
                raise RuntimeError(f"Error saving encrypted production JWT secret: {e}")

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Optional multi-key rotation support
JWT_KEYSET_RAW = os.getenv("JWT_KEYSET")  # JSON mapping of {kid: secret}
ACTIVE_KID_ENV = os.getenv("JWT_ACTIVE_KID")
KEYSET: Optional[Dict[str, str]] = None
if JWT_KEYSET_RAW:
    try:
        parsed = json.loads(JWT_KEYSET_RAW)
        if isinstance(parsed, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in parsed.items()):
            KEYSET = parsed
            logger.info(f"JWT keyset loaded with {len(KEYSET)} keys. Active kid: {ACTIVE_KID_ENV or 'auto'}")
        else:
            logger.error("JWT_KEYSET must be a JSON object mapping kid->secret strings. Ignoring.")
    except Exception as e:
        logger.error(f"Failed to parse JWT_KEYSET: {e}")

REVOCATIONS_FILE = Path("artifacts/jwt_revocations.json")

class RevocationStore:
    def __init__(self, path: Path):
        self.path = path
        self.revoked: Dict[str, int] = {}
        self._load()

    def _load(self) -> None:
        try:
            if self.path.exists():
                data = json.loads(self.path.read_text(encoding='utf-8'))
                if isinstance(data, dict):
                    # expect {jti: exp_ts}
                    self.revoked = {str(k): int(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Failed to load revocations: {e}")

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.revoked), encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to save revocations: {e}")

    def prune(self, now_ts: Optional[int] = None) -> None:
        now = now_ts or int(datetime.utcnow().timestamp())
        removed = [jti for jti, exp in self.revoked.items() if exp <= now]
        if removed:
            for j in removed:
                self.revoked.pop(j, None)
            self._save()

    def revoke(self, jti: str, exp_ts: int) -> None:
        self.prune()
        self.revoked[jti] = exp_ts
        self._save()

    def is_revoked(self, jti: Optional[str]) -> bool:
        if not jti:
            return False
        self.prune()
        return jti in self.revoked

revocations = RevocationStore(REVOCATIONS_FILE)

# In-memory user store (will be loaded from file)
users: Dict[str, User] = {}

def load_users():
    """Load users from the JSON file."""
    global users
    if not USERS_FILE.exists():
        # Create default admin user if no users file exists
        admin_user = User.create(
            username="admin",
            email="admin@example.com",
            password="Admin123!",  # This should be changed after first login
            role=UserRole.ADMIN
        )
        users = {"admin": admin_user}
        save_users()
        logger.info("Created default admin user")
        return

    try:
        with open(USERS_FILE, 'r') as f:
            user_data = json.load(f)
            users = {username: User(**data) for username, data in user_data.items()}
        logger.info(f"Loaded {len(users)} users from file")
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        # Create default admin user if loading fails
        admin_user = User.create(
            username="admin",
            email="admin@example.com",
            password="Admin123!",  # This should be changed after first login
            role=UserRole.ADMIN
        )
        users = {"admin": admin_user}
        save_users()
        logger.info("Created default admin user after error")

def save_users():
    """Save users to the JSON file."""
    try:
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Write to a temporary file first, then rename to ensure atomic write
        temp_file = USERS_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            # Convert User objects to dictionaries
            user_dict = {username: user.model_dump() for username, user in users.items()}
            json.dump(user_dict, f, default=str)  # Use default=str to handle datetime objects

        # Rename the temporary file to the actual file
        temp_file.replace(USERS_FILE)
        logger.info(f"Saved {len(users)} users to file")
    except Exception as e:
        logger.error(f"Error saving users: {e}")


def _get_signing_key_and_headers() -> Tuple[str, Dict[str, str]]:
    """Return the signing key and headers for JWT creation, supporting key rotation."""
    if KEYSET:
        # choose active kid
        kid = ACTIVE_KID_ENV or (sorted(KEYSET.keys())[0])
        key = KEYSET.get(kid)
        if not key:
            # fallback to first key in keyset
            kid, key = next(iter(KEYSET.items()))
        return key, {"kid": kid}
    return SECRET_KEY, {}


def _iter_verification_keys(preferred_kid: Optional[str]) -> List[Tuple[Optional[str], str]]:
    """Yield (kid, key) pairs to attempt verification with, preferring the provided kid."""
    tried = set()
    if KEYSET:
        if preferred_kid and preferred_kid in KEYSET:
            yield preferred_kid, KEYSET[preferred_kid]
            tried.add(preferred_kid)
        for k, v in KEYSET.items():
            if k not in tried:
                yield k, v
    # Always include legacy single SECRET_KEY as fallback
    if SECRET_KEY and (not KEYSET or SECRET_KEY not in KEYSET.values()):
        yield None, SECRET_KEY

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # Ensure standard claims
    to_encode.update({
        "exp": expire,
        "iat": int(now.timestamp()),
        "jti": to_encode.get("jti") or uuid.uuid4().hex,
    })
    key, headers = _get_signing_key_and_headers()
    encoded_jwt = jwt.encode(to_encode, key, algorithm=ALGORITHM, headers=headers)
    return encoded_jwt

def _decode_jwt(token: str) -> Dict:
    try:
        logger.info("Attempting to decode JWT token")
        try:
            header = jwt.get_unverified_header(token)
            preferred_kid = header.get("kid")
        except Exception:
            preferred_kid = None
        last_err: Optional[Exception] = None
        for kid, key in _iter_verification_keys(preferred_kid):
            try:
                return jwt.decode(token, key, algorithms=[ALGORITHM])
            except InvalidTokenError as e:
                last_err = e
                continue
        # If we reach here, all attempts failed
        raise last_err or InvalidTokenError("Invalid token")
    except InvalidTokenError as e:
        logger.warning(f"JWT token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _extract_claims(payload: Dict) -> tuple[str, str, int]:
    username: Optional[str] = payload.get("sub")
    role: Optional[str] = payload.get("role")
    exp: Optional[int] = payload.get("exp")
    logger.info(f"JWT token claims - username: {username}, role: {role}, exp: {exp}")
    if not username or not role or exp is None:
        logger.warning(
            f"Invalid JWT token claims - username: {username}, role: {role}, exp: {exp}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username, role, exp


def _ensure_not_expired(exp: int) -> datetime:
    exp_datetime = datetime.fromtimestamp(exp)
    now = datetime.utcnow()
    if exp_datetime < now:
        logger.warning(f"JWT token expired at {exp_datetime}, current time: {now}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"JWT token valid until {exp_datetime}")
    return exp_datetime


def verify_token(token: str) -> TokenData:
    """
    Verify a JWT token and return the token data.

    Args:
        token: The JWT token to verify

    Returns:
        The decoded token data

    Raises:
        HTTPException: If the token is invalid
    """
    token_preview = token[:5] + "..." if len(token) > 10 else "***"
    logger.info(f"Verifying JWT token: {token_preview}")

    payload = _decode_jwt(token)
    # Revocation check (if jti present)
    jti = payload.get("jti")
    if revocations.is_revoked(jti):
        logger.warning(f"JWT token revoked (jti={jti})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username, role, exp = _extract_claims(payload)
    exp_datetime = _ensure_not_expired(exp)
    return TokenData(username=username, role=UserRole(role), exp=exp_datetime)

# ---- Revocation helper functions ----

def revoke_token(token: str) -> None:
    """Revoke a JWT by parsing its jti and exp and storing it in the revocation list."""
    payload = _decode_jwt(token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has no jti to revoke")
    if exp is None:
        # Default to 24h if no exp found (should not happen for our tokens)
        exp_ts = int(datetime.utcnow().timestamp()) + 86400
    else:
        # exp might be numeric timestamp or datetime; normalize to int timestamp
        if isinstance(exp, (int, float)):
            exp_ts = int(exp)
        else:
            try:
                exp_ts = int(datetime.fromtimestamp(exp).timestamp())
            except Exception:
                exp_ts = int(datetime.utcnow().timestamp()) + 86400
    revocations.revoke(jti, exp_ts)


def revoke_jti(jti: str, exp_ts: Optional[int] = None) -> None:
    """Revoke a token by JTI until its expiration timestamp (or 24h by default)."""
    if not exp_ts:
        exp_ts = int(datetime.utcnow().timestamp()) + 86400
    revocations.revoke(jti, exp_ts)


def is_token_revoked(token: str) -> bool:
    payload = _decode_jwt(token)
    return revocations.is_revoked(payload.get("jti"))

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the token.

    Args:
        token: The JWT token

    Returns:
        The current user

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    logger.info("Getting current user from token")
    try:
        token_data = verify_token(token)
        logger.info(f"Token verified for username: {token_data.username}")

        user = users.get(token_data.username)
        if user is None:
            logger.warning(f"User not found: {token_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"User found: {user.username}, active: {user.is_active}")

        if not user.is_active:
            logger.warning(f"Inactive user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login time
        user.last_login = datetime.utcnow()
        logger.info(f"User {user.username} authenticated successfully, last login updated: {user.last_login}")

        return user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication",
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.

    Args:
        current_user: The current user

    Returns:
        The current active user

    Raises:
        HTTPException: If the user is inactive
    """
    logger.info(f"Verifying active status for user: {current_user.username}")

    if not current_user.is_active:
        logger.warning(f"User {current_user.username} is inactive")
        raise HTTPException(status_code=400, detail="Inactive user")

    logger.info(f"User {current_user.username} is active and authenticated")
    return current_user

def check_permission(permission: Permission):
    """
    Dependency to check if a user has a specific permission.

    Args:
        permission: The permission to check

    Returns:
        A dependency function that checks the permission
    """
    async def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. {permission} required.",
            )
        return current_user
    return permission_checker

# User management functions
def get_user(username: str) -> Optional[User]:
    """Get a user by username."""
    return users.get(username)

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password."""
    user = get_user(username)
    if not user:
        return None
    if not user.verify_password(password):
        return None
    return user

def create_user(user_create: UserCreate) -> User:
    """Create a new user."""
    if user_create.username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = User.create(
        username=user_create.username,
        email=user_create.email,
        password=user_create.password,
        role=user_create.role
    )
    users[user.username] = user
    save_users()
    return user

def update_user(username: str, user_update: UserUpdate) -> User:
    """Update an existing user."""
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update user fields
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = User.create(
            username="", email="temp@example.com", password=user_update.password
        ).hashed_password
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    users[username] = user
    save_users()
    return user

def delete_user(username: str) -> bool:
    """Delete a user."""
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    del users[username]
    save_users()
    return True

def get_all_users() -> List[UserResponse]:
    """Get all users."""
    return [
        UserResponse(
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        for user in users.values()
    ]

# Load users on module import
load_users()
