import logging
from typing import List, Dict, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..auth import get_current_active_user, Permission, User
from ..deps import world

# Configure logging
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(prefix="/api", tags=["rituals"])


async def auth(token: str = Depends(get_current_active_user)):
    """
    Authenticate requests using JWT-based authentication.
    """
    return token


@router.get(
    "/rituals",
    summary="List all rituals",
    description="Returns a list of all rituals in the system with their details.",
    response_description="List of rituals with their details",
    responses={
        200: {"description": "List of rituals successfully retrieved"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("60/minute")
async def list_rituals(request: Request, current_user: Union[str, User] = Depends(auth)):
    """
    List all rituals in the system.

    Args:
        request: The request object (for rate limiting)
        current_user: The authenticated user or legacy token

    Returns:
        List of rituals with their details
    """
    try:
        # Check if world.eterna and rituals are properly initialized
        if not hasattr(world, 'eterna') or not world.eterna:
            logger.error("World or Eterna not initialized")
            return []

        if not hasattr(world.eterna, 'rituals') or not world.eterna.rituals:
            logger.error("Rituals module not initialized")
            return []

        if not hasattr(world.eterna.rituals, 'rituals'):
            logger.error("Rituals dictionary not found in rituals module")
            return []

        rituals_dict = world.eterna.rituals.rituals
        if rituals_dict is None:
            logger.error("Rituals dictionary is None")
            return []

        return [
            {
                "id": i,  # Use index as ID
                "name": ritual.name,
                "purpose": ritual.purpose,
                "steps": ritual.steps,
                "symbolic_elements": ritual.symbolic_elements,
            }
            for i, ritual in enumerate(rituals_dict.values())
        ]
    except Exception as e:
        logger.error(f"Error retrieving rituals: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve rituals: {str(e)}")


@router.post(
    "/rituals/trigger/{id}",
    summary="Trigger ritual",
    description="Triggers a ritual by its ID, causing it to be performed in the simulation.",
    response_description="Confirmation of the ritual being triggered",
    responses={
        200: {"description": "Ritual successfully triggered"},
        400: {"description": "Invalid ritual ID"},
        404: {"description": "Ritual not found"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("20/minute")
async def trigger_ritual(
    request: Request, 
    id: int = Path(..., description="The ID of the ritual to trigger"), 
    current_user: Union[str, User] = Depends(auth)
):
    """
    Trigger a ritual by its ID.

    Args:
        request: The request object (for rate limiting)
        id: The ID of the ritual to trigger
        current_user: The authenticated user or legacy token

    Returns:
        Confirmation of the ritual being triggered
    """
    # All authenticated users can trigger rituals, no permission check needed

    try:
        # Validate ritual ID
        if not isinstance(id, int):
            raise HTTPException(status_code=400, detail="Invalid ritual ID")

        # Check if world.eterna and rituals are properly initialized
        if not hasattr(world, 'eterna') or not world.eterna:
            logger.error("World or Eterna not initialized")
            raise HTTPException(status_code=500, detail="World not initialized")

        if not hasattr(world.eterna, 'rituals') or not world.eterna.rituals:
            logger.error("Rituals module not initialized")
            raise HTTPException(status_code=500, detail="Rituals module not initialized")

        if not hasattr(world.eterna.rituals, 'rituals') or not world.eterna.rituals.rituals:
            logger.error("Rituals dictionary not found in rituals module")
            raise HTTPException(status_code=500, detail="Rituals not found")

        # Get rituals from the ritual system
        rituals = list(world.eterna.rituals.rituals.values())
        if id < 0 or id >= len(rituals):
            logger.warning(f"Attempt to trigger non-existent ritual with ID: {id}")
            raise HTTPException(status_code=404, detail="Ritual not found")

        # Check if perform method exists
        if not hasattr(world.eterna.rituals, 'perform'):
            logger.error("perform method not found in rituals module")
            raise HTTPException(status_code=500, detail="Method not found")

        # Log the user who triggered the ritual
        user_info = current_user.username if isinstance(current_user, User) else "legacy_token"

        ritual = rituals[id]
        world.eterna.rituals.perform(ritual.name)
        logger.info(f"Ritual '{ritual.name}' triggered by {user_info}")
        return {"status": "success", "message": f"Ritual '{ritual.name}' triggered"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering ritual with ID {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger ritual: {str(e)}")
