# 🌍 world_builder.py — Eterna initialization scaffolding

from modules.population import User
from modules.memory_integration import Memory
from modules.rituals import Ritual
from modules.physics import PhysicsProfile
from modules.emotions import EmotionalState
from modules.companion_ecology import MemoryEcho, LocalAgent, SymbolicBeing

from modules.zone_modifiers import SymbolicModifier

def setup_symbolic_modifiers(eterna):
    shroud = SymbolicModifier(
        name="Shroud of Memory",
        trigger_emotion="grief",
        effects=[
            "colors desaturate",
            "fog rolls in from the sea",
            "sorrow altar emerges from the rocks",
            "ambient cello music plays from the mist"
        ]
    )
    eterna.zone_modifiers.register_modifier(shroud)

def setup_eterna_world(eterna):
    eterna.register_zone("Orikum Sea", origin="user", complexity=80)
    eterna.register_zone("Quantum Forest", origin="AGI", complexity=120)
    eterna.register_zone("Library of Shared Minds", origin="shared", complexity=100)

    alice = User("Alice", intellect=115, emotional_maturity=115, consent=True)
    bob = User("Bob", intellect=120, emotional_maturity=118, consent=True)
    eterna.invite_social_user(alice)
    eterna.invite_social_user(bob)

    memory = Memory("Sunrise by the sea with family", clarity=9, emotional_quality="positive")
    eterna.integrate_memory(memory.description, memory.clarity, memory.emotional_quality)

    eterna.update_emotional_state(mood="curious", stress_level=3, trauma_triggered=False)

def setup_physics_profiles(eterna):
    normal = PhysicsProfile("Earth-Like", gravity=9.8, time_flow=1.0, dimensions=3)
    dream = PhysicsProfile("Dreamspace", gravity=1.5, time_flow=0.6, dimensions=4, energy_behavior="thought-sensitive")
    unstable = PhysicsProfile("Unstable Rift", gravity=0, time_flow=3.0, dimensions=5, conscious_safe=False)

    eterna.define_physics_profile("Orikum Sea", normal)
    eterna.define_physics_profile("Quantum Forest", dream)
    eterna.define_physics_profile("Void Spiral", unstable)

    eterna.show_zone_physics("Orikum Sea")
    eterna.show_zone_physics("Quantum Forest")
    eterna.show_zone_physics("Void Spiral")

def setup_rituals(eterna):
    ritual = Ritual(
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
    eterna.rituals.register(ritual)

def setup_companions(eterna):
    lira = MemoryEcho("Lira", "Your mother holding your hand near the sea during a golden sunrise in Orikum.")
    bran = LocalAgent("Bran", job="storykeeper")
    selene = SymbolicBeing("Selene", archetype="lunar guide")
    eko = SymbolicBeing("Eko", archetype="joyful shapeshifter")
    elder = SymbolicBeing("The Elder", archetype="existential mirror")

    eterna.companions.spawn(lira)
    eterna.companions.spawn(bran)
    eterna.companions.spawn(selene)
    eterna.companions.spawn(eko)
    eterna.companions.spawn(elder)

def setup_protection(eterna):
    eternal_threats = ["solar_flare", "aging"]
    detected = eterna.threats.detect(eternal_threats)
    eterna.vitals.add_threat("solar_flare")
    eterna.defense.engage(detected)
    eterna.defense.activate_failsafe()

def simulate_emotional_events(eterna):
    emotion = EmotionalState("grief", intensity=9, direction="locked")
    eterna.emotion_circuits.process_emotion(emotion)
    eterna.soul_invitations.invite("Lira")
    eterna.soul_invitations.receive_response("Lira", accepted=True)
    eterna.soul_presence.register_presence("Lira")
    eterna.soul_presence.list_present_souls()
