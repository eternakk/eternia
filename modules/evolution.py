class UserEvolution:
    def __init__(self, intellect=100, senses=100):
        self.intellect = intellect
        self.senses = senses

    def evolve(self, intellect_increment, senses_increment):
        self.intellect += intellect_increment
        self.senses += senses_increment
        print(f"Evolved intellect to {self.intellect}% and senses to {self.senses}%")