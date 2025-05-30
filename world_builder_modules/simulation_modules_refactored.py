"""
Simulation Modules for Eterna World (Refactored)

This module contains functions for simulating different aspects of the Eterna world,
including emotional events and sensory evolution.

The module uses the configuration system to get values instead of hardcoding them.
It also includes validation and error handling to ensure that functions receive valid inputs.

This is a refactored version that uses the shared utilities to reduce code duplication.
"""

from modules.emotions import EmotionalState
from modules.validation import (
    validate_params,
    validate_type,
    validate_non_empty_string,
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
def simulate_emotional_events(eterna: EternaInterface) -> None:
    """
    Simulate emotional events and soul interactions in the Eterna world.

    This function creates an emotional state, processes it through the emotion
    circuits, and simulates soul invitation and presence registration.
    The emotional event configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to use for simulation.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error simulating emotional events
    """
    try:
        # Get emotional event configuration with default values
        default_emotion_config = {
            'emotion': 'grief',
            'intensity': 9,
            'direction': 'locked',
            'companion': 'Lira'
        }
        emotion_config = get_config_dict('simulation.emotional_events', default=default_emotion_config)

        # Create and process emotion
        try:
            # Get emotion parameters with validation
            emotion_name = get_config_value('simulation.emotional_events.emotion', 
                                          default='grief', 
                                          expected_type=str)
            
            intensity = get_config_value('simulation.emotional_events.intensity', 
                                       default=9, 
                                       expected_type=(int, float))
            
            # Validate intensity is between 0 and 10
            if not isinstance(intensity, (int, float)) or intensity < 0 or intensity > 10:
                logger.warning(f"Invalid intensity: {intensity}, must be between 0 and 10, using 9")
                intensity = 9
            
            direction = get_config_value('simulation.emotional_events.direction', 
                                       default='locked', 
                                       expected_type=str)

            # Create the emotional state
            emotion = EmotionalState(
                emotion_name,
                intensity=intensity,
                direction=direction
            )

            # Process the emotion
            eterna.emotion_circuits.process_emotion(emotion)
            log_operation("Process emotion", True, logger, 
                         {"emotion": emotion_name, "intensity": intensity, "direction": direction})
        except Exception as e:
            log_operation("Process emotion", False, logger, error=e)
            # Continue with companion invitation

        # Invite and register companion
        try:
            companion_name = get_config_value('simulation.emotional_events.companion', 
                                            default='Lira', 
                                            expected_type=str)

            # Invite the companion
            eterna.soul_invitations.invite(companion_name)
            log_operation("Invite companion", True, logger, {"companion": companion_name})

            # Receive response and register presence
            eterna.soul_invitations.receive_response(companion_name, accepted=True)
            log_operation("Receive companion response", True, logger, 
                         {"companion": companion_name, "accepted": True})

            eterna.soul_presence.register_presence(companion_name)
            log_operation("Register companion presence", True, logger, {"companion": companion_name})

            # List present souls
            eterna.soul_presence.list_present_souls()
            log_operation("List present souls", True, logger)
        except Exception as e:
            log_operation("Companion interaction", False, logger, error=e)
    except Exception as e:
        log_operation("Simulate emotional events", False, logger, error=e)
        raise


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
def simulate_sensory_evolution(eterna: EternaInterface) -> None:
    """
    Simulate sensory evolution based on physics profiles of zones.

    This function adapts the senses to a specific physics profile,
    updates evolution statistics, and displays a tracker report.
    The sensory evolution configurations are loaded from the configuration system.

    Args:
        eterna: The EternaInterface instance to use for simulation.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error simulating sensory evolution
    """
    try:
        logger.info("Simulating sensory evolution through physics zones...")

        # Get sensory evolution configuration with default values
        default_sensory_config = {'zone': 'quantum_forest'}
        sensory_config = get_config_dict('simulation.sensory_evolution', default=default_sensory_config)

        # Get zone name from configuration
        try:
            zone_key = get_config_value('simulation.sensory_evolution.zone', 
                                      default='quantum_forest', 
                                      expected_type=str)
            
            zone_name = get_config_value(f'zones.{zone_key}.name', 
                                       default='Quantum Forest', 
                                       expected_type=str)
            
            logger.info(f"Using zone: {zone_name}")

            # Get physics profile and adapt senses
            physics_profile = eterna.physics_registry.get_profile(zone_name)

            if physics_profile:
                try:
                    # Adapt senses to physics profile
                    eterna.adapt_senses(physics_profile)
                    log_operation("Adapt senses", True, logger, {"zone": zone_name})

                    # Update evolution stats
                    eterna.update_evolution_stats()
                    log_operation("Update evolution stats", True, logger)

                    # Show tracker report
                    eterna.show_tracker_report()
                    log_operation("Display tracker report", True, logger)
                except Exception as e:
                    log_operation("Adapt senses or update evolution", False, logger, error=e)
            else:
                logger.warning(f"No physics profile found for zone: {zone_name}")
        except Exception as e:
            log_operation("Get zone information", False, logger, error=e)
    except Exception as e:
        log_operation("Simulate sensory evolution", False, logger, error=e)
        raise