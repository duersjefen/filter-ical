"""
Pure functions for event filtering and transformation
Functional Core: No side effects, deterministic, easy to test
All filtering logic separated from HTTP and database concerns
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, date
import json


def filter_events_by_categories(
    events: List[Dict[str, Any]], 
    include_categories: List[str], 
    exclude_categories: List[str], 
    filter_mode: str
) -> List[Dict[str, Any]]:
    """
    Pure function: Filter events by category inclusion/exclusion rules
    
    Args:
        events: List of event dictionaries
        include_categories: Categories to include 
        exclude_categories: Categories to exclude
        filter_mode: "include" or "exclude"
    
    Returns:
        Filtered list of events
    """
    if not events:
        return []
    
    filtered_events = []
    
    for event in events:
        event_category = event.get('category', '')
        
        if filter_mode == 'include':
            # Include mode: only include events in specified categories
            if include_categories:
                if event_category in include_categories:
                    filtered_events.append(event)
            else:
                # No include categories specified, include all
                filtered_events.append(event)
        
        elif filter_mode == 'exclude':
            # Exclude mode: exclude events in specified categories  
            if exclude_categories:
                if event_category not in exclude_categories:
                    filtered_events.append(event)
            else:
                # No exclude categories specified, include all
                filtered_events.append(event)
    
    return filtered_events


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


def apply_saved_filter_config(
    events: List[Dict[str, Any]], 
    filter_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Pure function: Apply a saved filter configuration to events
    
    Args:
        events: List of event dictionaries
        filter_config: Filter configuration matching SavedFilterConfig schema
    
    Returns:
        Filtered and sorted list of events
    """
    if not events:
        return []
    
    filtered_events = events
    
    # Apply category filter
    selected_types = filter_config.get('selectedEventTypes', [])
    if selected_types:
        filtered_events = filter_events_by_categories(
            filtered_events,
            include_categories=selected_types,
            exclude_categories=[],
            filter_mode='include'
        )
    
    # Apply keyword filter  
    keyword_filter = filter_config.get('keywordFilter', '')
    if keyword_filter.strip():
        filtered_events = filter_events_by_keywords(filtered_events, keyword_filter)
    
    # Apply date range filter
    date_range = filter_config.get('dateRange', {})
    start_date_str = date_range.get('start')
    end_date_str = date_range.get('end')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str)
        except:
            pass
            
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str)
        except:
            pass
    
    if start_date or end_date:
        filtered_events = filter_events_by_date_range(filtered_events, start_date, end_date)
    
    # Apply sorting
    sort_by = filter_config.get('sortBy', 'date')
    sort_direction = filter_config.get('sortDirection', 'asc')
    
    filtered_events = sort_events(filtered_events, sort_by, sort_direction)
    
    return filtered_events


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