# 🧭 Eterna Navigator (CLI)
from world_builder import (
    setup_eterna_world,
    setup_physics_profiles,
    setup_rituals,
    simulate_emotional_events,
    setup_symbolic_modifiers,
    simulate_sensory_evolution,
    setup_companions,
    setup_protection,
)

def eterna_cli(eterna):
    setup_eterna_world(eterna)
    setup_physics_profiles(eterna)
    setup_rituals(eterna)
    setup_companions(eterna)
    simulate_sensory_evolution(eterna)
    simulate_emotional_events(eterna)
    setup_protection(eterna)
    setup_symbolic_modifiers(eterna)


    print("\n🔄 Beginning Eterna Runtime...\n")
    eterna.run_eterna(cycles=5)
    eterna.runtime_report()

    print("\n🌀 Welcome to Eterna Navigator (CLI)")
    print("Type 'help' to list available commands.\n")

    while True:
        cmd = input("🧭 > ").strip().lower()

        if cmd == "help":
            print("""
Available commands:
  zones                                - List all zones
  explore <zone_name>                  - Explore a specific zone
  dreamwalk                            - Enter a random subconscious zone
  state                                - Show current cognitive/emotional state
  invite <name>                        - Send a soul invitation
  summon <name>                        - Summon a symbolic being
  evolve                               - Trigger manual evolution
  reflect <emotion>                    - Reflect and process an emotional state
  rituals                              - List all rituals
  perform <ritual_name>                - Perform a ritual
  companions                           - List companions
  interact <companion_name>            - Interact with a companion
  simulate senses <zone_name>          - Simulate senses in a zone
  synchronize time                     - Adjust and sync time dilation
  deploy agent <hazard_level>          - Deploy reality exploration agent
  recall agent                         - Recall active agent
  exit                                 - Leave Eterna
""")

        elif cmd == "zones":
            eterna.exploration.registry.list_zones()

        elif cmd.startswith("explore"):
            try:
                _, zone = cmd.split(maxsplit=1)
                eterna.exploration.manual_explore(zone)
            except ValueError:
                print("⚠️ Please specify a zone name after 'explore'.")

        elif cmd == "dreamwalk":
            eterna.exploration.explore_random_zone()

        elif cmd == "state":
            eterna.runtime.state.report()

        elif cmd.startswith("invite"):
            try:
                _, name = cmd.split(maxsplit=1)
                eterna.soul_invitations.invite(name)
            except ValueError:
                print("⚠️ Provide a name after 'invite'.")

        elif cmd.startswith("summon"):
            try:
                _, name = cmd.split(maxsplit=1)
                eterna.companions.interact_with(name)
            except ValueError:
                print("⚠️ Provide a name to summon.")

        elif cmd == "evolve":
            eterna.evolve_user(intellect_inc=5, senses_inc=3)
            eterna.state_tracker.update_evolution(
                intellect=eterna.evolution.intellect,
                senses=eterna.senses.score()
            )
            eterna.synchronize_evolution_state()
            print("🧠 Mind expanded, senses sharpened.")

        elif cmd.startswith("simulate senses"):
            zone = cmd.replace("simulate senses", "").strip()
            if zone:
                profile = eterna.physics_registry.get_profile(zone)
                if profile:
                    eterna.adapt_senses(profile)
                    eterna.update_evolution_stats()
                    eterna.show_tracker_report()
                else:
                    print(f"❓ No physics profile found for zone: {zone}")
            else:
                print("⚠️ Usage: simulate senses <zone name>")


        elif cmd == "reflect sample":
            from modules.emotion_data_loader import load_goemotions_sample, get_label_names, label_to_emotion
            from modules.emotional_agent import EmotionProcessor

            dataset = load_goemotions_sample(limit=1)
            label_names = get_label_names()
            sample = dataset[0]

            emotion = label_to_emotion(sample["labels"], label_names)
            agent = EmotionProcessor()
            score = agent(emotion.to_tensor())

            print(f"💥 Sample Emotion: {emotion.name}, Impact Score: {score.item():.2f}")
        elif cmd.startswith("reflect"):
            try:
                _, emotion = cmd.split(maxsplit=1)
                intensity = 7
                direction = "flowing" if emotion in ["awe", "joy", "love"] else "locked"
                from modules.emotions import EmotionalState
                state = EmotionalState(emotion, intensity, direction)
                eterna.emotion_circuits.process_emotion(state)
            except ValueError:
                print("⚠️ Provide an emotion to reflect.")

        elif cmd == "rituals":
            eterna.rituals.list_rituals()

        elif cmd.startswith("perform"):
            try:
                _, name = cmd.split(maxsplit=1)
                eterna.rituals.perform(name)
            except ValueError:
                print("⚠️ Provide ritual name after 'perform'.")

        elif cmd == "companions":
            eterna.companions.list_companions()

        elif cmd.startswith("interact"):
            try:
                _, name = cmd.split(maxsplit=1)
                eterna.companions.interact_with(name)
            except ValueError:
                print("⚠️ Provide a companion name after 'interact'.")

        elif cmd == "synchronize time":
            eterna.synchronize_time()

        elif cmd.startswith("deploy agent"):
            parts = cmd.split()
            hazard_level = int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else 5
            eterna.deploy_reality_agent({'hazard_level': hazard_level})

        elif cmd == "recall agent":
            eterna.recall_reality_agent()

        elif cmd == "exit":
            print("💫 Closing Eterna Navigator...")
            break

        else:
            print("❌ Unknown command. Type 'help' for options.")
