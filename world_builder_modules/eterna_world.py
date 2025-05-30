"""
Eterna World Class

This module contains the EternaWorld class that serves as a facade around the EternaInterface
and exposes methods expected by the AlignmentGovernor. It also includes checkpoint functionality
for saving and loading the world state.
"""

import pickle
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

import torch

from modules.ai_ml_rl.rl_companion_loop import PPOTrainer
from modules.law_parser import load_laws
from modules.state_tracker import EternaStateTracker
from eterna_interface import EternaInterface

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

CHECKPOINT_ROOT = Path("artifacts/checkpoints")


class EternaWorld:
    """
    Thin façade around EternaInterface that exposes the methods expected by AlignmentGovernor.

    This class wraps the EternaInterface and provides the methods required by the
    AlignmentGovernor: step(), collect_metrics(), save_checkpoint(), and load_checkpoint().
    It also handles the initialization of the Eterna world, including setting up zones,
    physics, rituals, companions, protection, and other components.

    The class includes a reinforcement learning loop for companions, which allows them
    to learn and adapt based on emotional feedback.

    Attributes:
        eterna: The EternaInterface instance that provides the core functionality.
        law_registry: Dictionary of laws loaded from the law registry.
        state_tracker: The EternaStateTracker for monitoring the world state.
        companion_trainer: PPOTrainer for reinforcement learning with companions.
    """

    def __init__(self) -> None:
        """
        Initialize the EternaWorld.

        This method:
        1. Creates the core EternaInterface
        2. Loads the law registry
        3. Gets the state tracker from the interface
        4. Sets up the companion trainer for reinforcement learning
        5. Performs one-time bootstrapping of the world by calling various setup functions
        """
        # Core interface
        self.eterna = EternaInterface()
        self.law_registry = load_laws(
            "laws"
        )  # <<--- Make sure this is here, near the top
        self.state_tracker: EternaStateTracker = self.eterna.state_tracker
        # RL loop for companions
        self.companion_trainer = PPOTrainer(
            obs_dim=10,  # placeholder – you'll define real obs later
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
    def step(self, dt: float = 1.0) -> None:
        """
        Advance the simulation by one step.

        This method:
        1. Advances the physics and emotions by running a cycle
        2. Updates the RL companion system:
           - Gets observations from the current state
           - Chooses actions based on the policy
           - Calculates rewards based on emotions
           - Updates the policy with the new observations
        3. Handles law compliance and agent evolution
        4. Performs debug logging every 100 ticks
        5. Updates agent and zone states for UI feedback
        6. Saves the current state

        Args:
            dt: The time delta for this step. Defaults to 1.0.
        """
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

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect metrics about the current state of the world.

        This method gathers metrics that are used by the AlignmentGovernor
        to determine if the simulation should continue, pause, or roll back.

        Returns:
            Dict[str, Any]: A dictionary of metrics, including 'identity_continuity'
                which measures how much the world's identity has changed.
        """
        return {
            "identity_continuity": self.state_tracker.identity_continuity(),
            # Placeholder for extra eval‑harness flags
        }

    # ---------- checkpoint API ---------- #
    def save_checkpoint(self, path: Path) -> None:
        """
        Save the current state of the world to a checkpoint file.

        This method serializes the entire EternaWorld instance using pickle
        and writes it to the specified path.

        Args:
            path: The path where the checkpoint should be saved.
        """
        with open(path, "wb") as f:
            pickle.dump(self, f)

    def load_checkpoint(self, path: Path) -> None:
        """
        Load a previously saved checkpoint.

        This method deserializes an EternaWorld instance from the specified path
        and updates the current instance's state to match it. This is done in-place
        so that external references to this instance remain valid.

        Args:
            path: The path to the checkpoint file to load.
        """
        with open(path, "rb") as f:
            restored: "EternaWorld" = pickle.load(f)
        # overwrite in‑place so external references remain valid
        self.__dict__.update(restored.__dict__)


# Public factory function
def build_world() -> EternaWorld:
    """
    Create and initialize a new EternaWorld instance.

    This function serves as a factory for creating EternaWorld instances.
    It ensures that the checkpoint directory exists before creating the world.

    Returns:
        EternaWorld: A fully initialized EternaWorld instance.
    """
    CHECKPOINT_ROOT.mkdir(parents=True, exist_ok=True)
    return EternaWorld()