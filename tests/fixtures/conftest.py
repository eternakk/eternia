"""
Pytest fixtures for fixture example tests.

This module imports fixtures from the integration tests conftest.py to make them available
for the example tests in this directory.
"""

import pytest
from tests.integration.conftest import (
    client,
    auth_headers,
    patched_governor,
    patched_world,
    patched_save_shutdown_state,
    patched_event_queue,
    patched_asyncio_create_task
)

# Re-export the fixtures
__all__ = [
    'client',
    'auth_headers',
    'patched_governor',
    'patched_world',
    'patched_save_shutdown_state',
    'patched_event_queue',
    'patched_asyncio_create_task'
]