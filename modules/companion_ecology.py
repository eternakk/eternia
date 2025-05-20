# 📦 companion_ecology.py — Populate Eterna with authentic companions

import random

DIALOGUE_TONES = [
    "neutral",  # 0
    "comforting",  # 1
    "curious",  # 2
    "playful",  # 3
    "serious",  # 4
]


class BaseCompanion:
    def __init__(self, name, role="neutral", memory_seed=None):
        self.name = name
        self.role = role  # friend, echo, guide, villager, mythic, etc.
        self.memory_seed = memory_seed or ""
        self.affinity = 50  # baseline trust/love toward user
        self.routine = []

    def apply_tone(companion, tone_id: int):
        tone = DIALOGUE_TONES[tone_id]
        companion.set_tone(tone)  # implement in your agent class

    def interact(self):
        print(f"🤝 You interact with {self.name} ({self.role}).")
        print(f"🧠 Memory seed: {self.memory_seed or 'N/A'}")
        self.react()

    def react(self):
        print(f"{self.name} responds with curiosity and presence.")


class MemoryEcho(BaseCompanion):
    def __init__(self, name, memory_seed):
        super().__init__(name, role="echo", memory_seed=memory_seed)
        self.evolves = False  # echoes do not change drastically

    def react(self):
        print(f"🕰️ {self.name} reflects a moment from your past...")


class LocalAgent(BaseCompanion):
    def __init__(self, name, job="farmer"):
        super().__init__(name, role="villager")
        self.job = job
        self.routine = ["wake", job, "rest", "reflect"]

    def react(self):
        print(f"🌾 {self.name} shares something from their daily life as a {self.job}.")


class SymbolicBeing(BaseCompanion):
    def __init__(self, name, archetype="guide"):
        super().__init__(name, role="mythic")
        self.archetype = archetype

    def react(self):
        print(
            f"🦄 {self.name} (a {self.archetype}) whispers a truth: '{self._generate_wisdom()}'"
        )

    def _generate_wisdom(self):
        sayings = [
            "To shape time, one must hold stillness.",
            "The horizon listens more than the mountain speaks.",
            "Every echo longs to return to its source.",
        ]
        return random.choice(sayings)


class CompanionManager:
    def __init__(self):
        self.companions = []
        self.active_index = 0  # Default to the first companion (if any)

    def spawn(self, companion):
        self.companions.append(companion)
        print(f"✨ Companion '{companion.name}' ({companion.role}) added to the world.")

    def get_current(self):
        if not self.companions:
            return None
        return self.companions[self.active_index]

    def set_active(self, idx):
        if 0 <= idx < len(self.companions):
            self.active_index = idx
        else:
            print("Invalid companion index.")

    def list_all(self):
        if not self.companions:
            print("🫧 No companions yet.")
        for c in self.companions:
            print(f" - {c.name} ({c.role})")

    def interact_with(self, name):
        match = next(
            (c for c in self.companions if c.name.lower() == name.lower()), None
        )
        if match:
            match.interact()
        else:
            print(f"❌ No companion named '{name}' found.")

    def list_companions(self):
        if not self.companions:
            print("👥 No companions currently in the world.")
        else:
            print("👥 Companions in the world:")
            for c in self.companions:
                print(f" - {c.name} ({c.role})")
