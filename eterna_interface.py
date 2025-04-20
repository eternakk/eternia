from contextlib import nullcontext

from modules.awareness import MultidimensionalAwareness
from modules.companion_ecology import CompanionManager
from modules.consciousness_replica import ConsciousnessReplica
from modules.emotional_safety import EmotionalSafetyModule
from modules.emotions import EmotionalCircuitSystem
from modules.evolution import UserEvolution
from modules.exploration import ExplorationModule, ExplorationZone
from modules.laws import PhilosophicalLawbook
from modules.memory_integration import MemoryIntegrationModule, Memory
from modules.physics import PhysicsZoneRegistry, PhysicsProfile
from modules.population import WorldPopulation
from modules.protection import ShellVitals, ThreatAnalyzer, DefenseSystem
from modules.reality_bridge import RealityBridgeModule, AgentCommunicationProtocol
from modules.rituals import RitualSystem
from modules.runtime import EternaRuntime, EternaState
from modules.sensory import SensoryProfile
from modules.social_interaction import SocialInteractionModule
from modules.social_presence import SoulInvitationSystem, SoulPresenceRegistry
from modules.state_tracker import EternaStateTracker
from modules.time_dilation import TimeSynchronizer
from modules.zone_modifiers import SymbolicModifierRegistry


class EternaInterface:
    def __init__(self):
        self.evolution = UserEvolution()
        self.replica = ConsciousnessReplica()
        self.awareness = MultidimensionalAwareness()
        self.population = WorldPopulation()
        self.reality_bridge = RealityBridgeModule(self)
        self.social_interaction = SocialInteractionModule()
        self.emotional_safety = EmotionalSafetyModule()
        self.memory_integration = MemoryIntegrationModule()
        self.exploration = ExplorationModule(user_intellect=self.evolution.intellect)
        self.runtime = EternaRuntime(self)
        self.lawbook = PhilosophicalLawbook()
        self.senses = SensoryProfile()
        self.physics_registry = PhysicsZoneRegistry()
        self.exploration = ExplorationModule(user_intellect=self.evolution.intellect, eterna_interface=self)
        self.rituals = RitualSystem()
        self.emotion_circuits = EmotionalCircuitSystem(eterna_interface=self)
        self.soul_invitations = SoulInvitationSystem()
        self.soul_presence = SoulPresenceRegistry()
        self.vitals = ShellVitals()
        self.threats = ThreatAnalyzer()
        self.defense = DefenseSystem(self)
        self.state = EternaState(self)
        self.companions = CompanionManager()
        self.state_tracker = EternaStateTracker()
        self.state_tracker.load()
        self.modifiers = SymbolicModifierRegistry()
        self.time_sync = TimeSynchronizer(self)
        self.agent_comm = AgentCommunicationProtocol(self)

    def synchronize_time(self):
        self.time_sync.adjust_time_flow(self.senses)
        self.time_sync.synchronize()

    def deploy_reality_agent(self, environment_conditions):
        self.agent_comm.deploy_agent(environment_conditions)

    def recall_reality_agent(self):
        self.agent_comm.recall_agent()

    # 🧠 Emotion Tracking
    def log_emotion(self, emotion):
        self.state_tracker.update_emotion(emotion)

    # 🎭 Modifier Logging
    def log_modifier(self, zone, modifier):
        self.state_tracker.add_modifier(zone, modifier)
        print(f"🌗 Zone '{zone}' was symbolically modified with '{modifier}'.")


    # 📚 Memory Tracking
    def log_memory(self, memory):
        self.state_tracker.add_memory({
            "description": memory.description,
            "clarity": memory.clarity,
            "emotional_quality": memory.emotional_quality
        })

    def show_tracker_report(self):
        self.state_tracker.report()

    # 🔍 Discovery Tracking
    def log_discovery(self, discovery):
        self.state_tracker.record_discovery(discovery)
        print(f"🧭 New discovery logged: {discovery}")

    # 🗺️ Exploration Zone Logging
    def mark_explored_zone(self, zone_name):
        self.state_tracker.mark_zone_explored(zone_name)

    # 📈 Evolution Progress
    def update_evolution_stats(self):
        sense_score = 0
        if self.senses.visual_range == "multiplanar":
            sense_score += 1
        if self.senses.hearing == "resonant":
            sense_score += 1
        if self.senses.balance == "stabilized":
            sense_score += 1

        self.state_tracker.update_evolution(
            intellect=self.evolution.intellect,
            senses=100 + sense_score * 5  # scale senses evolution with enhancements
        )
    def run_eterna(self, cycles=1):
        for _ in range(cycles):
            self.runtime.run_cycle()
            self.state_tracker.save()

    def show_laws(self):
        self.lawbook = PhilosophicalLawbook

    def toggle_law(self, name, status):
        self.lawbook.toggle_law(name, status)

    def define_physics_profile(self, zone_name, profile: PhysicsProfile):
        self.physics_registry.assign_profile(zone_name, profile)

    # Inside eterna_interface.py
    def synchronize_evolution_state(self):
        self.state_tracker.update_evolution(
            intellect=self.evolution.intellect,
            senses=self.senses.score()
        )

    def show_zone_physics(self, zone_name):
        profile = self.physics_registry.get_profile(zone_name)
        if profile:
            print(f"📊 Physics for '{zone_name}': {profile.summary()}")
        else:
            print(f"❓ No physics profile found for zone: {zone_name}")

    def adapt_senses(self, physics_profile):
        self.senses.adapt_to_physics(physics_profile)

    def periodic_discovery_update(self):
        discoveries = self.reality_bridge.periodic_update()
        self._log_discovery_report(discoveries)
        return discoveries

    def explore_and_integrate(self, discovery):
        if self.reality_bridge.explore_discovery(discovery):
            self._integrate_dimension()

    def interpret_thought(self, thought):
        if self._is_ready_for_manifestation(thought):
            return self.instant_manifest(thought)
        return self.abstract_concept_representation(thought)

    def instant_manifest(self, thought):
        self._log_manifestation(thought.description)
        return "Immersive World Created"

    def abstract_concept_representation(self, thought):
        print(f"🔮 Abstract representation of: {thought.description}")
        if not self.emotional_safety_check(thought):
            self.therapeutic_refinement(thought)
        return self.refine_abstract_concept(thought)

    def emotional_safety_check(self, thought):
        if thought.emotional_quality == 'negative':
            print("⚠️ Negative emotion detected. Pausing for refinement.")
            return False
        return True

    def spawn_companion(self, companion):
        self.companions.spawn(companion)

    def interact_with_companion(self, name):
        self.companions.interact_with(name)

    def therapeutic_refinement(self, thought):
        print("🛠️ Therapeutic refinement mode activated.")
        thought.emotional_quality = 'neutral'
        thought.clarity_level += 2
        print("✅ Thought refined therapeutically.")

    def refine_abstract_concept(self, thought):
        print("🎛️ Refining abstract concept...")
        thought.clarity_level = min(10, thought.clarity_level + 3)
        thought.emotional_quality = 'positive'
        return self.final_approval_check(thought)

    def final_approval_check(self, thought):
        if self._get_user_confirmation():
            self._log_user_approval(thought.description)
            return self.instant_manifest(thought)
        print("👎 User declined. Further refinement needed.")
        return "Refinement Continues"

    def evolve_user(self, intellect_inc, senses_inc):
        self.evolution.evolve(intellect_inc, senses_inc)
        self.runtime.state.intellect_level = self.evolution.intellect  # <--- Sync

    def calibrate_replica(self, feedback):
        self.replica.calibrate(feedback)

    def add_dimension(self):
        self._integrate_dimension()

    def invite_new_user(self, user):
        self.population.invite_user(user)

    # -- Extracted Private Helper Methods --

    def _is_ready_for_manifestation(self, thought):
        return thought.clarity_level >= 7 and thought.emotional_quality == 'positive'

    def _integrate_dimension(self):
        self.awareness.integrate_new_dimension()

    def _get_user_confirmation(self):
        # Placeholder method representing possible user interaction
        return True

    def _log_manifestation(self, description):
        print(f"✨ Instantly manifesting: {description} ✨")

    def _log_discovery_report(self, discoveries):
        print(f"🔍 {len(discoveries)} new prioritized discoveries ready for exploration.")

    def _log_user_approval(self, description):
        print(f"👍 User approved final manifestation: {description}")

    def invite_social_user(self, user_profile):
        self.social_interaction.invite_user(user_profile)

    def initiate_interaction(self, user1_name, user2_name):
        self.social_interaction.initiate_safe_interaction(user1_name, user2_name)

    def assign_challenge_to_users(self, user_names):
        self.social_interaction.assign_collaborative_challenge(user_names)

    def check_emotional_safety(self):
        return self.emotional_safety.monitor_and_manage_emotions()

    def update_emotional_state(self, mood, stress_level, trauma_triggered=False):
        self.emotional_safety.ems.update_emotional_state(mood, stress_level, trauma_triggered)

    def integrate_memory(self, description, clarity, emotional_quality):
        memory = Memory(description, clarity, emotional_quality)
        result = self.memory_integration.process_memory(memory)
        return result

    def register_zone(self, name, origin, complexity, emotion_tag="", default_physics=None):
        zone = ExplorationZone(name, origin, complexity)
        zone.emotion_tag = emotion_tag
        self.exploration.registry.register_zone(zone)

        # Optional: assign a default physics profile
        if default_physics:
            self.define_physics_profile(name, default_physics)

    def explore_random_area(self):
        self.exploration.explore_random_zone()

    # In eterna_interface.py
    def list_companions(self):
        self.companions.list_companions()

    def list_rituals(self):
        self.rituals.list_rituals()

    def mark_zone_explored(self, zone_name):
        self.state_tracker.mark_zone(zone_name)

    def track_modifier(self, zone_name, modifier):
        self.state_tracker.track_modifier(zone_name, modifier)

    def register_discovery(self, discovery):
        self.state_tracker.track_discovery(discovery)

    def runtime_report(self):
        state = self.runtime.state
        print("\n📘 Runtime Report")
        print(f"  🧠 Final Intellect: {state.intellect_level}")
        print(f"  🔄 Last Mode: {state.mode}")
        print(f"  ⚖️ Final Cognitive Load: {state.cognitive_load}")