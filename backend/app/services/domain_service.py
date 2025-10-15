"""
Domain service for domain calendar operations and grouping.

IMPERATIVE SHELL - Orchestrates pure functions with I/O operations.
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import func

from ..models.calendar import Calendar, Event, Group, RecurringEventGroup, AssignmentRule
from ..models.domain import Domain
from ..data.grouping import (
    load_domain_config, get_domain_config, create_group_data, create_recurring_event_group_data,
    create_assignment_rule_data, apply_assignment_rules, build_domain_events_response,
    build_domain_events_with_auto_groups, validate_group_data, validate_assignment_rule_data
)
from ..data.ical_parser import group_events_by_title
from .calendar_service import get_calendar_by_domain, sync_calendar_events


def load_domains_config(config_path: Path) -> Tuple[bool, Dict[str, Any], str]:
    """
    Load domain configuration from file.

    Args:
        config_path: Path to domains.yaml file

    Returns:
        Tuple of (success, config_dict, error_message)

    I/O Operation - File reading with error handling.
    """
    try:
        if not config_path.exists():
            return False, {}, f"Domain configuration file not found: {config_path}"

        with open(config_path, 'r') as f:
            config_content = f.read()

        # Use pure function to parse content
        result = load_domain_config(config_content)
        if not result.is_success:
            return False, {}, result.error
        return True, result.value, ""
        
    except Exception as e:
        return False, {}, f"Error reading domain configuration: {str(e)}"


async def ensure_domain_calendar_exists(db: Session, domain_key: str) -> Tuple[bool, Optional[Calendar], str]:
    """
    Ensure domain calendar exists and is up to date.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        Tuple of (success, calendar_obj, error_message)

    I/O Operation - Database operations with domain model.
    """
    try:
        # Get domain from database
        domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
        if not domain:
            return False, None, f"Domain {domain_key} not found"

        # Check if domain has a calendar
        if domain.calendar_id:
            calendar = db.query(Calendar).filter(Calendar.id == domain.calendar_id).first()
        else:
            calendar = None

        if not calendar:
            # Create domain calendar
            calendar = Calendar(
                name=domain.name,
                source_url=domain.calendar_url,
                type="domain",
                user_id=None
            )
            db.add(calendar)
            db.commit()
            db.refresh(calendar)

            # Link calendar to domain
            domain.calendar_id = calendar.id
            db.commit()

        # Sync calendar events
        sync_success, event_count, sync_error = await sync_calendar_events(db, calendar)
        if not sync_success:
            return False, calendar, sync_error

        return True, calendar, ""

    except Exception as e:
        return False, None, f"Error ensuring domain calendar: {str(e)}"


def get_domain_events(db: Session, domain_key: str) -> List[Dict[str, Any]]:
    """
    Get events for domain calendar.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        List of event dictionaries
        
    I/O Operation - Database query with transformation.
    """
    calendar = get_calendar_by_domain(db, domain_key)
    if not calendar:
        return []
    
    events = db.query(Event).filter(Event.calendar_id == calendar.id).all()
    
    # Transform to dictionaries for pure function processing
    event_dicts = []
    for event in events:
        # Extract categories from other_ical_fields if available
        categories = []
        raw_ical = ""
        if event.other_ical_fields and isinstance(event.other_ical_fields, dict):
            categories = event.other_ical_fields.get('categories', [])
            # Store raw iCal for rule matching (reconstructed minimal format)
            if categories:
                raw_ical = "\n".join([f"CATEGORIES:{cat}" for cat in categories])

        event_dict = {
            "id": f"evt_{event.id}",
            "calendar_id": f"domain_{domain_key}",
            "title": event.title,
            "start_time": event.start_time,  # Fixed: use start_time for export compatibility
            "end_time": event.end_time,      # Fixed: use end_time for export compatibility
            "description": event.description or "",
            "location": event.location,
            "uid": event.uid,
            "raw_ical": raw_ical,  # For category matching in rules
            "other_ical_fields": {           # Fixed: nest raw_ical for export compatibility
                "raw_ical": event.other_ical_fields.get("raw_ical", "") if event.other_ical_fields else ""
            },
            # Keep legacy format for domain UI compatibility
            "start": event.start_time.isoformat() if event.start_time else None,
            "end": event.end_time.isoformat() if event.end_time else None,
            "is_recurring": False,  # Will be determined by grouping
            "raw_ical": event.other_ical_fields.get("raw_ical", "") if event.other_ical_fields else ""
        }
        event_dicts.append(event_dict)

    return event_dicts


def get_domain_groups(db: Session, domain_key: str) -> List[Group]:
    """
    Get groups for domain.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        List of group objects

    I/O Operation - Database query.
    """
    # PERFORMANCE: Eager load recurring events to avoid N+1 query pattern
    # This is useful when groups are accessed with their recurring events
    return db.query(Group).options(
        selectinload(Group.recurring_event_groups)
    ).filter(Group.domain_key == domain_key).all()


def create_group(db: Session, domain_key: str, name: str) -> Tuple[bool, Optional[Group], str]:
    """
    Create group in database.

    Args:
        db: Database session
        domain_key: Domain identifier
        name: Group name

    Returns:
        Tuple of (success, group_obj, error_message)

    I/O Operation - Database creation with validation.
    """
    # Validate data using pure function
    validation_result = validate_group_data(name, domain_key)
    if not validation_result.is_success:
        return False, None, validation_result.error

    try:
        # Get domain_id from domain_key
        domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
        if not domain:
            return False, None, f"Domain {domain_key} not found"

        # Create group with both domain_id and domain_key for backward compatibility
        group = Group(
            domain_id=domain.id,
            domain_key=domain_key,
            name=name.strip()
        )
        db.add(group)
        db.commit()
        db.refresh(group)

        return True, group, ""

    except Exception as e:
        db.rollback()
        return False, None, f"Database error: {str(e)}"


def assign_recurring_events_to_group(db: Session, domain_key: str, group_id: int,
                                   recurring_event_titles: List[str]) -> Tuple[bool, int, str]:
    """
    Assign recurring events to group.

    Args:
        db: Database session
        domain_key: Domain identifier
        group_id: Target group ID
        recurring_event_titles: List of event titles to assign

    Returns:
        Tuple of (success, assignment_count, error_message)

    I/O Operation - Database operations.
    """
    try:
        # Get domain_id from domain_key
        domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
        if not domain:
            return False, 0, f"Domain {domain_key} not found"

        # Remove existing assignments for the specific events in this group only
        if recurring_event_titles:
            db.query(RecurringEventGroup).filter(
                RecurringEventGroup.group_id == group_id,
                RecurringEventGroup.recurring_event_title.in_(recurring_event_titles)
            ).delete(synchronize_session=False)

        # Create new assignments
        assignment_count = 0
        for title in recurring_event_titles:
            if title.strip():  # Skip empty titles
                assignment = RecurringEventGroup(
                    domain_id=domain.id,
                    domain_key=domain_key,
                    recurring_event_title=title.strip(),
                    group_id=group_id
                )
                db.add(assignment)
                assignment_count += 1

        db.commit()
        return True, assignment_count, ""

    except Exception as e:
        db.rollback()
        return False, 0, f"Database error: {str(e)}"


def create_assignment_rule(db: Session, domain_key: str, rule_type: str,
                          rule_value: str, target_group_id: int) -> Tuple[bool, Optional[AssignmentRule], str]:
    """
    Create assignment rule in database.

    Args:
        db: Database session
        domain_key: Domain identifier
        rule_type: Type of rule
        rule_value: Value to match
        target_group_id: Target group ID

    Returns:
        Tuple of (success, rule_obj, error_message)

    I/O Operation - Database creation with validation.
    """
    # Validate data using pure function
    validation_result = validate_assignment_rule_data(rule_type, rule_value, target_group_id)
    if not validation_result.is_success:
        return False, None, validation_result.error

    try:
        # Get domain_id from domain_key
        domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
        if not domain:
            return False, None, f"Domain {domain_key} not found"

        # Create rule with both domain_id and domain_key
        rule = AssignmentRule(
            domain_id=domain.id,
            domain_key=domain_key,
            rule_type=rule_type,
            rule_value=rule_value,
            target_group_id=target_group_id
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)

        return True, rule, ""

    except Exception as e:
        db.rollback()
        return False, None, f"Database error: {str(e)}"


def get_assignment_rules(db: Session, domain_key: str) -> List[AssignmentRule]:
    """
    Get assignment rules for domain.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        List of assignment rule objects
        
    I/O Operation - Database query.
    """
    return db.query(AssignmentRule).filter(AssignmentRule.domain_key == domain_key).all()


def get_recurring_event_assignments(db: Session, domain_key: str) -> List[RecurringEventGroup]:
    """
    Get recurring event group assignments for domain.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        List of recurring event group assignments
        
    I/O Operation - Database query.
    """
    return db.query(RecurringEventGroup).filter(
        RecurringEventGroup.domain_key == domain_key
    ).all()


def build_domain_events_response_data(db: Session, domain_key: str) -> Dict[str, Any]:
    """
    Build complete domain events response with auto-grouping.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        Domain events response with all events in groups (no ungrouped_events)
        
    I/O Operation - Orchestrates database queries with pure functions.
    """
    # Get events and transform for processing
    events = get_domain_events(db, domain_key)
    
    # Group events by title using pure function
    events_by_title = group_events_by_title(events)
    
    # Get groups and assignments from database
    groups = get_domain_groups(db, domain_key)
    assignments = get_recurring_event_assignments(db, domain_key)
    
    # Transform to dictionaries for pure function
    groups_data = [
        {"id": group.id, "name": group.name}
        for group in groups
    ]
    
    assignments_data = [
        {
            "group_id": assignment.group_id,
            "recurring_event_title": assignment.recurring_event_title
        }
        for assignment in assignments
    ]
    
    # Build response using new auto-grouping function
    return build_domain_events_with_auto_groups(events_by_title, groups_data, assignments_data, domain_key)


def build_domain_events_response_data_legacy(db: Session, domain_key: str) -> Dict[str, Any]:
    """
    Build domain events response with ungrouped_events array (legacy).
    
    LEGACY FUNCTION: Use build_domain_events_response_data for new implementations.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        Domain events response matching legacy OpenAPI schema
        
    I/O Operation - Orchestrates database queries with pure functions.
    """
    # Get events and transform for processing
    events = get_domain_events(db, domain_key)
    
    # Group events by title using pure function
    events_by_title = group_events_by_title(events)
    
    # Get groups and assignments from database
    groups = get_domain_groups(db, domain_key)
    assignments = get_recurring_event_assignments(db, domain_key)
    
    # Transform to dictionaries for pure function
    groups_data = [
        {"id": group.id, "name": group.name}
        for group in groups
    ]
    
    assignments_data = [
        {
            "group_id": assignment.group_id,
            "recurring_event_title": assignment.recurring_event_title
        }
        for assignment in assignments
    ]
    
    # Build response using legacy function
    return build_domain_events_response(events_by_title, groups_data, assignments_data)


async def auto_assign_events_with_rules(db: Session, domain_key: str) -> Tuple[bool, int, str]:
    """
    Auto-assign events to groups using assignment rules.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        Tuple of (success, assignment_count, error_message)
        
    I/O Operation - Orchestrates rule application with database updates.
    """
    try:
        # Get events and rules
        events = get_domain_events(db, domain_key)
        rules = get_assignment_rules(db, domain_key)
        
        if not rules:
            return True, 0, "No assignment rules defined"
        
        # Transform rules to dictionaries for pure function
        # Only include parent rules (child rules are nested within)
        parent_rules = [r for r in rules if r.parent_rule_id is None]

        rules_data = []
        for rule in parent_rules:
            if rule.is_compound:
                # Get child conditions for compound rules
                child_rules = [r for r in rules if r.parent_rule_id == rule.id]
                child_conditions = [
                    {
                        "rule_type": child.rule_type,
                        "rule_value": child.rule_value
                    }
                    for child in child_rules
                ]
                rules_data.append({
                    "is_compound": True,
                    "operator": rule.operator,
                    "child_conditions": child_conditions,
                    "target_group_id": rule.target_group_id
                })
            else:
                # Simple rule
                rules_data.append({
                    "is_compound": False,
                    "rule_type": rule.rule_type,
                    "rule_value": rule.rule_value,
                    "target_group_id": rule.target_group_id
                })
        
        # Apply rules using pure function
        group_assignments = apply_assignment_rules(events, rules_data)
        
        # Apply assignments to database
        total_assignments = 0
        for group_id, event_titles in group_assignments.items():
            success, count, error = assign_recurring_events_to_group(
                db, domain_key, group_id, event_titles
            )
            if success:
                total_assignments += count
            else:
                return False, 0, error
        
        return True, total_assignments, ""
        
    except Exception as e:
        return False, 0, f"Auto-assignment error: {str(e)}"


def get_available_recurring_events(db: Session, domain_key: str) -> List[Dict[str, Any]]:
    """
    Get all available recurring events for assignment (admin function).
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        List of recurring event data with titles and counts
        
    I/O Operation - Database query with grouping.
    """
    events = get_domain_events(db, domain_key)
    
    # Group events by title using pure function
    events_by_title = group_events_by_title(events)
    
    # Transform to admin response format
    recurring_events = []
    for title, events_data in events_by_title.items():
        if events_data.get('events'):  # Only include if there are actual events
            # Get sample event for display info
            sample_event = events_data.get('events', [{}])[0]
            
            recurring_events.append({
                "title": title,
                "event_count": events_data.get('event_count', 0),
                "sample_start_time": sample_event.get('start'),  # Use 'start' from existing format
                "sample_location": sample_event.get('location')
            })
    
    # Sort by event count (most recurring first) then by title
    return sorted(recurring_events, key=lambda x: (-x['event_count'], x['title']))


def update_group(db: Session, group_id: int, domain_key: str, name: str) -> Tuple[bool, Optional[Group], str]:
    """
    Update group name (admin function).
    
    Args:
        db: Database session
        group_id: Group ID to update
        domain_key: Domain identifier for security
        name: New group name
        
    Returns:
        Tuple of (success, group_obj, error_message)
        
    I/O Operation - Database update with validation.
    """
    # Validate data using pure function
    validation_result = validate_group_data(name, domain_key)
    if not validation_result.is_success:
        return False, None, validation_result.error
    
    try:
        # Get existing group
        group = db.query(Group).filter(
            Group.id == group_id,
            Group.domain_key == domain_key
        ).first()
        
        if not group:
            return False, None, "Group not found"
        
        # Update group
        group.name = name.strip()
        group.updated_at = func.now()
        
        db.commit()
        db.refresh(group)
        
        return True, group, ""
        
    except Exception as e:
        db.rollback()
        return False, None, f"Database error: {str(e)}"


def delete_group(db: Session, group_id: int, domain_key: str) -> Tuple[bool, str]:
    """
    Delete group and its assignments (admin function).
    
    Args:
        db: Database session
        group_id: Group ID to delete
        domain_key: Domain identifier for security
        
    Returns:
        Tuple of (success, error_message)
        
    I/O Operation - Database deletion with cascade.
    """
    try:
        # Get existing group
        group = db.query(Group).filter(
            Group.id == group_id,
            Group.domain_key == domain_key
        ).first()
        
        if not group:
            return False, "Group not found"
        
        # Delete group (cascade will delete assignments and rules)
        db.delete(group)
        db.commit()
        
        return True, ""
        
    except Exception as e:
        db.rollback()
        return False, f"Database error: {str(e)}"


def delete_assignment_rule(db: Session, rule_id: int, domain_key: str) -> Tuple[bool, str]:
    """
    Delete assignment rule (admin function).

    For compound rules, deletes both the parent rule and all child conditions.

    Args:
        db: Database session
        rule_id: Rule ID to delete
        domain_key: Domain identifier for security

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database deletion.
    """
    try:
        # Get existing rule
        rule = db.query(AssignmentRule).filter(
            AssignmentRule.id == rule_id,
            AssignmentRule.domain_key == domain_key
        ).first()

        if not rule:
            return False, "Assignment rule not found"

        # If compound rule, delete child conditions first
        if rule.is_compound:
            child_rules = db.query(AssignmentRule).filter(
                AssignmentRule.parent_rule_id == rule_id
            ).all()
            for child in child_rules:
                db.delete(child)

        # Delete parent rule
        db.delete(rule)
        db.commit()

        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Database error: {str(e)}"



def get_available_recurring_events_with_assignments(db: Session, domain_key: str) -> List[Dict[str, Any]]:
    """
    Get all available recurring events with their current group assignments (admin function).
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        List of recurring event data with assignment information
        
    I/O Operation - Database query with joins for assignment status.
    """
    events = get_domain_events(db, domain_key)
    
    # Get current assignments
    assignments = db.query(RecurringEventGroup).filter(
        RecurringEventGroup.domain_key == domain_key
    ).all()
    
    # Create mapping of event title -> list of group_ids (support multiple groups)
    assignment_map = {}
    for assignment in assignments:
        title = assignment.recurring_event_title
        if title not in assignment_map:
            assignment_map[title] = []
        assignment_map[title].append(assignment.group_id)
    
    # Group events by title using pure function
    events_by_title = group_events_by_title(events)
    
    # Transform to admin response format with assignment information
    recurring_events = []
    for title, events_data in events_by_title.items():
        if events_data.get('events'):  # Only include if there are actual events
            # Get sample event for display info
            sample_event = events_data.get('events', [{}])[0]
            
            assigned_groups = assignment_map.get(title, [])
            
            # Extract rich sample event data for rule matching
            sample_raw_ical = sample_event.get('raw_ical', '')
            sample_description = sample_event.get('description', '')
            
            # Extract categories from raw iCal using existing backend function
            from ..data.grouping import _extract_categories_from_raw_ical
            sample_categories = _extract_categories_from_raw_ical(sample_raw_ical)
            
            event_info = {
                "title": title,
                "event_count": events_data.get('event_count', 0),
                "sample_start_time": sample_event.get('start'),  # Use 'start' from existing format
                "sample_location": sample_event.get('location'),
                "sample_description": sample_description,
                "sample_raw_ical": sample_raw_ical,
                "sample_categories": sample_categories,
                "assigned_group_ids": assigned_groups,  # Multiple groups support
                # Keep backward compatibility with single assignment
                "assigned_group_id": assigned_groups[0] if assigned_groups else None
            }
            recurring_events.append(event_info)
    
    # Sort by assignment status (unassigned first) then by event count
    return sorted(recurring_events, key=lambda x: (x['assigned_group_id'] is not None, -x['event_count'], x['title']))


def bulk_unassign_recurring_events(db: Session, domain_key: str, event_titles: List[str]) -> Tuple[bool, int, str]:
    """
    Bulk unassign recurring events from their current groups (admin function).
    
    Args:
        db: Database session
        domain_key: Domain identifier
        event_titles: List of event titles to unassign
        
    Returns:
        Tuple of (success, unassigned_count, error_message)
        
    I/O Operation - Database deletion with bulk operations.
    """
    try:
        if not event_titles:
            return True, 0, "No events to unassign"
        
        # Delete existing assignments for these event titles
        deleted_count = db.query(RecurringEventGroup).filter(
            RecurringEventGroup.domain_key == domain_key,
            RecurringEventGroup.recurring_event_title.in_(event_titles)
        ).delete(synchronize_session=False)
        
        db.commit()
        
        return True, deleted_count, ""
        
    except Exception as e:
        db.rollback()
        return False, 0, f"Database error: {str(e)}"


def remove_events_from_specific_group(db: Session, domain_key: str, group_id: int, 
                                     event_titles: List[str]) -> Tuple[bool, int, str]:
    """
    Remove recurring events from a specific group while preserving assignments to other groups.
    
    Args:
        db: Database session
        domain_key: Domain identifier  
        group_id: Group ID to remove events from
        event_titles: List of event titles to remove
        
    Returns:
        Tuple of (success, removed_count, error_message)
        
    I/O Operation - Database deletion with specific group filtering.
    """
    try:
        if not event_titles:
            return True, 0, "No events to remove"
        
        # Verify group exists and belongs to domain
        group = db.query(Group).filter(
            Group.id == group_id,
            Group.domain_key == domain_key
        ).first()
        
        if not group:
            return False, 0, "Group not found or access denied"
        
        # Delete assignments only for specific events in specific group
        deleted_count = db.query(RecurringEventGroup).filter(
            RecurringEventGroup.domain_key == domain_key,
            RecurringEventGroup.group_id == group_id,
            RecurringEventGroup.recurring_event_title.in_(event_titles)
        ).delete(synchronize_session=False)
        
        db.commit()
        
        return True, deleted_count, ""
        
    except Exception as e:
        db.rollback()
        return False, 0, f"Database error: {str(e)}"