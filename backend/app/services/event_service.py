"""
Event Service - Business Logic Orchestration  
Rich Hickey: "Orchestrate pure functions with explicit state management"
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta

from ..data.schemas import AppState, EventData
from ..data.ical_parser import (
    fetch_ical_from_url, parse_ical_content, extract_categories_from_events,
    filter_events_by_categories, filter_events_by_date_range, generate_ical_content
)
from ..persistence.repositories import StateRepository


class ServiceResult(BaseModel):
    """Standard service result format"""
    success: bool = Field(..., description="Whether operation succeeded")
    data: Dict[str, Any] = Field(default_factory=dict, description="Result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Operation timestamp")


class EventService:
    """Event service for orchestrating event operations"""
    
    def __init__(self, repository: StateRepository):
        self.repository = repository
    
    def parse_calendar_from_url(self, url: str) -> ServiceResult:
        """Parse calendar from URL following OpenAPI contract"""
        try:
            if not url:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="URL parameter is required"
                )
            
            # Fetch iCal content from URL
            success, content, error_msg = fetch_ical_from_url(url)
            if not success:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message=f"Failed to fetch calendar: {error_msg}"
                )
            
            # Parse iCal content into events
            events, categories = parse_ical_content(content)
            
            # Convert EventData to dict format for JSON response
            events_dict = []
            for event in events:
                events_dict.append({
                    "uid": event.uid,
                    "summary": event.summary,
                    "description": event.description,
                    "location": event.location,
                    "dtstart": event.dtstart,
                    "dtend": event.dtend,
                    "categories": event.categories
                })
            
            return ServiceResult(
                success=True,
                data={
                    "events": events_dict,
                    "categories": categories,
                    "total_events": len(events_dict)
                },
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to parse calendar: {str(e)}"
            )
    
    def get_calendar_events(self, calendar_id: str, user_id: str, include_past: bool = False) -> ServiceResult:
        """Get events for a specific calendar following OpenAPI contract"""
        try:
            # Load current state
            state = self.repository.load_state()
            
            # Check if calendar exists and user has access
            if calendar_id not in state.calendars:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Calendar not found"
                )
            
            calendar = state.calendars[calendar_id]
            
            # Check ownership
            if calendar.user_id != user_id:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Access denied"
                )
            
            if not calendar.is_active:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Calendar not found"
                )
            
            # Try to get events from cache first
            events = []
            cache_status = "miss"
            
            if calendar_id in state.events_cache:
                events = state.events_cache[calendar_id]
                cache_status = "hit"
                # Check if cache is still valid (less than 1 hour old)
                # For now, we'll refresh every time for demo purposes
                cache_status = "refreshed"
                events = []
            
            # If no cached events, fetch fresh data
            if not events:
                success, content, error_msg = fetch_ical_from_url(calendar.url)
                if not success:
                    return ServiceResult(
                        success=False,
                        data={},
                        error_message=f"Failed to fetch calendar data: {error_msg}"
                    )
                
                # Parse events
                events, _ = parse_ical_content(content)
                cache_status = "refreshed"
                
                # Update cache in state
                new_events_cache = {**state.events_cache, calendar_id: events}
                new_state = AppState(
                    calendars=state.calendars,
                    communities=state.communities,
                    groups=state.groups,
                    filters=state.filters,
                    subscriptions=state.subscriptions,
                    filtered_calendars=state.filtered_calendars,
                    events_cache=new_events_cache,
                    version=state.version + 1
                )
                
                # Save updated state (async in background would be better)
                self.repository.save_state(new_state)
            
            # Filter past events if not included
            if not include_past:
                now = datetime.now(timezone.utc)
                filtered_events = []
                for event in events:
                    try:
                        # Parse event start time
                        if 'T' in event.dtstart:
                            if event.dtstart.endswith('Z'):
                                event_time = datetime.fromisoformat(event.dtstart.replace('Z', '+00:00'))
                            else:
                                event_time = datetime.strptime(event.dtstart, '%Y%m%dT%H%M%S').replace(tzinfo=timezone.utc)
                        else:
                            event_time = datetime.strptime(event.dtstart, '%Y%m%d').replace(tzinfo=timezone.utc)
                        
                        # Include events that haven't ended yet (add 1 day buffer for all-day events)
                        if event_time >= (now - timedelta(days=1)):
                            filtered_events.append(event)
                    except Exception:
                        # If we can't parse the date, include the event
                        filtered_events.append(event)
                
                events = filtered_events
            
            # Convert EventData to dict format for JSON response
            events_dict = []
            for event in events:
                events_dict.append({
                    "uid": event.uid,
                    "summary": event.summary,
                    "description": event.description,
                    "location": event.location,
                    "dtstart": event.dtstart,
                    "dtend": event.dtend,
                    "categories": event.categories
                })
            
            return ServiceResult(
                success=True,
                data={
                    "events": events_dict,
                    "total_count": len(events_dict),
                    "cache_status": cache_status
                },
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to get calendar events: {str(e)}"
            )
    
    def get_calendar_categories(self, calendar_id: str, user_id: str) -> ServiceResult:
        """Get event categories with counts for a calendar"""
        try:
            # First get all events
            events_result = self.get_calendar_events(calendar_id, user_id, include_past=True)
            if not events_result.success:
                return events_result
            
            events_data = events_result.data["events"]
            
            # Convert back to EventData objects for category processing
            events = []
            for event_dict in events_data:
                events.append(EventData(
                    uid=event_dict["uid"],
                    summary=event_dict["summary"],
                    description=event_dict["description"],
                    location=event_dict["location"],
                    dtstart=event_dict["dtstart"],
                    dtend=event_dict["dtend"],
                    categories=event_dict["categories"]
                ))
            
            # Extract categories with counts
            category_counts = extract_categories_from_events(events)
            
            return ServiceResult(
                success=True,
                data={
                    "categories": category_counts,
                    "total_events": len(events)
                },
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to get calendar categories: {str(e)}"
            )
    
    def generate_filtered_calendar(self, calendar_id: str, user_id: str, 
                                 selected_categories: List[str], filter_mode: str = "include",
                                 date_range_start: Optional[str] = None, 
                                 date_range_end: Optional[str] = None) -> ServiceResult:
        """Generate filtered iCal content"""
        try:
            # First get all events
            events_result = self.get_calendar_events(calendar_id, user_id, include_past=False)
            if not events_result.success:
                return events_result
            
            events_data = events_result.data["events"]
            
            # Convert back to EventData objects for filtering
            events = []
            for event_dict in events_data:
                events.append(EventData(
                    uid=event_dict["uid"],
                    summary=event_dict["summary"],
                    description=event_dict["description"],
                    location=event_dict["location"],
                    dtstart=event_dict["dtstart"],
                    dtend=event_dict["dtend"],
                    categories=event_dict["categories"]
                ))
            
            # Apply category filtering
            if selected_categories:
                events = filter_events_by_categories(events, selected_categories, filter_mode)
            
            # Apply date range filtering
            if date_range_start or date_range_end:
                events = filter_events_by_date_range(events, date_range_start, date_range_end)
            
            # Generate iCal content
            calendar_name = f"Filtered Calendar - {filter_mode} {', '.join(selected_categories) if selected_categories else 'All Events'}"
            ical_content = generate_ical_content(events, calendar_name)
            
            return ServiceResult(
                success=True,
                data={
                    "ical_content": ical_content,
                    "total_events": len(events),
                    "filter_applied": {
                        "selected_categories": selected_categories,
                        "filter_mode": filter_mode,
                        "date_range": {
                            "start": date_range_start,
                            "end": date_range_end
                        }
                    }
                },
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to generate filtered calendar: {str(e)}"
            )