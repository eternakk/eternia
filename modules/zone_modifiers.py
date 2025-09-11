# 🌌 zone_modifiers.py
from __future__ import annotations
from typing import Dict, List


class SymbolicModifier:
    def __init__(self, name: str, trigger_emotion: str, effects: List[str]) -> None:
        self.name: str = name
        self.trigger_emotion: str = trigger_emotion  # e.g., "grief", "awe"
        self.effects: List[str] = effects  # List of symbolic changes (visuals, music, interactions)

    def describe(self) -> None:
        print(f"🔮 Modifier: {self.name}")
        print(f"🎭 Trigger: {self.trigger_emotion}")
        print("✨ Effects:")
        for effect in self.effects:
            print(f" - {effect}")


class SymbolicModifierRegistry:
    def __init__(self) -> None:
        self.modifiers: Dict[str, SymbolicModifier] = {}

    def register_modifier(self, modifier: SymbolicModifier) -> None:
        self.modifiers[modifier.name] = modifier

    def get_by_emotion(self, emotion_name: str) -> List[SymbolicModifier]:
        return [m for m in self.modifiers.values() if m.trigger_emotion == emotion_name]

    def list_all(self) -> None:
        for mod in self.modifiers.values():
            mod.describe()


# Optional link to ExplorationZone:
class ZoneWithModifiers:
    def __init__(self, name: str, origin: str, complexity: int) -> None:
        self.name: str = name
        self.origin: str = origin
        self.complexity: int = complexity
        self.explored: bool = False
        self.modifiers: List[str] = []  # Names of symbolic modifiers tied to this zone

    def add_modifier(self, modifier_name: str) -> None:
        if modifier_name not in self.modifiers:
            self.modifiers.append(modifier_name)
            print(f"🌗 Zone '{self.name}' was symbolically modified with '{modifier_name}'.")

    def show_modifiers(self) -> None:
        if self.modifiers:
            print(f"🎨 Symbolic Layers for '{self.name}':")
            for m in self.modifiers:
                print(f" - {m}")
        else:
            print(f"➖ No symbolic modifiers in '{self.name}'.")
