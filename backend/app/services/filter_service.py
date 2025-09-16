"""
Filter Service - Business Logic Orchestration
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


class FilterService:
    """Filter service for orchestrating filter operations"""
    
    def __init__(self, repository: StateRepository):
        self.repository = repository
    
    def list_user_filtered_calendars(self, user_id: str) -> ServiceResult:
        """List all filtered calendars for a user"""
        try:
            # For now, return empty list - will implement with actual storage later
            return ServiceResult(
                success=True,
                data={"filtered_calendars": []},
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to list filtered calendars: {str(e)}"
            )
    
    def create_filtered_calendar_workflow(self, name: str, calendar_id: str, 
                                        filter_config: Dict[str, Any], user_id: str) -> ServiceResult:
        """Create a filtered calendar following OpenAPI contract"""
        try:
            # Validate inputs
            if not name or not calendar_id or not filter_config:
                return ServiceResult(
                    success=False,
                    data={},
                    error_message="Missing required fields: name, calendar_id, filter_config"
                )
            
            # Create filtered calendar object matching OpenAPI schema
            filtered_calendar_id = f"filtered_{user_id}_{int(datetime.now().timestamp())}"
            filtered_calendar = {
                "id": filtered_calendar_id,
                "name": name,
                "source_calendar_id": calendar_id,
                "filter_config": filter_config,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_active": True,
                "public_token": None  # Will be generated when making public
            }
            
            return ServiceResult(
                success=True,
                data={"filtered_calendar": filtered_calendar},
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
            # Validate filtered calendar exists and belongs to user
            # For now, we'll simulate this - in real implementation would check database
            if not filtered_calendar_id:
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
            
            # Create updated filtered calendar object
            updated_calendar = {
                "id": filtered_calendar_id,
                "user_id": user_id,
                "updated_at": datetime.now().isoformat(),
                **update_fields
            }
            
            return ServiceResult(
                success=True,
                data={"filtered_calendar": updated_calendar},
                error_message=None
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                data={},
                error_message=f"Failed to update filtered calendar: {str(e)}"
            )