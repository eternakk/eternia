import logging
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import BaseModel, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..auth import get_current_active_user, Permission, User
from ..deps import world
from ..schemas import StateOut

# Configure logging
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(tags=["state"])


async def auth(token: str = Depends(get_current_active_user)):
    """
    Authenticate requests using JWT-based authentication.
    """
    return token


class RewardIn(BaseModel):
    value: float

    @field_validator("value")
    def validate_value(cls, v):
        """Validate that the reward value is within acceptable bounds."""
        if not -100 <= v <= 100:
            raise ValueError("Reward value must be between -100 and 100")
        return v


@router.post(
    "/reward/{companion_name}",
    summary="Send reward to companion",
    description="Sends a reward value to a specific companion for reinforcement learning.",
    response_description="Confirmation of the reward being sent",
    responses={
        200: {"description": "Reward successfully sent"},
        400: {"description": "Invalid companion name or reward value"},
        403: {"description": "Not enough permissions"},
        404: {"description": "Companion not found"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("60/minute")
async def send_reward(
    request: Request, companion_name: str, body: RewardIn, current_user: Union[str, User] = Depends(auth)
):
    """
    Send a reward to a specific companion.

    Args:
        request: The request object (for rate limiting)
        companion_name: The name of the companion to reward
        body: The reward data
        current_user: The authenticated user or legacy token

    Returns:
        Confirmation of the reward being sent
    """
    # Check permissions if using JWT authentication
    if isinstance(current_user, User) and not current_user.has_permission(Permission.WRITE):
        logger.warning(f"User {current_user.username} attempted to send reward without permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. WRITE permission required.",
        )

    # Validate and sanitize companion name
    if not companion_name or not isinstance(companion_name, str):
        raise HTTPException(status_code=400, detail="Invalid companion name")

    # Prevent injection attacks
    if any(char in companion_name for char in "\"'\\;:,.<>/{}[]()"):
        logger.warning(
            f"Possible injection attempt with companion name: {companion_name}"
        )
        raise HTTPException(status_code=400, detail="Invalid companion name")

    # Check if companion exists
    companion = world.eterna.get_companion(companion_name)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    try:
        # Log the user who sent the reward
        user_info = current_user.username if isinstance(current_user, User) else "legacy_token"

        # stash reward so step() can read it
        world.companion_trainer.observe_reward(companion_name, body.value)
        logger.info(f"Reward of {body.value} sent to companion {companion_name} by {user_info}")
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error sending reward to companion {companion_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reward")


@router.get(
    "/state", 
    response_model=StateOut,
    summary="Get system state",
    description="Returns the current state of the Eternia simulation, including cycle count, identity score, emotion, modifiers, and current zone.",
    response_description="Current state of the system",
    responses={
        200: {"description": "State successfully retrieved", "model": StateOut},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("120/minute")
async def get_state(request: Request, current_user: Union[str, User] = Depends(auth)):
    """
    Get the current state of the system.

    Args:
        request: The request object (for rate limiting)
        current_user: The authenticated user or legacy token

    Returns:
        The current state of the system
    """
    try:
        # Check if world and state_tracker are properly initialized
        if not hasattr(world, 'state_tracker') or not world.state_tracker:
            logger.error("State tracker not initialized")
            raise HTTPException(status_code=500, detail="State tracker not initialized")

        tracker = world.state_tracker

        # Check if world.eterna and runtime are properly initialized
        if not hasattr(world, 'eterna') or not world.eterna:
            logger.error("World or Eterna not initialized")
            raise HTTPException(status_code=500, detail="World not initialized")

        if not hasattr(world.eterna, 'runtime') or not world.eterna.runtime:
            logger.error("Runtime not initialized")
            raise HTTPException(status_code=500, detail="Runtime not initialized")

        if not hasattr(world.eterna.runtime, 'cycle_count'):
            logger.error("cycle_count not found in runtime")
            raise HTTPException(status_code=500, detail="Cycle count not found")

        # Check if required methods and attributes exist in tracker
        if not hasattr(tracker, 'identity_continuity'):
            logger.error("identity_continuity method not found in state tracker")
            raise HTTPException(status_code=500, detail="Method not found")

        if not hasattr(tracker, 'applied_modifiers'):
            logger.error("applied_modifiers attribute not found in state tracker")
            raise HTTPException(status_code=500, detail="Attribute not found")

        if not hasattr(tracker, 'current_zone'):
            logger.error("current_zone method not found in state tracker")
            raise HTTPException(status_code=500, detail="Method not found")

        if not hasattr(tracker, 'last_emotion'):
            logger.error("last_emotion attribute not found in state tracker")
            raise HTTPException(status_code=500, detail="Attribute not found")

        # Extract emotion name if it's an object, otherwise use as is
        emotion = tracker.last_emotion
        if isinstance(emotion, dict) and "name" in emotion:
            emotion = emotion["name"]
        elif hasattr(emotion, "name"):
            emotion = emotion.name

        return {
            "cycle": world.eterna.runtime.cycle_count,
            "identity_score": tracker.identity_continuity(),
            "emotion": emotion,
            "modifiers": tracker.applied_modifiers,
            "current_zone": tracker.current_zone(),
        }
    except Exception as e:
        logger.error(f"Error retrieving state: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve state: {str(e)}")


@router.get(
    "/checkpoints",
    summary="List checkpoints",
    description="Returns a list of the 10 most recent system state checkpoints.",
    response_description="List of recent checkpoints",
    responses={
        200: {"description": "Checkpoints successfully retrieved"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("60/minute")
async def list_checkpoints(request: Request, current_user: Union[str, User] = Depends(auth)):
    """
    List the most recent checkpoints.

    Args:
        request: The request object (for rate limiting)
        current_user: The authenticated user or legacy token

    Returns:
        List of the 10 most recent checkpoints
    """
    try:
        checkpoints = world.state_tracker.list_checkpoints()
        return checkpoints[-10:] if checkpoints else []  # last 10 or empty list
    except Exception as e:
        logger.error(f"Error retrieving checkpoints: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve checkpoints")
