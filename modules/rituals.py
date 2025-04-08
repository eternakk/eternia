class Ritual:
    def __init__(self, name, purpose, steps, symbolic_elements):
        self.name = name
        self.purpose = purpose
        self.steps = steps  # List of symbolic steps (visual, emotional, narrative)
        self.symbolic_elements = symbolic_elements  # Fire, water, mirrors, etc.

    def perform(self):
        print(f"🔮 Performing Ritual: {self.name}")
        print(f"📘 Purpose: {self.purpose}")
        for step in self.steps:
            print(f"➡️ {step}")
        print(f"🧿 Elements used: {', '.join(self.symbolic_elements)}")

class RitualSystem:
    def __init__(self):
        self.rituals = {}

    def register(self, ritual: Ritual):
        self.rituals[ritual.name.strip().lower()] = ritual

    def perform(self, name):
        ritual = self.rituals.get(name.strip().lower())
        if ritual:
            ritual.perform()
        else:
            print(f"❌ Ritual '{name}' not found.")