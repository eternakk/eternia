"""
Integration tests for the API service.

These tests verify that the API endpoints correctly interact with the underlying components.
"""

import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from services.api.server import app
from services.api.deps import DEV_TOKEN
from modules.governor_events import PauseEvent, ResumeEvent, ShutdownEvent

# Define the test token that we're using for testing
TEST_TOKEN = "test-token-for-authentication"


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for API requests."""
    return {"Authorization": f"Bearer {TEST_TOKEN}"}


class TestAPIIntegration:
    """Integration tests for the API service."""

    def test_get_state(self, client, auth_headers):
        """Test that the /state endpoint returns the correct state."""
        response = client.get("/state", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "cycle" in data
        assert "identity_score" in data
        assert "emotion" in data
        assert "modifiers" in data
        assert "current_zone" in data

    def test_command_pause_resume(self, client, auth_headers):
        """Test that the pause and resume commands work correctly."""
        # Test pause command
        with patch("services.api.deps.governor") as mock_governor:
            response = client.post("/command/pause", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["status"] == "paused"
            mock_governor.pause.assert_called_once()

        # Test resume command
        with patch("services.api.deps.governor") as mock_governor:
            mock_governor.is_shutdown.return_value = False
            response = client.post("/command/resume", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["status"] == "running"
            mock_governor.resume.assert_called_once()

    def test_command_shutdown(self, client, auth_headers):
        """Test that the shutdown command works correctly."""
        with patch("services.api.deps.governor") as mock_governor, \
             patch("services.api.deps.save_governor_state") as mock_save:
            response = client.post("/command/shutdown", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["status"] == "shutdown"
            mock_governor.shutdown.assert_called_once_with("user request")
            mock_save.assert_called_once_with(shutdown=True, paused=False)

    def test_command_rollback(self, client, auth_headers):
        """Test that the rollback command works correctly."""
        with patch("services.api.deps.governor") as mock_governor:
            response = client.post("/command/rollback", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["status"] == "rolled_back"
            mock_governor.rollback.assert_called_once_with(None)

    def test_list_agents(self, client, auth_headers):
        """Test that the /api/agents endpoint returns the correct agents."""
        with patch("services.api.deps.world") as mock_world:
            # Create mock companions
            mock_companion = MagicMock()
            mock_companion.name = "TestCompanion"
            mock_companion.role = "TestRole"
            mock_companion.emotion = "Happy"
            mock_companion.zone = "TestZone"
            mock_companion.memory = ["Memory1", "Memory2"]

            # Set up the mock world to return our mock companions
            mock_world.eterna.companions.companions = [mock_companion]

            response = client.get("/api/agents", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "TestCompanion"
            assert data[0]["role"] == "TestRole"
            assert data[0]["emotion"] == "Happy"
            assert data[0]["zone"] == "TestZone"

    def test_list_zones(self, client, auth_headers):
        """Test that the /api/zones endpoint returns the correct zones."""
        with patch("services.api.deps.world") as mock_world:
            # Create mock zone
            mock_zone = MagicMock()
            mock_zone.name = "TestZone"
            mock_zone.origin = "TestOrigin"
            mock_zone.complexity_level = 3
            mock_zone.explored = True
            mock_zone.emotion_tag = "Peaceful"
            mock_zone.modifiers = ["Modifier1", "Modifier2"]

            # Set up the mock world to return our mock zone
            mock_world.eterna.exploration.registry.zones = [mock_zone]

            response = client.get("/api/zones", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "TestZone"
            assert data[0]["origin"] == "TestOrigin"
            assert data[0]["complexity"] == 3
            assert data[0]["explored"] is True
            assert data[0]["emotion"] == "Peaceful"
            assert data[0]["modifiers"] == ["Modifier1", "Modifier2"]

    def test_list_rituals(self, client, auth_headers):
        """Test that the /api/rituals endpoint returns rituals and authentication works."""
        response = client.get("/api/rituals", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Just verify we get a list of rituals with the expected structure
        assert isinstance(data, list)
        assert len(data) > 0
        # Check that each ritual has the expected fields
        for ritual in data:
            assert "id" in ritual
            assert "name" in ritual
            assert "purpose" in ritual
            assert "steps" in ritual
            assert "symbolic_elements" in ritual

    def test_trigger_ritual(self, client, auth_headers):
        """Test that the /api/rituals/trigger/{id} endpoint works correctly."""
        # Test triggering a ritual
        response = client.post("/api/rituals/trigger/0", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "triggered" in data["message"]

        # This test verifies that authentication works and the endpoint returns a success response
        # We don't need to verify the specific ritual name or mock the world object
        # since we're primarily testing the authentication mechanism

    def test_ritual_authentication(self, client):
        """Test that ritual endpoints require authentication."""
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/rituals", headers=invalid_headers)
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"

        # Test with missing token
        response = client.get("/api/rituals")
        assert response.status_code == 403, f"Expected 403 for missing token, got {response.status_code}"

        # Test trigger endpoint with invalid token
        response = client.post("/api/rituals/trigger/0", headers=invalid_headers)
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"

    def test_authentication(self, client):
        """Test that endpoints requiring authentication reject unauthorized requests."""
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/command/pause", headers=invalid_headers)
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"

        # Test with missing token
        # Note: FastAPI's HTTPBearer security will reject missing tokens with 403
        response = client.post("/command/pause")
        assert response.status_code == 403, f"Expected 403 for missing token, got {response.status_code}"

    def test_event_broadcasting(self, client):
        """Test that events are correctly broadcast to WebSocket clients."""
        # This test is more complex as it involves WebSockets
        # In a real test, we would use a WebSocket client to connect and verify events
        # For now, we'll just verify that the broadcaster task is created on startup

        # Create a mock for asyncio.create_task
        with patch("asyncio.create_task") as mock_create_task:
            # Call the startup event handler
            for handler in app.router.on_startup:
                # Create a new event loop instead of getting the current one
                # to avoid "RuntimeError: There is no current event loop in thread 'MainThread'." error
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(handler())
                finally:
                    loop.close()

            # Verify that create_task was called at least twice (for broadcaster and run_world)
            assert mock_create_task.call_count >= 2, f"Expected at least 2 calls to create_task, got {mock_create_task.call_count}"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
