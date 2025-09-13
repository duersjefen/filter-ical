"""
Calendar Service - Business logic for calendar operations
Coordinates between storage and event processing
"""

import httpx
import re
from typing import List, Tuple, Dict, Any
from ..models import CalendarEntry, Event
from ..storage.persistence import PersistentStore
from .events import fetch_ical_events, extract_category_from_event


class CalendarService:
    """Business logic for calendar operations"""
    
    def __init__(self, store: PersistentStore):
        self.store = store
    
    async def validate_ical_url(self, url: str) -> Tuple[bool, str]:
        """Validate if a URL points to a valid iCal resource"""
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False, "Invalid URL format"
        
        # Try to fetch and validate content
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True)
                
                if response.status_code != 200:
                    return False, f"HTTP {response.status_code}: Could not fetch calendar"
                
                content = response.text
                
                # Basic iCal content validation
                if not content.strip():
                    return False, "Empty response"
                
                # Check for iCal markers
                content_lower = content.lower()
                if 'begin:vcalendar' not in content_lower:
                    return False, "Not a valid iCal file (missing VCALENDAR)"
                
                if 'version:2.0' not in content_lower:
                    return False, "Not iCal version 2.0"
                
                # Check for at least one event
                if 'begin:vevent' not in content_lower:
                    return False, "iCal file contains no events"
                
                return True, "Valid iCal URL"
                
        except httpx.TimeoutException:
            return False, "Request timeout - URL not accessible"
        except httpx.RequestError as e:
            return False, f"Network error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_calendars(self, user_id: str) -> List[CalendarEntry]:
        """Get all calendars for a user"""
        return self.store.get_calendars(user_id)
    
    async def create_calendar(self, name: str, url: str, user_id: str) -> CalendarEntry:
        """Create a new calendar after validation"""
        # Note: URL validation should be done by the caller
        return self.store.add_calendar(name, url, user_id)
    
    def delete_calendar(self, calendar_id: str, user_id: str) -> bool:
        """Delete a calendar"""
        return self.store.delete_calendar(calendar_id, user_id)
    
    async def get_calendar_events(self, calendar_id: str) -> List[Event]:
        """Get events for a calendar (with caching)"""
        # Try cache first
        cached_events = self.store.get_cached_events(calendar_id)
        if cached_events:
            return cached_events
        
        # Fetch fresh data
        calendar = self.store.get_calendar(calendar_id)
        if not calendar:
            return []
        
        events = await fetch_ical_events(calendar.url)
        
        # Cache the results
        if events:
            self.store.cache_events(calendar_id, events)
        
        return events
    
    async def get_calendar_categories(self, calendar_id: str) -> Dict[str, int]:
        """Get categories (event types) for a calendar with counts"""
        events = await self.get_calendar_events(calendar_id)
        
        category_counts = {}
        for event in events:
            category = extract_category_from_event(event)
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Sort by count (descending)
        return dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))