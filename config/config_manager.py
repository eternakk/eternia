"""
Configuration Manager for Eternia

This module provides a centralized configuration management system for the Eternia project.
It loads configuration from YAML files and provides a clean API for accessing configuration values.
Configuration values can be overridden via environment variables.

Example usage:
    from config.config_manager import config

    # Access configuration values
    zone_complexity = config.get('zones.quantum_forest.complexity')
    physics_gravity = config.get('physics_profiles.dreamspace.gravity')

    # Access with default value if not found
    custom_value = config.get('custom.path', default='default_value')
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from modules.validation import (
    validate_params,
    validate_type,
    validate_non_empty_string,
    validate_directory_exists,
    ValidationError
)


class ConfigManager:
    """
    Configuration manager that loads configuration from YAML files and provides
    a clean API for accessing configuration values.

    Configuration values can be overridden via environment variables using the
    format ETERNIA_SECTION_KEY=value (e.g., ETERNIA_ZONES_QUANTUM_FOREST_COMPLEXITY=150).
    """

    @validate_params(config_dir=lambda v, p: validate_non_empty_string(v, p))
    def __init__(self, config_dir: str = 'config/settings') -> None:
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory containing configuration files.

        Raises:
            TypeValidationError: If config_dir is not a string
            ValueValidationError: If config_dir is an empty string
        """
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        self.env_prefix = 'ETERNIA_'

        # Create the config directory if it doesn't exist
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create config directory: {e}")
            raise

        # Load default configuration
        try:
            self._load_default_config()
        except Exception as e:
            logging.error(f"Failed to load default configuration: {e}")
            # Continue with empty config
            self.config = {}

        # Load environment-specific configuration
        try:
            env = os.environ.get('ETERNIA_ENV', 'development')
            self._load_env_config(env)
        except Exception as e:
            logging.error(f"Failed to load environment configuration: {e}")
            # Continue with default config

        # Override with environment variables
        try:
            self._load_env_vars()
        except Exception as e:
            logging.error(f"Failed to load environment variables: {e}")
            # Continue with current config

    def _load_default_config(self) -> None:
        """
        Load the default configuration from default.yaml.

        Raises:
            Exception: If there is an error loading the default configuration
        """
        default_config_path = self.config_dir / 'default.yaml'
        if default_config_path.exists():
            try:
                with open(default_config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    self.config = loaded_config or {}
                logging.info(f"Loaded default configuration from {default_config_path}")
            except yaml.YAMLError as e:
                logging.error(f"YAML error in default configuration file: {e}")
                raise
            except Exception as e:
                logging.error(f"Error loading default configuration: {e}")
                raise
        else:
            logging.warning(f"Default configuration file not found at {default_config_path}")
            self.config = {}

    @validate_params(env=lambda v, p: validate_non_empty_string(v, p))
    def _load_env_config(self, env: str) -> None:
        """
        Load environment-specific configuration.

        Args:
            env: Environment name (e.g., 'development', 'production').

        Raises:
            TypeValidationError: If env is not a string
            ValueValidationError: If env is an empty string
            Exception: If there is an error loading the environment configuration
        """
        env_config_path = self.config_dir / f'{env}.yaml'
        if env_config_path.exists():
            try:
                with open(env_config_path, 'r') as f:
                    env_config = yaml.safe_load(f) or {}
                    self._deep_update(self.config, env_config)
                logging.info(f"Loaded environment configuration from {env_config_path}")
            except yaml.YAMLError as e:
                logging.error(f"YAML error in environment configuration file: {e}")
                raise
            except Exception as e:
                logging.error(f"Error loading environment configuration: {e}")
                raise
        else:
            logging.info(f"Environment configuration file not found at {env_config_path}, using default configuration")

    def _load_env_vars(self) -> None:
        """
        Override configuration values with environment variables.

        Raises:
            Exception: If there is an error setting a configuration value from an environment variable
        """
        try:
            env_vars_count = 0
            for key, value in os.environ.items():
                if key.startswith(self.env_prefix):
                    try:
                        # Convert ETERNIA_ZONES_QUANTUM_FOREST_COMPLEXITY to zones.quantum_forest.complexity
                        config_key = key[len(self.env_prefix):].lower().replace('_', '.')
                        self.set(config_key, value)
                        env_vars_count += 1
                    except Exception as e:
                        logging.error(f"Error setting configuration value from environment variable {key}: {e}")
                        # Continue with other environment variables

            if env_vars_count > 0:
                logging.info(f"Loaded {env_vars_count} configuration values from environment variables")
        except Exception as e:
            logging.error(f"Error loading environment variables: {e}")
            raise

    @validate_params(
        target=lambda v, p: validate_type(v, dict, p),
        source=lambda v, p: validate_type(v, dict, p)
    )
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep update target dict with source dict.

        Args:
            target: Target dictionary to update.
            source: Source dictionary with new values.

        Raises:
            TypeValidationError: If target or source is not a dictionary
            Exception: If there is an error updating the target dictionary
        """
        try:
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    self._deep_update(target[key], value)
                else:
                    target[key] = value
        except Exception as e:
            logging.error(f"Error in deep update: {e}")
            raise

    @validate_params(key=lambda v, p: validate_non_empty_string(v, p))
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (e.g., 'zones.quantum_forest.complexity').
            default: Default value if the key is not found.

        Returns:
            Configuration value or default if not found.

        Raises:
            TypeValidationError: If key is not a string
            ValueValidationError: If key is an empty string
        """
        try:
            keys = key.split('.')
            value = self.config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value
        except Exception as e:
            logging.error(f"Error getting configuration value for key '{key}': {e}")
            return default

    @validate_params(key=lambda v, p: validate_non_empty_string(v, p))
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (e.g., 'zones.quantum_forest.complexity').
            value: Configuration value.

        Raises:
            TypeValidationError: If key is not a string
            ValueValidationError: If key is an empty string
        """
        try:
            keys = key.split('.')
            config = self.config

            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                elif not isinstance(config[k], dict):
                    # If the current node is not a dict, convert it to a dict
                    logging.warning(f"Converting non-dict node '{k}' to dict in config path '{key}'")
                    config[k] = {}
                config = config[k]

            config[keys[-1]] = value
        except Exception as e:
            logging.error(f"Error setting configuration value for key '{key}': {e}")
            raise

    @validate_params(env=lambda v, p: validate_non_empty_string(v, p))
    def save(self, env: str = 'default') -> None:
        """
        Save the current configuration to a file.

        Args:
            env: Environment name (e.g., 'development', 'production').

        Raises:
            TypeValidationError: If env is not a string
            ValueValidationError: If env is an empty string
        """
        try:
            config_path = self.config_dir / f'{env}.yaml'

            # Ensure the directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)

            logging.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logging.error(f"Error saving configuration to {env}.yaml: {e}")
            raise


# Create a singleton instance
config = ConfigManager()
