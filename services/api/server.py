import asyncio
import time

from fastapi import FastAPI, HTTPException,Depends, Header
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .deps import world, governor, event_queue, DEV_TOKEN
from .deps import run_world      # background sim loop
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

# ─────────────────────────────  STATE  ──────────────────────────────
@app.get("/state", response_model=StateOut, dependencies=[Depends(auth)])
async def get_state():
    tracker = world.state_tracker
    return {
        "cycle": world.eterna.runtime.cycle_count,
        "identity_score": tracker.identity_continuity(),
        "emotion": tracker.last_emotion,
        "modifiers": tracker.applied_modifiers,
    }


# ───────────────────────────  COMMANDS  ─────────────────────────────
@app.post("/command/{action}", response_model=CommandOut, dependencies=[Depends(auth)])
async def command(action: str):
    match action.lower():
        case "pause":
            governor.pause();     status = "paused"
        case "resume":
            governor.resume();    status = "running"
        case "rollback":
            governor.rollback();  status = "rolled_back"
            return {"status": status, "detail": "rolled to last checkpoint"}
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