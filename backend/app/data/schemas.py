"""
Pure Data Structures - Rich Hickey Style
No methods, no behavior - just information
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass(frozen=True)  # Immutable by default
class CalendarData:
    """Pure calendar information"""
    id: str
    name: str
    url: str
    user_id: str
    created_at: str
    updated_at: str
    is_active: bool = True


@dataclass(frozen=True)
class EventData:
    """Pure event information"""
    uid: str
    summary: str
    description: str
    location: str
    dtstart: str
    dtend: str
    categories: List[str]


@dataclass(frozen=True)
class CommunityData:
    """Pure community information"""
    id: str
    name: str
    description: str
    url_path: str
    password_hash: str
    calendar_url: str
    admin_emails: List[str]
    is_active: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class GroupData:
    """Pure group information"""
    id: str
    community_id: str
    name: str
    description: str
    icon: str
    color: str
    assignment_rules: List[str]
    is_active: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class FilterData:
    """Pure filter information"""
    id: str
    name: str
    include_categories: List[str]
    exclude_categories: List[str]
    filter_mode: str
    calendar_id: str
    user_id: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class SubscriptionData:
    """Pure subscription information"""
    id: str
    user_id: str
    community_id: str
    subscribed_groups: List[str]
    explicitly_subscribed_categories: List[str]
    explicitly_unsubscribed_categories: List[str]
    filter_mode: str
    personal_token: str
    created_at: str
    updated_at: str
    last_accessed: str


@dataclass(frozen=True)
class FilteredCalendarData:
    """Pure filtered calendar information"""
    id: str
    name: str
    source_calendar_id: str
    filter_config: Dict[str, Any]
    public_token: Optional[str]
    user_id: str
    created_at: str
    updated_at: str
    last_accessed: Optional[str]
    access_count: int
    is_active: bool


# State containers - immutable collections
@dataclass(frozen=True)
class AppState:
    """Complete application state as immutable value"""
    calendars: Dict[str, CalendarData]
    communities: Dict[str, CommunityData]
    groups: Dict[str, GroupData]
    filters: Dict[str, FilterData]
    subscriptions: Dict[str, SubscriptionData]
    filtered_calendars: Dict[str, FilteredCalendarData]
    events_cache: Dict[str, List[EventData]]
    version: int = 0  # For optimistic locking


# Pure data transformation results
@dataclass(frozen=True)
class StateTransition:
    """Result of a pure state transformation"""
    new_state: AppState
    events: List[str]  # What happened (for logging/auditing)
    success: bool
    error_message: Optional[str] = None


@dataclass(frozen=True)
class QueryResult:
    """Result of a data query"""
    data: Any
    success: bool
    error_message: Optional[str] = None