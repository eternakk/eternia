import asyncio
import time

from fastapi import FastAPI, HTTPException,Depends, Header
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query
from pathlib import Path
from .deps import world, governor, event_queue, DEV_TOKEN
from .deps import run_world      # background sim loop
from .schemas import StateOut, CommandOut
from fastapi.staticfiles import StaticFiles
import json

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
            governor.pause();     status = "paused"
        case "resume":
            governor.resume();    status = "running"
        case "shutdown":
            governor.shutdown("user request"); status = "shutdown"
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
    return world.state_tracker.checkpoints[-10:]   # last 10

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
    asyncio.create_task(broadcaster())
    asyncio.create_task(run_world())   # ← new line

