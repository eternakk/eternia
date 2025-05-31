"""
Utilities Package for Eternia

This package provides utility functions and classes for common tasks in the Eternia project.
It helps reduce duplicate code and standardize common patterns across the codebase.

Available modules:
- config_utils: Utilities for safely retrieving and validating configuration values
- logging_utils: Utilities for standardized logging
- string_utils: Utilities for common string operations
- file_utils: Utilities for common file operations
"""

from modules.utilities.config_utils import (
    get_config_value,
    get_config_dict,
    get_config_list,
    get_config_section_items,
    iterate_config_section
)

from modules.utilities.logging_utils import (
    log_function_entry_exit,
    log_operation,
    get_module_logger,
    log_config_operation,
    log_batch_operation
)

from modules.utilities.string_utils import (
    safe_format,
    truncate,
    snake_to_camel,
    camel_to_snake,
    pluralize,
    normalize_whitespace,
    extract_key_phrases,
    format_list
)

from modules.utilities.file_utils import (
    ensure_directory_exists,
    safe_read_file,
    safe_write_file,
    load_json,
    save_json,
    load_yaml,
    save_yaml,
    load_pickle,
    save_pickle,
    find_files,
    get_file_size,
    get_file_extension
)

__all__ = [
    # Configuration utilities
    'get_config_value',
    'get_config_dict',
    'get_config_list',
    'get_config_section_items',
    'iterate_config_section',

    # Logging utilities
    'log_function_entry_exit',
    'log_operation',
    'get_module_logger',
    'log_config_operation',
    'log_batch_operation',

    # String utilities
    'safe_format',
    'truncate',
    'snake_to_camel',
    'camel_to_snake',
    'pluralize',
    'normalize_whitespace',
    'extract_key_phrases',
    'format_list',

    # File utilities
    'ensure_directory_exists',
    'safe_read_file',
    'safe_write_file',
    'load_json',
    'save_json',
    'load_yaml',
    'save_yaml',
    'load_pickle',
    'save_pickle',
    'find_files',
    'get_file_size',
    'get_file_extension'
]