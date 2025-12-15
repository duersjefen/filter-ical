"""
Sync service for DynamoDB backend.

Provides calendar sync functionality for Lambda scheduled tasks.
"""

import httpx
from datetime import datetime
from typing import Optional

from ..db.repository import get_repository
from ..db.models import Event


async def fetch_ical_content(calendar_url: str, timeout: float = 30.0) -> Optional[str]:
    """Fetch iCal content from URL."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(calendar_url)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"Failed to fetch calendar: {e}")
        return None


def parse_ical_datetime(value: str) -> datetime:
    """Parse iCal datetime value."""
    value = value.replace("Z", "")

    formats = [
        "%Y%m%dT%H%M%S",
        "%Y%m%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return datetime.utcnow()


def parse_ical_events(content: str) -> list[dict]:
    """Parse iCal content into event dictionaries."""
    events = []
    current_event = None

    for line in content.split("\n"):
        line = line.strip()

        if line == "BEGIN:VEVENT":
            current_event = {}
        elif line == "END:VEVENT" and current_event:
            if "uid" in current_event and "title" in current_event:
                events.append(current_event)
            current_event = None
        elif current_event is not None:
            if line.startswith("UID:"):
                current_event["uid"] = line[4:]
            elif line.startswith("SUMMARY:"):
                current_event["title"] = line[8:]
            elif line.startswith("DTSTART"):
                value = line.split(":")[-1]
                current_event["start_time"] = parse_ical_datetime(value)
                current_event["start_date"] = current_event["start_time"].strftime("%Y-%m-%d")
            elif line.startswith("DTEND"):
                value = line.split(":")[-1]
                current_event["end_time"] = parse_ical_datetime(value)
            elif line.startswith("DESCRIPTION:"):
                current_event["description"] = line[12:].replace("\\n", "\n").replace("\\,", ",")
            elif line.startswith("LOCATION:"):
                current_event["location"] = line[9:].replace("\\,", ",")

    return events


async def sync_domain_calendar(domain_key: str) -> dict:
    """
    Sync a single domain's calendar from its URL.

    Returns sync result with counts.
    """
    repo = get_repository()

    # Get domain
    domain = repo.get_domain(domain_key)
    if not domain:
        return {"success": False, "error": f"Domain '{domain_key}' not found"}

    # Fetch calendar
    content = await fetch_ical_content(domain.calendar_url)
    if not content:
        return {"success": False, "error": "Failed to fetch calendar"}

    # Parse events
    parsed_events = parse_ical_events(content)
    if not parsed_events:
        return {"success": False, "error": "No events found in calendar"}

    # Delete old events
    deleted_count = repo.delete_all_events(domain_key)

    # Save new events
    event_objs = []
    for e in parsed_events:
        event_objs.append(Event(
            domain_key=domain_key,
            uid=e["uid"],
            start_date=e.get("start_date", ""),
            title=e["title"],
            start_time=e.get("start_time", datetime.utcnow()),
            end_time=e.get("end_time"),
            description=e.get("description"),
            location=e.get("location")
        ))

    repo.save_events(event_objs)

    return {
        "success": True,
        "domain_key": domain_key,
        "deleted_count": deleted_count,
        "synced_count": len(event_objs)
    }


async def sync_all_domains() -> dict:
    """
    Sync all active domains.

    Used by scheduled Lambda task.
    """
    repo = get_repository()
    domains = repo.list_domains()

    results = []
    success_count = 0
    error_count = 0

    for domain in domains:
        if domain.status != "active":
            continue

        result = await sync_domain_calendar(domain.domain_key)
        results.append(result)

        if result.get("success"):
            success_count += 1
            print(f"Synced {domain.domain_key}: {result.get('synced_count')} events")
        else:
            error_count += 1
            print(f"Failed to sync {domain.domain_key}: {result.get('error')}")

    return {
        "success": True,
        "synced_domains": success_count,
        "failed_domains": error_count,
        "results": results
    }
