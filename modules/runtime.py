import time
import random

from modules.resonance_engine import ResonanceEngine
from modules.emotions import EmotionalState

class EternaState:
    def __init__(self, eterna_interface):
        self.eterna = eterna_interface
        self.mode = "idle"  # options: 'exploration', 'creation', 'healing', 'social', etc.
        self.cognitive_load = 0  # 0 to 100
        self.last_cycle_summary = None

    def report(self):
        print("\n🧠 Eterna State Report:")
        print(f"  • Intellect Level     : {self.eterna.evolution.intellect}")
        print(f"  • Cognitive Load      : {self.cognitive_load}")
        print(f"  • Current Mode        : {self.mode}")

class EternaRuntime:
    def __init__(self, eterna_interface):
        self.eterna = eterna_interface
        self.state = EternaState(eterna_interface)
        self.cycle_count = 0
        self.max_cognitive_load = 100
        self.resonance = ResonanceEngine()

    def run_cycle(self):
        self.cycle_count += 1
        print(f"🌀 Runtime Cycle {self.cycle_count}")

        self.check_emotional_safety()

        current_emotion = self.eterna.emotion_circuits.current_emotion
        if current_emotion:
            print(f"🪞 Reflecting current emotional field: {current_emotion.describe()}")
            self.eterna.emotion_circuits.process_emotion(current_emotion)
            # Log emotional impact using EmotionProcessor
            from modules.emotional_agent import EmotionProcessor, EmotionalState
            if current_emotion:
                agent = EmotionProcessor()
                emotion_tensor = EmotionalState(current_emotion.name, current_emotion.intensity,
                                                current_emotion.direction).to_tensor()
                score = agent(emotion_tensor)
                self.eterna.state_tracker.log_emotional_impact(current_emotion.name, score.item())

            self.eterna.state_tracker.update_evolution(
                intellect=self.eterna.evolution.intellect,
                senses=self.eterna.senses.score()  # Make sure SensoryProfile has .score()
            )

        self.handle_exploration()
        self.refresh_reality_bridge()
        self.manage_social_interactions()
        self.apply_self_evolution()

        last_zone = self.eterna.state_tracker.last_zone_explored()
        if last_zone:
            self.resonance.apply_resonance_effects(
                zone_name=last_zone,
                frequency_hz=self.estimate_resonance_frequency(current_emotion),
                waveform="sine",
                emotional_resonance=current_emotion.name if current_emotion else None
            )

        self.eterna.synchronize_time()

        external_conditions = {'hazard_level': 7}
        self.eterna.deploy_reality_agent(external_conditions)

        self.save_persistent_states()
        self.introspect()

    def estimate_resonance_frequency(self, emotion):
        if not emotion:
            return 2.5
        emotion_map = {
            "grief": 0.5,
            "anger": 1.2,
            "curious": 2.5,
            "joy": 3.8,
            "awe": 5.1
        }
        return emotion_map.get(emotion.name, 2.5)

    def check_emotional_safety(self):
        self.state.cognitive_load += 10
        self.eterna.check_emotional_safety()
        current_emotion = self.eterna.emotion_circuits.current_emotion
        if current_emotion:
            print(f"🪞 Reflecting current emotional field: {current_emotion.describe()}")
            self.eterna.emotion_circuits.process_emotion(current_emotion)

    def apply_zone_physics(self, zone_name):
        profile = self.eterna.physics_registry.get_profile(zone_name)
        if profile:
            print(f"🧪 Applying physics profile for '{zone_name}': {profile.summary()}")
            self.state.cognitive_load += int(abs(profile.gravity - 9.8) * 2)
            if profile.dimensions > 3:
                self.eterna.evolve_user(3, 2)
                print("🌀 Spatial awareness expanded due to high-dimension zone.")
            self.eterna.adapt_senses(profile)
        else:
            print(f"⚠️ No physics profile found for zone: {zone_name}")

    def handle_exploration(self):
        if random.random() < 0.5:
            print("🌌 Triggering spontaneous exploration...")
            zone = self.eterna.exploration.explore_random_zone(return_zone=True)
            if zone:
                self.apply_zone_physics(zone.name)
                self.state.cognitive_load += 20

    def refresh_reality_bridge(self):
        if self.cycle_count % 3 == 0:
            print("🔭 Refreshing Reality Bridge...")
            self.eterna.periodic_discovery_update()

    def manage_social_interactions(self):
        if random.random() < 0.3:
            print("🤝 Engaging in a social interaction...")
            self.eterna.assign_challenge_to_users(["Alice", "Bob"])
            self.state.cognitive_load += 15

    def apply_self_evolution(self):
        if self.state.cognitive_load > 80:
            print("🧠 High load — triggering self-evolution...")
            self.eterna.evolve_user(5, 3)
            self.state.cognitive_load = 30

    def save_persistent_states(self):
        summary = f"Cycle {self.cycle_count} | Mode: {self.state.mode} | Intellect: {self.eterna.evolution.intellect} | Load: {self.state.cognitive_load}\n"
        print(f"💾 Saving to log: {summary.strip()}")
        with open("logs/eterna_cycles.log", "a") as log_file:
            log_file.write(summary)

    def introspect(self):
        print(f"🔍 Current mode: {self.state.mode}, Intellect: {self.eterna.evolution.intellect}, Load: {self.state.cognitive_load}")

    def migrate_to_eternal_shell(self):
        print("🧬 Consciousness container stabilized. Physical shell abandoned. Eterna becomes primary substrate.")