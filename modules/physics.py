class PhysicsProfile:
    def __init__(self, name, gravity=9.8, time_flow=1.0, dimensions=3, energy_behavior="standard", conscious_safe=True):
        self.name = name
        self.gravity = gravity  # relative to Earth (9.8 m/s²)
        self.time_flow = time_flow  # 1.0 = normal speed, <1 = slow, >1 = fast
        self.dimensions = dimensions  # spatial dimensions
        self.energy_behavior = energy_behavior  # e.g., "standard", "field-reactive", "thought-sensitive"
        self.conscious_safe = conscious_safe  # must be True for simulation stability

    def summary(self):
        return {
            "name": self.name,
            "gravity": self.gravity,
            "time_flow": self.time_flow,
            "dimensions": self.dimensions,
            "energy_behavior": self.energy_behavior,
            "conscious_safe": self.conscious_safe
        }

class PhysicsZoneRegistry:
    def __init__(self):
        self.zone_profiles = {}
        self.profiles = {}  # ✅ add this line to hold the profiles

    def assign_profile(self, zone_name, profile: PhysicsProfile):
        if profile.conscious_safe:
            self.zone_profiles[zone_name] = profile
            print(f"🌐 Physics profile '{profile.name}' assigned to zone: {zone_name}")
        else:
            print(f"❌ Profile '{profile.name}' rejected for zone '{zone_name}' — consciousness integrity risk.")

    def get_profile(self, zone_name):
        for key in self.zone_profiles:
            if key.lower() == zone_name.lower():
                return self.zone_profiles[key]
        return None