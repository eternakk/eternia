"""
String Utilities for Eternia

This module provides utility functions for common string operations in the Eternia project.
It helps reduce duplicate code and standardize string handling across the codebase.
"""

import re
from typing import List, Optional, Dict, Any, Union

def safe_format(template: str, **kwargs: Any) -> str:
    """
    Safely format a string template with the provided keyword arguments.
    
    This function is similar to str.format(), but it ignores missing keys
    instead of raising a KeyError.
    
    Args:
        template: The string template to format
        **kwargs: The keyword arguments to use for formatting
        
    Returns:
        The formatted string
    """
    class SafeDict(dict):
        def __missing__(self, key):
            return '{' + key + '}'
            
    return template.format_map(SafeDict(kwargs))

def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length, adding a suffix if truncated.
    
    Args:
        text: The string to truncate
        max_length: The maximum length of the string
        suffix: The suffix to add if the string is truncated
        
    Returns:
        The truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def snake_to_camel(snake_str: str) -> str:
    """
    Convert a snake_case string to camelCase.
    
    Args:
        snake_str: The snake_case string to convert
        
    Returns:
        The camelCase string
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake(camel_str: str) -> str:
    """
    Convert a camelCase string to snake_case.
    
    Args:
        camel_str: The camelCase string to convert
        
    Returns:
        The snake_case string
    """
    # Insert underscore before uppercase letters and convert to lowercase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def pluralize(singular: str, count: int) -> str:
    """
    Pluralize a word based on count.
    
    Args:
        singular: The singular form of the word
        count: The count to determine if the word should be pluralized
        
    Returns:
        The pluralized word if count != 1, otherwise the singular word
    """
    if count == 1:
        return singular
        
    # Simple English pluralization rules
    if singular.endswith('y') and not singular.endswith(('ay', 'ey', 'iy', 'oy', 'uy')):
        return singular[:-1] + 'ies'
    elif singular.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return singular + 'es'
    else:
        return singular + 's'

def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in a string by replacing multiple whitespace characters with a single space.
    
    Args:
        text: The string to normalize
        
    Returns:
        The normalized string
    """
    return ' '.join(text.split())

def extract_key_phrases(text: str, max_phrases: int = 5, min_word_length: int = 4) -> List[str]:
    """
    Extract key phrases from a text.
    
    This is a simple implementation that extracts phrases based on word length and frequency.
    For more sophisticated extraction, consider using NLP libraries.
    
    Args:
        text: The text to extract key phrases from
        max_phrases: The maximum number of phrases to extract
        min_word_length: The minimum length of words to consider
        
    Returns:
        A list of key phrases
    """
    # Remove punctuation and convert to lowercase
    cleaned_text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Split into words
    words = cleaned_text.split()
    
    # Filter words by length
    filtered_words = [word for word in words if len(word) >= min_word_length]
    
    # Count word frequency
    word_counts = {}
    for word in filtered_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Return top phrases
    return [word for word, count in sorted_words[:max_phrases]]

def format_list(items: List[str], conjunction: str = "and") -> str:
    """
    Format a list of items into a human-readable string.
    
    Args:
        items: The list of items to format
        conjunction: The conjunction to use for the last item
        
    Returns:
        A formatted string
    """
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    
    return ", ".join(items[:-1]) + f", {conjunction} {items[-1]}"