"""
Pytest fixtures for integration tests.

This module contains fixtures that are specific to integration tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from services.api.server import app
from services.api.deps import DEV_TOKEN


@pytest.fixture
def client():
    """Return a TestClient instance for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Return authentication headers for API requests."""
    return {"Authorization": f"Bearer {DEV_TOKEN}"}


@pytest.fixture
def patched_governor():
    """Return a context manager that patches the governor in the API server."""
    with patch("services.api.server.governor") as mock_governor:
        mock_governor.is_shutdown.return_value = False
        yield mock_governor


@pytest.fixture
def patched_world():
    """Return a context manager that patches the world in the API server."""
    with patch("services.api.server.world") as mock_world:
        # Set up companions
        companion = MagicMock()
        companion.name = "TestCompanion"
        companion.role = "TestRole"
        companion.emotion = "Happy"
        companion.zone = "TestZone"
        companion.memory = ["Memory1", "Memory2"]
        mock_world.eterna.companions.companions = [companion]

        # Set up zones
        zone = MagicMock()
        zone.name = "TestZone"
        zone.origin = "TestOrigin"
        zone.complexity_level = 3
        zone.explored = True
        zone.emotion_tag = "Peaceful"
        zone.modifiers = ["Modifier1", "Modifier2"]
        mock_world.eterna.exploration.registry.zones = [zone]

        yield mock_world


@pytest.fixture
def patched_save_governor_state():
    """Return a context manager that patches the save_governor_state function."""
    with patch("services.api.deps.save_governor_state") as mock_save:
        yield mock_save

@pytest.fixture
def patched_save_shutdown_state():
    """Return a context manager that patches the save_shutdown_state function (deprecated)."""
    # This fixture is kept for backward compatibility with existing tests
    # New tests should use patched_save_governor_state instead
    with patch("services.api.deps.save_governor_state") as mock_save:
        yield mock_save


@pytest.fixture
def patched_event_queue():
    """Return a context manager that patches the event_queue."""
    with patch("services.api.deps.event_queue") as mock_queue:
        yield mock_queue


@pytest.fixture
def patched_asyncio_create_task():
    """Return a context manager that patches asyncio.create_task."""
    with patch("asyncio.create_task") as mock_create_task:
        yield mock_create_task
