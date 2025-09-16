"""
Pure HTTP Operations - Rich Hickey Style
Pure async functions for HTTP operations with explicit error handling
No side effects, explicit data flow, composable functions
"""

import httpx
from typing import Tuple, Optional
from ..models import Event
from ..services.events import parse_ical_content


# === HTTP VALIDATION (Pure Functions) ===

async def fetch_url_content(url: str) -> Tuple[bool, str, str]:
    """
    Pure function: Fetch content from URL
    Returns (success, content_or_error_message, status_info)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            
            if response.status_code != 200:
                return False, f"HTTP {response.status_code}: Could not fetch calendar", f"HTTP {response.status_code}"
            
            content = response.text
            return True, content, "HTTP 200 OK"
            
    except httpx.TimeoutException:
        return False, "Request timeout - URL not accessible", "Timeout"
    except httpx.RequestError as e:
        return False, f"Network error: {str(e)}", "Network Error"
    except Exception as e:
        return False, f"Fetch error: {str(e)}", "Unknown Error"


async def validate_ical_url_http(url: str) -> Tuple[bool, str]:
    """
    Pure function: Validate iCal URL by fetching and checking content
    Combines URL validation + HTTP fetch + content validation
    """
    # Import pure validation functions
    from .calendar import is_valid_url_format, is_valid_ical_content
    
    # First validate URL format (pure function)
    if not is_valid_url_format(url):
        return False, "Invalid URL format"
    
    # Fetch content (I/O operation)
    success, content_or_error, _ = await fetch_url_content(url)
    if not success:
        return False, content_or_error
    
    # Validate iCal content (pure function)
    is_valid_content, validation_message = is_valid_ical_content(content_or_error)
    if not is_valid_content:
        return False, validation_message
    
    return True, "Valid iCal URL"


async def fetch_calendar_events(url: str) -> Tuple[bool, list[Event], str]:
    """
    Pure function: Fetch and parse events from iCal URL
    Returns (success, events_or_empty_list, error_message)
    """
    # Fetch content
    success, content_or_error, status = await fetch_url_content(url)
    if not success:
        return False, [], content_or_error
    
    # Parse content using existing pure function
    events = parse_ical_content(content_or_error)
    return True, events, "Events fetched successfully"


# === CALENDAR EVENT PROCESSING (Pure Functions) ===

def extract_event_categories(events: list[Event]) -> dict[str, int]:
    """
    Pure function: Extract categories from events with counts
    No side effects, explicit data flow
    """
    from ..services.events import extract_category_from_event
    
    category_counts = {}
    for event in events:
        category = extract_category_from_event(event)
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Sort by count (descending)
    return dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))


def create_calendar_workflow(name: str, url: str, user_id: str) -> dict:
    """
    Pure function: Create workflow data for calendar creation
    Returns workflow context for imperative shell to execute
    """
    return {
        "action": "create_calendar",
        "name": name,
        "url": url,
        "user_id": user_id,
        "steps": [
            "validate_input_data",
            "validate_url_format", 
            "fetch_and_validate_ical_content",
            "add_calendar_to_store",
            "return_calendar_entry"
        ]
    }


def get_events_workflow(calendar_id: str, calendar_url: str, use_cache: bool = True) -> dict:
    """
    Pure function: Create workflow data for fetching calendar events
    Returns workflow context for imperative shell to execute
    """
    return {
        "action": "get_events",
        "calendar_id": calendar_id,
        "calendar_url": calendar_url,
        "use_cache": use_cache,
        "steps": [
            "check_cache" if use_cache else "skip_cache",
            "fetch_from_url" if not use_cache else "fetch_if_cache_miss",
            "cache_events",
            "return_events"
        ]
    }