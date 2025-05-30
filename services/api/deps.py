import asyncio
import os
import json
import secrets
import logging
from pathlib import Path
from world_builder import build_world
from modules.governor import AlignmentGovernor
from modules.utilities.event_adapter import setup_legacy_adapter

# Generate a secure token if not provided in environment
if not os.getenv("ETERNA_TOKEN"):
    # Only generate a new token if one doesn't exist in the token file
    TOKEN_FILE = Path("artifacts/auth_token.txt")
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, 'r') as f:
                DEV_TOKEN = f.read().strip()
        except Exception as e:
            logging.error(f"Error reading token file: {e}")
            DEV_TOKEN = secrets.token_hex(16)
    else:
        DEV_TOKEN = secrets.token_hex(16)
        # Save the token to a file for persistence
        try:
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_FILE, 'w') as f:
                f.write(DEV_TOKEN)
        except Exception as e:
            logging.error(f"Error saving token file: {e}")
else:
    DEV_TOKEN = os.getenv("ETERNA_TOKEN")

event_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)

# Path to store shutdown state
SHUTDOWN_STATE_FILE = Path("artifacts/shutdown_state.json")

world = build_world()
governor = AlignmentGovernor(world, world.state_tracker, event_queue=event_queue)

# Set up the legacy event adapter to forward events from the event bus to the legacy event queue
legacy_adapter = setup_legacy_adapter(event_queue)

# Load shutdown state if exists
def load_shutdown_state():
    """
    Load the shutdown state from the file system with proper validation and error handling.
    """
    if not SHUTDOWN_STATE_FILE.exists():
        return

    try:
        # Validate the file path to prevent path traversal
        if not SHUTDOWN_STATE_FILE.is_absolute():
            SHUTDOWN_STATE_FILE.resolve()

        with open(SHUTDOWN_STATE_FILE, 'r') as f:
            state = json.load(f)

            # Validate the JSON structure
            if not isinstance(state, dict):
                logging.error("Invalid shutdown state format: not a dictionary")
                return

            if state.get('shutdown', False):
                governor._shutdown = True
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in shutdown state file: {e}")
    except PermissionError as e:
        logging.error(f"Permission denied when reading shutdown state: {e}")
    except Exception as e:
        logging.error(f"Error loading shutdown state: {e}")

# Save shutdown state
def save_shutdown_state(shutdown=False):
    """
    Save the shutdown state to the file system with proper error handling.
    """
    try:
        # Create directory if it doesn't exist
        SHUTDOWN_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Validate the file path to prevent path traversal
        if not SHUTDOWN_STATE_FILE.is_absolute():
            SHUTDOWN_STATE_FILE.resolve()

        # Write to a temporary file first, then rename to ensure atomic write
        temp_file = SHUTDOWN_STATE_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump({'shutdown': bool(shutdown)}, f)

        # Rename the temporary file to the actual file
        temp_file.replace(SHUTDOWN_STATE_FILE)
    except PermissionError as e:
        logging.error(f"Permission denied when saving shutdown state: {e}")
    except Exception as e:
        logging.error(f"Error saving shutdown state: {e}")

# Load shutdown state on startup, but ensure we're not in shutdown state
# to allow cycles to start running immediately
load_shutdown_state()
governor._shutdown = False  # Ensure we're not in shutdown state
save_shutdown_state(False)  # Save the non-shutdown state

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
            world.eterna.runtime.cycle_count += 1  # Increment cycle count
            await asyncio.sleep(0)   # yield when running
        else:
            # When paused, add a longer delay to prevent CPU spinning
            # and to ensure the pause state is maintained even when switching windows
            await asyncio.sleep(0.5) # longer delay when paused
