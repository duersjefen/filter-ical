"""
iCal export router for dynamic calendar generation.

Implements iCal export endpoints from OpenAPI specification.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.messages import ErrorMessages
from ..services.calendar_service import get_filter_by_uuid, get_calendar_events, apply_filter_to_events
from ..data.calendar import transform_events_for_export

router = APIRouter()


@router.get("/{uuid}.ics")
@router.head("/{uuid}.ics")
async def export_filtered_calendar(
    uuid: str,
    db: Session = Depends(get_db)
):
    """Export filtered calendar as iCal file."""
    try:
        # Get filter by UUID
        filter_obj = get_filter_by_uuid(db, uuid)
        if not filter_obj:
            raise HTTPException(status_code=404, detail=ErrorMessages.FILTER_NOT_FOUND)
        
        # Get events based on filter type (with graceful degradation)
        try:
            if filter_obj.calendar_id:
                # User calendar filter
                events = get_calendar_events(db, filter_obj.calendar_id)
            elif filter_obj.domain_key:
                # Domain calendar filter - need to get domain events
                from ..services.domain_service import get_domain_events
                events_data = get_domain_events(db, filter_obj.domain_key)
                events = events_data  # Already in dictionary format
            else:
                raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_FILTER_CONFIGURATION)
        except Exception as events_error:
            # Graceful degradation for database issues (return empty calendar)
            print(f"⚠️ Events retrieval error for filter {uuid}: {events_error}")
            events = []
        
        # Transform events to dictionary format if needed
        if events and hasattr(events[0], '__dict__'):
            # Convert SQLAlchemy objects to dictionaries
            events_data = []
            for event in events:
                event_dict = {
                    "id": event.id,
                    "title": event.title,
                    "start_time": event.start_time,
                    "end_time": event.end_time,
                    "description": event.description or "",
                    "location": event.location,
                    "uid": event.uid,
                    "other_ical_fields": event.other_ical_fields or {}
                }
                events_data.append(event_dict)
        else:
            events_data = events
        
        # Apply filter to events using service layer (handles DB queries for domain filters)
        filtered_events = apply_filter_to_events(db, events_data, filter_obj.__dict__)

        # Transform events to iCal format using pure function
        ical_content = transform_events_for_export(filtered_events, filter_obj.name)
        
        # Return iCal content with proper content type
        return Response(
            content=ical_content,
            media_type="text/calendar",
            headers={
                "Content-Disposition": f'attachment; filename="{filter_obj.name}.ics"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")