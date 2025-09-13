"""
Event Processing Service - Pure functions for calendar event handling
No side effects, only data transformation
"""

import httpx
from icalendar import Calendar
import recurring_ical_events
from datetime import datetime, date
from typing import List, Any
from ..models import Event


def parse_date_to_string(dt: Any) -> str:
    """Convert various date formats to ISO string"""
    if dt is None:
        return ""
    
    if isinstance(dt, datetime):
        return dt.isoformat()
    elif isinstance(dt, date):
        return dt.isoformat()
    elif hasattr(dt, 'dt') and dt.dt:
        return parse_date_to_string(dt.dt)
    elif isinstance(dt, str):
        return dt
    else:
        return str(dt)


def ical_component_to_event(component) -> Event:
    """Convert icalendar component to Event dataclass - original version"""
    return Event(
        uid=str(component.get('UID', '')),
        summary=str(component.get('SUMMARY', '')),
        dtstart=parse_date_to_string(component.get('DTSTART')),
        dtend=parse_date_to_string(component.get('DTEND')),
        location=str(component.get('LOCATION', '')) if component.get('LOCATION') else None,
        description=str(component.get('DESCRIPTION', '')) if component.get('DESCRIPTION') else None,
        raw=component.to_ical().decode('utf-8', errors='ignore')
    )


def parse_ical_content(content: str) -> List[Event]:
    """Parse iCal content and return list of events - original version"""
    try:
        calendar = Calendar.from_ical(content)
        events = []
        
        for component in calendar.walk():
            if component.name == "VEVENT":
                try:
                    event = ical_component_to_event(component)
                    events.append(event)
                except Exception as e:
                    print(f"Error parsing event: {e}")
                    continue
        
        return events
    except Exception as e:
        print(f"Error parsing calendar: {e}")
        return []


def ical_component_to_event_with_fallback(component) -> Event:
    """Enhanced version with better error handling"""
    try:
        dtstart = component.get('DTSTART')
        dtend = component.get('DTEND')
        
        dtstart_str = parse_date_to_string_enhanced(dtstart) if dtstart else ""
        dtend_str = parse_date_to_string_enhanced(dtend) if dtend else ""
        
        return Event(
            uid=str(component.get('UID', '')),
            summary=str(component.get('SUMMARY', 'Untitled Event')),
            dtstart=dtstart_str,
            dtend=dtend_str,
            location=str(component.get('LOCATION', '')) if component.get('LOCATION') else None,
            description=str(component.get('DESCRIPTION', '')) if component.get('DESCRIPTION') else None,
            raw=component.to_ical().decode('utf-8', errors='ignore')
        )
    except Exception as e:
        print(f"Error parsing event component: {e}")
        # Return a minimal event to avoid breaking the entire calendar
        return Event(
            uid="error-" + str(hash(str(component))),
            summary="Error parsing event",
            dtstart="",
            dtend="",
            location=None,
            description=f"Error: {str(e)}",
            raw=""
        )


def parse_date_to_string_enhanced(dt: Any) -> str:
    """Enhanced date parsing with better error handling"""
    if dt is None:
        return ""
    
    try:
        if isinstance(dt, datetime):
            return dt.isoformat()
        elif isinstance(dt, date):
            return dt.isoformat() + "T00:00:00"
        elif hasattr(dt, 'dt') and dt.dt:
            if isinstance(dt.dt, datetime):
                return dt.dt.isoformat()
            elif isinstance(dt.dt, date):
                return dt.dt.isoformat() + "T00:00:00"
        elif isinstance(dt, str):
            return dt
        else:
            return str(dt)
    except Exception as e:
        print(f"Error parsing date {dt}: {e}")
        return ""


async def fetch_ical_events(url: str) -> List[Event]:
    """Fetch and parse events from iCal URL"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            content = response.text
            return parse_ical_content(content)
    except Exception as e:
        print(f"Error fetching calendar from {url}: {e}")
        return []


def extract_category_from_event(event: Event) -> str:
    """Extract category from existing event data"""
    # Simple approach: use the event summary as the category
    return event.summary or 'Uncategorized'


def generate_ical_content(events: List[Event], calendar_name: str, categories: set) -> str:
    """Generate iCal content from filtered events"""
    from icalendar import Calendar, Event as ICalEvent
    
    cal = Calendar()
    cal.add('prodid', '-//iCal Viewer//iCal Viewer//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', calendar_name)
    
    for event in events:
        # Skip events that don't match the requested categories
        event_category = extract_category_from_event(event)
        if categories and event_category not in categories:
            continue
            
        # Create iCal event from raw data or construct from fields
        try:
            if event.raw and event.raw.strip():
                # Use raw iCal data if available
                ical_event = ICalEvent.from_ical(event.raw)
                cal.add_component(ical_event)
            else:
                # Construct from individual fields
                ical_event = ICalEvent()
                ical_event.add('uid', event.uid)
                ical_event.add('summary', event.summary)
                if event.dtstart:
                    ical_event.add('dtstart', datetime.fromisoformat(event.dtstart.replace('Z', '+00:00')))
                if event.dtend:
                    ical_event.add('dtend', datetime.fromisoformat(event.dtend.replace('Z', '+00:00')))
                if event.location:
                    ical_event.add('location', event.location)
                if event.description:
                    ical_event.add('description', event.description)
                cal.add_component(ical_event)
        except Exception as e:
            print(f"Error adding event to calendar: {e}")
            continue
    
    return cal.to_ical().decode('utf-8')