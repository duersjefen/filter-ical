"""
Data Models - Immutable dataclasses (Clojure-inspired)
Pure data structures with no business logic
Enhanced for filtered calendar feature
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass(frozen=True)
class CalendarEntry:
    """Immutable calendar entry"""
    id: str
    name: str
    url: str
    user_id: str


@dataclass(frozen=True) 
class Event:
    """Immutable event data structure"""
    uid: str
    summary: str
    dtstart: str
    dtend: str
    location: Optional[str]
    description: Optional[str]
    raw: str


@dataclass(frozen=True)
class Filter:
    """Immutable filter configuration (legacy)"""
    id: str
    name: str
    calendar_id: str
    types: List[str]
    user_id: str


@dataclass(frozen=True)
class FilterConfig:
    """Enhanced immutable filter configuration for dynamic filtering"""
    id: str
    name: str
    user_id: str
    # Category filters
    include_categories: List[str]
    exclude_categories: List[str]
    # Keyword filters  
    include_keywords: List[str]
    exclude_keywords: List[str]
    # Date filters
    date_range_start: Optional[str]  # ISO format
    date_range_end: Optional[str]    # ISO format
    date_range_type: str             # 'absolute', 'relative', 'rolling'
    # Advanced filters
    location_filter: Optional[str]
    attendee_filter: Optional[str]
    organizer_filter: Optional[str]
    min_duration_minutes: Optional[int]
    max_duration_minutes: Optional[int]
    # Filter logic
    filter_mode: str                 # 'include', 'exclude'
    match_all: bool                  # AND vs OR logic for multiple criteria
    # Metadata
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class FilteredCalendar:
    """Immutable filtered calendar subscription"""
    id: str
    source_calendar_id: str          # Reference to original calendar
    filter_config_id: str            # Reference to filter configuration
    public_token: str                # URL-safe token for public access
    name: str                        # User-friendly name
    description: Optional[str]       # Optional description
    user_id: str                     # Owner
    created_at: str                  # ISO timestamp
    last_accessed: Optional[str]     # Track usage for analytics
    access_count: int                # Usage metrics
    cache_key: Optional[str]         # For cache invalidation
    cache_expires_at: Optional[str]  # Cache expiration timestamp
    is_active: bool                  # Can be disabled without deletion


@dataclass(frozen=True)
class CalendarSubscription:
    """Immutable calendar subscription tracking for auto-refresh"""
    calendar_id: str
    last_fetched: str               # ISO timestamp
    etag: Optional[str]             # HTTP ETag for change detection
    content_hash: str               # SHA256 of content for change detection
    refresh_interval_minutes: int   # How often to check for updates
    next_refresh: str               # When to next check for updates
    failure_count: int              # Track consecutive failures
    last_error: Optional[str]       # Last error message
    is_active: bool                 # Can pause refresh without deletion


@dataclass(frozen=True)
class CachedFilterResult:
    """Immutable cached filter result"""
    cache_key: str                  # Unique cache identifier
    filtered_ical_content: str      # The actual iCal content
    event_count: int                # Number of events in filtered result
    created_at: str                 # When cache was created
    expires_at: str                 # When cache expires
    filter_config_hash: str         # Hash of filter config for invalidation
    source_content_hash: str        # Hash of source calendar for invalidation


@dataclass(frozen=True)
class FilterTemplate:
    """Immutable predefined filter templates"""
    id: str
    name: str
    description: str
    category: str                   # 'work', 'personal', 'time-based', etc.
    template_config: Dict[str, Any] # Template for FilterConfig
    is_public: bool                 # Available to all users
    created_by: Optional[str]       # Creator user_id if custom template


@dataclass(frozen=True)
class AccessLog:
    """Immutable access log entry for analytics"""
    id: str
    filtered_calendar_id: str
    accessed_at: str               # ISO timestamp
    user_agent: Optional[str]      # For analytics
    ip_address: Optional[str]      # For rate limiting (hashed)
    request_path: str              # Full request path
    response_size_bytes: int       # Size of response
    cache_hit: bool                # Whether response was served from cache