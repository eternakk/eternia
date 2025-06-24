"""
Shared rate limiter module for consistent rate limiting across the application.

This module provides a single instance of the Limiter class that can be imported
and used by all router files to ensure consistent rate limiting.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create a single shared limiter instance with memory storage
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",  # Use memory storage for simplicity, can be changed to Redis for production
    strategy="fixed-window",  # Use fixed window strategy for more predictable rate limiting
)