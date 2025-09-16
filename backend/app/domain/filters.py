"""
Filters Domain Functions - Pure Business Logic
Rich Hickey: "Functional Core - Pure functions only"
"""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime, date


def create_filter(name: str, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Pure function to create filter data structure
    
    Args:
        name: Filter name
        config: Filter configuration
        user_id: User identifier
        
    Returns:
        Filter data dictionary
    """
    timestamp = datetime.now().isoformat()
    filter_id = f"filter_{user_id}_{int(datetime.now().timestamp())}"
    
    return {
        "id": filter_id,
        "name": name.strip(),
        "config": normalize_filter_config(config),
        "user_id": user_id,
        "created_at": timestamp,
        "updated_at": timestamp,
        "is_active": True
    }


def normalize_filter_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure function to normalize and validate filter configuration
    
    Args:
        config: Raw filter configuration
        
    Returns:
        Normalized filter configuration
    """
    normalized = {}
    
    # Category filters
    if 'categories' in config:
        categories = config['categories']
        normalized['categories'] = {
            'include': normalize_string_list(categories.get('include', [])),
            'exclude': normalize_string_list(categories.get('exclude', [])),
            'mode': categories.get('mode', 'include').lower()
        }
    
    # Keyword filters
    if 'keywords' in config:
        keywords = config['keywords']
        if isinstance(keywords, list):
            normalized['keywords'] = [kw.strip().lower() for kw in keywords if kw.strip()]
        elif isinstance(keywords, str):
            normalized['keywords'] = [kw.strip().lower() for kw in keywords.split(',') if kw.strip()]
        else:
            normalized['keywords'] = []
    
    # Date range filters
    if 'date_range' in config:
        date_range = config['date_range']
        normalized['date_range'] = normalize_date_range(date_range)
    
    # Location filters
    if 'location' in config:
        location = config['location']
        normalized['location'] = {
            'include': normalize_string_list(location.get('include', [])),
            'exclude': normalize_string_list(location.get('exclude', [])),
            'mode': location.get('mode', 'include').lower()
        }
    
    # Duration filters
    if 'duration' in config:
        duration = config['duration']
        normalized['duration'] = {
            'min_minutes': max(0, int(duration.get('min_minutes', 0))),
            'max_minutes': max(0, int(duration.get('max_minutes', 0))) if duration.get('max_minutes') else None
        }
    
    # All-day event filter
    if 'all_day' in config:
        normalized['all_day'] = {
            'include': bool(config['all_day'].get('include', True)),
            'exclude': bool(config['all_day'].get('exclude', False))
        }
    
    return normalized


def normalize_string_list(items: Any) -> List[str]:
    """
    Pure function to normalize list of strings
    
    Args:
        items: Items to normalize
        
    Returns:
        List of normalized strings
    """
    if not items:
        return []
    
    if isinstance(items, str):
        return [item.strip() for item in items.split(',') if item.strip()]
    
    if isinstance(items, list):
        result = []
        for item in items:
            if isinstance(item, str):
                result.extend([i.strip() for i in item.split(',') if i.strip()])
            else:
                result.append(str(item).strip())
        return result
    
    return [str(items).strip()]


def normalize_date_range(date_range: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure function to normalize date range configuration
    
    Args:
        date_range: Raw date range config
        
    Returns:
        Normalized date range config
    """
    normalized = {}
    
    # Start date
    if 'start' in date_range:
        normalized['start'] = normalize_date_string(date_range['start'])
    
    # End date
    if 'end' in date_range:
        normalized['end'] = normalize_date_string(date_range['end'])
    
    # Relative ranges (e.g., "next 30 days")
    if 'relative' in date_range:
        relative = date_range['relative']
        if isinstance(relative, dict):
            normalized['relative'] = {
                'amount': max(0, int(relative.get('amount', 0))),
                'unit': relative.get('unit', 'days').lower(),
                'direction': relative.get('direction', 'future').lower()
            }
    
    return normalized


def normalize_date_string(date_value: Any) -> Optional[str]:
    """
    Pure function to normalize date value to ISO string
    
    Args:
        date_value: Date in various formats
        
    Returns:
        ISO date string or None
    """
    if date_value is None:
        return None
    
    if isinstance(date_value, str):
        return date_value
    
    if hasattr(date_value, 'isoformat'):
        return date_value.isoformat()
    
    return str(date_value)


def apply_filter_to_events(events: List[Dict[str, Any]], 
                          filter_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pure function to apply filter configuration to events
    
    Args:
        events: List of events to filter
        filter_config: Filter configuration
        
    Returns:
        Filtered events
    """
    filtered_events = events
    
    # Apply category filters
    if 'categories' in filter_config:
        filtered_events = apply_category_filter(filtered_events, filter_config['categories'])
    
    # Apply keyword filters
    if 'keywords' in filter_config:
        filtered_events = apply_keyword_filter(filtered_events, filter_config['keywords'])
    
    # Apply location filters
    if 'location' in filter_config:
        filtered_events = apply_location_filter(filtered_events, filter_config['location'])
    
    # Apply duration filters
    if 'duration' in filter_config:
        filtered_events = apply_duration_filter(filtered_events, filter_config['duration'])
    
    # Apply all-day filters
    if 'all_day' in filter_config:
        filtered_events = apply_all_day_filter(filtered_events, filter_config['all_day'])
    
    return filtered_events


def apply_category_filter(events: List[Dict[str, Any]], 
                         category_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pure function to apply category filters
    
    Args:
        events: Events to filter
        category_config: Category filter configuration
        
    Returns:
        Filtered events
    """
    include_categories = set(category_config.get('include', []))
    exclude_categories = set(category_config.get('exclude', []))
    mode = category_config.get('mode', 'include')
    
    if mode == 'include' and include_categories:
        return [
            event for event in events
            if any(cat in include_categories for cat in event.get('categories', []))
        ]
    
    if exclude_categories:
        return [
            event for event in events
            if not any(cat in exclude_categories for cat in event.get('categories', []))
        ]
    
    return events


def apply_keyword_filter(events: List[Dict[str, Any]], 
                        keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Pure function to apply keyword filters
    
    Args:
        events: Events to filter
        keywords: Keywords to search for
        
    Returns:
        Filtered events
    """
    if not keywords:
        return events
    
    keyword_set = set(keywords)
    
    return [
        event for event in events
        if any(
            keyword in event.get('summary', '').lower() or
            keyword in event.get('description', '').lower()
            for keyword in keyword_set
        )
    ]


def apply_location_filter(events: List[Dict[str, Any]], 
                         location_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pure function to apply location filters
    
    Args:
        events: Events to filter
        location_config: Location filter configuration
        
    Returns:
        Filtered events
    """
    include_locations = set(loc.lower() for loc in location_config.get('include', []))
    exclude_locations = set(loc.lower() for loc in location_config.get('exclude', []))
    mode = location_config.get('mode', 'include')
    
    if mode == 'include' and include_locations:
        return [
            event for event in events
            if any(loc in event.get('location', '').lower() for loc in include_locations)
        ]
    
    if exclude_locations:
        return [
            event for event in events
            if not any(loc in event.get('location', '').lower() for loc in exclude_locations)
        ]
    
    return events


def apply_duration_filter(events: List[Dict[str, Any]], 
                         duration_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pure function to apply duration filters
    
    Args:
        events: Events to filter
        duration_config: Duration filter configuration
        
    Returns:
        Filtered events
    """
    min_minutes = duration_config.get('min_minutes', 0)
    max_minutes = duration_config.get('max_minutes')
    
    filtered_events = []
    for event in events:
        duration = calculate_event_duration_minutes(event)
        
        if duration is None:
            # Include events with unknown duration
            filtered_events.append(event)
            continue
        
        if duration < min_minutes:
            continue
        
        if max_minutes is not None and duration > max_minutes:
            continue
        
        filtered_events.append(event)
    
    return filtered_events


def apply_all_day_filter(events: List[Dict[str, Any]], 
                        all_day_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pure function to apply all-day event filters
    
    Args:
        events: Events to filter
        all_day_config: All-day filter configuration
        
    Returns:
        Filtered events
    """
    include_all_day = all_day_config.get('include', True)
    exclude_all_day = all_day_config.get('exclude', False)
    
    if exclude_all_day:
        return [event for event in events if not event.get('all_day', False)]
    
    if not include_all_day:
        return [event for event in events if not event.get('all_day', False)]
    
    return events


def calculate_event_duration_minutes(event: Dict[str, Any]) -> Optional[int]:
    """
    Pure function to calculate event duration in minutes
    
    Args:
        event: Event data
        
    Returns:
        Duration in minutes or None if cannot calculate
    """
    start_time = event.get('start_time')
    end_time = event.get('end_time')
    
    if not start_time or not end_time:
        return None
    
    try:
        # This is a simplified calculation - real implementation would
        # need proper datetime parsing
        if isinstance(start_time, str) and isinstance(end_time, str):
            # Placeholder - would need actual datetime parsing
            return 60  # Default 1 hour
        
        return None
    except Exception:
        return None