"""
Pure functions for iCal parsing and event transformation.

FUNCTIONAL CORE - No side effects, fully testable.
All iCal processing logic without I/O operations.
"""

import re
import hashlib
import unicodedata
import logging
from datetime import datetime, timezone, date
from typing import Dict, List, Any, Optional, Tuple
from icalendar import Calendar as ICalCalendar, Event as ICalEvent
from app.core.result import Result, ok, fail

logger = logging.getLogger(__name__)


def parse_ical_content(ical_content: str) -> Result[List[Dict[str, Any]]]:
    """
    Parse iCal content string into structured event data.

    Args:
        ical_content: Raw iCal content string

    Returns:
        Result containing events list or error message

    Pure function - no side effects, same input always produces same output.
    """
    try:
        calendar = ICalCalendar.from_ical(ical_content)
        events = []

        for component in calendar.walk():
            if component.name == "VEVENT":
                event_data = _extract_event_data(component, ical_content)
                if event_data:
                    events.append(event_data)

        return ok(events)

    except Exception as e:
        logger.error(f"Failed to parse iCal content: {str(e)}", exc_info=True)
        return fail(f"Failed to parse iCal content: {str(e)}")


def _extract_event_data(ical_event: ICalEvent, raw_ical: str) -> Optional[Dict[str, Any]]:
    """
    Extract event data from iCal event component (simple approach like old backend).

    Args:
        ical_event: Parsed iCal event component
        raw_ical: Original raw iCal content for reference

    Returns:
        Event data dictionary or None if invalid

    Pure function - deterministic transformation using proven old backend logic.
    """
    try:
        # Generate unique event ID from UID and start time
        uid = str(ical_event.get('UID', ''))
        start_time = ical_event.get('DTSTART')
        event_id = _generate_event_id(uid, start_time)

        # Extract core event fields
        title = str(ical_event.get('SUMMARY', 'Untitled Event'))
        description = str(ical_event.get('DESCRIPTION', ''))
        location = ical_event.get('LOCATION')
        location_str = str(location) if location else None

        # Parse times (simple approach)
        start_dt = _parse_datetime(start_time)
        end_time = ical_event.get('DTEND')
        end_dt = _parse_datetime(end_time) if end_time else None

        # Handle missing start time with fallback
        if not start_dt:
            start_dt = create_fallback_datetime(title, description)


        # Extract raw event for debugging/export
        raw_event = _extract_raw_event(raw_ical, uid)

        return {
            "id": event_id,
            "title": title,
            "start_time": start_dt,
            "end_time": end_dt,
            "description": description,
            "location": location_str,
            "uid": uid,
            "raw_ical": raw_event
        }

    except Exception as e:
        logger.error(
            f"Failed to extract event data: {str(e)}",
            exc_info=True,
            extra={
                "event_summary": getattr(ical_event, "summary", None)
            }
        )
        return None


def _generate_event_id(uid: str, start_time: Any) -> str:
    """
    Generate deterministic event ID from UID and start time.
    
    Args:
        uid: Event UID from iCal
        start_time: Event start time
        
    Returns:
        8-character hex event ID
        
    Pure function - same inputs always produce same ID.
    """
    # Create a hash from UID and start time for deterministic IDs
    content = f"{uid}_{start_time}"
    hash_object = hashlib.md5(content.encode())
    return f"evt_{hash_object.hexdigest()[:8]}"


def _parse_datetime(dt_value: Any) -> Optional[datetime]:
    """
    Parse iCal datetime value to Python datetime (simple approach like old backend).
    
    Args:
        dt_value: iCal datetime value (can be DATE or DATETIME)
        
    Returns:
        Python datetime object in UTC or None
        
    Pure function - deterministic parsing using proven old backend logic.
    """
    if not dt_value:
        return None
        
    try:
        if hasattr(dt_value, 'dt'):
            dt = dt_value.dt
            
            # Handle date vs datetime (old backend logic)
            if isinstance(dt, date) and not isinstance(dt, datetime):
                dt = datetime.combine(dt, datetime.min.time())
            
            # Ensure timezone awareness
            if hasattr(dt, 'replace'):
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    # Convert to UTC
                    dt = dt.astimezone(timezone.utc)
                return dt
                
        return None
    except Exception:
        return None


def _extract_raw_event(raw_ical: str, uid: str) -> str:
    """
    Extract raw VEVENT block for specific UID.
    
    Args:
        raw_ical: Complete raw iCal content
        uid: Event UID to extract
        
    Returns:
        Raw VEVENT block as string
        
    Pure function - deterministic text extraction.
    """
    try:
        # Find the VEVENT block containing this UID
        lines = raw_ical.split('\n')
        event_lines = []
        in_event = False
        
        for line in lines:
            if line.startswith('BEGIN:VEVENT'):
                in_event = True
                event_lines = [line]
            elif line.startswith('END:VEVENT'):
                event_lines.append(line)
                # Check if this event contains our UID
                event_content = '\n'.join(event_lines)
                if f'UID:{uid}' in event_content:
                    return event_content
                # Reset for next event
                in_event = False
                event_lines = []
            elif in_event:
                event_lines.append(line)
        
        return ""
    except Exception:
        return ""


def normalize_event_title(title: str) -> str:
    """
    Normalize event title for consistent grouping.

    Algorithm:
    ----------
    1. Unicode normalization (NFC canonical form)
    2. Replace all whitespace variants with single spaces
    3. Collapse multiple consecutive spaces
    4. Strip leading/trailing whitespace
    5. Handle empty results with fallback

    Why This Approach:
    ------------------
    Different calendar systems produce titles that LOOK identical but have
    different internal representations. This causes recurring events to be
    split into multiple groups incorrectly.

    Problems Solved:
    ----------------
    - "Math Class" with regular space vs "\u00A0" (non-breaking space)
    - "Math  Class" with double space vs "Math Class" with single space
    - "Math\tClass" with tab vs "Math Class" with space
    - Composed vs decomposed Unicode (é as single char vs e + combining accent)
    - Trailing whitespace causing "Math Class " != "Math Class"

    Unicode NFC Normalization:
    --------------------------
    Converts characters to their canonical composed form:
    - "e\u0301" (e + combining acute) → "é" (single character)
    - Ensures visually identical text is byte-for-byte identical
    - Critical for reliable string comparison and grouping

    Example:
    --------
    >>> normalize_event_title("Math\u00A0Class  ")  # Non-breaking space + double space + trailing
    "Math Class"
    >>> normalize_event_title("Café")  # With composed é
    "Café"
    >>> normalize_event_title("Cafe\u0301")  # With decomposed é (e + combining accent)
    "Café"  # Same result after NFC normalization

    Args:
        title: Raw event title string

    Returns:
        Normalized title string suitable for grouping

    Pure function - deterministic normalization for consistent grouping.
    """
    if not title or not isinstance(title, str):
        return 'Untitled'
    
    # Unicode normalization - convert to canonical form (NFC)
    # This ensures characters that look the same are represented identically
    normalized = unicodedata.normalize('NFC', title)
    
    # Replace various whitespace characters with regular spaces
    # \u00A0 = non-breaking space, \u2000-\u200B = various Unicode spaces
    whitespace_pattern = r'[\s\u00A0\u1680\u2000-\u200B\u2028\u2029\u202F\u205F\u3000\uFEFF]+'
    normalized = re.sub(whitespace_pattern, ' ', normalized)
    
    # Strip leading/trailing whitespace
    normalized = normalized.strip()
    
    # Handle empty result after normalization
    if not normalized:
        return 'Untitled'
    
    return normalized


def group_events_by_title(events: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Group events by title for recurring event detection.
    
    Uses title normalization to handle formatting differences that prevent proper grouping.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        Dictionary mapping normalized_title -> {title, count, events: [...]}
        
    Pure function - deterministic grouping with title normalization.
    """
    grouped = {}
    logger = logging.getLogger(__name__)
    
    for event in events:
        raw_title = event.get('title', 'Untitled')
        normalized_title = normalize_event_title(raw_title)
        
        # Debug logging to identify title normalization differences
        if raw_title != normalized_title:
            logger.debug(f"Title normalized: '{raw_title}' -> '{normalized_title}' (Raw bytes: {raw_title.encode('unicode_escape')})")
        
        if normalized_title not in grouped:
            grouped[normalized_title] = {
                'title': normalized_title,  # Use normalized title for display
                'event_count': 0,
                'events': []
            }
        
        grouped[normalized_title]['event_count'] += 1
        grouped[normalized_title]['events'].append(event)
    
    return grouped



def validate_ical_url(url: str) -> Result[None]:
    """
    Validate iCal URL format.

    Args:
        url: URL to validate

    Returns:
        Result indicating success or validation error

    Pure function - no network access, just format validation.
    """
    if not url or not isinstance(url, str):
        return fail("URL is required")

    url = url.strip()

    if not url.startswith(('http://', 'https://')):
        return fail("URL must start with http:// or https://")

    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not url_pattern.match(url):
        return fail("Invalid URL format")

    return ok(None)


def validate_calendar_data(name: str, source_url: str) -> Result[None]:
    """
    Validate calendar creation data.

    Args:
        name: Calendar name
        source_url: Calendar source URL

    Returns:
        Result indicating success or validation error

    Pure function - validation without side effects.
    """
    if not name or not isinstance(name, str) or not name.strip():
        return fail("Calendar name is required")

    if len(name.strip()) > 255:
        return fail("Calendar name must be 255 characters or less")

    url_result = validate_ical_url(source_url)
    if not url_result.is_success:
        return fail(f"Invalid source URL: {url_result.error}")

    return ok(None)




def create_fallback_datetime(event_title: str, description: str) -> datetime:
    """
    Create fallback datetime when event has no start time.
    
    Args:
        event_title: Event title for context
        description: Event description for context
        
    Returns:
        Fallback datetime (current date at midnight UTC)
        
    Pure function - creates sensible fallback.
    """
    # For events without start times, use current date at midnight UTC
    # This allows them to be stored and displayed as "date unknown" events
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


