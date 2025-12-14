"""
iCal export router for DynamoDB backend.

Generates filtered iCal files for calendar subscriptions.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from .deps import get_repo

router = APIRouter()


def generate_ical(events: list, filter_name: str = "Filtered Calendar") -> str:
    """Generate iCal content from events."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Filter iCal//filter-ical.de//",
        f"X-WR-CALNAME:{filter_name}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]

    for event in events:
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{event.uid}")
        lines.append(f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}")

        # Format start time
        if event.start_time:
            dt = event.start_time
            if dt.hour == 0 and dt.minute == 0:
                # All-day event
                lines.append(f"DTSTART;VALUE=DATE:{dt.strftime('%Y%m%d')}")
            else:
                lines.append(f"DTSTART:{dt.strftime('%Y%m%dT%H%M%SZ')}")

        # Format end time
        if event.end_time:
            dt = event.end_time
            if dt.hour == 0 and dt.minute == 0:
                lines.append(f"DTEND;VALUE=DATE:{dt.strftime('%Y%m%d')}")
            else:
                lines.append(f"DTEND:{dt.strftime('%Y%m%dT%H%M%SZ')}")

        lines.append(f"SUMMARY:{event.title}")

        if event.description:
            # Escape description
            desc = event.description.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,")
            lines.append(f"DESCRIPTION:{desc}")

        if event.location:
            loc = event.location.replace(",", "\\,")
            lines.append(f"LOCATION:{loc}")

        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    return "\r\n".join(lines)


@router.get("/{link_uuid}.ics")
@router.head("/{link_uuid}.ics")
async def export_filtered_ical(link_uuid: str, request: Request):
    """
    Export filtered calendar as iCal file.

    PUBLIC ENDPOINT - Accessed by calendar apps for subscription.
    """
    repo = get_repo()

    # Get filter
    filter_obj = repo.get_filter_by_uuid(link_uuid)
    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    # Get domain
    domain_obj = repo.get_domain(filter_obj.domain_key)
    if not domain_obj:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Get all events
    all_events = repo.get_events(filter_obj.domain_key)

    # Apply filter
    filtered_events = []
    subscribed_group_ids = set(filter_obj.subscribed_group_ids)
    unselected_titles = set(filter_obj.unselected_event_titles)

    for event in all_events:
        # Skip unselected events
        if event.title in unselected_titles:
            continue

        # If no groups selected, include all (default behavior)
        if not subscribed_group_ids:
            filtered_events.append(event)
            continue

        # Check if event's title is assigned to a subscribed group
        assigned_group_id = domain_obj.recurring_assignments.get(event.title)
        if assigned_group_id in subscribed_group_ids:
            filtered_events.append(event)

    # Generate iCal
    ical_content = generate_ical(filtered_events, filter_obj.name)

    # Return response with proper headers for calendar apps
    return Response(
        content=ical_content,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filter_obj.name}.ics"',
            "Cache-Control": "no-cache, must-revalidate",
            "ETag": f'"{hash(ical_content)}"'
        }
    )
