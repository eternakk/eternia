from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, validator
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

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
    username: str
    email: EmailStr
    hashed_password: str
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

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
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class TokenData(BaseModel):
    username: str
    role: UserRole
    exp: datetime

# User creation and update models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.VIEWER

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength if provided."""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v

# User response model (without sensitive data)
class UserResponse(BaseModel):
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]