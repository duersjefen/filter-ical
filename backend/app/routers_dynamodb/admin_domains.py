"""
Admin domain management router for DynamoDB backend.

Implements admin-only domain CRUD endpoints.
"""

import re
import httpx
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body

from .deps import get_repo
from ..db.models import Domain, Event

router = APIRouter()


def validate_domain_key(domain_key: str) -> bool:
    """Validate domain key format (lowercase, numbers, hyphens only)."""
    return bool(re.match(r"^[a-z0-9-]+$", domain_key))


async def fetch_and_parse_ical(calendar_url: str) -> list[dict]:
    """
    Fetch iCal from URL and parse events.

    Returns list of event dictionaries.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(calendar_url)
            response.raise_for_status()
            content = response.text

        # Simple iCal parser
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
                    # Parse various date formats
                    value = line.split(":")[-1]
                    current_event["start_time"] = parse_ical_datetime(value)
                    current_event["start_date"] = current_event["start_time"].strftime("%Y-%m-%d") if current_event["start_time"] else ""
                elif line.startswith("DTEND"):
                    value = line.split(":")[-1]
                    current_event["end_time"] = parse_ical_datetime(value)
                elif line.startswith("DESCRIPTION:"):
                    current_event["description"] = line[12:].replace("\\n", "\n").replace("\\,", ",")
                elif line.startswith("LOCATION:"):
                    current_event["location"] = line[9:].replace("\\,", ",")

        return events

    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch calendar: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse calendar: {str(e)}")


def parse_ical_datetime(value: str) -> datetime:
    """Parse iCal datetime value."""
    value = value.replace("Z", "")

    # Try various formats
    formats = [
        "%Y%m%dT%H%M%S",
        "%Y%m%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    # Fallback
    return datetime.utcnow()


@router.get("/admin/domains")
async def list_all_domains_admin():
    """List all domains (admin view with inactive)."""
    repo = get_repo()
    domains = repo.list_domains()

    return [
        {
            "domain_key": d.domain_key,
            "name": d.name,
            "calendar_url": d.calendar_url,
            "status": d.status,
            "group_count": len(d.groups),
            "has_admin_password": d.admin_password_hash is not None,
            "has_user_password": d.user_password_hash is not None,
            "created_at": d.created_at.isoformat(),
            "updated_at": d.updated_at.isoformat()
        }
        for d in domains
    ]


@router.post("/admin/domains")
async def create_domain(data: dict = Body(...)):
    """Create a new domain."""
    domain_key = data.get("domain_key", "").lower().strip()
    name = data.get("name", "").strip()
    calendar_url = data.get("calendar_url", "").strip()

    # Validate
    if not domain_key:
        raise HTTPException(status_code=400, detail="domain_key is required")
    if not validate_domain_key(domain_key):
        raise HTTPException(status_code=400, detail="domain_key must contain only lowercase letters, numbers, and hyphens")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    if not calendar_url:
        raise HTTPException(status_code=400, detail="calendar_url is required")
    if not calendar_url.startswith("http://") and not calendar_url.startswith("https://"):
        raise HTTPException(status_code=400, detail="calendar_url must start with http:// or https://")

    repo = get_repo()

    # Check if domain already exists
    existing = repo.get_domain(domain_key)
    if existing:
        raise HTTPException(status_code=409, detail=f"Domain '{domain_key}' already exists")

    # Fetch and validate calendar
    events = await fetch_and_parse_ical(calendar_url)
    if not events:
        raise HTTPException(status_code=400, detail="Calendar has no events")

    # Create domain
    domain = Domain(
        domain_key=domain_key,
        name=name,
        calendar_url=calendar_url,
        status="active"
    )
    repo.save_domain(domain)

    # Save events
    event_objs = []
    for e in events:
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

    if event_objs:
        repo.save_events(event_objs)

    return {
        "success": True,
        "domain_key": domain_key,
        "name": name,
        "event_count": len(event_objs)
    }


@router.delete("/admin/domains/{domain_key}")
async def delete_domain(domain_key: str):
    """Delete a domain and all its data."""
    repo = get_repo()

    # Check if domain exists
    domain = repo.get_domain(domain_key)
    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_key}' not found")

    # Delete domain (this also deletes events)
    repo.delete_domain(domain_key)

    # Also delete filters for this domain
    filters = repo.list_filters_for_domain(domain_key)
    for f in filters:
        repo.delete_filter(f.link_uuid)

    return {
        "success": True,
        "message": f"Domain '{domain_key}' deleted"
    }


@router.post("/admin/domains/{domain_key}/sync")
async def sync_domain_events(domain_key: str):
    """Sync events from calendar URL."""
    repo = get_repo()

    domain = repo.get_domain(domain_key)
    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_key}' not found")

    # Fetch events
    events = await fetch_and_parse_ical(domain.calendar_url)

    # Delete old events
    deleted_count = repo.delete_all_events(domain_key)

    # Save new events
    event_objs = []
    for e in events:
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

    if event_objs:
        repo.save_events(event_objs)

    return {
        "success": True,
        "deleted_count": deleted_count,
        "synced_count": len(event_objs)
    }
