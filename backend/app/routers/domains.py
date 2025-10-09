"""
Domain router for domain calendar management.

Implements domain-specific endpoints from OpenAPI specification.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
import yaml

from ..core.database import get_db
from ..core.config import settings
from ..core.auth import require_user_auth, get_current_user_id
from ..models.domain import Domain
from ..services.domain_service import (
    load_domains_config, ensure_domain_calendar_exists,
    build_domain_events_response_data, get_domain_groups, create_group,
    assign_recurring_events_to_group, create_assignment_rule,
    get_assignment_rules, auto_assign_events_with_rules,
    get_available_recurring_events, get_available_recurring_events_with_assignments,
    bulk_unassign_recurring_events, update_group, delete_group, delete_assignment_rule,
    remove_events_from_specific_group
)
from ..services.domain_config_service import (
    export_domain_configuration, import_domain_configuration
)
from ..services.backup_service import (
    create_backup, list_backups, get_backup, delete_backup, restore_backup
)
from ..services.calendar_service import get_filters, create_filter, delete_filter, get_filter_by_id
from ..services.cache_service import get_or_build_domain_events

router = APIRouter()


@router.get("")
async def list_all_domains(db: Session = Depends(get_db)):
    """
    List all available domains.

    PUBLIC ENDPOINT - No authentication required.
    Returns basic domain information including group counts.
    """
    try:
        # Query all domains from database
        domains = db.query(Domain).filter(Domain.status == "active").all()

        # Build response with group counts and password status
        response = []
        for domain in domains:
            # Count groups for this domain using the direct relationship
            group_count = len(domain.groups) if domain.groups else 0

            response.append({
                "domain_key": domain.domain_key,
                "name": domain.name,
                "calendar_url": domain.calendar_url,
                "group_count": group_count,
                "has_user_password": domain.user_password_hash is not None and domain.user_password_hash != "",
                "has_admin_password": domain.admin_password_hash is not None and domain.admin_password_hash != ""
            })

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def verify_domain_exists(db: Session, domain_key: str) -> Domain:
    """
    Verify that a domain exists in the database.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        Domain object if found

    Raises:
        HTTPException: If domain not found
    """
    domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_key}' not found")
    return domain


@router.get("/{domain}")
async def get_domain_config(
    domain: str,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user_id)
):
    """Get domain configuration from database with optional user access info."""
    try:
        # Verify domain exists in database
        domain_obj = verify_domain_exists(db, domain)

        # Determine user's access level if authenticated
        is_owner = False
        is_admin = False
        if user_id:
            is_owner = domain_obj.owner_id == user_id
            is_admin = any(admin.id == user_id for admin in domain_obj.admins)

        return {
            "success": True,
            "data": {
                "id": domain_obj.id,
                "domain_key": domain_obj.domain_key,
                "name": domain_obj.name,
                "calendar_url": domain_obj.calendar_url,
                "status": domain_obj.status,
                "is_owner": is_owner,
                "is_admin": is_admin,
                "has_admin_access": is_owner or is_admin
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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


@router.put("/{domain}/groups/{group_id}/remove-events")
async def remove_events_from_group(
    domain: str,
    group_id: int,
    removal_data: dict,
    db: Session = Depends(get_db)
):
    """Remove events from specific group (admin)."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Validate request data
        if "recurring_event_titles" not in removal_data:
            raise HTTPException(status_code=400, detail="recurring_event_titles is required")
        
        event_titles = removal_data["recurring_event_titles"]
        if not isinstance(event_titles, list):
            raise HTTPException(status_code=400, detail="recurring_event_titles must be an array")
        
        # Remove events from specific group
        success, count, error = remove_events_from_specific_group(db, domain, group_id, event_titles)
        if not success:
            if "not found" in error.lower():
                raise HTTPException(status_code=404, detail=error)
            else:
                raise HTTPException(status_code=400, detail=error)
        
        return {
            "message": f"{count} events removed from group",
            "removed_count": count
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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


@router.post("/{domain}/assignment-rules/apply")
async def apply_domain_assignment_rules(
    domain: str,
    db: Session = Depends(get_db)
):
    """Manually trigger assignment rules to be applied to all events (admin)."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Apply assignment rules
        success, assignment_count, error = await auto_assign_events_with_rules(db, domain)
        if not success:
            raise HTTPException(status_code=500, detail=f"Rule application failed: {error}")

        return {
            "success": True,
            "message": f"Applied assignment rules to {assignment_count} events",
            "assignment_count": assignment_count
        }

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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Validate request data
        if "name" not in filter_data:
            raise HTTPException(status_code=400, detail="Filter name is required")
        
        # Get user_id from username if provided
        user_id = None
        if username:
            from ..models.user import User
            user = db.query(User).filter(User.username == username).first()
            if user:
                user_id = user.id

        # Create filter
        success, filter_obj, error = create_filter(
            db=db,
            name=filter_data["name"],
            domain_key=domain,
            user_id=user_id,
            subscribed_event_ids=filter_data.get("subscribed_event_ids", []),
            subscribed_group_ids=filter_data.get("subscribed_group_ids", []),
            unselected_event_ids=filter_data.get("unselected_event_ids", [])
        )
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        # Return filter data matching OpenAPI schema
        return {
            "id": filter_obj.id,
            "name": filter_obj.name,
            "domain_key": filter_obj.domain_key,
            "user_id": filter_obj.user_id,
            "subscribed_event_ids": filter_obj.subscribed_event_ids or [],
            "subscribed_group_ids": filter_obj.subscribed_group_ids or [],
            "unselected_event_ids": filter_obj.unselected_event_ids or [],
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
    user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List filters for domain calendar (authentication optional - returns user's filters if authenticated)."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)

        # Only get filters if user is authenticated
        if not user_id:
            return []

        # Get filters for authenticated user
        filters = get_filters(db, domain_key=domain, user_id=user_id)
        
        # Transform to OpenAPI schema format
        filters_response = []
        for filter_obj in filters:
            filters_response.append({
                "id": filter_obj.id,
                "name": filter_obj.name,
                "domain_key": filter_obj.domain_key,
                "user_id": filter_obj.user_id,
                "subscribed_event_ids": filter_obj.subscribed_event_ids or [],
                "subscribed_group_ids": filter_obj.subscribed_group_ids or [],
                "unselected_event_ids": filter_obj.unselected_event_ids or [],
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Get existing filter to verify it exists and user has access
        existing_filter = get_filter_by_id(db, filter_id)
        if not existing_filter or existing_filter.domain_key != domain:
            raise HTTPException(status_code=404, detail="Filter not found")

        # Get user_id from username if provided
        user_id = None
        if username:
            from ..models.user import User
            user = db.query(User).filter(User.username == username).first()
            if user:
                user_id = user.id

        # Verify user owns this filter
        if user_id and existing_filter.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update the filter
        if "name" in filter_data:
            existing_filter.name = filter_data["name"].strip()
        if "subscribed_event_ids" in filter_data:
            existing_filter.subscribed_event_ids = filter_data["subscribed_event_ids"]
        if "subscribed_group_ids" in filter_data:
            existing_filter.subscribed_group_ids = filter_data["subscribed_group_ids"]
        if "unselected_event_ids" in filter_data:
            existing_filter.unselected_event_ids = filter_data["unselected_event_ids"]

        existing_filter.updated_at = func.now()
        db.commit()
        db.refresh(existing_filter)

        # Return updated filter data
        return {
            "id": existing_filter.id,
            "name": existing_filter.name,
            "domain_key": existing_filter.domain_key,
            "user_id": existing_filter.user_id,
            "subscribed_event_ids": existing_filter.subscribed_event_ids or [],
            "subscribed_group_ids": existing_filter.subscribed_group_ids or [],
            "unselected_event_ids": existing_filter.unselected_event_ids or [],
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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


# Bulk Assignment endpoints for enhanced admin workflow

@router.get("/{domain}/recurring-events-with-assignments")
async def get_domain_recurring_events_with_assignments(
    domain: str,
    db: Session = Depends(get_db)
):
    """Get available recurring events with their current assignments (admin)."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Get recurring events with assignment information
        events_with_assignments = get_available_recurring_events_with_assignments(db, domain)
        
        return {
            "success": True,
            "data": events_with_assignments
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{domain}/bulk-assign-events")
async def bulk_assign_events_to_group(
    domain: str,
    assignment_data: dict,
    db: Session = Depends(get_db)
):
    """Bulk assign multiple events to a group (admin)."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Validate request data
        if "group_id" not in assignment_data or "recurring_event_titles" not in assignment_data:
            raise HTTPException(status_code=400, detail="group_id and recurring_event_titles are required")
        
        group_id = assignment_data["group_id"]
        event_titles = assignment_data["recurring_event_titles"]
        
        if not isinstance(event_titles, list):
            raise HTTPException(status_code=400, detail="recurring_event_titles must be an array")
        
        # Bulk assign events to group
        success, count, error = assign_recurring_events_to_group(db, domain, group_id, event_titles)
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "message": f"{count} recurring events assigned to group",
            "assigned_count": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{domain}/bulk-unassign-events")
async def bulk_unassign_events(
    domain: str,
    assignment_data: dict,
    db: Session = Depends(get_db)
):
    """Bulk unassign multiple events from their current groups (admin)."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Validate request data
        if "recurring_event_titles" not in assignment_data:
            raise HTTPException(status_code=400, detail="recurring_event_titles is required")
        
        event_titles = assignment_data["recurring_event_titles"]
        
        if not isinstance(event_titles, list):
            raise HTTPException(status_code=400, detail="recurring_event_titles must be an array")
        
        # Bulk unassign events
        success, count, error = bulk_unassign_recurring_events(db, domain, event_titles)
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "message": f"{count} recurring events unassigned",
            "unassigned_count": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{domain}/unassign-event")
async def unassign_single_event(
    domain: str,
    assignment_data: dict,
    db: Session = Depends(get_db)
):
    """Unassign a single event from its current group (admin)."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Validate request data
        if "recurring_event_title" not in assignment_data:
            raise HTTPException(status_code=400, detail="recurring_event_title is required")
        
        event_title = assignment_data["recurring_event_title"]
        
        # Unassign single event
        success, count, error = bulk_unassign_recurring_events(db, domain, [event_title])
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "message": f"Event '{event_title}' unassigned",
            "unassigned_count": count
        }
        
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Export current domain state
        success, export_config, error = export_domain_configuration(db, domain)
        if not success:
            raise HTTPException(status_code=500, detail=f"Export error: {error}")
        
        # Check if client wants YAML format
        accept_header = request.headers.get('accept', '').lower()
        if 'application/x-yaml' in accept_header or 'text/yaml' in accept_header:
            # Return raw YAML content with proper UTF-8 encoding
            yaml_content = yaml.dump(export_config, default_flow_style=False, indent=2, 
                                   allow_unicode=True, encoding=None)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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
        # Verify domain exists in database
        verify_domain_exists(db, domain)
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


# Domain Configuration Backup/Restore Endpoints

@router.post("/{domain}/backups")
async def create_domain_backup(
    domain: str,
    body: Optional[dict] = Body(None),
    db: Session = Depends(get_db)
):
    """Create a backup snapshot of current domain configuration."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Extract description from body if provided
        description = body.get('description') if body else None

        # Create backup
        backup_success, backup, backup_error = create_backup(
            db=db,
            domain_key=domain,
            description=description,
            backup_type='manual'
        )

        if not backup_success:
            raise HTTPException(status_code=500, detail=backup_error)

        # Return backup data matching OpenAPI schema
        return {
            "id": backup.id,
            "domain_key": backup.domain_key,
            "config_snapshot": backup.config_snapshot,
            "created_at": backup.created_at.isoformat() + 'Z' if backup.created_at else None,
            "created_by": backup.created_by,
            "description": backup.description,
            "backup_type": backup.backup_type
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{domain}/backups")
async def get_domain_backups(
    domain: str,
    db: Session = Depends(get_db)
):
    """List all backups for a domain, ordered by creation date (newest first)."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Get backups
        list_success, backups, list_error = list_backups(db=db, domain_key=domain)

        if not list_success:
            raise HTTPException(status_code=500, detail=list_error)

        # Transform to OpenAPI schema format
        backups_response = []
        for backup in backups:
            backups_response.append({
                "id": backup.id,
                "domain_key": backup.domain_key,
                "config_snapshot": backup.config_snapshot,
                "created_at": backup.created_at.isoformat() + 'Z' if backup.created_at else None,
                "created_by": backup.created_by,
                "description": backup.description,
                "backup_type": backup.backup_type
            })

        return backups_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{domain}/backups/{backup_id}")
async def delete_domain_backup(
    domain: str,
    backup_id: int,
    db: Session = Depends(get_db)
):
    """Delete a backup snapshot."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Delete backup
        delete_success, delete_error = delete_backup(
            db=db,
            domain_key=domain,
            backup_id=backup_id
        )

        if not delete_success:
            if "not found" in delete_error.lower():
                raise HTTPException(status_code=404, detail=delete_error)
            raise HTTPException(status_code=500, detail=delete_error)

        return {
            "success": True,
            "message": "Backup deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{domain}/backups/{backup_id}/restore")
async def restore_domain_backup(
    domain: str,
    backup_id: int,
    db: Session = Depends(get_db)
):
    """Restore domain from a backup snapshot. Automatically creates a backup of current state first."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Restore from backup
        restore_success, auto_backup_id, restore_error = restore_backup(
            db=db,
            domain_key=domain,
            backup_id=backup_id
        )

        if not restore_success:
            if "not found" in restore_error.lower():
                raise HTTPException(status_code=404, detail=restore_error)
            raise HTTPException(status_code=500, detail=restore_error)

        return {
            "success": True,
            "message": "Domain restored from backup",
            "auto_backup_id": auto_backup_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{domain}/backups/{backup_id}/download")
async def download_domain_backup(
    domain: str,
    backup_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Download a backup as YAML file."""
    try:
        # Verify domain exists in database
        verify_domain_exists(db, domain)
        # Get backup
        get_success, backup, get_error = get_backup(
            db=db,
            domain_key=domain,
            backup_id=backup_id
        )

        if not get_success:
            if "not found" in get_error.lower():
                raise HTTPException(status_code=404, detail=get_error)
            raise HTTPException(status_code=500, detail=get_error)

        # Convert to YAML
        yaml_content = yaml.dump(backup.config_snapshot, default_flow_style=False, indent=2,
                                allow_unicode=True, encoding=None)

        return Response(content=yaml_content, media_type="application/x-yaml")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Domain Admin Management Endpoints

@router.get("/{domain}/admins")
async def list_domain_admins(
    domain: str,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """List all admins for a domain (owner or admin access required)."""
    try:
        # Verify domain exists
        domain_obj = verify_domain_exists(db, domain)

        # Check if user is owner or admin
        is_owner = domain_obj.owner_id == user_id
        is_admin = any(admin.id == user_id for admin in domain_obj.admins)

        if not is_owner and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Only domain owner or admins can view admin list."
            )

        # Get owner info
        owner_info = None
        if domain_obj.owner:
            owner_info = {
                "id": domain_obj.owner.id,
                "username": domain_obj.owner.username,
                "email": domain_obj.owner.email
            }

        # Get admin list
        admins_list = []
        for admin in domain_obj.admins:
            admins_list.append({
                "id": admin.id,
                "username": admin.username,
                "email": admin.email
            })

        return {
            "owner": owner_info,
            "admins": admins_list
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{domain}/admins")
async def add_domain_admin(
    domain: str,
    request_data: dict,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Add a user as admin for the domain (owner access required)."""
    try:
        # Verify domain exists
        domain_obj = verify_domain_exists(db, domain)

        # Check if user is owner
        if domain_obj.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Only domain owner can add admins."
            )

        # Validate request
        if "username" not in request_data:
            raise HTTPException(status_code=400, detail="username is required")

        username = request_data["username"].strip()

        # Find user to add as admin
        from ..models.user import User
        user_to_add = db.query(User).filter(User.username == username).first()
        if not user_to_add:
            raise HTTPException(status_code=400, detail=f"User '{username}' not found")

        # Check if already admin
        if user_to_add in domain_obj.admins:
            raise HTTPException(status_code=409, detail=f"User '{username}' is already an admin")

        # Check if trying to add owner as admin
        if user_to_add.id == domain_obj.owner_id:
            raise HTTPException(status_code=400, detail="Domain owner is already admin by default")

        # Add admin
        domain_obj.admins.append(user_to_add)
        db.commit()

        return {
            "success": True,
            "message": f"User '{username}' added as admin"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{domain}/admins/{username}")
async def remove_domain_admin(
    domain: str,
    username: str,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Remove a user from domain admins (owner access required)."""
    try:
        # Verify domain exists
        domain_obj = verify_domain_exists(db, domain)

        # Check if user is owner
        if domain_obj.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Only domain owner can remove admins."
            )

        # Find user to remove
        from ..models.user import User
        user_to_remove = db.query(User).filter(User.username == username).first()
        if not user_to_remove:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

        # Check if user is admin
        if user_to_remove not in domain_obj.admins:
            raise HTTPException(status_code=404, detail=f"User '{username}' is not an admin")

        # Remove admin
        domain_obj.admins.remove(user_to_remove)
        db.commit()

        return {
            "success": True,
            "message": f"User '{username}' removed from admins"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
