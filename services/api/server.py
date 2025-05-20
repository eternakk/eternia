import asyncio
import json
import time
from pathlib import Path

from fastapi import Body
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi import Query
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from .deps import run_world  # background sim loop
from .deps import world, governor, event_queue, DEV_TOKEN
from .schemas import StateOut, CommandOut

LOG_PATH = "logs/eterna_runtime.log"


def auth(bearer: str = Header(..., alias="Authorization")):
    if bearer != f"Bearer {DEV_TOKEN}":
        raise HTTPException(401, "Unauthorized")


app = FastAPI(title="Eterna Control API", version="0.1.0")

# Configure CORS
origins = ["http://localhost:5173"]  # Vite dev server

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSET_MAP = json.load(open("assets/zone_assets.json"))
app.mount("/static", StaticFiles(directory="assets/static"), name="static")


@app.get("/zone/assets")
async def zone_assets(name: str):
    return ASSET_MAP.get(name, {})


# ─────────────────────────────  STATE  ──────────────────────────────


class RewardIn(BaseModel):
    value: float


@app.post("/reward/{companion_name}")
async def send_reward(
    companion_name: str, body: RewardIn, dependencies=[Depends(auth)]
):
    companion = world.eterna.get_companion(companion_name)
    if not companion:
        raise HTTPException(404, "companion not found")
    # stash reward so step() can read it
    world.companion_trainer.observe_reward(companion_name, body.value)
    return {"ok": True}


@app.get("/state", response_model=StateOut)
async def get_state():
    tracker = world.state_tracker
    return {
        "cycle": world.eterna.runtime.cycle_count,
        "identity_score": tracker.identity_continuity(),
        "emotion": tracker.last_emotion,
        "modifiers": tracker.applied_modifiers,
        "current_zone": tracker.current_zone(),
    }


# ───────────────────────────  COMMANDS  ─────────────────────────────


# --- modified rollback route ----------------------------------------
@app.post("/command/rollback", response_model=CommandOut, dependencies=[Depends(auth)])
async def rollback(file: str | None = Query(default=None)):
    target = Path(file) if file else None
    governor.rollback(target)
    return {"status": "rolled_back", "detail": str(target) if target else "latest"}


@app.post("/command/{action}", response_model=CommandOut, dependencies=[Depends(auth)])
async def command(action: str):
    match action.lower():
        case "pause":
            governor.pause()
            status = "paused"
        case "resume":
            governor.resume()
            status = "running"
        case "shutdown":
            governor.shutdown("user request")
            status = "shutdown"
            return {"status": status, "detail": "server will stop world loop"}
        case _:
            raise HTTPException(404, "unknown action")
    return {"status": status, "detail": None}


# ────────────────────────────  LOG TAIL  ────────────────────────────
@app.get("/log/stream")
async def stream_logs():
    async def event_generator():
        with open(LOG_PATH) as f:
            f.seek(0, 2)  # go to end
            while True:
                line = f.readline()
                if line:
                    yield {"data": line}
                else:
                    await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())


# ───────────────────────────  WEBSOCKET  ────────────────────────────
clients: set[WebSocket] = set()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    # send a hello packet so the client knows it’s live
    # await ws.send_json({"event": "connected"})
    try:
        while True:
            _ = await ws.receive_text()  # ignore client msgs for now
    except WebSocketDisconnect:
        clients.remove(ws)


# --- list checkpoints -----------------------------------------------
@app.get("/checkpoints")
async def list_checkpoints(dependencies=[Depends(auth)]):
    return world.state_tracker.checkpoints[-10:]  # last 10


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
def list_laws(dependencies=[Depends(auth)]):
    return {name: law.dict() for name, law in governor.laws.items()}


@app.post("/laws/{name}/toggle")
def toggle_law(name: str, enabled: bool = Body(embed=True)):
    governor.laws[name].enabled = enabled
    return {"enabled": enabled}


# register startup task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcaster())
    asyncio.create_task(run_world())  # ← new line


@app.get("/api/agents")
async def list_agents():
    # Access companions through the companions attribute
    agents = world.eterna.companions.companions
    return [
        {
            "name": agent.name,
            "role": agent.role,
            "emotion": getattr(agent, "emotion", None),  # if emotion attribute exists
            "zone": getattr(agent, "zone", None),
            "memory": getattr(agent, "memory", None),
            # Add other info (reward, stats, etc.) as needed
        }
        for agent in agents
    ]


@app.get("/api/zones")
async def list_zones():
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


@app.get("/api/rituals")
async def list_rituals():
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


@app.post("/api/rituals/trigger/{id}")
async def trigger_ritual(id: int):
    # Get rituals from the ritual system
    rituals = list(world.eterna.rituals.rituals.values())
    if id < 0 or id >= len(rituals):
        raise HTTPException(404, "Ritual not found")

    ritual = rituals[id]
    world.eterna.rituals.perform(ritual.name)
    return {"status": "success", "message": f"Ritual '{ritual.name}' triggered"}


@app.get("/api/agent/{name}")
async def get_agent(name: str):
    agent = world.eterna.get_companion(name)
    if not agent:
        raise HTTPException(404, "Agent not found")
    # Expand details as needed
    return {
        "name": agent.name,
        "role": agent.role,
        "emotion": getattr(agent, "emotion", None),
        "zone": getattr(agent, "zone", None),
        "memory": getattr(agent, "memory", None),
        "history": getattr(agent, "history", []),
    }
