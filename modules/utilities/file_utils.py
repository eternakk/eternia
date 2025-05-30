"""
File Utilities for Eternia

This module provides utility functions for common file operations in the Eternia project.
It helps reduce duplicate code and standardize file handling across the codebase.
"""

import os
import json
import pickle
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypeVar, Type, Callable

T = TypeVar('T')

def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: The directory path
        
    Returns:
        The directory path as a Path object
        
    Raises:
        OSError: If the directory cannot be created
    """
    path = Path(directory) if isinstance(directory, str) else directory
    path.mkdir(parents=True, exist_ok=True)
    return path

def safe_read_file(file_path: Union[str, Path], default: str = "") -> str:
    """
    Safely read a file, returning a default value if the file does not exist.
    
    Args:
        file_path: The path to the file
        default: The default value to return if the file does not exist
        
    Returns:
        The file contents as a string, or the default value if the file does not exist
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    try:
        if path.exists():
            with open(path, 'r') as f:
                return f.read()
        return default
    except Exception as e:
        logging.error(f"Error reading file {path}: {e}")
        return default

def safe_write_file(file_path: Union[str, Path], content: str, create_dirs: bool = True) -> bool:
    """
    Safely write content to a file, creating directories if necessary.
    
    Args:
        file_path: The path to the file
        content: The content to write
        create_dirs: Whether to create directories if they don't exist
        
    Returns:
        True if the file was written successfully, False otherwise
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    try:
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        logging.error(f"Error writing to file {path}: {e}")
        return False

def load_json(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Load JSON data from a file.
    
    Args:
        file_path: The path to the JSON file
        default: The default value to return if the file does not exist or is invalid
        
    Returns:
        The parsed JSON data, or the default value if the file does not exist or is invalid
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    try:
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return default
    except Exception as e:
        logging.error(f"Error loading JSON from {path}: {e}")
        return default

def save_json(file_path: Union[str, Path], data: Any, create_dirs: bool = True, indent: int = 2) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        file_path: The path to the JSON file
        data: The data to save
        create_dirs: Whether to create directories if they don't exist
        indent: The indentation level for the JSON file
        
    Returns:
        True if the data was saved successfully, False otherwise
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    try:
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {path}: {e}")
        return False

def load_yaml(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Load YAML data from a file.
    
    Args:
        file_path: The path to the YAML file
        default: The default value to return if the file does not exist or is invalid
        
    Returns:
        The parsed YAML data, or the default value if the file does not exist or is invalid
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    try:
        if path.exists():
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        return default
    except Exception as e:
        logging.error(f"Error loading YAML from {path}: {e}")
        return default

def save_yaml(file_path: Union[str, Path], data: Any, create_dirs: bool = True) -> bool:
    """
    Save data to a YAML file.
    
    Args:
        file_path: The path to the YAML file
        data: The data to save
        create_dirs: Whether to create directories if they don't exist
        
    Returns:
        True if the data was saved successfully, False otherwise
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    try:
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        return True
    except Exception as e:
        logging.error(f"Error saving YAML to {path}: {e}")
        return False

def load_pickle(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Load pickled data from a file.
    
    Args:
        file_path: The path to the pickle file
        default: The default value to return if the file does not exist or is invalid
        
    Returns:
        The unpickled data, or the default value if the file does not exist or is invalid
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    try:
        if path.exists():
            with open(path, 'rb') as f:
                return pickle.load(f)
        return default
    except Exception as e:
        logging.error(f"Error loading pickle from {path}: {e}")
        return default

def save_pickle(file_path: Union[str, Path], data: Any, create_dirs: bool = True) -> bool:
    """
    Save data to a pickle file.
    
    Args:
        file_path: The path to the pickle file
        data: The data to save
        create_dirs: Whether to create directories if they don't exist
        
    Returns:
        True if the data was saved successfully, False otherwise
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    try:
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        return True
    except Exception as e:
        logging.error(f"Error saving pickle to {path}: {e}")
        return False

def find_files(directory: Union[str, Path], pattern: str = "*", recursive: bool = True) -> List[Path]:
    """
    Find files in a directory that match a pattern.
    
    Args:
        directory: The directory to search in
        pattern: The glob pattern to match
        recursive: Whether to search recursively
        
    Returns:
        A list of matching file paths
    """
    path = Path(directory) if isinstance(directory, str) else directory
    
    if recursive:
        return list(path.glob(f"**/{pattern}"))
    else:
        return list(path.glob(pattern))

def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: The path to the file
        
    Returns:
        The size of the file in bytes, or 0 if the file does not exist
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    try:
        if path.exists() and path.is_file():
            return path.stat().st_size
        return 0
    except Exception as e:
        logging.error(f"Error getting file size for {path}: {e}")
        return 0

def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: The path to the file
        
    Returns:
        The file extension (without the dot)
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    return path.suffix.lstrip('.')