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

    Returns events with their group assignments in the format expected by frontend:
    {groups: [{id, name, recurring_events: [{title, event_count, events}]}]}
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

    # Build recurring events structure for each title
    def build_recurring_event(title: str, title_events: list) -> dict:
        """Build a recurring event structure."""
        # Sort events by start time
        title_events.sort(key=lambda e: e.start_time)

        # Build event instances
        event_instances = []
        for event in title_events:
            event_instances.append({
                "uid": event.uid,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "description": event.description,
                "location": event.location
            })

        return {
            "title": title,
            "event_count": len(title_events),
            "events": event_instances
        }

    # Group recurring events by their assigned group
    group_recurring_events = defaultdict(list)
    ungrouped_events = []

    for title, title_events in events_by_title.items():
        recurring_event = build_recurring_event(title, title_events)
        group_id = domain_obj.recurring_assignments.get(title)

        if group_id and group_id in groups_by_id:
            group_recurring_events[group_id].append(recurring_event)
        else:
            ungrouped_events.append(recurring_event)

    # Build groups response with nested recurring_events
    groups_with_events = []
    for group in domain_obj.groups:
        recurring_events = group_recurring_events.get(group.id, [])
        # Sort by title
        recurring_events.sort(key=lambda e: e["title"])

        # Only include groups that have events
        if recurring_events:
            groups_with_events.append({
                "id": group.id,
                "name": group.name,
                "recurring_events": recurring_events
            })

    # Add auto-groups for ungrouped events if any
    if ungrouped_events:
        # Sort ungrouped events
        ungrouped_events.sort(key=lambda e: e["title"])

        # Split into recurring and unique events
        recurring_ungrouped = [e for e in ungrouped_events if e["event_count"] > 1]
        unique_ungrouped = [e for e in ungrouped_events if e["event_count"] == 1]

        if recurring_ungrouped:
            groups_with_events.append({
                "id": -1,  # Auto-group ID
                "name": "📅 Other Recurring Events",
                "recurring_events": recurring_ungrouped
            })

        if unique_ungrouped:
            groups_with_events.append({
                "id": -2,  # Auto-group ID
                "name": "🎯 Special Events",
                "recurring_events": unique_ungrouped
            })

    return {"groups": groups_with_events}


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
