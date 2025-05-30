import asyncio
import logging
import time
from pathlib import Path
from typing import List, Dict

from fastapi import Body, Request
from fastapi import FastAPI, HTTPException, Depends
from fastapi import Query
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sse_starlette.sse import EventSourceResponse

from modules.utilities.file_utils import load_json
from .deps import run_world  # background sim loop
from .deps import world, governor, event_queue, DEV_TOKEN
from .schemas import StateOut, CommandOut

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/api_security.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

LOG_PATH = "logs/eterna_runtime.log"

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Set up security
security = HTTPBearer()


def auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Authenticate requests using Bearer token authentication.
    """
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.credentials != DEV_TOKEN:
        # Log failed authentication attempts
        logger.warning(f"Failed authentication attempt from {get_remote_address}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


app = FastAPI(title="Eterna Control API", version="0.1.0")

# Add rate limiter exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - restrict to only necessary origins
origins = ["http://localhost:5173"]  # Vite dev server

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to only necessary methods
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],  # Restrict to only necessary headers
)

ASSET_MAP = load_json("assets/zone_assets.json", {})
app.mount("/static", StaticFiles(directory="assets/static"), name="static")


@app.get("/zone/assets")
@limiter.limit("60/minute")
async def zone_assets(request: Request, name: str):
    """
    Get assets for a specific zone.

    Args:
        request: The request object (for rate limiting)
        name: The name of the zone

    Returns:
        The assets for the specified zone
    """
    # Validate and sanitize the zone name
    if not name or not isinstance(name, str):
        raise HTTPException(status_code=400, detail="Invalid zone name")

    # Prevent directory traversal
    if ".." in name or "/" in name or "\\" in name:
        logger.warning(f"Possible path traversal attempt with zone name: {name}")
        raise HTTPException(status_code=400, detail="Invalid zone name")

    return ASSET_MAP.get(name, {})


# ─────────────────────────────  STATE  ──────────────────────────────


class RewardIn(BaseModel):
    value: float

    @validator("value")
    def validate_value(cls, v):
        """Validate that the reward value is within acceptable bounds."""
        if not -100 <= v <= 100:
            raise ValueError("Reward value must be between -100 and 100")
        return v


@app.post("/reward/{companion_name}")
@limiter.limit("30/minute")
async def send_reward(
        request: Request, companion_name: str, body: RewardIn, token: str = Depends(auth)
):
    """
    Send a reward to a specific companion.

    Args:
        request: The request object (for rate limiting)
        companion_name: The name of the companion to reward
        body: The reward data
        token: The authentication token

    Returns:
        Confirmation of the reward being sent
    """
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
        # stash reward so step() can read it
        world.companion_trainer.observe_reward(companion_name, body.value)
        logger.info(f"Reward of {body.value} sent to companion {companion_name}")
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error sending reward to companion {companion_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reward")


@app.get("/state", response_model=StateOut)
@limiter.limit("120/minute")
async def get_state(request: Request):
    """
    Get the current state of the system.

    Args:
        request: The request object (for rate limiting)

    Returns:
        The current state of the system
    """
    try:
        tracker = world.state_tracker
        return {
            "cycle": world.eterna.runtime.cycle_count,
            "identity_score": tracker.identity_continuity(),
            "emotion": tracker.last_emotion,
            "modifiers": tracker.applied_modifiers,
            "current_zone": tracker.current_zone(),
        }
    except Exception as e:
        logger.error(f"Error retrieving state: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve state")


# ───────────────────────────  COMMANDS  ─────────────────────────────


# --- modified rollback route ----------------------------------------
@app.post("/command/rollback", response_model=CommandOut)
@limiter.limit("10/minute")
async def rollback(
        request: Request, file: str | None = Query(default=None), token: str = Depends(auth)
):
    """
    Roll back the system state to a previous checkpoint.

    Args:
        request: The request object (for rate limiting)
        file: The checkpoint file to roll back to (optional)
        token: The authentication token

    Returns:
        Confirmation of the rollback
    """
    try:
        # Validate file path if provided
        if file:
            # Prevent path traversal
            if ".." in file or file.startswith("/") or file.startswith("\\"):
                logger.warning(f"Possible path traversal attempt with file: {file}")
                raise HTTPException(status_code=400, detail="Invalid file path")

            # Ensure the file is in the checkpoints directory
            file_path = Path(file)
            if not file_path.suffix == ".json":
                raise HTTPException(status_code=400, detail="Invalid file type")

            target = file_path
        else:
            target = None

        # Perform the rollback
        governor.rollback(target)
        logger.info(f"System rolled back to {str(target) if target else 'latest'}")
        return {"status": "rolled_back", "detail": str(target) if target else "latest"}
    except Exception as e:
        logger.error(f"Error during rollback: {e}")
        raise HTTPException(status_code=500, detail="Failed to roll back system state")


@app.post("/command/{action}", response_model=CommandOut)
@limiter.limit("20/minute")
async def command(request: Request, action: str, token: str = Depends(auth)):
    """
    Execute a command on the system.

    Args:
        request: The request object (for rate limiting)
        action: The action to perform (pause, resume, shutdown)
        token: The authentication token

    Returns:
        The result of the command
    """
    from .deps import save_shutdown_state

    # Validate action
    valid_actions = ["pause", "resume", "shutdown"]
    action = action.lower()
    if action not in valid_actions:
        logger.warning(f"Invalid action attempted: {action}")
        raise HTTPException(status_code=404, detail="Unknown action")

    try:
        match action:
            case "pause":
                governor.pause()
                status = "paused"
                logger.info("System paused")
            case "resume":
                # If the simulation was shutdown, we need to reset the shutdown flag
                if governor.is_shutdown():
                    governor._shutdown = False
                    save_shutdown_state(False)  # Clear the shutdown state
                    # Reset the cycle count to start from the beginning
                    world.eterna.runtime.cycle_count = 0
                governor.resume()
                status = "running"
                logger.info("System resumed")
            case "shutdown":
                governor.shutdown("user request")
                save_shutdown_state(True)  # Save shutdown state immediately
                status = "shutdown"
                logger.info("System shutdown initiated")
                return {"status": status, "detail": "server will stop world loop"}

        return {"status": status, "detail": None}
    except Exception as e:
        logger.error(f"Error executing command {action}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to execute command {action}"
        )


# ────────────────────────────  LOG TAIL  ────────────────────────────
@app.get("/log/stream")
@limiter.limit("30/minute")
async def stream_logs(request: Request, token: str = Depends(auth)):
    """
    Stream log entries in real-time.

    Args:
        request: The request object (for rate limiting)
        token: The authentication token

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


# ───────────────────────────  WEBSOCKET  ────────────────────────────
clients: set[WebSocket] = set()
# Track connection attempts for rate limiting
connection_attempts: Dict[str, List[float]] = {}


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
        if token != DEV_TOKEN:
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


# --- list checkpoints -----------------------------------------------
@app.get("/checkpoints")
@limiter.limit("30/minute")
async def list_checkpoints(request: Request, token: str = Depends(auth)):
    """
    List the most recent checkpoints.

    Args:
        request: The request object (for rate limiting)
        token: The authentication token

    Returns:
        List of the 10 most recent checkpoints
    """
    try:
        checkpoints = world.state_tracker.checkpoints[-10:]  # last 10
        return checkpoints
    except Exception as e:
        logger.error(f"Error retrieving checkpoints: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve checkpoints")


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


@app.get("/laws")
@limiter.limit("30/minute")
async def list_laws(request: Request, token: str = Depends(auth)):
    """
    List all laws in the system.

    Args:
        request: The request object (for rate limiting)
        token: The authentication token

    Returns:
        Dictionary of laws with their details
    """
    try:
        return {name: law.dict() for name, law in governor.laws.items()}
    except Exception as e:
        logger.error(f"Error retrieving laws: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve laws")


@app.post("/laws/{name}/toggle")
@limiter.limit("20/minute")
async def toggle_law(
        request: Request,
        name: str,
        enabled: bool = Body(embed=True),
        token: str = Depends(auth),
):
    """
    Toggle a law on or off.

    Args:
        request: The request object (for rate limiting)
        name: The name of the law to toggle
        enabled: Whether to enable or disable the law
        token: The authentication token

    Returns:
        The new state of the law
    """
    try:
        # Validate law name
        if name not in governor.laws:
            logger.warning(f"Attempt to toggle non-existent law: {name}")
            raise HTTPException(status_code=404, detail="Law not found")

        # Validate enabled parameter
        if not isinstance(enabled, bool):
            raise HTTPException(status_code=400, detail="Enabled must be a boolean")

        # Toggle the law
        governor.laws[name].enabled = enabled
        logger.info(f"Law '{name}' {'enabled' if enabled else 'disabled'}")
        return {"enabled": enabled}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling law {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle law")


# register startup task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcaster())
    asyncio.create_task(run_world())  # ← new line


@app.get("/api/agents")
@limiter.limit("60/minute")
async def list_agents(request: Request):
    """
    List all agents in the system.

    Args:
        request: The request object (for rate limiting)

    Returns:
        List of agents with their details
    """
    try:
        # Access companions through the companions attribute
        agents = world.eterna.companions.companions
        return [
            {
                "name": agent.name,
                "role": agent.role,
                "emotion": getattr(
                    agent, "emotion", None
                ),  # if emotion attribute exists
                "zone": getattr(agent, "zone", None),
                "memory": getattr(agent, "memory", None),
                # Add other info (reward, stats, etc.) as needed
            }
            for agent in agents
        ]
    except Exception as e:
        logger.error(f"Error retrieving agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agents")


@app.get("/api/zones")
@limiter.limit("60/minute")
async def list_zones(request: Request):
    """
    List all zones in the system.

    Args:
        request: The request object (for rate limiting)

    Returns:
        List of zones with their details
    """
    try:
        # Get zones from the exploration registry
        zones = world.eterna.exploration.registry.zones
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
        raise HTTPException(status_code=500, detail="Failed to retrieve zones")


@app.get("/api/rituals")
@limiter.limit("60/minute")
async def list_rituals(request: Request):
    """
    List all rituals in the system.

    Args:
        request: The request object (for rate limiting)

    Returns:
        List of rituals with their details
    """
    try:
        # Get rituals from the ritual system
        rituals_dict = world.eterna.rituals.rituals
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
        raise HTTPException(status_code=500, detail="Failed to retrieve rituals")


@app.post("/api/rituals/trigger/{id}")
@limiter.limit("20/minute")
async def trigger_ritual(request: Request, id: int, token: str = Depends(auth)):
    """
    Trigger a ritual by its ID.

    Args:
        request: The request object (for rate limiting)
        id: The ID of the ritual to trigger
        token: The authentication token

    Returns:
        Confirmation of the ritual being triggered
    """
    try:
        # Validate ritual ID
        if not isinstance(id, int):
            raise HTTPException(status_code=400, detail="Invalid ritual ID")

        # Get rituals from the ritual system
        rituals = list(world.eterna.rituals.rituals.values())
        if id < 0 or id >= len(rituals):
            logger.warning(f"Attempt to trigger non-existent ritual with ID: {id}")
            raise HTTPException(status_code=404, detail="Ritual not found")

        ritual = rituals[id]
        world.eterna.rituals.perform(ritual.name)
        logger.info(f"Ritual '{ritual.name}' triggered")
        return {"status": "success", "message": f"Ritual '{ritual.name}' triggered"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering ritual with ID {id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger ritual")


@app.get("/api/agent/{name}")
@limiter.limit("60/minute")
async def get_agent(request: Request, name: str):
    """
    Get details of a specific agent.

    Args:
        request: The request object (for rate limiting)
        name: The name of the agent

    Returns:
        Details of the specified agent
    """
    try:
        # Validate agent name
        if not name or not isinstance(name, str):
            raise HTTPException(status_code=400, detail="Invalid agent name")

        # Prevent injection attacks
        if any(char in name for char in "\"'\\;:,.<>/{}[]()"):
            logger.warning(f"Possible injection attempt with agent name: {name}")
            raise HTTPException(status_code=400, detail="Invalid agent name")

        agent = world.eterna.get_companion(name)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Expand details as needed
        return {
            "name": agent.name,
            "role": agent.role,
            "emotion": getattr(agent, "emotion", None),
            "zone": getattr(agent, "zone", None),
            "memory": getattr(agent, "memory", None),
            "history": getattr(agent, "history", []),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent {name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent")
