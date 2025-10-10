"""
Pure functions for calendar data operations and transformations.

FUNCTIONAL CORE - No side effects, fully testable.
All calendar business logic without I/O operations.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple


def create_calendar_data(name: str, source_url: str, calendar_type: str = "user",
                        user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Create new calendar data structure.

    Args:
        name: Calendar name
        source_url: iCal source URL
        calendar_type: "user" or "domain"
        user_id: User ID for user scoping

    Returns:
        Calendar data dictionary

    Note: domain_key is no longer stored in calendars table.
    It's now in domain_auth table (see migration a1b2c3d4e5f6).

    Pure function - creates new data without side effects.
    """
    now = datetime.now(timezone.utc)

    return {
        "name": name.strip(),
        "source_url": source_url.strip(),
        "type": calendar_type,
        "user_id": user_id,
        "last_fetched": None,
        "created_at": now,
        "updated_at": now
    }


def update_calendar_data(calendar_data: Dict[str, Any], **updates) -> Dict[str, Any]:
    """
    Update calendar data with new values.
    
    Args:
        calendar_data: Existing calendar data
        **updates: Fields to update
        
    Returns:
        New calendar data dictionary with updates
        
    Pure function - returns new object, never mutates input.
    """
    now = datetime.now(timezone.utc)
    
    # Create new calendar data with updates
    updated_calendar = {**calendar_data}
    updated_calendar.update(updates)
    updated_calendar["updated_at"] = now
    
    return updated_calendar


def mark_calendar_fetched(calendar_data: Dict[str, Any], fetch_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Mark calendar as fetched at given time.
    
    Args:
        calendar_data: Calendar data
        fetch_time: When calendar was fetched (defaults to now)
        
    Returns:
        New calendar data with updated fetch time
        
    Pure function - creates new data structure.
    """
    if fetch_time is None:
        fetch_time = datetime.now(timezone.utc)
    
    return update_calendar_data(calendar_data, last_fetched=fetch_time)


def create_event_data(calendar_id: Any, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create event data structure for database storage (simple approach like old backend).
    
    Args:
        calendar_id: ID of parent calendar
        event_data: Parsed event data from iCal
        
    Returns:
        Event data ready for database
        
    Pure function - transforms data structure.
    """
    now = datetime.now(timezone.utc)
    
    return {
        "calendar_id": calendar_id,
        "title": event_data.get("title", ""),
        "start_time": event_data.get("start_time"),
        "end_time": event_data.get("end_time"),
        "description": event_data.get("description", ""),
        "location": event_data.get("location"),
        "uid": event_data.get("uid", ""),
        "other_ical_fields": {
            "raw_ical": event_data.get("raw_ical", "")
        },
        "created_at": now,
        "updated_at": now
    }


def filter_events_by_date_range(events: List[Dict[str, Any]], 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Filter events by date range.
    
    Args:
        events: List of event dictionaries
        start_date: Filter events after this date
        end_date: Filter events before this date
        
    Returns:
        Filtered list of events
        
    Pure function - returns new list.
    """
    filtered = []
    
    for event in events:
        event_start = event.get("start_time")
        if not event_start:
            continue
            
        # Convert to datetime if needed
        if isinstance(event_start, str):
            try:
                event_start = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
            except ValueError:
                continue
        
        # Apply date filters
        if start_date and event_start < start_date:
            continue
        if end_date and event_start > end_date:
            continue
            
        filtered.append(event)
    
    return filtered


def sort_events_by_start_time(events: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Sort events by start time.
    
    Args:
        events: List of event dictionaries
        reverse: Sort in descending order if True
        
    Returns:
        New sorted list of events
        
    Pure function - returns new list.
    """
    def get_start_time(event):
        start_time = event.get("start_time")
        if not start_time:
            return datetime.min.replace(tzinfo=timezone.utc)
        
        if isinstance(start_time, str):
            try:
                return datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                return datetime.min.replace(tzinfo=timezone.utc)
        
        return start_time
    
    return sorted(events, key=get_start_time, reverse=reverse)


def create_filter_data(name: str, calendar_id: Optional[int] = None,
                      domain_key: Optional[str] = None, user_id: Optional[int] = None,
                      subscribed_event_ids: Optional[List[int]] = None,
                      subscribed_group_ids: Optional[List[int]] = None,
                      unselected_event_ids: Optional[List[str]] = None,
                      include_future_events: Optional[bool] = None) -> Dict[str, Any]:
    """
    Create filter data structure.

    Args:
        name: Filter name
        calendar_id: Calendar ID for user filters
        domain_key: Domain key for domain filters
        user_id: User ID for user scoping
        subscribed_event_ids: List of event IDs/titles to include
        subscribed_group_ids: List of group IDs to include (domain filters only)
        unselected_event_ids: List of event titles to exclude from groups (domain filters only)
        include_future_events: Include future recurring events (personal calendars only)

    Returns:
        Filter data dictionary

    Pure function - creates new data structure.
    """
    now = datetime.now(timezone.utc)
    link_uuid = str(uuid.uuid4())

    # Only set include_future_events for personal calendars
    if calendar_id and not domain_key:
        include_future = include_future_events if include_future_events is not None else False
    else:
        include_future = None  # Domain filters don't use this

    return {
        "name": name.strip(),
        "calendar_id": calendar_id,
        "domain_key": domain_key,
        "user_id": user_id,
        "subscribed_event_ids": subscribed_event_ids or [],
        "subscribed_group_ids": subscribed_group_ids or [],
        "unselected_event_ids": unselected_event_ids or [],
        "include_future_events": include_future,
        "link_uuid": link_uuid,
        "created_at": now,
        "updated_at": now
    }


def apply_filter_to_events(events: List[Dict[str, Any]], filter_data: Dict[str, Any],
                          group_event_titles: Optional[set] = None) -> List[Dict[str, Any]]:
    """
    Apply filter criteria to events list using the three-list model.

    ✅ PURE FUNCTION - No side effects, no I/O, deterministic output.

    For DOMAIN CALENDARS (three-list model):
      - subscribed_group_ids: All events in these groups (including future ones)
      - subscribed_event_ids: Manual whitelist (event titles NOT in subscribed groups)
      - unselected_event_ids: Manual blacklist (event titles FROM subscribed groups to exclude)
      - Formula: included_titles = (group_titles ∪ subscribed_event_ids) - unselected_event_ids

    For PERSONAL CALENDARS:
      - If include_future_events=True: Include all events matching subscribed titles
      - If include_future_events=False: Only include events created before filter

    Args:
        events: List of all events
        filter_data: Filter configuration dict
        group_event_titles: Pre-resolved set of event titles in subscribed groups
                           (required for domain filters, None for personal filters)

    Returns:
        Filtered list of events (new list, original unchanged)

    Pure function - same inputs always produce same outputs, no I/O.
    """
    is_domain_filter = filter_data.get("domain_key") is not None

    # Domain filters: use three-list model
    if is_domain_filter:
        if group_event_titles is None:
            raise ValueError("group_event_titles is required for domain filter operations")

        # Get the three lists
        subscribed_event_ids = filter_data.get("subscribed_event_ids", [])
        unselected_event_ids = filter_data.get("unselected_event_ids", [])

        # Apply three-list formula: (group_titles ∪ subscribed_event_ids) - unselected_event_ids
        included_titles = (group_event_titles | set(subscribed_event_ids)) - set(unselected_event_ids)

        # If no titles to include, return empty
        if not included_titles:
            return []

        # Filter events by included titles
        filtered = []
        for event in events:
            event_title = event.get("title")
            if event_title in included_titles:
                filtered.append(event)
        return filtered

    # Personal calendar filters: use include_future_events logic
    subscribed_event_ids = filter_data.get("subscribed_event_ids", [])
    include_future = filter_data.get("include_future_events")

    if not subscribed_event_ids:
        return []

    filter_created_at = filter_data.get("created_at")
    filtered = []

    for event in events:
        event_title = event.get("title")

        # Check if event title matches subscribed titles
        if event_title not in subscribed_event_ids:
            continue

        # If NOT including future events, filter by creation date
        if include_future is False and filter_created_at:
            event_created = event.get("created_at")
            if event_created and event_created > filter_created_at:
                # Skip events created after the filter (frozen mode)
                continue

        filtered.append(event)

    return filtered


def transform_events_for_export(events: List[Dict[str, Any]], filter_name: str) -> str:
    """
    Transform events into iCal format for export.

    Args:
        events: List of events to export
        filter_name: Name of the filter for iCal metadata

    Returns:
        iCal formatted string

    Pure function - deterministic text transformation.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//Filter iCal//{filter_name}//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{filter_name}",
        "X-WR-CALDESC:Filtered calendar from Filter iCal"
    ]

    for event in events:
        raw_ical = event.get("other_ical_fields", {}).get("raw_ical", "")

        # Check if raw_ical has proper DTSTART field
        # If not, generate from our parsed data to ensure compliance
        has_dtstart = raw_ical and "DTSTART" in raw_ical

        if has_dtstart:
            # Use original raw iCal if it has proper date fields
            lines.append(raw_ical)
        else:
            # Generate proper VEVENT from our parsed data (with DTSTART/DTEND)
            event_lines = _generate_vevent_from_data(event)
            lines.extend(event_lines)

    lines.append("END:VCALENDAR")
    return "\n".join(lines)


def _generate_vevent_from_data(event: Dict[str, Any]) -> List[str]:
    """
    Generate VEVENT lines from event data.

    Args:
        event: Event data dictionary

    Returns:
        List of iCal VEVENT lines

    Pure function - generates iCal format.
    """
    lines = ["BEGIN:VEVENT"]

    # Required fields
    uid = event.get("uid", f"generated-{event.get('id', 'unknown')}")
    lines.append(f"UID:{uid}")

    title = event.get("title", "Untitled Event")
    lines.append(f"SUMMARY:{title}")

    # Times - REQUIRED for calendar apps to display events
    start_time = event.get("start_time")
    if start_time:
        # Handle both datetime objects and ISO strings
        if isinstance(start_time, str):
            # Clean ISO string to iCal format (remove timezone suffix if present)
            clean_time = start_time.replace('+00:00', '').replace('Z', '').replace('-', '').replace(':', '')
            if 'T' not in clean_time:
                clean_time = f"{clean_time}T000000"
            if not clean_time.endswith('Z'):
                clean_time += 'Z'
            lines.append(f"DTSTART:{clean_time}")
        elif hasattr(start_time, 'strftime'):
            # Datetime object - format as UTC
            if start_time.tzinfo:
                # Convert to UTC if timezone-aware
                start_time = start_time.astimezone(timezone.utc)
            formatted_time = start_time.strftime("%Y%m%dT%H%M%SZ")
            lines.append(f"DTSTART:{formatted_time}")
    else:
        # Fallback: Use current date if start_time is missing (legacy events)
        fallback = datetime.now(timezone.utc)
        lines.append(f"DTSTART:{fallback.strftime('%Y%m%dT%H%M%SZ')}")

    end_time = event.get("end_time")
    if end_time:
        # Handle both datetime objects and ISO strings
        if isinstance(end_time, str):
            # Clean ISO string to iCal format
            clean_time = end_time.replace('+00:00', '').replace('Z', '').replace('-', '').replace(':', '')
            if 'T' not in clean_time:
                clean_time = f"{clean_time}T000000"
            if not clean_time.endswith('Z'):
                clean_time += 'Z'
            lines.append(f"DTEND:{clean_time}")
        elif hasattr(end_time, 'strftime'):
            # Datetime object - format as UTC
            if end_time.tzinfo:
                # Convert to UTC if timezone-aware
                end_time = end_time.astimezone(timezone.utc)
            formatted_time = end_time.strftime("%Y%m%dT%H%M%SZ")
            lines.append(f"DTEND:{formatted_time}")

    # Optional fields
    description = event.get("description")
    if description:
        lines.append(f"DESCRIPTION:{description}")

    location = event.get("location")
    if location:
        lines.append(f"LOCATION:{location}")

    lines.append("END:VEVENT")
    return lines


def validate_filter_data(name: str, calendar_id: Optional[int] = None, 
                        domain_key: Optional[str] = None,
                        subscribed_event_ids: Optional[List[int]] = None,
                        subscribed_group_ids: Optional[List[int]] = None) -> Tuple[bool, str]:
    """
    Validate filter creation data.
    
    Args:
        name: Filter name
        calendar_id: Calendar ID for user filters
        domain_key: Domain key for domain filters
        subscribed_event_ids: Event IDs list
        subscribed_group_ids: Group IDs list
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Pure function - validation without side effects.
    """
    if not name or not isinstance(name, str) or not name.strip():
        return False, "Filter name is required"
    
    if len(name.strip()) > 255:
        return False, "Filter name must be 255 characters or less"
    
    # Must have either calendar_id or domain_key, not both
    if calendar_id and domain_key:
        return False, "Filter cannot be both user and domain filter"
    
    if not calendar_id and not domain_key:
        return False, "Filter must specify either calendar_id or domain_key"
    
    # Validate event IDs if provided
    if subscribed_event_ids and not isinstance(subscribed_event_ids, list):
        return False, "Subscribed event IDs must be a list"
    
    # Validate group IDs if provided
    if subscribed_group_ids and not isinstance(subscribed_group_ids, list):
        return False, "Subscribed group IDs must be a list"
    
    # Group IDs only valid for domain filters
    if subscribed_group_ids and not domain_key:
        return False, "Group subscriptions only valid for domain filters"
    
    return True, ""


def validate_calendar_data(name: str, source_url: str, calendar_type: str = "user") -> Tuple[bool, str]:
    """
    Validate calendar creation data.
    
    Args:
        name: Calendar name
        source_url: iCal source URL
        calendar_type: Calendar type ("user" or "domain")
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Pure function - validation without side effects.
    """
    if not name or not isinstance(name, str) or not name.strip():
        return False, "Calendar name is required"
    
    if len(name.strip()) > 255:
        return False, "Calendar name must be 255 characters or less"
    
    if not source_url or not isinstance(source_url, str) or not source_url.strip():
        return False, "Calendar source URL is required"
    
    # Basic URL validation
    url = source_url.strip().lower()
    if not (url.startswith('http://') or url.startswith('https://')):
        return False, "Calendar source URL must be a valid HTTP/HTTPS URL"
    
    if calendar_type not in ['user', 'domain']:
        return False, "Calendar type must be 'user' or 'domain'"
    
    return True, ""