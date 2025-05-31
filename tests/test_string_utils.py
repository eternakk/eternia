"""
Test script for string_utils.py

This script tests the naming convention conversion functions in string_utils.py.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.utilities.string_utils import (
    snake_to_camel, camel_to_snake,
    snake_to_kebab, kebab_to_snake,
    camel_to_kebab, kebab_to_camel,
    snake_to_pascal, pascal_to_snake,
    camel_to_pascal, pascal_to_camel,
    kebab_to_pascal, pascal_to_kebab
)

def test_naming_conventions():
    """Test all naming convention conversion functions."""
    # Test data
    snake_case = "user_profile_data"
    camel_case = "userProfileData"
    kebab_case = "user-profile-data"
    pascal_case = "UserProfileData"
    
    # Test snake_case conversions
    assert snake_to_camel(snake_case) == camel_case
    assert snake_to_kebab(snake_case) == kebab_case
    assert snake_to_pascal(snake_case) == pascal_case
    
    # Test camel_case conversions
    assert camel_to_snake(camel_case) == snake_case
    assert camel_to_kebab(camel_case) == kebab_case
    assert camel_to_pascal(camel_case) == pascal_case
    
    # Test kebab_case conversions
    assert kebab_to_snake(kebab_case) == snake_case
    assert kebab_to_camel(kebab_case) == camel_case
    assert kebab_to_pascal(kebab_case) == pascal_case
    
    # Test pascal_case conversions
    assert pascal_to_snake(pascal_case) == snake_case
    assert pascal_to_camel(pascal_case) == camel_case
    assert pascal_to_kebab(pascal_case) == kebab_case
    
    # Test edge cases
    assert snake_to_camel("") == ""
    assert camel_to_snake("") == ""
    assert snake_to_kebab("") == ""
    assert kebab_to_snake("") == ""
    assert snake_to_pascal("") == ""
    assert pascal_to_snake("") == ""
    assert camel_to_pascal("") == ""
    assert pascal_to_camel("") == ""
    assert kebab_to_pascal("") == ""
    assert pascal_to_kebab("") == ""
    
    # Test single word
    assert snake_to_camel("user") == "user"
    assert camel_to_snake("user") == "user"
    assert snake_to_kebab("user") == "user"
    assert kebab_to_snake("user") == "user"
    assert snake_to_pascal("user") == "User"
    assert pascal_to_snake("User") == "user"
    assert camel_to_pascal("user") == "User"
    assert pascal_to_camel("User") == "user"
    assert kebab_to_pascal("user") == "User"
    assert pascal_to_kebab("User") == "user"
    
    print("All tests passed!")

if __name__ == "__main__":
    test_naming_conventions()