"""
Pure Filtering Functions - Rich Hickey Style
Advanced calendar event filtering with immutable data transformations
No side effects, explicit data flow, composable functions
"""

import re
import hashlib
from datetime import datetime, timedelta
from typing import List, Set, Dict, Tuple, Optional, Any
from ..models import Event, FilterConfig


# === FILTER VALIDATION (Pure Functions) ===

def validate_filter_config(config: FilterConfig) -> Tuple[bool, List[str]]:
    """
    Pure function: Validate filter configuration
    Returns: (is_valid, error_messages)
    """
    errors = []
    
    # Validate required fields
    if not config.name.strip():
        errors.append("Filter name is required")
    
    if not config.user_id.strip():
        errors.append("User ID is required")
    
    # Validate filter mode
    if config.filter_mode not in ['include', 'exclude']:
        errors.append("Filter mode must be 'include' or 'exclude'")
    
    # Validate date range type
    if config.date_range_type not in ['absolute', 'relative', 'rolling']:
        errors.append("Date range type must be 'absolute', 'relative', or 'rolling'")
    
    # Validate date range consistency
    if config.date_range_start and config.date_range_end:
        try:
            start = datetime.fromisoformat(config.date_range_start.replace('Z', '+00:00'))
            end = datetime.fromisoformat(config.date_range_end.replace('Z', '+00:00'))
            if start >= end:
                errors.append("Start date must be before end date")
        except ValueError:
            errors.append("Invalid date format (use ISO format)")
    
    # Validate duration filters
    if config.min_duration_minutes and config.max_duration_minutes:
        if config.min_duration_minutes >= config.max_duration_minutes:
            errors.append("Minimum duration must be less than maximum duration")
    
    return len(errors) == 0, errors


def normalize_filter_config(config: FilterConfig) -> FilterConfig:
    """
    Pure function: Normalize filter configuration for consistent processing
    Returns: New normalized FilterConfig
    """
    # Normalize keywords (lowercase, strip whitespace)
    include_keywords = [kw.lower().strip() for kw in config.include_keywords if kw.strip()]
    exclude_keywords = [kw.lower().strip() for kw in config.exclude_keywords if kw.strip()]
    
    # Normalize categories (strip whitespace, preserve case)
    include_categories = [cat.strip() for cat in config.include_categories if cat.strip()]
    exclude_categories = [cat.strip() for cat in config.exclude_categories if cat.strip()]
    
    # Create new normalized config
    return FilterConfig(
        id=config.id,
        name=config.name.strip(),
        user_id=config.user_id.strip(),
        include_categories=include_categories,
        exclude_categories=exclude_categories,
        include_keywords=include_keywords,
        exclude_keywords=exclude_keywords,
        date_range_start=config.date_range_start,
        date_range_end=config.date_range_end,
        date_range_type=config.date_range_type,
        location_filter=config.location_filter.strip() if config.location_filter else None,
        attendee_filter=config.attendee_filter.strip() if config.attendee_filter else None,
        organizer_filter=config.organizer_filter.strip() if config.organizer_filter else None,
        min_duration_minutes=config.min_duration_minutes,
        max_duration_minutes=config.max_duration_minutes,
        filter_mode=config.filter_mode,
        match_all=config.match_all,
        created_at=config.created_at,
        updated_at=config.updated_at
    )


# === INDIVIDUAL FILTER FUNCTIONS (Pure Functions) ===

def filter_by_categories(events: List[Event], include: List[str], exclude: List[str]) -> List[Event]:
    """
    Pure function: Filter events by categories
    Returns: New list of events matching category criteria
    """
    if not include and not exclude:
        return events
    
    include_set = set(include) if include else set()
    exclude_set = set(exclude) if exclude else set()
    
    filtered_events = []
    for event in events:
        event_category = extract_category_from_event(event)
        
        # If exclude list exists and category matches, skip event
        if exclude_set and event_category in exclude_set:
            continue
        
        # If include list exists, only include matching categories
        if include_set and event_category not in include_set:
            continue
        
        filtered_events.append(event)
    
    return filtered_events


def filter_by_keywords(events: List[Event], include: List[str], exclude: List[str], match_all: bool = False) -> List[Event]:
    """
    Pure function: Filter events by keywords in summary/description
    Returns: New list of events matching keyword criteria
    """
    if not include and not exclude:
        return events
    
    filtered_events = []
    for event in events:
        # Combine searchable text
        searchable_text = " ".join([
            event.summary or "",
            event.description or "",
            event.location or ""
        ]).lower()
        
        # Check exclude keywords first
        if exclude:
            exclude_found = any(keyword in searchable_text for keyword in exclude)
            if exclude_found:
                continue
        
        # Check include keywords
        if include:
            if match_all:
                # All keywords must be present
                include_match = all(keyword in searchable_text for keyword in include)
            else:
                # At least one keyword must be present
                include_match = any(keyword in searchable_text for keyword in include)
            
            if not include_match:
                continue
        
        filtered_events.append(event)
    
    return filtered_events


def filter_by_date_range(events: List[Event], start_date: Optional[str], end_date: Optional[str], 
                        range_type: str = 'absolute') -> List[Event]:
    """
    Pure function: Filter events by date range
    Returns: New list of events within date range
    """
    if not start_date and not end_date:
        return events
    
    # Parse dates
    start_dt = None
    end_dt = None
    
    try:
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError:
        # Invalid date format, return all events
        return events
    
    # Handle relative dates (relative to current time)
    if range_type == 'relative':
        now = datetime.now()
        if start_dt:
            start_dt = now + timedelta(days=(start_dt - datetime(1970, 1, 1)).days)
        if end_dt:
            end_dt = now + timedelta(days=(end_dt - datetime(1970, 1, 1)).days)
    
    # Handle rolling window (always X days from now)
    elif range_type == 'rolling':
        now = datetime.now()
        if start_date:
            # Treat as days offset from now
            days_offset = int(start_date) if start_date.isdigit() else 0
            start_dt = now + timedelta(days=days_offset)
        if end_date:
            # Treat as days offset from now
            days_offset = int(end_date) if end_date.isdigit() else 30
            end_dt = now + timedelta(days=days_offset)
    
    filtered_events = []
    for event in events:
        event_start = parse_event_datetime(event.dtstart)
        if not event_start:
            continue
        
        # Check if event falls within range
        if start_dt and event_start < start_dt:
            continue
        if end_dt and event_start > end_dt:
            continue
        
        filtered_events.append(event)
    
    return filtered_events


def filter_by_duration(events: List[Event], min_minutes: Optional[int], max_minutes: Optional[int]) -> List[Event]:
    """
    Pure function: Filter events by duration
    Returns: New list of events within duration range
    """
    if not min_minutes and not max_minutes:
        return events
    
    filtered_events = []
    for event in events:
        duration = calculate_event_duration_minutes(event)
        if duration is None:
            continue
        
        if min_minutes and duration < min_minutes:
            continue
        if max_minutes and duration > max_minutes:
            continue
        
        filtered_events.append(event)
    
    return filtered_events


def filter_by_location(events: List[Event], location_pattern: Optional[str]) -> List[Event]:
    """
    Pure function: Filter events by location (supports regex)
    Returns: New list of events matching location pattern
    """
    if not location_pattern:
        return events
    
    try:
        # Compile regex pattern (case insensitive)
        pattern = re.compile(location_pattern, re.IGNORECASE)
    except re.error:
        # Invalid regex, treat as literal string
        pattern = re.compile(re.escape(location_pattern), re.IGNORECASE)
    
    filtered_events = []
    for event in events:
        if event.location and pattern.search(event.location):
            filtered_events.append(event)
    
    return filtered_events


def filter_by_attendee(events: List[Event], attendee_pattern: Optional[str]) -> List[Event]:
    """
    Pure function: Filter events by attendee (requires parsing raw iCal)
    Returns: New list of events with matching attendees
    """
    if not attendee_pattern:
        return events
    
    try:
        pattern = re.compile(attendee_pattern, re.IGNORECASE)
    except re.error:
        pattern = re.compile(re.escape(attendee_pattern), re.IGNORECASE)
    
    filtered_events = []
    for event in events:
        # Extract attendees from raw iCal data
        attendees = extract_attendees_from_raw_ical(event.raw)
        if any(pattern.search(attendee) for attendee in attendees):
            filtered_events.append(event)
    
    return filtered_events


# === COMPOSITE FILTER FUNCTIONS (Pure Functions) ===

def apply_filter_config(events: List[Event], config: FilterConfig) -> List[Event]:
    """
    Pure function: Apply complete filter configuration to events
    Returns: New list of filtered events
    """
    # Start with all events
    filtered_events = events
    
    # Apply each filter type in sequence
    filtered_events = filter_by_categories(
        filtered_events, config.include_categories, config.exclude_categories
    )
    
    filtered_events = filter_by_keywords(
        filtered_events, config.include_keywords, config.exclude_keywords, config.match_all
    )
    
    filtered_events = filter_by_date_range(
        filtered_events, config.date_range_start, config.date_range_end, config.date_range_type
    )
    
    if config.min_duration_minutes or config.max_duration_minutes:
        filtered_events = filter_by_duration(
            filtered_events, config.min_duration_minutes, config.max_duration_minutes
        )
    
    if config.location_filter:
        filtered_events = filter_by_location(filtered_events, config.location_filter)
    
    if config.attendee_filter:
        filtered_events = filter_by_attendee(filtered_events, config.attendee_filter)
    
    return filtered_events


def create_filter_pipeline(configs: List[FilterConfig]) -> callable:
    """
    Pure function: Create a composable filter pipeline
    Returns: Function that applies all filters in sequence
    """
    def pipeline(events: List[Event]) -> List[Event]:
        result = events
        for config in configs:
            result = apply_filter_config(result, config)
        return result
    
    return pipeline


# === HELPER FUNCTIONS (Pure Functions) ===

def extract_category_from_event(event: Event) -> str:
    """
    Pure function: Extract category from event
    Enhanced to check multiple fields
    """
    # Try to extract from raw iCal first
    if event.raw:
        categories = extract_categories_from_raw_ical(event.raw)
        if categories:
            return categories[0]
    
    # Fall back to summary-based categorization
    if event.summary:
        summary_lower = event.summary.lower()
        
        # Common category patterns
        if any(word in summary_lower for word in ['meeting', 'call', 'standup', 'sync']):
            return 'Meeting'
        elif any(word in summary_lower for word in ['lunch', 'dinner', 'coffee', 'break']):
            return 'Social'
        elif any(word in summary_lower for word in ['deadline', 'due', 'task', 'todo']):
            return 'Task'
        elif any(word in summary_lower for word in ['vacation', 'holiday', 'pto', 'off']):
            return 'Personal'
        elif any(word in summary_lower for word in ['training', 'workshop', 'seminar', 'course']):
            return 'Learning'
    
    return 'Uncategorized'


def extract_categories_from_raw_ical(raw_ical: str) -> List[str]:
    """
    Pure function: Extract CATEGORIES from raw iCal data
    Returns: List of categories found in the event
    """
    categories = []
    for line in raw_ical.split('\n'):
        line = line.strip()
        if line.startswith('CATEGORIES:'):
            # Categories can be comma-separated
            cats = line[11:].split(',')
            categories.extend([cat.strip() for cat in cats if cat.strip()])
    
    return categories


def extract_attendees_from_raw_ical(raw_ical: str) -> List[str]:
    """
    Pure function: Extract attendees from raw iCal data
    Returns: List of attendee email addresses
    """
    attendees = []
    for line in raw_ical.split('\n'):
        line = line.strip()
        if line.startswith('ATTENDEE'):
            # Extract email from ATTENDEE line
            # Format: ATTENDEE;CN=Name;ROLE=REQ-PARTICIPANT:mailto:email@domain.com
            if 'mailto:' in line:
                email_part = line.split('mailto:')[1]
                if email_part:
                    attendees.append(email_part)
    
    return attendees


def parse_event_datetime(dt_str: str) -> Optional[datetime]:
    """
    Pure function: Parse event datetime string to datetime object
    Handles various iCal datetime formats
    """
    if not dt_str:
        return None
    
    try:
        # Handle different datetime formats
        if 'T' in dt_str:
            # Full datetime
            if dt_str.endswith('Z'):
                return datetime.fromisoformat(dt_str[:-1] + '+00:00')
            elif '+' in dt_str or dt_str.count('-') > 2:
                return datetime.fromisoformat(dt_str)
            else:
                return datetime.fromisoformat(dt_str)
        else:
            # Date only
            return datetime.fromisoformat(dt_str + 'T00:00:00')
    except (ValueError, IndexError):
        return None


def calculate_event_duration_minutes(event: Event) -> Optional[int]:
    """
    Pure function: Calculate event duration in minutes
    Returns: Duration in minutes or None if unable to calculate
    """
    start_dt = parse_event_datetime(event.dtstart)
    end_dt = parse_event_datetime(event.dtend)
    
    if not start_dt or not end_dt:
        return None
    
    duration = end_dt - start_dt
    return int(duration.total_seconds() / 60)


def create_filter_config_hash(config: FilterConfig) -> str:
    """
    Pure function: Create hash of filter configuration for cache keys
    Returns: SHA256 hash of configuration
    """
    # Create deterministic string representation
    config_str = f"{config.include_categories}{config.exclude_categories}" + \
                f"{config.include_keywords}{config.exclude_keywords}" + \
                f"{config.date_range_start}{config.date_range_end}{config.date_range_type}" + \
                f"{config.location_filter}{config.attendee_filter}{config.organizer_filter}" + \
                f"{config.min_duration_minutes}{config.max_duration_minutes}" + \
                f"{config.filter_mode}{config.match_all}"
    
    return hashlib.sha256(config_str.encode()).hexdigest()


def create_events_content_hash(events: List[Event]) -> str:
    """
    Pure function: Create hash of events list for change detection
    Returns: SHA256 hash of events content
    """
    # Create deterministic string from event UIDs and last modified times
    events_str = "".join([f"{event.uid}{event.dtstart}{event.dtend}" for event in events])
    return hashlib.sha256(events_str.encode()).hexdigest()


def filter_stats_summary(original_events: List[Event], filtered_events: List[Event], 
                        config: FilterConfig) -> Dict[str, Any]:
    """
    Pure function: Generate filtering statistics
    Returns: Dictionary with filtering statistics
    """
    original_count = len(original_events)
    filtered_count = len(filtered_events)
    reduction_percent = ((original_count - filtered_count) / original_count * 100) if original_count > 0 else 0
    
    return {
        "original_event_count": original_count,
        "filtered_event_count": filtered_count,
        "events_removed": original_count - filtered_count,
        "reduction_percent": round(reduction_percent, 1),
        "filter_name": config.name,
        "active_filters": {
            "categories": bool(config.include_categories or config.exclude_categories),
            "keywords": bool(config.include_keywords or config.exclude_keywords),
            "date_range": bool(config.date_range_start or config.date_range_end),
            "duration": bool(config.min_duration_minutes or config.max_duration_minutes),
            "location": bool(config.location_filter),
            "attendee": bool(config.attendee_filter)
        }
    }