"""
Domain event assignment router for DynamoDB backend.

Implements event-to-group assignment endpoints.
"""

from fastapi import APIRouter, HTTPException, Body

from .deps import get_repo, get_verified_domain_ddb

router = APIRouter()


@router.put("/{domain}/groups/{group_id}/assign-recurring-events")
async def assign_events_to_group(domain: str, group_id: int, data: dict = Body(...)):
    """Assign recurring events to a group by their titles."""
    domain_obj = await get_verified_domain_ddb(domain)

    # Verify group exists
    group = next((g for g in domain_obj.groups if g.id == group_id), None)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    event_titles = data.get("event_titles", [])
    if not event_titles:
        raise HTTPException(status_code=400, detail="event_titles is required")

    repo = get_repo()

    assigned_count = 0
    for title in event_titles:
        if repo.assign_event_to_group(domain, title, group_id):
            assigned_count += 1

    return {
        "success": True,
        "assigned_count": assigned_count,
        "group_id": group_id,
        "group_name": group.name
    }


@router.put("/{domain}/groups/{group_id}/remove-events")
async def remove_events_from_group(domain: str, group_id: int, data: dict = Body(...)):
    """Remove event assignments from a specific group."""
    domain_obj = await get_verified_domain_ddb(domain)

    # Verify group exists
    group = next((g for g in domain_obj.groups if g.id == group_id), None)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    event_titles = data.get("event_titles", [])
    if not event_titles:
        raise HTTPException(status_code=400, detail="event_titles is required")

    repo = get_repo()

    removed_count = 0
    for title in event_titles:
        # Only remove if assigned to this specific group
        if domain_obj.recurring_assignments.get(title) == group_id:
            if repo.unassign_event(domain, title):
                removed_count += 1

    return {
        "success": True,
        "removed_count": removed_count,
        "group_id": group_id
    }


@router.put("/{domain}/bulk-assign-events")
async def bulk_assign_events(domain: str, data: dict = Body(...)):
    """Bulk assign events to groups."""
    await get_verified_domain_ddb(domain)

    assignments = data.get("assignments", [])
    if not assignments:
        raise HTTPException(status_code=400, detail="assignments is required")

    repo = get_repo()

    assigned_count = 0
    for assignment in assignments:
        title = assignment.get("title")
        group_id = assignment.get("group_id")
        if title and group_id:
            if repo.assign_event_to_group(domain, title, group_id):
                assigned_count += 1

    return {
        "success": True,
        "assigned_count": assigned_count
    }


@router.put("/{domain}/bulk-unassign-events")
async def bulk_unassign_events(domain: str, data: dict = Body(...)):
    """Bulk unassign events from all groups."""
    await get_verified_domain_ddb(domain)

    event_titles = data.get("event_titles", [])
    if not event_titles:
        raise HTTPException(status_code=400, detail="event_titles is required")

    repo = get_repo()

    unassigned_count = 0
    for title in event_titles:
        if repo.unassign_event(domain, title):
            unassigned_count += 1

    return {
        "success": True,
        "unassigned_count": unassigned_count
    }


@router.put("/{domain}/unassign-event")
async def unassign_single_event(domain: str, data: dict = Body(...)):
    """Unassign a single event."""
    await get_verified_domain_ddb(domain)

    title = data.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    repo = get_repo()
    success = repo.unassign_event(domain, title)

    return {
        "success": success,
        "title": title
    }
