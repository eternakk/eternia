"""
Module initializer for the Eternia project.

This module is responsible for initializing and registering all modules
with the dependency injection container, ensuring that dependencies are
properly resolved and injected.
"""

from modules.awareness import MultidimensionalAwareness
from modules.companion_ecology import CompanionManager
from modules.consciousness_replica import ConsciousnessReplica
from modules.dependency_injection import DependencyContainer, get_container
from modules.emotional_safety import EmotionalSafetyModule
from modules.emotions import EmotionalCircuitSystem
from modules.evolution import UserEvolution
from modules.exploration import ExplorationModule
from modules.interfaces import (
    AwarenessInterface,
    ConsciousnessInterface,
    EmotionalInterface,
    EvolutionInterface,
    ExplorationInterface,
    MemoryInterface,
    RuntimeInterface,
    SocialInterface,
    StateTrackerInterface,
)
from modules.law_parser import load_laws
from modules.laws import PhilosophicalLawbook
from modules.memory_integration import MemoryIntegrationModule
from modules.physics import PhysicsZoneRegistry
from modules.population import WorldPopulation
from modules.protection import DefenseSystem, ShellVitals, ThreatAnalyzer
from modules.reality_bridge import AgentCommunicationProtocol, RealityBridgeModule
from modules.rituals import RitualSystem
from modules.runtime import EternaRuntime, EternaState
from modules.sensory import SensoryProfile
from modules.social_interaction import SocialInteractionModule
from modules.social_presence import SoulInvitationSystem, SoulPresenceRegistry
from modules.state_tracker import EternaStateTracker
from modules.time_dilation import TimeSynchronizer
from modules.zone_modifiers import SymbolicModifierRegistry


def initialize_modules(container: DependencyContainer = None) -> DependencyContainer:
    """
    Initialize all modules and register them with the dependency injection container.
    
    Args:
        container: The dependency injection container to use. If None, the global
                  container will be used.
    
    Returns:
        The dependency injection container with all modules registered.
    """
    if container is None:
        container = get_container()
    
    # Register core components as singletons
    container.register_singleton("evolution", lambda: UserEvolution())
    container.register_singleton("consciousness_replica", lambda: ConsciousnessReplica())
    container.register_singleton("awareness", lambda: MultidimensionalAwareness())
    container.register_singleton("population", lambda: WorldPopulation())
    container.register_singleton("social_interaction", lambda: SocialInteractionModule())
    container.register_singleton("emotional_safety", lambda: EmotionalSafetyModule())
    container.register_singleton("memory_integration", lambda: MemoryIntegrationModule())
    container.register_singleton("lawbook", lambda: PhilosophicalLawbook())
    container.register_singleton("sensory_profile", lambda: SensoryProfile())
    container.register_singleton("physics_registry", lambda: PhysicsZoneRegistry())
    container.register_singleton("rituals", lambda: RitualSystem())
    container.register_singleton("soul_invitations", lambda: SoulInvitationSystem())
    container.register_singleton("soul_presence", lambda: SoulPresenceRegistry())
    container.register_singleton("vitals", lambda: ShellVitals())
    container.register_singleton("threats", lambda: ThreatAnalyzer())
    container.register_singleton("companions", lambda: CompanionManager())
    container.register_singleton("state_tracker", lambda: EternaStateTracker())
    container.register_singleton("modifiers", lambda: SymbolicModifierRegistry())
    container.register_singleton("law_registry", lambda: load_laws())
    
    # Register components that depend on other components
    container.register_singleton("reality_bridge", lambda: RealityBridgeModule(
        container.get("eterna_interface")
    ))
    container.register_singleton("exploration", lambda: ExplorationModule(
        user_intellect=container.get("evolution").intellect,
        eterna_interface=container.get("eterna_interface")
    ))
    container.register_singleton("runtime", lambda: EternaRuntime(
        container.get("eterna_interface")
    ))
    container.register_singleton("emotion_circuits", lambda: EmotionalCircuitSystem(
        eterna_interface=container.get("eterna_interface")
    ))
    container.register_singleton("defense", lambda: DefenseSystem(
        container.get("eterna_interface")
    ))
    container.register_singleton("state", lambda: EternaState(
        container.get("eterna_interface")
    ))
    container.register_singleton("time_sync", lambda: TimeSynchronizer(
        container.get("eterna_interface")
    ))
    container.register_singleton("agent_comm", lambda: AgentCommunicationProtocol(
        container.get("eterna_interface")
    ))
    
    return container