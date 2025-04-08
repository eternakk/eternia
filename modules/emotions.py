class EmotionalState:
    def __init__(self, name, intensity, direction):
        self.name = name  # e.g., "grief", "awe", "shame"
        self.intensity = intensity  # 0–10
        self.direction = direction  # "inward", "outward", "locked", "flowing"

    def describe(self):
        return f"{self.name.capitalize()} (Intensity: {self.intensity}, Direction: {self.direction})"


class SymbolicEmotionMap:
    def __init__(self):
        self.mappings = {
            "grief": {
                "ritual": "Chamber of Waters",
                "zone_effect": "foggy",
                "color_filter": "muted blues",
                "music": "slow cello ambient",
                "modifiers": ["Shroud of Memory"]
            },
            "awe": {
                "ritual": "Starlight Spiral",
                "zone_effect": "dimensional bloom",
                "color_filter": "vivid gold and violet",
                "music": "choral reverb",
                "modifiers": []
            },
            "love": {
                "ritual": "Circle of Threads",
                "zone_effect": "blossoming trees",
                "color_filter": "warm rose",
                "music": "gentle strings",
                "modifiers": []
            },
            "joy": {
                "ritual": "Festival of Light",
                "zone_effect": "sunlight burst",
                "color_filter": "sunny yellow",
                "music": "lively folk",
                "modifiers": []
            },
            "anger": {
                "ritual": "Ash Garden Rebirth",
                "zone_effect": "cracked ground",
                "color_filter": "deep crimson",
                "music": "tribal percussion",
                "modifiers": []
            }
        }

    def get_mapping(self, emotion_name):
        return self.mappings.get(emotion_name.lower(), {})


class EmotionalCircuitSystem:
    def __init__(self, eterna_interface=None):
        self.current_emotion = None
        self.eterna = eterna_interface  # Store the Eterna interface for ritual access
        self.symbolic_map = SymbolicEmotionMap()

    def process_emotion(self, emotion: EmotionalState):
        self.current_emotion = emotion
        print(f"🧠 Processing emotion: {emotion.describe()}")

        mapping = self.symbolic_map.get_mapping(emotion.name)

        if mapping:
            print(f"🎭 Applying symbolic world effects:")
            print(f" - Ritual: {mapping['ritual']}")
            print(f" - Zone Effect: {mapping['zone_effect']}")
            print(f" - Color Filter: {mapping['color_filter']}")
            print(f" - Music: {mapping['music']}")
            if self.eterna:
                self.eterna.rituals.perform(mapping['ritual'])

                # 🌌 Apply symbolic modifiers to linked zones
                linked_zones = self.eterna.exploration.registry.get_zones_by_emotion(emotion.name)
                for mod_name in mapping.get("modifiers", []):
                    for zone in linked_zones:
                        zone.add_modifier(mod_name)

        elif emotion.intensity >= 8 and emotion.direction == "locked":
            print("⚠️ Emotion is blocked and becoming volatile.")
            if self.eterna:
                self.eterna.rituals.perform("Chamber of Waters")

        elif emotion.direction == "flowing":
            print("🌊 Emotion is integrating. You may evolve or access sensitive memories.")

        elif emotion.name == "awe":
            print("✨ Awe detected. You gain access to high-dimensional zones.")

        elif emotion.name == "grief" and emotion.intensity > 7:
            print("🖤 Deep grief detected. Initiating healing path.")
            if self.eterna:
                self.eterna.rituals.perform("Chamber of Waters")

        else:
            print("🌀 Emotion registered. No intervention required.")
