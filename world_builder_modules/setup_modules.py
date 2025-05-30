"""
Setup Modules for Eterna World

This module contains functions for setting up different aspects of the Eterna world,
including symbolic modifiers, zones, physics profiles, rituals, companions, protection,
resonance engine, and time and agents.

The module uses the configuration system to get values instead of hardcoding them.
It also includes validation and error handling to ensure that functions receive valid inputs.
"""

import logging
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
from modules.validation import (
    validate_params,
    validate_type,
    validate_non_empty_string,
    validate_positive_number,
    validate_non_negative_number,
    validate_dict_has_keys,
    ValidationError
)
from eterna_interface import EternaInterface
from config.config_manager import config


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
def setup_symbolic_modifiers(eterna: EternaInterface) -> None:
    """
    Set up symbolic modifiers for the Eterna world.

    This function creates and registers symbolic modifiers that can be triggered
    by emotions and affect the appearance and behavior of zones.
    The symbolic modifier configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error setting up symbolic modifiers
    """
    try:
        # Add a default symbolic modifier if none are configured
        if not config.get('symbolic_modifiers'):
            logging.info("No symbolic modifiers configured, adding default 'Shroud of Memory' modifier")
            try:
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
                logging.info("Default symbolic modifier 'Shroud of Memory' registered")
            except Exception as e:
                logging.error(f"Error creating default symbolic modifier: {e}")
                raise
        else:
            # Set up symbolic modifiers from configuration
            modifiers_count = 0
            for modifier_key in config.get('symbolic_modifiers', {}):
                try:
                    modifier_config = config.get(f'symbolic_modifiers.{modifier_key}')
                    if not modifier_config:
                        logging.warning(f"Empty configuration for symbolic modifier '{modifier_key}', skipping")
                        continue

                    # Validate required keys in modifier configuration
                    required_keys = ['name', 'trigger_emotion', 'effects']
                    try:
                        validate_dict_has_keys(modifier_config, required_keys, f"symbolic_modifiers.{modifier_key}")
                    except ValidationError as e:
                        logging.warning(f"Invalid configuration for symbolic modifier '{modifier_key}': {e}")
                        continue

                    # Create and register the modifier
                    modifier = SymbolicModifier(
                        name=modifier_config['name'],
                        trigger_emotion=modifier_config['trigger_emotion'],
                        effects=modifier_config['effects'],
                    )
                    eterna.modifiers.register_modifier(modifier)
                    modifiers_count += 1
                    logging.info(f"Registered symbolic modifier '{modifier_config['name']}'")
                except Exception as e:
                    logging.error(f"Error setting up symbolic modifier '{modifier_key}': {e}")
                    # Continue with other modifiers

            if modifiers_count > 0:
                logging.info(f"Set up {modifiers_count} symbolic modifiers")
            else:
                logging.warning("No valid symbolic modifiers found in configuration")
    except Exception as e:
        logging.error(f"Error setting up symbolic modifiers: {e}")
        raise


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
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

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error setting up the Eterna world
    """
    try:
        # Set up zones
        zones_count = 0
        for zone_key in config.get('zones', {}):
            try:
                zone_config = config.get(f'zones.{zone_key}')
                if not zone_config:
                    logging.warning(f"Empty configuration for zone '{zone_key}', skipping")
                    continue

                # Validate required keys in zone configuration
                required_keys = ['name', 'origin', 'complexity', 'emotion_tag']
                try:
                    validate_dict_has_keys(zone_config, required_keys, f"zones.{zone_key}")
                except ValidationError as e:
                    logging.warning(f"Invalid configuration for zone '{zone_key}': {e}")
                    continue

                # Validate complexity is a positive number
                try:
                    complexity = zone_config['complexity']
                    if not isinstance(complexity, (int, float)) or complexity <= 0:
                        logging.warning(f"Invalid complexity for zone '{zone_key}': {complexity}, must be a positive number")
                        complexity = 100  # Default value
                    else:
                        complexity = int(complexity)  # Ensure it's an integer
                except (TypeError, ValueError) as e:
                    logging.warning(f"Error parsing complexity for zone '{zone_key}': {e}, using default value")
                    complexity = 100  # Default value

                # Register the zone
                eterna.register_zone(
                    zone_config['name'],
                    origin=zone_config['origin'],
                    complexity=complexity,
                    emotion_tag=zone_config['emotion_tag']
                )
                zones_count += 1
                logging.info(f"Registered zone '{zone_config['name']}'")
            except Exception as e:
                logging.error(f"Error setting up zone '{zone_key}': {e}")
                # Continue with other zones

        if zones_count > 0:
            logging.info(f"Set up {zones_count} zones")
        else:
            logging.warning("No valid zones found in configuration")

        # Set up physics profiles
        profiles_count = 0
        for profile_key in config.get('physics_profiles', {}):
            try:
                profile_config = config.get(f'physics_profiles.{profile_key}')
                if not profile_config:
                    logging.warning(f"Empty configuration for physics profile '{profile_key}', skipping")
                    continue

                # Validate required keys in physics profile configuration
                required_keys = ['name', 'gravity', 'time_flow', 'dimensions']
                try:
                    validate_dict_has_keys(profile_config, required_keys, f"physics_profiles.{profile_key}")
                except ValidationError as e:
                    logging.warning(f"Invalid configuration for physics profile '{profile_key}': {e}")
                    continue

                # Create the physics profile
                physics_profile = PhysicsProfile(
                    profile_config['name'],
                    gravity=profile_config['gravity'],
                    time_flow=profile_config['time_flow'],
                    dimensions=profile_config['dimensions'],
                    energy_behavior=profile_config.get('energy_behavior', 'standard'),
                    conscious_safe=profile_config.get('conscious_safe', True)
                )
                profiles_count += 1
                logging.info(f"Created physics profile '{profile_config['name']}'")

                # Apply physics profile to zones
                applied_count = 0
                for zone_key, physics_key in config.get('zone_physics', {}).items():
                    if physics_key == profile_key:
                        zone_name = config.get(f'zones.{zone_key}.name')
                        if zone_name:
                            try:
                                eterna.define_physics_profile(zone_name, physics_profile)
                                applied_count += 1
                                logging.info(f"Applied physics profile '{profile_config['name']}' to zone '{zone_name}'")
                            except Exception as e:
                                logging.error(f"Error applying physics profile '{profile_config['name']}' to zone '{zone_name}': {e}")
                                # Continue with other zones

                if applied_count > 0:
                    logging.info(f"Applied physics profile '{profile_config['name']}' to {applied_count} zones")
            except Exception as e:
                logging.error(f"Error setting up physics profile '{profile_key}': {e}")
                # Continue with other profiles

        if profiles_count > 0:
            logging.info(f"Set up {profiles_count} physics profiles")
        else:
            logging.warning("No valid physics profiles found in configuration")

        # Set up users
        users_count = 0
        for user_key in config.get('users', {}):
            try:
                user_config = config.get(f'users.{user_key}')
                if not user_config:
                    logging.warning(f"Empty configuration for user '{user_key}', skipping")
                    continue

                # Validate required keys in user configuration
                required_keys = ['name', 'intellect', 'emotional_maturity', 'consent']
                try:
                    validate_dict_has_keys(user_config, required_keys, f"users.{user_key}")
                except ValidationError as e:
                    logging.warning(f"Invalid configuration for user '{user_key}': {e}")
                    continue

                # Create and invite the user
                user = User(
                    user_config['name'],
                    intellect=user_config['intellect'],
                    emotional_maturity=user_config['emotional_maturity'],
                    consent=user_config['consent']
                )
                eterna.invite_social_user(user)
                users_count += 1
                logging.info(f"Invited user '{user_config['name']}'")
            except Exception as e:
                logging.error(f"Error setting up user '{user_key}': {e}")
                # Continue with other users

        if users_count > 0:
            logging.info(f"Set up {users_count} users")
        else:
            logging.warning("No valid users found in configuration")

        # Set up initial memory
        try:
            memory_config = config.get('memory.initial')
            if memory_config:
                # Validate required keys in memory configuration
                required_keys = ['description', 'clarity', 'emotional_quality']
                try:
                    validate_dict_has_keys(memory_config, required_keys, "memory.initial")
                except ValidationError as e:
                    logging.warning(f"Invalid configuration for initial memory: {e}")
                else:
                    memory = Memory(
                        memory_config['description'],
                        clarity=memory_config['clarity'],
                        emotional_quality=memory_config['emotional_quality']
                    )
                    eterna.integrate_memory(
                        memory.description, memory.clarity, memory.emotional_quality
                    )
                    logging.info(f"Integrated initial memory: '{memory_config['description']}'")
            else:
                logging.info("No initial memory configured")
        except Exception as e:
            logging.error(f"Error setting up initial memory: {e}")
            # Continue with emotional state

        # Set up initial emotional state
        try:
            emotional_state_config = config.get('emotional_state.initial')
            if emotional_state_config:
                # Validate required keys in emotional state configuration
                required_keys = ['mood', 'stress_level', 'trauma_triggered']
                try:
                    validate_dict_has_keys(emotional_state_config, required_keys, "emotional_state.initial")
                except ValidationError as e:
                    logging.warning(f"Invalid configuration for initial emotional state: {e}")
                else:
                    eterna.update_emotional_state(
                        mood=emotional_state_config['mood'],
                        stress_level=emotional_state_config['stress_level'],
                        trauma_triggered=emotional_state_config['trauma_triggered']
                    )
                    logging.info(f"Updated emotional state: mood='{emotional_state_config['mood']}', stress_level={emotional_state_config['stress_level']}")
            else:
                logging.info("No initial emotional state configured")
        except Exception as e:
            logging.error(f"Error setting up initial emotional state: {e}")
            # Continue with next steps
    except Exception as e:
        logging.error(f"Error setting up Eterna world: {e}")
        raise


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
def setup_physics_profiles(eterna: EternaInterface) -> None:
    """
    Display the physics properties of each zone.

    This function is now simplified since the physics profiles are set up
    in the setup_eterna_world function. It just displays the physics properties
    of each zone for debugging purposes.

    Args:
        eterna: The EternaInterface instance to configure.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error displaying physics properties
    """
    try:
        # Display physics properties of each zone
        zones_count = 0
        for zone_key in config.get('zones', {}):
            try:
                zone_name = config.get(f'zones.{zone_key}.name')
                if zone_name:
                    eterna.show_zone_physics(zone_name)
                    zones_count += 1
                    logging.info(f"Displayed physics properties for zone '{zone_name}'")
            except Exception as e:
                logging.error(f"Error displaying physics properties for zone '{zone_key}': {e}")
                # Continue with other zones

        if zones_count > 0:
            logging.info(f"Displayed physics properties for {zones_count} zones")
        else:
            logging.warning("No zones found to display physics properties")
    except Exception as e:
        logging.error(f"Error setting up physics profiles: {e}")
        raise


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
def setup_rituals(eterna: EternaInterface) -> None:
    """
    Set up rituals that can be performed in the Eterna world.

    This function creates ritual objects with defined purposes, steps, and
    symbolic elements, and registers them with the Eterna interface.
    The ritual configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error setting up rituals
    """
    try:
        # Set up rituals from configuration
        rituals_count = 0
        for ritual_key in config.get('rituals', {}):
            try:
                ritual_config = config.get(f'rituals.{ritual_key}')
                if not ritual_config:
                    logging.warning(f"Empty configuration for ritual '{ritual_key}', skipping")
                    continue

                # Validate required keys in ritual configuration
                required_keys = ['name', 'purpose', 'steps', 'symbolic_elements']
                try:
                    validate_dict_has_keys(ritual_config, required_keys, f"rituals.{ritual_key}")
                except ValidationError as e:
                    logging.warning(f"Invalid configuration for ritual '{ritual_key}': {e}")
                    continue

                # Validate steps and symbolic_elements are lists
                if not isinstance(ritual_config['steps'], list):
                    logging.warning(f"Invalid steps for ritual '{ritual_key}': must be a list")
                    continue

                if not isinstance(ritual_config['symbolic_elements'], list):
                    logging.warning(f"Invalid symbolic_elements for ritual '{ritual_key}': must be a list")
                    continue

                # Create and register the ritual
                ritual = Ritual(
                    name=ritual_config['name'],
                    purpose=ritual_config['purpose'],
                    steps=ritual_config['steps'],
                    symbolic_elements=ritual_config['symbolic_elements'],
                )
                eterna.rituals.register(ritual)
                rituals_count += 1
                logging.info(f"Registered ritual '{ritual_config['name']}'")
            except Exception as e:
                logging.error(f"Error setting up ritual '{ritual_key}': {e}")
                # Continue with other rituals

        if rituals_count > 0:
            logging.info(f"Set up {rituals_count} rituals")
        else:
            logging.warning("No valid rituals found in configuration")
    except Exception as e:
        logging.error(f"Error setting up rituals: {e}")
        raise


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
def setup_companions(eterna: EternaInterface) -> None:
    """
    Set up companion entities that inhabit the Eterna world.

    This function creates different types of companions (MemoryEcho, LocalAgent,
    SymbolicBeing) and spawns them in the Eterna world.
    The companion configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error setting up companions
    """
    try:
        # Set up companions from configuration
        companions_count = 0
        for companion_key in config.get('companions', {}):
            try:
                companion_config = config.get(f'companions.{companion_key}')
                if not companion_config:
                    logging.warning(f"Empty configuration for companion '{companion_key}', skipping")
                    continue

                # Validate required keys in companion configuration
                required_keys = ['name']
                try:
                    validate_dict_has_keys(companion_config, required_keys, f"companions.{companion_key}")
                except ValidationError as e:
                    logging.warning(f"Invalid configuration for companion '{companion_key}': {e}")
                    continue

                # Get companion type and validate additional required keys based on type
                companion_type = companion_config.get('type', '').lower()
                name = companion_config['name']

                try:
                    if companion_type == 'memory_echo':
                        # Validate required keys for memory_echo
                        if 'description' not in companion_config:
                            logging.warning(f"Missing 'description' for memory_echo companion '{name}', skipping")
                            continue

                        companion = MemoryEcho(name, companion_config['description'])
                    elif companion_type == 'local_agent':
                        # Validate required keys for local_agent
                        if 'job' not in companion_config:
                            logging.warning(f"Missing 'job' for local_agent companion '{name}', skipping")
                            continue

                        companion = LocalAgent(name, job=companion_config['job'])
                    elif companion_type == 'symbolic_being':
                        # Validate required keys for symbolic_being
                        if 'archetype' not in companion_config:
                            logging.warning(f"Missing 'archetype' for symbolic_being companion '{name}', skipping")
                            continue

                        companion = SymbolicBeing(name, archetype=companion_config['archetype'])
                    else:
                        # Default to SymbolicBeing if type is not recognized
                        logging.warning(f"Unknown companion type '{companion_type}' for companion '{name}', defaulting to SymbolicBeing")
                        companion = SymbolicBeing(name, archetype="unknown")

                    # Spawn the companion
                    eterna.companions.spawn(companion)
                    companions_count += 1
                    logging.info(f"Spawned {companion_type} companion '{name}'")
                except Exception as e:
                    logging.error(f"Error creating companion '{name}' of type '{companion_type}': {e}")
                    # Continue with other companions
            except Exception as e:
                logging.error(f"Error setting up companion '{companion_key}': {e}")
                # Continue with other companions

        if companions_count > 0:
            logging.info(f"Set up {companions_count} companions")
        else:
            logging.warning("No valid companions found in configuration")
    except Exception as e:
        logging.error(f"Error setting up companions: {e}")
        raise


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
def setup_protection(eterna: EternaInterface) -> None:
    """
    Set up protection mechanisms against threats in the Eterna world.

    This function identifies potential threats, adds them to the vitals system,
    engages defense mechanisms, and activates failsafe protocols.
    The threat configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error setting up protection mechanisms
    """
    try:
        # Get threats from configuration
        threats = config.get('protection.threats', [])

        # Validate threats is a list
        if not isinstance(threats, list):
            logging.warning("Invalid threats configuration: must be a list, using empty list")
            threats = []

        if not threats:
            logging.warning("No threats configured")
        else:
            logging.info(f"Found {len(threats)} configured threats")

        try:
            # Detect threats
            detected = eterna.threats.detect(threats)
            logging.info(f"Detected {len(detected)} threats")

            # Add threats to vitals system
            for threat in threats:
                try:
                    eterna.vitals.add_threat(threat)
                    logging.info(f"Added threat '{threat}' to vitals system")
                except Exception as e:
                    logging.error(f"Error adding threat '{threat}' to vitals system: {e}")
                    # Continue with other threats

            # Engage defense mechanisms
            try:
                eterna.defense.engage(detected)
                logging.info(f"Engaged defense mechanisms for {len(detected)} detected threats")
            except Exception as e:
                logging.error(f"Error engaging defense mechanisms: {e}")
                # Continue with failsafe protocols

            # Activate failsafe protocols
            try:
                eterna.defense.activate_failsafe()
                logging.info("Activated failsafe protocols")
            except Exception as e:
                logging.error(f"Error activating failsafe protocols: {e}")
        except Exception as e:
            logging.error(f"Error detecting threats: {e}")
            # Continue with next steps
    except Exception as e:
        logging.error(f"Error setting up protection mechanisms: {e}")
        raise


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
def setup_resonance_engine(eterna: EternaInterface) -> None:
    """
    Set up the resonance engine for the Eterna world.

    This function creates a ResonanceEngine instance and tunes the environment
    of different zones with specific frequencies.
    The zone frequency configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error setting up the resonance engine
    """
    try:
        # Create resonance engine
        try:
            eterna.resonance = ResonanceEngine()
            logging.info("Created resonance engine")
        except Exception as e:
            logging.error(f"Error creating resonance engine: {e}")
            raise

        # Tune environments based on configuration
        zone_frequencies = config.get('resonance.zone_frequencies', {})

        # Validate zone_frequencies is a dictionary
        if not isinstance(zone_frequencies, dict):
            logging.warning("Invalid zone_frequencies configuration: must be a dictionary, using empty dictionary")
            zone_frequencies = {}

        if not zone_frequencies:
            logging.warning("No zone frequencies configured")
        else:
            logging.info(f"Found {len(zone_frequencies)} configured zone frequencies")

        tuned_count = 0
        for zone_key, frequency in zone_frequencies.items():
            try:
                zone_name = config.get(f'zones.{zone_key}.name')
                if not zone_name:
                    logging.warning(f"Zone '{zone_key}' not found in configuration, skipping")
                    continue

                # Validate frequency is a string
                if not isinstance(frequency, str):
                    logging.warning(f"Invalid frequency for zone '{zone_key}': {frequency}, must be a string, skipping")
                    continue

                # Tune the environment
                eterna.resonance.tune_environment(zone_name, frequency=frequency)
                tuned_count += 1
                logging.info(f"Tuned environment for zone '{zone_name}' with frequency '{frequency}'")
            except Exception as e:
                logging.error(f"Error tuning environment for zone '{zone_key}': {e}")
                # Continue with other zones

        if tuned_count > 0:
            logging.info(f"Tuned {tuned_count} zone environments")
        else:
            logging.warning("No zone environments tuned")
    except Exception as e:
        logging.error(f"Error setting up resonance engine: {e}")
        raise


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
def setup_time_and_agents(eterna: EternaInterface) -> None:
    """
    Set up time synchronization and reality agents in the Eterna world.

    This function initializes time synchronization and deploys a reality agent
    with specified environment conditions.
    The reality agent configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to configure.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error setting up time synchronization or reality agents
    """
    try:
        # Initialize time synchronization
        try:
            logging.info("Initializing time synchronization...")
            eterna.synchronize_time()
            logging.info("Time synchronization initialized")
        except Exception as e:
            logging.error(f"Error initializing time synchronization: {e}")
            # Continue with reality agent

        # Deploy reality agent
        try:
            logging.info("Preparing reality agent...")
            environment_conditions = config.get('reality_agent.environment_conditions', {})

            # Validate environment_conditions is a dictionary
            if not isinstance(environment_conditions, dict):
                logging.warning("Invalid environment_conditions configuration: must be a dictionary, using empty dictionary")
                environment_conditions = {}

            if not environment_conditions:
                logging.warning("No environment conditions configured for reality agent")
            else:
                logging.info(f"Found {len(environment_conditions)} configured environment conditions for reality agent")

            eterna.deploy_reality_agent(environment_conditions)
            logging.info("Reality agent deployed")
        except Exception as e:
            logging.error(f"Error deploying reality agent: {e}")
    except Exception as e:
        logging.error(f"Error setting up time and agents: {e}")
        raise
