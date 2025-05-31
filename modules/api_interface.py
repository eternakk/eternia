"""
API Interface for the Eternia project.

This module provides a clean interface between the core simulation logic and
the API server, helping to decouple the UI/visualization components from the
core simulation logic.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from modules.dependency_injection import get_container
from modules.governor import AlignmentGovernor
from modules.interfaces import ModuleInterface


class APIInterface(ModuleInterface):
    """
    Interface between the core simulation logic and the API server.
    
    This class provides methods for the API server to interact with the core
    simulation logic without directly accessing the internal components.
    """
    
    def __init__(self, world=None, governor=None, event_queue=None):
        """
        Initialize the API interface.
        
        Args:
            world: The EternaInterface instance
            governor: The AlignmentGovernor instance
            event_queue: The event queue for communication
        """
        self._world = world
        self._governor = governor
        self._event_queue = event_queue
        self._logger = logging.getLogger(__name__)
    
    def initialize(self) -> None:
        """Initialize the API interface with any required setup."""
        if self._world is None or self._governor is None or self._event_queue is None:
            container = get_container()
            if self._world is None:
                self._world = container.get("eterna_interface")
            if self._governor is None:
                self._governor = container.get("governor")
            if self._event_queue is None:
                self._event_queue = container.get("event_queue")
    
    def shutdown(self) -> None:
        """Perform any cleanup operations when shutting down."""
        pass
    
    @property
    def world(self):
        """Get the world instance."""
        return self._world
    
    @property
    def governor(self):
        """Get the governor instance."""
        return self._governor
    
    @property
    def event_queue(self):
        """Get the event queue."""
        return self._event_queue
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the simulation.
        
        Returns:
            Dict[str, Any]: The current state
        """
        state = {
            "cycle": self._world.eterna.runtime.cycle_count,
            "identity_score": self._world.eterna.evolution.intellect,
            "emotion": None,
            "modifiers": {},
            "current_zone": "unknown"
        }
        
        # Get the current emotion if available
        if hasattr(self._world.eterna.state_tracker, "current_emotion"):
            state["emotion"] = self._world.eterna.state_tracker.current_emotion
        
        # Get the modifiers if available
        if hasattr(self._world.eterna.state_tracker, "modifiers"):
            state["modifiers"] = self._world.eterna.state_tracker.modifiers
        
        # Get the current zone if available
        if hasattr(self._world.eterna.exploration, "current_zone"):
            state["current_zone"] = self._world.eterna.exploration.current_zone
        
        return state
    
    def execute_command(self, action: str) -> Dict[str, Any]:
        """
        Execute a command in the simulation.
        
        Args:
            action: The command to execute
            
        Returns:
            Dict[str, Any]: The result of the command
        """
        result = {"success": False, "message": "Unknown command"}
        
        try:
            if action == "pause":
                self._governor.pause()
                result = {"success": True, "message": "Simulation paused"}
            elif action == "resume":
                self._governor.resume()
                result = {"success": True, "message": "Simulation resumed"}
            elif action == "shutdown":
                self._governor.shutdown()
                result = {"success": True, "message": "Simulation shutdown"}
            elif action == "step":
                metrics = self._world.collect_metrics()
                if self._governor.tick(metrics):
                    self._world.step()
                    self._world.eterna.runtime.cycle_count += 1
                    result = {"success": True, "message": "Simulation stepped"}
                else:
                    result = {"success": False, "message": "Governor prevented step"}
            elif action == "explore":
                self._world.eterna.explore_random_area()
                result = {"success": True, "message": "Exploration initiated"}
            else:
                # Try to execute the command on the world if it's a method
                if hasattr(self._world.eterna, action) and callable(getattr(self._world.eterna, action)):
                    getattr(self._world.eterna, action)()
                    result = {"success": True, "message": f"Command {action} executed"}
                else:
                    result = {"success": False, "message": f"Unknown command: {action}"}
        except Exception as e:
            self._logger.error(f"Error executing command {action}: {e}")
            result = {"success": False, "message": f"Error: {str(e)}"}
        
        return result
    
    def rollback(self, checkpoint_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Rollback the simulation to a previous state.
        
        Args:
            checkpoint_file: The checkpoint file to rollback to
            
        Returns:
            Dict[str, Any]: The result of the rollback
        """
        result = {"success": False, "message": "Rollback failed"}
        
        try:
            if checkpoint_file:
                success = self._world.eterna.state_tracker.load_from_file(checkpoint_file)
            else:
                success = self._world.eterna.state_tracker.load_latest()
            
            if success:
                result = {"success": True, "message": "Rollback successful"}
            else:
                result = {"success": False, "message": "Rollback failed: No checkpoint found"}
        except Exception as e:
            self._logger.error(f"Error during rollback: {e}")
            result = {"success": False, "message": f"Rollback error: {str(e)}"}
        
        return result
    
    def get_checkpoints(self) -> List[str]:
        """
        Get the list of available checkpoints.
        
        Returns:
            List[str]: The list of checkpoint files
        """
        try:
            return self._world.eterna.state_tracker.list_checkpoints()
        except Exception as e:
            self._logger.error(f"Error getting checkpoints: {e}")
            return []
    
    def get_laws(self) -> List[Dict[str, Any]]:
        """
        Get the list of laws.
        
        Returns:
            List[Dict[str, Any]]: The list of laws
        """
        try:
            laws = []
            for law in self._world.eterna.law_registry:
                laws.append({
                    "name": law.name,
                    "description": law.description,
                    "enabled": law.enabled
                })
            return laws
        except Exception as e:
            self._logger.error(f"Error getting laws: {e}")
            return []
    
    def toggle_law(self, name: str, enabled: bool) -> Dict[str, Any]:
        """
        Toggle a law.
        
        Args:
            name: The name of the law
            enabled: Whether the law should be enabled
            
        Returns:
            Dict[str, Any]: The result of the toggle
        """
        result = {"success": False, "message": f"Law {name} not found"}
        
        try:
            for law in self._world.eterna.law_registry:
                if law.name == name:
                    law.enabled = enabled
                    result = {
                        "success": True,
                        "message": f"Law {name} {'enabled' if enabled else 'disabled'}"
                    }
                    break
        except Exception as e:
            self._logger.error(f"Error toggling law {name}: {e}")
            result = {"success": False, "message": f"Error: {str(e)}"}
        
        return result
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """
        Get the list of agents.
        
        Returns:
            List[Dict[str, Any]]: The list of agents
        """
        try:
            agents = []
            for agent in self._world.eterna.companions.list_all():
                agents.append({
                    "name": agent.name,
                    "type": agent.type,
                    "description": agent.description
                })
            return agents
        except Exception as e:
            self._logger.error(f"Error getting agents: {e}")
            return []
    
    def get_agent(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent by name.
        
        Args:
            name: The name of the agent
            
        Returns:
            Optional[Dict[str, Any]]: The agent, or None if not found
        """
        try:
            for agent in self._world.eterna.companions.list_all():
                if agent.name == name:
                    return {
                        "name": agent.name,
                        "type": agent.type,
                        "description": agent.description,
                        "attributes": agent.attributes if hasattr(agent, "attributes") else {}
                    }
            return None
        except Exception as e:
            self._logger.error(f"Error getting agent {name}: {e}")
            return None
    
    def get_zones(self) -> List[Dict[str, Any]]:
        """
        Get the list of zones.
        
        Returns:
            List[Dict[str, Any]]: The list of zones
        """
        try:
            zones = []
            for zone in self._world.eterna.exploration.registry.list_zones():
                zones.append({
                    "name": zone.name,
                    "origin": zone.origin,
                    "complexity": zone.complexity,
                    "emotion_tag": zone.emotion_tag if hasattr(zone, "emotion_tag") else ""
                })
            return zones
        except Exception as e:
            self._logger.error(f"Error getting zones: {e}")
            return []
    
    def get_rituals(self) -> List[Dict[str, Any]]:
        """
        Get the list of rituals.
        
        Returns:
            List[Dict[str, Any]]: The list of rituals
        """
        try:
            rituals = []
            for i, ritual in enumerate(self._world.eterna.rituals.list_all()):
                rituals.append({
                    "id": i,
                    "name": ritual.name,
                    "description": ritual.description,
                    "requirements": ritual.requirements if hasattr(ritual, "requirements") else []
                })
            return rituals
        except Exception as e:
            self._logger.error(f"Error getting rituals: {e}")
            return []
    
    def trigger_ritual(self, ritual_id: int) -> Dict[str, Any]:
        """
        Trigger a ritual.
        
        Args:
            ritual_id: The ID of the ritual
            
        Returns:
            Dict[str, Any]: The result of triggering the ritual
        """
        result = {"success": False, "message": f"Ritual with ID {ritual_id} not found"}
        
        try:
            rituals = self._world.eterna.rituals.list_all()
            if 0 <= ritual_id < len(rituals):
                ritual = rituals[ritual_id]
                outcome = self._world.eterna.rituals.perform(ritual.name)
                result = {
                    "success": True,
                    "message": f"Ritual {ritual.name} performed",
                    "outcome": outcome
                }
            else:
                result = {"success": False, "message": f"Ritual with ID {ritual_id} not found"}
        except Exception as e:
            self._logger.error(f"Error triggering ritual {ritual_id}: {e}")
            result = {"success": False, "message": f"Error: {str(e)}"}
        
        return result