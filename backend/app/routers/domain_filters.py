"""
Domain filters router for user filter management.

Implements filter-related endpoints from OpenAPI specification.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.database import get_db
from ..core.error_handlers import handle_endpoint_errors
from ..core.auth import require_user_auth, get_current_user_id, get_verified_domain
from ..core.messages import ErrorMessages
from ..models.domain import Domain
from ..services.calendar_service import get_filters, create_filter, delete_filter, get_filter_by_id

router = APIRouter()


def _format_filter_response(filter_obj):
    """Helper function to format filter object to API response."""
    return {
        "id": filter_obj.id,
        "name": filter_obj.name,
        "domain_key": filter_obj.domain_key,
        "user_id": filter_obj.user_id,
        "subscribed_event_ids": filter_obj.subscribed_event_ids or [],
        "subscribed_group_ids": filter_obj.subscribed_group_ids or [],
        "unselected_event_ids": filter_obj.unselected_event_ids or [],
        "link_uuid": filter_obj.link_uuid,
        "export_url": f"/ical/{filter_obj.link_uuid}.ics",
        "filter_config": {
            "recurring_events": filter_obj.subscribed_event_ids or [],
            "groups": filter_obj.subscribed_group_ids or []
        },
        "created_at": filter_obj.created_at.isoformat() if filter_obj.created_at else None,
        "updated_at": filter_obj.updated_at.isoformat() if filter_obj.updated_at else None
    }


@router.post("/{domain}/filters")
@handle_endpoint_errors
async def create_domain_filter(
    domain_obj: Domain = Depends(get_verified_domain),
    filter_data: dict = None,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Create filter for domain calendar (authentication required)."""
    # Validate request data
    if "name" not in filter_data:
        raise HTTPException(status_code=400, detail=ErrorMessages.FILTER_NAME_REQUIRED)

    # Create filter
    success, filter_obj, error = create_filter(
        db=db,
        name=filter_data["name"],
        domain_key=domain_obj.domain_key,
        user_id=user_id,
        subscribed_event_ids=filter_data.get("subscribed_event_ids", []),
        subscribed_group_ids=filter_data.get("subscribed_group_ids", []),
        unselected_event_ids=filter_data.get("unselected_event_ids", [])
    )
    if not success:
        raise HTTPException(status_code=400, detail=error)

    return _format_filter_response(filter_obj)


@router.get("/{domain}/filters")
@handle_endpoint_errors
async def get_domain_filters(
    domain_obj: Domain = Depends(get_verified_domain),
    user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List filters for domain calendar (authentication optional - returns user's filters if authenticated)."""
    # Only get filters if user is authenticated
    if not user_id:
        return []

    # Get filters for authenticated user
    filters = get_filters(db, domain_key=domain_obj.domain_key, user_id=user_id)

    # Transform to OpenAPI schema format
    return [_format_filter_response(filter_obj) for filter_obj in filters]


@router.put("/{domain}/filters/{filter_id}")
@handle_endpoint_errors
async def update_domain_filter(
    filter_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    filter_data: dict = None,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Update an existing domain filter (authentication required)."""
    try:
        # Get existing filter to verify it exists and user has access
        existing_filter = get_filter_by_id(db, filter_id)
        if not existing_filter or existing_filter.domain_key != domain_obj.domain_key:
            raise HTTPException(status_code=404, detail=ErrorMessages.FILTER_NOT_FOUND)

        # Verify user owns this filter
        if existing_filter.user_id != user_id:
            raise HTTPException(status_code=403, detail=ErrorMessages.ACCESS_DENIED)

        # Update the filter
        if "name" in filter_data:
            existing_filter.name = filter_data["name"].strip()
        if "subscribed_event_ids" in filter_data:
            existing_filter.subscribed_event_ids = filter_data["subscribed_event_ids"]
        if "subscribed_group_ids" in filter_data:
            existing_filter.subscribed_group_ids = filter_data["subscribed_group_ids"]
        if "unselected_event_ids" in filter_data:
            existing_filter.unselected_event_ids = filter_data["unselected_event_ids"]

        existing_filter.updated_at = func.now()
        db.commit()
        db.refresh(existing_filter)

        return _format_filter_response(existing_filter)
    except Exception as e:
        db.rollback()
        raise


@router.delete("/{domain}/filters/{filter_id}")
@handle_endpoint_errors
async def delete_domain_filter(
    filter_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Delete filter for domain calendar (authentication required)."""
    # Delete filter
    success, error = delete_filter(db, filter_id, domain_key=domain_obj.domain_key, user_id=user_id)
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=ErrorMessages.FILTER_NOT_FOUND)
        else:
            raise HTTPException(status_code=400, detail=error)

    # Return 204 No Content on successful deletion
    return None
