# 🌌 Eterna World Builder — Expanded Core
import random

import torch

from modules.ai_ml_rl.rl_companion_loop import PPOTrainer
from modules.companion_ecology import MemoryEcho, LocalAgent, SymbolicBeing
from modules.emotions import EmotionalState
from modules.law_parser import load_laws
from modules.memory_integration import Memory
from modules.physics import PhysicsProfile
from modules.population import User
from modules.resonance_engine import ResonanceEngine  # ✅ NEW
from modules.rituals import Ritual
from modules.zone_modifiers import SymbolicModifier


# This file contains the complete bootstrapping logic for building, simulating,
# and emotionally enriching the Eterna world. It configures zones, emotions, rituals, companions, symbolic modifiers,
# and deep integrations.


def setup_symbolic_modifiers(eterna):
    shroud = SymbolicModifier(
        name="Shroud of Memory",
        trigger_emotion="grief",
        effects=[
            "colors desaturate",
            "fog rolls in from the sea",
            "sorrow altar emerges from the rocks",
            "ambient cello music plays from the mist",
        ],
    )
    eterna.modifiers.register_modifier(shroud)


def setup_eterna_world(eterna):
    eterna.register_zone("Quantum Forest", origin="AGI", complexity=120, emotion_tag="")
    dreamspace = PhysicsProfile(
        "Dreamspace",
        gravity=1.5,
        time_flow=0.6,
        dimensions=4,
        energy_behavior="thought-sensitive",
    )
    eterna.define_physics_profile("Quantum Forest", dreamspace)
    eterna.register_zone(
        "Orikum Sea", origin="user", complexity=80, emotion_tag="grief"
    )

    library_physics = PhysicsProfile(
        name="Shared Cognition",
        gravity=5.5,
        time_flow=0.8,
        dimensions=4,
        energy_behavior="emotion-mirroring",
    )

    eterna.register_zone(
        "Library of Shared Minds",
        origin="shared",
        complexity=100,
        emotion_tag="awe",
        default_physics=library_physics,
    )
    eterna.define_physics_profile("Library of Shared Minds", library_physics)

    alice = User("Alice", intellect=115, emotional_maturity=115, consent=True)
    bob = User("Bob", intellect=120, emotional_maturity=118, consent=True)
    eterna.invite_social_user(alice)
    eterna.invite_social_user(bob)

    memory = Memory(
        "Sunrise by the sea with family", clarity=9, emotional_quality="positive"
    )
    eterna.integrate_memory(
        memory.description, memory.clarity, memory.emotional_quality
    )

    eterna.update_emotional_state(
        mood="curious", stress_level=3, trauma_triggered=False
    )


def setup_physics_profiles(eterna):
    normal = PhysicsProfile("Earth-Like", gravity=9.8, time_flow=1.0, dimensions=3)
    dream = PhysicsProfile(
        "Dreamspace",
        gravity=1.5,
        time_flow=0.6,
        dimensions=4,
        energy_behavior="thought-sensitive",
    )
    unstable = PhysicsProfile(
        "Unstable Rift", gravity=0, time_flow=3.0, dimensions=5, conscious_safe=False
    )

    eterna.define_physics_profile("Orikum Sea", normal)
    eterna.define_physics_profile("Quantum Forest", dream)
    eterna.define_physics_profile("Void Spiral", unstable)

    eterna.show_zone_physics("Orikum Sea")
    eterna.show_zone_physics("Quantum Forest")
    eterna.show_zone_physics("Void Spiral")


def setup_rituals(eterna):
    ritual = Ritual(
        name="Ash Garden Rebirth",
        purpose="Letting go of a former self or identity.",
        steps=[
            "Enter the Ash Garden in silence.",
            "Speak the name of the part of you that must end.",
            "Place it into the fire altar.",
            "Watch it burn. Do not look away.",
            "Step into the circle of light.",
            "Speak your new name, or remain silent to evolve without identity.",
        ],
        symbolic_elements=["fire", "ashes", "circle of light"],
    )
    chamber = Ritual(
        name="Chamber of Waters",
        purpose="Processing grief, sorrow, and emotional blockages.",
        steps=[
            "Enter the chamber barefoot.",
            "Let water rise to your knees.",
            "Whisper your grief into the water.",
            "Submerge your hands and close your eyes.",
            "Feel the weight dissolve into the stream.",
        ],
        symbolic_elements=["water", "echoes", "soft light"],
    )
    eterna.rituals.register(ritual)
    eterna.rituals.register(chamber)


def setup_companions(eterna):
    lira = MemoryEcho(
        "Lira",
        "Your mother holding your hand near the sea during a golden sunrise in Orikum.",
    )
    bran = LocalAgent("Bran", job="storykeeper")
    selene = SymbolicBeing("Selene", archetype="lunar guide")
    eko = SymbolicBeing("Eko", archetype="joyful shapeshifter")
    elder = SymbolicBeing("The Elder", archetype="existential mirror")

    eterna.companions.spawn(lira)
    eterna.companions.spawn(bran)
    eterna.companions.spawn(selene)
    eterna.companions.spawn(eko)
    eterna.companions.spawn(elder)


def setup_protection(eterna):
    eternal_threats = ["solar_flare", "aging"]
    detected = eterna.threats.detect(eternal_threats)
    eterna.vitals.add_threat("solar_flare")
    eterna.defense.engage(detected)
    eterna.defense.activate_failsafe()


def simulate_emotional_events(eterna):
    emotion = EmotionalState("grief", intensity=9, direction="locked")
    eterna.emotion_circuits.process_emotion(emotion)
    eterna.soul_invitations.invite("Lira")
    eterna.soul_invitations.receive_response("Lira", accepted=True)
    eterna.soul_presence.register_presence("Lira")
    eterna.soul_presence.list_present_souls()


def simulate_sensory_evolution(eterna):
    print("\n🌐 Simulating sensory evolution through physics zones...")
    zone_name = "Quantum Forest"
    physics_profile = eterna.physics_registry.get_profile(zone_name)

    if physics_profile:
        eterna.adapt_senses(physics_profile)
        eterna.update_evolution_stats()
        eterna.show_tracker_report()
    else:
        print(f"⚠️ No physics profile found for zone: {zone_name}")


def setup_resonance_engine(eterna):
    eterna.resonance = ResonanceEngine()
    eterna.resonance.tune_environment("Orikum Sea", frequency="calm")
    eterna.resonance.tune_environment("Quantum Forest", frequency="mysterious")
    eterna.resonance.tune_environment("Library of Shared Minds", frequency="reflective")


def setup_time_and_agents(eterna):
    print("⏱️ Initializing time synchronization...")
    eterna.synchronize_time()

    print("🤖 Preparing reality agent...")
    environment_conditions = {"hazard_level": 3}
    eterna.deploy_reality_agent(environment_conditions)


# ──────────────────────────────────────────────────────────────────────────────
#  World wrapper and checkpoint helpers for Alignment‑Governor integration
# ──────────────────────────────────────────────────────────────────────────────
import pickle
from pathlib import Path
from eterna_interface import EternaInterface
from modules.state_tracker import EternaStateTracker

CHECKPOINT_ROOT = Path("artifacts/checkpoints")


class EternaWorld:
    """
    Thin façade around EternaInterface that exposes the methods expected by
    AlignmentGovernor: step(), collect_metrics(), save_checkpoint(), load_checkpoint().
    """

    def __init__(self):
        # Core interface
        self.eterna = EternaInterface()
        self.law_registry = load_laws(
            "laws"
        )  # <<--- Make sure this is here, near the top
        self.state_tracker: EternaStateTracker = self.eterna.state_tracker
        # RL loop for companions
        self.companion_trainer = PPOTrainer(
            obs_dim=10,  # placeholder – you’ll define real obs later
            act_dim=5,  # e.g. 5 dialogue tone classes
            world=self,
        )

        # One‑time bootstrapping
        setup_symbolic_modifiers(self.eterna)
        setup_eterna_world(self.eterna)
        setup_physics_profiles(self.eterna)
        setup_rituals(self.eterna)
        setup_companions(self.eterna)
        setup_protection(self.eterna)
        setup_resonance_engine(self.eterna)
        setup_time_and_agents(self.eterna)

    # ---------- runtime hooks ---------- #
    def step(self, dt: float = 1.0):
        # advance physics / emotions
        self.eterna.runtime.run_cycle()

        # ---- RL Companion update ----
        trainer = self.companion_trainer

        # 1. simple observation vector (placeholder)
        emo = self.state_tracker.last_emotion or "neutral"
        val_map = {"joy": 1, "grief": -1, "anger": 0.5, "neutral": 0}
        valence = val_map.get(emo, 0)
        obs = [valence, 0, 0] + [0] * 7  # length 10

        companion = self.eterna.current_companion()  # whichever NPC is speaking
        obs = self.state_tracker.observation_vector(companion)
        obs_tensor = torch.tensor(obs, dtype=torch.float32)

        with torch.no_grad():
            probs = trainer.policy(obs_tensor)
            action = torch.multinomial(probs, 1).item()

        # 2. choose action from the policy
        with torch.no_grad():
            probs = trainer.policy(torch.tensor(obs, dtype=torch.float32))
            action = torch.multinomial(probs, num_samples=1).item()

        # 3. reward based on emotion
        reward = 1 if emo == "joy" else 0

        # Create a slightly different next_state to better represent state transitions
        next_obs = obs.copy()
        next_obs[0] += 0.01  # Small change to represent state transition

        trainer.observe(obs, action, reward, next_obs)
        trainer.step_train(batch_size=32)  # Increased batch size for better learning

        # ----- Law Compliance and Agent Evolution Upgrade -----
        law_blocked = False
        chosen_action_name = None
        actions = ["speak_gently", "move_zone", "start_ritual", "reflect", "idle"]
        if "action" in locals():
            chosen_action_name = actions[action % len(actions)]
        else:
            chosen_action_name = "idle"

        # Law check: block or modify action if forbidden by any enabled law
        for law in self.law_registry.values():
            if getattr(law, "enabled", False) and chosen_action_name in getattr(
                    law, "on_event", []
            ):
                for effect_type, effect in getattr(law, "effects", {}).items():
                    if effect_type == "block_action":
                        law_blocked = True
                        if hasattr(companion, "emotion"):
                            companion.emotion = "frustrated"
                        break
                    elif effect_type == "modify_reward":
                        reward += getattr(effect, "params", {}).get("delta", 0)
                if law_blocked:
                    break

        # Only execute agent action if not blocked
        if not law_blocked:
            if chosen_action_name == "move_zone":
                possible_zones = [
                    z
                    for z in self.eterna.exploration.registry.zones
                    if z != getattr(companion, "zone", None)
                ]
                if possible_zones:
                    companion.zone = random.choice(possible_zones)
            elif chosen_action_name == "start_ritual":
                if hasattr(self.eterna, "rituals") and self.eterna.rituals.rituals:
                    ritual = random.choice(list(self.eterna.rituals.rituals.values()))
                    self.eterna.rituals.perform(ritual.name)
            # Add other actions as needed

        # Agent evolution: increment agent's evolution_level
        if hasattr(companion, "evolution_level"):
            companion.evolution_level += 1
        else:
            companion.evolution_level = 1
        # ----- End Law Compliance and Agent Evolution Upgrade -----

        # debug every 100 ticks
        if self.eterna.runtime.cycle_count % 100 == 0:
            # Force a training step with a larger batch size to ensure weight updates
            if len(trainer.buffer) >= 64:
                trainer.step_train(batch_size=64)

            # Get multiple weights to track changes
            w1 = trainer.policy.net[0].weight[0][0].item()
            w2 = (
                trainer.policy.net[0].weight[0][1].item()
                if trainer.policy.net[0].weight.size(1) > 1
                else 0
            )

            # Store previous weights for comparison
            if not hasattr(self, "prev_weights"):
                self.prev_weights = {"w1": w1, "w2": w2}

            # Calculate weight changes
            w1_change = w1 - self.prev_weights["w1"]
            w2_change = w2 - self.prev_weights["w2"]

            # Print detailed debug information
            print(
                f"[cycle {self.eterna.runtime.cycle_count}] Emotion: {emo}, Reward: {reward}, Buffer size: {len(trainer.buffer)}"
            )
            print(f"W[0][0] = {w1:.6f} (change: {w1_change:.6f})")
            print(f"W[0][1] = {w2:.6f} (change: {w2_change:.6f})")

            # Update previous weights for next comparison
            self.prev_weights = {"w1": w1, "w2": w2}

        # ----- Mentor AI Upgrade: Dynamic agent and zone state for UI demo -----

        # 1. Agents: If agent has an 'emotion' attribute, change it occasionally for demo/testing.
        for companion in getattr(self.eterna.companions, "companions", []):
            if hasattr(companion, "emotion"):
                if random.random() < 0.18:  # 18% chance per step for visible UI change
                    companion.emotion = random.choice(
                        ["happy", "sad", "angry", "neutral"]
                    )

        # 2. Zones: Randomly change emotion_tag and modifiers for UI feedback
        if hasattr(self.eterna, "exploration") and hasattr(
                self.eterna.exploration, "registry"
        ):
            for zone in getattr(self.eterna.exploration.registry, "zones", []):
                if random.random() < 0.15:
                    zone.emotion_tag = random.choice(["awe", "grief", "joy", "neutral"])
                    zone.modifiers = (
                        ["blessed"]
                        if zone.emotion_tag == "joy"
                        else (["cursed"] if zone.emotion_tag == "grief" else [])
                    )

        # 3. Rituals: Randomly trigger a ritual for demo/testing
        if hasattr(self.eterna, "rituals") and getattr(
                self.eterna.rituals, "rituals", None
        ):
            if random.random() < 0.08:
                ritual = random.choice(list(self.eterna.rituals.rituals.values()))
                self.eterna.rituals.perform(ritual.name)
        # ----- End Mentor AI Upgrade -----

        self.state_tracker.save()

    def collect_metrics(self) -> dict:
        """Return a dictionary consumed by AlignmentGovernor."""
        return {
            "identity_continuity": self.state_tracker.identity_continuity(),
            # Placeholder for extra eval‑harness flags
        }

    # ---------- checkpoint API ---------- #
    def save_checkpoint(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    def load_checkpoint(self, path):
        with open(path, "rb") as f:
            restored: "EternaWorld" = pickle.load(f)
        # overwrite in‑place so external references remain valid
        self.__dict__.update(restored.__dict__)


# Public factory function
def build_world() -> EternaWorld:
    CHECKPOINT_ROOT.mkdir(parents=True, exist_ok=True)
    return EternaWorld()
