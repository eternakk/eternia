# navigator.py

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
  state                - Show your current cognitive/emotional state
  invite <name>        - Send a soul invitation
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

        elif cmd == "state":
            eterna.state.report()

        elif cmd.startswith("invite"):
            try:
                _, name = cmd.split(maxsplit=1)
                eterna.soul_invitations.invite(name)
            except ValueError:
                print("⚠️  Please provide a name after 'invite'.")

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