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

class EmotionalSafetyModule:
    def __init__(self):
        self.ems = EmotionalMonitoringSystem()
        self.ptis = TherapeuticInterventionSystem()

    def monitor_and_manage_emotions(self):
        if self.ems.detect_negative_emotions():
            return self.provide_therapy()
        print("✅ Emotional state stable.")
        return "Stable"

    def provide_therapy(self):
        intervention = self.ptis.offer_intervention()
        user_accepts = True  # Simulate user's manual control
        if user_accepts:
            print(f"🧘 User accepted therapy: {intervention}. Therapy initiated.")
            self.ems.update_emotional_state("calm", stress_level=2)
            return "Therapy Successful"
        else:
            print("🚧 User declined therapy. Offering alternate options.")
            return "Therapy Declined"