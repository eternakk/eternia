"""
Test script for logging_utils.py

This script tests the logging utility functions in logging_utils.py.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.utilities.logging_utils import (
    log_function_entry_exit,
    log_operation,
    get_module_logger,
    log_config_operation,
    log_batch_operation
)

class TestLoggingUtils(unittest.TestCase):
    """Test cases for logging_utils.py functions."""

    @patch('modules.utilities.logging_utils.logging')
    def test_log_function_entry_exit(self, mock_logging):
        """Test log_function_entry_exit decorator."""
        # Setup mock
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        # Define a test function with the decorator
        @log_function_entry_exit()
        def test_function(arg1, arg2):
            return arg1 + arg2

        # Call the function and check logging
        result = test_function(1, 2)

        self.assertEqual(result, 3)  # Function should work normally
        mock_logger.debug.assert_any_call("Entering test_function")
        mock_logger.debug.assert_any_call("Exiting test_function")

        # Test with custom logger
        custom_logger = MagicMock()

        @log_function_entry_exit(logger=custom_logger)
        def test_function2(arg1, arg2):
            return arg1 * arg2

        result = test_function2(2, 3)

        self.assertEqual(result, 6)  # Function should work normally
        custom_logger.debug.assert_any_call("Entering test_function2")
        custom_logger.debug.assert_any_call("Exiting test_function2")

        # Test with exception
        @log_function_entry_exit()
        def test_function_error():
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            test_function_error()

        mock_logger.debug.assert_any_call("Entering test_function_error")
        mock_logger.error.assert_any_call("Error in test_function_error: Test error")

    @patch('modules.utilities.logging_utils.logging')
    def test_log_operation(self, mock_logging):
        """Test log_operation function."""
        # Setup mock
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        # Test successful operation
        log_operation("Test operation", True)
        mock_logger.info.assert_called_with("Test operation: SUCCESS")

        # Test failed operation
        log_operation("Test operation", False)
        mock_logger.error.assert_called_with("Test operation: FAILURE")

        # Test with details
        details = {"key": "value"}
        log_operation("Test operation", True, details=details)
        mock_logger.info.assert_called_with(f"Test operation: SUCCESS - {details}")

        # Test with error
        error = Exception("Test error")
        log_operation("Test operation", False, error=error)
        mock_logger.error.assert_called_with("Test operation: FAILURE - Error: Test error")

        # Test with custom logger
        custom_logger = MagicMock()
        log_operation("Test operation", True, logger=custom_logger)
        custom_logger.info.assert_called_with("Test operation: SUCCESS")

    @patch('modules.utilities.logging_utils.logging')
    def test_get_module_logger(self, mock_logging):
        """Test get_module_logger function."""
        # Setup mock
        mock_module_logger = MagicMock()
        mock_root_logger = MagicMock()

        # Configure getLogger to return different loggers based on the argument
        def get_logger_side_effect(name=None):
            if name == "test_module":
                return mock_module_logger
            return mock_root_logger

        mock_logging.getLogger.side_effect = get_logger_side_effect

        # Configure handlers
        mock_module_logger.handlers = []
        mock_root_logger.handlers = []

        # Test getting a logger
        result = get_module_logger("test_module")

        # Verify that getLogger was called with the correct module name
        mock_logging.getLogger.assert_any_call("test_module")
        self.assertEqual(result, mock_module_logger)

        # Test that a handler is added if none exists
        mock_logging.reset_mock()  # Reset the mock to clear previous calls

        # Create new mocks for this test
        mock_handler = MagicMock()
        mock_formatter = MagicMock()
        mock_logging.StreamHandler.return_value = mock_handler
        mock_logging.Formatter.return_value = mock_formatter

        # Make sure the logger has no handlers for this test
        mock_module_logger.handlers = []
        mock_root_logger.handlers = []

        result = get_module_logger("test_module")

        # Verify that StreamHandler and Formatter were called
        mock_logging.StreamHandler.assert_called_once()
        mock_logging.Formatter.assert_called_once()
        mock_handler.setFormatter.assert_called_with(mock_formatter)
        mock_module_logger.addHandler.assert_called_with(mock_handler)

        # Test that no handler is added if one already exists
        mock_logging.reset_mock()
        mock_module_logger.handlers = [MagicMock()]

        result = get_module_logger("test_module")

        mock_logging.StreamHandler.assert_not_called()

    @patch('modules.utilities.logging_utils.logging')
    def test_log_config_operation(self, mock_logging):
        """Test log_config_operation function."""
        # Setup mock
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        # Test successful operation
        log_config_operation("Loading", "test.config", True)
        mock_logger.info.assert_called_with("Loading configuration 'test.config': SUCCESS")

        # Test failed operation
        log_config_operation("Loading", "test.config", False)
        mock_logger.error.assert_called_with("Loading configuration 'test.config': FAILURE")

        # Test with details
        details = {"key": "value"}
        log_config_operation("Loading", "test.config", True, details=details)
        mock_logger.info.assert_called_with(f"Loading configuration 'test.config': SUCCESS - {details}")

        # Test with error
        error = Exception("Test error")
        log_config_operation("Loading", "test.config", False, error=error)
        mock_logger.error.assert_called_with("Loading configuration 'test.config': FAILURE - Error: Test error")

        # Test with custom logger
        custom_logger = MagicMock()
        log_config_operation("Loading", "test.config", True, logger=custom_logger)
        custom_logger.info.assert_called_with("Loading configuration 'test.config': SUCCESS")

    @patch('modules.utilities.logging_utils.logging')
    def test_log_batch_operation(self, mock_logging):
        """Test log_batch_operation function."""
        # Setup mock
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        # Test all successful
        log_batch_operation("Processing items", 10, 10)
        mock_logger.info.assert_called_with("Processing items: 10/10 successful (100.0%)")

        # Test some failures
        log_batch_operation("Processing items", 10, 7)
        mock_logger.warning.assert_called_with("Processing items: 7/10 successful (70.0%), 3 failed")

        # Test all failures
        log_batch_operation("Processing items", 10, 0)
        mock_logger.error.assert_called_with("Processing items: 0/10 successful (0.0%), 10 failed")

        # Test with details
        details = {"key": "value"}
        log_batch_operation("Processing items", 10, 10, details=details)
        mock_logger.info.assert_called_with(f"Processing items: 10/10 successful (100.0%) - {details}")

        # Test with custom logger
        custom_logger = MagicMock()
        log_batch_operation("Processing items", 10, 10, logger=custom_logger)
        custom_logger.info.assert_called_with("Processing items: 10/10 successful (100.0%)")

        # Test with zero total
        log_batch_operation("Processing items", 0, 0)
        mock_logger.info.assert_called_with("Processing items: 0/0 successful (0.0%)")

if __name__ == "__main__":
    unittest.main()
