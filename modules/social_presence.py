# modules/social_presence.py

class SoulInvitation:
    def __init__(self, name, message=None):
        self.name = name
        self.message = message or "You are invited to co-create in Eterna."
        self.accepted = False


class SoulInvitationSystem:
    def __init__(self):
        self.sent_invitations = []

    def invite(self, name, message=None):
        invitation = SoulInvitation(name, message)
        self.sent_invitations.append(invitation)
        print(f"📨 Invitation sent to {name}. Awaiting consent...")

    def receive_response(self, name, accepted):
        for invitation in self.sent_invitations:
            if invitation.name == name:
                invitation.accepted = accepted
                print(f"🧾 Response received from {name}: {'Accepted' if accepted else 'Declined'}")
                return
        print(f"❓ No invitation found for {name}")


class SoulPresenceRegistry:
    def __init__(self):
        self.present_souls = []

    def register_presence(self, name):
        if name not in self.present_souls:
            self.present_souls.append(name)
            print(f"🌟 {name} is now present in your world.")
        else:
            print(f"ℹ️ {name} is already present.")

    def list_present_souls(self):
        if not self.present_souls:
            print("👥 No souls currently in Eterna.")
        else:
            print("👥 Souls currently in Eterna:")
            for name in self.present_souls:
                print(f"   • {name}")