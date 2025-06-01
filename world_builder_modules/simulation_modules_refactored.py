"""
Simulation Modules for Eterna World (Refactored)

This module contains functions for simulating different aspects of the Eterna world,
including emotional events and sensory evolution.

The module uses the configuration system to get values instead of hardcoding them.
It also includes validation and error handling to ensure that functions receive valid inputs.

This is a refactored version that uses the shared utilities to reduce code duplication.

Memory optimization features:
- Configurable log rotation to prevent unbounded log growth
- Batch processing of operations where possible
- Efficient error handling to minimize memory overhead
- Reduced memory footprint for configuration access
"""

from modules.emotions import EmotionalState
from modules.validation import (
    validate_params,
    validate_type,
    validate_non_empty_string,
    validate_dict_has_keys,
    ValidationError
)
import os
import logging
from logging.handlers import RotatingFileHandler

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

# Configure memory-efficient logging with rotation
def get_memory_efficient_logger(name):
    """
    Create a memory-efficient logger with log rotation.

    Args:
        name: The name of the logger.

    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name)

    # Only configure if handlers haven't been added yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        # Create a rotating file handler (10 MB max size, keep 3 backup files)
        log_file = os.path.join(log_dir, f"{name.split('.')[-1]}.log")
        handler = RotatingFileHandler(
            log_file, 
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=3
        )

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

        # Add console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Get a memory-efficient logger for this module
logger = get_memory_efficient_logger(__name__)


@validate_params(eterna=lambda v, p: validate_type(v, EternaInterface, p))
def simulate_emotional_events(eterna: EternaInterface) -> None:
    """
    Simulate emotional events and soul interactions in the Eterna world.

    This function creates an emotional state, processes it through the emotion
    circuits, and simulates soul invitation and presence registration.
    The emotional event configurations are loaded from the configuration system.

    Memory optimization:
    - Uses batch processing for multiple emotions and companions
    - Caches configuration values to reduce repeated lookups
    - Uses memory-efficient logging with rotation
    - Minimizes object creation and destruction

    Args:
        eterna: The EternaInterface instance to use for simulation.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error simulating emotional events
    """
    try:
        # Get emotional event configuration with default values - do this once
        default_emotion_config = {
            'emotion': 'grief',
            'intensity': 9,
            'direction': 'locked',
            'companion': 'Lira',
            'batch_size': 5  # Default batch size
        }

        # Cache the entire configuration to avoid repeated lookups
        emotion_config = get_config_dict('simulation.emotional_events', default=default_emotion_config)

        # Extract values from cached config
        emotion_name = emotion_config.get('emotion', 'grief')
        intensity = emotion_config.get('intensity', 9)
        direction = emotion_config.get('direction', 'locked')
        companion_name = emotion_config.get('companion', 'Lira')
        batch_size = emotion_config.get('batch_size', 5)

        # Validate intensity is between 0 and 10
        if not isinstance(intensity, (int, float)) or intensity < 0 or intensity > 10:
            logger.warning(f"Invalid intensity: {intensity}, must be between 0 and 10, using 9")
            intensity = 9

        # Batch process emotions
        try:
            # Prepare batch of emotions (variations of the base emotion)
            emotion_batch = []
            for i in range(batch_size):
                # Create slight variations for the batch
                batch_intensity = max(0, min(10, intensity + (i - batch_size // 2) * 0.5))

                # Create the emotional state
                emotion = EmotionalState(
                    emotion_name,
                    intensity=batch_intensity,
                    direction=direction
                )
                emotion_batch.append(emotion)

            # Process the emotions in batch
            batch_results = []
            for emotion in emotion_batch:
                try:
                    eterna.emotion_circuits.process_emotion(emotion)
                    batch_results.append({
                        "emotion": emotion.name,
                        "intensity": emotion.intensity,
                        "direction": emotion.direction,
                        "success": True
                    })
                except Exception as e:
                    batch_results.append({
                        "emotion": emotion.name if hasattr(emotion, 'name') else "unknown",
                        "error": str(e),
                        "success": False
                    })

            # Log the batch operation once instead of individual logs
            log_batch_operation("Process emotions", batch_results, logger)

        except Exception as e:
            log_operation("Process emotion batch", False, logger, error=e)
            # Continue with companion invitation

        # Batch process companion interactions
        try:
            # Get companion names (could be multiple in a real implementation)
            companions = [companion_name]  # In a real implementation, this could be a list from config

            # Prepare batch operations
            invite_results = []
            presence_results = []

            for companion in companions:
                # Invite the companion
                try:
                    eterna.soul_invitations.invite(companion)
                    invite_results.append({"companion": companion, "success": True})

                    # Receive response and register presence
                    eterna.soul_invitations.receive_response(companion, accepted=True)
                    eterna.soul_presence.register_presence(companion)
                    presence_results.append({"companion": companion, "success": True})
                except Exception as e:
                    invite_results.append({"companion": companion, "success": False, "error": str(e)})
                    presence_results.append({"companion": companion, "success": False, "error": str(e)})

            # Log batch operations
            log_batch_operation("Invite companions", invite_results, logger)
            log_batch_operation("Register companion presence", presence_results, logger)

            # List present souls (single operation)
            eterna.soul_presence.list_present_souls()
            log_operation("List present souls", True, logger)

        except Exception as e:
            log_operation("Companion interaction batch", False, logger, error=e)
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

    Memory optimization:
    - Uses batch processing for multiple zones
    - Caches configuration values to reduce repeated lookups
    - Uses memory-efficient logging with rotation
    - Minimizes object creation and destruction

    Args:
        eterna: The EternaInterface instance to use for simulation.

    Raises:
        TypeValidationError: If eterna is not an EternaInterface instance
        Exception: If there is an error simulating sensory evolution
    """
    try:
        logger.info("Simulating sensory evolution through physics zones...")

        # Get sensory evolution configuration with default values - do this once
        default_sensory_config = {
            'zone': 'quantum_forest',
            'batch_size': 3,  # Default batch size
            'additional_zones': ['crystal_cavern', 'nebula_plains']  # Default additional zones
        }

        # Cache the entire configuration to avoid repeated lookups
        sensory_config = get_config_dict('simulation.sensory_evolution', default=default_sensory_config)

        # Extract values from cached config
        primary_zone_key = sensory_config.get('zone', 'quantum_forest')
        batch_size = sensory_config.get('batch_size', 3)
        additional_zones = sensory_config.get('additional_zones', [])

        # Prepare a list of zones to process
        zone_keys = [primary_zone_key] + additional_zones[:batch_size-1]  # Limit to batch_size

        # Batch process zones
        zone_results = []

        for zone_key in zone_keys:
            try:
                # Get zone name from configuration - use cached lookup when possible
                zone_name = get_config_value(f'zones.{zone_key}.name', 
                                           default=zone_key.replace('_', ' ').title(), 
                                           expected_type=str)

                # Get physics profile
                physics_profile = eterna.physics_registry.get_profile(zone_name)

                if physics_profile:
                    # Process this zone
                    zone_result = {"zone": zone_name, "success": True, "operations": []}

                    try:
                        # Adapt senses to physics profile
                        eterna.adapt_senses(physics_profile)
                        zone_result["operations"].append({"operation": "adapt_senses", "success": True})

                        # Update evolution stats
                        eterna.update_evolution_stats()
                        zone_result["operations"].append({"operation": "update_evolution_stats", "success": True})
                    except Exception as e:
                        zone_result["success"] = False
                        zone_result["error"] = str(e)
                        zone_result["operations"].append({"operation": "process_zone", "success": False, "error": str(e)})
                else:
                    zone_result = {"zone": zone_name, "success": False, "error": "No physics profile found"}

                zone_results.append(zone_result)

            except Exception as e:
                zone_results.append({"zone": zone_key, "success": False, "error": str(e)})

        # Log the batch operation once instead of individual logs
        log_batch_operation("Process zones for sensory evolution", zone_results, logger)

        # Show tracker report once at the end (not for each zone)
        try:
            eterna.show_tracker_report()
            log_operation("Display tracker report", True, logger)
        except Exception as e:
            log_operation("Display tracker report", False, logger, error=e)

    except Exception as e:
        log_operation("Simulate sensory evolution", False, logger, error=e)
        raise
