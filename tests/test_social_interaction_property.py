"""
Property-based tests for the SocialInteractionModule.

This module contains property-based tests for the SocialInteractionModule using the Hypothesis library.
"""

import unittest
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st, assume

from modules.social_interaction import SocialInteractionModule
from modules.population import User


class TestSocialInteractionModule(unittest.TestCase):
    """Property-based tests for the SocialInteractionModule."""

    @given(
        user_name=st.text(min_size=1, max_size=20),
        is_allowed=st.booleans()
    )
    def test_invite_user(self, user_name, is_allowed):
        """Test that invite_user correctly handles users based on their allowed status."""
        # Arrange
        module = SocialInteractionModule()
        user = MagicMock(spec=User)
        user.name = user_name
        user.is_allowed.return_value = is_allowed

        # Act
        module.invite_user(user)

        # Assert
        if is_allowed:
            # User should be added to the users list
            self.assertIn(user, module.users)
        else:
            # User should not be added to the users list
            self.assertNotIn(user, module.users)

    @given(
        user1_name=st.text(min_size=1, max_size=20),
        user2_name=st.text(min_size=1, max_size=20),
        user1_allowed=st.booleans(),
        user2_allowed=st.booleans()
    )
    def test_initiate_safe_interaction(self, user1_name, user2_name, user1_allowed, user2_allowed):
        """Test that initiate_safe_interaction correctly handles interactions based on user existence and permissions."""
        # Assume that the user names are different
        assume(user1_name != user2_name)

        # Arrange
        module = SocialInteractionModule()

        # Create users
        user1 = MagicMock(spec=User)
        user1.name = user1_name
        user1.is_allowed.return_value = user1_allowed

        user2 = MagicMock(spec=User)
        user2.name = user2_name
        user2.is_allowed.return_value = user2_allowed

        # Add users to the module if they are allowed
        if user1_allowed:
            module.users.append(user1)
        if user2_allowed:
            module.users.append(user2)

        # Mock the InteractionManagementSystem
        module.ims = MagicMock()

        # Act
        module.initiate_safe_interaction(user1_name, user2_name)

        # Assert
        if user1_allowed and user2_allowed and user1_name in [u.name for u in module.users] and user2_name in [u.name for u in module.users]:
            # Both users exist and are allowed, so interaction should be initiated
            module.ims.initiate_interaction.assert_called_once()
        else:
            # Either one or both users don't exist or aren't allowed, so interaction should not be initiated
            module.ims.initiate_interaction.assert_not_called()

    @given(
        user_names=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5, unique=True),
        user_allowed=st.lists(st.booleans(), min_size=0, max_size=5)
    )
    def test_assign_collaborative_challenge(self, user_names, user_allowed):
        """Test that assign_collaborative_challenge correctly handles challenge assignment based on user existence."""
        # Arrange
        module = SocialInteractionModule()

        # Create users
        users = []
        for i, name in enumerate(user_names):
            user = MagicMock(spec=User)
            user.name = name
            # Use user_allowed[i] if available, otherwise default to True
            allowed = user_allowed[i] if i < len(user_allowed) else True
            user.is_allowed.return_value = allowed
            users.append(user)

        # Add users to the module if they are allowed
        for user in users:
            if user.is_allowed():
                module.users.append(user)

        # Mock the CollaborativeChallengesSystem
        module.ccs = MagicMock()

        # Act
        module.assign_collaborative_challenge(user_names)

        # Assert
        # All users must exist in the module for the challenge to be assigned
        if all(name in [u.name for u in module.users] for name in user_names):
            # All users exist, so challenge should be assigned
            module.ccs.assign_challenge.assert_called_once()
        else:
            # Some users don't exist, so challenge should not be assigned
            module.ccs.assign_challenge.assert_not_called()


if __name__ == "__main__":
    unittest.main()
