"""
User-level filter router for cross-calendar and cross-domain filter management.

Implements user filter endpoints from OpenAPI specification.
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import get_current_user_id
from ..services.calendar_service import get_filters

router = APIRouter()


@router.get("")
async def get_user_filters(
    user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all filters for a user (both calendar and domain filters).

    This endpoint aggregates filters from both user calendars and domain calendars,
    allowing the frontend to display domain navigation buttons for domains where
    the user has created filters.

    Authentication via JWT token in Authorization header (optional - returns empty for anonymous).

    Args:
        user_id: User ID extracted from JWT token (None for anonymous users)
        db: Database session

    Returns:
        List of filter objects matching the OpenAPI Filter schema
    """
    try:
        # Return empty list for anonymous users
        if not user_id:
            return []

        # Get all filters for the authenticated user
        filters = get_filters(db, user_id=user_id)

        # Transform to OpenAPI schema format
        filters_response = []
        for filter_obj in filters:
            filter_dict = {
                "id": filter_obj.id,
                "name": filter_obj.name,
                "user_id": filter_obj.user_id,
                "subscribed_event_ids": filter_obj.subscribed_event_ids or [],
                "subscribed_group_ids": filter_obj.subscribed_group_ids or [],
                "link_uuid": filter_obj.link_uuid,
                "export_url": f"/ical/{filter_obj.link_uuid}.ics",
                "created_at": filter_obj.created_at.isoformat() if filter_obj.created_at else None,
                "updated_at": filter_obj.updated_at.isoformat() if filter_obj.updated_at else None
            }

            # Include calendar_id or domain_key depending on filter type
            if filter_obj.calendar_id:
                filter_dict["calendar_id"] = filter_obj.calendar_id
            if filter_obj.domain_key:
                filter_dict["domain_key"] = filter_obj.domain_key

            filters_response.append(filter_dict)

        return filters_response

    except Exception as e:
        # Log error and return empty list to prevent breaking the frontend
        print(f"Error fetching user filters: {str(e)}")
        return []
