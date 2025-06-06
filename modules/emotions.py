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
                "modifiers": ["Dimensional Expansion", "Cosmic Awareness"]
            },
            "love": {
                "ritual": "Circle of Threads",
                "zone_effect": "blossoming trees",
                "color_filter": "warm rose",
                "music": "gentle strings",
                "modifiers": ["Harmonic Resonance", "Connection Weave"]
            },
            "joy": {
                "ritual": "Festival of Light",
                "zone_effect": "sunlight burst",
                "color_filter": "sunny yellow",
                "music": "lively folk",
                "modifiers": ["Luminous Cascade", "Vibrant Pulse"]
            },
            "anger": {
                "ritual": "Ash Garden Rebirth",
                "zone_effect": "cracked ground",
                "color_filter": "deep crimson",
                "music": "tribal percussion",
                "modifiers": ["Volcanic Surge", "Transformative Heat"]
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
        from modules.logging_config import get_logger

        logger = get_logger("emotions")

        # Log the emotion change
        previous_emotion = self.current_emotion
        previous_desc = previous_emotion.describe() if previous_emotion else "None"
        logger.info(f"🔄 Emotion changing from {previous_desc} to {emotion.describe()}")

        self.current_emotion = emotion
        if self.eterna:
            self.eterna.log_emotion(emotion)  # ✅ Logs emotional state to the tracker
        logger.info(f"🧠 Processing emotion: {emotion.describe()}")

        mapping = self.symbolic_map.get_mapping(emotion.name)

        if mapping:
            logger.info(f"🎭 Applying symbolic world effects for emotion: {emotion.name}")
            logger.info(f" - Ritual: {mapping['ritual']}")
            logger.info(f" - Zone Effect: {mapping['zone_effect']}")
            logger.info(f" - Color Filter: {mapping['color_filter']}")
            logger.info(f" - Music: {mapping['music']}")

            if self.eterna:
                self.eterna.rituals.perform(mapping['ritual'])

                # 🌌 Apply symbolic modifiers to linked zones
                linked_zones = self.eterna.exploration.registry.get_zones_by_emotion(emotion.name)
                logger.info(f"🔗 Found {len(linked_zones)} zones linked to emotion '{emotion.name}'")

                # Debug: Print all zones in the registry
                all_zones = self.eterna.exploration.registry.zones
                logger.info(f"🔍 All zones in registry: {[z.name for z in all_zones]}")
                logger.info(f"🔍 All emotion tags in registry: {[z.emotion_tag for z in all_zones]}")

                # Debug: Print the emotion name being searched for
                logger.info(f"🔍 Searching for zones with emotion tag: '{emotion.name}'")

                for mod_name in mapping.get("modifiers", []):
                    for zone in linked_zones:
                        logger.info(f"🔄 Applying modifier '{mod_name}' to zone '{zone.name}' due to emotion '{emotion.name}'")
                        zone.add_modifier(mod_name)

        elif emotion.intensity >= 8 and emotion.direction == "locked":
            logger.warning("⚠️ Emotion is blocked and becoming volatile.")
            if self.eterna:
                logger.info("🔄 Performing 'Chamber of Waters' ritual due to blocked emotion")
                self.eterna.rituals.perform("Chamber of Waters")

        elif emotion.direction == "flowing":
            logger.info("🌊 Emotion is integrating. You may evolve or access sensitive memories.")

        elif emotion.name == "awe":
            logger.info("✨ Awe detected. You gain access to high-dimensional zones.")

        elif emotion.name == "grief" and emotion.intensity > 7:
            logger.info("🖤 Deep grief detected. Initiating healing path.")
            if self.eterna:
                logger.info("🔄 Performing 'Chamber of Waters' ritual due to deep grief")
                self.eterna.rituals.perform("Chamber of Waters")

        else:
            logger.info("🌀 Emotion registered. No intervention required.")
