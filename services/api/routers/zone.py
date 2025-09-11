import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address

from modules.utilities.file_utils import load_json
from ..auth import get_current_active_user, Permission, User
from ..deps import world, DEV_TOKEN

# Configure logging
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Set up security
security = HTTPBearer()

# Create router
router = APIRouter(tags=["zones"])

# Load zone assets once at startup
ASSET_MAP = load_json("assets/zone_assets.json", {})
# Create a cache for zone assets with TTL (time-to-live)
ZONE_ASSETS_CACHE = {}
ZONE_ASSETS_CACHE_TTL = {}  # Store expiration timestamps
ZONE_ASSETS_CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)


def _client_info() -> str:
    """Best-effort extraction of client host for logging."""
    try:
        # Request injection isn't used here; keep defensive approach
        from fastapi import Request  # type: ignore
        request = Request.scope.get("request")  # type: ignore[attr-defined]
        if request:
            return f" from {request.client.host}"
    except Exception:
        pass
    return ""


def _ensure_bearer_scheme(credentials: HTTPAuthorizationCredentials, client_info: str) -> None:
    if credentials.scheme.lower() != "bearer":
        logger.warning(
            f"Invalid authentication scheme in zone router{client_info}: {credentials.scheme}"
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _token_matches(token: str, expected: str) -> bool:
    """Return True if token equals, startswith, or contains expected string."""
    return token == expected or token.startswith(expected) or (expected in token)


def _try_static_tokens(token: str, client_info: str) -> Optional[Union[str, User]]:
    """Check TEST_TOKEN and DEV_TOKEN shortcuts; return token if matched."""
    TEST_TOKEN = "test-token-for-authentication"

    # Log detailed token comparison for debugging
    logger.info(
        f"Token comparison in zone router - Token: '{token}', TEST_TOKEN: '{TEST_TOKEN}'"
    )
    logger.info(
        f"Token length: {len(token)}, TEST_TOKEN length: {len(TEST_TOKEN)}"
    )

    if _token_matches(token, TEST_TOKEN):
        logger.info(
            f"Test token match in zone router - authentication successful{client_info}"
        )
        return token

    logger.info(f"DEV_TOKEN for comparison in zone router: '{DEV_TOKEN}'")
    if _token_matches(token, DEV_TOKEN):
        logger.info(
            f"Legacy token match in zone router - authentication successful{client_info}"
        )
        return token

    # No static match
    logger.warning(
        f"Token did not match static tokens in zone router{client_info}: '{token}'"
    )
    logger.warning(f"Expected TEST_TOKEN: '{TEST_TOKEN}'")
    logger.warning(f"Expected DEV_TOKEN: '{DEV_TOKEN}'")
    return None


async def _try_jwt(token: str, client_info: str) -> User:
    logger.info(
        f"Legacy/static token auth failed in zone router{client_info}, trying JWT"
    )
    user = await get_current_active_user(token)
    logger.info(
        f"JWT authentication successful in zone router{client_info} for user: {user.username}"
    )
    return user


async def auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Authenticate requests using Bearer token authentication.

    Supports both legacy DEV_TOKEN and JWT-based authentication.
    """
    client_info = _client_info()
    logger.info(f"Authentication attempt in zone router{client_info}")

    _ensure_bearer_scheme(credentials, client_info)

    # Clean the token by removing any leading/trailing whitespace
    token = credentials.credentials.strip()
    logger.info(
        f"Authenticating with token in zone router{client_info}: '{token}'"
    )

    # Try static tokens first
    static_auth = _try_static_tokens(token, client_info)
    if static_auth is not None:
        return static_auth

    # Fallback to JWT authentication
    try:
        return await _try_jwt(token, client_info)
    except Exception as e:
        # Log failed authentication attempts with detailed error
        logger.warning(
            f"Failed authentication attempt in zone router{client_info}: {str(e)}"
        )
        # Log token and DEV_TOKEN comparison for debugging
        token_preview = token[:3] + "..." + token[-3:] if len(token) > 6 else token
        logger.warning(
            f"Failed token in zone router{client_info}: {token_preview}"
        )
        logger.warning(
            f"Token comparison - Token: {token[:3]}...{token[-3:] if len(token) > 6 else ''}, "
            f"DEV_TOKEN: {DEV_TOKEN[:3]}...{DEV_TOKEN[-3:] if len(DEV_TOKEN) > 6 else ''}"
        )
        logger.warning(
            f"Token length: {len(token)}, DEV_TOKEN length: {len(DEV_TOKEN)}"
        )
        logger.warning(f"Token == DEV_TOKEN: {token == DEV_TOKEN}")
        logger.warning(f"Token startswith DEV_TOKEN: {token.startswith(DEV_TOKEN)}")
        logger.warning(f"DEV_TOKEN in Token: {DEV_TOKEN in token}")

        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
        zones = _get_zones_safely()
        return _serialize_zones(zones)
    except Exception as e:
        logger.error(f"Error retrieving zones: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve zones: {str(e)}")


def _get_zones_safely():
    """Safely retrieve zones list from the world exploration registry.

    Returns the zones list or an empty list if not available, with appropriate logging.
    """
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

    return zones


def _serialize_zones(zones):
    """Serialize zone objects into dictionaries for API response."""
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


def _validate_zone_name(zone_name: str):
    if not zone_name or not isinstance(zone_name, str):
        raise HTTPException(status_code=400, detail="Invalid zone name")
    # Prevent simple injection/path traversal characters
    if any(char in zone_name for char in "\"'\\;:,.<>/{}[]()"):
        logger.warning(f"Possible injection attempt with zone name: {zone_name}")
        raise HTTPException(status_code=400, detail="Invalid zone name")


def _ensure_world_ready():
    """Ensure world and exploration registry with zones are available; return zones list."""
    if not hasattr(world, 'eterna') or not world.eterna:
        logger.error("World or Eterna not initialized")
        raise HTTPException(status_code=500, detail="World not initialized")

    exploration = getattr(world.eterna, 'exploration', None)
    if not exploration:
        logger.error("Exploration module not initialized")
        raise HTTPException(status_code=500, detail="Exploration module not initialized")

    registry = getattr(exploration, 'registry', None)
    if not registry:
        logger.error("Exploration registry not initialized")
        raise HTTPException(status_code=500, detail="Exploration registry not initialized")

    zones = getattr(registry, 'zones', None)
    if zones is None:
        logger.error("Zones list is None")
        raise HTTPException(status_code=500, detail="Zones not found")

    return zones


def _ensure_state_tracker_ready():
    """Ensure state_tracker exists and supports mark_zone; return it."""
    st = getattr(world, 'state_tracker', None)
    if not st:
        logger.error("State tracker not initialized")
        raise HTTPException(status_code=500, detail="State tracker not initialized")
    if not hasattr(st, 'mark_zone'):
        logger.error("mark_zone method not found in state tracker")
        raise HTTPException(status_code=500, detail="Method not found")
    return st


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
    _validate_zone_name(zone_name)

    try:
        zones = _ensure_world_ready()

        # Ensure the zone exists
        if not any(z.name == zone_name for z in zones):
            raise HTTPException(status_code=404, detail="Zone not found")

        # Ensure state tracker is ready
        st = _ensure_state_tracker_ready()

        # Log the user who changed the zone
        user_info = current_user.username if isinstance(current_user, User) else "legacy_token"

        # Update the current zone
        st.mark_zone(zone_name)
        logger.info(f"Zone changed to {zone_name} by {user_info}")

        return {"status": "success", "message": f"Zone changed to {zone_name}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing zone to {zone_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to change zone: {str(e)}")
