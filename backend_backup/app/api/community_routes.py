"""
Community API Routes - HTTP Boundary Layer
Rich Hickey: "Push I/O to the edges, keep business logic pure"
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from typing import Dict, Any
import hashlib

from ..services.community_service import (
    CommunityService, CommunityCreateRequest, CommunityUpdateRequest, 
    CommunityResponse, ServiceResult
)
from ..persistence.repositories import StateRepository


# Create router with comprehensive OpenAPI metadata
router = APIRouter(
    prefix="/api/v1/communities",
    tags=["Communities"],
    responses={
        404: {"description": "Community not found"},
        500: {"description": "Internal server error"}
    }
)

# Dependency injection for service
def get_community_service() -> CommunityService:
    """Dependency injection for community service"""
    repository = StateRepository()
    return CommunityService(repository)


@router.post(
    "/{community_id}/init",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Initialize a new community",
    description="""
    Create a new community calendar with the specified configuration.
    
    This endpoint:
    - Validates all input data
    - Creates the community record
    - Sets up default groups (Football, Youth, Events, etc.)
    - Initializes the community with proper access controls
    
    **Note**: Community ID is derived from the URL path (e.g., "/exter" → "exter")
    """,
    responses={
        201: {
            "description": "Community created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "community": {
                            "id": "exter",
                            "name": "BCC Community Calendar",
                            "url_path": "/exter",
                            "calendar_url": "https://widgets.bcc.no/ical-xyz/Portal-Calendar.ics",
                            "is_active": True,
                            "created_at": "2024-09-16T05:00:00Z"
                        },
                        "groups_created": 5
                    }
                }
            }
        },
        409: {
            "description": "Community already exists",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "Community exter already exists"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "Calendar URL must be a valid HTTP URL"
                    }
                }
            }
        }
    }
)
async def initialize_community(
    community_id: str,
    request: CommunityCreateRequest,
    service: CommunityService = Depends(get_community_service)
):
    """
    Initialize a new community with default configuration
    
    **Rich Hickey Design**:
    - Pure business logic in service layer
    - Immutable data transformations
    - Explicit error handling
    - No side effects in business logic
    """
    # Hash password (side effect isolated)
    password_hash = hashlib.sha256(request.password.encode()).hexdigest()
    
    # Execute business workflow (pure functions)
    result = service.create_community_workflow(request, password_hash)
    
    if not result.success:
        if "already exists" in result.error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.error_message
            )
    
    return {
        "success": True,
        "community": result.data["community"],
        "groups_created": len([e for e in result.events if e.startswith("group_created")])
    }


@router.get(
    "/{community_id}/info",
    response_model=Dict[str, Any],
    summary="Get community information",
    description="""
    Retrieve detailed information about a specific community.
    
    Returns:
    - Community metadata (name, description, etc.)
    - Calendar source URL
    - Administrative information
    - Current status
    
    **Performance**: This is a read-only operation with no side effects.
    """,
    responses={
        200: {
            "description": "Community information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "exter",
                        "name": "BCC Community Calendar", 
                        "description": "Community calendar for BCC events",
                        "calendar_url": "https://widgets.bcc.no/ical-xyz/Portal-Calendar.ics",
                        "is_active": True
                    }
                }
            }
        }
    }
)
async def get_community_info(
    community_id: str,
    service: CommunityService = Depends(get_community_service)
):
    """
    Get community information by ID
    
    **Rich Hickey Design**:
    - Pure query function
    - No side effects
    - Immutable data return
    """
    url_path = f"/{community_id}"
    result = service.get_community_by_path_workflow(url_path)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Community {community_id} not found"
        )
    
    return result.data["community"]


@router.put(
    "/{community_id}/calendar-url",
    response_model=Dict[str, Any],
    summary="Update community calendar URL",
    description="""
    Update the source calendar URL for a community.
    
    This is useful when:
    - The calendar provider changes URLs
    - Moving to a different calendar system
    - Updating calendar permissions
    
    **Note**: This operation is atomic - either succeeds completely or fails with no changes.
    """,
    responses={
        200: {
            "description": "Calendar URL updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "community": {
                            "id": "exter",
                            "name": "BCC Community Calendar",
                            "calendar_url": "https://widgets.bcc.no/ical-new/Portal-Calendar.ics",
                            "updated_at": "2024-09-16T05:30:00Z"
                        }
                    }
                }
            }
        }
    }
)
async def update_community_calendar_url(
    community_id: str,
    request: CommunityUpdateRequest,
    service: CommunityService = Depends(get_community_service)
):
    """
    Update community calendar URL
    
    **Rich Hickey Design**:
    - Immutable state transformation
    - Atomic operation
    - Explicit error handling
    """
    result = service.update_calendar_url_workflow(community_id, request)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.error_message
        )
    
    return {
        "success": True,
        "community": result.data["community"],
        "events": result.events
    }


@router.get(
    "/{community_id}/groups",
    response_model=Dict[str, Any],
    summary="Get community groups",
    description="""
    Retrieve all active groups for a community.
    
    Groups are used for:
    - Organizing events by category (Football, Youth, etc.)
    - User subscription preferences
    - Automatic event categorization
    
    **Performance**: Results are cached and optimized for frequent access.
    """,
    responses={
        200: {
            "description": "Groups retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "groups": [
                            {
                                "id": "football",
                                "name": "Football",
                                "description": "All football-related events",
                                "icon": "⚽",
                                "color": "#22C55E",
                                "assignment_rules": ["football", "soccer", "match"]
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_community_groups(
    community_id: str,
    service: CommunityService = Depends(get_community_service)
):
    """
    Get all groups for a community
    
    **Rich Hickey Design**:
    - Pure query function
    - Immutable data structures
    - No side effects
    """
    result = service.get_community_groups_workflow(community_id)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.error_message
        )
    
    return result.data


# Health check endpoint
@router.get(
    "/health",
    summary="Community service health check",
    description="Check if the community service is operational",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-09-16T05:00:00Z",
                        "version": "1.0.0"
                    }
                }
            }
        }
    }
)
async def health_check():
    """Health check endpoint for monitoring"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "architecture": "functional_core_imperative_shell"
    }