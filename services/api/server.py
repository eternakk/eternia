import asyncio
import logging
import time
from pathlib import Path
from typing import Union

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette_exporter import PrometheusMiddleware

from modules.monitoring import http_metrics_middleware
from modules.backup_manager import backup_manager
from .deps import run_world, world, event_queue, DEV_TOKEN, save_governor_state
from .auth import auth_router, get_current_active_user, User
from .routers import (
    agent_router,
    zone_router,
    ritual_router,
    command_router,
    state_router,
    log_router,
    law_router,
    monitoring_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/api_security.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Set up security
security = HTTPBearer()


async def auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Authenticate requests using Bearer token authentication.

    Supports both legacy DEV_TOKEN and JWT-based authentication.
    """
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # First try legacy token for backward compatibility
    # Check if the provided token matches DEV_TOKEN or starts with DEV_TOKEN
    # This handles cases where there might be extra characters at the end
    if credentials.credentials == DEV_TOKEN or credentials.credentials.startswith(DEV_TOKEN):
        return credentials.credentials

    # If not legacy token, try JWT authentication
    try:
        # Get current user from JWT token
        user = await get_current_active_user(credentials.credentials)
        return user
    except Exception as e:
        # Log failed authentication attempts
        logger.warning(f"Failed authentication attempt: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


app = FastAPI(
    title="Eterna Control API",
    version="0.1.0",
    description="API for controlling and monitoring the Eternia simulation",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add rate limiter exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include all routers
app.include_router(auth_router, prefix="/auth")
app.include_router(agent_router)
app.include_router(zone_router)
app.include_router(ritual_router)
app.include_router(command_router)
app.include_router(state_router)
app.include_router(log_router)
app.include_router(law_router)
app.include_router(monitoring_router)

# Configure CORS - allow necessary origins
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8000",  # API server (for same-origin requests)
    "http://localhost",       # For requests without port specified
    "https://eternia.example.com",  # Production
    "https://staging.eternia.example.com",  # Staging
    "*",  # Allow all origins temporarily to debug CORS issues
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS for preflight requests
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Access-Control-Allow-Origin",
    ],  # Restrict to only necessary headers
)

# Add Prometheus middleware for metrics collection
app.add_middleware(
    PrometheusMiddleware,
    app_name="eternia",
    group_paths=True,
    prefix="eternia",
)

# Add custom HTTP metrics middleware
http_metrics_middleware(app)

# Use absolute path for static files
base_dir = Path(__file__).parent.parent.parent  # Go up to the project root
static_dir = base_dir / "assets" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ─────────────────────────────  TOKEN  ──────────────────────────────

@app.get(
    "/api/token",
    summary="Get API token",
    description="Returns the development API token for authentication. This endpoint is intended for development and testing purposes only.",
    response_description="The development token for API authentication",
    responses={
        200: {"description": "Token successfully retrieved"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("30/minute")
async def get_token(request: Request):
    """
    Get the API token for authentication.

    This endpoint returns the DEV_TOKEN that should be used for authentication.
    It's intended for development and testing purposes only.

    Args:
        request: The request object (for rate limiting)

    Returns:
        The DEV_TOKEN for authentication
    """
    return {"token": DEV_TOKEN}


# ───────────────────────────  WEBSOCKET  ────────────────────────────
clients = set()
# Track connection attempts for rate limiting
connection_attempts = {}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    WebSocket endpoint for real-time event streaming.

    Args:
        ws: The WebSocket connection
    """
    client = ws.client.host
    current_time = time.time()

    # Implement basic rate limiting for WebSocket connections
    if client in connection_attempts:
        # Remove attempts older than 1 minute
        connection_attempts[client] = [
            t for t in connection_attempts[client] if current_time - t < 60
        ]

        # Check if too many connection attempts
        if len(connection_attempts[client]) > 10:  # Max 10 connections per minute
            logger.warning(f"WebSocket connection rate limit exceeded for {client}")
            await ws.close(code=1008)  # Policy violation
            return

        connection_attempts[client].append(current_time)
    else:
        connection_attempts[client] = [current_time]

    # Authenticate the WebSocket connection
    try:
        # Wait for authentication message with token
        await ws.accept()
        auth_message = await asyncio.wait_for(ws.receive_json(), timeout=5.0)

        if not isinstance(auth_message, dict) or "token" not in auth_message:
            logger.warning(f"Invalid WebSocket authentication format from {client}")
            await ws.close(code=1008)
            return

        token = auth_message.get("token")
        # Check if the provided token matches DEV_TOKEN or starts with DEV_TOKEN
        # This handles cases where there might be extra characters at the end
        if token != DEV_TOKEN and not token.startswith(DEV_TOKEN):
            logger.warning(f"Invalid WebSocket authentication token from {client}")
            await ws.close(code=1008)
            return

        # Authentication successful
        clients.add(ws)
        await ws.send_json({"event": "connected", "status": "authenticated"})

        try:
            while True:
                message = await ws.receive_text()
                # Implement message validation if needed
                # For now, we just ignore client messages
        except WebSocketDisconnect:
            logger.info(f"WebSocket client disconnected: {client}")
            clients.remove(ws)
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {e}")
            clients.discard(ws)
    except asyncio.TimeoutError:
        logger.warning(f"WebSocket authentication timeout for {client}")
        await ws.close(code=1008)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await ws.close(code=1011)  # Internal error
        except:
            pass


# ───────── background broadcaster ──────────
async def broadcaster():
    """Relays governor events from the queue to all connected WebSocket clients."""
    while True:
        event = await event_queue.get()
        if "t" not in event:
            event["t"] = time.time()
        stale = []
        for ws in clients:
            try:
                await ws.send_json(event)
            except Exception:
                stale.append(ws)
        for ws in stale:
            clients.discard(ws)


# register startup task
@app.on_event("startup")
async def startup_event():
    # Initialize the backup manager with the state tracker
    backup_manager.set_state_tracker(world.state_tracker)

    # Start the backup scheduler if backups are enabled
    backup_manager.start_scheduler()

    # Start the broadcaster and world loop
    asyncio.create_task(broadcaster())
    asyncio.create_task(run_world())
