# modules/runtime.py

import time
import random

class EternaState:
    def __init__(self):
        self.mode = "idle"  # options: 'exploration', 'creation', 'healing', 'social', etc.
        self.cognitive_load = 0  # 0 to 100
        self.intellect_level = 100  # evolves over time
        self.last_cycle_summary = None

class EternaRuntime:
    def __init__(self, eterna_interface):
        self.state = EternaState()
        self.eterna = eterna_interface
        self.cycle_count = 0
        self.max_cognitive_load = 100

    def run_cycle(self):
        self.cycle_count += 1
        print(f"🌀 Runtime Cycle {self.cycle_count}")

        self.check_emotional_safety()
        self.handle_exploration()
        self.refresh_reality_bridge()
        self.manage_social_interactions()
        self.apply_self_evolution()
        self.save_persistent_states()

        self.introspect()

    def check_emotional_safety(self):
        self.state.cognitive_load += 10
        self.eterna.check_emotional_safety()

    def apply_zone_physics(self, zone_name):
        profile = self.eterna.physics_registry.get_profile(zone_name)
        if profile:
            print(f"🧪 Applying physics profile for '{zone_name}': {profile.summary()}")
            # simulate a brain/body adaptation load
            self.state.cognitive_load += int(abs(profile.gravity - 9.8) * 2)
            self.eterna.adapt_senses(profile)
            if profile.dimensions > 3:
                self.eterna.evolve_user(3, 2)
                print("🌀 Spatial awareness expanded due to high-dimension zone.")
        else:
            print(f"⚠️ No physics profile found for zone '{zone_name}'.")

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
            self.state.intellect_level += 5
            self.state.cognitive_load = 30  # cool down

    def save_persistent_states(self):
        summary = f"Cycle {self.cycle_count} | Mode: {self.state.mode} | Intellect: {self.state.intellect_level} | Load: {self.state.cognitive_load}\n"
        print(f"💾 Saving to log: {summary.strip()}")

        with open("logs/eterna_cycles.log", "a") as log_file:
            log_file.write(summary)

    def introspect(self):
        print(f"🔍 Current mode: {self.state.mode}, Intellect: {self.state.intellect_level}, Load: {self.state.cognitive_load}")

