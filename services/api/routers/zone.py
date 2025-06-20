import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address

from modules.utilities.file_utils import load_json
from ..auth import get_current_active_user, Permission, User
from ..deps import world

# Configure logging
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(tags=["zones"])

# Load zone assets once at startup
ASSET_MAP = load_json("assets/zone_assets.json", {})
# Create a cache for zone assets with TTL (time-to-live)
ZONE_ASSETS_CACHE = {}
ZONE_ASSETS_CACHE_TTL = {}  # Store expiration timestamps
ZONE_ASSETS_CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)


async def auth(token: str = Depends(get_current_active_user)):
    """
    Authenticate requests using JWT-based authentication.
    """
    return token


@router.get(
    "/zone/assets",
    summary="Get zone assets",
    description="Returns assets for a specific zone, used for visualization.",
    response_description="Assets for the specified zone",
    responses={
        200: {"description": "Zone assets successfully retrieved"},
        400: {"description": "Invalid zone name"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("120/minute")
async def zone_assets(request: Request, name: str, current_user: Union[str, User] = Depends(auth)):
    """
    Get assets for a specific zone.

    Args:
        request: The request object (for rate limiting)
        name: The name of the zone
        current_user: The authenticated user or legacy token

    Returns:
        The assets for the specified zone
    """
    try:
        # Validate and sanitize the zone name
        if not name or not isinstance(name, str):
            raise HTTPException(status_code=400, detail="Invalid zone name")

        # Prevent directory traversal
        if ".." in name or "/" in name or "\\" in name:
            logger.warning(f"Possible path traversal attempt with zone name: {name}")
            raise HTTPException(status_code=400, detail="Invalid zone name")

        # Get current time for cache validation
        current_time = time.time()

        # Check if the zone assets are in the cache and not expired
        if name in ZONE_ASSETS_CACHE and ZONE_ASSETS_CACHE_TTL.get(name, 0) > current_time:
            # Return cached assets
            return ZONE_ASSETS_CACHE[name]

        # Check if ASSET_MAP is properly initialized
        if not isinstance(ASSET_MAP, dict):
            logger.error("ASSET_MAP is not properly initialized")
            return {}

        # Get assets from the ASSET_MAP
        assets = ASSET_MAP.get(name, {})

        # Cache the assets with TTL
        ZONE_ASSETS_CACHE[name] = assets
        ZONE_ASSETS_CACHE_TTL[name] = current_time + ZONE_ASSETS_CACHE_DURATION

        return assets
    except Exception as e:
        logger.error(f"Error retrieving zone assets for {name}: {e}")
        return {}


@router.get(
    "/api/zones",
    summary="List all zones",
    description="Returns a list of all zones in the system with their details.",
    response_description="List of zones with their details",
    responses={
        200: {"description": "List of zones successfully retrieved"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("60/minute")
async def list_zones(request: Request, current_user: Union[str, User] = Depends(auth)):
    """
    List all zones in the system.

    Args:
        request: The request object (for rate limiting)
        current_user: The authenticated user or legacy token

    Returns:
        List of zones with their details
    """
    try:
        # Check if world.eterna and exploration are properly initialized
        if not hasattr(world, 'eterna') or not world.eterna:
            logger.error("World or Eterna not initialized")
            return []

        if not hasattr(world.eterna, 'exploration') or not world.eterna.exploration:
            logger.error("Exploration module not initialized")
            return []

        if not hasattr(world.eterna.exploration, 'registry') or not world.eterna.exploration.registry:
            logger.error("Exploration registry not initialized")
            return []

        if not hasattr(world.eterna.exploration.registry, 'zones'):
            logger.error("Zones list not found in exploration registry")
            return []

        zones = world.eterna.exploration.registry.zones
        if zones is None:
            logger.error("Zones list is None")
            return []

        return [
            {
                "id": i,  # Use index as ID
                "name": zone.name,
                "origin": zone.origin,
                "complexity": zone.complexity_level,
                "explored": zone.explored,
                "emotion": zone.emotion_tag,
                "modifiers": zone.modifiers,
            }
            for i, zone in enumerate(zones)
        ]
    except Exception as e:
        logger.error(f"Error retrieving zones: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve zones: {str(e)}")


@router.post(
    "/api/change_zone",
    summary="Change active zone",
    description="Changes the current active zone in the simulation.",
    response_description="Confirmation of the zone change",
    responses={
        200: {"description": "Zone successfully changed"},
        400: {"description": "Invalid zone name"},
        403: {"description": "Not enough permissions"},
        404: {"description": "Zone not found"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("30/minute")
async def change_zone(request: Request, body: dict = Body(...), current_user: Union[str, User] = Depends(auth)):
    """
    Change the current active zone.

    Args:
        request: The request object (for rate limiting)
        body: The request body containing the zone name
        current_user: The authenticated user or legacy token

    Returns:
        Confirmation of the zone change
    """
    # Check permissions if using JWT authentication
    if isinstance(current_user, User) and not current_user.has_permission(Permission.WRITE):
        logger.warning(f"User {current_user.username} attempted to change zone without permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. WRITE permission required.",
        )

    # Validate zone name
    zone_name = body.get("zone")
    if not zone_name or not isinstance(zone_name, str):
        raise HTTPException(status_code=400, detail="Invalid zone name")

    # Prevent injection attacks
    if any(char in zone_name for char in "\"'\\;:,.<>/{}[]()"):
        logger.warning(f"Possible injection attempt with zone name: {zone_name}")
        raise HTTPException(status_code=400, detail="Invalid zone name")

    try:
        # Check if world.eterna and exploration are properly initialized
        if not hasattr(world, 'eterna') or not world.eterna:
            logger.error("World or Eterna not initialized")
            raise HTTPException(status_code=500, detail="World not initialized")

        if not hasattr(world.eterna, 'exploration') or not world.eterna.exploration:
            logger.error("Exploration module not initialized")
            raise HTTPException(status_code=500, detail="Exploration module not initialized")

        if not hasattr(world.eterna.exploration, 'registry') or not world.eterna.exploration.registry:
            logger.error("Exploration registry not initialized")
            raise HTTPException(status_code=500, detail="Exploration registry not initialized")

        if not hasattr(world.eterna.exploration.registry, 'zones'):
            logger.error("Zones list not found in exploration registry")
            raise HTTPException(status_code=500, detail="Zones not found")

        # Check if zone exists
        zones = world.eterna.exploration.registry.zones
        if zones is None:
            logger.error("Zones list is None")
            raise HTTPException(status_code=500, detail="Zones list is None")

        zone_exists = False
        for zone in zones:
            if zone.name == zone_name:
                zone_exists = True
                break

        if not zone_exists:
            raise HTTPException(status_code=404, detail="Zone not found")

        # Check if state_tracker is properly initialized
        if not hasattr(world, 'state_tracker') or not world.state_tracker:
            logger.error("State tracker not initialized")
            raise HTTPException(status_code=500, detail="State tracker not initialized")

        if not hasattr(world.state_tracker, 'mark_zone'):
            logger.error("mark_zone method not found in state tracker")
            raise HTTPException(status_code=500, detail="Method not found")

        # Log the user who changed the zone
        user_info = current_user.username if isinstance(current_user, User) else "legacy_token"

        # Update the current zone
        world.state_tracker.mark_zone(zone_name)
        logger.info(f"Zone changed to {zone_name} by {user_info}")

        return {"status": "success", "message": f"Zone changed to {zone_name}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing zone to {zone_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to change zone: {str(e)}")
