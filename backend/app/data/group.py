"""
Group Data Functions (Functional Core)
Pure functions for group data transformations and tree building.
No I/O operations, just data transformations following functional architecture.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime


def build_group_tree(groups: List[Any], events_by_group: Dict[str, List[Any]]) -> Dict[str, Any]:
    """
    Build nested group tree structure from flat list of groups.
    Pure function - transforms flat data into hierarchical structure.
    
    Args:
        groups: List of group objects from database
        events_by_group: Dictionary mapping group_id to list of events
        
    Returns:
        Dict with root groups containing nested children and events
    """
    # Create lookup dict for quick access
    groups_dict = {group.id: group for group in groups}
    
    # Separate root groups from child groups
    root_groups = {}
    child_groups_by_parent = {}
    
    for group in groups:
        if group.parent_group_id is None:
            # Root group
            root_groups[group.id] = _build_group_data(group, events_by_group.get(group.id, []))
        else:
            # Child group
            if group.parent_group_id not in child_groups_by_parent:
                child_groups_by_parent[group.parent_group_id] = []
            child_groups_by_parent[group.parent_group_id].append(group)
    
    # Recursively add children to root groups
    for group_id, group_data in root_groups.items():
        group_data['children'] = _build_children_recursive(
            group_id, 
            child_groups_by_parent, 
            events_by_group
        )
    
    return root_groups


def _build_group_data(group: Any, events: List[Any]) -> Dict[str, Any]:
    """
    Build group data dictionary from group object and events.
    Pure function - transforms group object to API response format.
    
    Args:
        group: Group database object
        events: List of events for this group
        
    Returns:
        Dict matching OpenAPI Group schema
    """
    return {
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'color': group.color,
        'parent_group_id': group.parent_group_id,
        'created_at': group.created_at.isoformat() if isinstance(group.created_at, datetime) else group.created_at,
        'children': [],  # Will be populated by recursive function
        'events': [_transform_event_for_group_response(event) for event in events]
    }


def _build_children_recursive(
    parent_group_id: str, 
    child_groups_by_parent: Dict[str, List[Any]], 
    events_by_group: Dict[str, List[Any]]
) -> List[Dict[str, Any]]:
    """
    Recursively build children for a parent group.
    Pure function - handles unlimited nesting depth.
    
    Args:
        parent_group_id: ID of the parent group
        child_groups_by_parent: Dict mapping parent_id to list of child groups
        events_by_group: Dict mapping group_id to list of events
        
    Returns:
        List of child group dictionaries with their own children
    """
    if parent_group_id not in child_groups_by_parent:
        return []
    
    children = []
    for child_group in child_groups_by_parent[parent_group_id]:
        child_data = _build_group_data(
            child_group, 
            events_by_group.get(child_group.id, [])
        )
        
        # Recursively add grandchildren
        child_data['children'] = _build_children_recursive(
            child_group.id,
            child_groups_by_parent,
            events_by_group
        )
        
        children.append(child_data)
    
    return children


def _transform_event_for_group_response(event: Any) -> Dict[str, Any]:
    """
    Transform event object to API response format.
    Pure function - converts database event to OpenAPI Event schema.
    
    Args:
        event: Event database object
        
    Returns:
        Dict matching OpenAPI Event schema
    """
    return {
        'id': event.id,
        'title': event.title,
        'start': event.start.isoformat() if isinstance(event.start, datetime) else event.start,
        'end': event.end.isoformat() if isinstance(event.end, datetime) else event.end,
        'event_type': event.category,  # Maps to category field in database
        'description': event.description,
        'location': event.location
    }


def get_event_types_for_group(group_id: str, event_type_groups: List[Any]) -> List[str]:
    """
    Get all event types assigned to a specific group.
    Pure function - filters event type assignments by group.
    
    Args:
        group_id: ID of the group
        event_type_groups: List of EventTypeGroup association objects
        
    Returns:
        List of event type strings for this group
    """
    return [
        etg.event_type 
        for etg in event_type_groups 
        if etg.group_id == group_id
    ]


def collect_all_descendant_group_ids(group_id: str, groups: List[Any]) -> List[str]:
    """
    Collect all descendant group IDs for a given group (recursive).
    Pure function - traverses tree to find all nested children.
    
    Args:
        group_id: ID of the parent group
        groups: List of all group objects
        
    Returns:
        List of all descendant group IDs (including the original group_id)
    """
    descendant_ids = [group_id]
    
    # Find direct children
    direct_children = [g.id for g in groups if g.parent_group_id == group_id]
    
    # Recursively collect grandchildren
    for child_id in direct_children:
        descendant_ids.extend(collect_all_descendant_group_ids(child_id, groups))
    
    return descendant_ids


def validate_group_hierarchy(groups: List[Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that group hierarchy has no circular references.
    Pure function - checks for cycles in parent-child relationships.
    
    Args:
        groups: List of all group objects
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Build parent-child mapping
    children_by_parent = {}
    for group in groups:
        if group.parent_group_id:
            if group.parent_group_id not in children_by_parent:
                children_by_parent[group.parent_group_id] = []
            children_by_parent[group.parent_group_id].append(group.id)
    
    # Check each group for circular references
    for group in groups:
        if _has_circular_reference(group.id, children_by_parent, set()):
            return False, f"Circular reference detected in group hierarchy starting from {group.id}"
    
    return True, None


def _has_circular_reference(group_id: str, children_by_parent: Dict[str, List[str]], visited: set) -> bool:
    """
    Check if a group has circular references in its descendant tree.
    Pure function - detects cycles using depth-first traversal.
    
    Args:
        group_id: Current group being checked
        children_by_parent: Dict mapping parent_id to list of child_ids
        visited: Set of group_ids already visited in current path
        
    Returns:
        True if circular reference found, False otherwise
    """
    if group_id in visited:
        return True
    
    visited.add(group_id)
    
    # Check all children
    for child_id in children_by_parent.get(group_id, []):
        if _has_circular_reference(child_id, children_by_parent, visited.copy()):
            return True
    
    return False