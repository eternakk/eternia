from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .models import User, UserRole, Permission, Token, UserCreate, UserUpdate, UserResponse
from .auth_service import (
    authenticate_user, create_access_token, get_current_active_user,
    create_user, update_user, delete_user, get_all_users, check_permission,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create router
router = APIRouter(tags=["auth"])

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
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
        last_login=current_user.last_login
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
        last_login=updated_user.last_login
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