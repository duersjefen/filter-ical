"""
Pure functions for event grouping and domain organization logic.

FUNCTIONAL CORE - No side effects, fully testable.
All grouping business logic without I/O operations.
"""

import yaml
from typing import Dict, List, Any, Optional, Tuple


def load_domain_config(config_content: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Parse domain configuration from YAML content.
    
    Args:
        config_content: Raw YAML configuration string
        
    Returns:
        Tuple of (success, config_dict, error_message)
        
    Pure function - deterministic parsing.
    """
    try:
        config = yaml.safe_load(config_content)
        if not config or 'domains' not in config:
            return False, {}, "Invalid domain configuration: missing 'domains' key"
        
        return True, config, ""
    except yaml.YAMLError as e:
        return False, {}, f"Failed to parse domain configuration: {str(e)}"


def get_domain_config(domain_key: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get configuration for specific domain.
    
    Args:
        domain_key: Domain identifier
        config: Loaded domain configuration
        
    Returns:
        Domain configuration or None if not found
        
    Pure function - simple data lookup.
    """
    domains = config.get('domains', {})
    domain_config = domains.get(domain_key)
    
    if domain_config:
        # Add domain key to config for convenience
        domain_config = {**domain_config, 'id': domain_key}
    
    return domain_config




def create_group_data(domain_key: str, name: str) -> Dict[str, Any]:
    """
    Create group data structure.
    
    Args:
        domain_key: Domain identifier
        name: Group name
        
    Returns:
        Group data dictionary
        
    Pure function - creates new data structure.
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    
    return {
        "domain_key": domain_key,
        "name": name.strip(),
        "created_at": now,
        "updated_at": now
    }


def create_recurring_event_group_data(domain_key: str, recurring_event_title: str, 
                                    group_id: int) -> Dict[str, Any]:
    """
    Create recurring event group assignment data.
    
    Args:
        domain_key: Domain identifier
        recurring_event_title: Title of recurring event
        group_id: ID of target group
        
    Returns:
        Recurring event group data dictionary
        
    Pure function - creates new data structure.
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    
    return {
        "domain_key": domain_key,
        "recurring_event_title": recurring_event_title.strip(),
        "group_id": group_id,
        "created_at": now
    }


def create_assignment_rule_data(domain_key: str, rule_type: str, rule_value: str, 
                               target_group_id: int) -> Dict[str, Any]:
    """
    Create assignment rule data structure.
    
    Args:
        domain_key: Domain identifier
        rule_type: Type of rule (title_contains, description_contains)
        rule_value: Value to match against
        target_group_id: ID of target group
        
    Returns:
        Assignment rule data dictionary
        
    Pure function - creates new data structure.
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    
    return {
        "domain_key": domain_key,
        "rule_type": rule_type,
        "rule_value": rule_value.strip(),
        "target_group_id": target_group_id,
        "created_at": now,
        "updated_at": now
    }


def apply_assignment_rules(events: List[Dict[str, Any]], 
                          assignment_rules: List[Dict[str, Any]]) -> Dict[int, List[str]]:
    """
    Apply assignment rules to events and return group assignments.
    
    Args:
        events: List of events to process
        assignment_rules: List of assignment rule data
        
    Returns:
        Dictionary mapping group_id -> list of event titles to assign
        
    Pure function - rule application logic.
    """
    group_assignments = {}
    
    # Group events by title to find recurring events
    events_by_title = {}
    for event in events:
        title = event.get('title', '')
        if title not in events_by_title:
            events_by_title[title] = []
        events_by_title[title].append(event)
    
    # Apply rules to each unique event title
    for title, title_events in events_by_title.items():
        # Use first event as representative for rule matching
        representative_event = title_events[0]
        
        for rule in assignment_rules:
            if _event_matches_rule(representative_event, rule):
                group_id = rule['target_group_id']
                if group_id not in group_assignments:
                    group_assignments[group_id] = []
                group_assignments[group_id].append(title)
                break  # First matching rule wins
    
    return group_assignments


def _event_matches_rule(event: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """
    Check if event matches assignment rule.
    
    Args:
        event: Event data
        rule: Assignment rule data
        
    Returns:
        True if event matches rule
        
    Pure function - rule matching logic.
    """
    rule_type = rule.get('rule_type', '')
    rule_value = rule.get('rule_value', '').lower()
    
    if rule_type == 'title_contains':
        title = event.get('title', '').lower()
        return rule_value in title
    
    elif rule_type == 'description_contains':
        description = event.get('description', '').lower()
        return rule_value in description
    
    
    return False


def build_domain_events_response(grouped_events: Dict[str, List[Dict[str, Any]]], 
                                groups_data: List[Dict[str, Any]],
                                recurring_assignments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build domain events response matching OpenAPI specification.
    
    Args:
        grouped_events: Events grouped by title
        groups_data: List of group data from database
        recurring_assignments: List of recurring event group assignments
        
    Returns:
        Domain events response matching OpenAPI schema
        
    Pure function - data structure transformation.
    """
    # Create mapping of group_id -> group_name
    groups_map = {group['id']: group for group in groups_data}
    
    # Create mapping of group_id -> assigned recurring event titles
    group_recurring_titles = {}
    for assignment in recurring_assignments:
        group_id = assignment['group_id']
        title = assignment['recurring_event_title']
        
        if group_id not in group_recurring_titles:
            group_recurring_titles[group_id] = []
        group_recurring_titles[group_id].append(title)
    
    # Build groups with their recurring events
    groups_with_events = []
    ungrouped_events = []
    
    for group_id, group_data in groups_map.items():
        assigned_titles = group_recurring_titles.get(group_id, [])
        
        # Find events for assigned titles
        group_recurring_events = []
        for title in assigned_titles:
            if title in grouped_events:
                events_for_title = grouped_events[title]
                
                recurring_event = {
                    "title": title,
                    "event_count": len(events_for_title),
                    "events": events_for_title
                }
                group_recurring_events.append(recurring_event)
                
                # Remove from grouped_events so they don't appear as ungrouped
                del grouped_events[title]
        
        if group_recurring_events:  # Only include groups that have events
            groups_with_events.append({
                "id": group_id,
                "name": group_data['name'],
                "recurring_events": group_recurring_events
            })
    
    # Remaining events are ungrouped
    for title, events in grouped_events.items():
        recurring_event = {
            "title": title,
            "event_count": len(events),
            "events": events
        }
        ungrouped_events.append(recurring_event)
    
    return {
        "groups": groups_with_events,
        "ungrouped_events": ungrouped_events
    }


def validate_group_data(name: str, domain_key: str) -> Tuple[bool, str]:
    """
    Validate group creation data.
    
    Args:
        name: Group name
        domain_key: Domain identifier
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Pure function - validation without side effects.
    """
    if not name or not isinstance(name, str) or not name.strip():
        return False, "Group name is required"
    
    if len(name.strip()) > 255:
        return False, "Group name must be 255 characters or less"
    
    if not domain_key or not isinstance(domain_key, str) or not domain_key.strip():
        return False, "Domain key is required"
    
    return True, ""


def validate_assignment_rule_data(rule_type: str, rule_value: str, 
                                 target_group_id: int) -> Tuple[bool, str]:
    """
    Validate assignment rule creation data.
    
    Args:
        rule_type: Type of rule
        rule_value: Value to match
        target_group_id: Target group ID
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Pure function - validation without side effects.
    """
    valid_rule_types = ['title_contains', 'description_contains']
    
    if rule_type not in valid_rule_types:
        return False, f"Rule type must be one of: {', '.join(valid_rule_types)}"
    
    if not rule_value or not isinstance(rule_value, str) or not rule_value.strip():
        return False, "Rule value is required"
    
    if not isinstance(target_group_id, int) or target_group_id <= 0:
        return False, "Target group ID must be a positive integer"
    
    return True, ""