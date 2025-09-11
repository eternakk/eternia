"""
Logging Utilities for Eternia

This module provides utility functions for standardized logging throughout the
Eternia project. It helps ensure consistent logging patterns and reduces
duplicate code for common logging scenarios.

This module supports structured logging with contextual information, allowing
for more detailed and searchable logs.
"""

import logging
import functools
import inspect
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, cast
from contextlib import contextmanager

# Type variable for generic function return type
T = TypeVar('T')

def log_function_entry_exit(logger: Optional[logging.Logger] = None, include_args: bool = False) -> Callable:
    """
    Decorator to log function entry and exit with contextual information.

    Args:
        logger: The logger to use. If None, the root logger is used.
        include_args: Whether to include function arguments in the log context

    Returns:
        A decorator function

    Example:
        @log_function_entry_exit(include_args=True)
        def my_function(arg1, arg2):
            # Function implementation
    """
    if logger is None:
        logger = logging.getLogger()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create context with function information
            context = {
                'function': func.__name__,
                'module': func.__module__,
            }

            # Add arguments to context if requested
            if include_args:
                # Get function signature
                sig = inspect.signature(func)

                # Bind arguments to parameters
                try:
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()

                    # Add arguments to context, excluding self/cls for methods
                    for param_name, param_value in bound_args.arguments.items():
                        if param_name not in ('self', 'cls'):
                            # Convert to string to avoid complex objects
                            try:
                                context[f'arg_{param_name}'] = str(param_value)
                            except:
                                context[f'arg_{param_name}'] = f"<unprintable {type(param_value).__name__}>"
                except Exception as e:
                    context['arg_binding_error'] = str(e)

            logger.debug(f"Entering {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Exiting {func.__name__}")
                return result
            except Exception as e:
                error_context = context.copy()
                error_context['error'] = str(e)
                error_context['error_type'] = type(e).__name__
                logger.error(f"Error in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

def log_operation(
    operation: str,
    success: bool,
    logger: Optional[logging.Logger] = None,
    details: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an operation with standardized format and contextual information.

    Args:
        operation: The operation being performed
        success: Whether the operation was successful
        logger: The logger to use. If None, the root logger is used.
        details: Additional details about the operation
        error: The exception if the operation failed
        context: Additional contextual information to include in the log
    """
    if logger is None:
        logger = logging.getLogger()

    status = "SUCCESS" if success else "FAILURE"
    message = f"{operation}: {status}"

    if details:
        message += f" - {details}"

    # Create extra context dictionary
    extra = {
        'operation_type': 'standard',
        'operation_name': operation,
        'success': success,
    }

    # Add details to context
    if details:
        for key, value in details.items():
            extra[f'detail_{key}'] = value

    # Add error information to context
    if error:
        extra['error'] = str(error)
        extra['error_type'] = type(error).__name__

        # Add traceback if available
        if hasattr(error, '__traceback__'):
            import traceback
            tb_str = ''.join(traceback.format_tb(error.__traceback__))
            extra['traceback'] = tb_str

    # Add any additional context
    if context:
        extra.update(context)

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
    error: Optional[Exception] = None,
    context: Optional[Dict[str, Any]] = None
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
        context: Additional contextual information to include in the log
    """
    if logger is None:
        logger = logging.getLogger()

    status = "SUCCESS" if success else "FAILURE"
    message = f"{operation} configuration '{config_key}': {status}"

    if details:
        message += f" - {details}"

    # Create extra context dictionary
    extra = {
        'operation_type': 'config',
        'operation_name': operation,
        'config_key': config_key,
        'success': success,
    }

    # Add details to context
    if details:
        for key, value in details.items():
            extra[f'detail_{key}'] = value

    # Add error information to context
    if error:
        extra['error'] = str(error)
        extra['error_type'] = type(error).__name__

        # Add traceback if available
        if hasattr(error, '__traceback__'):
            import traceback
            tb_str = ''.join(traceback.format_tb(error.__traceback__))
            extra['traceback'] = tb_str

    # Add any additional context
    if context:
        extra.update(context)

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
    details: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a batch operation with standardized format.

    Args:
        operation: The operation being performed
        total_count: The total number of items processed
        success_count: The number of items successfully processed
        logger: The logger to use. If None, the root logger is used.
        details: Additional details about the operation
        context: Contextual information to include in the log
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

    # Create extra context dictionary
    extra = {
        'operation_type': 'batch',
        'operation_name': operation,
        'total_count': total_count,
        'success_count': success_count,
        'failure_count': failure_count,
        'success_rate': success_rate
    }

    # Add any additional context
    if context:
        extra.update(context)

    if failure_count == 0:
        logger.info(message)
    elif failure_count < total_count:
        logger.warning(message)
    else:
        logger.error(message)

class ContextAdapter(logging.LoggerAdapter):
    """
    A logger adapter that adds contextual information to log records.
    """
    def process(self, msg, kwargs):
        # Add context to the extra dict
        kwargs.setdefault('extra', {}).update(self.extra)
        return msg, kwargs

def get_logger_with_context(name: str, context: Dict[str, Any]) -> logging.LoggerAdapter:
    """
    Get a logger with contextual information.

    Args:
        name: The name of the logger
        context: Contextual information to include in all logs from this logger

    Returns:
        A logger adapter that includes the specified context in all logs
    """
    logger = logging.getLogger(name)
    return ContextAdapter(logger, context)

@contextmanager
def log_context(**context):
    """
    Context manager that adds contextual information to logs within its scope.

    Args:
        **context: Keyword arguments representing contextual information

    Example:
        with log_context(user_id=123, action='login'):
            logger.info('User logged in')
    """
    # Get the current frame and its caller
    frame = inspect.currentframe().f_back

    # Store original extra values for all loggers
    original_extras = {}

    # Apply context to all loggers
    for name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            # Store original extra if it exists
            if hasattr(logger, 'extra'):
                original_extras[name] = logger.extra.copy()

            # Apply new context
            if hasattr(logger, 'extra'):
                logger.extra.update(context)
            else:
                logger.extra = context

    try:
        yield
    finally:
        # Restore original extra values
        for name, logger in logging.Logger.manager.loggerDict.items():
            if isinstance(logger, logging.Logger):
                if name in original_extras:
                    logger.extra = original_extras[name]
                elif hasattr(logger, 'extra'):
                    delattr(logger, 'extra')

def log_function_with_context(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that adds function call context to logs within the function.

    Args:
        func: The function to decorate

    Returns:
        A decorated function that adds context to logs

    Example:
        @log_function_with_context
        def process_user(user_id, action):
            logger.info('Processing user')  # Will include user_id and action in context
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get function signature
        sig = inspect.signature(func)

        # Bind arguments to parameters
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Create context from arguments
        context = {
            'function': func.__name__,
            'module': func.__module__,
        }

        # Add arguments to context, excluding self/cls for methods
        for param_name, param_value in bound_args.arguments.items():
            if param_name not in ('self', 'cls'):
                # Convert to string to avoid complex objects
                try:
                    context[f'arg_{param_name}'] = str(param_value)
                except:
                    context[f'arg_{param_name}'] = f"<unprintable {type(param_value).__name__}>"

        # Execute function with context
        with log_context(**context):
            return func(*args, **kwargs)

    return cast(Callable[..., T], wrapper)
