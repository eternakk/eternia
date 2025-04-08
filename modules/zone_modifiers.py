# 🌌 zone_modifiers.py

class SymbolicModifier:
    def __init__(self, name, trigger_emotion, effects):
        self.name = name
        self.trigger_emotion = trigger_emotion  # e.g., "grief", "awe"
        self.effects = effects  # List of symbolic changes (visuals, music, interactions)

    def describe(self):
        print(f"🔮 Modifier: {self.name}")
        print(f"🎭 Trigger: {self.trigger_emotion}")
        print("✨ Effects:")
        for effect in self.effects:
            print(f" - {effect}")


class SymbolicModifierRegistry:
    def __init__(self):
        self.modifiers = {}

    def register_modifier(self, modifier: SymbolicModifier):
        self.modifiers[modifier.name] = modifier

    def get_by_emotion(self, emotion_name):
        return [m for m in self.modifiers.values() if m.trigger_emotion == emotion_name]

    def list_all(self):
        for mod in self.modifiers.values():
            mod.describe()


# Optional link to ExplorationZone:
class ZoneWithModifiers:
    def __init__(self, name, origin, complexity):
        self.name = name
        self.origin = origin
        self.complexity = complexity
        self.explored = False
        self.modifiers = []  # Names of symbolic modifiers tied to this zone

    def add_modifier(self, modifier_name):
        if modifier_name not in self.modifiers:
            self.modifiers.append(modifier_name)
            print(f"🌗 Zone '{self.name}' was symbolically modified with '{modifier_name}'.")

    def show_modifiers(self):
        if self.modifiers:
            print(f"🎨 Symbolic Layers for '{self.name}':")
            for m in self.modifiers:
                print(f" - {m}")
        else:
            print(f"➖ No symbolic modifiers in '{self.name}'.")
