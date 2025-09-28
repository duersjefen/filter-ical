"""
Calendars router for user calendar management.

Implements user calendar endpoints from OpenAPI specification.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.database import get_db
from ..i18n.utils import get_locale_from_request, format_error_message
from ..services.calendar_service import (
    create_calendar, get_calendars, get_calendar_by_id, delete_calendar,
    get_calendar_events, sync_calendar_events, create_filter, get_filters,
    delete_filter, get_filter_by_id
)

router = APIRouter()


@router.post("")
async def add_calendar(
    calendar_data: dict,
    request: Request,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Add a user calendar."""
    try:
        # Validate request data
        locale = get_locale_from_request(request)
        
        if "name" not in calendar_data:
            raise HTTPException(status_code=400, detail=format_error_message("calendar_name_required", locale))
        if "source_url" not in calendar_data:
            raise HTTPException(status_code=400, detail=format_error_message("source_url_required", locale))
        
        # Create calendar
        success, calendar, error = create_calendar(
            db=db,
            name=calendar_data["name"],
            source_url=calendar_data["source_url"],
            username=username
        )
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        # Sync calendar events
        sync_success, event_count, sync_error = await sync_calendar_events(db, calendar)
        warnings = []
        if not sync_success:
            # Calendar created but sync failed - still return calendar with warning
            warning_msg = f"Calendar created but failed to sync events: {sync_error}"
            warnings.append(warning_msg)
            print(f"⚠️ Calendar sync warning for {calendar.name}: {sync_error}")
        elif event_count == 0:
            warnings.append("Calendar synced successfully but contains no events")
            print(f"ℹ️ Calendar {calendar.name} synced but has 0 events")
        
        # Return calendar data matching OpenAPI schema
        response = {
            "id": calendar.id,
            "name": calendar.name,
            "source_url": calendar.source_url,
            "type": calendar.type,
            "domain_key": calendar.domain_key,
            "username": calendar.username,
            "last_fetched": calendar.last_fetched.isoformat() if calendar.last_fetched else None
        }
        
        # Add warnings if any
        if warnings:
            response["warnings"] = warnings
            response["event_count"] = event_count if sync_success else 0
        
        # Return 201 Created for successful calendar creation (REST convention)
        from fastapi import status
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("")
async def list_calendars(
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List user calendars."""
    try:
        # Get calendars from database
        calendars = get_calendars(db, username=username)
        
        # Transform to OpenAPI schema format
        calendars_response = []
        for calendar in calendars:
            calendars_response.append({
                "id": calendar.id,
                "name": calendar.name,
                "source_url": calendar.source_url,
                "type": calendar.type,
                "domain_key": calendar.domain_key,
                "username": calendar.username,
                "last_fetched": calendar.last_fetched.isoformat() if calendar.last_fetched else None
            })
        
        return calendars_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{calendar_id}/sync")
async def sync_calendar_endpoint(
    calendar_id: int,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Manually sync calendar events from source."""
    try:
        # Verify calendar exists and user has access
        calendar = get_calendar_by_id(db, calendar_id, username=username)
        if not calendar:
            raise HTTPException(status_code=404, detail="Calendar not found")
            
        # Sync calendar events
        sync_success, event_count, sync_error = await sync_calendar_events(db, calendar)
        
        if not sync_success:
            raise HTTPException(status_code=400, detail=f"Sync failed: {sync_error}")
            
        return {
            "message": f"Calendar synced successfully. {event_count} events processed.",
            "event_count": event_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{calendar_id}")
async def delete_user_calendar(
    calendar_id: int,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Delete a user calendar."""
    try:
        # Delete calendar
        success, error = delete_calendar(db, calendar_id, username=username)
        if not success:
            if "not found" in error.lower():
                raise HTTPException(status_code=404, detail="Calendar not found")
            else:
                raise HTTPException(status_code=400, detail=error)
        
        # Return 204 No Content on successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{calendar_id}/events")
async def get_calendar_events_endpoint(
    calendar_id: int,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get calendar events (flat structure for user calendars)."""
    try:
        # Verify calendar exists and user has access
        calendar = get_calendar_by_id(db, calendar_id, username=username)
        if not calendar:
            raise HTTPException(status_code=404, detail="Calendar not found")
        
        # Get events
        events = get_calendar_events(db, calendar_id)
        
        # Transform to OpenAPI schema format
        events_response = []
        for event in events:
            events_response.append({
                "id": event.id,
                "title": event.title,
                "start_time": event.start_time.isoformat() if event.start_time else None,
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "description": event.description or "",
                "location": event.location,
                "uid": event.uid
            })
        
        return {
            "events": events_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{calendar_id}/filters")
async def create_calendar_filter(
    calendar_id: int,
    filter_data: dict,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Create filter for user calendar."""
    try:
        # Verify calendar exists and user has access
        calendar = get_calendar_by_id(db, calendar_id, username=username)
        if not calendar:
            raise HTTPException(status_code=404, detail="Calendar not found")
        
        # Validate request data
        if "name" not in filter_data:
            raise HTTPException(status_code=400, detail="Filter name is required")
        
        # Create filter
        success, filter_obj, error = create_filter(
            db=db,
            name=filter_data["name"],
            calendar_id=calendar_id,
            username=username,
            subscribed_event_ids=filter_data.get("subscribed_event_ids", [])
        )
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        # Return filter data matching OpenAPI schema
        return {
            "id": filter_obj.id,
            "name": filter_obj.name,
            "calendar_id": filter_obj.calendar_id,
            "domain_key": filter_obj.domain_key,
            "username": filter_obj.username,
            "subscribed_event_ids": filter_obj.subscribed_event_ids or [],
            "subscribed_group_ids": filter_obj.subscribed_group_ids or [],
            "link_uuid": filter_obj.link_uuid,
            "export_url": f"/ical/{filter_obj.link_uuid}.ics",
            # Add filter_config for frontend compatibility
            "filter_config": {
                "recurring_events": filter_obj.subscribed_event_ids or [],
                "groups": filter_obj.subscribed_group_ids or []
            },
            "created_at": filter_obj.created_at.isoformat() if filter_obj.created_at else None,
            "updated_at": filter_obj.updated_at.isoformat() if filter_obj.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{calendar_id}/filters")
async def get_calendar_filters(
    calendar_id: int,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List filters for user calendar."""
    try:
        # Verify calendar exists and user has access
        calendar = get_calendar_by_id(db, calendar_id, username=username)
        if not calendar:
            raise HTTPException(status_code=404, detail="Calendar not found")
        
        # Get filters
        filters = get_filters(db, calendar_id=calendar_id, username=username)
        
        # Transform to OpenAPI schema format
        filters_response = []
        for filter_obj in filters:
            filters_response.append({
                "id": filter_obj.id,
                "name": filter_obj.name,
                "calendar_id": filter_obj.calendar_id,
                "domain_key": filter_obj.domain_key,
                "username": filter_obj.username,
                "subscribed_event_ids": filter_obj.subscribed_event_ids or [],
                "subscribed_group_ids": filter_obj.subscribed_group_ids or [],
                "link_uuid": filter_obj.link_uuid,
                "export_url": f"/ical/{filter_obj.link_uuid}.ics",
                # Add filter_config for frontend compatibility
                "filter_config": {
                    "recurring_events": filter_obj.subscribed_event_ids or [],
                    "groups": filter_obj.subscribed_group_ids or []
                },
                "created_at": filter_obj.created_at.isoformat() if filter_obj.created_at else None,
                "updated_at": filter_obj.updated_at.isoformat() if filter_obj.updated_at else None
            })
        
        return filters_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{calendar_id}/filters/{filter_id}")
async def update_calendar_filter(
    calendar_id: int,
    filter_id: int,
    filter_data: dict,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Update an existing calendar filter."""
    try:
        # Verify calendar exists and user has access
        calendar = get_calendar_by_id(db, calendar_id, username=username)
        if not calendar:
            raise HTTPException(status_code=404, detail="Calendar not found")
        
        # Get existing filter to verify it exists and user has access
        existing_filter = get_filter_by_id(db, filter_id)
        if not existing_filter or existing_filter.calendar_id != calendar_id:
            raise HTTPException(status_code=404, detail="Filter not found")
        
        if username and existing_filter.username != username:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update the filter
        if "name" in filter_data:
            existing_filter.name = filter_data["name"].strip()
        if "subscribed_event_ids" in filter_data:
            existing_filter.subscribed_event_ids = filter_data["subscribed_event_ids"]
        if "subscribed_group_ids" in filter_data:
            existing_filter.subscribed_group_ids = filter_data["subscribed_group_ids"]
        
        existing_filter.updated_at = func.now()
        db.commit()
        db.refresh(existing_filter)
        
        # Return updated filter data
        return {
            "id": existing_filter.id,
            "name": existing_filter.name,
            "calendar_id": existing_filter.calendar_id,
            "domain_key": existing_filter.domain_key,
            "username": existing_filter.username,
            "subscribed_event_ids": existing_filter.subscribed_event_ids or [],
            "subscribed_group_ids": existing_filter.subscribed_group_ids or [],
            "link_uuid": existing_filter.link_uuid,
            "export_url": f"/ical/{existing_filter.link_uuid}.ics",
            # Add filter_config for frontend compatibility
            "filter_config": {
                "recurring_events": existing_filter.subscribed_event_ids or [],
                "groups": existing_filter.subscribed_group_ids or []
            },
            "created_at": existing_filter.created_at.isoformat() if existing_filter.created_at else None,
            "updated_at": existing_filter.updated_at.isoformat() if existing_filter.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{calendar_id}/filters/{filter_id}")
async def delete_calendar_filter(
    calendar_id: int,
    filter_id: int,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Delete filter for user calendar."""
    try:
        # Verify calendar exists and user has access
        calendar = get_calendar_by_id(db, calendar_id, username=username)
        if not calendar:
            raise HTTPException(status_code=404, detail="Calendar not found")
        
        # Delete filter
        success, error = delete_filter(db, filter_id, calendar_id=calendar_id, username=username)
        if not success:
            if "not found" in error.lower():
                raise HTTPException(status_code=404, detail="Filter not found")
            else:
                raise HTTPException(status_code=400, detail=error)
        
        # Return 204 No Content on successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")