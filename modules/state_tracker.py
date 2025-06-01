import copy
import datetime
import json
import math
import os
import random
import time
from typing import Any, Dict, List, Optional, Union, Deque
from collections import deque

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

    Memory optimization features:
    - Uses deque for bounded collections (memories, discoveries, modifiers, checkpoints)
    - Configurable maximum sizes for collections
    - Automatic pruning of old data when limits are reached
    - Memory-efficient storage of zone and modifier information

    Attributes:
        save_path: Path where the state snapshot is saved.
        last_emotion: The most recent emotion experienced in the world.
        applied_modifiers: Dictionary mapping zone names to lists of modifiers.
        memories: Deque of memories integrated into the world (bounded).
        evolution_stats: Dictionary of evolution statistics (intellect, senses).
        discoveries: Deque of discoveries made in the world (bounded).
        explored_zones: Deque of zones that have been explored (bounded).
        last_zone: The most recently explored zone.
        modifiers: Deque of modifiers applied to zones (bounded).
        checkpoints: Deque of checkpoint paths (bounded).
        last_intensity: The intensity of the last emotion.
        last_dominance: The dominance of the last emotion.
        max_memories: Maximum number of memories to store.
        max_discoveries: Maximum number of discoveries to store.
        max_explored_zones: Maximum number of explored zones to store.
        max_modifiers: Maximum number of modifiers to store.
        max_checkpoints: Maximum number of checkpoints to store.
    """

    def __init__(self, save_path="logs/state_snapshot.json", 
                 max_memories=100, max_discoveries=50, 
                 max_explored_zones=20, max_modifiers=50, 
                 max_checkpoints=10):
        """
        Initialize the EternaStateTracker with memory optimization.

        Args:
            save_path: Path where the state snapshot will be saved.
                Defaults to "logs/state_snapshot.json".
            max_memories: Maximum number of memories to store. Defaults to 100.
            max_discoveries: Maximum number of discoveries to store. Defaults to 50.
            max_explored_zones: Maximum number of explored zones to store. Defaults to 20.
            max_modifiers: Maximum number of modifiers to store. Defaults to 50.
            max_checkpoints: Maximum number of checkpoints to store. Defaults to 10.
        """
        self.save_path = save_path
        self.last_emotion = None
        self.applied_modifiers = {}  # {zone_name: [modifier1, modifier2]}

        # Memory optimization: use bounded deques instead of unbounded lists
        self.max_memories = max_memories
        self.max_discoveries = max_discoveries
        self.max_explored_zones = max_explored_zones
        self.max_modifiers = max_modifiers
        self.max_checkpoints = max_checkpoints

        self.memories = deque(maxlen=self.max_memories)
        self.discoveries = deque(maxlen=self.max_discoveries)
        self.explored_zones = deque(maxlen=self.max_explored_zones)
        self.modifiers = deque(maxlen=self.max_modifiers)
        self.checkpoints = deque(maxlen=self.max_checkpoints)

        # Efficient indexing for state queries
        self._zone_index = set()  # Fast lookup for explored zones
        self._memory_index = {}   # Index memories by emotional_quality
        self._discovery_index = {}  # Index discoveries by category
        self._modifier_index = {}   # Index modifiers by type

        # Initialize cache for frequently accessed data
        self._cache = {}
        self._cache_ttl = {}  # Time-to-live for cached items
        self._cache_default_ttl = 100  # Default TTL in ticks

        self.evolution_stats = {"intellect": 100, "senses": 100}
        # initialize previous intellect for identity_continuity()
        self._prev_intellect = self.evolution_stats["intellect"]
        self.last_zone = None
        self.last_emotion: str | None = None
        self.last_intensity: float = 0.0
        self.last_dominance: float = 0.0

    def initialize(self) -> None:
        """Initialize the state tracker module."""
        print("🔄 Initializing EternaStateTracker")
        # Load the state from disk if it exists
        self.load()

        # Initialize cache maintenance counters
        self._cache_maintenance_counter = 0
        self._cache_maintenance_interval = 1000  # Check cache every 1000 operations

    def shutdown(self) -> None:
        """Perform any cleanup operations when shutting down."""
        print("🛑 Shutting down EternaStateTracker")
        # Clear the cache before saving to reduce file size
        self._clear_cache()
        # Save the current state to disk
        self.save()

    def _maintain_cache(self):
        """
        Perform cache maintenance operations.

        This method:
        1. Increments the maintenance counter
        2. Checks if maintenance is due
        3. Clears expired cache entries
        4. Limits the cache size

        Should be called by methods that use the cache.
        """
        # Increment the counter
        self._cache_maintenance_counter += 1

        # Check if maintenance is due
        if self._cache_maintenance_counter >= self._cache_maintenance_interval:
            # Clear expired cache entries
            expired_keys = [k for k, ttl in self._cache_ttl.items() if ttl <= 0]
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                if key in self._cache_ttl:
                    del self._cache_ttl[key]

            # Limit cache size (keep only the most recently used entries)
            if len(self._cache) > 100:  # Arbitrary limit
                # Sort by TTL (higher TTL means more recently used)
                sorted_keys = sorted(self._cache_ttl.keys(), key=lambda k: self._cache_ttl.get(k, 0), reverse=True)
                # Keep only the top 100
                keys_to_remove = sorted_keys[100:]
                for key in keys_to_remove:
                    if key in self._cache:
                        del self._cache[key]
                    if key in self._cache_ttl:
                        del self._cache_ttl[key]

            # Reset the counter
            self._cache_maintenance_counter = 0

    def _clear_cache(self):
        """
        Clear the entire cache.

        This method completely empties the cache and TTL dictionaries.
        Should be called during shutdown or when a major state change occurs.
        """
        self._cache = {}
        self._cache_ttl = {}

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

        Memory optimization:
        - Maintains an index by modifier type for efficient queries
        - Uses dictionary structure for O(1) lookups by zone

        Args:
            zone: The name of the zone to add the modifier to.
            modifier: The modifier to add. Expected to be a dictionary with at least
                     'type' and 'effect' keys, or a string.
        """
        # Add to the applied_modifiers dictionary
        self.applied_modifiers.setdefault(zone, []).append(modifier)

        # Add to the modifiers deque for tracking all modifiers
        modifier_entry = {"zone": zone, "modifier": modifier}
        self.modifiers.append(modifier_entry)

        # Update the modifier index for efficient lookups
        modifier_type = None
        if isinstance(modifier, dict) and 'type' in modifier:
            modifier_type = modifier['type']
        elif isinstance(modifier, str):
            modifier_type = modifier

        if modifier_type:
            if modifier_type not in self._modifier_index:
                self._modifier_index[modifier_type] = []
            self._modifier_index[modifier_type].append(modifier_entry)

            # If the deque is at capacity and removed an item, we need to update the index
            if len(self.modifiers) == self.max_modifiers:
                # Rebuild the entire index to ensure consistency
                self._rebuild_modifier_index()

    def _rebuild_modifier_index(self):
        """
        Rebuild the modifier index from scratch.

        This ensures the index stays consistent with the modifiers deque,
        especially after items are removed due to capacity limits.
        """
        self._modifier_index = {}
        for entry in self.modifiers:
            modifier = entry.get("modifier")
            modifier_type = None
            if isinstance(modifier, dict) and 'type' in modifier:
                modifier_type = modifier['type']
            elif isinstance(modifier, str):
                modifier_type = modifier

            if modifier_type:
                if modifier_type not in self._modifier_index:
                    self._modifier_index[modifier_type] = []
                self._modifier_index[modifier_type].append(entry)

    def get_modifiers_by_type(self, modifier_type):
        """
        Get all modifiers of the specified type.

        Uses the modifier index for efficient O(1) lookups instead of
        scanning all zones and their modifiers.

        Args:
            modifier_type: The type of modifier to search for.

        Returns:
            A list of modifier entries, each containing 'zone' and 'modifier' keys.
        """
        # Perform cache maintenance
        self._maintain_cache()

        # Check the cache first
        cache_key = f"modifiers_{modifier_type}"
        if cache_key in self._cache and self._cache_ttl.get(cache_key, 0) > 0:
            self._cache_ttl[cache_key] -= 1
            return self._cache[cache_key]

        # Use the index for efficient lookup
        result = self._modifier_index.get(modifier_type, [])

        # Cache the result for future queries
        self._cache[cache_key] = result
        self._cache_ttl[cache_key] = self._cache_default_ttl

        return result

    def add_memory(self, memory):
        """
        Add a memory to the world.

        Memory optimization: 
        - Uses a bounded deque that automatically removes the oldest memories
        - Maintains an index by emotional_quality for efficient queries
        - Handles index updates when items are removed due to capacity limits

        Args:
            memory: The memory to add. Expected to be a dictionary with at least
                   'description' and 'emotional_quality' keys.
        """
        # The deque will automatically handle removing old items when maxlen is reached
        self.memories.append(memory)

        # Update the memory index for efficient lookups
        if isinstance(memory, dict) and 'emotional_quality' in memory:
            emotional_quality = memory['emotional_quality']
            if emotional_quality not in self._memory_index:
                self._memory_index[emotional_quality] = []
            self._memory_index[emotional_quality].append(memory)

            # If the deque is at capacity and removed an item, we need to update the index
            if len(self.memories) == self.max_memories:
                # Rebuild the entire index to ensure consistency
                self._rebuild_memory_index()

    def _rebuild_memory_index(self):
        """
        Rebuild the memory index from scratch.

        This ensures the index stays consistent with the memories deque,
        especially after items are removed due to capacity limits.
        """
        self._memory_index = {}
        for memory in self.memories:
            if isinstance(memory, dict) and 'emotional_quality' in memory:
                emotional_quality = memory['emotional_quality']
                if emotional_quality not in self._memory_index:
                    self._memory_index[emotional_quality] = []
                self._memory_index[emotional_quality].append(memory)

    def get_memories_by_emotion(self, emotional_quality):
        """
        Get all memories with the specified emotional quality.

        Uses the memory index for efficient O(1) lookups instead of
        scanning the entire memories collection.

        Args:
            emotional_quality: The emotional quality to search for.

        Returns:
            A list of memories with the specified emotional quality.
        """
        # Perform cache maintenance
        self._maintain_cache()

        # Check the cache first
        cache_key = f"memories_{emotional_quality}"
        if cache_key in self._cache and self._cache_ttl.get(cache_key, 0) > 0:
            self._cache_ttl[cache_key] -= 1
            return self._cache[cache_key]

        # Use the index for efficient lookup
        result = self._memory_index.get(emotional_quality, [])

        # Cache the result for future queries
        self._cache[cache_key] = result
        self._cache_ttl[cache_key] = self._cache_default_ttl

        return result

    def record_discovery(self, discovery):
        """
        Record a discovery made in the world.

        Memory optimization: 
        - Uses a bounded deque that automatically removes the oldest discoveries
        - Maintains an index by category for efficient queries
        - Handles index updates when items are removed due to capacity limits

        Args:
            discovery: The discovery to record. Expected to be a dictionary with at least
                      'name' and 'category' keys.
        """
        # The deque will automatically handle removing old items when maxlen is reached
        self.discoveries.append(discovery)

        # Update the discovery index for efficient lookups
        if isinstance(discovery, dict) and 'category' in discovery:
            category = discovery['category']
            if category not in self._discovery_index:
                self._discovery_index[category] = []
            self._discovery_index[category].append(discovery)

            # If the deque is at capacity and removed an item, we need to update the index
            if len(self.discoveries) == self.max_discoveries:
                # Rebuild the entire index to ensure consistency
                self._rebuild_discovery_index()

    def _rebuild_discovery_index(self):
        """
        Rebuild the discovery index from scratch.

        This ensures the index stays consistent with the discoveries deque,
        especially after items are removed due to capacity limits.
        """
        self._discovery_index = {}
        for discovery in self.discoveries:
            if isinstance(discovery, dict) and 'category' in discovery:
                category = discovery['category']
                if category not in self._discovery_index:
                    self._discovery_index[category] = []
                self._discovery_index[category].append(discovery)

    def get_discoveries_by_category(self, category):
        """
        Get all discoveries in the specified category.

        Uses the discovery index for efficient O(1) lookups instead of
        scanning the entire discoveries collection.

        Args:
            category: The category to search for.

        Returns:
            A list of discoveries in the specified category.
        """
        # Perform cache maintenance
        self._maintain_cache()

        # Check the cache first
        cache_key = f"discoveries_{category}"
        if cache_key in self._cache and self._cache_ttl.get(cache_key, 0) > 0:
            self._cache_ttl[cache_key] -= 1
            return self._cache[cache_key]

        # Use the index for efficient lookup
        result = self._discovery_index.get(category, [])

        # Cache the result for future queries
        self._cache[cache_key] = result
        self._cache_ttl[cache_key] = self._cache_default_ttl

        return result

    def mark_zone_explored(self, zone_name):
        """
        Mark a zone as explored.

        Memory optimization: 
        - Uses a bounded deque that automatically removes the oldest explored zones
        - Uses a set index for O(1) lookups
        - Only adds the zone if it's not already tracked

        Args:
            zone_name: The name of the zone to mark as explored.
        """
        # Check if zone is already in the index (O(1) operation)
        if zone_name not in self._zone_index:
            # Add to the deque (which will automatically handle removing old items when maxlen is reached)
            self.explored_zones.append(zone_name)
            # Add to the index for fast lookups
            self._zone_index.add(zone_name)

            # If the deque is at capacity and removed an item, we need to update the index
            if len(self.explored_zones) == self.max_explored_zones:
                # Rebuild the index to match the current deque contents
                self._zone_index = set(self.explored_zones)

    def update_evolution(self, intellect, senses):
        """
        Update the evolution statistics.

        Args:
            intellect: The new intellect value.
            senses: The new senses value.
        """
        self.evolution_stats["intellect"] = intellect
        self.evolution_stats["senses"] = senses

    def save(self, incremental=True):
        """
        Save the current state to a JSON file.

        This method creates a snapshot of the current state and saves it to
        the file specified by save_path. It creates the directory if it doesn't exist.

        Memory optimization: 
        - Converts deques to lists before serialization
        - Limits the amount of data saved
        - Supports incremental updates to avoid saving unchanged data
        - Uses a more compact JSON representation

        Args:
            incremental: If True, only save data that has changed since the last save.
                         If False, save the entire state. Defaults to True.
        """
        # Initialize the snapshot with metadata
        snapshot = {
            "timestamp": time.time(),
            "version": getattr(self, "_state_version", 0) + 1
        }

        # Store the current version for future comparisons
        self._state_version = snapshot["version"]

        # If this is the first save or a full save is requested, save everything
        if not incremental or not hasattr(self, "_last_saved_state"):
            # Convert deques to lists for JSON serialization
            snapshot.update({
                "emotion": self.last_emotion,
                "modifiers": self.applied_modifiers,
                "memories": list(self.memories),
                "evolution": self.evolution_stats,
                "explored_zones": list(self.explored_zones),
                "discoveries": list(self.discoveries),
                "last_zone": self.last_zone,
                # Save configuration for when we load
                "max_memories": self.max_memories,
                "max_discoveries": self.max_discoveries,
                "max_explored_zones": self.max_explored_zones,
                "max_modifiers": self.max_modifiers,
                "max_checkpoints": self.max_checkpoints,
            })

            # Store a copy of the current state for future incremental saves
            self._last_saved_state = {
                "emotion": copy.deepcopy(self.last_emotion) if self.last_emotion else None,
                "modifiers": copy.deepcopy(self.applied_modifiers),
                "memories": list(self.memories),
                "evolution": copy.deepcopy(self.evolution_stats),
                "explored_zones": list(self.explored_zones),
                "discoveries": list(self.discoveries),
                "last_zone": self.last_zone,
            }
        else:
            # Incremental save: only include data that has changed
            if self.last_emotion != self._last_saved_state["emotion"]:
                snapshot["emotion"] = self.last_emotion
                self._last_saved_state["emotion"] = copy.deepcopy(self.last_emotion) if self.last_emotion else None

            # Check if modifiers have changed
            if self.applied_modifiers != self._last_saved_state["modifiers"]:
                snapshot["modifiers"] = self.applied_modifiers
                self._last_saved_state["modifiers"] = copy.deepcopy(self.applied_modifiers)

            # For collections, check if they've changed in size or content
            current_memories = list(self.memories)
            if len(current_memories) != len(self._last_saved_state["memories"]) or set(str(m) for m in current_memories) != set(str(m) for m in self._last_saved_state["memories"]):
                snapshot["memories"] = current_memories
                self._last_saved_state["memories"] = current_memories

            # Check if evolution stats have changed
            if self.evolution_stats != self._last_saved_state["evolution"]:
                snapshot["evolution"] = self.evolution_stats
                self._last_saved_state["evolution"] = copy.deepcopy(self.evolution_stats)

            # Check if explored zones have changed
            current_zones = list(self.explored_zones)
            if set(current_zones) != set(self._last_saved_state["explored_zones"]):
                snapshot["explored_zones"] = current_zones
                self._last_saved_state["explored_zones"] = current_zones

            # Check if discoveries have changed
            current_discoveries = list(self.discoveries)
            if set(str(d) for d in current_discoveries) != set(str(d) for d in self._last_saved_state["discoveries"]):
                snapshot["discoveries"] = current_discoveries
                self._last_saved_state["discoveries"] = current_discoveries

            # Check if last zone has changed
            if self.last_zone != self._last_saved_state["last_zone"]:
                snapshot["last_zone"] = self.last_zone
                self._last_saved_state["last_zone"] = self.last_zone

        # Use a more compact JSON representation (no indent) to save space
        save_json(self.save_path, snapshot, create_dirs=True, indent=None)
        print(f"💾 Eterna state saved to {self.save_path} (version {snapshot['version']}, {'incremental' if incremental else 'full'})")

    def load(self):
        """
        Load the state from a JSON file.

        This method loads a previously saved state from the file specified by
        save_path. If the file doesn't exist, it prints a warning message.

        Memory optimization: 
        - Converts loaded lists to bounded deques
        - Respects the configured maximum sizes
        - Handles incremental state updates
        - Maintains a cache of the loaded state for future incremental saves
        """
        snapshot = load_json(self.save_path)
        if snapshot:
            # Check if this is an incremental update (has version and timestamp)
            is_incremental = "version" in snapshot and "timestamp" in snapshot

            # Store the version for future saves
            if is_incremental:
                self._state_version = snapshot.get("version", 0)

            # Update configuration parameters if present
            if "max_memories" in snapshot:
                self.max_memories = snapshot.get("max_memories", self.max_memories)
                self.max_discoveries = snapshot.get("max_discoveries", self.max_discoveries)
                self.max_explored_zones = snapshot.get("max_explored_zones", self.max_explored_zones)
                self.max_modifiers = snapshot.get("max_modifiers", self.max_modifiers)
                self.max_checkpoints = snapshot.get("max_checkpoints", self.max_checkpoints)

            # Update state attributes if present in the snapshot
            if "emotion" in snapshot:
                self.last_emotion = snapshot.get("emotion")

            if "modifiers" in snapshot:
                self.applied_modifiers = snapshot.get("modifiers", {})

            if "memories" in snapshot:
                # Reset deques with new max sizes
                self.memories = deque(snapshot.get("memories", []), maxlen=self.max_memories)

            if "discoveries" in snapshot:
                self.discoveries = deque(snapshot.get("discoveries", []), maxlen=self.max_discoveries)

            if "explored_zones" in snapshot:
                self.explored_zones = deque(snapshot.get("explored_zones", []), maxlen=self.max_explored_zones)

            if "evolution" in snapshot:
                self.evolution_stats = snapshot.get("evolution", self.evolution_stats)

            if "last_zone" in snapshot:
                self.last_zone = snapshot.get("last_zone")

            # Store a copy of the current state for future incremental saves
            self._last_saved_state = {
                "emotion": copy.deepcopy(self.last_emotion) if self.last_emotion else None,
                "modifiers": copy.deepcopy(self.applied_modifiers),
                "memories": list(self.memories),
                "evolution": copy.deepcopy(self.evolution_stats),
                "explored_zones": list(self.explored_zones),
                "discoveries": list(self.discoveries),
                "last_zone": self.last_zone,
            }

            print(f"📂 Loaded Eterna state from {self.save_path} (version {getattr(self, '_state_version', 'unknown')})")
        else:
            print(f"⚠️ No saved state found at {self.save_path}")

    # --- quick‑and‑dirty identity drift metric -------------------------------
    # ------------------------------------------------------------------
    # Alignment‑Governor uses this to record saved checkpoints
    # ------------------------------------------------------------------
    def register_checkpoint(self, path: str):
        """
        Append a new checkpoint path to the internal deque so the UI and
        governor rollback logic can query available snapshots.

        Memory optimization: Uses a bounded deque that automatically removes
        the oldest checkpoints when the maximum size is reached.
        """
        # The deque will automatically handle removing old items when maxlen is reached
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

    def list_checkpoints(self) -> List[str]:
        """
        Get a list of all registered checkpoint paths.

        Returns:
            List[str]: A list of checkpoint paths as strings.
        """
        return list(self.checkpoints)

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

        # Extract emotion name if it's a dictionary
        if isinstance(emo, dict):
            emo = emo.get("name", "neutral")

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
