"""
Example tests that demonstrate how to use the fixtures.

This module contains example tests that show how to use the fixtures defined in the conftest.py files.
"""

import pytest
from unittest.mock import MagicMock


def test_event_system_fixtures(event_bus, pause_event, resume_event, shutdown_event):
    """Demonstrate how to use the event system fixtures."""
    # Create a mock handler
    mock_handler = MagicMock()
    
    # Subscribe to events
    event_bus.subscribe(type(pause_event), mock_handler)
    event_bus.subscribe(type(resume_event), mock_handler)
    event_bus.subscribe(type(shutdown_event), mock_handler)
    
    # Publish events
    event_bus.publish(pause_event)
    event_bus.publish(resume_event)
    event_bus.publish(shutdown_event)
    
    # Verify that the handler was called for each event
    assert mock_handler.call_count == 3
    mock_handler.assert_any_call(pause_event)
    mock_handler.assert_any_call(resume_event)
    mock_handler.assert_any_call(shutdown_event)


@pytest.mark.parametrize("emotional_state", [
    {"name": "joy", "intensity": 8, "direction": "outward"},
    {"name": "grief", "intensity": 5, "direction": "inward"},
], indirect=True)
def test_emotional_system_fixtures(emotional_circuit_system, emotional_state):
    """Demonstrate how to use the emotional system fixtures with parametrization."""
    # Process the emotion
    emotional_circuit_system.process_emotion(emotional_state)
    
    # Verify that the appropriate methods were called
    if emotional_state.name in ["grief", "awe", "love", "joy", "anger"]:
        emotional_circuit_system.eterna.rituals.perform.assert_called_once()
    elif emotional_state.name == "grief" and emotional_state.intensity > 7:
        emotional_circuit_system.eterna.rituals.perform.assert_called_once_with("Chamber of Waters")
    elif emotional_state.intensity >= 8 and emotional_state.direction == "locked":
        emotional_circuit_system.eterna.rituals.perform.assert_called_once_with("Chamber of Waters")


def test_physics_fixtures(physics_zone_registry, physics_profile):
    """Demonstrate how to use the physics fixtures."""
    # Assign the profile to a zone
    zone_name = "test_zone"
    physics_zone_registry.assign_profile(zone_name, physics_profile)
    
    # Verify that the profile was assigned correctly
    assert physics_zone_registry.get_profile(zone_name) == physics_profile


def test_time_fixtures(time_synchronizer, sensory_profile):
    """Demonstrate how to use the time fixtures."""
    # Adjust the time flow based on the sensory profile
    time_synchronizer.adjust_time_flow(sensory_profile)
    
    # Verify that the time ratio was set correctly
    if sensory_profile.visual_range == "multiplanar":
        assert time_synchronizer.time_ratio == 0.5
    elif sensory_profile.hearing == "resonant":
        assert time_synchronizer.time_ratio == 0.75
    else:
        assert time_synchronizer.time_ratio == 1.0


def test_social_interaction_fixtures(social_interaction_module, user):
    """Demonstrate how to use the social interaction fixtures."""
    # Invite the user
    social_interaction_module.invite_user(user)
    
    # Verify that the user was added to the users list
    assert user in social_interaction_module.users


def test_world_fixtures(mock_world, mock_governor):
    """Demonstrate how to use the world fixtures."""
    # Verify that the world has the expected companions
    assert len(mock_world.eterna.companions.companions) == 1
    assert mock_world.eterna.companions.companions[0].name == "TestCompanion"
    
    # Verify that the world has the expected zones
    assert len(mock_world.eterna.exploration.registry.zones) == 1
    assert mock_world.eterna.exploration.registry.zones[0].name == "TestZone"
    
    # Verify that the governor has the expected methods
    assert not mock_governor.is_shutdown()