"""
Logging Utilities for Eternia

This module provides utility functions for standardized logging throughout the
Eternia project. It helps ensure consistent logging patterns and reduces
duplicate code for common logging scenarios.
"""

import logging
from typing import Any, Dict, List, Optional, Union, Callable

def log_function_entry_exit(logger: Optional[logging.Logger] = None) -> Callable:
    """
    Decorator to log function entry and exit.
    
    Args:
        logger: The logger to use. If None, the root logger is used.
        
    Returns:
        A decorator function
        
    Example:
        @log_function_entry_exit()
        def my_function(arg1, arg2):
            # Function implementation
    """
    if logger is None:
        logger = logging.getLogger()
        
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            logger.debug(f"Entering {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Exiting {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

def log_operation(
    operation: str,
    success: bool,
    logger: Optional[logging.Logger] = None,
    details: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None
) -> None:
    """
    Log an operation with standardized format.
    
    Args:
        operation: The operation being performed
        success: Whether the operation was successful
        logger: The logger to use. If None, the root logger is used.
        details: Additional details about the operation
        error: The exception if the operation failed
    """
    if logger is None:
        logger = logging.getLogger()
        
    status = "SUCCESS" if success else "FAILURE"
    message = f"{operation}: {status}"
    
    if details:
        message += f" - {details}"
        
    if success:
        logger.info(message)
    else:
        if error:
            message += f" - Error: {error}"
        logger.error(message)

def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a module with standardized configuration.
    
    Args:
        module_name: The name of the module
        
    Returns:
        A configured logger for the module
    """
    logger = logging.getLogger(module_name)
    
    # Ensure the logger is configured with at least a StreamHandler if none exists
    if not logger.handlers and not logging.getLogger().handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def log_config_operation(
    operation: str,
    config_key: str,
    success: bool,
    logger: Optional[logging.Logger] = None,
    details: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None
) -> None:
    """
    Log a configuration operation with standardized format.
    
    Args:
        operation: The operation being performed (e.g., 'Loading', 'Validating')
        config_key: The configuration key being operated on
        success: Whether the operation was successful
        logger: The logger to use. If None, the root logger is used.
        details: Additional details about the operation
        error: The exception if the operation failed
    """
    if logger is None:
        logger = logging.getLogger()
        
    status = "SUCCESS" if success else "FAILURE"
    message = f"{operation} configuration '{config_key}': {status}"
    
    if details:
        message += f" - {details}"
        
    if success:
        logger.info(message)
    else:
        if error:
            message += f" - Error: {error}"
        logger.error(message)

def log_batch_operation(
    operation: str,
    total_count: int,
    success_count: int,
    logger: Optional[logging.Logger] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a batch operation with standardized format.
    
    Args:
        operation: The operation being performed
        total_count: The total number of items processed
        success_count: The number of items successfully processed
        logger: The logger to use. If None, the root logger is used.
        details: Additional details about the operation
    """
    if logger is None:
        logger = logging.getLogger()
        
    failure_count = total_count - success_count
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    message = f"{operation}: {success_count}/{total_count} successful ({success_rate:.1f}%)"
    
    if failure_count > 0:
        message += f", {failure_count} failed"
        
    if details:
        message += f" - {details}"
        
    if failure_count == 0:
        logger.info(message)
    elif failure_count < total_count:
        logger.warning(message)
    else:
        logger.error(message)