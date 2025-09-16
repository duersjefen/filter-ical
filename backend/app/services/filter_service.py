"""
Filter Service - Business Logic Orchestration
Rich Hickey: "Orchestrate pure functions with explicit state management"
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import secrets

from ..data.schemas import AppState, FilteredCalendarData
from ..persistence.repositories import StateRepository


class ServiceResult(BaseModel):
    """Standard service result format"""
    success: bool = Field(..., description="Whether operation succeeded")
    data: Dict[str, Any] = Field(default_factory=dict, description="Result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Operation timestamp")


class FilterService:
    """Filter service for orchestrating filter operations"""
    
    def __init__(self, repository: StateRepository):
        self.repository = repository
    
    def list_user_filtered_calendars(self, user_id: str) -> ServiceResult:
        """List all filtered calendars for a user"""
        try:
            # Load current state from database
            state = self.repository.load_state()
            
            # Filter filtered calendars by user ID
            user_filtered_calendars = []
            for filtered_cal in state.filtered_calendars.values():
                if filtered_cal.user_id == user_id and filtered_cal.is_active:
                    # Build URLs
                    calendar_url = f"https://filter-ical.de/cal/{filtered_cal.public_token}.ics" if filtered_cal.public_token else None
                    preview_url = f"https://filter-ical.de/cal/{filtered_cal.public_token}" if filtered_cal.public_token else None
                    
                    user_filtered_calendars.append({
                        "id": filtered_cal.id,
                        "name": filtered_cal.name,
                        "source_calendar_id": filtered_cal.source_calendar_id,
                        "filter_config": filtered_cal.filter_config,
                        "public_token": filtered_cal.public_token,
                        "calendar_url": calendar_url,
                        "preview_url": preview_url,
                        "user_id": filtered_cal.user_id,
                        "created_at": filtered_cal.created_at,
                        "updated_at": filtered_cal.updated_at,
                        "last_accessed": filtered_cal.last_accessed,
                        "access_count": filtered_cal.access_count,
                        "is_active": filtered_cal.is_active
                    })
            
            return ServiceResult(
                success=True,
                data={"filtered_calendars": user_filtered_calendars},
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to list filtered calendars: {str(e)}"
            )
    
    def create_filtered_calendar_workflow(self, name: str, source_calendar_id: str, 
                                        filter_config: Dict[str, Any], user_id: str) -> ServiceResult:
        """Create a filtered calendar following OpenAPI contract"""
        try:
            # Validate inputs
            if not name or not source_calendar_id or not filter_config:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Missing required fields: name, source_calendar_id, filter_config"
                )
            
            if not name.strip():
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Filtered calendar name cannot be empty"
                )
            
            # Load current state
            state = self.repository.load_state()
            
            # Verify source calendar exists and belongs to user
            if source_calendar_id not in state.calendars:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Source calendar not found"
                )
            
            source_calendar = state.calendars[source_calendar_id]
            if source_calendar.user_id != user_id or not source_calendar.is_active:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Source calendar not found or access denied"
                )
            
            # Generate IDs and tokens
            filtered_calendar_id = f"filtered-{uuid.uuid4()}"
            public_token = f"tok_{secrets.token_urlsafe(16)}"
            now = datetime.utcnow().isoformat() + "Z"
            
            # Create filtered calendar data
            filtered_calendar_data = FilteredCalendarData(
                id=filtered_calendar_id,
                name=name.strip(),
                source_calendar_id=source_calendar_id,
                filter_config=filter_config,
                public_token=public_token,
                user_id=user_id,
                created_at=now,
                updated_at=now,
                last_accessed=None,
                access_count=0,
                is_active=True
            )
            
            # Add to state
            new_filtered_calendars = {**state.filtered_calendars, filtered_calendar_id: filtered_calendar_data}
            new_state = AppState(
                calendars=state.calendars,
                communities=state.communities,
                groups=state.groups,
                filters=state.filters,
                subscriptions=state.subscriptions,
                filtered_calendars=new_filtered_calendars,
                events_cache=state.events_cache,
                version=state.version + 1
            )
            
            # Save to database
            save_success = self.repository.save_state(new_state)
            if not save_success:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Failed to save filtered calendar to database"
                )
            
            # Return response matching OpenAPI schema
            calendar_url = f"https://filter-ical.de/cal/{public_token}.ics"
            preview_url = f"https://filter-ical.de/cal/{public_token}"
            
            filtered_calendar_response = {
                "id": filtered_calendar_data.id,
                "name": filtered_calendar_data.name,
                "source_calendar_id": filtered_calendar_data.source_calendar_id,
                "filter_config": filtered_calendar_data.filter_config,
                "public_token": filtered_calendar_data.public_token,
                "calendar_url": calendar_url,
                "preview_url": preview_url,
                "user_id": filtered_calendar_data.user_id,
                "created_at": filtered_calendar_data.created_at,
                "updated_at": filtered_calendar_data.updated_at,
                "last_accessed": filtered_calendar_data.last_accessed,
                "access_count": filtered_calendar_data.access_count,
                "is_active": filtered_calendar_data.is_active
            }
            
            return ServiceResult(
                success=True,
                data={"filtered_calendar": filtered_calendar_response},
                error_message=None
            )
            
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to create filtered calendar: {str(e)}"
            )
    
    def update_filtered_calendar_workflow(self, filtered_calendar_id: str, 
                                        update_data: Dict[str, Any], user_id: str) -> ServiceResult:
        """Update a filtered calendar following OpenAPI contract"""
        try:
            # Load current state
            state = self.repository.load_state()
            
            # Check if filtered calendar exists
            if filtered_calendar_id not in state.filtered_calendars:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Filtered calendar not found"
                )
            
            filtered_calendar = state.filtered_calendars[filtered_calendar_id]
            
            # Check ownership
            if filtered_calendar.user_id != user_id:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Access denied - you can only update your own filtered calendars"
                )
            
            # Check if active
            if not filtered_calendar.is_active:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Filtered calendar not found"
                )
            
            # Validate update data
            allowed_fields = ["name", "filter_config"]
            update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if not update_fields:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="No valid fields to update"
                )
            
            # Validate name if provided
            if "name" in update_fields and not update_fields["name"].strip():
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Filtered calendar name cannot be empty"
                )
            
            # Create updated filtered calendar
            updated_filtered_calendar = FilteredCalendarData(
                id=filtered_calendar.id,
                name=update_fields.get("name", filtered_calendar.name).strip() if "name" in update_fields else filtered_calendar.name,
                source_calendar_id=filtered_calendar.source_calendar_id,
                filter_config=update_fields.get("filter_config", filtered_calendar.filter_config),
                public_token=filtered_calendar.public_token,
                user_id=filtered_calendar.user_id,
                created_at=filtered_calendar.created_at,
                updated_at=datetime.utcnow().isoformat() + "Z",
                last_accessed=filtered_calendar.last_accessed,
                access_count=filtered_calendar.access_count,
                is_active=filtered_calendar.is_active
            )
            
            # Update state
            new_filtered_calendars = {**state.filtered_calendars, filtered_calendar_id: updated_filtered_calendar}
            new_state = AppState(
                calendars=state.calendars,
                communities=state.communities,
                groups=state.groups,
                filters=state.filters,
                subscriptions=state.subscriptions,
                filtered_calendars=new_filtered_calendars,
                events_cache=state.events_cache,
                version=state.version + 1
            )
            
            # Save to database
            save_success = self.repository.save_state(new_state)
            if not save_success:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Failed to update filtered calendar in database"
                )
            
            return ServiceResult(
                success=True,
                data={"message": "Filtered calendar updated successfully"},
                error_message=None
            )
            
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to update filtered calendar: {str(e)}"
            )
    
    def delete_filtered_calendar_workflow(self, filtered_calendar_id: str, user_id: str) -> ServiceResult:
        """Delete (deactivate) a filtered calendar"""
        try:
            # Load current state
            state = self.repository.load_state()
            
            # Check if filtered calendar exists
            if filtered_calendar_id not in state.filtered_calendars:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Filtered calendar not found"
                )
            
            filtered_calendar = state.filtered_calendars[filtered_calendar_id]
            
            # Check ownership
            if filtered_calendar.user_id != user_id:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Access denied"
                )
            
            # Check if already deleted
            if not filtered_calendar.is_active:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Filtered calendar not found"
                )
            
            # Soft delete - mark as inactive
            deleted_filtered_calendar = FilteredCalendarData(
                id=filtered_calendar.id,
                name=filtered_calendar.name,
                source_calendar_id=filtered_calendar.source_calendar_id,
                filter_config=filtered_calendar.filter_config,
                public_token=filtered_calendar.public_token,
                user_id=filtered_calendar.user_id,
                created_at=filtered_calendar.created_at,
                updated_at=datetime.utcnow().isoformat() + "Z",
                last_accessed=filtered_calendar.last_accessed,
                access_count=filtered_calendar.access_count,
                is_active=False
            )
            
            # Update state
            new_filtered_calendars = {**state.filtered_calendars, filtered_calendar_id: deleted_filtered_calendar}
            new_state = AppState(
                calendars=state.calendars,
                communities=state.communities,
                groups=state.groups,
                filters=state.filters,
                subscriptions=state.subscriptions,
                filtered_calendars=new_filtered_calendars,
                events_cache=state.events_cache,
                version=state.version + 1
            )
            
            # Save to database
            save_success = self.repository.save_state(new_state)
            if not save_success:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Failed to delete filtered calendar from database"
                )
            
            return ServiceResult(
                success=True,
                data={"message": "Filtered calendar deleted successfully"},
                error_message=None
            )
            
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to delete filtered calendar: {str(e)}"
            )
    
    def get_filtered_calendar_by_token(self, token: str) -> ServiceResult:
        """Get filtered calendar by public token for public access"""
        try:
            # Load current state
            state = self.repository.load_state()
            
            # Find filtered calendar by token
            filtered_calendar = None
            for fc in state.filtered_calendars.values():
                if fc.public_token == token and fc.is_active:
                    filtered_calendar = fc
                    break
            
            if not filtered_calendar:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Filtered calendar not found"
                )
            
            # Update access stats
            updated_filtered_calendar = FilteredCalendarData(
                id=filtered_calendar.id,
                name=filtered_calendar.name,
                source_calendar_id=filtered_calendar.source_calendar_id,
                filter_config=filtered_calendar.filter_config,
                public_token=filtered_calendar.public_token,
                user_id=filtered_calendar.user_id,
                created_at=filtered_calendar.created_at,
                updated_at=filtered_calendar.updated_at,
                last_accessed=datetime.utcnow().isoformat() + "Z",
                access_count=filtered_calendar.access_count + 1,
                is_active=filtered_calendar.is_active
            )
            
            # Update state (background task in real implementation)
            new_filtered_calendars = {**state.filtered_calendars, filtered_calendar.id: updated_filtered_calendar}
            new_state = AppState(
                calendars=state.calendars,
                communities=state.communities,
                groups=state.groups,
                filters=state.filters,
                subscriptions=state.subscriptions,
                filtered_calendars=new_filtered_calendars,
                events_cache=state.events_cache,
                version=state.version + 1
            )
            
            # Save updated stats
            self.repository.save_state(new_state)
            
            return ServiceResult(
                success=True,
                data={"filtered_calendar": updated_filtered_calendar},
                error_message=None
            )
            
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to get filtered calendar: {str(e)}"
            )