"""
Pure functions for event grouping and domain organization logic.

FUNCTIONAL CORE - No side effects, fully testable.
All grouping business logic without I/O operations.
"""

import yaml
from typing import Dict, List, Any, Optional, Tuple
from app.core.result import Result, ok, fail


def load_domain_config(config_content: str) -> Result[Dict[str, Any]]:
    """
    Parse domain configuration from YAML content.

    Args:
        config_content: Raw YAML configuration string

    Returns:
        Result containing config dict or error message

    Pure function - deterministic parsing.
    """
    try:
        config = yaml.safe_load(config_content)
        if not config or 'domains' not in config:
            return fail("Invalid domain configuration: missing 'domains' key")

        return ok(config)
    except yaml.YAMLError as e:
        return fail(f"Failed to parse domain configuration: {str(e)}")


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

    Algorithm:
    ----------
    Processes unique event titles (grouped by recurring events) and applies
    assignment rules to determine which group each event belongs to.

    Rule Matching Process:
    1. Group events by title to identify recurring events
    2. For each unique title, use first event as representative
    3. Test assignment rules in order until one matches
    4. First matching rule wins - subsequent rules ignored

    Precedence:
    -----------
    Rules are evaluated in the order they appear in assignment_rules list.
    This allows admins to create priority-based grouping:
    - More specific rules should come first (e.g., "title_contains: Exam")
    - More general rules should come last (e.g., "title_contains: Class")

    Why This Approach:
    ------------------
    - First-match prevents ambiguous multi-group assignments
    - Rule ordering gives admins explicit control over precedence
    - Using representative event is efficient (no need to check all instances)
    - Supports multiple rule types (title_contains, description_contains, category_contains)

    Example:
    --------
    >>> events = [
    ...     {"title": "Math Exam", "description": "Final exam"},
    ...     {"title": "Math Class", "description": "Regular class"}
    ... ]
    >>> rules = [
    ...     {"rule_type": "title_contains", "rule_value": "exam", "target_group_id": 1},
    ...     {"rule_type": "title_contains", "rule_value": "math", "target_group_id": 2}
    ... ]
    >>> result = apply_assignment_rules(events, rules)
    >>> # Result: {1: ["Math Exam"], 2: ["Math Class"]}
    >>> # "Math Exam" matches first rule (1), so second rule (2) not applied

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


def _extract_categories_from_raw_ical(raw_ical: str) -> List[str]:
    """
    Extract CATEGORY values from raw iCal content.
    
    Args:
        raw_ical: Raw iCal event content
        
    Returns:
        List of category values found in the iCal content
        
    Pure function - deterministic text parsing.
    """
    categories = []
    if not raw_ical:
        return categories
    
    for line in raw_ical.split('\n'):
        line = line.strip()
        # Case-insensitive matching for CATEGORY/CATEGORIES lines
        if line.upper().startswith('CATEGORY:') or line.upper().startswith('CATEGORIES:'):
            # Find the colon and extract everything after it
            colon_index = line.find(':')
            if colon_index != -1:
                category = line[colon_index + 1:].strip()
                if category:
                    categories.append(category)
    
    return categories


def _event_matches_rule(event: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """
    Check if event matches assignment rule (supports compound rules).

    Compound rules can combine multiple conditions using AND/OR operators:
    - AND: All child conditions must match
    - OR: At least one child condition must match

    Args:
        event: Event data
        rule: Assignment rule data (single condition or compound)

    Returns:
        True if event matches rule

    Pure function - rule matching logic.
    """
    # Compound rule (has child conditions)
    if rule.get('is_compound'):
        child_conditions = rule.get('child_conditions', [])
        operator = rule.get('operator', 'AND')

        if operator == 'AND':
            # All conditions must match (empty list returns True - all zero conditions match)
            return all(_event_matches_single_condition(event, cond) for cond in child_conditions)
        elif operator == 'OR':
            # At least one condition must match (empty list returns False - no conditions to match)
            return any(_event_matches_single_condition(event, cond) for cond in child_conditions)

    # Single condition (backward compatible)
    return _event_matches_single_condition(event, rule)


def _event_matches_single_condition(event: Dict[str, Any], condition: Dict[str, Any]) -> bool:
    """
    Check if event matches a single condition.

    Supports both positive (contains) and negative (not_contains) matching.
    Negative rules return True when the value is NOT found in the field.

    Args:
        event: Event data
        condition: Single condition data

    Returns:
        True if event matches condition

    Pure function - single condition matching logic.
    """
    rule_type = condition.get('rule_type', '')
    rule_value = condition.get('rule_value', '').lower()

    # Positive matching - title contains
    if rule_type == 'title_contains':
        title = event.get('title', '').lower()
        return rule_value in title

    # Negative matching - title does NOT contain
    elif rule_type == 'title_not_contains':
        title = event.get('title', '').lower()
        return rule_value not in title

    # Positive matching - description contains
    elif rule_type == 'description_contains':
        description = event.get('description', '').lower()
        return rule_value in description

    # Negative matching - description does NOT contain
    elif rule_type == 'description_not_contains':
        description = event.get('description', '').lower()
        return rule_value not in description

    # Positive matching - category contains
    elif rule_type == 'category_contains':
        categories = _extract_categories_from_raw_ical(event.get('raw_ical', ''))
        return any(rule_value in cat.lower() for cat in categories)

    # Negative matching - category does NOT contain
    elif rule_type == 'category_not_contains':
        categories = _extract_categories_from_raw_ical(event.get('raw_ical', ''))
        # Returns True if NO categories contain the rule_value
        return not any(rule_value in cat.lower() for cat in categories)

    return False


def create_auto_group_data(domain_key: str, group_type: str) -> Dict[str, Any]:
    """
    Create auto-group data structure for ungrouped events.
    
    Args:
        domain_key: Domain identifier
        group_type: Type of auto-group ('recurring' or 'unique')
        
    Returns:
        Auto-group data dictionary
        
    Pure function - creates new data structure.
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    
    group_names = {
        'recurring': '📅 Other Recurring Events',
        'unique': '🎯 Special Events'
    }
    
    return {
        "domain_key": domain_key,
        "name": group_names.get(group_type, f"Auto-{group_type.title()} Events"),
        "created_at": now,
        "updated_at": now,
        "auto_group_type": group_type,  # Mark as auto-created
        "auto_group_id": f"{domain_key}_auto_{group_type}"  # Unique identifier
    }


def assign_ungrouped_to_auto_groups(ungrouped_events: List[Dict[str, Any]],
                                  domain_key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Create auto-groups and assign ungrouped events to them.

    Algorithm:
    ----------
    Categorizes events that don't match any custom group into two auto-created groups:
    1. "📅 Other Recurring Events" (event_count > 1) - ID: 9998
    2. "🎯 Special Events" (event_count == 1) - ID: 9999

    Why These Groups:
    -----------------
    - Ensures ALL events appear in some group (no orphaned events)
    - High numeric IDs (9998, 9999) ensure auto-groups appear last in UI
    - Recurring vs unique distinction helps users understand event patterns
    - Auto-groups are visually distinct with emojis and special naming

    Why This Approach:
    ------------------
    - Prevents UX confusion from "ungrouped" events section
    - Maintains consistent group-based navigation pattern
    - Makes it obvious which events need manual grouping
    - Preserves filtering contract (all events must be in a group)

    Edge Cases:
    -----------
    - Empty ungrouped_events: Returns auto-groups with empty recurring_events lists
    - All events recurring: unique_auto_group will have empty list
    - All events unique: recurring_auto_group will have empty list

    Example:
    --------
    >>> ungrouped = [
    ...     {"title": "Weekly Meeting", "event_count": 5},
    ...     {"title": "One-time Conference", "event_count": 1}
    ... ]
    >>> recurring_group, unique_group = assign_ungrouped_to_auto_groups(ungrouped, "school")
    >>> # recurring_group['id'] == 9998, contains "Weekly Meeting"
    >>> # unique_group['id'] == 9999, contains "One-time Conference"

    Args:
        ungrouped_events: List of ungrouped event data
        domain_key: Domain identifier

    Returns:
        Tuple of (recurring_auto_group, unique_auto_group) with events assigned

    Pure function - data categorization logic.
    """
    # Create auto-groups
    recurring_group = create_auto_group_data(domain_key, 'recurring')
    unique_group = create_auto_group_data(domain_key, 'unique')
    
    # Assign high numeric IDs for auto-groups to ensure they appear last
    recurring_group['id'] = 9998  # Auto-recurring (second-to-last)
    unique_group['id'] = 9999     # Auto-unique (last)
    
    # Categorize events
    recurring_events = []
    unique_events = []
    
    for event_data in ungrouped_events:
        event_count = event_data.get('event_count', 0)
        if event_count > 1:
            recurring_events.append(event_data)
        else:
            unique_events.append(event_data)
    
    # Add events to groups
    recurring_group['recurring_events'] = recurring_events
    unique_group['recurring_events'] = unique_events
    
    return recurring_group, unique_group


def build_domain_events_with_auto_groups(grouped_events: Dict[str, List[Dict[str, Any]]], 
                                        groups_data: List[Dict[str, Any]],
                                        recurring_assignments: List[Dict[str, Any]],
                                        domain_key: str) -> Dict[str, Any]:
    """
    Build domain events response with auto-grouping for ungrouped events.
    
    Args:
        grouped_events: Events grouped by title
        groups_data: List of group data from database
        recurring_assignments: List of recurring event group assignments
        domain_key: Domain identifier for auto-group creation
        
    Returns:
        Domain events response with all events in groups (no ungrouped_events)
        
    Pure function - data structure transformation with auto-grouping.
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
    
    # Track which events have been assigned to groups (for auto-grouping)
    assigned_titles = set()
    
    # Build groups with their recurring events
    groups_with_events = []
    
    for group_id, group_data in groups_map.items():
        assigned_titles_for_group = group_recurring_titles.get(group_id, [])
        
        # Find events for assigned titles
        group_recurring_events = []
        for title in assigned_titles_for_group:
            if title in grouped_events:
                # grouped_events[title] already has correct structure: {title, event_count, events}
                events_for_title = grouped_events[title]
                group_recurring_events.append(events_for_title)
                
                # Track that this title has been assigned to at least one group
                assigned_titles.add(title)
        
        # Only include groups that have events with actual event data
        if group_recurring_events and any(event_data.get('events') for event_data in group_recurring_events):
            groups_with_events.append({
                "id": group_id,
                "name": group_data['name'],
                "recurring_events": group_recurring_events
            })
    
    # Handle ungrouped events (events not assigned to any group) with auto-grouping
    ungrouped_events = []
    for title, events_data in grouped_events.items():
        # Only include events that haven't been assigned to any group
        if title not in assigned_titles and events_data.get('events'):
            ungrouped_events.append(events_data)
    
    # Create auto-groups for ungrouped events
    if ungrouped_events:
        recurring_auto_group, unique_auto_group = assign_ungrouped_to_auto_groups(ungrouped_events, domain_key)
        
        # Add auto-groups to response (only if they have events)
        if recurring_auto_group['recurring_events']:
            groups_with_events.append(recurring_auto_group)
        
        if unique_auto_group['recurring_events']:
            groups_with_events.append(unique_auto_group)
    
    # Return response with all events in groups (no ungrouped_events array)
    return {
        "groups": groups_with_events
    }


def build_domain_events_response(grouped_events: Dict[str, List[Dict[str, Any]]], 
                                groups_data: List[Dict[str, Any]],
                                recurring_assignments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build domain events response matching OpenAPI specification.
    
    LEGACY FUNCTION: Use build_domain_events_with_auto_groups for new implementations.
    
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
    
    # Track which events have been assigned to groups (for ungrouped events)
    assigned_titles = set()
    
    # Build groups with their recurring events
    groups_with_events = []
    
    for group_id, group_data in groups_map.items():
        assigned_titles_for_group = group_recurring_titles.get(group_id, [])
        
        # Find events for assigned titles
        group_recurring_events = []
        for title in assigned_titles_for_group:
            if title in grouped_events:
                # grouped_events[title] already has correct structure: {title, event_count, events}
                events_for_title = grouped_events[title]
                group_recurring_events.append(events_for_title)
                
                # Track that this title has been assigned to at least one group
                assigned_titles.add(title)
        
        # Only include groups that have events with actual event data
        if group_recurring_events and any(event_data.get('events') for event_data in group_recurring_events):
            groups_with_events.append({
                "id": group_id,
                "name": group_data['name'],
                "recurring_events": group_recurring_events
            })
    
    # Remaining events are ungrouped (events not assigned to any group)
    ungrouped_events = []
    for title, events_data in grouped_events.items():
        # Only include events that haven't been assigned to any group
        if title not in assigned_titles and events_data.get('events'):
            ungrouped_events.append(events_data)
    
    return {
        "groups": groups_with_events,
        "ungrouped_events": ungrouped_events
    }


def validate_group_data(name: str, domain_key: str) -> Result[None]:
    """
    Validate group creation data.

    Args:
        name: Group name
        domain_key: Domain identifier

    Returns:
        Result indicating success or validation error

    Pure function - validation without side effects.
    """
    if not name or not isinstance(name, str) or not name.strip():
        return fail("Group name is required")

    if len(name.strip()) > 255:
        return fail("Group name must be 255 characters or less")

    if not domain_key or not isinstance(domain_key, str) or not domain_key.strip():
        return fail("Domain key is required")

    return ok(None)


def validate_assignment_rule_data(rule_type: str, rule_value: str,
                                 target_group_id: int) -> Result[None]:
    """
    Validate assignment rule creation data.

    Supports both positive (contains) and negative (not_contains) rule types.

    Args:
        rule_type: Type of rule
        rule_value: Value to match
        target_group_id: Target group ID

    Returns:
        Result indicating success or validation error

    Pure function - validation without side effects.
    """
    valid_rule_types = [
        'title_contains', 'title_not_contains',
        'description_contains', 'description_not_contains',
        'category_contains', 'category_not_contains'
    ]

    if rule_type not in valid_rule_types:
        return fail(f"Rule type must be one of: {', '.join(valid_rule_types)}")

    if not rule_value or not isinstance(rule_value, str) or not rule_value.strip():
        return fail("Rule value is required")

    if not isinstance(target_group_id, int) or target_group_id <= 0:
        return fail("Target group ID must be a positive integer")

    return ok(None)