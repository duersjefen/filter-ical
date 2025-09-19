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
        
        # Check if event is recurring (has RRULE)
        is_recurring = component.get('RRULE') is not None
        
        # Extract event_type - use event title as the event type for group mapping
        # The recurring event names themselves ARE the event types
        categories = component.get('CATEGORIES')
        if categories:
            # Handle icalendar vCategory objects
            if hasattr(categories, 'to_ical'):
                event_type = categories.to_ical().decode('utf-8').split(',')[0].strip()
            else:
                event_type = str(categories).split(',')[0].strip()
            
            # For domain calendars: if event_type is generic "Exter", use event title as event type
            # This makes recurring event names the actual event types for group mapping
            if event_type.lower() in ['exter', 'domain'] and title:
                event_type = title.strip()
        else:
            # Use event title as event_type - recurring event names are the event types
            event_type = title.strip() if title else 'Event'
        
        return {
            'id': f"evt_{uuid.uuid4().hex[:8]}",
            'calendar_id': calendar_id,
            'title': title,
            'start': start_dt,
            'end': end_dt,
            'event_type': event_type,
            'description': description,
            'location': location,
            'is_recurring': is_recurring,
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
            
        # Use recurring-ical-events library to handle all events (including recurring ones)
        # This avoids processing the same events twice
        try:
            start_date = datetime.now().replace(day=1, month=1) 
            end_date = datetime.now().replace(year=datetime.now().year + 2)
            
            recurring_events = recurring_ical_events.of(calendar).between(start_date, end_date)
            
            events = []
            seen_events = set()  # Track processed events to avoid duplicates
            
            # Convert events to our format with deduplication
            for event in recurring_events:
                if hasattr(event, 'get'):
                    event_data = extract_event_data(event, calendar_id)
                    if event_data:
                        # Create a unique key based on event content (not ID)
                        event_key = (
                            event_data['title'],
                            event_data['start'],
                            event_data['end'],
                            event_data['description'],
                            event_data['location']
                        )
                        
                        # Only add if we haven't seen this exact event before
                        if event_key not in seen_events:
                            seen_events.add(event_key)
                            events.append(event_data)
                            
        except Exception:
            # Fallback: Process all VEVENT components if recurring events fail
            events = []
            for component in calendar.walk():
                if component.name == "VEVENT":
                    event_data = extract_event_data(component, calendar_id)
                    if event_data:
                        events.append(event_data)
            
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


def events_to_event_types(events: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Pure function: Transform events list into event types summary
    Returns dictionary matching OpenAPI event types response format
    """
    event_types = {}
    
    for event in events:
        event_type = event.get('event_type', 'Uncategorized')
        
        if event_type not in event_types:
            event_types[event_type] = {
                'count': 0,
                'events': []
            }
            
        event_types[event_type]['count'] += 1
        event_types[event_type]['events'].append(event['id'])
    
    return event_types


def split_ungrouped_events_by_type(events_by_type: Dict[str, Dict[str, Any]], ungrouped_event_types: List[str], events_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Pure function: Split ungrouped event types into recurring vs unique categories
    Returns: {'recurring': [...], 'unique': [...]} with event type objects including name and count
    """
    recurring_types = []
    unique_types = []
    
    # Create a mapping of event_type -> actual events for checking is_recurring
    events_by_event_type = {}
    for event in events_data:
        event_type = event.get('event_type', '')
        if event_type not in events_by_event_type:
            events_by_event_type[event_type] = []
        events_by_event_type[event_type].append(event)
    
    for event_type_name in ungrouped_event_types:
        if event_type_name in events_by_type:
            type_data = events_by_type[event_type_name]
            event_count = type_data.get('count', 0)
            
            # Determine if this event type is primarily recurring or unique
            # Use count-based logic: count > 1 means recurring, count = 1 means unique
            is_recurring_type = event_count > 1
            
            event_type_obj = {
                'name': event_type_name,
                'count': event_count
            }
            
            if is_recurring_type:
                recurring_types.append(event_type_obj)
            else:
                unique_types.append(event_type_obj)
    
    return {
        'recurring': recurring_types,
        'unique': unique_types
    }


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
        
        # Format event for API response with proper ISO dates and timezone handling
        formatted_event = dict(event)
        if 'start' in formatted_event and hasattr(formatted_event['start'], 'isoformat'):
            start_dt = formatted_event['start']
            # Ensure timezone-aware datetime for proper ISO formatting
            if hasattr(start_dt, 'tzinfo') and start_dt.tzinfo is None:
                from datetime import timezone
                start_dt = start_dt.replace(tzinfo=timezone.utc)
            formatted_event['start'] = start_dt.isoformat() + ('Z' if start_dt.tzinfo else '')
        if 'end' in formatted_event and hasattr(formatted_event['end'], 'isoformat'):
            end_dt = formatted_event['end']
            # Ensure timezone-aware datetime for proper ISO formatting
            if hasattr(end_dt, 'tzinfo') and end_dt.tzinfo is None:
                from datetime import timezone
                end_dt = end_dt.replace(tzinfo=timezone.utc)
            formatted_event['end'] = end_dt.isoformat() + ('Z' if end_dt.tzinfo else '')
            
        recurring_types[title]['events'].append(formatted_event)
    
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
        if event_data.get('event_type'):
            event.add('categories', event_data['event_type'])
            
        cal.add_component(event)
    
    return cal.to_ical().decode('utf-8')