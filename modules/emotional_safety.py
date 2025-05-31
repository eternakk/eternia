from modules.emotions import EmotionalState as CircuitEmotion, EmotionalCircuitSystem
from modules.interfaces import EmotionalInterface


class EmotionalState:
    def __init__(self, mood="calm", stress_level=0, trauma_triggered=False):
        self.mood = mood
        self.stress_level = stress_level  # 0 to 10 scale
        self.trauma_triggered = trauma_triggered

class EmotionalMonitoringSystem:
    def __init__(self):
        self.state = EmotionalState()

    def detect_negative_emotions(self):
        if self.state.stress_level >= 7 or self.state.trauma_triggered:
            print("⚠️ Negative emotion or trauma detected.")
            return True
        return False

    def update_emotional_state(self, mood, stress_level, trauma_triggered=False):
        self.state.mood = mood
        self.state.stress_level = stress_level
        self.state.trauma_triggered = trauma_triggered

class TherapeuticInterventionSystem:
    def __init__(self):
        self.interventions = [
            "Guided emotional release meditation",
            "Memory refinement therapy",
            "Calming immersive sensory experience"
        ]

    def offer_intervention(self):
        intervention = self.interventions[0]  # Rotate or choose based on emotional context
        print(f"🌈 Offered therapeutic intervention: {intervention}")
        return intervention

class EmotionalSafetyModule(EmotionalInterface):
    def __init__(self, eterna_interface=None):
        self.ems = EmotionalMonitoringSystem()
        self.ptis = TherapeuticInterventionSystem()
        self.circuits = EmotionalCircuitSystem(eterna_interface)

    def initialize(self) -> None:
        """Initialize the emotional safety module."""
        pass

    def shutdown(self) -> None:
        """Perform any cleanup operations when shutting down."""
        pass

    def monitor_and_manage_emotions(self) -> bool:
        """
        Monitor and manage emotions for safety.

        Returns:
            bool: True if emotional state is safe, False otherwise
        """
        if self.ems.detect_negative_emotions():
            # Map internal emotional state to new emotion circuit model
            mapped_emotion = CircuitEmotion(
                name=self.ems.state.mood,
                intensity=self.ems.state.stress_level,
                direction="locked" if self.ems.state.trauma_triggered else "flowing"
            )
            self.circuits.process_emotion(mapped_emotion)
            print("Emotion Processed via Circuit")
            return False  # Emotional state is not safe

        print("✅ Emotional state stable.")
        return True  # Emotional state is safe

    def update_emotional_state(self, mood: str, stress_level: int, trauma_triggered: bool = False) -> None:
        """
        Update the emotional state.

        Args:
            mood: The current mood
            stress_level: The current stress level
            trauma_triggered: Whether trauma has been triggered
        """
        self.ems.update_emotional_state(mood, stress_level, trauma_triggered)
