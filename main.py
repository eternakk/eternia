from eterna_interface import EternaInterface
from navigator import eterna_cli

from world_builder import (
    setup_eterna_world,
    setup_physics_profiles,
    setup_rituals,
    setup_companions,
    setup_protection,
    simulate_emotional_events
)

def main():
    eterna = EternaInterface()
    print("\n🚀 Initializing Eterna...\n")

    setup_eterna_world(eterna)
    setup_physics_profiles(eterna)
    setup_rituals(eterna)
    setup_companions(eterna)
    simulate_emotional_events(eterna)
    setup_protection(eterna)

    print("\n🔄 Beginning Eterna Runtime...\n")
    eterna.run_eterna(cycles=5)
    eterna.runtime_report()

    eterna_cli(eterna)

if __name__ == "__main__":
    main()
