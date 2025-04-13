class SensoryProfile:
    def __init__(self, visual_range="normal", hearing="normal", balance="standard"):
        self.visual_range = visual_range
        self.hearing = hearing
        self.balance = balance

    def adapt_to_physics(self, physics_profile):
        print("🧬 Adapting sensory systems to new physics...")
        if physics_profile.dimensions > 3:
            self.visual_range = "multiplanar"
        if physics_profile.gravity < 5:
            self.balance = "stabilized"
        if physics_profile.energy_behavior == "thought-sensitive":
            self.hearing = "resonant"
        print(f"👁 Visual: {self.visual_range}, 🎧 Hearing: {self.hearing}, ⚖️ Balance: {self.balance}")

    def score(self):
        score_map = {"normal": 100, "multiplanar": 120, "resonant": 110, "stabilized": 105, "standard": 100}
        return (score_map.get(self.visual_range, 100) +
                score_map.get(self.hearing, 100) +
                score_map.get(self.balance, 100)) // 3