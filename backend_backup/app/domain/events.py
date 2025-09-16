"""
Events Domain Functions - Pure Business Logic
Rich Hickey: "Functional Core - Pure functions only"
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import re


def process_calendar_events(events_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Pure function to process and normalize calendar events
    
    Args:
        events_data: Raw event data from calendar
        
    Returns:
        Processed and normalized events
    """
    processed_events = []
    
    for event in events_data:
        processed_event = normalize_event_data(event)
        if processed_event:
            processed_events.append(processed_event)
    
    return processed_events


def normalize_event_data(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Pure function to normalize single event data
    
    Args:
        event: Raw event data
        
    Returns:
        Normalized event or None if invalid
    """
    try:
        # Required fields
        summary = event.get('summary', '').strip()
        if not summary:
            return None
        
        # Create normalized event structure
        normalized = {
            "id": event.get('uid', f"event_{hash(summary)}"),
            "summary": summary,
            "description": event.get('description', '').strip(),
            "start_time": normalize_datetime(event.get('dtstart')),
            "end_time": normalize_datetime(event.get('dtend')),
            "location": event.get('location', '').strip(),
            "categories": extract_categories(event.get('categories', [])),
            "status": event.get('status', 'CONFIRMED').upper(),
            "created": normalize_datetime(event.get('created')),
            "last_modified": normalize_datetime(event.get('last-modified')),
            "organizer": extract_organizer(event.get('organizer')),
            "attendees": extract_attendees(event.get('attendee', [])),
            "url": event.get('url', '').strip(),
            "all_day": is_all_day_event(event)
        }
        
        return normalized
    except Exception:
        # If normalization fails, skip this event
        return None


def normalize_datetime(dt_value: Any) -> Optional[str]:
    """
    Pure function to normalize datetime values to ISO format
    
    Args:
        dt_value: Datetime value in various formats
        
    Returns:
        ISO formatted datetime string or None
    """
    if dt_value is None:
        return None
    
    if isinstance(dt_value, str):
        return dt_value
    
    if hasattr(dt_value, 'isoformat'):
        return dt_value.isoformat()
    
    return str(dt_value)


def extract_categories(categories: Any) -> List[str]:
    """
    Pure function to extract and normalize categories
    
    Args:
        categories: Categories in various formats
        
    Returns:
        List of category strings
    """
    if not categories:
        return []
    
    if isinstance(categories, str):
        # Split by comma and clean up
        return [cat.strip() for cat in categories.split(',') if cat.strip()]
    
    if isinstance(categories, list):
        result = []
        for cat in categories:
            if isinstance(cat, str):
                result.extend([c.strip() for c in cat.split(',') if c.strip()])
            else:
                result.append(str(cat).strip())
        return result
    
    return [str(categories).strip()]


def extract_organizer(organizer: Any) -> Optional[Dict[str, str]]:
    """
    Pure function to extract organizer information
    
    Args:
        organizer: Organizer data in various formats
        
    Returns:
        Organizer dictionary or None
    """
    if not organizer:
        return None
    
    if isinstance(organizer, str):
        # Extract email from string like "MAILTO:email@example.com"
        email_match = re.search(r'mailto:([^;]+)', organizer, re.IGNORECASE)
        email = email_match.group(1) if email_match else organizer
        
        # Extract name from CN parameter
        name_match = re.search(r'CN=([^;:]+)', organizer)
        name = name_match.group(1) if name_match else None
        
        return {
            "email": email.strip(),
            "name": name.strip() if name else None
        }
    
    if isinstance(organizer, dict):
        return {
            "email": organizer.get('email', '').strip(),
            "name": organizer.get('name', '').strip() or None
        }
    
    return None


def extract_attendees(attendees: Any) -> List[Dict[str, str]]:
    """
    Pure function to extract attendee information
    
    Args:
        attendees: Attendee data in various formats
        
    Returns:
        List of attendee dictionaries
    """
    if not attendees:
        return []
    
    if not isinstance(attendees, list):
        attendees = [attendees]
    
    result = []
    for attendee in attendees:
        attendee_info = extract_organizer(attendee)  # Same logic as organizer
        if attendee_info:
            result.append(attendee_info)
    
    return result


def is_all_day_event(event: Dict[str, Any]) -> bool:
    """
    Pure function to determine if event is all-day
    
    Args:
        event: Event data
        
    Returns:
        True if event is all-day
    """
    # Check if start time is date-only (no time component)
    start = event.get('dtstart')
    if hasattr(start, 'date') and not hasattr(start, 'time'):
        return True
    
    # Check for explicit all-day markers
    if isinstance(start, date) and not isinstance(start, datetime):
        return True
    
    return False


def filter_events_by_criteria(events: List[Dict[str, Any]], 
                            criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pure function to filter events based on criteria
    
    Args:
        events: List of events to filter
        criteria: Filter criteria
        
    Returns:
        Filtered events list
    """
    filtered_events = events
    
    # Filter by categories
    if 'categories' in criteria:
        include_categories = criteria['categories'].get('include', [])
        exclude_categories = criteria['categories'].get('exclude', [])
        
        if include_categories:
            filtered_events = [
                event for event in filtered_events
                if any(cat in event.get('categories', []) for cat in include_categories)
            ]
        
        if exclude_categories:
            filtered_events = [
                event for event in filtered_events
                if not any(cat in event.get('categories', []) for cat in exclude_categories)
            ]
    
    # Filter by keywords in summary/description
    if 'keywords' in criteria:
        keywords = criteria['keywords']
        if keywords:
            keyword_list = [kw.lower().strip() for kw in keywords if kw.strip()]
            filtered_events = [
                event for event in filtered_events
                if any(
                    keyword in event.get('summary', '').lower() or
                    keyword in event.get('description', '').lower()
                    for keyword in keyword_list
                )
            ]
    
    # Filter by date range
    if 'date_range' in criteria:
        date_range = criteria['date_range']
        start_date = date_range.get('start')
        end_date = date_range.get('end')
        
        # Implementation would depend on date parsing logic
        # For now, just return the events as-is
    
    return filtered_events