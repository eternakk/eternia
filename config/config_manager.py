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
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ConfigManager:
    """
    Configuration manager that loads configuration from YAML files and provides
    a clean API for accessing configuration values.
    
    Configuration values can be overridden via environment variables using the
    format ETERNIA_SECTION_KEY=value (e.g., ETERNIA_ZONES_QUANTUM_FOREST_COMPLEXITY=150).
    """
    
    def __init__(self, config_dir: str = 'config/settings') -> None:
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files.
        """
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        self.env_prefix = 'ETERNIA_'
        
        # Create the config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load default configuration
        self._load_default_config()
        
        # Load environment-specific configuration
        env = os.environ.get('ETERNIA_ENV', 'development')
        self._load_env_config(env)
        
        # Override with environment variables
        self._load_env_vars()
    
    def _load_default_config(self) -> None:
        """Load the default configuration from default.yaml."""
        default_config_path = self.config_dir / 'default.yaml'
        if default_config_path.exists():
            with open(default_config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
    
    def _load_env_config(self, env: str) -> None:
        """
        Load environment-specific configuration.
        
        Args:
            env: Environment name (e.g., 'development', 'production').
        """
        env_config_path = self.config_dir / f'{env}.yaml'
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f) or {}
                self._deep_update(self.config, env_config)
    
    def _load_env_vars(self) -> None:
        """Override configuration values with environment variables."""
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Convert ETERNIA_ZONES_QUANTUM_FOREST_COMPLEXITY to zones.quantum_forest.complexity
                config_key = key[len(self.env_prefix):].lower().replace('_', '.')
                self.set(config_key, value)
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep update target dict with source dict.
        
        Args:
            target: Target dictionary to update.
            source: Source dictionary with new values.
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (e.g., 'zones.quantum_forest.complexity').
            default: Default value if the key is not found.
            
        Returns:
            Configuration value or default if not found.
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (e.g., 'zones.quantum_forest.complexity').
            value: Configuration value.
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, env: str = 'default') -> None:
        """
        Save the current configuration to a file.
        
        Args:
            env: Environment name (e.g., 'development', 'production').
        """
        config_path = self.config_dir / f'{env}.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)


# Create a singleton instance
config = ConfigManager()