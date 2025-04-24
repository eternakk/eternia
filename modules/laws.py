from modules.law_parser import load_laws

class EternaLaw:
    def __init__(self, name, description, active=True):
        self.name = name
        self.description = description
        self.active = active

class PhilosophicalLawbook:
    def __init__(self):
        # Load all laws from TOML files in the `laws/` directory
        toml_laws = load_laws("laws")
        self.laws = [
            EternaLaw(
                name=law.name,
                description=law.description,
                active=law.enabled
            )
            for law in toml_laws.values()
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