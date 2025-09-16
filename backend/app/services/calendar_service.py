"""
Calendar Service - Business Logic Orchestration
Rich Hickey: "Orchestrate pure functions with explicit state management"
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from ..data.schemas import AppState, StateTransition, QueryResult
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
            # For now, return empty list - will implement with actual storage later
            return ServiceResult(
                success=True,
                data={"calendars": []},
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
            
            # Create calendar object matching OpenAPI schema
            calendar_id = f"cal_{user_id}_{int(datetime.now().timestamp())}"
            calendar = {
                "id": calendar_id,
                "name": name,
                "url": url,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_active": True
            }
            
            return ServiceResult(
                success=True,
                data={"calendar": calendar},
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
            # For now, simulate successful deletion
            # In real implementation, would check ownership and delete from storage
            if not calendar_id:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Calendar not found"
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