import logging
import logging.handlers
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

class StructuredLogFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in a structured format.
    Includes contextual information from the 'extra' parameter.
    """
    def format(self, record):
        # Base fields
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        # Location
        self._add_location(log_record, record)
        # Exception
        self._add_exception(log_record, record)
        # Extra context
        self._add_extra_context(log_record, record)
        # Output
        return self._to_output(log_record)

    # --- helpers to reduce cyclomatic complexity ---
    def _add_location(self, log_record: Dict[str, Any], record: logging.LogRecord) -> None:
        if getattr(record, 'pathname', None):
            log_record['file'] = record.pathname
            log_record['line'] = record.lineno
            log_record['function'] = record.funcName

    def _add_exception(self, log_record: Dict[str, Any], record: logging.LogRecord) -> None:
        if getattr(record, 'exc_info', None):
            log_record['exception'] = self.formatException(record.exc_info)

    def _add_extra_context(self, log_record: Dict[str, Any], record: logging.LogRecord) -> None:
        exclude = {
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename', 'funcName',
            'id', 'levelname', 'levelno', 'lineno', 'module', 'msecs', 'message', 'msg', 'name',
            'pathname', 'process', 'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'
        }
        for key, value in record.__dict__.items():
            if key not in exclude:
                log_record[key] = value

    def _to_output(self, log_record: Dict[str, Any]) -> str:
        if self.datefmt == 'json':
            return json.dumps(log_record)
        # human readable
        parts = [
            f"{log_record['timestamp']} | {log_record['level']:<8} | {log_record['logger']} | {log_record['message']}"
        ]
        context_items = [
            f"{k}={v}" for k, v in log_record.items()
            if k not in ['timestamp', 'level', 'logger', 'message']
        ]
        if context_items:
            parts.append(" | " + " ".join(context_items))
        return "".join(parts)

# Configure root logger
def configure_logging(level=logging.INFO):
    """
    Configure the logging system for the Eternia project.

    Args:
        level: The minimum logging level to capture (default: INFO)
    """
    # Create formatter
    formatter = StructuredLogFormatter(
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear any existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    # File handler for general logs
    file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "eternia.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)

    # Create specialized loggers

    # Runtime cycles logger
    cycles_logger = logging.getLogger("eternia.cycles")
    cycles_handler = logging.FileHandler(logs_dir / "eterna_cycles.log")
    cycles_handler.setFormatter(logging.Formatter('%(message)s'))
    cycles_logger.addHandler(cycles_handler)
    cycles_logger.propagate = False  # Don't propagate to root logger

    # Governor events logger
    governor_logger = logging.getLogger("eternia.governor")
    governor_handler = logging.FileHandler(logs_dir / "governor_events.log")
    governor_handler.setFormatter(formatter)
    governor_logger.addHandler(governor_handler)
    governor_logger.propagate = True  # Also log to root logger

    # Debug logger with more detailed information
    debug_logger = logging.getLogger("eternia.debug")
    debug_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "debug.log",
        maxBytes=20 * 1024 * 1024,  # 20 MB
        backupCount=3
    )
    debug_handler.setFormatter(formatter)
    debug_handler.setLevel(logging.DEBUG)
    debug_logger.addHandler(debug_handler)
    debug_logger.propagate = False  # Don't propagate to root logger

    logging.info("Logging system initialized")

# Get loggers for different components
def get_logger(name):
    """
    Get a logger for a specific component.

    Args:
        name: The name of the component (e.g., 'runtime', 'governor', 'physics')

    Returns:
        A configured logger instance
    """
    return logging.getLogger(f"eternia.{name}")

# Initialize logging with default settings
configure_logging()
