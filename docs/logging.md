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

## Log Levels

The logging system uses the following log levels, in order of increasing severity:

1. DEBUG: Detailed information, typically useful only for diagnosing problems
2. INFO: Confirmation that things are working as expected
3. WARNING: An indication that something unexpected happened, or may happen in the near future
4. ERROR: Due to a more serious problem, the software has not been able to perform some function
5. CRITICAL: A serious error, indicating that the program itself may be unable to continue running

## Examples

Here are some examples of how the logging system is used in the Eternia project:

```python
# In modules/runtime.py
self.logger.info(f"🌀 Runtime Cycle {self.cycle_count}")
self.logger.warning(f"⚠️ No physics profile found for zone: {zone_name}")

# In modules/governor.py
self.logger.info(f"Event: {event}, Payload: {payload}")

# In modules/alignement.py
self.logger.warning(f"🚨 AlignmentGovernor: Action blocked by rule: {rule.__name__}")
```