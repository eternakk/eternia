"""
Standardized interfaces for major system components in the Eternia project.

This module defines abstract base classes that standardize how different
components of the Eternia system interact with each other. By implementing
these interfaces, components can be more easily swapped or extended without
affecting other parts of the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union


class ModuleInterface(ABC):
    """Base interface that all module interfaces should inherit from."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the module with any required setup."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Perform any cleanup operations when shutting down the module."""
        pass


class EvolutionInterface(ModuleInterface):
    """Interface for evolution-related functionality."""
    
    @abstractmethod
    def evolve(self, intellect_inc: int, senses_inc: int) -> None:
        """
        Evolve the user's capabilities.
        
        Args:
            intellect_inc: The amount to increase intellect by
            senses_inc: The amount to increase senses by
        """
        pass
    
    @property
    @abstractmethod
    def intellect(self) -> int:
        """Get the current intellect level."""
        pass


class ConsciousnessInterface(ModuleInterface):
    """Interface for consciousness-related functionality."""
    
    @abstractmethod
    def calibrate(self, feedback: Dict[str, Any]) -> None:
        """
        Calibrate the consciousness replica based on feedback.
        
        Args:
            feedback: Dictionary containing calibration parameters
        """
        pass


class AwarenessInterface(ModuleInterface):
    """Interface for awareness-related functionality."""
    
    @abstractmethod
    def integrate_new_dimension(self) -> None:
        """Integrate a new dimension into awareness."""
        pass


class SocialInterface(ModuleInterface):
    """Interface for social interaction functionality."""
    
    @abstractmethod
    def invite_user(self, user_profile: Dict[str, Any]) -> None:
        """
        Invite a user to participate in social interactions.
        
        Args:
            user_profile: Dictionary containing user profile information
        """
        pass
    
    @abstractmethod
    def initiate_safe_interaction(self, user1_name: str, user2_name: str) -> None:
        """
        Initiate a safe interaction between two users.
        
        Args:
            user1_name: Name of the first user
            user2_name: Name of the second user
        """
        pass


class EmotionalInterface(ModuleInterface):
    """Interface for emotional functionality."""
    
    @abstractmethod
    def monitor_and_manage_emotions(self) -> bool:
        """
        Monitor and manage emotions for safety.
        
        Returns:
            bool: True if emotional state is safe, False otherwise
        """
        pass
    
    @abstractmethod
    def update_emotional_state(self, mood: str, stress_level: int, trauma_triggered: bool = False) -> None:
        """
        Update the emotional state.
        
        Args:
            mood: The current mood
            stress_level: The current stress level
            trauma_triggered: Whether trauma has been triggered
        """
        pass


class MemoryInterface(ModuleInterface):
    """Interface for memory-related functionality."""
    
    @abstractmethod
    def process_memory(self, memory: Any) -> Dict[str, Any]:
        """
        Process a memory for integration.
        
        Args:
            memory: The memory to process
            
        Returns:
            Dict[str, Any]: Result of memory processing
        """
        pass


class ExplorationInterface(ModuleInterface):
    """Interface for exploration functionality."""
    
    @abstractmethod
    def explore_random_zone(self) -> None:
        """Explore a random zone."""
        pass
    
    @abstractmethod
    def register_zone(self, zone: Any) -> None:
        """
        Register a new exploration zone.
        
        Args:
            zone: The zone to register
        """
        pass


class RuntimeInterface(ModuleInterface):
    """Interface for runtime functionality."""
    
    @abstractmethod
    def run_cycle(self) -> None:
        """Run a single cycle of the runtime."""
        pass


class StateTrackerInterface(ModuleInterface):
    """Interface for state tracking functionality."""
    
    @abstractmethod
    def save(self) -> None:
        """Save the current state."""
        pass
    
    @abstractmethod
    def load(self) -> None:
        """Load the saved state."""
        pass
    
    @abstractmethod
    def update_emotion(self, emotion: str) -> None:
        """
        Update the tracked emotional state.
        
        Args:
            emotion: The emotion to track
        """
        pass
    
    @abstractmethod
    def add_memory(self, memory: Dict[str, Any]) -> None:
        """
        Add a memory to the state tracker.
        
        Args:
            memory: Dictionary containing memory information
        """
        pass
    
    @abstractmethod
    def record_discovery(self, discovery: str) -> None:
        """
        Record a discovery in the state tracker.
        
        Args:
            discovery: The discovery to record
        """
        pass
    
    @abstractmethod
    def mark_zone_explored(self, zone_name: str) -> None:
        """
        Mark a zone as explored.
        
        Args:
            zone_name: Name of the zone to mark as explored
        """
        pass
    
    @abstractmethod
    def update_evolution(self, intellect: int, senses: int) -> None:
        """
        Update evolution stats in the state tracker.
        
        Args:
            intellect: Current intellect level
            senses: Current senses level
        """
        pass