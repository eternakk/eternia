import json
import os

class EternaStateTracker:
    def __init__(self, save_path="logs/state_snapshot.json"):
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

    def log_emotional_impact(self, emotion_name, score):
        if not hasattr(self, "emotional_log"):
            self.emotional_log = []

        self.emotional_log.append((emotion_name, round(score, 2)))

        print(f"📝 Logged emotional impact: {emotion_name} → {round(score, 2)}")

    def mark_zone(self, zone_name):
        self.last_zone = zone_name
        if zone_name not in self.explored_zones:
            self.explored_zones.append(zone_name)

    def track_modifier(self, zone_name, modifier):
        self.modifiers.append((zone_name, modifier))

    def track_discovery(self, discovery):
        self.discoveries.append(discovery)

    def update_emotion(self, emotion):
        self.last_emotion = {
            "name": emotion.name,
            "intensity": emotion.intensity,
            "direction": emotion.direction
        }

    def add_modifier(self, zone, modifier):
        self.applied_modifiers.setdefault(zone, []).append(modifier)

    def add_memory(self, memory):
        self.memories.append(memory)

    def record_discovery(self, discovery):
        self.discoveries.append(discovery)

    def mark_zone_explored(self, zone_name):
        if zone_name not in self.explored_zones:
            self.explored_zones.append(zone_name)

    def update_evolution(self, intellect, senses):
        self.evolution_stats["intellect"] = intellect
        self.evolution_stats["senses"] = senses

    def save(self):
        snapshot = {
            "emotion": self.last_emotion,
            "modifiers": self.applied_modifiers,
            "memories": self.memories,
            "evolution": self.evolution_stats,
            "explored_zones": self.explored_zones,
            "discoveries": self.discoveries,
        }
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w") as f:
            json.dump(snapshot, f, indent=2)
        print(f"💾 Eterna state saved to {self.save_path}")

    def load(self):
        if os.path.exists(self.save_path):
            with open(self.save_path, "r") as f:
                snapshot = json.load(f)
                self.last_emotion = snapshot.get("emotion")
                self.applied_modifiers = snapshot.get("modifiers", {})
                self.memories = snapshot.get("memories", [])
                self.evolution_stats = snapshot.get("evolution", self.evolution_stats)
                self.explored_zones = snapshot.get("explored_zones", [])
                self.discoveries = snapshot.get("discoveries", [])
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
        # TODO: replace with real embedding similarity
        if not hasattr(self, "_prev_intellect"):
            self._prev_intellect = self.evolution_stats["intellect"]
            return 1.0
        cur = self.evolution_stats["intellect"]
        prev = self._prev_intellect
        self._prev_intellect = cur
        return 1.0 - abs(cur - prev) / max(cur, prev, 1)

    def report(self):
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
            print(f"  • {mem['description']} (Clarity: {mem['clarity']}, Emotion: {mem['emotional_quality']})")
        print("Discoveries:")
        for disc in self.discoveries:
            print(f"  • {disc}")

    def last_zone_explored(self):
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
        """
        self.checkpoints.append(f"ROLLED_BACK→{path}")
        # optional: reset any per‑run counters
        if hasattr(self, "current_cycle"):
            self.current_cycle = 0
