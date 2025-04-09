from eterna_interface import EternaInterface
from navigator import eterna_cli

from world_builder import (
    setup_eterna_world,
    setup_physics_profiles,
    setup_rituals,
    setup_companions,
    setup_protection,
    simulate_emotional_events, setup_symbolic_modifiers, simulate_sensory_evolution
)

def main():
    eterna = EternaInterface()
    print("\n🚀 Initializing Eterna...\n")



    eterna_cli(eterna)

if __name__ == "__main__":
    main()
