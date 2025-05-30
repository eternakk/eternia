"""
Simulation Modules for Eterna World

This module contains functions for simulating different aspects of the Eterna world,
including emotional events and sensory evolution.

The module uses the configuration system to get values instead of hardcoding them.
"""

from modules.emotions import EmotionalState
from eterna_interface import EternaInterface
from config.config_manager import config


def simulate_emotional_events(eterna: EternaInterface) -> None:
    """
    Simulate emotional events and soul interactions in the Eterna world.

    This function creates an emotional state, processes it through the emotion
    circuits, and simulates soul invitation and presence registration.
    The emotional event configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to use for simulation.
    """
    # Get emotional event configuration
    emotion_config = config.get('simulation.emotional_events', {
        'emotion': 'grief',
        'intensity': 9,
        'direction': 'locked',
        'companion': 'Lira'
    })

    # Create and process emotion
    emotion = EmotionalState(
        emotion_config.get('emotion', 'grief'),
        intensity=emotion_config.get('intensity', 9),
        direction=emotion_config.get('direction', 'locked')
    )
    eterna.emotion_circuits.process_emotion(emotion)

    # Invite and register companion
    companion_name = emotion_config.get('companion', 'Lira')
    eterna.soul_invitations.invite(companion_name)
    eterna.soul_invitations.receive_response(companion_name, accepted=True)
    eterna.soul_presence.register_presence(companion_name)
    eterna.soul_presence.list_present_souls()


def simulate_sensory_evolution(eterna: EternaInterface) -> None:
    """
    Simulate sensory evolution based on physics profiles of zones.

    This function adapts the senses to a specific physics profile,
    updates evolution statistics, and displays a tracker report.
    The sensory evolution configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to use for simulation.
    """
    print("\n🌐 Simulating sensory evolution through physics zones...")

    # Get sensory evolution configuration
    sensory_config = config.get('simulation.sensory_evolution', {
        'zone': 'quantum_forest'
    })

    # Get zone name from configuration
    zone_key = sensory_config.get('zone', 'quantum_forest')
    zone_name = config.get(f'zones.{zone_key}.name', 'Quantum Forest')

    # Get physics profile and adapt senses
    physics_profile = eterna.physics_registry.get_profile(zone_name)

    if physics_profile:
        eterna.adapt_senses(physics_profile)
        eterna.update_evolution_stats()
        eterna.show_tracker_report()
    else:
        print(f"⚠️ No physics profile found for zone: {zone_name}")
