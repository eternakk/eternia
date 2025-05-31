"""
Setup Modules for Eterna World (Refactored)

This module contains functions for setting up different aspects of the Eterna world,
including symbolic modifiers, zones, physics profiles, rituals, companions, protection,
resonance engine, and time and agents.

The module uses the configuration system to get values instead of hardcoding them.
It also includes validation and error handling to ensure that functions receive valid inputs.

This is a refactored version that uses the shared utilities to reduce code duplication.
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
from modules.validation import (
    validate_params,
    validate_type,
    validate_non_empty_string,
    validate_positive_number,
    validate_non_negative_number,
    validate_dict_has_keys,
    ValidationError
)
from modules.utilities import (
    get_config_value,
    get_config_dict,
    get_config_list,
    get_config_section_items,
    iterate_config_section,
    get_module_logger,
    log_operation,
    log_batch_operation
)
from eterna_interface import EternaInterface

# Get a logger for this module
logger = get_module_logger(__name__)

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
        modifiers = get_config_dict('symbolic_modifiers')

        if not modifiers:
            logger.info("No symbolic modifiers configured, adding default 'Shroud of Memory' modifier")
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
                log_operation("Register default symbolic modifier", True, logger, 
                             {"name": "Shroud of Memory"})
            except Exception as e:
                log_operation("Register default symbolic modifier", False, logger, 
                             {"name": "Shroud of Memory"}, e)
                raise
        else:
            # Process each modifier using the iterate_config_section utility
            def process_modifier(key: str, config_item: Dict[str, Any]) -> None:
                try:
                    # Create and register the modifier
                    modifier = SymbolicModifier(
                        name=config_item['name'],
                        trigger_emotion=config_item['trigger_emotion'],
                        effects=config_item['effects'],
                    )
                    eterna.modifiers.register_modifier(modifier)
                    log_operation("Register symbolic modifier", True, logger, 
                                 {"name": config_item['name']})
                except Exception as e:
                    log_operation("Register symbolic modifier", False, logger, 
                                 {"name": config_item.get('name', key)}, e)
                    # Continue with other modifiers

            # Process all modifiers with required keys validation
            required_keys = ['name', 'trigger_emotion', 'effects']
            count = iterate_config_section('symbolic_modifiers', process_modifier, required_keys)

            log_batch_operation("Setup symbolic modifiers", count, count, logger)
    except Exception as e:
        log_operation("Setup symbolic modifiers", False, logger, error=e)
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
        def process_zone(key: str, config_item: Dict[str, Any]) -> None:
            try:
                # Validate complexity is a positive number
                complexity = config_item.get('complexity', 100)
                if not isinstance(complexity, (int, float)) or complexity <= 0:
                    logger.warning(f"Invalid complexity for zone '{key}': {complexity}, must be a positive number")
                    complexity = 100  # Default value
                else:
                    complexity = int(complexity)  # Ensure it's an integer

                # Register the zone
                eterna.register_zone(
                    config_item['name'],
                    origin=config_item['origin'],
                    complexity=complexity,
                    emotion_tag=config_item['emotion_tag']
                )
                log_operation("Register zone", True, logger, {"name": config_item['name']})
            except Exception as e:
                log_operation("Register zone", False, logger, {"name": config_item.get('name', key)}, e)
                # Continue with other zones

        # Process all zones with required keys validation
        required_keys = ['name', 'origin', 'complexity', 'emotion_tag']
        zones_count = iterate_config_section('zones', process_zone, required_keys)
        log_batch_operation("Setup zones", zones_count, zones_count, logger)

        # Set up physics profiles
        def process_physics_profile(key: str, config_item: Dict[str, Any]) -> None:
            try:
                # Create the physics profile
                physics_profile = PhysicsProfile(
                    config_item['name'],
                    gravity=config_item['gravity'],
                    time_flow=config_item['time_flow'],
                    dimensions=config_item['dimensions'],
                    energy_behavior=config_item.get('energy_behavior', 'standard'),
                    conscious_safe=config_item.get('conscious_safe', True)
                )
                log_operation("Create physics profile", True, logger, {"name": config_item['name']})

                # Apply physics profile to zones
                applied_count = 0
                zone_physics = get_config_dict('zone_physics')
                for zone_key, physics_key in zone_physics.items():
                    if physics_key == key:
                        zone_name = get_config_value(f'zones.{zone_key}.name')
                        if zone_name:
                            try:
                                eterna.define_physics_profile(zone_name, physics_profile)
                                applied_count += 1
                                log_operation("Apply physics profile", True, logger, 
                                            {"profile": config_item['name'], "zone": zone_name})
                            except Exception as e:
                                log_operation("Apply physics profile", False, logger, 
                                            {"profile": config_item['name'], "zone": zone_name}, e)
                                # Continue with other zones

                if applied_count > 0:
                    log_batch_operation(f"Apply physics profile '{config_item['name']}'", 
                                      applied_count, applied_count, logger)
            except Exception as e:
                log_operation("Create physics profile", False, logger, {"name": config_item.get('name', key)}, e)
                # Continue with other profiles

        # Process all physics profiles with required keys validation
        required_keys = ['name', 'gravity', 'time_flow', 'dimensions']
        profiles_count = iterate_config_section('physics_profiles', process_physics_profile, required_keys)
        log_batch_operation("Setup physics profiles", profiles_count, profiles_count, logger)

        # Set up users
        def process_user(key: str, config_item: Dict[str, Any]) -> None:
            try:
                # Create and invite the user
                user = User(
                    config_item['name'],
                    intellect=config_item['intellect'],
                    emotional_maturity=config_item['emotional_maturity'],
                    consent=config_item['consent']
                )
                eterna.invite_social_user(user)
                log_operation("Invite user", True, logger, {"name": config_item['name']})
            except Exception as e:
                log_operation("Invite user", False, logger, {"name": config_item.get('name', key)}, e)
                # Continue with other users

        # Process all users with required keys validation
        required_keys = ['name', 'intellect', 'emotional_maturity', 'consent']
        users_count = iterate_config_section('users', process_user, required_keys)
        log_batch_operation("Setup users", users_count, users_count, logger)

        # Integrate initial memory
        try:
            memory_text = get_config_value('initial_memory.text')
            if memory_text:
                memory = Memory(memory_text)
                eterna.integrate_memory(memory)
                log_operation("Integrate initial memory", True, logger)
            else:
                logger.warning("No initial memory text configured")
        except Exception as e:
            log_operation("Integrate initial memory", False, logger, error=e)
            # Continue with next steps

        # Set initial emotional state
        try:
            emotion = get_config_value('initial_emotional_state.emotion', 'neutral')
            intensity = get_config_value('initial_emotional_state.intensity', 0.5)

            # Validate intensity is between 0 and 1
            if not isinstance(intensity, (int, float)) or intensity < 0 or intensity > 1:
                logger.warning(f"Invalid intensity for initial emotional state: {intensity}, must be between 0 and 1")
                intensity = 0.5  # Default value

            try:
                emotional_state = EmotionalState(emotion, intensity)
                eterna.update_emotional_state(emotional_state)
                log_operation("Update emotional state", True, logger, 
                             {"emotion": emotion, "intensity": intensity})
            except Exception as e:
                log_operation("Update emotional state", False, logger, error=e)
                # Continue with next steps
        except Exception as e:
            log_operation("Update emotional state", False, logger, error=e)
            # Continue with next steps
    except Exception as e:
        log_operation("Setup Eterna world", False, logger, error=e)
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
        # Display physics properties of each zone using iterate_config_section
        def display_zone_physics(key: str, config_item: Dict[str, Any]) -> None:
            try:
                zone_name = config_item.get('name')
                if zone_name:
                    eterna.show_zone_physics(zone_name)
                    log_operation("Display zone physics", True, logger, {"zone": zone_name})
            except Exception as e:
                log_operation("Display zone physics", False, logger, {"zone": config_item.get('name', key)}, e)
                # Continue with other zones

        # Process all zones
        zones_count = iterate_config_section('zones', display_zone_physics)

        if zones_count > 0:
            log_batch_operation("Display zone physics", zones_count, zones_count, logger)
        else:
            logger.warning("No zones found to display physics properties")
    except Exception as e:
        log_operation("Setup physics profiles", False, logger, error=e)
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
        # Set up rituals from configuration using iterate_config_section
        def process_ritual(key: str, config_item: Dict[str, Any]) -> None:
            try:
                # Validate steps and symbolic_elements are lists
                if not isinstance(config_item.get('steps', []), list):
                    logger.warning(f"Invalid steps for ritual '{key}': must be a list")
                    return

                if not isinstance(config_item.get('symbolic_elements', []), list):
                    logger.warning(f"Invalid symbolic_elements for ritual '{key}': must be a list")
                    return

                # Create and register the ritual
                ritual = Ritual(
                    name=config_item['name'],
                    purpose=config_item['purpose'],
                    steps=config_item['steps'],
                    symbolic_elements=config_item['symbolic_elements'],
                )
                eterna.rituals.register(ritual)
                log_operation("Register ritual", True, logger, {"name": config_item['name']})
            except Exception as e:
                log_operation("Register ritual", False, logger, {"name": config_item.get('name', key)}, e)
                # Continue with other rituals

        # Process all rituals with required keys validation
        required_keys = ['name', 'purpose', 'steps', 'symbolic_elements']
        rituals_count = iterate_config_section('rituals', process_ritual, required_keys)

        if rituals_count > 0:
            log_batch_operation("Setup rituals", rituals_count, rituals_count, logger)
        else:
            logger.warning("No valid rituals found in configuration")
    except Exception as e:
        log_operation("Setup rituals", False, logger, error=e)
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

        # Define a function to process each companion
        def process_companion(key: str, config_item: Dict[str, Any]) -> None:
            nonlocal companions_count
            try:
                # Get companion type and validate additional required keys based on type
                companion_type = config_item.get('type', '').lower()
                name = config_item['name']

                try:
                    if companion_type == 'memory_echo':
                        # Validate required keys for memory_echo
                        if 'description' not in config_item:
                            logger.warning(f"Missing 'description' for memory_echo companion '{name}', skipping")
                            return

                        companion = MemoryEcho(name, config_item['description'])
                    elif companion_type == 'local_agent':
                        # Validate required keys for local_agent
                        if 'job' not in config_item:
                            logger.warning(f"Missing 'job' for local_agent companion '{name}', skipping")
                            return

                        companion = LocalAgent(name, job=config_item['job'])
                    elif companion_type == 'symbolic_being':
                        # Validate required keys for symbolic_being
                        if 'archetype' not in config_item:
                            logger.warning(f"Missing 'archetype' for symbolic_being companion '{name}', skipping")
                            return

                        companion = SymbolicBeing(name, archetype=config_item['archetype'])
                    else:
                        # Default to SymbolicBeing if type is not recognized
                        logger.warning(f"Unknown companion type '{companion_type}' for companion '{name}', defaulting to SymbolicBeing")
                        companion = SymbolicBeing(name, archetype="unknown")

                    # Spawn the companion
                    eterna.companions.spawn(companion)
                    companions_count += 1
                    log_operation("Spawn companion", True, logger, 
                                 {"name": name, "type": companion_type})
                except Exception as e:
                    log_operation("Spawn companion", False, logger, 
                                 {"name": name, "type": companion_type}, e)
                    # Continue with other companions
            except Exception as e:
                log_operation("Process companion", False, logger, {"key": key}, e)
                # Continue with other companions

        # Process all companions with required keys validation
        required_keys = ['name']
        companions_dict = get_config_dict('companions')

        if not companions_dict:
            logger.warning("No companions configured")
        else:
            logger.info(f"Found {len(companions_dict)} configured companions")
            iterate_config_section('companions', process_companion, required_keys)

        if companions_count > 0:
            log_batch_operation("Setup companions", len(companions_dict), companions_count, logger)
        else:
            logger.warning("No valid companions found in configuration")
    except Exception as e:
        log_operation("Setup companions", False, logger, error=e)
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
        threats = get_config_list('protection.threats', default=[], item_type=str)

        if not threats:
            logger.warning("No threats configured")
        else:
            logger.info(f"Found {len(threats)} configured threats")

        try:
            # Detect threats
            detected = eterna.threats.detect(threats)
            log_operation("Detect threats", True, logger, {"count": len(detected)})

            # Add threats to vitals system
            added_count = 0
            for threat in threats:
                try:
                    eterna.vitals.add_threat(threat)
                    added_count += 1
                    log_operation("Add threat to vitals", True, logger, {"threat": threat})
                except Exception as e:
                    log_operation("Add threat to vitals", False, logger, {"threat": threat}, e)
                    # Continue with other threats

            log_batch_operation("Add threats to vitals", len(threats), added_count, logger)

            # Engage defense mechanisms
            try:
                eterna.defense.engage(detected)
                log_operation("Engage defense mechanisms", True, logger, 
                             {"threats_count": len(detected)})
            except Exception as e:
                log_operation("Engage defense mechanisms", False, logger, 
                             {"threats_count": len(detected)}, e)
                # Continue with failsafe protocols

            # Activate failsafe protocols
            try:
                eterna.defense.activate_failsafe()
                log_operation("Activate failsafe protocols", True, logger)
            except Exception as e:
                log_operation("Activate failsafe protocols", False, logger, error=e)
        except Exception as e:
            log_operation("Detect threats", False, logger, error=e)
            # Continue with next steps
    except Exception as e:
        log_operation("Setup protection mechanisms", False, logger, error=e)
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
            log_operation("Create resonance engine", True, logger)
        except Exception as e:
            log_operation("Create resonance engine", False, logger, error=e)
            raise

        # Tune environments based on configuration
        zone_frequencies = get_config_dict('resonance.zone_frequencies')

        if not zone_frequencies:
            logger.warning("No zone frequencies configured")
        else:
            logger.info(f"Found {len(zone_frequencies)} configured zone frequencies")

        tuned_count = 0
        for zone_key, frequency in zone_frequencies.items():
            try:
                zone_name = get_config_value(f'zones.{zone_key}.name')
                if not zone_name:
                    logger.warning(f"Zone '{zone_key}' not found in configuration, skipping")
                    continue

                # Validate frequency is a string
                if not isinstance(frequency, str):
                    logger.warning(f"Invalid frequency for zone '{zone_key}': {frequency}, must be a string, skipping")
                    continue

                # Tune the environment
                eterna.resonance.tune_environment(zone_name, frequency=frequency)
                tuned_count += 1
                log_operation("Tune zone environment", True, logger, 
                             {"zone": zone_name, "frequency": frequency})
            except Exception as e:
                log_operation("Tune zone environment", False, logger, 
                             {"zone": zone_key, "frequency": str(frequency)}, e)
                # Continue with other zones

        if tuned_count > 0:
            log_batch_operation("Tune zone environments", len(zone_frequencies), tuned_count, logger)
        else:
            logger.warning("No zone environments tuned")
    except Exception as e:
        log_operation("Setup resonance engine", False, logger, error=e)
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
            logger.info("Initializing time synchronization...")
            eterna.synchronize_time()
            log_operation("Initialize time synchronization", True, logger)
        except Exception as e:
            log_operation("Initialize time synchronization", False, logger, error=e)
            # Continue with reality agent

        # Deploy reality agent
        try:
            logger.info("Preparing reality agent...")
            environment_conditions = get_config_dict('reality_agent.environment_conditions')

            if not environment_conditions:
                logger.warning("No environment conditions configured for reality agent")
            else:
                logger.info(f"Found {len(environment_conditions)} configured environment conditions for reality agent")

            eterna.deploy_reality_agent(environment_conditions)
            log_operation("Deploy reality agent", True, logger, 
                         {"conditions_count": len(environment_conditions)})
        except Exception as e:
            log_operation("Deploy reality agent", False, logger, error=e)
    except Exception as e:
        log_operation("Setup time and agents", False, logger, error=e)
        raise
