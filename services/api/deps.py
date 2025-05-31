import asyncio
import os
import json
import secrets
import logging
from pathlib import Path
from world_builder import build_world
from modules.governor import AlignmentGovernor
from modules.utilities.event_adapter import setup_legacy_adapter
from modules.api_interface import APIInterface
from modules.dependency_injection import get_container, DependencyContainer

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

# Path to store shutdown and pause state
STATE_FILE = Path("artifacts/governor_state.json")

# Initialize the world and governor
container = get_container()

# Check if the container already has the world and governor
if "eterna_interface" not in container._instances and "governor" not in container._instances:
    # Build the world and register it with the container
    world = build_world()
    container.register_instance("eterna_interface", world.eterna)

    # Create the governor and register it with the container
    governor = AlignmentGovernor(world, world.state_tracker, event_queue=event_queue)
    container.register_instance("governor", governor)

    # Register the event queue with the container
    container.register_instance("event_queue", event_queue)
else:
    # Get the world and governor from the container
    world = container.get("eterna_interface")
    governor = container.get("governor")

# Create the API interface
api_interface = APIInterface(world, governor, event_queue)
api_interface.initialize()

# Set up the legacy event adapter to forward events from the event bus to the legacy event queue
legacy_adapter = setup_legacy_adapter(event_queue)

# Load governor state if exists
def load_governor_state():
    """
    Load the governor state (shutdown and pause) from the file system with proper validation and error handling.
    """
    if not STATE_FILE.exists():
        return

    try:
        # Validate the file path to prevent path traversal
        if not STATE_FILE.is_absolute():
            STATE_FILE.resolve()

        with open(STATE_FILE, 'r') as f:
            state = json.load(f)

            # Validate the JSON structure
            if not isinstance(state, dict):
                logging.error("Invalid governor state format: not a dictionary")
                return

            # Use the api_interface to access the governor
            api_interface.governor._shutdown = state.get('shutdown', False)
            api_interface.governor._paused = state.get('paused', False)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in governor state file: {e}")
    except PermissionError as e:
        logging.error(f"Permission denied when reading governor state: {e}")
    except Exception as e:
        logging.error(f"Error loading governor state: {e}")

# Save governor state
def save_governor_state(shutdown=False, paused=False):
    """
    Save the governor state (shutdown and pause) to the file system with proper error handling.
    """
    try:
        # Create directory if it doesn't exist
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Validate the file path to prevent path traversal
        if not STATE_FILE.is_absolute():
            STATE_FILE.resolve()

        # Write to a temporary file first, then rename to ensure atomic write
        temp_file = STATE_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump({
                'shutdown': bool(shutdown),
                'paused': bool(paused)
            }, f)

        # Rename the temporary file to the actual file
        temp_file.replace(STATE_FILE)
    except PermissionError as e:
        logging.error(f"Permission denied when saving governor state: {e}")
    except Exception as e:
        logging.error(f"Error saving governor state: {e}")

# Load governor state on startup, but ensure we're not in shutdown state
# to allow cycles to start running immediately
load_governor_state()
api_interface.governor._shutdown = False  # Ensure we're not in shutdown state
api_interface.governor._paused = False    # Ensure we're not in paused state
save_governor_state(False, False)  # Save the non-shutdown, non-paused state

# ---------------- simulation task ----------------
async def run_world():
    while True:
        # Check if the governor is shutdown or paused and save the state
        if api_interface.governor.is_shutdown():
            # Save governor state to persist across page reloads
            save_governor_state(shutdown=True, paused=api_interface.governor.is_paused())
            # Wait for a long time to effectively stop the simulation
            await asyncio.sleep(10)  # Check every 10 seconds if shutdown is still active
            continue  # Continue checking instead of breaking to allow for resume
        elif api_interface.governor.is_paused():
            # Save governor state to persist across page reloads
            save_governor_state(shutdown=False, paused=True)
            # When paused, add a longer delay to prevent CPU spinning
            await asyncio.sleep(0.5)  # longer delay when paused
            continue  # Skip the rest of the loop
        else:
            # Clear governor state if not shutdown or paused
            save_governor_state(shutdown=False, paused=False)

        # Use the api_interface to execute a step
        metrics = api_interface.world.collect_metrics()
        if api_interface.governor.tick(metrics):
            api_interface.world.step()
            # Use the api_interface to access the world's runtime
            api_interface.world.eterna.runtime.cycle_count += 1  # Increment cycle count
            await asyncio.sleep(0)   # yield when running
        else:
            # This case is handled above now, but keep as a fallback
            # When paused, add a longer delay to prevent CPU spinning
            await asyncio.sleep(0.5) # longer delay when paused
