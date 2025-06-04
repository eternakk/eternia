"""
Pytest fixtures for fixture tests.

This module imports fixtures from tests/integration/conftest.py to make them available to tests in this directory.
"""

import sys
from pathlib import Path

# Add the project root to the Python path to ensure imports work in all environments
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.conftest import (
    client,
    auth_headers,
    patched_governor,
    patched_world,
    patched_save_governor_state,
    patched_save_shutdown_state,
    patched_event_queue,
    patched_asyncio_create_task,
)
