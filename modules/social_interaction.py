
from typing import Any, Dict, List, Optional, Union

from modules.interfaces import SocialInterface
from modules.population import User

class InteractionManagementSystem:
    def __init__(self):
        self.active_interactions = []

    def initiate_interaction(self, user1, user2):
        if user1.is_allowed() and user2.is_allowed():
            interaction = (user1.name, user2.name)
            self.active_interactions.append(interaction)
            print(f"✅ Interaction initiated between {user1.name} and {user2.name}.")
        else:
            print("⚠️ One or both users don't meet interaction criteria.")

    def monitor_interactions(self):
        for interaction in self.active_interactions:
            print(f"🛡️ Monitoring interaction: {interaction}")

class CollaborativeChallengesSystem:
    def __init__(self):
        self.challenges = [
            "Solve the Multidimensional Ethics Puzzle",
            "Co-explore Quantum Consciousness Landscape",
            "Create a joint world-section inspired by mutual memories"
        ]

    def assign_challenge(self, users):
        challenge = self.challenges[0]  # Simple rotation or random selection
        print(f"🎯 Assigned Challenge to {[u.name for u in users]}: {challenge}")
        return challenge

class SocialInteractionModule(SocialInterface):
    def __init__(self):
        self.users = []
        self.ims = InteractionManagementSystem()
        self.ccs = CollaborativeChallengesSystem()

    def initialize(self) -> None:
        """Initialize the social interaction module."""
        pass

    def shutdown(self) -> None:
        """Perform any cleanup operations when shutting down."""
        pass

    def invite_user(self, user_profile: Dict[str, Any]) -> None:
        """
        Invite a user to participate in social interactions.

        Args:
            user_profile: Dictionary containing user profile information
        """
        # Handle both User objects and dictionaries for backward compatibility
        if isinstance(user_profile, User):
            user = user_profile
        else:
            # Create a User object from the dictionary
            name = user_profile.get('name', 'Unknown')
            intellect = user_profile.get('intellect', 100)
            emotional_maturity = user_profile.get('emotional_maturity', 100)
            consent = user_profile.get('consent', True)  # Default to True for testing
            user = User(name=name, intellect=intellect, emotional_maturity=emotional_maturity, consent=consent)

        if user.is_allowed():
            self.users.append(user)
            print(f"🌟 User {user.name} successfully joined Eterna.")
        else:
            print(f"❌ User {user.name} does not meet criteria or hasn't consented.")

    def initiate_safe_interaction(self, user1_name: str, user2_name: str) -> None:
        """
        Initiate a safe interaction between two users.

        Args:
            user1_name: Name of the first user
            user2_name: Name of the second user
        """
        user1 = next((u for u in self.users if u.name == user1_name), None)
        user2 = next((u for u in self.users if u.name == user2_name), None)
        if user1 and user2 and user1.is_allowed() and user2.is_allowed():
            self.ims.initiate_interaction(user1, user2)
        else:
            print("❌ One or both users not found or not allowed.")

    def assign_collaborative_challenge(self, user_names: List[str]) -> None:
        """
        Assign a collaborative challenge to a group of users.

        Args:
            user_names: List of user names to assign the challenge to
        """
        selected_users = [u for u in self.users if u.name in user_names]
        if len(selected_users) == len(user_names):
            self.ccs.assign_challenge(selected_users)
        else:
            print("❌ Some users not found for challenge assignment.")
