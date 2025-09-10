from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
import bcrypt
import re

# ---- Password validation helpers (module-internal) ----
_SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;:,.<>?/")

def _has_min_length(pwd: str, min_len: int = 8) -> bool:
    return len(pwd) >= min_len

def _has_upper(pwd: str) -> bool:
    return any(c.isupper() for c in pwd)

def _has_lower(pwd: str) -> bool:
    return any(c.islower() for c in pwd)

def _has_digit(pwd: str) -> bool:
    return any(c.isdigit() for c in pwd)

def _has_special(pwd: str) -> bool:
    return any(c in _SPECIAL_CHARS for c in pwd)

def _validate_password_strength(pwd: str) -> str:
    """Common password strength validation used by create/update models.
    Returns the password if valid; raises ValueError otherwise.
    """
    if not _has_min_length(pwd):
        raise ValueError("Password must be at least 8 characters long")
    if not _has_upper(pwd):
        raise ValueError("Password must contain at least one uppercase letter")
    if not _has_lower(pwd):
        raise ValueError("Password must contain at least one lowercase letter")
    if not _has_digit(pwd):
        raise ValueError("Password must contain at least one number")
    if not _has_special(pwd):
        raise ValueError("Password must contain at least one special character")
    return pwd

# Define user roles
class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

# Define permission levels
class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

# Role to permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.ADMIN],
    UserRole.OPERATOR: [Permission.READ, Permission.WRITE, Permission.EXECUTE],
    UserRole.VIEWER: [Permission.READ],
}

# User model for database
class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username for the user")
    email: EmailStr = Field(..., description="Email address of the user")
    hashed_password: str = Field(..., description="Hashed password for the user")
    role: UserRole = Field(default=UserRole.VIEWER, description="Role of the user")
    is_active: bool = Field(default=True, description="Whether the user is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the user was created")
    last_login: Optional[datetime] = Field(default=None, description="When the user last logged in")

    @field_validator("username")
    def validate_username(cls, v):
        """Validate that the username contains only allowed characters."""
        if not re.fullmatch(r"[A-Za-z0-9_-]+", v):
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        return v

    @field_validator("hashed_password")
    def validate_hashed_password(cls, v):
        """Validate that the hashed password is in the correct format."""
        if not v.startswith("$2b$") and not v.startswith("$2a$"):
            raise ValueError("Invalid hashed password format")
        return v

    @classmethod
    def create(cls, username: str, email: EmailStr, password: str, role: UserRole = UserRole.VIEWER) -> 'User':
        """Create a new user with a hashed password."""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return cls(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )

    def verify_password(self, password: str) -> bool:
        """Verify a password against the hashed password."""
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

    def has_permission(self, permission: Permission) -> bool:
        """Check if the user has a specific permission based on their role."""
        return permission in ROLE_PERMISSIONS.get(self.role, [])

# Token models
class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of token")
    expires_at: datetime = Field(..., description="Expiration time of the token")

    @field_validator("token_type")
    def validate_token_type(cls, v):
        """Validate that the token type is 'bearer'."""
        if v.lower() != "bearer":
            raise ValueError("Token type must be 'bearer'")
        return v.lower()

    @field_validator("access_token")
    def validate_access_token(cls, v):
        """Validate that the access token is not empty."""
        if not v or len(v) < 10:  # Arbitrary minimum length for a JWT token
            raise ValueError("Access token must be a valid JWT token")
        return v

class TokenData(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username of the token owner")
    role: UserRole = Field(..., description="Role of the token owner")
    exp: datetime = Field(..., description="Expiration time of the token")

    @field_validator("exp")
    def validate_expiration(cls, v):
        """Validate that the expiration time is in the future."""
        if v < datetime.utcnow():
            raise ValueError("Token has expired")
        return v

# User creation and update models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username for the new user")
    email: EmailStr = Field(..., description="Email address of the new user")
    password: str = Field(..., min_length=8, description="Password for the new user")
    role: UserRole = Field(default=UserRole.VIEWER, description="Role of the new user")

    @field_validator("username")
    def validate_username(cls, v):
        """Validate that the username contains only allowed characters."""
        if not re.fullmatch(r"[A-Za-z0-9_-]+", v):
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        return v

    @field_validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        return _validate_password_strength(v)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(default=None, description="New email address")
    password: Optional[str] = Field(default=None, min_length=8, description="New password")
    role: Optional[UserRole] = Field(default=None, description="New role")
    is_active: Optional[bool] = Field(default=None, description="New active status")

    @field_validator('password')
    def password_strength(cls, v):
        """Validate password strength if provided."""
        if v is None:
            return v
        return _validate_password_strength(v)

# User response model (without sensitive data)
class UserResponse(BaseModel):
    username: str = Field(..., description="Username of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    role: UserRole = Field(..., description="Role of the user")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime = Field(..., description="When the user was created")
    last_login: Optional[datetime] = Field(default=None, description="When the user last logged in")

    @field_validator("created_at")
    def validate_created_at(cls, v):
        """Validate that the creation time is not in the future."""
        if v > datetime.utcnow():
            raise ValueError("Creation time cannot be in the future")
        return v

    @field_validator("last_login")
    def validate_last_login(cls, v):
        """Validate that the last login time is not in the future if provided."""
        if v is not None and v > datetime.utcnow():
            raise ValueError("Last login time cannot be in the future")
        return v
