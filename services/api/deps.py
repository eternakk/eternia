import asyncio
import os
import json
from pathlib import Path
from world_builder import build_world
from modules.governor import AlignmentGovernor
from modules.utilities.event_adapter import setup_legacy_adapter

DEV_TOKEN = os.getenv("ETERNA_TOKEN", "7eba339e71568d9957617382fdb1df65")
event_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)

# Path to store shutdown state
SHUTDOWN_STATE_FILE = Path("artifacts/shutdown_state.json")

world = build_world()
governor = AlignmentGovernor(world, world.state_tracker, event_queue=event_queue)

# Set up the legacy event adapter to forward events from the event bus to the legacy event queue
legacy_adapter = setup_legacy_adapter(event_queue)

# Load shutdown state if exists
def load_shutdown_state():
    if SHUTDOWN_STATE_FILE.exists():
        try:
            with open(SHUTDOWN_STATE_FILE, 'r') as f:
                state = json.load(f)
                if state.get('shutdown', False):
                    governor._shutdown = True
        except Exception as e:
            print(f"Error loading shutdown state: {e}")

# Save shutdown state
def save_shutdown_state(shutdown=False):
    SHUTDOWN_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(SHUTDOWN_STATE_FILE, 'w') as f:
            json.dump({'shutdown': shutdown}, f)
    except Exception as e:
        print(f"Error saving shutdown state: {e}")

# Load shutdown state on startup
load_shutdown_state()

# ---------------- simulation task ----------------
async def run_world():
    while True:
        if governor.is_shutdown():
            # Save shutdown state to persist across page reloads
            save_shutdown_state(True)
            # Wait for a long time to effectively stop the simulation
            await asyncio.sleep(10)  # Check every 10 seconds if shutdown is still active
            continue  # Continue checking instead of breaking to allow for resume
        else:
            # Clear shutdown state if not shutdown
            save_shutdown_state(False)

        metrics = world.collect_metrics()
        if governor.tick(metrics):
            world.step()
            await asyncio.sleep(0)   # yield when running
        else:
            # When paused, add a longer delay to prevent CPU spinning
            # and to ensure the pause state is maintained even when switching windows
            await asyncio.sleep(0.5) # longer delay when paused
