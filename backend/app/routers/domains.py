"""
Domain router for domain calendar management.

Implements domain-specific endpoints from OpenAPI specification.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
import yaml

from ..core.database import get_db
from ..core.config import settings
from ..services.domain_service import (
    load_domains_config, ensure_domain_calendar_exists,
    build_domain_events_response_data, get_domain_groups, create_group,
    assign_recurring_events_to_group, create_assignment_rule,
    get_assignment_rules, auto_assign_events_with_rules,
    get_available_recurring_events, update_group, delete_group, delete_assignment_rule
)
from ..services.domain_config_service import (
    export_domain_configuration, import_domain_configuration
)
from ..services.calendar_service import get_filters, create_filter, delete_filter, get_filter_by_id
from ..services.cache_service import get_or_build_domain_events

router = APIRouter()


@router.get("/{domain}")
async def get_domain_config(domain: str):
    """Get domain configuration from domains.yaml."""
    try:
        # Load domain configuration
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        # Check if domain exists in configuration
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Return the domain configuration
        domain_config = config['domains'][domain]
        return {
            "success": True,
            "data": {
                "domain_key": domain,
                "name": domain_config.get("name", domain),
                "calendar_url": domain_config.get("calendar_url", ""),
                **domain_config  # Include any additional config fields
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
            "export_url": f"/ical/{filter_obj.link_uuid}.ics",
            # Add filter_config for frontend compatibility
            "filter_config": {
                "recurring_events": filter_obj.subscribed_event_ids or [],
                "groups": filter_obj.subscribed_group_ids or []
            },
            "created_at": filter_obj.created_at.isoformat() if filter_obj.created_at else None,
            "updated_at": filter_obj.updated_at.isoformat() if filter_obj.updated_at else None
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
                "export_url": f"/ical/{filter_obj.link_uuid}.ics",
                # Add filter_config for frontend compatibility
                "filter_config": {
                    "recurring_events": filter_obj.subscribed_event_ids or [],
                    "groups": filter_obj.subscribed_group_ids or []
                },
                "created_at": filter_obj.created_at.isoformat() if filter_obj.created_at else None,
                "updated_at": filter_obj.updated_at.isoformat() if filter_obj.updated_at else None
            })
        
        return filters_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{domain}/filters/{filter_id}")
async def update_domain_filter(
    domain: str,
    filter_id: int,
    filter_data: dict,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Update an existing domain filter."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Get existing filter to verify it exists and user has access
        existing_filter = get_filter_by_id(db, filter_id)
        if not existing_filter or existing_filter.domain_key != domain:
            raise HTTPException(status_code=404, detail="Filter not found")
        
        if username and existing_filter.username != username:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update the filter
        if "name" in filter_data:
            existing_filter.name = filter_data["name"].strip()
        if "subscribed_event_ids" in filter_data:
            existing_filter.subscribed_event_ids = filter_data["subscribed_event_ids"]
        if "subscribed_group_ids" in filter_data:
            existing_filter.subscribed_group_ids = filter_data["subscribed_group_ids"]
        
        existing_filter.updated_at = func.now()
        db.commit()
        db.refresh(existing_filter)
        
        # Return updated filter data
        return {
            "id": existing_filter.id,
            "name": existing_filter.name,
            "domain_key": existing_filter.domain_key,
            "username": existing_filter.username,
            "subscribed_event_ids": existing_filter.subscribed_event_ids or [],
            "subscribed_group_ids": existing_filter.subscribed_group_ids or [],
            "link_uuid": existing_filter.link_uuid,
            "export_url": f"/ical/{existing_filter.link_uuid}.ics",
            # Add filter_config for frontend compatibility
            "filter_config": {
                "recurring_events": existing_filter.subscribed_event_ids or [],
                "groups": existing_filter.subscribed_group_ids or []
            },
            "created_at": existing_filter.created_at.isoformat() if existing_filter.created_at else None,
            "updated_at": existing_filter.updated_at.isoformat() if existing_filter.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{domain}/filters/{filter_id}")
async def delete_domain_filter(
    domain: str,
    filter_id: int,
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Delete filter for domain calendar."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Delete filter
        success, error = delete_filter(db, filter_id, domain_key=domain, username=username)
        if not success:
            if "not found" in error.lower():
                raise HTTPException(status_code=404, detail="Filter not found")
            else:
                raise HTTPException(status_code=400, detail=error)
        
        # Return 204 No Content on successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Admin endpoints for event-to-group management

@router.get("/{domain}/recurring-events")
async def get_domain_recurring_events(
    domain: str,
    db: Session = Depends(get_db)
):
    """Get available recurring events for assignment (admin)."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Get recurring events
        recurring_events = get_available_recurring_events(db, domain)
        
        return recurring_events
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{domain}/groups/{group_id}")
async def update_domain_group(
    domain: str,
    group_id: int,
    group_data: dict,
    db: Session = Depends(get_db)
):
    """Update group (admin)."""
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
        
        # Update group
        success, group, error = update_group(db, group_id, domain, group_data["name"])
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{domain}/groups/{group_id}")
async def delete_domain_group(
    domain: str,
    group_id: int,
    db: Session = Depends(get_db)
):
    """Delete group and its assignments (admin)."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Delete group
        success, error = delete_group(db, group_id, domain)
        if not success:
            if "not found" in error.lower():
                raise HTTPException(status_code=404, detail=error)
            else:
                raise HTTPException(status_code=400, detail=error)
        
        # Return 204 No Content on successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{domain}/assignment-rules/{rule_id}")
async def delete_domain_assignment_rule(
    domain: str,
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Delete assignment rule (admin)."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Delete rule
        success, error = delete_assignment_rule(db, rule_id, domain)
        if not success:
            if "not found" in error.lower():
                raise HTTPException(status_code=404, detail=error)
            else:
                raise HTTPException(status_code=400, detail=error)
        
        # Return 204 No Content on successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Configuration Export/Import endpoints for Living Domain System

@router.get("/{domain}/export-config")
async def export_domain_config(
    domain: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Export current domain configuration as YAML (admin)."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Export current domain state
        success, export_config, error = export_domain_configuration(db, domain)
        if not success:
            raise HTTPException(status_code=500, detail=f"Export error: {error}")
        
        # Check if client wants YAML format
        accept_header = request.headers.get('accept', '').lower()
        if 'application/x-yaml' in accept_header or 'text/yaml' in accept_header:
            # Return raw YAML content
            yaml_content = yaml.dump(export_config, default_flow_style=False, indent=2)
            return Response(content=yaml_content, media_type="application/x-yaml")
        else:
            # Return JSON (default)
            return export_config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{domain}/import-config")
async def import_domain_config(
    domain: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Import domain configuration from YAML (admin)."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Get raw content from request
        content_type = request.headers.get('content-type', '').lower()
        
        if 'application/x-yaml' in content_type or 'text/yaml' in content_type:
            # Parse YAML content
            yaml_content = await request.body()
            try:
                config_data = yaml.safe_load(yaml_content.decode('utf-8'))
            except yaml.YAMLError as e:
                raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")
        else:
            # Assume JSON (for backward compatibility)
            config_data = await request.json()
        
        # Validate required fields in import
        if not isinstance(config_data, dict):
            raise HTTPException(status_code=400, detail="Configuration must be an object/dictionary")
        
        required_sections = ["domain", "groups", "assignments", "rules"]
        for section in required_sections:
            if section not in config_data:
                raise HTTPException(status_code=400, detail=f"Missing required section: '{section}'")
        
        # Import configuration
        success, error = import_domain_configuration(db, domain, config_data)
        if not success:
            raise HTTPException(status_code=400, detail=f"Import error: {error}")
        
        return {
            "success": True,
            "message": error  # Contains success message from import function
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{domain}/reset-config")
async def reset_domain_config(
    domain: str,
    db: Session = Depends(get_db)
):
    """Reset domain to baseline configuration from YAML file (admin)."""
    try:
        # Load domain configuration to verify domain exists
        success, config, error = load_domains_config(settings.domains_config_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Configuration error: {error}")
        
        if domain not in config.get('domains', {}):
            raise HTTPException(status_code=404, detail="Domain not found")
        
        # Load baseline configuration from YAML file
        from ..services.domain_config_service import load_domain_configuration
        domains_dir = settings.domains_config_path.parent
        success, baseline_config, error = load_domain_configuration(domain, domains_dir)
        if not success:
            raise HTTPException(status_code=404, detail=f"No baseline configuration found: {error}")
        
        # Import baseline configuration
        success, error = import_domain_configuration(db, domain, baseline_config)
        if not success:
            raise HTTPException(status_code=400, detail=f"Reset error: {error}")
        
        return {
            "success": True,
            "message": f"Domain '{domain}' reset to baseline configuration"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")