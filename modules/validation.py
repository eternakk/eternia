"""
Validation Module for Eternia

This module provides validation functions and custom exceptions for input validation
throughout the Eternia project. It helps ensure that functions receive valid inputs
and provides meaningful error messages when validation fails.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypeVar, Type, Callable

# Custom exceptions
class ValidationError(Exception):
    """Base exception for all validation errors."""
    pass

class TypeValidationError(ValidationError):
    """Exception raised when a value has an incorrect type."""
    def __init__(self, param_name: str, expected_type: Union[Type, List[Type]], actual_type: Type):
        self.param_name = param_name
        self.expected_type = expected_type
        self.actual_type = actual_type
        
        if isinstance(expected_type, list):
            expected_type_str = " or ".join([t.__name__ for t in expected_type])
        else:
            expected_type_str = expected_type.__name__
            
        message = f"Parameter '{param_name}' should be of type {expected_type_str}, but got {actual_type.__name__}"
        super().__init__(message)

class ValueValidationError(ValidationError):
    """Exception raised when a value is invalid (e.g., negative number, empty string)."""
    def __init__(self, param_name: str, message: str):
        self.param_name = param_name
        full_message = f"Invalid value for parameter '{param_name}': {message}"
        super().__init__(full_message)

class ExistenceValidationError(ValidationError):
    """Exception raised when a required resource (file, directory, etc.) does not exist."""
    def __init__(self, resource_type: str, resource_path: Union[str, Path], message: Optional[str] = None):
        self.resource_type = resource_type
        self.resource_path = resource_path
        
        if message:
            full_message = f"{resource_type} '{resource_path}' does not exist: {message}"
        else:
            full_message = f"{resource_type} '{resource_path}' does not exist"
            
        super().__init__(full_message)

class SchemaValidationError(ValidationError):
    """Exception raised when data does not conform to an expected schema."""
    def __init__(self, data_name: str, message: str):
        self.data_name = data_name
        full_message = f"Schema validation failed for '{data_name}': {message}"
        super().__init__(full_message)

# Type validation functions
T = TypeVar('T')

def validate_type(value: Any, expected_type: Union[Type[T], List[Type]], param_name: str) -> T:
    """
    Validate that a value is of the expected type.
    
    Args:
        value: The value to validate
        expected_type: The expected type or list of types
        param_name: The name of the parameter being validated
        
    Returns:
        The validated value
        
    Raises:
        TypeValidationError: If the value is not of the expected type
    """
    if isinstance(expected_type, list):
        if not any(isinstance(value, t) for t in expected_type):
            raise TypeValidationError(param_name, expected_type, type(value))
    elif not isinstance(value, expected_type):
        raise TypeValidationError(param_name, expected_type, type(value))
    
    return value

# Value validation functions
def validate_non_empty_string(value: str, param_name: str) -> str:
    """
    Validate that a string is not empty.
    
    Args:
        value: The string to validate
        param_name: The name of the parameter being validated
        
    Returns:
        The validated string
        
    Raises:
        TypeValidationError: If the value is not a string
        ValueValidationError: If the string is empty
    """
    validate_type(value, str, param_name)
    
    if not value:
        raise ValueValidationError(param_name, "String cannot be empty")
    
    return value

def validate_positive_number(value: Union[int, float], param_name: str) -> Union[int, float]:
    """
    Validate that a number is positive.
    
    Args:
        value: The number to validate
        param_name: The name of the parameter being validated
        
    Returns:
        The validated number
        
    Raises:
        TypeValidationError: If the value is not a number
        ValueValidationError: If the number is not positive
    """
    validate_type(value, [int, float], param_name)
    
    if value <= 0:
        raise ValueValidationError(param_name, "Number must be positive")
    
    return value

def validate_non_negative_number(value: Union[int, float], param_name: str) -> Union[int, float]:
    """
    Validate that a number is non-negative.
    
    Args:
        value: The number to validate
        param_name: The name of the parameter being validated
        
    Returns:
        The validated number
        
    Raises:
        TypeValidationError: If the value is not a number
        ValueValidationError: If the number is negative
    """
    validate_type(value, [int, float], param_name)
    
    if value < 0:
        raise ValueValidationError(param_name, "Number cannot be negative")
    
    return value

# Existence validation functions
def validate_file_exists(file_path: Union[str, Path], param_name: str) -> Path:
    """
    Validate that a file exists.
    
    Args:
        file_path: The path to the file
        param_name: The name of the parameter being validated
        
    Returns:
        The validated file path as a Path object
        
    Raises:
        TypeValidationError: If the file_path is not a string or Path
        ExistenceValidationError: If the file does not exist
    """
    validate_type(file_path, [str, Path], param_name)
    
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    if not path.is_file():
        raise ExistenceValidationError("File", path)
    
    return path

def validate_directory_exists(dir_path: Union[str, Path], param_name: str) -> Path:
    """
    Validate that a directory exists.
    
    Args:
        dir_path: The path to the directory
        param_name: The name of the parameter being validated
        
    Returns:
        The validated directory path as a Path object
        
    Raises:
        TypeValidationError: If the dir_path is not a string or Path
        ExistenceValidationError: If the directory does not exist
    """
    validate_type(dir_path, [str, Path], param_name)
    
    path = Path(dir_path) if isinstance(dir_path, str) else dir_path
    
    if not path.is_dir():
        raise ExistenceValidationError("Directory", path)
    
    return path

# Schema validation functions
def validate_dict_has_keys(data: Dict[str, Any], required_keys: List[str], data_name: str) -> Dict[str, Any]:
    """
    Validate that a dictionary has all the required keys.
    
    Args:
        data: The dictionary to validate
        required_keys: The list of required keys
        data_name: The name of the data being validated
        
    Returns:
        The validated dictionary
        
    Raises:
        TypeValidationError: If the data is not a dictionary
        SchemaValidationError: If the dictionary is missing required keys
    """
    validate_type(data, dict, data_name)
    
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        raise SchemaValidationError(data_name, f"Missing required keys: {', '.join(missing_keys)}")
    
    return data

def validate_list_non_empty(data: List[Any], data_name: str) -> List[Any]:
    """
    Validate that a list is not empty.
    
    Args:
        data: The list to validate
        data_name: The name of the data being validated
        
    Returns:
        The validated list
        
    Raises:
        TypeValidationError: If the data is not a list
        SchemaValidationError: If the list is empty
    """
    validate_type(data, list, data_name)
    
    if not data:
        raise SchemaValidationError(data_name, "List cannot be empty")
    
    return data

# Decorator for validating function parameters
def validate_params(**validators: Callable[[Any, str], Any]):
    """
    Decorator for validating function parameters.
    
    Args:
        validators: A dictionary mapping parameter names to validator functions
        
    Returns:
        A decorator function
        
    Example:
        @validate_params(
            name=lambda v, p: validate_non_empty_string(v, p),
            age=lambda v, p: validate_positive_number(v, p)
        )
        def create_user(name, age):
            # Function implementation
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Get the parameter names from the function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    bound_args.arguments[param_name] = validator(value, param_name)
            
            # Call the function with the validated parameters
            return func(*bound_args.args, **bound_args.kwargs)
        
        return wrapper
    
    return decorator