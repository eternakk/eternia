import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sse_starlette.sse import EventSourceResponse

from ..auth import get_current_active_user, Permission, User

# Configure logging
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(prefix="/log", tags=["logs"])

# Define log path
LOG_PATH = "logs/eterna_runtime.log"


async def auth(token: str = Depends(get_current_active_user)):
    """
    Authenticate requests using JWT-based authentication.
    """
    return token


@router.get(
    "/stream",
    summary="Stream logs",
    description="Streams log entries in real-time using server-sent events.",
    response_description="Server-sent events stream of log entries",
    responses={
        200: {"description": "Log stream successfully established"},
        404: {"description": "Log file not found"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("30/minute")
async def stream_logs(request: Request, current_user: Union[str, User] = Depends(auth)):
    """
    Stream log entries in real-time.

    Args:
        request: The request object (for rate limiting)
        current_user: The authenticated user or legacy token

    Returns:
        Server-sent events stream of log entries
    """
    # Validate log path
    log_file = Path(LOG_PATH)
    if not log_file.exists():
        logger.error(f"Log file not found: {LOG_PATH}")
        raise HTTPException(status_code=404, detail="Log file not found")

    async def event_generator():
        try:
            with open(LOG_PATH) as f:
                f.seek(0, 2)  # go to end
                while True:
                    try:
                        line = f.readline()
                        if line:
                            # Sanitize log line to prevent XSS
                            sanitized_line = line.replace("<", "&lt;").replace(
                                ">", "&gt;"
                            )
                            yield {"data": sanitized_line}
                        else:
                            await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.error(f"Error reading log line: {e}")
                        await asyncio.sleep(1)  # Wait before retrying
        except Exception as e:
            logger.error(f"Error opening log file: {e}")
            yield {"data": f"Error: {str(e)}"}

    return EventSourceResponse(event_generator())
