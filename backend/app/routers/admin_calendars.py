"""
Admin calendars router - Calendar permissions management for global admin.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..core.database import get_db
from ..core.auth import verify_admin_auth
from ..models.calendar import Calendar
from ..models.user import User
from ..models.domain import Domain
from ..models.calendar_admin import calendar_admins
from ..services import permission_service

router = APIRouter()


# Response models
class UserInfo(BaseModel):
    id: int
    username: str
    email: Optional[str]


class DomainInfo(BaseModel):
    domain_key: str
    name: str
    calendar_url: str
    status: str
    created_at: datetime


class AdminCalendarResponse(BaseModel):
    id: int
    name: str
    source_url: str
    type: str
    owner: Optional[UserInfo]
    domain: Optional[DomainInfo]
    events_count: int
    last_fetched: Optional[datetime]
    created_at: datetime


class PermissionInfo(BaseModel):
    user: UserInfo
    permission_level: str
    granted_at: datetime


class GrantPermissionRequest(BaseModel):
    user_id: int
    permission_level: str  # user, admin


@router.get(
    "/admin/calendars",
    summary="List all calendars (admin only)",
    description="Get list of all calendars across all users"
)
async def list_calendars(
    type: Optional[str] = Query(None, description="Filter by calendar type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of calendars per page"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    List all calendars with pagination.

    Requires admin authentication.
    """
    # Build query
    query = db.query(Calendar)

    # Apply type filter
    if type:
        if type not in ['user', 'domain']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid type. Must be 'user' or 'domain'"
            )
        query = query.filter(Calendar.type == type)

    # Get total count
    total = query.count()

    # Calculate pagination
    offset = (page - 1) * limit
    total_pages = (total + limit - 1) // limit

    # Get paginated results
    calendars = query.order_by(Calendar.created_at.desc()).offset(offset).limit(limit).all()

    # Build response
    calendars_response = []
    for calendar in calendars:
        # Get owner info
        owner = None
        if calendar.user_id:
            user = db.query(User).filter(User.id == calendar.user_id).first()
            if user:
                owner = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }

        # Get domain info (for domain calendars)
        domain = None
        if calendar.type == 'domain':
            # Find domain that owns this calendar
            domain_obj = db.query(Domain).filter(Domain.calendar_id == calendar.id).first()
            if domain_obj:
                domain = {
                    "domain_key": domain_obj.domain_key,
                    "name": domain_obj.name,
                    "calendar_url": domain_obj.calendar_url,
                    "status": domain_obj.status,
                    "created_at": domain_obj.created_at
                }

        # Get events count
        events_count = len(calendar.events)

        calendars_response.append({
            "id": calendar.id,
            "name": calendar.name,
            "source_url": calendar.source_url,
            "type": calendar.type,
            "owner": owner,
            "domain": domain,
            "events_count": events_count,
            "last_fetched": calendar.last_fetched,
            "created_at": calendar.created_at
        })

    return {
        "calendars": calendars_response,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.get(
    "/admin/calendars/{calendar_id}/permissions",
    summary="List calendar permissions (admin only)",
    description="Get all users who have permissions for this calendar"
)
async def list_calendar_permissions(
    calendar_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    List all permissions for a calendar.
    Requires admin authentication.
    """
    # Use service layer
    success, data_or_error = permission_service.list_calendar_permissions(db, calendar_id)

    if not success:
        # Check if error is "not found"
        if "not found" in data_or_error.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=data_or_error
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=data_or_error
        )

    # Get calendar info
    calendar = db.query(Calendar).filter(Calendar.id == calendar_id).first()
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calendar with ID {calendar_id} not found"
        )

    # Get calendar info
    owner = None
    if calendar.user_id:
        user = db.query(User).filter(User.id == calendar.user_id).first()
        if user:
            owner = {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }

    domain = None
    if calendar.type == 'domain':
        domain_obj = db.query(Domain).filter(Domain.calendar_id == calendar.id).first()
        if domain_obj:
            domain = {
                "domain_key": domain_obj.domain_key,
                "name": domain_obj.name,
                "calendar_url": domain_obj.calendar_url,
                "status": domain_obj.status,
                "created_at": domain_obj.created_at
            }

    events_count = len(calendar.events)

    calendar_response = {
        "id": calendar.id,
        "name": calendar.name,
        "source_url": calendar.source_url,
        "type": calendar.type,
        "owner": owner,
        "domain": domain,
        "events_count": events_count,
        "last_fetched": calendar.last_fetched,
        "created_at": calendar.created_at
    }

    # Build permissions list from service layer data
    permissions = []
    for perm in data_or_error:
        permissions.append({
            "user": {
                "id": perm["user_id"],
                "username": perm["username"],
                "email": perm["email"]
            },
            "permission_level": perm["permission_level"],
            "granted_at": perm["created_at"]
        })

    return {
        "calendar": calendar_response,
        "permissions": permissions
    }


@router.post(
    "/admin/calendars/{calendar_id}/permissions",
    status_code=status.HTTP_201_CREATED,
    summary="Grant calendar permission (admin only)",
    description="Grant a user access to a calendar"
)
async def grant_calendar_permission(
    calendar_id: int,
    permission_data: GrantPermissionRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Grant a user permission to access a calendar.
    Requires admin authentication.
    """
    # Use service layer
    success, error = permission_service.grant_calendar_permission(
        db,
        calendar_id,
        permission_data.user_id,
        permission_data.permission_level
    )

    if not success:
        # Determine appropriate status code based on error message
        if "not found" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error
            )
        elif "invalid" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        elif "already" in error.lower() or "exists" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error
            )

    return {
        "success": True,
        "message": "Permission granted successfully"
    }


@router.delete(
    "/admin/calendars/{calendar_id}/permissions/{user_id}",
    summary="Revoke calendar permission (admin only)",
    description="Remove user's access to a calendar"
)
async def revoke_calendar_permission(
    calendar_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Revoke a user's permission to access a calendar.
    Requires admin authentication.
    """
    # Use service layer
    success, error = permission_service.revoke_calendar_permission(
        db,
        calendar_id,
        user_id
    )

    if not success:
        # Determine appropriate status code based on error message
        if "not found" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error
            )

    return {
        "success": True,
        "message": "Permission revoked successfully"
    }
