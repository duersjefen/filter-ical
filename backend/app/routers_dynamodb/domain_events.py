"""
Domain events router for DynamoDB backend.

Implements event listing and grouping endpoints.
"""

from datetime import datetime
from collections import defaultdict
from fastapi import APIRouter

from .deps import get_repo, get_verified_domain_ddb

router = APIRouter()


@router.get("/{domain}/events")
async def get_domain_events(domain: str):
    """
    Get events for domain calendar grouped by title.

    Returns events with their group assignments.
    """
    domain_obj = await get_verified_domain_ddb(domain)
    repo = get_repo()

    # Get all events for this domain
    events = repo.get_events(domain)

    # Build groups lookup
    groups_by_id = {g.id: g for g in domain_obj.groups}

    # Group events by title (recurring events detection)
    events_by_title = defaultdict(list)
    for event in events:
        events_by_title[event.title].append(event)

    # Build response with group assignments
    recurring_events = []
    for title, title_events in events_by_title.items():
        # Get group assignment for this title
        group_id = domain_obj.recurring_assignments.get(title)
        group_name = None
        if group_id and group_id in groups_by_id:
            group_name = groups_by_id[group_id].name

        # Sort events by start time
        title_events.sort(key=lambda e: e.start_time)

        # Build event instances
        instances = []
        for event in title_events:
            instances.append({
                "uid": event.uid,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "description": event.description,
                "location": event.location
            })

        recurring_events.append({
            "title": title,
            "group_id": group_id,
            "group_name": group_name,
            "event_count": len(title_events),
            "instances": instances
        })

    # Sort by title
    recurring_events.sort(key=lambda e: e["title"])

    return {
        "domain_key": domain,
        "groups": [{"id": g.id, "name": g.name} for g in domain_obj.groups],
        "recurring_events": recurring_events,
        "total_events": len(events)
    }


@router.get("/{domain}/recurring-events")
async def get_recurring_events(domain: str):
    """Get available recurring event titles for assignment."""
    domain_obj = await get_verified_domain_ddb(domain)
    repo = get_repo()

    events = repo.get_events(domain)

    # Get unique titles
    titles = set(e.title for e in events)

    # Build response with assignment status
    recurring_events = []
    for title in sorted(titles):
        group_id = domain_obj.recurring_assignments.get(title)
        recurring_events.append({
            "title": title,
            "assigned_group_id": group_id
        })

    return recurring_events


@router.get("/{domain}/recurring-events-with-assignments")
async def get_recurring_events_with_assignments(domain: str):
    """Get recurring events with their current group assignments."""
    domain_obj = await get_verified_domain_ddb(domain)
    repo = get_repo()

    events = repo.get_events(domain)

    # Count events per title
    title_counts = defaultdict(int)
    for event in events:
        title_counts[event.title] += 1

    # Build response
    groups_by_id = {g.id: g.name for g in domain_obj.groups}
    recurring_events = []

    for title in sorted(title_counts.keys()):
        group_id = domain_obj.recurring_assignments.get(title)
        group_name = groups_by_id.get(group_id) if group_id else None

        recurring_events.append({
            "title": title,
            "event_count": title_counts[title],
            "assigned_group_id": group_id,
            "assigned_group_name": group_name
        })

    return recurring_events
