class User:
    def __init__(self, name, intellect=100, emotional_maturity=100, consent=False):
        self.name = name
        self.intellect = intellect
        self.emotional_maturity = emotional_maturity
        self.consent = consent

    def is_allowed(self, intellect_threshold=110, emotional_threshold=110):
        return (self.intellect >= intellect_threshold and
                self.emotional_maturity >= emotional_threshold and
                self.consent)

class WorldPopulation:
    def __init__(self):
        self.users = []

    def invite_user(self, user):
        if user.is_allowed():
            self.users.append(user)
            print(f"{user.name} successfully invited to Eterna.")
        else:
            print(f"{user.name} doesn't meet the maturity or intelligence criteria.")