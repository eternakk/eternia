"""
Setup Modules for Eterna World

This module contains functions for setting up different aspects of the Eterna world,
including symbolic modifiers, zones, physics profiles, rituals, companions, protection,
resonance engine, and time and agents.

The module uses the configuration system to get values instead of hardcoding them.
"""

from typing import Any, Dict, List, Optional, Union, Tuple

from modules.ai_ml_rl.rl_companion_loop import PPOTrainer
from modules.companion_ecology import MemoryEcho, LocalAgent, SymbolicBeing
from modules.emotions import EmotionalState
from modules.memory_integration import Memory
from modules.physics import PhysicsProfile
from modules.population import User
from modules.resonance_engine import ResonanceEngine
from modules.rituals import Ritual
from modules.zone_modifiers import SymbolicModifier
from eterna_interface import EternaInterface
from config.config_manager import config


def setup_symbolic_modifiers(eterna: EternaInterface) -> None:
    """
    Set up symbolic modifiers for the Eterna world.

    This function creates and registers symbolic modifiers that can be triggered
    by emotions and affect the appearance and behavior of zones.
    The symbolic modifier configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.
    """
    # Add a default symbolic modifier if none are configured
    if not config.get('symbolic_modifiers'):
        shroud = SymbolicModifier(
            name="Shroud of Memory",
            trigger_emotion="grief",
            effects=[
                "colors desaturate",
                "fog rolls in from the sea",
                "sorrow altar emerges from the rocks",
                "ambient cello music plays from the mist",
            ],
        )
        eterna.modifiers.register_modifier(shroud)
    else:
        # Set up symbolic modifiers from configuration
        for modifier_key in config.get('symbolic_modifiers', {}):
            modifier_config = config.get(f'symbolic_modifiers.{modifier_key}')
            if modifier_config:
                modifier = SymbolicModifier(
                    name=modifier_config['name'],
                    trigger_emotion=modifier_config['trigger_emotion'],
                    effects=modifier_config['effects'],
                )
                eterna.modifiers.register_modifier(modifier)


def setup_eterna_world(eterna: EternaInterface) -> None:
    """
    Set up the core zones, physics, users, and initial state of the Eterna world.

    This function:
    1. Creates and configures the main zones (Quantum Forest, Orikum Sea, Library of Shared Minds)
    2. Defines physics profiles for each zone
    3. Creates and invites social users (Alice and Bob)
    4. Integrates an initial memory
    5. Sets the initial emotional state

    Args:
        eterna: The EternaInterface instance to configure.
    """
    # Set up zones
    for zone_key in config.get('zones', {}):
        zone_config = config.get(f'zones.{zone_key}')
        if zone_config:
            eterna.register_zone(
                zone_config['name'],
                origin=zone_config['origin'],
                complexity=zone_config['complexity'],
                emotion_tag=zone_config['emotion_tag']
            )

    # Set up physics profiles
    for profile_key in config.get('physics_profiles', {}):
        profile_config = config.get(f'physics_profiles.{profile_key}')
        if profile_config:
            physics_profile = PhysicsProfile(
                profile_config['name'],
                gravity=profile_config['gravity'],
                time_flow=profile_config['time_flow'],
                dimensions=profile_config['dimensions'],
                energy_behavior=profile_config.get('energy_behavior', 'standard'),
                conscious_safe=profile_config.get('conscious_safe', True)
            )

            # Apply physics profile to zones
            for zone_key, physics_key in config.get('zone_physics', {}).items():
                if physics_key == profile_key:
                    zone_name = config.get(f'zones.{zone_key}.name')
                    if zone_name:
                        eterna.define_physics_profile(zone_name, physics_profile)

    # Set up users
    for user_key in config.get('users', {}):
        user_config = config.get(f'users.{user_key}')
        if user_config:
            user = User(
                user_config['name'],
                intellect=user_config['intellect'],
                emotional_maturity=user_config['emotional_maturity'],
                consent=user_config['consent']
            )
            eterna.invite_social_user(user)

    # Set up initial memory
    memory_config = config.get('memory.initial')
    if memory_config:
        memory = Memory(
            memory_config['description'],
            clarity=memory_config['clarity'],
            emotional_quality=memory_config['emotional_quality']
        )
        eterna.integrate_memory(
            memory.description, memory.clarity, memory.emotional_quality
        )

    # Set up initial emotional state
    emotional_state_config = config.get('emotional_state.initial')
    if emotional_state_config:
        eterna.update_emotional_state(
            mood=emotional_state_config['mood'],
            stress_level=emotional_state_config['stress_level'],
            trauma_triggered=emotional_state_config['trauma_triggered']
        )


def setup_physics_profiles(eterna: EternaInterface) -> None:
    """
    Display the physics properties of each zone.

    This function is now simplified since the physics profiles are set up
    in the setup_eterna_world function. It just displays the physics properties
    of each zone for debugging purposes.

    Args:
        eterna: The EternaInterface instance to configure.
    """
    # Display physics properties of each zone
    for zone_key in config.get('zones', {}):
        zone_name = config.get(f'zones.{zone_key}.name')
        if zone_name:
            eterna.show_zone_physics(zone_name)


def setup_rituals(eterna: EternaInterface) -> None:
    """
    Set up rituals that can be performed in the Eterna world.

    This function creates ritual objects with defined purposes, steps, and
    symbolic elements, and registers them with the Eterna interface.
    The ritual configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.
    """
    # Set up rituals from configuration
    for ritual_key in config.get('rituals', {}):
        ritual_config = config.get(f'rituals.{ritual_key}')
        if ritual_config:
            ritual = Ritual(
                name=ritual_config['name'],
                purpose=ritual_config['purpose'],
                steps=ritual_config['steps'],
                symbolic_elements=ritual_config['symbolic_elements'],
            )
            eterna.rituals.register(ritual)


def setup_companions(eterna: EternaInterface) -> None:
    """
    Set up companion entities that inhabit the Eterna world.

    This function creates different types of companions (MemoryEcho, LocalAgent,
    SymbolicBeing) and spawns them in the Eterna world.
    The companion configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.
    """
    # Set up companions from configuration
    for companion_key in config.get('companions', {}):
        companion_config = config.get(f'companions.{companion_key}')
        if companion_config:
            companion_type = companion_config.get('type', '').lower()
            name = companion_config['name']

            if companion_type == 'memory_echo':
                companion = MemoryEcho(name, companion_config['description'])
            elif companion_type == 'local_agent':
                companion = LocalAgent(name, job=companion_config['job'])
            elif companion_type == 'symbolic_being':
                companion = SymbolicBeing(name, archetype=companion_config['archetype'])
            else:
                # Default to SymbolicBeing if type is not recognized
                companion = SymbolicBeing(name, archetype="unknown")

            eterna.companions.spawn(companion)


def setup_protection(eterna: EternaInterface) -> None:
    """
    Set up protection mechanisms against threats in the Eterna world.

    This function identifies potential threats, adds them to the vitals system,
    engages defense mechanisms, and activates failsafe protocols.
    The threat configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.
    """
    # Get threats from configuration
    threats = config.get('protection.threats', [])

    # Detect threats
    detected = eterna.threats.detect(threats)

    # Add threats to vitals system
    for threat in threats:
        eterna.vitals.add_threat(threat)

    # Engage defense mechanisms
    eterna.defense.engage(detected)

    # Activate failsafe protocols
    eterna.defense.activate_failsafe()


def setup_resonance_engine(eterna: EternaInterface) -> None:
    """
    Set up the resonance engine for the Eterna world.

    This function creates a ResonanceEngine instance and tunes the environment
    of different zones with specific frequencies.
    The zone frequency configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.
    """
    # Create resonance engine
    eterna.resonance = ResonanceEngine()

    # Tune environments based on configuration
    zone_frequencies = config.get('resonance.zone_frequencies', {})
    for zone_key, frequency in zone_frequencies.items():
        zone_name = config.get(f'zones.{zone_key}.name')
        if zone_name:
            eterna.resonance.tune_environment(zone_name, frequency=frequency)


def setup_time_and_agents(eterna: EternaInterface) -> None:
    """
    Set up time synchronization and reality agents in the Eterna world.

    This function initializes time synchronization and deploys a reality agent
    with specified environment conditions.
    The reality agent configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.
    """
    print("⏱️ Initializing time synchronization...")
    eterna.synchronize_time()

    print("🤖 Preparing reality agent...")
    environment_conditions = config.get('reality_agent.environment_conditions', {})
    eterna.deploy_reality_agent(environment_conditions)
