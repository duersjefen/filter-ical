"""
Pure Calendar Business Logic - Rich Hickey Style
Pure functions that validate and transform calendar data
No side effects, no classes, explicit data flow
"""

import re
from typing import Tuple, Dict, Any, List
from ..models import CalendarEntry


# === URL VALIDATION (Pure Functions) ===

def is_valid_url_format(url: str) -> bool:
    """Pure function: check if URL has valid format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def is_valid_ical_content(content: str) -> Tuple[bool, str]:
    """Pure function: validate iCal content structure"""
    if not content.strip():
        return False, "Empty response"
    
    content_lower = content.lower()
    
    if 'begin:vcalendar' not in content_lower:
        return False, "Not a valid iCal file (missing VCALENDAR)"
    
    if 'version:2.0' not in content_lower:
        return False, "Not iCal version 2.0"
    
    if 'begin:vevent' not in content_lower:
        return False, "iCal file contains no events"
    
    return True, "Valid iCal content"


def validate_calendar_data(name: str, url: str) -> Tuple[bool, str]:
    """Pure function: validate calendar creation data"""
    if not name or not name.strip():
        return False, "Calendar name is required"
    
    if not url or not url.strip():
        return False, "Calendar URL is required"
    
    if not is_valid_url_format(url):
        return False, "Invalid URL format"
    
    return True, "Valid calendar data"


def user_owns_calendar(calendar: CalendarEntry, user_id: str) -> bool:
    """Pure function: check if user owns calendar"""
    return calendar.user_id == user_id


# === CALENDAR OPERATIONS (Pure Functions) ===

def find_calendar_by_id(calendars: List[CalendarEntry], calendar_id: str) -> CalendarEntry:
    """Pure function: find calendar by ID in list"""
    return next((cal for cal in calendars if cal.id == calendar_id), None)


def filter_calendars_by_user(calendars: List[CalendarEntry], user_id: str) -> List[CalendarEntry]:
    """Pure function: filter calendars for specific user"""
    return [cal for cal in calendars if cal.user_id == user_id]


def calendar_to_dict(calendar: CalendarEntry) -> Dict[str, Any]:
    """Pure function: convert calendar to API response format"""
    return {
        "id": calendar.id,
        "name": calendar.name,
        "url": calendar.url
    }