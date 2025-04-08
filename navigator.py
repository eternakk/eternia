# 🧭 Eterna Navigator (CLI)

def eterna_cli(eterna):
    print("\n🌀 Welcome to Eterna Navigator (CLI)")
    print("Type 'help' to list available commands.\n")

    while True:
        cmd = input("🧭 > ").strip().lower()

        if cmd == "help":
            print("""
Available commands:
  zones                - List all zones
  explore <zone_name>  - Explore a specific zone
  dreamwalk            - Enter a random subconscious or memory-based zone
  state                - Show your current cognitive/emotional state
  invite <name>        - Send a soul invitation
  summon <name>        - Summon a symbolic being by name
  evolve               - Trigger a manual evolution process
  reflect <emotion>    - Reflect and process a named emotional state
  rituals              - List all rituals
  perform <name>       - Perform a ritual
  companions           - List companions in your world
  interact <name>      - Interact with a named companion
  exit                 - Leave Eterna
""")

        elif cmd == "zones":
            eterna.exploration.registry.list_zones()

        elif cmd.startswith("explore"):
            try:
                _, zone = cmd.split(maxsplit=1)
                eterna.exploration.manual_explore(zone)
            except ValueError:
                print("⚠️  Please specify a zone name after 'explore'.")

        elif cmd == "dreamwalk":
            print("💭 Entering dreamspace...")
            eterna.exploration.explore_random_zone()

        elif cmd == "state":
            eterna.runtime.state.report()

        elif cmd.startswith("invite"):
            try:
                _, name = cmd.split(maxsplit=1)
                eterna.soul_invitations.invite(name)
            except ValueError:
                print("⚠️  Please provide a name after 'invite'.")

        elif cmd.startswith("summon"):
            try:
                _, name = cmd.split(maxsplit=1)
                eterna.companions.interact_with(name)
            except ValueError:
                print("⚠️  Provide a name to summon a being.")

        elif cmd == "evolve":
            eterna.evolve_user(intellect_inc=5, senses_inc=3)
            print("🧠 You feel your mind expanding and your senses sharpening.")


        elif cmd.startswith("reflect"):

            try:

                _, emotion = cmd.split(maxsplit=1)

                print(f"🪞 Reflecting on {emotion}...")

                # Default reflection parameters

                intensity = 7

                direction = "flowing" if emotion in ["awe", "joy", "love"] else "locked"

                from modules.emotions import EmotionalState

                state = EmotionalState(emotion, intensity, direction)

                eterna.emotion_circuits.process_emotion(state)

            except ValueError:

                print("⚠️ Provide an emotion to reflect upon.")

        elif cmd == "rituals":
            print("\n🔮 Available Rituals:")
            for r in eterna.rituals.rituals.keys():
                print(f" - {r}")

        elif cmd.startswith("perform"):
            try:
                _, name = cmd.split(maxsplit=1)
                eterna.rituals.perform(name)
            except ValueError:
                print("⚠️  Please provide a ritual name after 'perform'.")

        elif cmd == "companions":
            eterna.companions.list_all()

        elif cmd.startswith("interact"):
            try:
                _, name = cmd.split(maxsplit=1)
                eterna.companions.interact_with(name)
            except ValueError:
                print("⚠️  Please provide a companion name after 'interact'.")

        elif cmd == "exit":
            print("💫 Closing Eterna Navigator...")
            break

        else:
            print("❌ Unknown command. Type 'help' for options.")
