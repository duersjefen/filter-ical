"""
Preference Service - Business Logic Orchestration
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


class PreferenceService:
    """Preference service for orchestrating user preference operations"""
    
    def __init__(self, repository: StateRepository):
        self.repository = repository
    
    def get_calendar_preferences(self, calendar_id: str, user_id: str) -> ServiceResult:
        """Get preferences for a specific calendar"""
        try:
            if not calendar_id:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Calendar not found"
                )
            
            # Default preferences matching OpenAPI schema
            default_preferences = {
                "calendar_id": calendar_id,
                "user_id": user_id,
                "view_mode": "month",
                "time_zone": "UTC",
                "first_day_of_week": 1,  # Monday
                "show_weekends": True,
                "default_view": "month",
                "event_display_format": "standard",
                "notifications_enabled": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            return ServiceResult(
                success=True,
                data={"preferences": default_preferences},
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to get calendar preferences: {str(e)}"
            )
    
    def update_calendar_preferences_workflow(self, calendar_id: str, 
                                           preferences: Dict[str, Any], user_id: str) -> ServiceResult:
        """Update calendar preferences following OpenAPI contract"""
        try:
            if not calendar_id:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Calendar not found"
                )
            
            # Create updated preferences object
            updated_preferences = {
                "calendar_id": calendar_id,
                "user_id": user_id,
                **preferences,  # Merge in provided preferences
                "updated_at": datetime.now().isoformat()
            }
            
            return ServiceResult(
                success=True,
                data={"preferences": updated_preferences},
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to update calendar preferences: {str(e)}"
            )