"""
Pytest fixtures for the Eternia project.

This module contains fixtures that can be used across all tests in the project.
"""

import pytest
from unittest.mock import MagicMock
import time

from modules.utilities.event_bus import EventBus, Event, EventListener, EventPriority
from modules.governor_events import PauseEvent, ResumeEvent, ShutdownEvent
from modules.emotions import EmotionalState, EmotionalCircuitSystem
from modules.physics import PhysicsProfile, PhysicsZoneRegistry
from modules.time_dilation import TimeSynchronizer
from modules.social_interaction import SocialInteractionModule
from modules.population import User


# Event System Fixtures

@pytest.fixture
def event_bus():
    """Return a fresh EventBus instance."""
    return EventBus()


@pytest.fixture
def pause_event():
    """Return a PauseEvent instance."""
    return PauseEvent(timestamp=time.time())


@pytest.fixture
def resume_event():
    """Return a ResumeEvent instance."""
    return ResumeEvent(timestamp=time.time())


@pytest.fixture
def shutdown_event():
    """Return a ShutdownEvent instance."""
    return ShutdownEvent(timestamp=time.time(), reason="Test shutdown")


# Emotional System Fixtures

@pytest.fixture
def emotional_state(request):
    """
    Return an EmotionalState instance.
    
    Parameters can be customized using indirect parametrization:
    @pytest.mark.parametrize("emotional_state", [
        {"name": "joy", "intensity": 8, "direction": "outward"},
        {"name": "grief", "intensity": 5, "direction": "inward"},
    ], indirect=True)
    """
    params = getattr(request, "param", {})
    name = params.get("name", "neutral")
    intensity = params.get("intensity", 5)
    direction = params.get("direction", "inward")
    return EmotionalState(name, intensity, direction)


@pytest.fixture
def emotional_circuit_system():
    """Return an EmotionalCircuitSystem instance with a mocked Eterna interface."""
    eterna_mock = MagicMock()
    eterna_mock.exploration.registry.get_zones_by_emotion.return_value = []
    return EmotionalCircuitSystem(eterna_mock)


# Physics Fixtures

@pytest.fixture
def physics_profile(request):
    """
    Return a PhysicsProfile instance.
    
    Parameters can be customized using indirect parametrization:
    @pytest.mark.parametrize("physics_profile", [
        {"name": "standard", "gravity": 9.8, "time_flow": 1.0, "dimensions": 3, "energy_behavior": "standard", "conscious_safe": True},
        {"name": "low_gravity", "gravity": 2.0, "time_flow": 1.0, "dimensions": 3, "energy_behavior": "standard", "conscious_safe": True},
    ], indirect=True)
    """
    params = getattr(request, "param", {})
    name = params.get("name", "standard")
    gravity = params.get("gravity", 9.8)
    time_flow = params.get("time_flow", 1.0)
    dimensions = params.get("dimensions", 3)
    energy_behavior = params.get("energy_behavior", "standard")
    conscious_safe = params.get("conscious_safe", True)
    return PhysicsProfile(name, gravity, time_flow, dimensions, energy_behavior, conscious_safe)


@pytest.fixture
def physics_zone_registry():
    """Return a PhysicsZoneRegistry instance."""
    return PhysicsZoneRegistry()


# Time Fixtures

@pytest.fixture
def time_synchronizer():
    """Return a TimeSynchronizer instance with a mocked Eterna interface."""
    eterna_mock = MagicMock()
    eterna_mock.runtime.state.cognitive_load = 50
    return TimeSynchronizer(eterna_mock)


@pytest.fixture
def sensory_profile(request):
    """
    Return a mocked sensory profile.
    
    Parameters can be customized using indirect parametrization:
    @pytest.mark.parametrize("sensory_profile", [
        {"visual_range": "normal", "hearing": "normal"},
        {"visual_range": "multiplanar", "hearing": "resonant"},
    ], indirect=True)
    """
    params = getattr(request, "param", {})
    profile = MagicMock()
    profile.visual_range = params.get("visual_range", "normal")
    profile.hearing = params.get("hearing", "normal")
    return profile


# Social Interaction Fixtures

@pytest.fixture
def social_interaction_module():
    """Return a SocialInteractionModule instance."""
    module = SocialInteractionModule()
    module.ims = MagicMock()
    module.ccs = MagicMock()
    return module


@pytest.fixture
def user(request):
    """
    Return a mocked User instance.
    
    Parameters can be customized using indirect parametrization:
    @pytest.mark.parametrize("user", [
        {"name": "test_user", "is_allowed": True},
        {"name": "blocked_user", "is_allowed": False},
    ], indirect=True)
    """
    params = getattr(request, "param", {})
    name = params.get("name", "test_user")
    is_allowed_value = params.get("is_allowed", True)
    
    user = MagicMock(spec=User)
    user.name = name
    user.is_allowed.return_value = is_allowed_value
    return user


# World Fixtures

@pytest.fixture
def mock_world():
    """Return a mocked world instance."""
    world = MagicMock()
    
    # Set up companions
    companion = MagicMock()
    companion.name = "TestCompanion"
    companion.role = "TestRole"
    companion.emotion = "Happy"
    companion.zone = "TestZone"
    companion.memory = ["Memory1", "Memory2"]
    world.eterna.companions.companions = [companion]
    
    # Set up zones
    zone = MagicMock()
    zone.name = "TestZone"
    zone.origin = "TestOrigin"
    zone.complexity_level = 3
    zone.explored = True
    zone.emotion_tag = "Peaceful"
    zone.modifiers = ["Modifier1", "Modifier2"]
    world.eterna.exploration.registry.zones = [zone]
    
    return world


@pytest.fixture
def mock_governor():
    """Return a mocked governor instance."""
    governor = MagicMock()
    governor.is_shutdown.return_value = False
    return governor