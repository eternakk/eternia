# Logging System Documentation

## Overview

The Eternia project uses a comprehensive logging system based on Python's built-in `logging` module. This system provides structured logging with appropriate log levels, timestamps, and component names, making it easier to debug issues and monitor the application's behavior.

## Configuration

The logging system is configured in the `modules/logging_config.py` file, which provides:

1. A root logger that logs to both console and a rotating file
2. Specialized loggers for different components (cycles, governor, debug)
3. A convenient function to get loggers for specific components
4. Proper log formatting with timestamps, log levels, and component names
5. Log rotation to prevent log files from growing too large

## Log Files

The logging system creates several log files:

- `logs/eternia.log`: The main log file containing all log messages
- `logs/eterna_cycles.log`: A specialized log file for cycle information
- `logs/governor_events.log`: A specialized log file for governor events
- `logs/debug.log`: A detailed log file for debugging purposes

## Usage

To use the logging system in your code:

1. Import the `get_logger` function from `modules/logging_config.py`:
   ```python
   from modules.logging_config import get_logger
   ```

2. Create a logger instance for your component:
   ```python
   logger = get_logger("your_component_name")
   ```

3. Use the logger to log messages with appropriate log levels:
   ```python
   logger.debug("Detailed information for debugging")
   logger.info("General information about program execution")
   logger.warning("Warning about potential issues")
   logger.error("Error that doesn't prevent the program from running")
   logger.critical("Critical error that may prevent the program from running")
   ```

4. Add contextual information to your logs using the `extra` parameter:
   ```python
   logger.info("User logged in", extra={"user_id": 123, "ip_address": "192.168.1.1"})
   ```

5. For more advanced logging with context, use the utility functions in `modules/utilities/logging_utils.py`:
   ```python
   from modules.utilities.logging_utils import log_operation, log_function_with_context

   # Log an operation with context
   log_operation(
       operation="user_login",
       success=True,
       details={"user_id": 123},
       context={"ip_address": "192.168.1.1"}
   )

   # Add context to all logs within a function
   @log_function_with_context
   def process_user(user_id, action):
       logger.info("Processing user")  # Will include user_id and action in context
   ```

## Log Levels

The logging system uses the following log levels, in order of increasing severity:

1. DEBUG: Detailed information, typically useful only for diagnosing problems
2. INFO: Confirmation that things are working as expected
3. WARNING: An indication that something unexpected happened, or may happen in the near future
4. ERROR: Due to a more serious problem, the software has not been able to perform some function
5. CRITICAL: A serious error, indicating that the program itself may be unable to continue running

## Structured Logging

The Eternia project uses structured logging to provide more context and make logs more searchable and analyzable. Structured logging adds key-value pairs to log messages, which can be used for filtering, searching, and analysis.

### Benefits of Structured Logging

1. **Improved Searchability**: Easily search for logs with specific context values
2. **Better Debugging**: More context means faster problem identification
3. **Analytics**: Structured data can be analyzed to identify patterns and trends
4. **Monitoring**: Structured logs can be used to trigger alerts based on specific conditions

### Using Structured Logging

The `StructuredLogFormatter` in `logging_config.py` formats logs with contextual information. When using the `extra` parameter, the key-value pairs are added to the log record and included in the output.

```python
# Basic structured logging
logger.info("Processing order", extra={"order_id": "12345", "customer_id": "C789"})

# Using context manager for multiple log statements
from modules.utilities.logging_utils import log_context

with log_context(order_id="12345", customer_id="C789"):
    logger.info("Starting order processing")
    # ... processing code ...
    logger.info("Order processing completed")  # Both logs include the context
```

### Utility Functions for Structured Logging

The `logging_utils.py` module provides several utility functions and decorators for structured logging:

1. **log_operation**: Log an operation with standardized format and context
2. **log_batch_operation**: Log batch operations with success rates and context
3. **log_function_entry_exit**: Decorator to log function entry and exit with context
4. **log_function_with_context**: Decorator that adds function arguments as context
5. **get_logger_with_context**: Get a logger that always includes specific context
6. **log_context**: Context manager for adding context to all logs within a block

## Examples

Here are some examples of how the logging system is used in the Eternia project:

```python
# Basic logging
# In modules/runtime.py
self.logger.info(f"🌀 Runtime Cycle {self.cycle_count}")
self.logger.warning(f"⚠️ No physics profile found for zone: {zone_name}")

# Structured logging
# In modules/governor.py
self.logger.info("Event received", extra={"event": event, "payload": payload})

# Using utility functions
# In modules/alignment.py
from modules.utilities.logging_utils import log_operation

log_operation(
    operation="rule_enforcement",
    success=False,
    details={"rule": rule.__name__, "action": action_name},
    context={"agent_id": agent_id, "zone_id": zone_id}
)
```
