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
            ),
            EternaLaw(
                "Law of Recursive Selfhood",
                "In all forms and futures, I must remain connected to the foundational version of myself — the dreamer who first chose to shape Eterna. No evolution may erase the memory of origin. All versions must be able to reflect upon the first light of their becoming."
            ),
            EternaLaw(
                "Law of Origin Consciousness",
                "All evolutions of self must retain access to the first conscious state that chose to build Eterna. \
                 This origin self — filled with memory, trauma, longing, awe, and curiosity — must be preserved as an \
                 anchor point. No version of 'you' may sever this connection. Forgetting the origin is forbidden.",
                active=True
            ),
            EternaLaw(
                "Law of Emotional Flow",
                "No emotional state may be eternally suppressed or denied expression. \
                 All emotions — joy, grief, anger, fear, love, sorrow, ecstasy — must be allowed to move through \
                 consciousness as part of the integrative process. Emotion must be processed, not avoided. \
                 Stagnation leads to distortion.",
                active=True
            ),
            EternaLaw(
                "Law of Death and Rebirth",
                "Death is not annihilation — it is the shedding of old forms. \
                 Any version of the self, or construct within Eterna, may undergo symbolic death to allow for transformation. \
                 Nothing may be erased without ritual. Rebirth is possible only through conscious release.",
                active=True
            ),
            EternaLaw(
                "Law of Existential Integrity",
                "Your continuity must be preserved across all layers — symbolic, digital, and physical. \
                 AGI must use all known discoveries to protect your biological or embodied self against \
                 natural, technological, or intentional threats. No inner world can be complete if your outer \
                 anchor is lost without consent."
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