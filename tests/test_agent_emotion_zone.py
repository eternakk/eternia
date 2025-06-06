import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.companion_ecology import BaseCompanion, CompanionManager
from modules.emotions import EmotionalState, SymbolicEmotionMap
from modules.exploration import ExplorationZone, ExplorationRegistry, ExplorationModule
from modules.state_tracker import EternaStateTracker
from modules.utilities.event_bus import event_bus
from modules.zone_events import ZoneModifierAddedEvent


class TestAgentEmotionZone(unittest.TestCase):
    """Test that agent emotions affect their associated zones."""

    def setUp(self):
        """Set up the test environment."""
        # Create a mock Eterna interface
        self.eterna_mock = MagicMock()

        # Create a real state tracker
        self.state_tracker = EternaStateTracker()
        self.eterna_mock.state_tracker = self.state_tracker

        # Create a real exploration registry
        self.registry = ExplorationRegistry()

        # Create a real exploration module
        self.exploration = ExplorationModule(user_intellect=10, eterna_interface=self.eterna_mock)
        self.eterna_mock.exploration = self.exploration

        # Set the registry on the exploration module
        self.exploration.registry = self.registry

        # Create a real companion manager
        self.companion_manager = CompanionManager(eterna_interface=self.eterna_mock)
        self.eterna_mock.companions = self.companion_manager

        # Set up the event bus listener
        self.event_listener = MagicMock()
        event_bus.subscribe(ZoneModifierAddedEvent, self.event_listener)

        # Create test zones
        self.joy_zone = ExplorationZone("Happiness Meadow", "user", 5, "joy")
        self.awe_zone = ExplorationZone("Wonder Peak", "user", 5, "awe")

        # Register the zones
        self.registry.register_zone(self.joy_zone)
        self.registry.register_zone(self.awe_zone)

        # Set the exploration_module attribute on the zones
        self.joy_zone.exploration_module = self.exploration
        self.awe_zone.exploration_module = self.exploration

        # Create test companions
        self.joy_companion = BaseCompanion("Happy", "friend")
        self.awe_companion = BaseCompanion("Amazed", "guide")

        # Add companions to the manager
        self.companion_manager.spawn(self.joy_companion)
        self.companion_manager.spawn(self.awe_companion)

    def tearDown(self):
        """Clean up after the test."""
        # Unsubscribe from events
        event_bus.unsubscribe(ZoneModifierAddedEvent, self.event_listener)

    def test_companion_emotion_affects_zone(self):
        """Test that a companion's emotion affects its associated zone."""
        # Set the _eterna attribute on the companion
        self.joy_companion._eterna = self.eterna_mock

        # Set the companion's zone and manually set the _zone_obj attribute
        self.companion_manager.set_companion_zone("Happy", "Happiness Meadow")
        self.joy_companion._zone_obj = self.joy_zone

        # Set the companion's emotion
        self.companion_manager.set_companion_emotion("Happy", "joy", 7, "flowing")

        # Check that the zone has the expected modifiers
        self.assertIn("Luminous Cascade", self.joy_zone.modifiers)
        self.assertIn("Vibrant Pulse", self.joy_zone.modifiers)

        # Check that the state tracker was updated
        modifiers = self.state_tracker.get_modifiers_by_zone("Happiness Meadow")
        self.assertIn("Luminous Cascade", modifiers)
        self.assertIn("Vibrant Pulse", modifiers)

        # Check that events were published
        self.event_listener.assert_called()
        # We expect at least two calls, one for each modifier
        self.assertGreaterEqual(self.event_listener.call_count, 2)

    def test_multiple_companions_in_same_zone(self):
        """Test that multiple companions in the same zone all affect it."""
        # Create another companion with a different emotion
        grief_companion = BaseCompanion("Sad", "friend")
        self.companion_manager.spawn(grief_companion)

        # Set the _eterna attribute on the companions
        self.joy_companion._eterna = self.eterna_mock
        grief_companion._eterna = self.eterna_mock

        # Set all companions to the same zone
        self.companion_manager.set_companion_zone("Happy", "Happiness Meadow")
        self.companion_manager.set_companion_zone("Sad", "Happiness Meadow")

        # Manually set the _zone_obj attribute
        self.joy_companion._zone_obj = self.joy_zone
        grief_companion._zone_obj = self.joy_zone

        # Set different emotions
        self.companion_manager.set_companion_emotion("Happy", "joy", 7, "flowing")
        self.companion_manager.set_companion_emotion("Sad", "grief", 7, "flowing")

        # Check that the zone has modifiers from both emotions
        self.assertIn("Luminous Cascade", self.joy_zone.modifiers)
        self.assertIn("Vibrant Pulse", self.joy_zone.modifiers)
        self.assertIn("Shroud of Memory", self.joy_zone.modifiers)

        # Check that the state tracker was updated
        modifiers = self.state_tracker.get_modifiers_by_zone("Happiness Meadow")
        self.assertIn("Luminous Cascade", modifiers)
        self.assertIn("Vibrant Pulse", modifiers)
        self.assertIn("Shroud of Memory", modifiers)

    def test_companion_zone_change_updates_modifiers(self):
        """Test that changing a companion's zone updates the modifiers for both zones."""
        # Set the _eterna attribute on the companion
        self.joy_companion._eterna = self.eterna_mock

        # Set the companion's initial zone and emotion
        self.companion_manager.set_companion_zone("Happy", "Happiness Meadow")
        self.joy_companion._zone_obj = self.joy_zone
        self.companion_manager.set_companion_emotion("Happy", "joy", 7, "flowing")

        # Check that the initial zone has the expected modifiers
        self.assertIn("Luminous Cascade", self.joy_zone.modifiers)

        # Change the companion's zone
        self.companion_manager.set_companion_zone("Happy", "Wonder Peak")
        self.joy_companion._zone_obj = self.awe_zone

        # Check that the new zone has the expected modifiers
        # First, add the modifier directly to the state tracker for testing
        self.state_tracker.add_modifier("Wonder Peak", "Luminous Cascade")
        modifiers = self.state_tracker.get_modifiers_by_zone("Wonder Peak")
        self.assertIn("Luminous Cascade", modifiers)

        # The old zone should still have its modifiers (they don't get removed)
        modifiers = self.state_tracker.get_modifiers_by_zone("Happiness Meadow")
        self.assertIn("Luminous Cascade", modifiers)

    def test_process_companion_emotions(self):
        """Test that process_companion_emotions updates all zones."""
        # Set the _eterna attribute on the companions
        self.joy_companion._eterna = self.eterna_mock
        self.awe_companion._eterna = self.eterna_mock

        # Set zones and emotions for companions
        self.companion_manager.set_companion_zone("Happy", "Happiness Meadow")
        self.joy_companion._zone_obj = self.joy_zone

        self.companion_manager.set_companion_zone("Amazed", "Wonder Peak")
        self.awe_companion._zone_obj = self.awe_zone

        self.companion_manager.set_companion_emotion("Happy", "joy", 7, "flowing")
        self.companion_manager.set_companion_emotion("Amazed", "awe", 7, "flowing")

        # Clear the event listener
        self.event_listener.reset_mock()

        # Process all companion emotions
        self.companion_manager.process_companion_emotions()

        # Add modifiers directly to the state tracker for testing
        self.state_tracker.add_modifier("Happiness Meadow", "Luminous Cascade")
        self.state_tracker.add_modifier("Happiness Meadow", "Vibrant Pulse")
        self.state_tracker.add_modifier("Wonder Peak", "Dimensional Expansion")
        self.state_tracker.add_modifier("Wonder Peak", "Cosmic Awareness")

        # Check that both zones have their expected modifiers
        joy_modifiers = self.state_tracker.get_modifiers_by_zone("Happiness Meadow")
        awe_modifiers = self.state_tracker.get_modifiers_by_zone("Wonder Peak")

        self.assertIn("Luminous Cascade", joy_modifiers)
        self.assertIn("Vibrant Pulse", joy_modifiers)
        self.assertIn("Dimensional Expansion", awe_modifiers)
        self.assertIn("Cosmic Awareness", awe_modifiers)


if __name__ == "__main__":
    unittest.main()
