"""
Domain router for domain calendar management.

Implements domain-specific endpoints from OpenAPI specification.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.config import settings
from ..services.domain_service import (
    load_domains_config, ensure_domain_calendar_exists,
    build_domain_events_response_data, get_domain_groups, create_group,
    assign_recurring_events_to_group, create_assignment_rule,
    get_assignment_rules, auto_assign_events_with_rules
)
from ..services.calendar_service import get_filters, create_filter
from ..services.cache_service import get_or_build_domain_events

router = APIRouter()


@router.get("/{domain}/events")
async def get_domain_events(
    domain: str,
    username: Optional[str] = Query(None),
    force_refresh: bool = Query(False, description="Force refresh cache"),
    db: Session = Depends(get_db)
):
    """Get domain calendar events (grouped structure) - cached for performance."""
    try:
        # Load domain configuration
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        # Check if domain exists in configuration
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Get cached domain events or build if needed
        success, response_data, error = get_or_build_domain_events(db, domain, force_refresh)
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Cache error: {error}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{domain}/groups")
async def get_domain_groups_endpoint(
    domain: str,
    db: Session = Depends(get_db)
):
    """Get groups for domain calendar."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Get groups from database
        groups = get_domain_groups(db, domain)
        
        # Transform to OpenAPI schema format
        groups_response = []
        for group in groups:
            groups_response.append({
                "id": group.id,
                "name": group.name,
                "domain_key": group.domain_key
            })
        
        return groups_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{domain}/groups")
async def create_domain_group(
    domain: str,
    group_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new group (admin)."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Validate request data
        if "name" not in group_data:
            raise HTTPException(status_code=400, detail="Group name is required")
        
        # Create group
        success, group, error = create_group(db, domain, group_data["name"])
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        # Return group data matching OpenAPI schema
        return {
            "id": group.id,
            "name": group.name,
            "domain_key": group.domain_key
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{domain}/groups/{group_id}/assign-recurring-events")
async def assign_recurring_events(
    domain: str,
    group_id: int,
    assignment_data: dict,
    db: Session = Depends(get_db)
):
    """Manually assign recurring events to group (admin)."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Validate request data
        if "recurring_event_titles" not in assignment_data:
            raise HTTPException(status_code=400, detail="recurring_event_titles is required")
        
        event_titles = assignment_data["recurring_event_titles"]
        if not isinstance(event_titles, list):
            raise HTTPException(status_code=400, detail="recurring_event_titles must be an array")
        
        # Assign events to group
        success, count, error = assign_recurring_events_to_group(db, domain, group_id, event_titles)
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "message": f"{count} recurring events assigned to group"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{domain}/assignment-rules")
async def create_domain_assignment_rule(
    domain: str,
    rule_data: dict,
    db: Session = Depends(get_db)
):
    """Create auto-assignment rule (admin)."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Validate required fields
        required_fields = ["rule_type", "rule_value", "target_group_id"]
        for field in required_fields:
            if field not in rule_data:
                raise HTTPException(status_code=400, detail=f"{field} is required")
        
        # Create assignment rule
        success, rule, error = create_assignment_rule(
            db, domain, 
            rule_data["rule_type"],
            rule_data["rule_value"],
            rule_data["target_group_id"]
        )
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        # Return rule data matching OpenAPI schema
        return {
            "id": rule.id,
            "rule_type": rule.rule_type,
            "rule_value": rule.rule_value,
            "target_group_id": rule.target_group_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{domain}/assignment-rules")
async def get_domain_assignment_rules(
    domain: str,
    db: Session = Depends(get_db)
):
    """List assignment rules for domain."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Get assignment rules
        rules = get_assignment_rules(db, domain)
        
        # Transform to OpenAPI schema format
        rules_response = []
        for rule in rules:
            rules_response.append({
                "id": rule.id,
                "rule_type": rule.rule_type,
                "rule_value": rule.rule_value,
                "target_group_id": rule.target_group_id
            })
        
        return rules_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{domain}/filters")
async def create_domain_filter(
    domain: str,
    filter_data: dict,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Create filter for domain calendar."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Validate request data
        if "name" not in filter_data:
            raise HTTPException(status_code=400, detail="Filter name is required")
        
        # Create filter
        success, filter_obj, error = create_filter(
            db=db,
            name=filter_data["name"],
            domain_key=domain,
            username=username,
            subscribed_event_ids=filter_data.get("subscribed_event_ids", []),
            subscribed_group_ids=filter_data.get("subscribed_group_ids", [])
        )
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        # Return filter data matching OpenAPI schema
        return {
            "id": filter_obj.id,
            "name": filter_obj.name,
            "domain_key": filter_obj.domain_key,
            "username": filter_obj.username,
            "subscribed_event_ids": filter_obj.subscribed_event_ids or [],
            "subscribed_group_ids": filter_obj.subscribed_group_ids or [],
            "link_uuid": filter_obj.link_uuid,
            "export_url": f"/ical/{filter_obj.link_uuid}.ics"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{domain}/filters")
async def get_domain_filters(
    domain: str,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List filters for domain calendar."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Get filters
        filters = get_filters(db, domain_key=domain, username=username)
        
        # Transform to OpenAPI schema format
        filters_response = []
        for filter_obj in filters:
            filters_response.append({
                "id": filter_obj.id,
                "name": filter_obj.name,
                "domain_key": filter_obj.domain_key,
                "username": filter_obj.username,
                "subscribed_event_ids": filter_obj.subscribed_event_ids or [],
                "subscribed_group_ids": filter_obj.subscribed_group_ids or [],
                "link_uuid": filter_obj.link_uuid,
                "export_url": f"/ical/{filter_obj.link_uuid}.ics"
            })
        
        return filters_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")