# config/__init__.py
"""
Configuration package for Eternia.

This package provides access to the configuration system for the Eternia project.
It re-exports the config singleton from config_manager.py for easy access.
"""

from config.config_manager import config

# For backward compatibility
INTELLECT_THRESHOLD = config.get('user_acceptance.intellect_threshold')
EMOTIONAL_MATURITY_THRESHOLD = config.get('user_acceptance.emotional_maturity_threshold')
DEFAULT_LAWS = config.get('default_laws')
