from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status

from services.api.deps import api_interface

from .models import (
    User,
    UserRole,
    Permission,
    Token,
    UserCreate,
    UserUpdate,
    UserResponse,
    TwoFactorSetupResponse,
    TwoFactorCodeRequest,
    TwoFactorStatusResponse,
)
from .auth_service import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    create_user,
    update_user,
    delete_user,
    get_all_users,
    check_permission,
    start_two_factor_enrollment,
    verify_two_factor_code,
    validate_two_factor_code,
    disable_two_factor,
    get_two_factor_status,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# Create router
router = APIRouter(tags=["auth"])


class OAuth2PasswordRequestFormTotp:
    """OAuth2 password form extended with optional TOTP code."""

    def __init__(
        self,
        grant_type: str | None = Form(default="password"),
        username: str = Form(...),
        password: str = Form(...),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
        totp_code: str | None = Form(default=None),
    ):
        if grant_type and grant_type.lower() not in {"password", ""}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported grant type",
            )
        self.grant_type = grant_type or "password"
        self.username = username
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret
        self.totp_code = totp_code


def _ensure_governor_permits_auth(user: User | None = None) -> None:
    """Ensure authentication actions are allowed for the current governor state."""

    governor = api_interface.governor

    def admin_override() -> bool:
        return bool(user and user.role == UserRole.ADMIN)

    if governor.is_shutdown() and not admin_override():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication suspended while governor is in shutdown",
        )
    if getattr(governor, "is_rollback_active", None) and governor.is_rollback_active() and not admin_override():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Authentication paused during rollback",
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestFormTotp = Depends(),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _ensure_governor_permits_auth(user)
    status_info = get_two_factor_status(user)
    if status_info.pending:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Two-factor enrollment pending confirmation",
        )
    if status_info.enabled:
        if not form_data.totp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Two-factor authentication code required",
            )
        if not validate_two_factor_code(user, form_data.totp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid two-factor authentication code",
            )
    
    # Update last login time
    user.last_login = datetime.utcnow()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires,
    )
    
    # Return token with expiration time
    expires_at = user.last_login + access_token_expires
    return Token(access_token=access_token, token_type="bearer", expires_at=expires_at)


@router.get("/2fa/status", response_model=TwoFactorStatusResponse)
async def two_factor_status(current_user: User = Depends(get_current_active_user)):
    status_data = get_two_factor_status(current_user)
    return TwoFactorStatusResponse(
        enabled=status_data.enabled,
        status=status_data.status,
        version=status_data.version,
        pending=status_data.pending,
        last_verified_at=status_data.last_verified_at,
        created_at=status_data.created_at,
        issuer=status_data.issuer,
    )


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor(current_user: User = Depends(get_current_active_user)):
    _ensure_governor_permits_auth(current_user)
    payload = start_two_factor_enrollment(current_user)
    return TwoFactorSetupResponse(
        secret=payload["secret"],
        otpauth_url=payload["otpauth_url"],
        version=int(payload["version"]),
    )


@router.post("/2fa/verify")
async def verify_two_factor(payload: TwoFactorCodeRequest, current_user: User = Depends(get_current_active_user)):
    _ensure_governor_permits_auth(current_user)
    if not verify_two_factor_code(current_user, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
    status_data = get_two_factor_status(current_user)
    return {"status": status_data.status, "version": status_data.version}


@router.post("/2fa/disable")
async def disable_two_factor_endpoint(
    payload: TwoFactorCodeRequest,
    current_user: User = Depends(get_current_active_user),
):
    _ensure_governor_permits_auth(current_user)
    status_data = get_two_factor_status(current_user)
    if status_data.enabled:
        if not validate_two_factor_code(current_user, payload.code):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid two-factor code")
    if not disable_two_factor(current_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two-factor authentication not enabled")
    return {"status": "disabled"}

@router.post("/register", response_model=UserResponse, dependencies=[Depends(check_permission(Permission.ADMIN))])
async def register_user(user_create: UserCreate, current_user: User = Depends(get_current_active_user)):
    """
    Register a new user (admin only).
    """
    return create_user(user_create)

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        two_factor_enabled=current_user.two_factor_enabled,
    )

@router.get("/users", response_model=List[UserResponse], dependencies=[Depends(check_permission(Permission.ADMIN))])
async def read_users(current_user: User = Depends(get_current_active_user)):
    """
    Get all users (admin only).
    """
    return get_all_users()

@router.put("/users/{username}", response_model=UserResponse, dependencies=[Depends(check_permission(Permission.ADMIN))])
async def update_user_endpoint(username: str, user_update: UserUpdate, current_user: User = Depends(get_current_active_user)):
    """
    Update a user (admin only).
    """
    # Allow users to update their own information
    if username != current_user.username and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update other users",
        )
    
    # Prevent non-admin users from changing their role
    if user_update.role is not None and username == current_user.username and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to change your role",
        )
    
    updated_user = update_user(username, user_update)
    return UserResponse(
        username=updated_user.username,
        email=updated_user.email,
        role=updated_user.role,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        last_login=updated_user.last_login,
        two_factor_enabled=updated_user.two_factor_enabled,
    )

@router.delete("/users/{username}", dependencies=[Depends(check_permission(Permission.ADMIN))])
async def delete_user_endpoint(username: str, current_user: User = Depends(get_current_active_user)):
    """
    Delete a user (admin only).
    """
    # Prevent deleting yourself
    if username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    delete_user(username)
    return {"detail": "User deleted successfully"}

@router.post("/users/me/password")
async def change_password(password: str, current_user: User = Depends(get_current_active_user)):
    """
    Change current user's password.
    """
    user_update = UserUpdate(password=password)
    update_user(current_user.username, user_update)
    return {"detail": "Password changed successfully"}
