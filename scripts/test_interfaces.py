#!/usr/bin/env python3
"""
Test script for verifying that interfaces are properly implemented.

This script creates instances of all the classes that implement interfaces
and calls methods on them to ensure they work correctly.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.awareness import MultidimensionalAwareness
from modules.consciousness_replica import ConsciousnessReplica
from modules.emotional_safety import EmotionalSafetyModule
from modules.evolution import UserEvolution
from modules.exploration import ExplorationModule, ExplorationZone
from modules.memory_integration import MemoryIntegrationModule, Memory
from modules.runtime import EternaRuntime
from modules.social_interaction import SocialInteractionModule
from modules.state_tracker import EternaStateTracker

from modules.interfaces import (
    AwarenessInterface,
    ConsciousnessInterface,
    EmotionalInterface,
    EvolutionInterface,
    ExplorationInterface,
    MemoryInterface,
    RuntimeInterface,
    SocialInterface,
    StateTrackerInterface,
)


def test_evolution_interface():
    """Test that UserEvolution properly implements EvolutionInterface."""
    print("\n=== Testing EvolutionInterface ===")
    evolution = UserEvolution()

    # Verify that it implements the interface
    assert isinstance(evolution, EvolutionInterface)

    # Test the methods
    evolution.initialize()
    evolution.evolve(10, 5)
    assert evolution.intellect == 110
    evolution.shutdown()

    print("✅ UserEvolution properly implements EvolutionInterface")


def test_consciousness_interface():
    """Test that ConsciousnessReplica properly implements ConsciousnessInterface."""
    print("\n=== Testing ConsciousnessInterface ===")
    replica = ConsciousnessReplica()

    # Verify that it implements the interface
    assert isinstance(replica, ConsciousnessInterface)

    # Test the methods
    replica.initialize()
    replica.calibrate({"status": "perfect"})
    replica.shutdown()

    print("✅ ConsciousnessReplica properly implements ConsciousnessInterface")


def test_awareness_interface():
    """Test that MultidimensionalAwareness properly implements AwarenessInterface."""
    print("\n=== Testing AwarenessInterface ===")
    awareness = MultidimensionalAwareness()

    # Verify that it implements the interface
    assert isinstance(awareness, AwarenessInterface)

    # Test the methods
    awareness.initialize()
    awareness.integrate_new_dimension()
    assert awareness.dimensions == 4
    awareness.shutdown()

    print("✅ MultidimensionalAwareness properly implements AwarenessInterface")


def test_social_interface():
    """Test that SocialInteractionModule properly implements SocialInterface."""
    print("\n=== Testing SocialInterface ===")
    social = SocialInteractionModule()

    # Verify that it implements the interface
    assert isinstance(social, SocialInterface)

    # Test the methods
    social.initialize()
    social.invite_user({"name": "TestUser", "intellect": 120, "emotional_maturity": 120, "consent": True})
    social.initiate_safe_interaction("TestUser", "NonExistentUser")
    social.shutdown()

    print("✅ SocialInteractionModule properly implements SocialInterface")


def test_emotional_interface():
    """Test that EmotionalSafetyModule properly implements EmotionalInterface."""
    print("\n=== Testing EmotionalInterface ===")
    emotional = EmotionalSafetyModule()

    # Verify that it implements the interface
    assert isinstance(emotional, EmotionalInterface)

    # Test the methods
    emotional.initialize()
    emotional.update_emotional_state("calm", 3)
    assert emotional.monitor_and_manage_emotions() is True
    emotional.shutdown()

    print("✅ EmotionalSafetyModule properly implements EmotionalInterface")


def test_memory_interface():
    """Test that MemoryIntegrationModule properly implements MemoryInterface."""
    print("\n=== Testing MemoryInterface ===")
    memory_module = MemoryIntegrationModule()

    # Verify that it implements the interface
    assert isinstance(memory_module, MemoryInterface)

    # Test the methods
    memory_module.initialize()
    memory = Memory("Test memory", 8, "positive")
    result = memory_module.process_memory(memory)
    assert isinstance(result, dict)
    memory_module.shutdown()

    print("✅ MemoryIntegrationModule properly implements MemoryInterface")


def test_exploration_interface():
    """Test that ExplorationModule properly implements ExplorationInterface."""
    print("\n=== Testing ExplorationInterface ===")
    exploration = ExplorationModule(user_intellect=100)

    # Verify that it implements the interface
    assert isinstance(exploration, ExplorationInterface)

    # Test the methods
    exploration.initialize()
    zone = ExplorationZone("TestZone", "test", 50)
    exploration.register_zone(zone)
    # Note: explore_random_zone requires more setup, so we'll skip testing it fully
    exploration.shutdown()

    print("✅ ExplorationModule properly implements ExplorationInterface")


def test_runtime_interface():
    """Test that EternaRuntime properly implements RuntimeInterface."""
    print("\n=== Testing RuntimeInterface ===")
    # Create a mock EternaInterface
    class MockEterna:
        def __init__(self):
            self.evolution = UserEvolution()
            self.emotion_circuits = type('obj', (object,), {
                'current_emotion': None
            })
            self.check_emotional_safety = lambda: None
            self.exploration = type('obj', (object,), {
                'explore_random_zone': lambda return_zone=False: None,
                'registry': type('obj', (object,), {
                    'get_zones_by_emotion': lambda name: []
                })
            })
            self.periodic_discovery_update = lambda: None
            self.assign_challenge_to_users = lambda users: None
            self.evolve_user = lambda i, s: None
            self.synchronize_time = lambda: None
            self.deploy_reality_agent = lambda conditions: None
            self.state_tracker = type('obj', (object,), {
                'last_zone_explored': lambda: None,
                'mark_zone': lambda name: None,
                'update_evolution': lambda intellect, senses: None
            })

    runtime = EternaRuntime(MockEterna())

    # Verify that it implements the interface
    assert isinstance(runtime, RuntimeInterface)

    # Test the methods
    runtime.initialize()
    # Note: run_cycle requires more setup, so we'll skip testing it fully
    runtime.shutdown()

    print("✅ EternaRuntime properly implements RuntimeInterface")


def test_state_tracker_interface():
    """Test that EternaStateTracker properly implements StateTrackerInterface."""
    print("\n=== Testing StateTrackerInterface ===")
    tracker = EternaStateTracker()

    # Verify that it implements the interface
    assert isinstance(tracker, StateTrackerInterface)

    # Test the methods
    tracker.initialize()
    tracker.update_emotion("joy")
    tracker.add_memory({"description": "Test memory", "clarity": 8, "emotional_quality": "positive"})
    tracker.record_discovery("Test discovery")
    tracker.mark_zone_explored("TestZone")
    tracker.update_evolution(110, 105)
    # Note: save and load interact with the file system, so we'll skip testing them fully
    tracker.shutdown()

    print("✅ EternaStateTracker properly implements StateTrackerInterface")


def main():
    """Run all the interface tests."""
    print("Testing interfaces implementation...")

    test_evolution_interface()
    test_consciousness_interface()
    test_awareness_interface()
    test_social_interface()
    test_emotional_interface()
    test_memory_interface()
    test_exploration_interface()
    test_runtime_interface()
    test_state_tracker_interface()

    print("\n✅ All interfaces are properly implemented!")


if __name__ == "__main__":
    main()
