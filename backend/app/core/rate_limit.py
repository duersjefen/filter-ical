"""
Rate limiting configuration.

Centralized rate limiter to avoid circular imports.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Global rate limiter instance
limiter = Limiter(key_func=get_remote_address)
