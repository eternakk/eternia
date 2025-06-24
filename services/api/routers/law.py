import logging
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..auth import get_current_active_user, Permission, User
from ..deps import world, governor

# Configure logging
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(prefix="/laws", tags=["laws"])


async def auth(token: str = Depends(get_current_active_user)):
    """
    Authenticate requests using JWT-based authentication.
    """
    return token


@router.get(
    "",
    summary="List all laws",
    description="Returns a dictionary of all laws in the system with their details.",
    response_description="Dictionary of laws with their details",
    responses={
        200: {"description": "Laws successfully retrieved"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("60/minute")
async def list_laws(request: Request, current_user: Union[str, User] = Depends(auth)):
    """
    List all laws in the system.

    Args:
        request: The request object (for rate limiting)
        current_user: The authenticated user or legacy token

    Returns:
        Dictionary of laws with their details
    """
    try:
        return {name: law.model_dump() for name, law in governor.laws.items()}
    except Exception as e:
        logger.error(f"Error retrieving laws: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve laws")


@router.post(
    "/{name}/toggle",
    summary="Toggle law",
    description="Enables or disables a specific law in the system.",
    response_description="The new state of the law",
    responses={
        200: {"description": "Law successfully toggled"},
        400: {"description": "Invalid request parameters"},
        403: {"description": "Not enough permissions"},
        404: {"description": "Law not found"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("20/minute")
async def toggle_law(
    request: Request,
    name: str = Path(..., description="The name of the law to toggle"),
    enabled: bool = Body(embed=True, description="Whether to enable or disable the law"),
    current_user: Union[str, User] = Depends(auth),
):
    """
    Toggle a law on or off.

    Args:
        request: The request object (for rate limiting)
        name: The name of the law to toggle
        enabled: Whether to enable or disable the law
        current_user: The authenticated user or legacy token

    Returns:
        The new state of the law
    """
    # Check permissions if using JWT authentication - require ADMIN permission for law modification
    if isinstance(current_user, User) and not current_user.has_permission(Permission.ADMIN):
        logger.warning(f"User {current_user.username} attempted to toggle law without admin permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. ADMIN permission required.",
        )

    try:
        # Validate law name
        if name not in governor.laws:
            logger.warning(f"Attempt to toggle non-existent law: {name}")
            raise HTTPException(status_code=404, detail="Law not found")

        # Validate enabled parameter
        if not isinstance(enabled, bool):
            raise HTTPException(status_code=400, detail="Enabled must be a boolean")

        # Log the user who performed the action
        user_info = current_user.username if isinstance(current_user, User) else "legacy_token"

        # Toggle the law
        governor.laws[name].enabled = enabled
        logger.info(f"Law '{name}' {'enabled' if enabled else 'disabled'} by {user_info}")
        return {"enabled": enabled}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling law {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle law")
