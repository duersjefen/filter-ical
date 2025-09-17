"""
Pure functions for iCal parsing and processing
Functional Core: No side effects, easy to test, deterministic
Following Rich Hickey's functional programming principles
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from urllib.parse import urlparse
import icalendar
import recurring_ical_events
import httpx
import uuid


def validate_ical_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Pure function: Validate iCal URL format
    Returns: (is_valid, error_message)
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme in ['http', 'https']:
            return False, "URL must use HTTP or HTTPS protocol"
        if not parsed.netloc:
            return False, "URL must have a valid domain"
        return True, None
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def fetch_ical_content(url: str) -> tuple[Optional[str], Optional[str]]:
    """
    Pure function: Fetch iCal content from URL
    Returns: (ical_content, error_message)
    """
    try:
        # Validate URL first
        is_valid, error = validate_ical_url(url)
        if not is_valid:
            return None, error
            
        # Fetch with reasonable timeout and headers
        response = httpx.get(
            url, 
            timeout=30.0,
            headers={
                'User-Agent': 'iCal-Viewer/2.0 (https://filter-ical.de)',
                'Accept': 'text/calendar, application/calendar, text/plain, */*'
            },
            follow_redirects=True
        )
        response.raise_for_status()
        
        return response.text, None
        
    except httpx.TimeoutException:
        return None, "Calendar URL timed out after 30 seconds"
    except httpx.HTTPStatusError as e:
        return None, f"Calendar URL returned error {e.response.status_code}"
    except Exception as e:
        return None, f"Failed to fetch calendar: {str(e)}"


def parse_ical_content(ical_content: str) -> tuple[Optional[icalendar.Calendar], Optional[str]]:
    """
    Pure function: Parse iCal content string into icalendar.Calendar object
    Returns: (calendar_object, error_message)
    """
    try:
        calendar = icalendar.Calendar.from_ical(ical_content)
        return calendar, None
    except Exception as e:
        return None, f"Invalid iCal format: {str(e)}"


def extract_event_data(component: icalendar.Event, calendar_id: str) -> Optional[Dict[str, Any]]:
    """
    Pure function: Extract event data from icalendar component
    Returns standardized event dictionary matching OpenAPI Event schema
    """
    try:
        # Extract required fields
        title = str(component.get('SUMMARY', 'Untitled Event'))
        dtstart = component.get('DTSTART')
        dtend = component.get('DTEND')
        
        if not dtstart or not dtend:
            return None
            
        # Convert to datetime objects
        start_dt = dtstart.dt if hasattr(dtstart, 'dt') else dtstart
        end_dt = dtend.dt if hasattr(dtend, 'dt') else dtend
        
        # Handle date vs datetime
        if isinstance(start_dt, date) and not isinstance(start_dt, datetime):
            start_dt = datetime.combine(start_dt, datetime.min.time())
        if isinstance(end_dt, date) and not isinstance(end_dt, datetime):
            end_dt = datetime.combine(end_dt, datetime.min.time())
            
        # Extract optional fields
        description = str(component.get('DESCRIPTION', '')) if component.get('DESCRIPTION') else None
        location = str(component.get('LOCATION', '')) if component.get('LOCATION') else None
        
        # Extract category (use first category or summary as fallback)
        categories = component.get('CATEGORIES')
        if categories:
            # Handle icalendar vCategory objects
            if hasattr(categories, 'to_ical'):
                category = categories.to_ical().decode('utf-8').split(',')[0].strip()
            else:
                category = str(categories).split(',')[0].strip()
        else:
            # Use full event title as category fallback (for proper filtering/grouping)
            category = title if title else 'Event'
        
        return {
            'id': f"evt_{uuid.uuid4().hex[:8]}",
            'calendar_id': calendar_id,
            'title': title,
            'start': start_dt,
            'end': end_dt,
            'category': category,
            'description': description,
            'location': location,
            'raw_ical': component.to_ical().decode('utf-8')
        }
        
    except Exception as e:
        # Skip malformed events rather than failing entire parse
        return None


def parse_calendar_events(ical_content: str, calendar_id: str) -> tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Pure function: Parse iCal content and extract all events
    Returns: (list_of_events, error_message)
    """
    try:
        calendar, error = parse_ical_content(ical_content)
        if error:
            return [], error
            
        events = []
        
        # Process all VEVENT components
        for component in calendar.walk():
            if component.name == "VEVENT":
                event_data = extract_event_data(component, calendar_id)
                if event_data:
                    events.append(event_data)
        
        # Handle recurring events (expand them)
        try:
            # Use recurring-ical-events for proper recurrence handling
            start_date = datetime.now().replace(day=1, month=1) 
            end_date = datetime.now().replace(year=datetime.now().year + 2)
            
            recurring_events = recurring_ical_events.of(calendar).between(start_date, end_date)
            
            # Convert recurring events to our format
            for event in recurring_events:
                if hasattr(event, 'get'):
                    event_data = extract_event_data(event, calendar_id)
                    if event_data and event_data not in events:
                        events.append(event_data)
                        
        except Exception:
            # If recurring event processing fails, just use basic events
            pass
            
        return events, None
        
    except Exception as e:
        return [], f"Failed to parse calendar events: {str(e)}"


def filter_future_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Pure function: Filter events to only include future events (from today forward)
    Returns: List of events starting from today or later
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    future_events = []
    for event in events:
        start = event.get('start')
        if start:
            # Convert to timezone-aware datetime for comparison
            if isinstance(start, datetime):
                if start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)
                if start >= now:
                    future_events.append(event)
            # Handle date objects (all-day events)
            elif hasattr(start, 'year'):
                start_dt = datetime.combine(start, datetime.min.time()).replace(tzinfo=timezone.utc)
                if start_dt >= now:
                    future_events.append(event)
    
    return future_events


def events_to_categories(events: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Pure function: Transform events list into categories summary
    Returns dictionary matching OpenAPI categories response format
    """
    categories = {}
    
    for event in events:
        category = event.get('category', 'Uncategorized')
        
        if category not in categories:
            categories[category] = {
                'count': 0,
                'events': []
            }
            
        categories[category]['count'] += 1
        categories[category]['events'].append(event['id'])
    
    return categories


def events_to_recurring_types(events: List[Dict[str, Any]], future_only: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Pure function: Transform events list into recurring event types grouped by identical titles
    Returns dictionary matching OpenAPI events response format for recurring events
    """
    # Filter to future events only if requested
    processed_events = filter_future_events(events) if future_only else events
    
    recurring_types = {}
    
    for event in processed_events:
        title = event.get('title', 'Untitled Event').strip()
        
        if title not in recurring_types:
            recurring_types[title] = {
                'count': 0,
                'events': []
            }
            
        recurring_types[title]['count'] += 1
        recurring_types[title]['events'].append(event)  # Store full event object, not just ID
    
    return recurring_types


def create_ical_from_events(events: List[Dict[str, Any]], calendar_name: str) -> str:
    """
    Pure function: Generate iCal content from events list
    Returns: iCal format string
    """
    cal = icalendar.Calendar()
    cal.add('prodid', '-//iCal Viewer//Filter-iCal.de//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('x-wr-calname', calendar_name)
    
    for event_data in events:
        event = icalendar.Event()
        event.add('summary', event_data['title'])
        event.add('dtstart', event_data['start'])
        event.add('dtend', event_data['end'])
        event.add('uid', f"{event_data['id']}@filter-ical.de")
        event.add('dtstamp', datetime.utcnow())
        
        if event_data.get('description'):
            event.add('description', event_data['description'])
        if event_data.get('location'):
            event.add('location', event_data['location'])
        if event_data.get('category'):
            event.add('categories', event_data['category'])
            
        cal.add_component(event)
    
    return cal.to_ical().decode('utf-8')