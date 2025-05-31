"""
Test script for config_utils.py

This script tests the configuration utility functions in config_utils.py.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.utilities.config_utils import (
    get_config_value,
    get_config_dict,
    get_config_list,
    get_config_section_items,
    iterate_config_section
)

class TestConfigUtils(unittest.TestCase):
    """Test cases for config_utils.py functions."""

    @patch('modules.utilities.config_utils.config')
    def test_get_config_value(self, mock_config):
        """Test get_config_value function."""
        # Setup mock
        mock_config.get.return_value = "test_value"

        # Test basic retrieval
        result = get_config_value("test.key")
        self.assertEqual(result, "test_value")
        mock_config.get.assert_called_with("test.key", None)

        # Test with default value
        mock_config.get.side_effect = lambda key, default=None: default if key == "missing.key" else "test_value"
        result = get_config_value("missing.key", default="default_value")
        self.assertEqual(result, "default_value")

        # Test with required=True and missing value
        mock_config.get.side_effect = None  # Reset side_effect
        mock_config.get.return_value = None
        with self.assertRaises(Exception):
            get_config_value("required.key", required=True)

        # Test with expected_type
        mock_config.get.return_value = "string_value"
        result = get_config_value("string.key", expected_type=str)
        self.assertEqual(result, "string_value")

        # Test with wrong type
        mock_config.get.return_value = "not_an_int"
        result = get_config_value("int.key", expected_type=int, default=0)
        self.assertEqual(result, 0)  # Should return default when type validation fails

    @patch('modules.utilities.config_utils.config')
    def test_get_config_dict(self, mock_config):
        """Test get_config_dict function."""
        # Setup mock
        test_dict = {"key1": "value1", "key2": "value2"}
        mock_config.get.return_value = test_dict

        # Test basic retrieval
        result = get_config_dict("test.dict")
        self.assertEqual(result, test_dict)

        # Test with default value when not a dict
        mock_config.get.return_value = "not_a_dict"
        result = get_config_dict("not.dict", default={"default": "value"})
        self.assertEqual(result, {"default": "value"})

        # Test with required keys
        mock_config.get.return_value = test_dict
        result = get_config_dict("test.dict", required_keys=["key1"])
        self.assertEqual(result, test_dict)

        # Test with missing required keys
        result = get_config_dict("test.dict", required_keys=["key3"])
        self.assertEqual(result, {})  # Should return default when required keys are missing

    @patch('modules.utilities.config_utils.config')
    def test_get_config_list(self, mock_config):
        """Test get_config_list function."""
        # Setup mock
        test_list = ["item1", "item2", "item3"]
        mock_config.get.return_value = test_list

        # Test basic retrieval
        result = get_config_list("test.list")
        self.assertEqual(result, test_list)

        # Test with default value when not a list
        mock_config.get.return_value = "not_a_list"
        result = get_config_list("not.list", default=["default"])
        self.assertEqual(result, ["default"])

        # Test with item_type
        mock_config.get.return_value = ["1", "2", "3"]
        result = get_config_list("string.list", item_type=str)
        self.assertEqual(result, ["1", "2", "3"])

        # Test with wrong item type
        mock_config.get.return_value = ["1", "2", "not_an_int"]
        result = get_config_list("int.list", item_type=int)
        self.assertEqual(result, [])  # Should filter out invalid items

    @patch('modules.utilities.config_utils.config')
    def test_get_config_section_items(self, mock_config):
        """Test get_config_section_items function."""
        # Setup mock
        section_dict = {"item1": {}, "item2": {}}
        mock_config.get.side_effect = lambda key, default=None: (
            section_dict if key == "section" else 
            {"subkey": "value"} if key in ["section.item1", "section.item2"] else 
            default
        )

        # Test retrieval of section items
        result = get_config_section_items("section")
        self.assertEqual(result, {"item1": {"subkey": "value"}, "item2": {"subkey": "value"}})

    @patch('modules.utilities.config_utils.config')
    def test_iterate_config_section(self, mock_config):
        """Test iterate_config_section function."""
        # Setup mock
        section_dict = {"item1": {}, "item2": {}}
        item1_dict = {"required_key": "value1", "other_key": "other1"}
        item2_dict = {"required_key": "value2", "other_key": "other2"}

        mock_config.get.side_effect = lambda key, default=None: (
            section_dict if key == "section" else 
            item1_dict if key == "section.item1" else
            item2_dict if key == "section.item2" else
            default
        )

        # Test iteration with callback
        processed_items = {}

        def callback(key, value):
            processed_items[key] = value

        count = iterate_config_section("section", callback)

        self.assertEqual(count, 2)
        self.assertEqual(processed_items, {"item1": item1_dict, "item2": item2_dict})

        # Test with required keys
        processed_items.clear()
        count = iterate_config_section("section", callback, required_keys=["required_key"])

        self.assertEqual(count, 2)
        self.assertEqual(processed_items, {"item1": item1_dict, "item2": item2_dict})

        # Test with missing required keys
        processed_items.clear()
        count = iterate_config_section("section", callback, required_keys=["missing_key"])

        self.assertEqual(count, 0)
        self.assertEqual(processed_items, {})

if __name__ == "__main__":
    unittest.main()
