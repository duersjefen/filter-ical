"""
Calendar Service - Business Logic Orchestration
Rich Hickey: "Orchestrate pure functions with explicit state management"
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ..data.schemas import AppState, CalendarData
from ..data.ical_parser import fetch_ical_from_url, parse_ical_content
from ..persistence.repositories import StateRepository


class ServiceResult(BaseModel):
    """Standard service result format"""
    success: bool = Field(..., description="Whether operation succeeded")
    data: Dict[str, Any] = Field(default_factory=dict, description="Result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Operation timestamp")


class CalendarService:
    """Calendar service for orchestrating calendar operations"""
    
    def __init__(self, repository: StateRepository):
        self.repository = repository
    
    def list_user_calendars(self, user_id: str) -> ServiceResult:
        """List all calendars for a user"""
        try:
            # Load current state from database
            state = self.repository.load_state()
            
            # Filter calendars by user ID
            user_calendars = []
            for calendar in state.calendars.values():
                if calendar.user_id == user_id and calendar.is_active:
                    user_calendars.append({
                        "id": calendar.id,
                        "name": calendar.name,
                        "url": calendar.url,
                        "user_id": calendar.user_id,
                        "created_at": calendar.created_at,
                        "updated_at": calendar.updated_at,
                        "is_active": calendar.is_active
                    })
            
            return ServiceResult(
                success=True,
                data={"calendars": user_calendars},
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to list calendars: {str(e)}"
            )
    
    def create_calendar_workflow(self, name: str, url: str, user_id: str) -> ServiceResult:
        """Create a new calendar following OpenAPI contract"""
        try:
            # Validate inputs
            if not name or not url:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Missing required fields: name and url"
                )
            
            if not name.strip():
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Calendar name cannot be empty"
                )
            
            # Validate URL by attempting to fetch it
            success, content, error_msg = fetch_ical_from_url(url)
            if not success:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message=f"Invalid calendar URL: {error_msg}"
                )
            
            # Validate that URL contains parseable iCal content
            try:
                events, categories = parse_ical_content(content)
                print(f"Successfully parsed {len(events)} events with {len(categories)} categories")
            except Exception as e:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message=f"URL does not contain valid iCal content: {str(e)}"
                )
            
            # Load current state
            state = self.repository.load_state()
            
            # Check for duplicate URLs for this user
            for existing_calendar in state.calendars.values():
                if (existing_calendar.user_id == user_id and 
                    existing_calendar.url == url and 
                    existing_calendar.is_active):
                    return ServiceResult(
                        success=False,
                        data={},
                        error_message="Calendar with this URL already exists"
                    )
            
            # Create calendar object matching OpenAPI schema
            calendar_id = f"cal-{uuid.uuid4()}"
            now = datetime.utcnow().isoformat() + "Z"
            
            calendar_data = CalendarData(
                id=calendar_id,
                name=name.strip(),
                url=url,
                user_id=user_id,
                created_at=now,
                updated_at=now,
                is_active=True
            )
            
            # Add calendar to state
            new_calendars = {**state.calendars, calendar_id: calendar_data}
            new_state = AppState(
                calendars=new_calendars,
                communities=state.communities,
                groups=state.groups,
                filters=state.filters,
                subscriptions=state.subscriptions,
                filtered_calendars=state.filtered_calendars,
                events_cache=state.events_cache,
                version=state.version + 1
            )
            
            # Save to database
            save_success = self.repository.save_state(new_state)
            if not save_success:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Failed to save calendar to database"
                )
            
            # Return calendar object matching OpenAPI schema
            calendar_response = {
                "id": calendar_data.id,
                "name": calendar_data.name,
                "url": calendar_data.url,
                "user_id": calendar_data.user_id,
                "created_at": calendar_data.created_at,
                "updated_at": calendar_data.updated_at,
                "is_active": calendar_data.is_active
            }
            
            return ServiceResult(
                success=True,
                data={"calendar": calendar_response},
                error_message=None
            )
            
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to create calendar: {str(e)}"
            )
    
    def delete_calendar_workflow(self, calendar_id: str, user_id: str) -> ServiceResult:
        """Delete a calendar following OpenAPI contract"""
        try:
            # Load current state
            state = self.repository.load_state()
            
            # Check if calendar exists
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
                    error_message="Access denied - you can only delete your own calendars"
                )
            
            # Check if already deleted
            if not calendar.is_active:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Calendar not found"
                )
            
            # Soft delete - mark as inactive
            updated_calendar = CalendarData(
                id=calendar.id,
                name=calendar.name,
                url=calendar.url,
                user_id=calendar.user_id,
                created_at=calendar.created_at,
                updated_at=datetime.utcnow().isoformat() + "Z",
                is_active=False
            )
            
            # Update state
            new_calendars = {**state.calendars, calendar_id: updated_calendar}
            
            # Also clean up related data
            new_filters = {
                fid: fdata for fid, fdata in state.filters.items() 
                if fdata.calendar_id != calendar_id
            }
            
            new_events_cache = {
                cid: events for cid, events in state.events_cache.items() 
                if cid != calendar_id
            }
            
            new_state = AppState(
                calendars=new_calendars,
                communities=state.communities,
                groups=state.groups,
                filters=new_filters,
                subscriptions=state.subscriptions,
                filtered_calendars=state.filtered_calendars,
                events_cache=new_events_cache,
                version=state.version + 1
            )
            
            # Save to database
            save_success = self.repository.save_state(new_state)
            if not save_success:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Failed to delete calendar from database"
                )
            
            return ServiceResult(
                success=True,
                data={"message": "Calendar deleted successfully"},
                error_message=None
            )
            
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to delete calendar: {str(e)}"
            )
    
    def get_calendar_by_id(self, calendar_id: str, user_id: str) -> ServiceResult:
        """Get a specific calendar by ID"""
        try:
            state = self.repository.load_state()
            
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
            
            calendar_response = {
                "id": calendar.id,
                "name": calendar.name,
                "url": calendar.url,
                "user_id": calendar.user_id,
                "created_at": calendar.created_at,
                "updated_at": calendar.updated_at,
                "is_active": calendar.is_active
            }
            
            return ServiceResult(
                success=True,
                data={"calendar": calendar_response},
                error_message=None
            )
            
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to get calendar: {str(e)}"
            )