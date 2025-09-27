import copy
import datetime
import json
import math
import os
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Deque
from collections import deque

from modules.interfaces import StateTrackerInterface
from modules.utilities.file_utils import save_json, load_json
from modules.database import EternaDatabase


def _utc_now_iso() -> str:
    """Return the current UTC timestamp in RFC3339 format."""
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _iso_from_timestamp(timestamp: float) -> str:
    """Convert a UNIX timestamp (seconds) to an ISO-8601 string."""
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_from_iso(value: str) -> Optional[float]:
    """Parse an ISO-8601 timestamp into epoch seconds, returning None on failure."""
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.datetime.fromisoformat(value).timestamp()
    except Exception:
        return None


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
                 max_checkpoints=10,
                 db_path="data/eternia.db",
                 use_database=True,
                 use_lazy_loading=True):
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
            db_path: Path to the SQLite database file. Defaults to "data/eternia.db".
            use_database: Whether to use the database for persistence. Defaults to True.
                If False, will fall back to JSON-based persistence.
            use_lazy_loading: Whether to use lazy loading for collections. Defaults to True.
                This can significantly reduce memory usage for large states.
        """
        self.save_path = save_path
        self.db_path = db_path
        self.use_database = use_database
        self.use_lazy_loading = use_lazy_loading
        self.last_emotion = None
        self.applied_modifiers = {}  # {zone_name: [modifier1, modifier2]}

        # Initialize database if enabled
        self.db = None
        if self.use_database:
            self.db = EternaDatabase(db_path=self.db_path)

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

        # Versioning for snapshot alignment
        self._state_version = 0
        self._last_saved_state: Dict[str, Any] = {}

        # Lazy loading state
        self._lazy_state = None
        self._collections_accessed = set()

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
        # Save the current state to disk or database
        self.save()
        # Close the database connection if it exists
        if self.use_database and self.db:
            self.db.close()
            print("🔌 Closed database connection")

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
        Publishes a ZoneChangedEvent to notify other components.

        Args:
            zone_name: The name of the zone to mark.
        """
        from modules.utilities.event_bus import event_bus
        from modules.zone_events import ZoneChangedEvent
        from modules.logging_config import get_logger

        logger = get_logger("zone_changes")

        is_new = zone_name not in self.explored_zones
        previous_zone = self.last_zone
        self.last_zone = zone_name

        # Log zone change
        if previous_zone != zone_name:
            logger.info(f"🌍 Zone changed from '{previous_zone}' to '{zone_name}'")

        if is_new:
            self.explored_zones.append(zone_name)
            logger.info(f"🆕 New zone discovered: '{zone_name}'")

        # Publish event to notify other components
        event_bus.publish(ZoneChangedEvent(zone_name, is_new))

    def track_modifier(self, zone_name, modifier):
        """
        Track a modifier applied to a zone.

        This method is maintained for backward compatibility and now calls add_modifier.

        Args:
            zone_name: The name of the zone the modifier is applied to.
            modifier: The modifier being applied.
        """
        # Call add_modifier for standardized modifier tracking
        self.add_modifier(zone_name, modifier)

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
        Publishes a ZoneModifierAddedEvent to notify other components.

        Memory optimization:
        - Maintains an index by modifier type for efficient queries
        - Uses dictionary structure for O(1) lookups by zone

        Args:
            zone: The name of the zone to add the modifier to.
            modifier: The modifier to add. Expected to be a dictionary with at least
                     'type' and 'effect' keys, or a string.
        """
        from modules.utilities.event_bus import event_bus
        from modules.zone_events import ZoneModifierAddedEvent
        from modules.logging_config import get_logger

        logger = get_logger("zone_modifiers")

        # Log the modifier being added
        modifier_str = modifier if isinstance(modifier, str) else str(modifier)
        logger.info(f"🔄 Adding modifier '{modifier_str}' to zone '{zone}'")

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
                logger.debug(f"Rebuilt modifier index due to capacity limit ({self.max_modifiers})")

        # Get current modifiers for the zone for logging
        zone_modifiers = self.applied_modifiers.get(zone, [])
        logger.info(f"🔍 Zone '{zone}' now has {len(zone_modifiers)} modifiers: {zone_modifiers}")

        # Publish event to notify other components
        event_bus.publish(ZoneModifierAddedEvent(zone, modifier))

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
        # Ensure modifiers are loaded if using lazy loading
        self._ensure_collection_loaded("modifiers")

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

    def get_modifiers_by_zone(self, zone_name):
        """
        Get all modifiers for the specified zone.

        Args:
            zone_name: The name of the zone to get modifiers for.

        Returns:
            A list of modifiers for the specified zone.
        """
        # Ensure modifiers are loaded if using lazy loading
        try:
            self._ensure_collection_loaded("modifiers")
        except (AttributeError, Exception):
            # If the method doesn't exist or fails, continue anyway
            pass

        # Perform cache maintenance if the method exists
        try:
            if hasattr(self, '_maintain_cache'):
                self._maintain_cache()
        except (AttributeError, Exception):
            # If the method doesn't exist or fails, continue anyway
            pass

        # Check the cache first if it exists
        try:
            cache_key = f"zone_modifiers_{zone_name}"
            if hasattr(self, '_cache') and hasattr(self, '_cache_ttl') and cache_key in self._cache and self._cache_ttl.get(cache_key, 0) > 0:
                self._cache_ttl[cache_key] -= 1
                return self._cache[cache_key]
        except (AttributeError, Exception):
            # If the cache doesn't exist or fails, continue anyway
            pass

        # Get modifiers for the zone from the applied_modifiers dictionary
        result = self.applied_modifiers.get(zone_name, [])

        # Cache the result for future queries if the cache exists
        try:
            if hasattr(self, '_cache') and hasattr(self, '_cache_ttl') and hasattr(self, '_cache_default_ttl'):
                self._cache[cache_key] = result
                self._cache_ttl[cache_key] = self._cache_default_ttl
        except (AttributeError, Exception):
            # If the cache doesn't exist or fails, continue anyway
            pass

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

    def _ensure_collection_loaded(self, collection_name):
        """
        Ensure a collection is loaded if using lazy loading.

        Args:
            collection_name: The name of the collection to ensure is loaded.
        """
        if not self.use_lazy_loading or not self.use_database or not self.db or not self._lazy_state:
            # Not using lazy loading or no lazy state available
            return

        if collection_name in self._collections_accessed:
            # Already accessed this collection
            return

        # Mark as accessed
        self._collections_accessed.add(collection_name)

        # Load the collection
        if collection_name == "memories":
            memories = self.db.lazy_load_collection(self._lazy_state, "memories")
            self.memories = deque(memories, maxlen=self.max_memories)
            self._rebuild_memory_index()
            # Update last_saved_state
            self._last_saved_state["memories"] = list(self.memories)
        elif collection_name == "discoveries":
            discoveries = self.db.lazy_load_collection(self._lazy_state, "discoveries")
            self.discoveries = deque(discoveries, maxlen=self.max_discoveries)
            self._rebuild_discovery_index()
            # Update last_saved_state
            self._last_saved_state["discoveries"] = list(self.discoveries)
        elif collection_name == "explored_zones":
            explored_zones = self.db.lazy_load_collection(self._lazy_state, "explored_zones")
            self.explored_zones = deque(explored_zones, maxlen=self.max_explored_zones)
            self._zone_index = set(self.explored_zones)
            # Update last_saved_state
            self._last_saved_state["explored_zones"] = list(self.explored_zones)
        elif collection_name == "modifiers":
            modifiers_dict = self.db.lazy_load_collection(self._lazy_state, "modifiers")
            # Update applied_modifiers
            self.applied_modifiers = modifiers_dict
            # Rebuild modifiers deque
            self.modifiers = deque(maxlen=self.max_modifiers)
            for zone, mods in modifiers_dict.items():
                for mod in mods:
                    self.modifiers.append({"zone": zone, "modifier": mod})
            self._rebuild_modifier_index()
        elif collection_name == "checkpoints":
            checkpoints = self.db.lazy_load_collection(self._lazy_state, "checkpoints")
            normalized = [self._normalize_checkpoint_entry(entry) for entry in checkpoints]
            self.checkpoints = deque(normalized, maxlen=self.max_checkpoints)
            self._last_saved_state["checkpoints"] = [copy.deepcopy(entry) for entry in self.checkpoints]

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
        # Ensure memories are loaded if using lazy loading
        self._ensure_collection_loaded("memories")

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
        # Ensure discoveries are loaded if using lazy loading
        self._ensure_collection_loaded("discoveries")

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
        Publishes a ZoneExploredEvent to notify other components.

        Memory optimization: 
        - Uses a bounded deque that automatically removes the oldest explored zones
        - Uses a set index for O(1) lookups
        - Only adds the zone if it's not already tracked

        Args:
            zone_name: The name of the zone to mark as explored.
        """
        from modules.utilities.event_bus import event_bus
        from modules.zone_events import ZoneExploredEvent

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

            # Publish event to notify other components
            event_bus.publish(ZoneExploredEvent(zone_name))

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
        Save the current state to persistent storage.

        This method creates a snapshot of the current state and saves it to
        either the database (if use_database is True) or a JSON file (if use_database is False).
        It creates the directory if it doesn't exist.

        Memory optimization:
        - Converts deques to lists before serialization
        - Limits the amount of data saved
        - Supports incremental updates to avoid saving unchanged data
        - Uses a more compact JSON representation

        Args:
            incremental: If True, only save data that has changed since the last save.
                         If False, save the entire state. Defaults to True.
        """
        snapshot = self._init_snapshot_metadata()

        if not incremental or not hasattr(self, "_last_saved_state"):
            snapshot.update(self._full_snapshot_fields())
        else:
            snapshot.update(self._compute_incremental_changes())

        self._persist_snapshot(snapshot, incremental)

    # --- Save helpers to reduce cyclomatic complexity ---
    def _init_snapshot_metadata(self) -> Dict[str, Any]:
        """Initialize snapshot metadata and bump internal version counter."""
        snapshot = {
            "timestamp": time.time(),
            "version": getattr(self, "_state_version", 0) + 1,
            "last_intensity": self.last_intensity,
            "last_dominance": self.last_dominance,
        }
        # Store the current version for future comparisons
        self._state_version = snapshot["version"]
        return snapshot

    def _full_snapshot_fields(self) -> Dict[str, Any]:
        """Return the full set of fields for a non-incremental save and update cache."""
        full = {
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
            "checkpoints": [copy.deepcopy(entry) for entry in self.checkpoints],
        }
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
        return full

    def _compute_incremental_changes(self) -> Dict[str, Any]:
        """Compute fields that changed since last save and update the cache."""
        changes: Dict[str, Any] = {}
        # Emotion
        if self.last_emotion != self._last_saved_state.get("emotion"):
            changes["emotion"] = self.last_emotion
            self._last_saved_state["emotion"] = copy.deepcopy(self.last_emotion) if self.last_emotion else None
        # Modifiers
        if self.applied_modifiers != self._last_saved_state.get("modifiers"):
            changes["modifiers"] = self.applied_modifiers
            self._last_saved_state["modifiers"] = copy.deepcopy(self.applied_modifiers)
        # Memories
        current_memories = list(self.memories)
        if (
            len(current_memories) != len(self._last_saved_state.get("memories", []))
            or {str(m) for m in current_memories} != {str(m) for m in self._last_saved_state.get("memories", [])}
        ):
            changes["memories"] = current_memories
            self._last_saved_state["memories"] = current_memories
        # Evolution
        if self.evolution_stats != self._last_saved_state.get("evolution"):
            changes["evolution"] = self.evolution_stats
            self._last_saved_state["evolution"] = copy.deepcopy(self.evolution_stats)
        # Explored zones
        current_zones = list(self.explored_zones)
        if set(current_zones) != set(self._last_saved_state.get("explored_zones", [])):
            changes["explored_zones"] = current_zones
            self._last_saved_state["explored_zones"] = current_zones
        # Discoveries
        current_discoveries = list(self.discoveries)
        if {str(d) for d in current_discoveries} != {str(d) for d in self._last_saved_state.get("discoveries", [])}:
            changes["discoveries"] = current_discoveries
            self._last_saved_state["discoveries"] = current_discoveries
        # Last zone
        if self.last_zone != self._last_saved_state.get("last_zone"):
            changes["last_zone"] = self.last_zone
            self._last_saved_state["last_zone"] = self.last_zone
        # Always include checkpoints
        changes["checkpoints"] = [copy.deepcopy(entry) for entry in self.checkpoints]
        return changes

    def _persist_snapshot(self, snapshot: Dict[str, Any], incremental: bool) -> None:
        """Persist the snapshot either to DB or to JSON file."""
        if self.use_database and self.db:
            state_id = self.db.save_state(snapshot)
            print(
                f"💾 Eterna state saved to database (ID: {state_id}, version {snapshot['version']}, {'incremental' if incremental else 'full'})"
            )
        else:
            save_json(self.save_path, snapshot, create_dirs=True, indent=None)
            print(
                f"💾 Eterna state saved to {self.save_path} (version {snapshot['version']}, {'incremental' if incremental else 'full'})"
            )

    def _load_snapshot(self) -> Optional[dict]:
        """Internal helper to load a snapshot from DB or JSON with identical behavior and prints."""
        snapshot = None
        # Try to load from database if enabled
        if self.use_database and self.db:
            snapshot = self.db.load_latest_state(lazy_load=self.use_lazy_loading)
            if snapshot:
                print(
                    f"📂 Loaded Eterna state from database (version {snapshot.get('version', 'unknown')}, "
                    f"{'lazy' if self.use_lazy_loading else 'eager'} loading)"
                )
                if self.use_lazy_loading:
                    # Store the lazy-loaded state for future access
                    self._lazy_state = snapshot
                    self._collections_accessed = set()
        # Fall back to JSON file if database load failed or is disabled
        if not snapshot:
            snapshot = load_json(self.save_path)
            if snapshot:
                print(
                    f"📂 Loaded Eterna state from {self.save_path} (version {snapshot.get('version', 'unknown')})"
                )
            else:
                print(f"⚠️ No saved state found at {self.save_path}")
                return None
        return snapshot

    def _apply_version_and_config(self, snapshot: dict) -> bool:
        """Apply version info and configuration limits from the snapshot. Returns is_incremental."""
        is_incremental = "version" in snapshot and "timestamp" in snapshot
        if is_incremental:
            self._state_version = snapshot.get("version", 0)
        # Update configuration parameters if present
        if "max_memories" in snapshot:
            self.max_memories = snapshot.get("max_memories", self.max_memories)
            self.max_discoveries = snapshot.get("max_discoveries", self.max_discoveries)
            self.max_explored_zones = snapshot.get("max_explored_zones", self.max_explored_zones)
            self.max_modifiers = snapshot.get("max_modifiers", self.max_modifiers)
            self.max_checkpoints = snapshot.get("max_checkpoints", self.max_checkpoints)
        return is_incremental

    def _apply_scalar_fields(self, snapshot: dict) -> None:
        if "emotion" in snapshot:
            self.last_emotion = snapshot.get("emotion")
        if "last_intensity" in snapshot:
            self.last_intensity = snapshot.get("last_intensity", 0.0)
        if "last_dominance" in snapshot:
            self.last_dominance = snapshot.get("last_dominance", 0.0)
        if "modifiers" in snapshot:
            self.applied_modifiers = snapshot.get("modifiers", {})

    def _setup_collections(self, snapshot: dict) -> None:
        # If using lazy loading with database, don't load collections now
        if self.use_lazy_loading and self.use_database and self.db and getattr(self, "_lazy_state", None):
            # Initialize empty collections with proper bounds
            self.memories = deque(maxlen=self.max_memories)
            self.discoveries = deque(maxlen=self.max_discoveries)
            self.explored_zones = deque(maxlen=self.max_explored_zones)
            self.modifiers = deque(maxlen=self.max_modifiers)
            self.checkpoints = deque(maxlen=self.max_checkpoints)
            # Clear indexes
            self._zone_index = set()
            self._memory_index = {}
            self._discovery_index = {}
            self._modifier_index = {}
            return
        # Eager loading of collections
        if "memories" in snapshot:
            self.memories = deque(snapshot.get("memories", []), maxlen=self.max_memories)
            self._rebuild_memory_index()
        if "discoveries" in snapshot:
            self.discoveries = deque(snapshot.get("discoveries", []), maxlen=self.max_discoveries)
            self._rebuild_discovery_index()
        if "explored_zones" in snapshot:
            self.explored_zones = deque(snapshot.get("explored_zones", []), maxlen=self.max_explored_zones)
            self._zone_index = set(self.explored_zones)
        if "checkpoints" in snapshot:
            raw_checkpoints = snapshot.get("checkpoints", [])
            normalized = [self._normalize_checkpoint_entry(entry) for entry in raw_checkpoints]
            self.checkpoints = deque(normalized, maxlen=self.max_checkpoints)

    def _apply_evolution_and_zone(self, snapshot: dict) -> None:
        if "evolution" in snapshot:
            self.evolution_stats = snapshot.get("evolution", self.evolution_stats)
            # Handle missing intellect
            self._prev_intellect = self.evolution_stats.get("intellect", 100)
        if "last_zone" in snapshot:
            self.last_zone = snapshot.get("last_zone")

    def _init_last_saved_state(self) -> None:
        lazy_mode = self.use_lazy_loading and self.use_database and self.db and getattr(self, "_lazy_state", None)
        self._last_saved_state = {
            "emotion": copy.deepcopy(self.last_emotion) if self.last_emotion else None,
            "modifiers": copy.deepcopy(self.applied_modifiers),
            "memories": [] if lazy_mode else list(getattr(self, "memories", [])),
            "evolution": copy.deepcopy(self.evolution_stats),
            "explored_zones": [] if lazy_mode else list(getattr(self, "explored_zones", [])),
            "discoveries": [] if lazy_mode else list(getattr(self, "discoveries", [])),
            "last_zone": self.last_zone,
            "checkpoints": [] if lazy_mode else [copy.deepcopy(entry) for entry in getattr(self, "checkpoints", [])],
        }

    def load(self):
        """
        Load the state from persistent storage.

        This method loads a previously saved state from either the database
        (if use_database is True) or a JSON file (if use_database is False).
        If no saved state is found, it prints a warning message.

        Memory optimization: 
        - Converts loaded lists to bounded deques
        - Respects the configured maximum sizes
        - Handles incremental state updates
        - Maintains a cache of the loaded state for future incremental saves
        - Supports lazy loading of collections for reduced memory usage
        """
        snapshot = self._load_snapshot()
        if not snapshot:
            return
        self._apply_version_and_config(snapshot)
        self._apply_scalar_fields(snapshot)
        self._setup_collections(snapshot)
        self._apply_evolution_and_zone(snapshot)
        self._init_last_saved_state()

    # --- quick‑and‑dirty identity drift metric -------------------------------
    # ------------------------------------------------------------------
    # Alignment‑Governor uses this to record saved checkpoints
    # ------------------------------------------------------------------
    def _checkpoint_created_at_from_path(self, path: str) -> Optional[str]:
        match = re.search(r"ckpt_(\d+)", path)
        if match:
            try:
                millis = int(match.group(1))
                return _iso_from_timestamp(millis / 1000)
            except Exception:
                return None
        return None

    def _normalize_checkpoint_entry(self, entry: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(entry, dict):
            record = copy.deepcopy(entry)
        else:
            record = {"path": str(entry)}

        # Normalize path and derive defaults
        raw_path = record.get("path")
        target_path = raw_path

        if isinstance(raw_path, str) and raw_path.startswith("ROLLED_BACK→"):
            target_path = raw_path.split("→", 1)[1]
            record.setdefault("kind", "rollback")
            record["target_path"] = target_path
        record["path"] = str(target_path) if target_path is not None else ""

        record.setdefault("label", Path(record["path"]).name or record["path"])
        record.setdefault("kind", "auto")

        created_at = record.get("created_at")
        if isinstance(created_at, str):
            parsed = _timestamp_from_iso(created_at)
            record["created_at"] = _iso_from_timestamp(parsed) if parsed else _utc_now_iso()
        else:
            inferred = self._checkpoint_created_at_from_path(record["path"])
            record["created_at"] = inferred or _utc_now_iso()

        if "size_bytes" not in record or record.get("size_bytes") is None:
            try:
                record["size_bytes"] = Path(record["path"]).stat().st_size
            except Exception:
                record["size_bytes"] = None

        if "state_version" not in record or record.get("state_version") is None:
            record["state_version"] = getattr(self, "_state_version", None)

        if "continuity" in record and record["continuity"] is not None:
            try:
                record["continuity"] = float(record["continuity"])
            except (TypeError, ValueError):
                record["continuity"] = None

        return record

    def register_checkpoint(self, checkpoint: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Append a new checkpoint path to the internal deque so the UI and
        governor rollback logic can query available snapshots.

        Memory optimization: Uses a bounded deque that automatically removes
        the oldest checkpoints when the maximum size is reached.
        """
        record = self._normalize_checkpoint_entry(checkpoint)
        self.checkpoints.append(record)
        self._last_saved_state.setdefault("checkpoints", [])
        self._last_saved_state["checkpoints"] = [copy.deepcopy(entry) for entry in self.checkpoints]
        return record

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
            self._prev_intellect = self.evolution_stats.get("intellect", 100)  # Default to 100 if not present
            return 1.0
        cur = self.evolution_stats.get("intellect", 100)  # Default to 100 if not present
        prev = self._prev_intellect
        self._prev_intellect = cur
        return 1.0 - abs(cur - prev) / max(cur, prev, 1)

    def report(self):
        """
        Print a detailed report of the current state.

        This method prints information about the current emotion, evolution stats,
        explored zones, applied modifiers, discoveries, and memories.
        """
        # Ensure all collections are loaded if using lazy loading
        self._ensure_collection_loaded("memories")
        self._ensure_collection_loaded("discoveries")
        self._ensure_collection_loaded("explored_zones")
        self._ensure_collection_loaded("modifiers")
        self._ensure_collection_loaded("checkpoints")

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
        self.register_checkpoint({
            "path": str(path),
            "kind": "rollback",
            "target_path": str(path),
            "created_at": _utc_now_iso(),
        })
        # optional: reset any per‑run counters
        if hasattr(self, "current_cycle"):
            self.current_cycle = 0

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        Get a list of all registered checkpoints with metadata.

        Returns:
            List[Dict[str, Any]]: Normalized checkpoint records sorted by insertion order.
        """
        self._ensure_collection_loaded("checkpoints")
        return [copy.deepcopy(entry) for entry in self.checkpoints]

    def backup_state(self, backup_path=None) -> Optional[str]:
        """
        Create a backup of the current state.

        If using the database, this creates a backup of the database file.
        If using JSON files, this creates a copy of the state snapshot file.

        Args:
            backup_path: Path where the backup will be saved. If None, a default path
                        will be generated based on the current timestamp.

        Returns:
            Optional[str]: The path to the backup file, or None if the backup failed.
        """
        # Save the current state first to ensure it's up to date
        self.save(incremental=False)

        if self.use_database and self.db:
            # Use the database backup functionality
            return self.db.backup_state(backup_path)
        else:
            # Create a backup of the JSON file
            if backup_path is None:
                # Generate a default backup path with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = os.path.join(os.path.dirname(self.save_path), "backups")
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, f"eternia_state_{timestamp}.json")

            # Ensure the backup directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)

            try:
                # Copy the state snapshot file to the backup path
                import shutil
                shutil.copy2(self.save_path, backup_path)
                print(f"✅ State backup created at {backup_path}")
                return backup_path
            except Exception as e:
                print(f"❌ State backup failed: {e}")
                return None

    def restore_from_backup(self, backup_path) -> bool:
        """
        Restore the state from a backup.

        If using the database, this restores the database from a backup file.
        If using JSON files, this restores the state snapshot from a backup file.

        Args:
            backup_path: Path to the backup file to restore from.

        Returns:
            bool: True if the restore was successful, False otherwise.
        """
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False

        if self.use_database and self.db:
            # Use the database restore functionality
            return self.db.restore_from_backup(backup_path)
        else:
            # Create a backup of the current state snapshot before restoring
            current_backup = None
            if os.path.exists(self.save_path):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                current_backup = f"{self.save_path}.{timestamp}.bak"
                try:
                    import shutil
                    shutil.copy2(self.save_path, current_backup)
                    print(f"✅ Created backup of current state at {current_backup}")
                except Exception as e:
                    print(f"⚠️ Failed to create backup of current state: {e}")

            try:
                # Copy the backup file to the state snapshot path
                import shutil
                shutil.copy2(backup_path, self.save_path)

                # Load the restored state
                self.load()

                print(f"✅ State restored from {backup_path}")
                return True
            except Exception as e:
                print(f"❌ State restore failed: {e}")

                # Try to restore from the backup of the current state
                if current_backup and os.path.exists(current_backup):
                    try:
                        shutil.copy2(current_backup, self.save_path)
                        self.load()  # Reload the state
                        print(f"✅ Reverted to previous state from {current_backup}")
                    except Exception as e2:
                        print(f"❌ Failed to revert to previous state: {e2}")

                return False

    def list_backups(self) -> List[str]:
        """
        List all available state backups.

        Returns:
            List[str]: A list of backup file paths.
        """
        if self.use_database and self.db:
            # Use the database list_backups functionality
            return self.db.list_backups()
        else:
            # List JSON backups
            backup_dir = os.path.join(os.path.dirname(self.save_path), "backups")
            if not os.path.exists(backup_dir):
                return []

            backups = []
            for file in os.listdir(backup_dir):
                if file.startswith("eternia_state_") and file.endswith(".json"):
                    backups.append(os.path.join(backup_dir, file))

            # Sort by modification time (newest first)
            backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return backups

    def export_to_json(self, output_path=None) -> Optional[str]:
        """
        Export the current state to a JSON file.

        This is useful for data migration between different storage formats
        or for creating human-readable backups.

        Args:
            output_path: Path where the JSON file will be saved. If None, a default path
                        will be generated based on the current timestamp.

        Returns:
            Optional[str]: The path to the JSON file, or None if the export failed.
        """
        if self.use_database and self.db:
            # Use the database export functionality
            return self.db.export_to_json(output_path)
        else:
            # For JSON-based storage, create a copy of the state file
            if output_path is None:
                # Generate a default output path with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                export_dir = os.path.join(os.path.dirname(self.save_path), "exports")
                os.makedirs(export_dir, exist_ok=True)
                output_path = os.path.join(export_dir, f"eternia_export_{timestamp}.json")

            # Ensure the export directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            try:
                # Save the current state first to ensure it's up to date
                self.save(incremental=False)

                # Read the state file
                snapshot = load_json(self.save_path)

                if not snapshot:
                    print("❌ No state data to export")
                    return None

                # Add metadata
                export_data = {
                    "export_timestamp": time.time(),
                    "schema_version": 1,  # Use version 1 for JSON exports
                    "state": snapshot
                }

                # Write to JSON file with indentation for readability
                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2)

                print(f"✅ State exported to {output_path}")
                return output_path
            except Exception as e:
                print(f"❌ State export failed: {e}")
                return None

    def import_from_json(self, input_path) -> bool:
        """
        Import state data from a JSON file.

        This is useful for data migration between different storage formats.

        Args:
            input_path: Path to the JSON file to import.

        Returns:
            bool: True if the import was successful, False otherwise.
        """
        if not os.path.exists(input_path):
            print(f"❌ Import file not found: {input_path}")
            return False

        try:
            # Read the JSON file
            with open(input_path, 'r') as f:
                import_data = json.load(f)

            # Get the state data
            state_data = import_data.get("state")
            if not state_data:
                print("❌ No state data found in import file")
                return False

            if self.use_database and self.db:
                # Use the database import functionality
                return self.db.import_from_json(input_path)
            else:
                # For JSON-based storage, save the state data to the state file
                save_json(self.save_path, state_data, create_dirs=True)

                # Reload the state
                self.load()

                print(f"✅ Data imported from {input_path}")
                return True
        except Exception as e:
            print(f"❌ Data import failed: {e}")
            return False

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
