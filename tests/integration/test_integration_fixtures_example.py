"""
Example integration tests that demonstrate how to use the integration fixtures.

This module contains example tests that show how to use the fixtures defined in the tests/integration/conftest.py file.
"""

import pytest
import asyncio


def test_api_client_fixture(client):
    """Demonstrate how to use the client fixture."""
    # Make a request to the API
    response = client.get("/state")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert "cycle" in data
    assert "identity_score" in data
    assert "emotion" in data
    assert "modifiers" in data
    assert "current_zone" in data


def test_auth_headers_fixture(client, auth_headers):
    """Demonstrate how to use the auth_headers fixture."""
    # Make an authenticated request to the API
    response = client.post("/command/rollback", headers=auth_headers)

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rolled_back"


def test_patched_governor_fixture(client, auth_headers, patched_governor):
    """Demonstrate how to use the patched_governor fixture."""
    # Make a request that uses the governor
    response = client.post("/command/pause", headers=auth_headers)

    # Verify the response and that the governor was called
    assert response.status_code == 200
    assert response.json()["status"] == "paused"
    patched_governor.pause.assert_called_once()


def test_patched_world_fixture(client, patched_world):
    """Demonstrate how to use the patched_world fixture."""
    # Make a request that uses the world
    response = client.get("/api/agents")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "TestCompanion"
    assert data[0]["role"] == "TestRole"
    assert data[0]["emotion"] == "Happy"
    assert data[0]["zone"] == "TestZone"


def test_patched_save_shutdown_state_fixture(client, auth_headers, patched_governor, patched_save_shutdown_state):
    """Demonstrate how to use the patched_save_shutdown_state fixture."""
    # Make a request that uses the save_shutdown_state function
    response = client.post("/command/shutdown", headers=auth_headers)

    # Verify the response and that the function was called
    assert response.status_code == 200
    assert response.json()["status"] == "shutdown"
    patched_governor.shutdown.assert_called_once_with("user request")
    patched_save_shutdown_state.assert_called_once_with(shutdown=True, paused=False)


@pytest.mark.asyncio
async def test_patched_event_queue_and_asyncio_create_task_fixtures(client, patched_event_queue, patched_asyncio_create_task):
    """Demonstrate how to use the patched_event_queue and patched_asyncio_create_task fixtures."""
    # Call the startup event handler to trigger the broadcaster task
    for handler in client.app.router.on_startup:
        await handler()

    # Verify that create_task was called at least twice (for broadcaster and run_world)
    assert patched_asyncio_create_task.call_count >= 2
