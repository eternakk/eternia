import random
from typing import Any, Optional

from modules.interfaces import ExplorationInterface


class ExplorationZone:
    def __init__(self, name, origin, complexity_level, emotion_tag=None):
        self.name = name
        self.origin = origin  # 'user', 'AGI', 'shared'
        self.complexity_level = complexity_level
        self.explored = False
        self.emotion_tag = emotion_tag  # New symbolic emotional link
        self.modifiers = []  # To store symbolic overlays

    def add_modifier(self, modifier_name):
        if modifier_name not in self.modifiers:
            self.modifiers.append(modifier_name)
            print(f"🌗 Zone '{self.name}' was symbolically modified with '{modifier_name}'.")

    def show_modifiers(self):
        if self.modifiers:
            print(f"🎨 Symbolic Layers for '{self.name}':")
            for m in self.modifiers:
                print(f" - {m}")
        else:
            print(f"➖ No symbolic modifiers in '{self.name}'.")

class ExplorationRegistry:
    def __init__(self):
        self.zones = []

    def register_zone(self, zone):
        self.zones.append(zone)
        print(f"🌍 New zone registered: {zone.name} ({zone.origin})")

    def available_zones(self, user_intellect):
        return [z for z in self.zones if not z.explored and z.complexity_level <= user_intellect + 15]

    def list_zones(self):
        if not self.zones:
            print("🌌 No zones registered.")
        else:
            print("🌌 Registered Exploration Zones:")
            for zone in self.zones:
                explored_status = "✅" if zone.explored else "🟣"
                print(f" - {zone.name} ({zone.origin}, complexity: {zone.complexity_level}) {explored_status}")

    def get_zones_by_emotion(self, emotion_name):
        return [z for z in self.zones if z.emotion_tag == emotion_name]

class VirgilGuide:
    def guide_user(self, zone, physics_profile=None):
        print(f"🧭 Virgil: 'Entering {zone.name} — a {zone.origin} zone.'")
        if physics_profile:
            print(f"📐 Virgil: 'Expect {physics_profile.dimensions} dimensions, gravity {physics_profile.gravity}, and {physics_profile.energy_behavior} energy.'")

class ExplorationModule(ExplorationInterface):
    def __init__(self, user_intellect, eterna_interface=None):
        self.registry = ExplorationRegistry()
        self.virgil = VirgilGuide()
        self.user_intellect = user_intellect
        self.eterna = eterna_interface
        self.current_zone = None

    def initialize(self) -> None:
        """Initialize the exploration module."""
        pass

    def shutdown(self) -> None:
        """Perform any cleanup operations when shutting down."""
        pass

    def register_zone(self, zone: Any) -> None:
        """
        Register a new exploration zone.

        Args:
            zone: The zone to register
        """
        self.registry.register_zone(zone)

    def explore_random_zone(self, return_zone=False) -> Optional[Any]:
        """
        Explore a random zone.

        Args:
            return_zone: Whether to return the zone object

        Returns:
            The zone object if return_zone is True, None otherwise
        """
        available = self.registry.available_zones(self.user_intellect)
        if not available:
            print("⚠️ No suitable zones to explore. Try evolving first.")
            return None

        zone = random.choice(available)
        self.current_zone = zone.name

        # 🧠 Get physics profile for Virgil to reference
        physics_profile = self.eterna.physics_registry.get_profile(zone.name) if hasattr(self, 'eterna') else None

        # 🧙 Virgil provides guidance with physics context
        self.virgil.guide_user(zone, physics_profile)

        zone.explored = True
        if self.eterna:
            self.eterna.state_tracker.mark_zone(zone.name)
        print(f"✨ You explored: {zone.name} — Complexity: {zone.complexity_level}")
        return zone if return_zone else None

    def manual_explore(self, zone_name):
        zone = next((z for z in self.registry.zones if z.name.lower() == zone_name.lower()), None)
        if zone:
            physics_profile = self.eterna.physics_registry.get_profile(zone.name) if self.eterna else None
            self.virgil.guide_user(zone, physics_profile)
            zone.explored = True
            if self.eterna:
                self.eterna.state_tracker.mark_zone(zone.name)
            print(f"✨ Manually explored: {zone.name} — Complexity: {zone.complexity_level}")
        else:
            print(f"⚠️ Zone '{zone_name}' doesn't exist.")


    def mark_zone_as_explored(self, zone_name):
        for zone in self.registry.zones:
            if zone.name == zone_name:
                zone.explored = True
                print(f"✅ Zone '{zone_name}' marked as explored.")
                return
