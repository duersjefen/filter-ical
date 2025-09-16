"""
Community Service - Business Logic Orchestration
Rich Hickey: "Orchestrate pure functions with explicit state management"
"""

from typing import Tuple, Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from ..data.schemas import AppState, StateTransition, CommunityData, QueryResult
from ..domain.community import (
    create_community, update_community_calendar_url, find_community_by_path,
    get_community_groups, validate_community_data, add_default_groups_to_community
)
from ..persistence.repositories import StateRepository
from ..data.groups import create_default_groups


# Pydantic models for API documentation
class CommunityCreateRequest(BaseModel):
    """Request model for creating a community"""
    name: str = Field(..., description="Community name", example="BCC Community Calendar")
    description: str = Field(..., description="Community description", example="Community calendar for BCC events")
    url_path: str = Field(..., description="URL path for community", example="/exter")
    password: str = Field(..., description="Community access password", example="bcc2024")
    calendar_url: str = Field(..., description="Source calendar URL", example="https://widgets.bcc.no/ical-xyz/Portal-Calendar.ics")
    admin_emails: List[str] = Field(..., description="Administrator email addresses", example=["admin@example.com"])


class CommunityUpdateRequest(BaseModel):
    """Request model for updating community calendar URL"""
    calendar_url: str = Field(..., description="New calendar URL", example="https://widgets.bcc.no/ical-xyz/Portal-Calendar.ics")


class CommunityResponse(BaseModel):
    """Response model for community data"""
    id: str = Field(..., description="Community ID", example="exter")
    name: str = Field(..., description="Community name", example="BCC Community Calendar")
    description: str = Field(..., description="Community description")
    url_path: str = Field(..., description="URL path", example="/exter")
    calendar_url: str = Field(..., description="Calendar URL")
    admin_emails: List[str] = Field(..., description="Administrator emails")
    is_active: bool = Field(..., description="Whether community is active")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class ServiceResult(BaseModel):
    """Standard service result format"""
    success: bool = Field(..., description="Whether operation succeeded")
    data: Optional[Dict] = Field(None, description="Result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    events: List[str] = Field(default_factory=list, description="Events that occurred")


class CommunityService:
    """
    Community business logic service
    Orchestrates pure functions with state management
    """
    
    def __init__(self, repository: StateRepository):
        self.repository = repository
    
    def create_community_workflow(
        self,
        request: CommunityCreateRequest,
        password_hash: str
    ) -> ServiceResult:
        """
        Complete workflow for creating a community
        Combines validation, state transformation, and persistence
        """
        # Step 1: Validate input (pure function)
        is_valid, error_msg = validate_community_data(
            request.name,
            request.description,
            request.url_path,
            request.calendar_url
        )
        
        if not is_valid:
            return ServiceResult(
                success=False,
                error_message=error_msg
            )
        
        # Step 2: Load current state (I/O)
        current_state = self.repository.load_state()
        
        # Step 3: Apply state transformation (pure function)
        transition = create_community(
            current_state,
            request.name,
            request.description,
            request.url_path,
            password_hash,
            request.calendar_url,
            request.admin_emails
        )
        
        if not transition.success:
            return ServiceResult(
                success=False,
                error_message=transition.error_message
            )
        
        # Step 4: Add default groups (pure function)
        community_id = request.url_path.lstrip('/')
        default_groups = create_default_groups()
        
        groups_transition = add_default_groups_to_community(
            transition.new_state,
            community_id,
            default_groups
        )
        
        if not groups_transition.success:
            return ServiceResult(
                success=False,
                error_message=groups_transition.error_message
            )
        
        # Step 5: Persist new state (I/O)
        save_success = self.repository.save_state(groups_transition.new_state)
        
        if not save_success:
            return ServiceResult(
                success=False,
                error_message="Failed to persist community data"
            )
        
        # Step 6: Return success result
        community_data = groups_transition.new_state.communities[community_id]
        return ServiceResult(
            success=True,
            data={
                "community": {
                    "id": community_data.id,
                    "name": community_data.name,
                    "description": community_data.description,
                    "url_path": community_data.url_path,
                    "calendar_url": community_data.calendar_url,
                    "admin_emails": community_data.admin_emails,
                    "is_active": community_data.is_active,
                    "created_at": community_data.created_at,
                    "updated_at": community_data.updated_at
                }
            },
            events=transition.events + groups_transition.events
        )
    
    def update_calendar_url_workflow(
        self,
        community_id: str,
        request: CommunityUpdateRequest
    ) -> ServiceResult:
        """
        Complete workflow for updating community calendar URL
        """
        # Step 1: Load current state (I/O)
        current_state = self.repository.load_state()
        
        # Step 2: Apply state transformation (pure function)
        transition = update_community_calendar_url(
            current_state,
            community_id,
            request.calendar_url
        )
        
        if not transition.success:
            return ServiceResult(
                success=False,
                error_message=transition.error_message
            )
        
        # Step 3: Persist new state (I/O)
        save_success = self.repository.save_state(transition.new_state)
        
        if not save_success:
            return ServiceResult(
                success=False,
                error_message="Failed to persist calendar URL update"
            )
        
        # Step 4: Return success result
        updated_community = transition.new_state.communities[community_id]
        return ServiceResult(
            success=True,
            data={
                "community": {
                    "id": updated_community.id,
                    "name": updated_community.name,
                    "calendar_url": updated_community.calendar_url,
                    "updated_at": updated_community.updated_at
                }
            },
            events=transition.events
        )
    
    def get_community_by_path_workflow(self, url_path: str) -> ServiceResult:
        """
        Workflow for finding community by URL path
        """
        # Step 1: Load current state (I/O)
        current_state = self.repository.load_state()
        
        # Step 2: Query data (pure function)
        result = find_community_by_path(current_state, url_path)
        
        if not result.success:
            return ServiceResult(
                success=False,
                error_message=result.error_message
            )
        
        # Step 3: Return result
        community = result.data
        return ServiceResult(
            success=True,
            data={
                "community": {
                    "id": community.id,
                    "name": community.name,
                    "description": community.description,
                    "url_path": community.url_path,
                    "calendar_url": community.calendar_url,
                    "admin_emails": community.admin_emails,
                    "is_active": community.is_active,
                    "created_at": community.created_at,
                    "updated_at": community.updated_at
                }
            }
        )
    
    def get_community_groups_workflow(self, community_id: str) -> ServiceResult:
        """
        Workflow for getting community groups
        """
        # Step 1: Load current state (I/O)
        current_state = self.repository.load_state()
        
        # Step 2: Query data (pure function)
        result = get_community_groups(current_state, community_id)
        
        if not result.success:
            return ServiceResult(
                success=False,
                error_message=result.error_message
            )
        
        # Step 3: Return result
        groups = result.data
        return ServiceResult(
            success=True,
            data={
                "groups": [
                    {
                        "id": group.id,
                        "community_id": group.community_id,
                        "name": group.name,
                        "description": group.description,
                        "icon": group.icon,
                        "color": group.color,
                        "assignment_rules": group.assignment_rules,
                        "is_active": group.is_active,
                        "created_at": group.created_at,
                        "updated_at": group.updated_at
                    }
                    for group in groups
                ]
            }
        )