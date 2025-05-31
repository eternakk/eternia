from modules.interfaces import EvolutionInterface

class UserEvolution(EvolutionInterface):
    def __init__(self, intellect=100, senses=100):
        self.intellect = intellect
        self.senses = senses

    def initialize(self) -> None:
        """Initialize the evolution module."""
        pass

    def shutdown(self) -> None:
        """Perform any cleanup operations when shutting down."""
        pass

    def evolve(self, intellect_inc: int, senses_inc: int) -> None:
        """
        Evolve the user's capabilities.

        Args:
            intellect_inc: The amount to increase intellect by
            senses_inc: The amount to increase senses by
        """
        self.intellect += intellect_inc
        self.senses += senses_inc
        print(f"Evolved intellect to {self.intellect}% and senses to {self.senses}%")

    @property
    def intellect(self) -> int:
        """Get the current intellect level."""
        return self._intellect

    @intellect.setter
    def intellect(self, value: int) -> None:
        """Set the intellect level."""
        self._intellect = value
