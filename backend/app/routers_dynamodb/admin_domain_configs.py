"""
Admin domain configuration router for DynamoDB backend.

Implements YAML-based domain seeding and configuration management.
"""

import yaml
import httpx
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException

from .deps import get_repo
from ..db.models import Domain, DomainGroup, AssignmentRule, Event
from ..core.config import settings

router = APIRouter()


def get_domains_dir() -> Path:
    """Get the domains configuration directory."""
    return settings.domains_config_path.parent


def load_yaml_config(domain_key: str) -> dict:
    """Load a domain's YAML configuration file."""
    yaml_path = get_domains_dir() / f"{domain_key}.yaml"
    if not yaml_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Configuration file not found: {domain_key}.yaml"
        )

    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


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
                    current_event["start_date"] = current_event["start_time"].strftime("%Y-%m-%d") if current_event["start_time"] else ""
                elif line.startswith("DTEND"):
                    value = line.split(":")[-1]
                    current_event["end_time"] = parse_ical_datetime(value)
                elif line.startswith("DESCRIPTION:"):
                    current_event["description"] = line[12:].replace("\\n", "\n").replace("\\,", ",")
                elif line.startswith("LOCATION:"):
                    current_event["location"] = line[9:].replace("\\,", ",")
                elif line.startswith("CATEGORIES:"):
                    current_event["categories"] = line[11:].replace("\\,", ",")

        return events

    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch calendar: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse calendar: {str(e)}")


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


@router.get("/admin/domain-configs")
async def list_domain_configs():
    """List all available domain configuration YAML files."""
    domains_dir = get_domains_dir()

    if not domains_dir.exists():
        return {"configs": []}

    configs = []
    for yaml_file in domains_dir.glob("*.yaml"):
        if yaml_file.name != "domains.yaml":  # Skip registry file
            domain_key = yaml_file.stem
            try:
                config = load_yaml_config(domain_key)
                configs.append({
                    "domain_key": domain_key,
                    "name": config.get("domain", {}).get("name", domain_key),
                    "group_count": len(config.get("groups", [])),
                    "assignment_count": sum(len(v) for v in config.get("assignments", {}).values()),
                    "rule_count": len(config.get("rules", [])),
                })
            except Exception:
                configs.append({
                    "domain_key": domain_key,
                    "name": domain_key,
                    "error": "Failed to parse"
                })

    return {"configs": configs}


@router.get("/admin/domain-configs/{domain_key}")
async def get_domain_config(domain_key: str):
    """Get a domain's YAML configuration."""
    config = load_yaml_config(domain_key)
    return config


@router.post("/admin/domain-configs/{domain_key}/seed")
async def seed_domain_from_yaml(domain_key: str):
    """
    Seed a domain from its YAML configuration file.

    Creates the domain with all groups, assignments, and rules from the YAML.
    Also fetches and imports events from the calendar URL.
    """
    repo = get_repo()

    # Check if domain already exists
    existing = repo.get_domain(domain_key)
    if existing:
        return {
            "success": True,
            "message": f"Domain '{domain_key}' already exists",
            "domain_key": domain_key,
            "group_count": len(existing.groups),
            "assignment_count": len(existing.recurring_assignments),
            "already_existed": True
        }

    # Load YAML configuration
    config = load_yaml_config(domain_key)

    domain_config = config.get("domain", {})
    groups_config = config.get("groups", [])
    assignments_config = config.get("assignments", {})
    rules_config = config.get("rules", [])

    # Build semantic ID to numeric ID mapping
    semantic_to_numeric = {}
    groups = []

    for idx, group_cfg in enumerate(groups_config, start=1):
        semantic_id = group_cfg.get("id", f"group_{idx}")
        semantic_to_numeric[semantic_id] = idx

        groups.append(DomainGroup(
            id=idx,
            name=group_cfg.get("name", semantic_id),
            rules=[],  # Rules added below
        ))

    # Add assignment rules to groups
    for rule_cfg in rules_config:
        target_semantic_id = rule_cfg.get("target_group_id")
        target_numeric_id = semantic_to_numeric.get(target_semantic_id)

        if target_numeric_id:
            # Find the group and add the rule
            for group in groups:
                if group.id == target_numeric_id:
                    rule = AssignmentRule(
                        id=len(group.rules) + 1,
                        type=rule_cfg.get("rule_type"),
                        value=rule_cfg.get("rule_value"),
                        is_compound=False,
                    )
                    group.rules.append(rule)
                    break

    # Build recurring assignments mapping
    recurring_assignments = {}
    for semantic_group_id, event_titles in assignments_config.items():
        numeric_id = semantic_to_numeric.get(semantic_group_id)
        if numeric_id:
            for event_title in event_titles:
                recurring_assignments[event_title] = numeric_id

    # Create domain
    domain = Domain(
        domain_key=domain_key,
        name=domain_config.get("name", domain_key),
        calendar_url=domain_config.get("calendar_url", ""),
        status="active",
        groups=groups,
        recurring_assignments=recurring_assignments,
    )

    repo.save_domain(domain)

    # Fetch and save events from calendar
    event_count = 0
    if domain.calendar_url:
        try:
            events_data = await fetch_and_parse_ical(domain.calendar_url)
            event_objs = []

            for e in events_data:
                event_objs.append(Event(
                    domain_key=domain_key,
                    uid=e["uid"],
                    start_date=e.get("start_date", ""),
                    title=e["title"],
                    start_time=e.get("start_time", datetime.utcnow()),
                    end_time=e.get("end_time"),
                    description=e.get("description"),
                    location=e.get("location"),
                ))

            if event_objs:
                repo.save_events(event_objs)
                event_count = len(event_objs)

        except Exception as e:
            # Don't fail the whole operation if calendar fetch fails
            print(f"Warning: Failed to fetch calendar events: {e}")

    return {
        "success": True,
        "message": f"Domain '{domain_key}' seeded successfully",
        "domain_key": domain_key,
        "name": domain.name,
        "group_count": len(groups),
        "assignment_count": len(recurring_assignments),
        "rule_count": sum(len(g.rules) for g in groups),
        "event_count": event_count,
        "already_existed": False
    }


@router.delete("/admin/domain-configs/{domain_key}/reset")
async def reset_domain_config(domain_key: str):
    """
    Reset a domain by deleting it and re-seeding from YAML.

    WARNING: This will delete all existing data for the domain.
    """
    repo = get_repo()

    # Delete existing domain and its events
    existing = repo.get_domain(domain_key)
    if existing:
        repo.delete_domain(domain_key)

    # Re-seed from YAML
    return await seed_domain_from_yaml(domain_key)
