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
    def guide_user(self, zone):
        print(f"🧭 Virgil says: 'This is {zone.name}, a {zone.origin} zone. Let's explore carefully.'")

class ExplorationModule:
    def __init__(self, user_intellect):
        self.registry = ExplorationRegistry()
        self.virgil = VirgilGuide()
        self.user_intellect = user_intellect

    def explore_random_zone(self, return_zone=False):
        available = self.registry.available_zones(self.user_intellect)
        if not available:
            print("⚠️ No suitable zones to explore. Try evolving first.")
            return None

        zone = random.choice(available)
        self.virgil.guide_user(zone)
        zone.explored = True
        print(f"✨ You explored: {zone.name} — Complexity: {zone.complexity_level}")
        return zone if return_zone else None

    def mark_zone_as_explored(self, zone_name):
        for zone in self.registry.zones:
            if zone.name == zone_name:
                zone.explored = True
                print(f"✅ Zone '{zone_name}' marked as explored.")
                return