"""
Configuration Utilities for Eternia

This module provides utility functions for safely retrieving and validating
configuration values from the configuration system. It helps reduce duplicate
code and standardize error handling when working with configuration values.
"""

import logging
from typing import Any, Dict, List, Optional, Union, Type, TypeVar, Callable

from config.config_manager import config
from modules.validation import (
    validate_type,
    validate_dict_has_keys,
    ValidationError
)

T = TypeVar('T')

def get_config_value(
    key: str,
    default: Any = None,
    required: bool = False,
    expected_type: Optional[Union[Type, List[Type]]] = None
) -> Any:
    """
    Safely retrieve a configuration value with validation.
    
    Args:
        key: The configuration key (e.g., 'zones.quantum_forest.complexity')
        default: The default value to return if the key is not found
        required: Whether the configuration value is required
        expected_type: The expected type or list of types for the value
        
    Returns:
        The configuration value, or the default if not found
        
    Raises:
        ValidationError: If the value is required but not found, or if it's not of the expected type
    """
    value = config.get(key, default)
    
    if required and value is None:
        logging.error(f"Required configuration value '{key}' not found")
        raise ValidationError(f"Required configuration value '{key}' not found")
    
    if expected_type is not None and value is not None:
        try:
            validate_type(value, expected_type, key)
        except ValidationError as e:
            logging.warning(f"Invalid configuration value for '{key}': {e}")
            return default
    
    return value

def get_config_dict(
    key: str,
    default: Dict[str, Any] = None,
    required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Safely retrieve a dictionary configuration value with validation.
    
    Args:
        key: The configuration key (e.g., 'zones.quantum_forest')
        default: The default dictionary to return if the key is not found
        required_keys: List of keys that must be present in the dictionary
        
    Returns:
        The configuration dictionary, or the default if not found or invalid
        
    Raises:
        ValidationError: If the value is not a dictionary or if required keys are missing
    """
    if default is None:
        default = {}
    
    value = config.get(key, default)
    
    if not isinstance(value, dict):
        logging.warning(f"Configuration value '{key}' is not a dictionary, using default")
        return default
    
    if required_keys:
        try:
            validate_dict_has_keys(value, required_keys, key)
        except ValidationError as e:
            logging.warning(f"Invalid configuration dictionary for '{key}': {e}")
            return default
    
    return value

def get_config_list(
    key: str,
    default: List[Any] = None,
    item_type: Optional[Union[Type, List[Type]]] = None
) -> List[Any]:
    """
    Safely retrieve a list configuration value with validation.
    
    Args:
        key: The configuration key (e.g., 'protection.threats')
        default: The default list to return if the key is not found
        item_type: The expected type or list of types for the list items
        
    Returns:
        The configuration list, or the default if not found or invalid
    """
    if default is None:
        default = []
    
    value = config.get(key, default)
    
    if not isinstance(value, list):
        logging.warning(f"Configuration value '{key}' is not a list, using default")
        return default
    
    if item_type is not None:
        valid_items = []
        for i, item in enumerate(value):
            try:
                validate_type(item, item_type, f"{key}[{i}]")
                valid_items.append(item)
            except ValidationError as e:
                logging.warning(f"Invalid item in configuration list '{key}': {e}")
        return valid_items
    
    return value

def get_config_section_items(section_key: str) -> Dict[str, Any]:
    """
    Get all items in a configuration section.
    
    Args:
        section_key: The section key (e.g., 'zones', 'physics_profiles')
        
    Returns:
        A dictionary of all items in the section
    """
    section = get_config_dict(section_key)
    result = {}
    
    for key in section:
        item_key = f"{section_key}.{key}"
        item = config.get(item_key)
        if item is not None:
            result[key] = item
    
    return result

def iterate_config_section(
    section_key: str,
    callback: Callable[[str, Any], None],
    required_keys: Optional[List[str]] = None
) -> int:
    """
    Iterate over items in a configuration section and apply a callback to each valid item.
    
    Args:
        section_key: The section key (e.g., 'zones', 'physics_profiles')
        callback: A function to call for each item, taking the item key and value
        required_keys: List of keys that must be present in each item
        
    Returns:
        The number of items processed
    """
    section = get_config_dict(section_key)
    processed_count = 0
    
    for key in section:
        try:
            item_key = f"{section_key}.{key}"
            item = get_config_dict(item_key)
            
            if not item:
                logging.warning(f"Empty configuration for {item_key}, skipping")
                continue
            
            if required_keys:
                try:
                    validate_dict_has_keys(item, required_keys, item_key)
                except ValidationError as e:
                    logging.warning(f"Invalid configuration for {item_key}: {e}")
                    continue
            
            callback(key, item)
            processed_count += 1
            
        except Exception as e:
            logging.error(f"Error processing configuration item '{key}' in section '{section_key}': {e}")
            # Continue with other items
    
    return processed_count