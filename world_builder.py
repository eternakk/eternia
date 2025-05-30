"""
🌌 Eterna World Builder — Expanded Core

This module serves as the main entry point for building, simulating, and managing
the Eterna world. It has been refactored to use a more modular approach, with
functionality split into separate modules in the world_builder_modules package.

The module re-exports the key functions and classes from the world_builder_modules
package, making them available to other parts of the application.
"""

from pathlib import Path

# Re-export setup functions
from world_builder_modules.setup_modules import (
    setup_symbolic_modifiers,
    setup_eterna_world,
    setup_physics_profiles,
    setup_rituals,
    setup_companions,
    setup_protection,
    setup_resonance_engine,
    setup_time_and_agents,
)

# Re-export simulation functions
from world_builder_modules.simulation_modules import (
    simulate_emotional_events,
    simulate_sensory_evolution,
)

# Re-export EternaWorld class and build_world function
from world_builder_modules.eterna_world import (
    EternaWorld,
    build_world,
    CHECKPOINT_ROOT,
)

# This ensures backward compatibility with code that imports from this module
__all__ = [
    # Setup functions
    "setup_symbolic_modifiers",
    "setup_eterna_world",
    "setup_physics_profiles",
    "setup_rituals",
    "setup_companions",
    "setup_protection",
    "setup_resonance_engine",
    "setup_time_and_agents",
    # Simulation functions
    "simulate_emotional_events",
    "simulate_sensory_evolution",
    # EternaWorld class and related
    "EternaWorld",
    "build_world",
    "CHECKPOINT_ROOT",
]
