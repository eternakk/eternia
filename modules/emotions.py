class EmotionalState:
    def __init__(self, name, intensity, direction):
        self.name = name  # e.g., "grief", "awe", "shame"
        self.intensity = intensity  # 0–10
        self.direction = direction  # "inward", "outward", "locked", "flowing"

    def describe(self):
        return f"{self.name.capitalize()} (Intensity: {self.intensity}, Direction: {self.direction})"

class EmotionalCircuitSystem:
    def __init__(self, eterna_interface=None):  # Add this parameter
        self.current_emotion = None
        self.eterna = eterna_interface  # Store the Eterna interface for ritual access

    def process_emotion(self, emotion: EmotionalState):
        self.current_emotion = emotion
        print(f"🧠 Processing emotion: {emotion.describe()}")

        if emotion.intensity >= 8 and emotion.direction == "locked":
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