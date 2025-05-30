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


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for API requests."""
    return {"Authorization": f"Bearer {DEV_TOKEN}"}


class TestAPIIntegration:
    """Integration tests for the API service."""

    def test_get_state(self, client):
        """Test that the /state endpoint returns the correct state."""
        response = client.get("/state")
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
             patch("services.api.deps.save_shutdown_state") as mock_save:
            response = client.post("/command/shutdown", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["status"] == "shutdown"
            mock_governor.shutdown.assert_called_once_with("user request")
            mock_save.assert_called_once_with(True)

    def test_command_rollback(self, client, auth_headers):
        """Test that the rollback command works correctly."""
        with patch("services.api.deps.governor") as mock_governor:
            response = client.post("/command/rollback", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["status"] == "rolled_back"
            mock_governor.rollback.assert_called_once_with(None)

    def test_list_agents(self, client):
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
            
            response = client.get("/api/agents")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "TestCompanion"
            assert data[0]["role"] == "TestRole"
            assert data[0]["emotion"] == "Happy"
            assert data[0]["zone"] == "TestZone"

    def test_list_zones(self, client):
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
            
            response = client.get("/api/zones")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "TestZone"
            assert data[0]["origin"] == "TestOrigin"
            assert data[0]["complexity"] == 3
            assert data[0]["explored"] is True
            assert data[0]["emotion"] == "Peaceful"
            assert data[0]["modifiers"] == ["Modifier1", "Modifier2"]

    def test_authentication(self, client):
        """Test that endpoints requiring authentication reject unauthorized requests."""
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/command/pause", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test with missing token
        response = client.post("/command/pause")
        assert response.status_code == 422  # FastAPI validation error for missing header

    def test_event_broadcasting(self, client):
        """Test that events are correctly broadcast to WebSocket clients."""
        with patch("services.api.deps.event_queue") as mock_queue:
            # This test is more complex as it involves WebSockets
            # In a real test, we would use a WebSocket client to connect and verify events
            # For now, we'll just verify that the broadcaster task is created on startup
            
            # Create a mock for asyncio.create_task
            with patch("asyncio.create_task") as mock_create_task:
                # Call the startup event handler
                for handler in app.router.on_startup:
                    asyncio.run(handler())
                
                # Verify that create_task was called at least twice (for broadcaster and run_world)
                assert mock_create_task.call_count >= 2


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])