"""
Domain groups router for group management and event assignments.

Implements group-related endpoints from OpenAPI specification.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.error_handlers import handle_endpoint_errors
from ..core.auth import get_verified_domain
from ..core.messages import ErrorMessages
from ..models.domain import Domain
from ..services.domain_service import (
    get_domain_groups, create_group, assign_recurring_events_to_group,
    get_available_recurring_events, get_available_recurring_events_with_assignments,
    bulk_unassign_recurring_events, update_group, delete_group,
    remove_events_from_specific_group
)

router = APIRouter()


@router.get("/{domain}/groups")
@handle_endpoint_errors
async def get_domain_groups_endpoint(
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Get groups for domain calendar."""
    # Get groups from database
    groups = get_domain_groups(db, domain_obj.domain_key)

    # Transform to OpenAPI schema format
    groups_response = []
    for group in groups:
        groups_response.append({
            "id": group.id,
            "name": group.name,
            "domain_key": group.domain_key
        })

    return groups_response


@router.post("/{domain}/groups")
@handle_endpoint_errors
async def create_domain_group(
    domain_obj: Domain = Depends(get_verified_domain),
    group_data: dict = None,
    db: Session = Depends(get_db)
):
    """Create a new group (admin)."""
    # Validate request data
    if "name" not in group_data:
        raise HTTPException(status_code=400, detail=ErrorMessages.GROUP_NAME_REQUIRED)

    # Create group
    success, group, error = create_group(db, domain_obj.domain_key, group_data["name"])
    if not success:
        raise HTTPException(status_code=400, detail=error)

    # Return group data matching OpenAPI schema
    return {
        "id": group.id,
        "name": group.name,
        "domain_key": group.domain_key
    }


@router.put("/{domain}/groups/{group_id}")
@handle_endpoint_errors
async def update_domain_group(
    group_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    group_data: dict = None,
    db: Session = Depends(get_db)
):
    """Update group (admin)."""
    # Validate request data
    if "name" not in group_data:
        raise HTTPException(status_code=400, detail=ErrorMessages.GROUP_NAME_REQUIRED)

    # Update group
    success, group, error = update_group(db, group_id, domain_obj.domain_key, group_data["name"])
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)

    # Return updated group data matching OpenAPI schema
    return {
        "id": group.id,
        "name": group.name,
        "domain_key": group.domain_key
    }


@router.delete("/{domain}/groups/{group_id}")
@handle_endpoint_errors
async def delete_domain_group(
    group_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Delete group and its assignments (admin)."""
    # Delete group
    success, error = delete_group(db, group_id, domain_obj.domain_key)
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)

    # Return 204 No Content on successful deletion
    return None


@router.put("/{domain}/groups/{group_id}/assign-recurring-events")
@handle_endpoint_errors
async def assign_recurring_events(
    group_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    assignment_data: dict = None,
    db: Session = Depends(get_db)
):
    """Manually assign recurring events to group (admin)."""
    # Validate request data
    if "recurring_event_titles" not in assignment_data:
        raise HTTPException(status_code=400, detail=ErrorMessages.RECURRING_EVENT_TITLES_REQUIRED)

    event_titles = assignment_data["recurring_event_titles"]
    if not isinstance(event_titles, list):
        raise HTTPException(status_code=400, detail=ErrorMessages.RECURRING_EVENT_TITLES_MUST_BE_ARRAY)

    # Assign events to group
    success, count, error = assign_recurring_events_to_group(db, domain_obj.domain_key, group_id, event_titles)
    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {
        "message": f"{count} recurring events assigned to group"
    }


@router.put("/{domain}/groups/{group_id}/remove-events")
@handle_endpoint_errors
async def remove_events_from_group(
    group_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    removal_data: dict = None,
    db: Session = Depends(get_db)
):
    """Remove events from specific group (admin)."""
    # Validate request data
    if "recurring_event_titles" not in removal_data:
        raise HTTPException(status_code=400, detail=ErrorMessages.RECURRING_EVENT_TITLES_REQUIRED)

    event_titles = removal_data["recurring_event_titles"]
    if not isinstance(event_titles, list):
        raise HTTPException(status_code=400, detail=ErrorMessages.RECURRING_EVENT_TITLES_MUST_BE_ARRAY)

    # Remove events from specific group
    success, count, error = remove_events_from_specific_group(db, domain_obj.domain_key, group_id, event_titles)
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)

    return {
        "message": f"{count} events removed from group",
        "removed_count": count
    }


@router.get("/{domain}/recurring-events")
@handle_endpoint_errors
async def get_domain_recurring_events(
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Get available recurring events for assignment (admin)."""
    # Get recurring events
    recurring_events = get_available_recurring_events(db, domain_obj.domain_key)
    return recurring_events


@router.get("/{domain}/recurring-events-with-assignments")
@handle_endpoint_errors
async def get_domain_recurring_events_with_assignments(
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Get available recurring events with their current assignments (admin)."""
    # Get recurring events with assignment information
    events_with_assignments = get_available_recurring_events_with_assignments(db, domain_obj.domain_key)

    return {
        "success": True,
        "data": events_with_assignments
    }


@router.put("/{domain}/bulk-assign-events")
@handle_endpoint_errors
async def bulk_assign_events_to_group(
    domain_obj: Domain = Depends(get_verified_domain),
    assignment_data: dict = None,
    db: Session = Depends(get_db)
):
    """Bulk assign multiple events to a group (admin)."""
    # Validate request data
    if "group_id" not in assignment_data or "recurring_event_titles" not in assignment_data:
        raise HTTPException(status_code=400, detail=ErrorMessages.GROUP_ID_AND_EVENTS_REQUIRED)

    group_id = assignment_data["group_id"]
    event_titles = assignment_data["recurring_event_titles"]

    if not isinstance(event_titles, list):
        raise HTTPException(status_code=400, detail=ErrorMessages.RECURRING_EVENT_TITLES_MUST_BE_ARRAY)

    # Bulk assign events to group
    success, count, error = assign_recurring_events_to_group(db, domain_obj.domain_key, group_id, event_titles)
    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {
        "message": f"{count} recurring events assigned to group",
        "assigned_count": count
    }


@router.put("/{domain}/bulk-unassign-events")
@handle_endpoint_errors
async def bulk_unassign_events(
    domain_obj: Domain = Depends(get_verified_domain),
    assignment_data: dict = None,
    db: Session = Depends(get_db)
):
    """Bulk unassign multiple events from their current groups (admin)."""
    # Validate request data
    if "recurring_event_titles" not in assignment_data:
        raise HTTPException(status_code=400, detail=ErrorMessages.RECURRING_EVENT_TITLES_REQUIRED)

    event_titles = assignment_data["recurring_event_titles"]

    if not isinstance(event_titles, list):
        raise HTTPException(status_code=400, detail=ErrorMessages.RECURRING_EVENT_TITLES_MUST_BE_ARRAY)

    # Bulk unassign events
    success, count, error = bulk_unassign_recurring_events(db, domain_obj.domain_key, event_titles)
    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {
        "message": f"{count} recurring events unassigned",
        "unassigned_count": count
    }


@router.put("/{domain}/unassign-event")
@handle_endpoint_errors
async def unassign_single_event(
    domain_obj: Domain = Depends(get_verified_domain),
    assignment_data: dict = None,
    db: Session = Depends(get_db)
):
    """Unassign a single event from its current group (admin)."""
    # Validate request data
    if "recurring_event_title" not in assignment_data:
        raise HTTPException(status_code=400, detail=ErrorMessages.RECURRING_EVENT_TITLE_REQUIRED)

    event_title = assignment_data["recurring_event_title"]

    # Unassign single event
    success, count, error = bulk_unassign_recurring_events(db, domain_obj.domain_key, [event_title])
    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {
        "message": f"Event '{event_title}' unassigned",
        "unassigned_count": count
    }
