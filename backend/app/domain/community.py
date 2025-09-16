"""
Community Domain Logic - Pure Functions Only
Rich Hickey: "Functions that take values and return values"
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import uuid

from ..data.schemas import (
    AppState, StateTransition, CommunityData, GroupData, 
    SubscriptionData, QueryResult
)


def create_community(
    state: AppState,
    name: str,
    description: str,
    url_path: str,
    password_hash: str,
    calendar_url: str,
    admin_emails: List[str]
) -> StateTransition:
    """
    Pure function: Create new community in state
    Returns new state with community added
    """
    community_id = url_path.lstrip('/')  # Use path as ID
    now = datetime.utcnow().isoformat()
    
    # Check if community already exists
    if community_id in state.communities:
        return StateTransition(
            new_state=state,
            events=[],
            success=False,
            error_message=f"Community {community_id} already exists"
        )
    
    # Create new community data
    new_community = CommunityData(
        id=community_id,
        name=name,
        description=description,
        url_path=url_path,
        password_hash=password_hash,
        calendar_url=calendar_url,
        admin_emails=admin_emails,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    
    # Return new state with community added
    new_communities = {**state.communities, community_id: new_community}
    new_state = AppState(
        calendars=state.calendars,
        communities=new_communities,
        groups=state.groups,
        filters=state.filters,
        subscriptions=state.subscriptions,
        events_cache=state.events_cache,
        version=state.version + 1
    )
    
    return StateTransition(
        new_state=new_state,
        events=[f"community_created:{community_id}"],
        success=True
    )


def update_community_calendar_url(
    state: AppState,
    community_id: str,
    new_calendar_url: str
) -> StateTransition:
    """
    Pure function: Update community calendar URL
    Returns new state with updated community
    """
    # Check if community exists
    if community_id not in state.communities:
        return StateTransition(
            new_state=state,
            events=[],
            success=False,
            error_message=f"Community {community_id} not found"
        )
    
    # Get existing community
    existing_community = state.communities[community_id]
    
    # Create updated community (immutable)
    updated_community = CommunityData(
        id=existing_community.id,
        name=existing_community.name,
        description=existing_community.description,
        url_path=existing_community.url_path,
        password_hash=existing_community.password_hash,
        calendar_url=new_calendar_url,  # Only this changes
        admin_emails=existing_community.admin_emails,
        is_active=existing_community.is_active,
        created_at=existing_community.created_at,
        updated_at=datetime.utcnow().isoformat()
    )
    
    # Return new state with updated community
    new_communities = {**state.communities, community_id: updated_community}
    new_state = AppState(
        calendars=state.calendars,
        communities=new_communities,
        groups=state.groups,
        filters=state.filters,
        subscriptions=state.subscriptions,
        events_cache=state.events_cache,
        version=state.version + 1
    )
    
    return StateTransition(
        new_state=new_state,
        events=[f"community_calendar_updated:{community_id}"],
        success=True
    )


def find_community_by_path(state: AppState, url_path: str) -> QueryResult:
    """
    Pure function: Find community by URL path
    Returns query result with community data
    """
    for community in state.communities.values():
        if community.url_path == url_path:
            return QueryResult(
                data=community,
                success=True
            )
    
    return QueryResult(
        data=None,
        success=False,
        error_message=f"Community with path {url_path} not found"
    )


def get_community_groups(state: AppState, community_id: str) -> QueryResult:
    """
    Pure function: Get all active groups for a community
    Returns query result with group list
    """
    if community_id not in state.communities:
        return QueryResult(
            data=[],
            success=False,
            error_message=f"Community {community_id} not found"
        )
    
    community_groups = [
        group for group in state.groups.values()
        if group.community_id == community_id and group.is_active
    ]
    
    return QueryResult(
        data=community_groups,
        success=True
    )


def validate_community_data(
    name: str,
    description: str,
    url_path: str,
    calendar_url: str
) -> Tuple[bool, str]:
    """
    Pure function: Validate community data
    Returns (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Community name is required"
    
    if not url_path or not url_path.startswith('/'):
        return False, "URL path must start with /"
    
    if not calendar_url or not calendar_url.startswith('http'):
        return False, "Calendar URL must be a valid HTTP URL"
    
    return True, ""


def add_default_groups_to_community(
    state: AppState,
    community_id: str,
    default_groups: List[Dict]
) -> StateTransition:
    """
    Pure function: Add default groups to community
    Returns new state with groups added
    """
    if community_id not in state.communities:
        return StateTransition(
            new_state=state,
            events=[],
            success=False,
            error_message=f"Community {community_id} not found"
        )
    
    new_groups = dict(state.groups)
    events = []
    
    for group_data in default_groups:
        group = GroupData(
            id=group_data["id"],
            community_id=community_id,
            name=group_data["name"],
            description=group_data["description"],
            icon=group_data["icon"],
            color=group_data["color"],
            assignment_rules=group_data["assignment_rules"],
            is_active=group_data["is_active"],
            created_at=group_data["created_at"],
            updated_at=group_data["updated_at"]
        )
        new_groups[group.id] = group
        events.append(f"group_created:{group.id}")
    
    new_state = AppState(
        calendars=state.calendars,
        communities=state.communities,
        groups=new_groups,
        filters=state.filters,
        subscriptions=state.subscriptions,
        events_cache=state.events_cache,
        version=state.version + 1
    )
    
    return StateTransition(
        new_state=new_state,
        events=events,
        success=True
    )