import datetime
import json
import math
import os
import random
from typing import Any, Dict, List, Optional, Union

from modules.interfaces import StateTrackerInterface
from modules.utilities.file_utils import save_json, load_json


class EternaStateTracker(StateTrackerInterface):
    """
    Tracks and manages the state of the Eterna world.

    This class is responsible for tracking various aspects of the Eterna world,
    including emotions, modifiers, memories, evolution statistics, explored zones,
    and checkpoints. It provides methods for updating and querying this state,
    as well as saving and loading it from disk.

    The state tracker is used by the AlignmentGovernor to monitor the world's
    state and ensure it remains within acceptable parameters.

    Attributes:
        save_path: Path where the state snapshot is saved.
        last_emotion: The most recent emotion experienced in the world.
        applied_modifiers: Dictionary mapping zone names to lists of modifiers.
        memories: List of memories integrated into the world.
        evolution_stats: Dictionary of evolution statistics (intellect, senses).
        discoveries: List of discoveries made in the world.
        explored_zones: List of zones that have been explored.
        last_zone: The most recently explored zone.
        modifiers: List of modifiers applied to zones.
        checkpoints: List of checkpoint paths.
        last_intensity: The intensity of the last emotion.
        last_dominance: The dominance of the last emotion.
    """

    def __init__(self, save_path="logs/state_snapshot.json"):
        """
        Initialize the EternaStateTracker.

        Args:
            save_path: Path where the state snapshot will be saved.
                Defaults to "logs/state_snapshot.json".
        """
        self.save_path = save_path
        self.last_emotion = None
        self.applied_modifiers = {}  # {zone_name: [modifier1, modifier2]}
        self.memories = []
        self.evolution_stats = {"intellect": 100, "senses": 100}
        self.discoveries = []
        # initialize previous intellect for identity_continuity()
        self._prev_intellect = self.evolution_stats["intellect"]
        self.explored_zones = []
        self.last_zone = None
        self.explored_zones = []
        self.modifiers = []
        self.discoveries = []
        self.checkpoints: list[str] = []
        self.last_emotion: str | None = None
        self.last_intensity: float = 0.0
        self.last_dominance: float = 0.0

    def initialize(self) -> None:
        """Initialize the state tracker module."""
        print("🔄 Initializing EternaStateTracker")
        # Load the state from disk if it exists
        self.load()

    def shutdown(self) -> None:
        """Perform any cleanup operations when shutting down."""
        print("🛑 Shutting down EternaStateTracker")
        # Save the current state to disk
        self.save()

    def log_emotional_impact(self, emotion_name, score):
        """
        Log the impact of an emotion on the world.

        Args:
            emotion_name: The name of the emotion.
            score: A numerical score representing the impact of the emotion.
        """
        if not hasattr(self, "emotional_log"):
            self.emotional_log = []

        self.emotional_log.append((emotion_name, round(score, 2)))

        print(f"📝 Logged emotional impact: {emotion_name} → {round(score, 2)}")

    def mark_zone(self, zone_name):
        """
        Mark a zone as the currently active zone and add it to explored zones if new.

        Args:
            zone_name: The name of the zone to mark.
        """
        self.last_zone = zone_name
        if zone_name not in self.explored_zones:
            self.explored_zones.append(zone_name)

    def track_modifier(self, zone_name, modifier):
        """
        Track a modifier applied to a zone.

        Args:
            zone_name: The name of the zone the modifier is applied to.
            modifier: The modifier being applied.
        """
        self.modifiers.append((zone_name, modifier))

    def track_discovery(self, discovery):
        """
        Track a new discovery made in the world.

        Args:
            discovery: The discovery to track.
        """
        self.discoveries.append(discovery)

    def update_emotion(self, emotion):
        """
        Update the current emotion state.

        Args:
            emotion: An emotion object with name, intensity, and direction attributes,
                    or a string representing the emotion name.
        """
        if isinstance(emotion, str):
            # Handle string input
            self.last_emotion = {
                "name": emotion,
                "intensity": 0.5,  # Default intensity
                "direction": "neutral",  # Default direction
            }
        else:
            # Handle emotion object
            self.last_emotion = {
                "name": emotion.name,
                "intensity": emotion.intensity,
                "direction": emotion.direction,
            }

    def add_modifier(self, zone, modifier):
        """
        Add a modifier to a specific zone.

        Args:
            zone: The name of the zone to add the modifier to.
            modifier: The modifier to add.
        """
        self.applied_modifiers.setdefault(zone, []).append(modifier)

    def add_memory(self, memory):
        """
        Add a memory to the world.

        Args:
            memory: The memory to add.
        """
        self.memories.append(memory)

    def record_discovery(self, discovery):
        """
        Record a discovery made in the world.

        Args:
            discovery: The discovery to record.
        """
        self.discoveries.append(discovery)

    def mark_zone_explored(self, zone_name):
        """
        Mark a zone as explored.

        Args:
            zone_name: The name of the zone to mark as explored.
        """
        if zone_name not in self.explored_zones:
            self.explored_zones.append(zone_name)

    def update_evolution(self, intellect, senses):
        """
        Update the evolution statistics.

        Args:
            intellect: The new intellect value.
            senses: The new senses value.
        """
        self.evolution_stats["intellect"] = intellect
        self.evolution_stats["senses"] = senses

    def save(self):
        """
        Save the current state to a JSON file.

        This method creates a snapshot of the current state and saves it to
        the file specified by save_path. It creates the directory if it doesn't exist.
        """
        snapshot = {
            "emotion": self.last_emotion,
            "modifiers": self.applied_modifiers,
            "memories": self.memories,
            "evolution": self.evolution_stats,
            "explored_zones": self.explored_zones,
            "discoveries": self.discoveries,
            "last_zone": self.last_zone,  # Add this line
        }
        save_json(self.save_path, snapshot, create_dirs=True, indent=2)
        print(f"💾 Eterna state saved to {self.save_path}")

    def load(self):
        """
        Load the state from a JSON file.

        This method loads a previously saved state from the file specified by
        save_path. If the file doesn't exist, it prints a warning message.
        """
        snapshot = load_json(self.save_path)
        if snapshot:
            self.last_emotion = snapshot.get("emotion")
            self.applied_modifiers = snapshot.get("modifiers", {})
            self.memories = snapshot.get("memories", [])
            self.evolution_stats = snapshot.get("evolution", self.evolution_stats)
            self.explored_zones = snapshot.get("explored_zones", [])
            self.discoveries = snapshot.get("discoveries", [])
            self.last_zone = snapshot.get("last_zone")  # Add this line
            print(f"📂 Loaded Eterna state from {self.save_path}")
        else:
            print(f"⚠️ No saved state found at {self.save_path}")

    # --- quick‑and‑dirty identity drift metric -------------------------------
    # ------------------------------------------------------------------
    # Alignment‑Governor uses this to record saved checkpoints
    # ------------------------------------------------------------------
    def register_checkpoint(self, path: str):
        """
        Append a new checkpoint path to the internal list so the UI and
        governor rollback logic can query available snapshots.
        """
        self.checkpoints.append(str(path))

    def identity_continuity(self) -> float:
        """
        Calculate a measure of identity continuity based on intellect changes.

        This is a simple metric that measures how much the intellect has changed
        since the last check. A value of 1.0 means no change, while lower values
        indicate more significant changes.

        Returns:
            float: A value between 0.0 and 1.0 representing identity continuity.
        """
        # TODO: replace with real embedding similarity
        if not hasattr(self, "_prev_intellect"):
            self._prev_intellect = self.evolution_stats["intellect"]
            return 1.0
        cur = self.evolution_stats["intellect"]
        prev = self._prev_intellect
        self._prev_intellect = cur
        return 1.0 - abs(cur - prev) / max(cur, prev, 1)

    def report(self):
        """
        Print a detailed report of the current state.

        This method prints information about the current emotion, evolution stats,
        explored zones, applied modifiers, discoveries, and memories.
        """
        print("🧾 Eterna State Report:")
        print("Last Emotion:", self.last_emotion)
        print("Evolution Stats:", self.evolution_stats)
        print(f"Explored Zones: {self.explored_zones}")
        print(f"Applied Modifiers: {self.modifiers}")
        print(f"Discoveries: {self.discoveries}")
        for zone, mods in self.applied_modifiers.items():
            print(f"  • {zone}: {mods}")
        print("Memories:")
        for mem in self.memories:
            print(
                f"  • {mem['description']} (Clarity: {mem['clarity']}, Emotion: {mem['emotional_quality']})"
            )
        print("Discoveries:")
        for disc in self.discoveries:
            print(f"  • {disc}")

    def last_zone_explored(self):
        """
        Get the name of the last zone that was explored.

        This method tries several approaches to determine the last zone:
        1. Check the last_zone attribute
        2. Check the last element of the explored_zones list
        3. Check for zones with applied modifiers

        Returns:
            str or None: The name of the last zone explored, or None if no zone has been explored.
        """
        if self.last_zone:
            return self.last_zone
        if self.explored_zones:
            return self.explored_zones[-1]
        if self.applied_modifiers:
            print("🔮 Symbolic Modifiers Applied:")
            for zone, mods in self.applied_modifiers.items():
                print(f"  • {zone}: {mods}")
        if self.applied_modifiers:
            last_modified_zone = list(self.applied_modifiers.keys())[-1]
            print(f"🔮 Last modified zone: {last_modified_zone}")
        return None

    # ------------------------------------------------------------------
    # Record that we just rolled back to a given checkpoint
    # ------------------------------------------------------------------
    def mark_rollback(self, path: str):
        """
        Update internal bookkeeping after a rollback so the UI and logs
        can show which checkpoint is active.

        Args:
            path: The path to the checkpoint that was rolled back to.
        """
        self.checkpoints.append(f"ROLLED_BACK→{path}")
        # optional: reset any per‑run counters
        if hasattr(self, "current_cycle"):
            self.current_cycle = 0

    def current_zone(self):
        """
        Get the name of the current zone.

        Returns:
            str: The name of the current zone, or "Quantum Forest" if no zone is set.
        """
        return self.last_zone or "Quantum Forest"

    def zone_index(self, zone_name: str | None) -> int:
        """
        Convert a zone name to a numerical index.

        This method uses a hash function to convert a zone name to a number
        between 0 and 9, which can be used for indexing or other purposes.

        Args:
            zone_name: The name of the zone to convert, or None.

        Returns:
            int: A number between 0 and 9 representing the zone.
        """
        return abs(hash(zone_name or "")) % 10

    def recent_reward_avg(self) -> float:
        """
        Get the average of recent rewards.

        Returns:
            float: The average of recent rewards, or 0.0 if no rewards have been recorded.
        """
        return getattr(self, "_recent_reward_avg", 0.0)

    def observation_vector(self, companion=None) -> list[float]:
        """
        Generate an observation vector for reinforcement learning.

        This method creates a vector of observations that can be used by
        reinforcement learning algorithms to make decisions. The vector includes
        information about emotions, zones, identity continuity, and other factors.

        Args:
            companion: Optional companion object to include in the observation.

        Returns:
            list[float]: A list of 10 floating-point values representing the observation.
        """
        val_map = {"joy": 1, "grief": -1, "anger": 0.5, "neutral": 0}
        emo = self.last_emotion or "neutral"
        valence = val_map.get(emo, 0)
        arousal = self.last_intensity / 10.0
        dominance = self.last_dominance / 10.0
        zone_id = self.zone_index(getattr(self, "last_zone", None)) / 10.0
        role_id = getattr(companion, "role_id", 0) / 10.0 if companion else 0.0
        convo_len = 0.0
        ident = self.identity_continuity()
        tod = math.sin(datetime.datetime.now().hour / 24 * 2 * math.pi)
        recent_r = self.recent_reward_avg()
        noise = random.random()
        return [
            valence,
            arousal,
            dominance,
            zone_id,
            role_id,
            convo_len,
            ident,
            tod,
            recent_r,
            noise,
        ]

    # bind dynamically so self.observation_vector works
    zone_index = zone_index
    identity_continuity = identity_continuity
    recent_reward_avg = recent_reward_avg
    observation_vector = observation_vector
