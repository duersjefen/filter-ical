"""
Pure functions for event filtering and transformation
Functional Core: No side effects, deterministic, easy to test
All filtering logic separated from HTTP and database concerns
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, date
import json




def filter_events_by_date_range(
    events: List[Dict[str, Any]], 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Pure function: Filter events by date range
    
    Args:
        events: List of event dictionaries
        start_date: Minimum event start date (inclusive)
        end_date: Maximum event end date (inclusive)
    
    Returns:
        Filtered list of events
    """
    if not events:
        return []
    
    filtered_events = []
    
    for event in events:
        event_start = event.get('start')
        event_end = event.get('end')
        
        if not event_start or not event_end:
            continue
            
        # Convert to datetime if needed
        if isinstance(event_start, str):
            try:
                event_start = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
            except:
                continue
                
        if isinstance(event_end, str):
            try:
                event_end = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
            except:
                continue
        
        # Check date range
        include_event = True
        
        if start_date and event_end < start_date:
            include_event = False
            
        if end_date and event_start > end_date:
            include_event = False
            
        if include_event:
            filtered_events.append(event)
    
    return filtered_events


def filter_events_by_keywords(
    events: List[Dict[str, Any]], 
    keywords: str
) -> List[Dict[str, Any]]:
    """
    Pure function: Filter events by keyword search in title and description
    
    Args:
        events: List of event dictionaries
        keywords: Space-separated keywords to search for
    
    Returns:
        Filtered list of events matching keywords
    """
    if not events or not keywords.strip():
        return events
    
    # Split keywords and convert to lowercase
    keyword_list = [kw.lower().strip() for kw in keywords.split() if kw.strip()]
    if not keyword_list:
        return events
    
    filtered_events = []
    
    for event in events:
        # Search in title and description
        searchable_text = ""
        searchable_text += event.get('title', '').lower()
        searchable_text += ' ' + event.get('description', '').lower()
        searchable_text += ' ' + event.get('location', '').lower()
        
        # Check if any keyword matches
        matches = any(keyword in searchable_text for keyword in keyword_list)
        
        if matches:
            filtered_events.append(event)
    
    return filtered_events


def sort_events(
    events: List[Dict[str, Any]], 
    sort_by: str = 'date', 
    sort_direction: str = 'asc'
) -> List[Dict[str, Any]]:
    """
    Pure function: Sort events by specified field and direction
    
    Args:
        events: List of event dictionaries
        sort_by: Field to sort by ('date', 'title', 'category')
        sort_direction: 'asc' or 'desc'
    
    Returns:
        Sorted list of events
    """
    if not events:
        return []
    
    reverse_order = sort_direction.lower() == 'desc'
    
    if sort_by == 'date':
        # Sort by start date
        return sorted(
            events, 
            key=lambda x: x.get('start', datetime.min),
            reverse=reverse_order
        )
    elif sort_by == 'title':
        # Sort by event title
        return sorted(
            events,
            key=lambda x: x.get('title', '').lower(),
            reverse=reverse_order
        )
    elif sort_by == 'category':
        # Sort by category, then by date
        return sorted(
            events,
            key=lambda x: (x.get('category', '').lower(), x.get('start', datetime.min)),
            reverse=reverse_order
        )
    else:
        # Default to date sorting
        return sorted(
            events,
            key=lambda x: x.get('start', datetime.min),
            reverse=reverse_order
        )




def parse_json_field(json_string: str, default: Any = None) -> Any:
    """
    Pure function: Safely parse JSON string field
    
    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails
    
    Returns:
        Parsed JSON data or default value
    """
    try:
        return json.loads(json_string) if json_string else default
    except:
        return default


def serialize_json_field(data: Any) -> str:
    """
    Pure function: Safely serialize data to JSON string
    
    Args:
        data: Data to serialize
    
    Returns:
        JSON string representation
    """
    try:
        return json.dumps(data) if data is not None else "[]"
    except:
        return "[]"