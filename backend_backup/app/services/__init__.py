"""
Services Package - Pure event processing functions
Legacy module for backward compatibility
"""

from .events import (
    fetch_ical_events, 
    parse_ical_content, 
    extract_category_from_event,
    generate_ical_content
)

__all__ = [
    'fetch_ical_events',
    'parse_ical_content',
    'extract_category_from_event',
    'generate_ical_content'
]