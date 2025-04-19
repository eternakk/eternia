from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from fastapi import WebSocket, WebSocketDisconnect

from .deps import world, governor
from .schemas import StateOut, CommandOut

LOG_PATH = "logs/eterna_runtime.log"

app = FastAPI(title="Eterna Control API", version="0.1.0")


# ─────────────────────────────  STATE  ──────────────────────────────
@app.get("/state", response_model=StateOut)
async def get_state():
    tracker = world.state_tracker
    return {
        "cycle": tracker.current_cycle,
        "identity_score": tracker.identity_continuity(),
        "emotion": tracker.last_emotion,
        "modifiers": tracker.applied_modifiers,
    }


# ───────────────────────────  COMMANDS  ─────────────────────────────
@app.post("/command/{action}", response_model=CommandOut)
async def command(action: str):
    match action.lower():
        case "pause":
            governor.pause();     status = "paused"
        case "resume":
            governor.resume();    status = "running"
        case "rollback":
            governor.rollback();  status = "rolled_back"
        case "shutdown":
            governor.shutdown("user request"); status = "shutdown"
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
    try:
        while True:
            _ = await ws.receive_text()  # ignore client msgs for now
    except WebSocketDisconnect:
        clients.remove(ws)