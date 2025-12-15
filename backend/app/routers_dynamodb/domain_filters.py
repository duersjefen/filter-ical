"""
Domain filters router for DynamoDB backend.

Implements filter CRUD endpoints for iCal export.
"""

from fastapi import APIRouter, HTTPException, Body

from .deps import get_repo, get_verified_domain_ddb

router = APIRouter()


@router.get("/{domain}/filters")
async def list_domain_filters(domain: str):
    """List all filters for a domain."""
    await get_verified_domain_ddb(domain)

    repo = get_repo()
    filters = repo.list_filters_for_domain(domain)

    return [
        {
            "link_uuid": f.link_uuid,
            "name": f.name,
            "domain_key": f.domain_key,
            "subscribed_group_ids": f.subscribed_group_ids,
            "unselected_event_titles": f.unselected_event_titles,
            "include_future_events": f.include_future_events,
            "created_at": f.created_at.isoformat(),
            "updated_at": f.updated_at.isoformat()
        }
        for f in filters
    ]


@router.post("/{domain}/filters")
async def create_domain_filter(domain: str, filter_data: dict = Body(...)):
    """Create a new filter for iCal export."""
    await get_verified_domain_ddb(domain)

    repo = get_repo()
    filter_obj = repo.create_filter(
        domain_key=domain,
        name=filter_data.get("name", "My Filter"),
        subscribed_group_ids=filter_data.get("subscribed_group_ids", []),
        unselected_event_titles=filter_data.get("unselected_event_titles", []),
        include_future_events=filter_data.get("include_future_events", False)
    )

    return {
        "success": True,
        "link_uuid": filter_obj.link_uuid,
        "name": filter_obj.name,
        "domain_key": filter_obj.domain_key,
        "subscribed_group_ids": filter_obj.subscribed_group_ids,
        "unselected_event_titles": filter_obj.unselected_event_titles,
        "include_future_events": filter_obj.include_future_events
    }


@router.get("/{domain}/filters/{link_uuid}")
async def get_domain_filter(domain: str, link_uuid: str):
    """Get a specific filter."""
    await get_verified_domain_ddb(domain)

    repo = get_repo()
    filter_obj = repo.get_filter_by_uuid(link_uuid)

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    if filter_obj.domain_key != domain:
        raise HTTPException(status_code=404, detail="Filter not found for this domain")

    return {
        "link_uuid": filter_obj.link_uuid,
        "name": filter_obj.name,
        "domain_key": filter_obj.domain_key,
        "subscribed_group_ids": filter_obj.subscribed_group_ids,
        "unselected_event_titles": filter_obj.unselected_event_titles,
        "include_future_events": filter_obj.include_future_events
    }


@router.put("/{domain}/filters/{link_uuid}")
async def update_domain_filter(domain: str, link_uuid: str, filter_data: dict = Body(...)):
    """Update a filter."""
    await get_verified_domain_ddb(domain)

    repo = get_repo()
    filter_obj = repo.get_filter_by_uuid(link_uuid)

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    if filter_obj.domain_key != domain:
        raise HTTPException(status_code=404, detail="Filter not found for this domain")

    # Update fields
    if "name" in filter_data:
        filter_obj.name = filter_data["name"]
    if "subscribed_group_ids" in filter_data:
        filter_obj.subscribed_group_ids = filter_data["subscribed_group_ids"]
    if "unselected_event_titles" in filter_data:
        filter_obj.unselected_event_titles = filter_data["unselected_event_titles"]
    if "include_future_events" in filter_data:
        filter_obj.include_future_events = filter_data["include_future_events"]

    repo.save_filter(filter_obj)

    return {
        "success": True,
        "link_uuid": filter_obj.link_uuid,
        "name": filter_obj.name,
        "subscribed_group_ids": filter_obj.subscribed_group_ids,
        "unselected_event_titles": filter_obj.unselected_event_titles,
        "include_future_events": filter_obj.include_future_events
    }


@router.delete("/{domain}/filters/{link_uuid}")
async def delete_domain_filter(domain: str, link_uuid: str):
    """Delete a filter."""
    await get_verified_domain_ddb(domain)

    repo = get_repo()
    filter_obj = repo.get_filter_by_uuid(link_uuid)

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    if filter_obj.domain_key != domain:
        raise HTTPException(status_code=404, detail="Filter not found for this domain")

    repo.delete_filter(link_uuid)

    return {"success": True, "message": "Filter deleted"}
