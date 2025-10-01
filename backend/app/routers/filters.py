"""
User-level filter router for cross-calendar and cross-domain filter management.

Implements user filter endpoints from OpenAPI specification.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.calendar_service import get_filters

router = APIRouter()


@router.get("")
async def get_user_filters(
    username: Optional[str] = Query(None, description="Username to filter by"),
    db: Session = Depends(get_db)
):
    """
    Get all filters for a user (both calendar and domain filters).

    This endpoint aggregates filters from both user calendars and domain calendars,
    allowing the frontend to display domain navigation buttons for domains where
    the user has created filters.

    Args:
        username: Optional username to filter by
        db: Database session

    Returns:
        List of filter objects matching the OpenAPI Filter schema
    """
    try:
        # Get all filters for the user (no calendar_id or domain_key filter)
        # The get_filters function already supports filtering by username only
        filters = get_filters(db, username=username)

        # Transform to OpenAPI schema format
        filters_response = []
        for filter_obj in filters:
            filter_dict = {
                "id": filter_obj.id,
                "name": filter_obj.name,
                "username": filter_obj.username,
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
