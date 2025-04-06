import random


class ExplorationZone:
    def __init__(self, name, origin, complexity_level):
        self.name = name
        self.origin = origin  # 'user', 'AGI', 'shared'
        self.complexity_level = complexity_level
        self.explored = False

class ExplorationRegistry:
    def __init__(self):
        self.zones = []

    def register_zone(self, zone):
        self.zones.append(zone)
        print(f"🌍 New zone registered: {zone.name} ({zone.origin})")

    def available_zones(self, user_intellect):
        return [z for z in self.zones if not z.explored and z.complexity_level <= user_intellect + 15]

class VirgilGuide:
    def guide_user(self, zone, physics_profile=None):
        print(f"🧭 Virgil: 'Entering {zone.name} — a {zone.origin} zone.'")
        if physics_profile:
            print(f"📐 Virgil: 'Expect {physics_profile.dimensions} dimensions, gravity {physics_profile.gravity}, and {physics_profile.energy_behavior} energy.'")

class ExplorationModule:
    def __init__(self, user_intellect,  eterna_interface = None):
        self.registry = ExplorationRegistry()
        self.virgil = VirgilGuide()
        self.user_intellect = user_intellect
        self.eterna = eterna_interface  # Add this

    def explore_random_zone(self, return_zone=False):
        available = self.registry.available_zones(self.user_intellect)
        if not available:
            print("⚠️ No suitable zones to explore. Try evolving first.")
            return None

        zone = random.choice(available)

        # 🧠 Get physics profile for Virgil to reference
        physics_profile = self.eterna.physics_registry.get_profile(zone.name) if hasattr(self, 'eterna') else None

        # 🧙 Virgil provides guidance with physics context
        self.virgil.guide_user(zone, physics_profile)

        zone.explored = True
        print(f"✨ You explored: {zone.name} — Complexity: {zone.complexity_level}")
        return zone if return_zone else None

    def mark_zone_as_explored(self, zone_name):
        for zone in self.registry.zones:
            if zone.name == zone_name:
                zone.explored = True
                print(f"✅ Zone '{zone_name}' marked as explored.")
                return