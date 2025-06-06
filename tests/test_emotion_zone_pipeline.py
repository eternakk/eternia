import unittest
from unittest.mock import MagicMock, patch

from modules.emotions import EmotionalState, EmotionalCircuitSystem, SymbolicEmotionMap
from modules.exploration import ExplorationZone, ExplorationRegistry, ExplorationModule
from modules.state_tracker import EternaStateTracker
from modules.utilities.event_bus import event_bus
from modules.zone_events import ZoneModifierAddedEvent


class TestEmotionZonePipeline(unittest.TestCase):
    """Test the emotion-to-zone-modifier pipeline."""

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

        # Create a real emotional circuit system
        self.emotion_circuits = EmotionalCircuitSystem(eterna_interface=self.eterna_mock)
        self.eterna_mock.emotion_circuits = self.emotion_circuits

        # Set up the event bus listener
        self.event_listener = MagicMock()
        event_bus.subscribe(ZoneModifierAddedEvent, self.event_listener)

        # Create test zones linked to emotions
        self.grief_zone = ExplorationZone("Sorrow Valley", "user", 5, "grief")
        self.awe_zone = ExplorationZone("Wonder Peak", "user", 5, "awe")
        self.joy_zone = ExplorationZone("Happiness Meadow", "user", 5, "joy")

        # Register the zones
        self.registry.register_zone(self.grief_zone)
        self.registry.register_zone(self.awe_zone)
        self.registry.register_zone(self.joy_zone)

        # Set the registry on the exploration module
        self.exploration.registry = self.registry

        # Set the exploration_module attribute on the zones
        self.grief_zone.exploration_module = self.exploration
        self.awe_zone.exploration_module = self.exploration
        self.joy_zone.exploration_module = self.exploration

    def tearDown(self):
        """Clean up after the test."""
        # Unsubscribe from events
        event_bus.unsubscribe(ZoneModifierAddedEvent, self.event_listener)

    def test_emotion_affects_linked_zone(self):
        """Test that an emotion affects its linked zone."""
        # Create an emotion
        grief_emotion = EmotionalState("grief", 7, "flowing")

        # Debug: Print all zones in the registry
        print(f"All zones in registry: {[z.name for z in self.registry.zones]}")
        print(f"All emotion tags in registry: {[z.emotion_tag for z in self.registry.zones]}")

        # Debug: Print the emotion name being searched for
        print(f"Searching for zones with emotion tag: '{grief_emotion.name}'")

        # Debug: Print the zones found by get_zones_by_emotion
        linked_zones = self.registry.get_zones_by_emotion(grief_emotion.name)
        print(f"Found {len(linked_zones)} zones linked to emotion '{grief_emotion.name}'")

        # Process the emotion
        self.emotion_circuits.process_emotion(grief_emotion)

        # Debug: Print the modifiers on the grief zone
        print(f"Modifiers on grief zone: {self.grief_zone.modifiers}")

        # Check that the zone has the expected modifiers
        self.assertIn("Shroud of Memory", self.grief_zone.modifiers)

        # Check that the state tracker was updated
        modifiers = self.state_tracker.get_modifiers_by_zone("Sorrow Valley")
        self.assertIn("Shroud of Memory", modifiers)

        # Check that an event was published
        self.event_listener.assert_called()
        event = self.event_listener.call_args[0][0]
        self.assertIsInstance(event, ZoneModifierAddedEvent)
        self.assertEqual(event.zone_name, "Sorrow Valley")
        self.assertEqual(event.modifier, "Shroud of Memory")

    def test_emotion_affects_multiple_zones(self):
        """Test that an emotion affects multiple linked zones."""
        # Create a second zone linked to grief
        grief_zone2 = ExplorationZone("Mourning Lake", "user", 5, "grief")
        self.registry.register_zone(grief_zone2)

        # Set the exploration_module attribute on the second grief zone
        grief_zone2.exploration_module = self.exploration

        # Create an emotion
        grief_emotion = EmotionalState("grief", 7, "flowing")

        # Process the emotion
        self.emotion_circuits.process_emotion(grief_emotion)

        # Check that both zones have the expected modifiers
        self.assertIn("Shroud of Memory", self.grief_zone.modifiers)
        self.assertIn("Shroud of Memory", grief_zone2.modifiers)

        # Check that the state tracker was updated for both zones
        modifiers1 = self.state_tracker.get_modifiers_by_zone("Sorrow Valley")
        modifiers2 = self.state_tracker.get_modifiers_by_zone("Mourning Lake")
        self.assertIn("Shroud of Memory", modifiers1)
        self.assertIn("Shroud of Memory", modifiers2)

        # Check that events were published for both zones
        self.assertEqual(self.event_listener.call_count, 2)

    def test_emotion_does_not_affect_unlinked_zone(self):
        """Test that an emotion does not affect unlinked zones."""
        # Create an emotion
        grief_emotion = EmotionalState("grief", 7, "flowing")

        # Process the emotion
        self.emotion_circuits.process_emotion(grief_emotion)

        # Check that unlinked zones don't have the modifier
        self.assertNotIn("Shroud of Memory", self.awe_zone.modifiers)
        self.assertNotIn("Shroud of Memory", self.joy_zone.modifiers)

        # Check that the state tracker was not updated for unlinked zones
        modifiers_awe = self.state_tracker.get_modifiers_by_zone("Wonder Peak")
        modifiers_joy = self.state_tracker.get_modifiers_by_zone("Happiness Meadow")
        self.assertNotIn("Shroud of Memory", modifiers_awe)
        self.assertNotIn("Shroud of Memory", modifiers_joy)

    def test_different_emotions_affect_different_zones(self):
        """Test that different emotions affect their respective linked zones."""
        # Create emotions
        grief_emotion = EmotionalState("grief", 7, "flowing")
        awe_emotion = EmotionalState("awe", 7, "flowing")

        # Process the emotions
        self.emotion_circuits.process_emotion(grief_emotion)
        self.emotion_circuits.process_emotion(awe_emotion)

        # Check that each zone has its expected modifiers
        self.assertIn("Shroud of Memory", self.grief_zone.modifiers)
        self.assertIn("Dimensional Expansion", self.awe_zone.modifiers)
        self.assertIn("Cosmic Awareness", self.awe_zone.modifiers)

        # Check that the state tracker was updated correctly
        grief_modifiers = self.state_tracker.get_modifiers_by_zone("Sorrow Valley")
        awe_modifiers = self.state_tracker.get_modifiers_by_zone("Wonder Peak")
        self.assertIn("Shroud of Memory", grief_modifiers)
        self.assertIn("Dimensional Expansion", awe_modifiers)
        self.assertIn("Cosmic Awareness", awe_modifiers)

    def test_high_intensity_emotion_still_affects_zones(self):
        """Test that high intensity emotions still affect their linked zones."""
        # Create a high intensity emotion
        grief_emotion = EmotionalState("grief", 10, "locked")

        # Process the emotion
        self.emotion_circuits.process_emotion(grief_emotion)

        # Check that the zone still has the expected modifiers
        self.assertIn("Shroud of Memory", self.grief_zone.modifiers)

        # Check that the state tracker was updated
        modifiers = self.state_tracker.get_modifiers_by_zone("Sorrow Valley")
        self.assertIn("Shroud of Memory", modifiers)


if __name__ == "__main__":
    unittest.main()
