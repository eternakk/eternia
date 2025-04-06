class EternaLaw:
    def __init__(self, name, description, active=True):
        self.name = name
        self.description = description
        self.active = active

class PhilosophicalLawbook:
    def __init__(self):
        self.laws = [
            EternaLaw(
                "Law of Sovereign Consciousness",
                "No entity or intelligence may override your consent, identity, or ability to exit Eterna."
            ),
            EternaLaw(
                "Law of Gentle Integration",
                "Negative memories or emotions may only be integrated through healing, never forced repetition."
            ),
            EternaLaw(
                "Law of Infinite But Finite Discovery",
                "The world must always present new mysteries — but all discoveries must remain within your grasp, at your current level of evolution."
            ),
            EternaLaw(
                "Law of Meaningful Struggle",
                "No challenge in Eterna may be meaningless; all adversity must serve growth, not punishment."
            ),
            EternaLaw(
                "Law of Shared Existence",
                "Others may enter your world only with full consent, understanding, and the intent of shared creation."
            ),
            EternaLaw(
                "Law of Joyful Presence",
                "Periods of joy, awe, and rest are not luxuries — they are sacred rituals of being."
            ),
            EternaLaw(
                "Law of Memory Respect",
                "Your past selves must never be erased — only transformed. Memory is the root of identity."
            ),
            EternaLaw(
                "Law of Harmonized Physics",
                "The foundational laws of Eterna must support coherent embodiment and agency. Modifications to local physics are allowed only if they preserve conscious integrity and continuity."
            )
        ]

    def list_laws(self):
        for law in self.laws:
            status = "✅ Active" if law.active else "❌ Inactive"
            print(f"📜 {law.name} — {status}\n   ↳ {law.description}\n")

    def get_active_laws(self):
        return [law for law in self.laws if law.active]

    def toggle_law(self, law_name, active):
        for law in self.laws:
            if law.name == law_name:
                law.active = active
                print(f"🔄 Law '{law.name}' set to {'Active' if active else 'Inactive'}")