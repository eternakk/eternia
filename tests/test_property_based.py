"""
Property-based tests for complex simulation logic.

This module contains property-based tests for complex simulation logic using the Hypothesis library.
"""

import unittest
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st

from modules.emotions import EmotionalState, EmotionalCircuitSystem
from modules.physics import PhysicsProfile, PhysicsZoneRegistry
from modules.time_dilation import TimeSynchronizer


class TestEmotionalCircuitSystem(unittest.TestCase):
    """Property-based tests for the EmotionalCircuitSystem."""

    @given(
        name=st.text(min_size=1, max_size=20),
        intensity=st.integers(min_value=0, max_value=10),
        direction=st.sampled_from(["inward", "outward", "locked", "flowing"])
    )
    def test_process_emotion_does_not_raise_exception(self, name, intensity, direction):
        """Test that process_emotion does not raise an exception for any valid input."""
        # Arrange
        eterna_mock = MagicMock()
        system = EmotionalCircuitSystem(eterna_mock)
        emotion = EmotionalState(name, intensity, direction)
        
        # Act & Assert
        try:
            system.process_emotion(emotion)
        except Exception as e:
            self.fail(f"process_emotion raised {type(e).__name__} unexpectedly!")

    @given(
        name=st.sampled_from(["grief", "awe", "love", "joy", "anger"]),
        intensity=st.integers(min_value=0, max_value=10),
        direction=st.sampled_from(["inward", "outward", "locked", "flowing"])
    )
    def test_process_emotion_with_mapped_emotions(self, name, intensity, direction):
        """Test that process_emotion correctly handles emotions with mappings."""
        # Arrange
        eterna_mock = MagicMock()
        eterna_mock.exploration.registry.get_zones_by_emotion.return_value = []
        system = EmotionalCircuitSystem(eterna_mock)
        emotion = EmotionalState(name, intensity, direction)
        
        # Act
        system.process_emotion(emotion)
        
        # Assert
        # For mapped emotions, the ritual should be performed
        eterna_mock.rituals.perform.assert_called_once()

    @given(
        name=st.text(min_size=1, max_size=20).filter(lambda x: x.lower() not in ["grief", "awe", "love", "joy", "anger"]),
        intensity=st.integers(min_value=8, max_value=10),
        direction=st.just("locked")
    )
    def test_process_emotion_with_locked_high_intensity(self, name, intensity, direction):
        """Test that process_emotion correctly handles locked high-intensity emotions."""
        # Arrange
        eterna_mock = MagicMock()
        system = EmotionalCircuitSystem(eterna_mock)
        emotion = EmotionalState(name, intensity, direction)
        
        # Act
        system.process_emotion(emotion)
        
        # Assert
        # For locked high-intensity emotions, the Chamber of Waters ritual should be performed
        eterna_mock.rituals.perform.assert_called_once_with("Chamber of Waters")


class TestPhysicsZoneRegistry(unittest.TestCase):
    """Property-based tests for the PhysicsZoneRegistry."""

    @given(
        zone_name=st.text(min_size=1, max_size=20),
        profile_name=st.text(min_size=1, max_size=20),
        gravity=st.floats(min_value=0, max_value=20),
        time_flow=st.floats(min_value=0.1, max_value=10),
        dimensions=st.integers(min_value=2, max_value=11),
        energy_behavior=st.sampled_from(["standard", "field-reactive", "thought-sensitive"]),
        conscious_safe=st.just(True)
    )
    def test_assign_profile_with_safe_profile(self, zone_name, profile_name, gravity, time_flow, dimensions, energy_behavior, conscious_safe):
        """Test that assign_profile succeeds for any profile with conscious_safe=True."""
        # Arrange
        registry = PhysicsZoneRegistry()
        profile = PhysicsProfile(profile_name, gravity, time_flow, dimensions, energy_behavior, conscious_safe)
        
        # Act
        registry.assign_profile(zone_name, profile)
        
        # Assert
        self.assertEqual(registry.get_profile(zone_name), profile)

    @given(
        zone_name=st.text(min_size=1, max_size=20),
        profile_name=st.text(min_size=1, max_size=20),
        gravity=st.floats(min_value=0, max_value=20),
        time_flow=st.floats(min_value=0.1, max_value=10),
        dimensions=st.integers(min_value=2, max_value=11),
        energy_behavior=st.sampled_from(["standard", "field-reactive", "thought-sensitive"]),
        conscious_safe=st.just(False)
    )
    def test_assign_profile_with_unsafe_profile(self, zone_name, profile_name, gravity, time_flow, dimensions, energy_behavior, conscious_safe):
        """Test that assign_profile fails for any profile with conscious_safe=False."""
        # Arrange
        registry = PhysicsZoneRegistry()
        profile = PhysicsProfile(profile_name, gravity, time_flow, dimensions, energy_behavior, conscious_safe)
        
        # Act
        registry.assign_profile(zone_name, profile)
        
        # Assert
        self.assertIsNone(registry.get_profile(zone_name))


class TestTimeSynchronizer(unittest.TestCase):
    """Property-based tests for the TimeSynchronizer."""

    @given(
        visual_range=st.sampled_from(["normal", "multiplanar"]),
        hearing=st.sampled_from(["normal", "resonant"]),
        cognitive_load=st.integers(min_value=0, max_value=100)
    )
    def test_adjust_time_flow_properties(self, visual_range, hearing, cognitive_load):
        """Test that adjust_time_flow correctly sets the time_ratio based on sensory profile and cognitive load."""
        # Arrange
        eterna_mock = MagicMock()
        eterna_mock.runtime.state.cognitive_load = cognitive_load
        synchronizer = TimeSynchronizer(eterna_mock)
        sensory_profile = MagicMock()
        sensory_profile.visual_range = visual_range
        sensory_profile.hearing = hearing
        
        # Act
        synchronizer.adjust_time_flow(sensory_profile)
        
        # Assert
        # Check that time_ratio is between 0 and 1
        self.assertGreaterEqual(synchronizer.time_ratio, 0)
        self.assertLessEqual(synchronizer.time_ratio, 1)
        
        # Check specific rules
        if visual_range == "multiplanar":
            self.assertAlmostEqual(synchronizer.time_ratio, 0.5 * (0.8 if cognitive_load > 70 else 1.0), places=6)
        elif hearing == "resonant":
            self.assertAlmostEqual(synchronizer.time_ratio, 0.75 * (0.8 if cognitive_load > 70 else 1.0), places=6)
        else:
            self.assertAlmostEqual(synchronizer.time_ratio, 1.0 * (0.8 if cognitive_load > 70 else 1.0), places=6)


if __name__ == "__main__":
    unittest.main()