# 🌌 Eterna World Builder — Expanded Core

# This file contains the complete bootstrapping logic for building, simulating,
# and emotionally enriching the Eterna world. It configures zones, emotions, rituals, companions, symbolic modifiers,
# and deep integrations.

from modules.population import User
from modules.memory_integration import Memory
from modules.rituals import Ritual
from modules.physics import PhysicsProfile
from modules.emotions import EmotionalState
from modules.companion_ecology import MemoryEcho, LocalAgent, SymbolicBeing
from modules.zone_modifiers import SymbolicModifier
from modules.resonance_engine import ResonanceEngine  # ✅ NEW

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
    eterna.modifiers.register_modifier(shroud)

def setup_eterna_world(eterna):
    eterna.register_zone("Quantum Forest", origin="AGI", complexity=120, emotion_tag="")
    dreamspace = PhysicsProfile("Dreamspace", gravity=1.5, time_flow=0.6, dimensions=4, energy_behavior="thought-sensitive")
    eterna.define_physics_profile("Quantum Forest", dreamspace)
    eterna.register_zone("Orikum Sea", origin="user", complexity=80, emotion_tag="grief")

    library_physics = PhysicsProfile(
        name="Shared Cognition",
        gravity=5.5,
        time_flow=0.8,
        dimensions=4,
        energy_behavior="emotion-mirroring"
    )

    eterna.register_zone(
        "Library of Shared Minds",
        origin="shared",
        complexity=100,
        emotion_tag="awe",
        default_physics=library_physics
    )
    eterna.define_physics_profile("Library of Shared Minds", library_physics)

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
    chamber = Ritual(
        name="Chamber of Waters",
        purpose="Processing grief, sorrow, and emotional blockages.",
        steps=[
            "Enter the chamber barefoot.",
            "Let water rise to your knees.",
            "Whisper your grief into the water.",
            "Submerge your hands and close your eyes.",
            "Feel the weight dissolve into the stream."
        ],
        symbolic_elements=["water", "echoes", "soft light"]
    )
    eterna.rituals.register(ritual)
    eterna.rituals.register(chamber)

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

def simulate_sensory_evolution(eterna):
    print("\n🌐 Simulating sensory evolution through physics zones...")
    zone_name = "Quantum Forest"
    physics_profile = eterna.physics_registry.get_profile(zone_name)

    if physics_profile:
        eterna.adapt_senses(physics_profile)
        eterna.update_evolution_stats()
        eterna.show_tracker_report()
    else:
        print(f"⚠️ No physics profile found for zone: {zone_name}")

def setup_resonance_engine(eterna):
    eterna.resonance = ResonanceEngine()
    eterna.resonance.tune_environment("Orikum Sea", frequency="calm")
    eterna.resonance.tune_environment("Quantum Forest", frequency="mysterious")
    eterna.resonance.tune_environment("Library of Shared Minds", frequency="reflective")
