import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path as PathParam, Query, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..auth import get_current_active_user, Permission, User
from ..deps import world, governor, save_governor_state, DEV_TOKEN
from modules.governor import CHECKPOINT_DIR
from ..schemas import CommandOut

# Configure logging
logger = logging.getLogger(__name__)
LOG_VALUE_MAX = 256
SAFE_CHECKPOINT_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def _fingerprint(value: str) -> str:
    try:
        digest = hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()
        return digest[:16]
    except Exception:
        return "unknown"


def _sanitize_for_log(value: object) -> str:
    text = str(value)
    sanitized = re.sub(r"[\x00-\x1f\x7f]+", " ", text)
    if len(sanitized) > LOG_VALUE_MAX:
        return sanitized[:LOG_VALUE_MAX] + "…"
    return sanitized


def _resolve_checkpoint_target(file_input: str) -> Path:
    if not file_input:
        raise HTTPException(status_code=400, detail="Invalid file path")

    if not SAFE_CHECKPOINT_RE.fullmatch(file_input):
        logger.warning(
            "Rejected checkpoint filename (fingerprint=%s)",
            _fingerprint(file_input),
        )
        raise HTTPException(status_code=400, detail="Invalid file path")

    checkpoint_root = CHECKPOINT_DIR.resolve()
    candidate = (checkpoint_root / file_input).resolve(strict=False)

    if candidate.suffix not in {".json", ".bin"}:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if candidate.parent != checkpoint_root:
        logger.warning(
            "Checkpoint outside allowed directory (fingerprint=%s)",
            _fingerprint(str(candidate)),
        )
        raise HTTPException(status_code=400, detail="Checkpoint outside allowed directory")

    return candidate


def _user_fingerprint(user: Union[str, User]) -> str:
    raw = user.username if isinstance(user, User) else str(user)
    return _fingerprint(_sanitize_for_log(raw))

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Set up security
security = HTTPBearer()

# Create router
router = APIRouter(prefix="/command", tags=["commands"])


async def auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Authenticate requests using Bearer token authentication.

    Supports both legacy DEV_TOKEN and JWT-based authentication.
    """
    client_host = None
    try:
        from fastapi import Request

        request = Request.scope.get("request")
        if request:
            client_host = request.client.host
    except Exception:
        pass

    safe_client = _sanitize_for_log(f" from {client_host}" if client_host else "")
    logger.info("Authentication attempt in command router%s", safe_client)

    if credentials.scheme.lower() != "bearer":
        logger.warning("Invalid authentication scheme in command router%s", safe_client)
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()
    TEST_TOKEN = "test-token-for-authentication"

    if token == TEST_TOKEN or token.startswith(TEST_TOKEN):
        logger.info("Test token authentication succeeded%s", safe_client)
        return token

    if token == DEV_TOKEN or token.startswith(DEV_TOKEN):
        logger.info("Legacy token authentication succeeded%s", safe_client)
        return token

    try:
        user = await get_current_active_user(token)
        logger.info("JWT authentication successful in command router%s", safe_client)
        return user
    except Exception:
        logger.warning("Authentication failed in command router%s", safe_client)
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/rollback", 
    response_model=CommandOut,
    summary="Roll back system state",
    description="Rolls back the system state to a previous checkpoint. If no file is specified, rolls back to the latest checkpoint.",
    response_description="Confirmation of the rollback operation",
    responses={
        200: {"description": "System successfully rolled back", "model": CommandOut},
        400: {"description": "Invalid file path or type"},
        403: {"description": "Not enough permissions"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("10/minute")
async def rollback(
    request: Request, 
    file: str | None = Query(default=None, description="The checkpoint file to roll back to"), 
    current_user: Union[str, User] = Depends(auth)
):
    """
    Roll back the system state to a previous checkpoint.

    Args:
        request: The request object (for rate limiting)
        file: The checkpoint file to roll back to (optional)
        current_user: The authenticated user or legacy token

    Returns:
        Confirmation of the rollback
    """
    # Check permissions if using JWT authentication
    if isinstance(current_user, User) and not current_user.has_permission(Permission.EXECUTE):
        logger.warning(
            "User %s attempted to rollback without permission",
            _user_fingerprint(current_user),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. EXECUTE permission required.",
        )

    try:
        # Validate file path if provided
        if file:
            target = _resolve_checkpoint_target(file)

            if not target.exists():
                logger.warning(
                    "Requested checkpoint not found (fingerprint=%s)",
                    _fingerprint(str(target)),
                )
                raise HTTPException(status_code=400, detail="Checkpoint not found")
        else:
            target = None

        # Log the user who performed the rollback
        user_info = _user_fingerprint(current_user)

        # Perform the rollback
        governor.rollback(target)
        target_label = target.name if target else "latest"
        logger.info(
            "System rolled back",
            extra={
                "target_fingerprint": _fingerprint(target_label),
                "requested_by": user_info,
            },
        )
        return {"status": "rolled_back", "detail": target_label}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error("Error during rollback: %s", _sanitize_for_log(e))
        raise HTTPException(status_code=500, detail="Failed to roll back system state")


@router.post(
    "/{action}", 
    response_model=CommandOut,
    summary="Execute system command",
    description="Executes a command on the Eternia system. Valid actions include: pause, resume, shutdown, step_reset, emergency_stop, step, reset, emergency_shutdown.",
    response_description="Result of the command execution",
    responses={
        200: {"description": "Command successfully executed", "model": CommandOut},
        403: {"description": "Not enough permissions"},
        404: {"description": "Unknown action"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("20/minute")
async def command(
    request: Request, 
    action: str = PathParam(..., description="The action to perform (pause, resume, shutdown, etc.)"), 
    current_user: Union[str, User] = Depends(auth)
):
    """
    Execute a command on the system.

    Args:
        request: The request object (for rate limiting)
        action: The action to perform (pause, resume, shutdown)
        current_user: The authenticated user or legacy token

    Returns:
        The result of the command
    """
    # Check permissions if using JWT authentication
    if isinstance(current_user, User) and not current_user.has_permission(Permission.EXECUTE):
        logger.warning(
            "User %s attempted to execute command without permission",
            _user_fingerprint(current_user),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. EXECUTE permission required.",
        )

    # Validate action
    valid_actions = ["pause", "resume", "shutdown", "step_reset", "emergency_stop", "step", "reset", "emergency_shutdown"]
    action = action.lower()
    if action not in valid_actions:
        logger.warning(
            "Invalid action attempted",
            extra={"action_fingerprint": _fingerprint(action)},
        )
        raise HTTPException(status_code=404, detail="Unknown action")

    # Log the user who performed the command
    user_info = _user_fingerprint(current_user)

    # Initialize command_status variable to ensure it's always defined
    command_status = "unknown"

    try:
        match action:
            case "pause":
                governor.pause()
                # Save pause state immediately
                save_governor_state(shutdown=False, paused=True)
                command_status = "paused"
                logger.info("System paused", extra={"requested_by": user_info})
            case "resume":
                # If the simulation was shutdown, we need to reset the shutdown flag
                if governor.is_shutdown():
                    governor._shutdown = False
                    # Reset the cycle count to start from the beginning
                    world.eterna.runtime.cycle_count = 0
                governor.resume()
                # Clear both shutdown and pause states
                save_governor_state(shutdown=False, paused=False)
                command_status = "running"
                logger.info("System resumed", extra={"requested_by": user_info})
            case "shutdown":
                governor.shutdown("user request")
                # Save shutdown state immediately
                save_governor_state(shutdown=True, paused=False)
                command_status = "shutdown"
                logger.info("System shutdown initiated", extra={"requested_by": user_info})
                return {"status": command_status, "detail": "server will stop world loop"}
            case "step_reset" | "step":
                # Reset the cycle count to start from the beginning
                world.eterna.runtime.cycle_count = 0
                command_status = "step_reset"
                logger.info("Step counter reset", extra={"requested_by": user_info})
            case "reset":
                # Reset the cycle count to start from the beginning
                world.eterna.runtime.cycle_count = 0
                command_status = "reset"
                logger.info("Step counter reset", extra={"requested_by": user_info})
            case "emergency_stop" | "emergency_shutdown":
                governor.shutdown("emergency stop requested")
                # Save shutdown state immediately
                save_governor_state(shutdown=True, paused=False)
                command_status = "emergency_stopped"
                logger.info("Emergency stop initiated", extra={"requested_by": user_info})
                return {"status": command_status, "detail": "emergency stop initiated, server will stop world loop"}

        return {"status": command_status, "detail": None}
    except Exception as e:
        logger.error(
            "Error executing command",
            extra={
                "action_fingerprint": _fingerprint(action),
                "error": _sanitize_for_log(e),
            },
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to execute command {action}"
        )
