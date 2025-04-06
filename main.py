from eterna_interface import EternaInterface
from modules.emotions import EmotionalState
from modules.physics import PhysicsProfile
from modules.population import  User
from modules.memory_integration import Memory
from modules.rituals import Ritual


def setup_eterna_world(eterna):

    # Register some initial exploration zones
    eterna.register_zone("Orikum Sea", origin="user", complexity=80)
    eterna.register_zone("Quantum Forest", origin="AGI", complexity=120)
    eterna.register_zone("Library of Shared Minds", origin="shared", complexity=100)

    # Invite some users (must meet criteria)
    alice = User("Alice", intellect=115, emotional_maturity=115, consent=True)
    bob = User("Bob", intellect=120, emotional_maturity=118, consent=True)
    eterna.invite_social_user(alice)
    eterna.invite_social_user(bob)

    # Add a memory to test memory integration
    memory = Memory("Sunrise by the sea with family", clarity=9, emotional_quality="positive")
    eterna.integrate_memory(memory.description, memory.clarity, memory.emotional_quality)

    # Simulate emotional input
    eterna.update_emotional_state(mood="curious", stress_level=3, trauma_triggered=False)

def setup_physics_profiles(eterna):
    # Define some example physics profiles
    normal_physics = PhysicsProfile("Earth-Like", gravity=9.8, time_flow=1.0, dimensions=3)
    dreamspace = PhysicsProfile("Dreamspace", gravity=1.5, time_flow=0.6, dimensions=4, energy_behavior="thought-sensitive")
    unstable = PhysicsProfile("Unstable Rift", gravity=0, time_flow=3.0, dimensions=5, conscious_safe=False)

    # Assign profiles to zones
    eterna.define_physics_profile("Orikum Sea", normal_physics)
    eterna.define_physics_profile("Quantum Forest", dreamspace)
    eterna.define_physics_profile("Void Spiral", unstable)  # Will be rejected due to safety

    # View physics summaries
    eterna.show_zone_physics("Orikum Sea")
    eterna.show_zone_physics("Quantum Forest")
    eterna.show_zone_physics("Void Spiral")

def setup_rituals(eterna):
    rebirth_ritual = Ritual(
        name="Ash Garden Rebirth",
        purpose="Letting go of a former self or identity.",
        steps=[
            "Enter the Ash Garden in silence.",
            "Speak the name of the part of you that must end.",
            "Place it into the fire altar.",
            "Watch it burn. Do not look away.",
            "Step into the circle of light.",
            "Speak your new name, or remain silent to evolve without identity."
        ],
        symbolic_elements=["fire", "ashes", "circle of light"]
    )

    eterna.rituals.register(rebirth_ritual)


def main():
    # Initialize your world
    eterna = EternaInterface()

    print("🚀 Initializing Eterna...\n")
    setup_eterna_world(eterna)

    setup_physics_profiles(eterna)

    # Run simulation cycles
    print("\n🔄 Beginning Eterna Runtime...\n")
    eterna.run_eterna(cycles=5)  # You can increase to 10, 20, etc.
    eterna.runtime_report()
    setup_rituals(eterna)
    emotion = EmotionalState("grief", intensity=9, direction="locked")
    eterna.emotion_circuits.process_emotion(emotion)
    eterna.soul_invitations.invite("Lira")
    eterna.soul_invitations.receive_response("Lira", accepted=True)
    eterna.soul_presence.register_presence("Lira")
    eterna.soul_presence.list_present_souls()

if __name__ == "__main__":
    main()