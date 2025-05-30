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

        This method orchestrates the simulation step by calling more focused helper methods:
        1. Advances the physics and emotions by running a cycle
        2. Updates the RL companion system
        3. Handles law compliance and agent evolution
        4. Performs debug logging every 100 ticks
        5. Updates agent and zone states for UI feedback
        6. Saves the current state

        Args:
            dt: The time delta for this step. Defaults to 1.0.
        """
        # Advance physics / emotions
        self.eterna.runtime.run_cycle()

        # Get current companion and emotion
        companion = self.eterna.current_companion()
        emo = self.state_tracker.last_emotion or "neutral"

        # Update RL companion system
        obs, action, reward = self._update_rl_companion(companion, emo)

        # Handle law compliance and execute actions
        chosen_action_name = self._get_action_name(action)
        law_blocked = self._handle_law_compliance(companion, chosen_action_name, reward)

        if not law_blocked:
            self._execute_agent_action(companion, chosen_action_name)

        # Update agent evolution
        self._update_agent_evolution(companion)

        # Log debug information
        self._log_debug_info(emo, reward)

        # Update UI state
        self._update_ui_state()

        # Save current state
        self.state_tracker.save()

    def _update_rl_companion(self, companion, emo: str) -> Tuple[List[float], int, float]:
        """
        Update the RL companion system.

        This method:
        1. Gets observations from the current state
        2. Chooses actions based on the policy
        3. Calculates rewards based on emotions
        4. Updates the policy with the new observations

        Args:
            companion: The current companion
            emo: The current emotion

        Returns:
            Tuple containing:
            - obs: The observation vector
            - action: The chosen action
            - reward: The calculated reward
        """
        trainer = self.companion_trainer

        # Create observation vector
        val_map = {"joy": 1, "grief": -1, "anger": 0.5, "neutral": 0}
        valence = val_map.get(emo, 0)
        obs = [valence, 0, 0] + [0] * 7  # length 10

        # Get observation from state tracker
        obs = self.state_tracker.observation_vector(companion)
        obs_tensor = torch.tensor(obs, dtype=torch.float32)

        # Choose action from policy
        with torch.no_grad():
            probs = trainer.policy(obs_tensor)
            action = torch.multinomial(probs, num_samples=1).item()

        # Calculate reward based on emotion
        reward = 1 if emo == "joy" else 0

        # Create next state and observe transition
        next_obs = obs.copy()
        next_obs[0] += 0.01  # Small change to represent state transition
        trainer.observe(obs, action, reward, next_obs)

        # Train the model
        trainer.step_train(batch_size=32)

        return obs, action, reward

    def _get_action_name(self, action: int) -> str:
        """
        Convert action index to action name.

        Args:
            action: The action index

        Returns:
            The name of the action
        """
        actions = ["speak_gently", "move_zone", "start_ritual", "reflect", "idle"]
        return actions[action % len(actions)]

    def _handle_law_compliance(self, companion, chosen_action_name: str, reward: float) -> bool:
        """
        Check and enforce law compliance.

        This method checks if the chosen action is forbidden by any enabled law
        and applies the appropriate effects.

        Args:
            companion: The current companion
            chosen_action_name: The name of the chosen action
            reward: The current reward value

        Returns:
            True if the action is blocked by a law, False otherwise
        """
        law_blocked = False

        # Check each law for compliance
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

        return law_blocked

    def _execute_agent_action(self, companion, chosen_action_name: str) -> None:
        """
        Execute the chosen agent action.

        This method performs the action specified by chosen_action_name.

        Args:
            companion: The current companion
            chosen_action_name: The name of the chosen action
        """
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

    def _update_agent_evolution(self, companion) -> None:
        """
        Update agent evolution.

        This method increments the companion's evolution level.

        Args:
            companion: The current companion
        """
        if hasattr(companion, "evolution_level"):
            companion.evolution_level += 1
        else:
            companion.evolution_level = 1

    def _log_debug_info(self, emo: str, reward: float) -> None:
        """
        Log debug information.

        This method logs debug information every 100 ticks.

        Args:
            emo: The current emotion
            reward: The current reward value
        """
        trainer = self.companion_trainer

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

    def _update_ui_state(self) -> None:
        """
        Update agent and zone states for UI feedback.

        This method:
        1. Updates companion emotions
        2. Updates zone emotion tags and modifiers
        3. Randomly triggers rituals
        """
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
