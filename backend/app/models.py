"""
SQLModel database models matching the OpenAPI specification exactly
Ensures contract compliance through type-safe database operations
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class FilterMode(str, Enum):
    include = "include"
    exclude = "exclude"



# Core Calendar Model
class Calendar(SQLModel, table=True):
    """Calendar model matching OpenAPI Calendar schema"""
    __tablename__ = "calendars"
    
    id: str = Field(primary_key=True)  # ID will be set explicitly using generate_calendar_id()
    name: str = Field(min_length=3, max_length=100)
    url: str = Field()
    user_id: str = Field(index=True)
    domain_id: Optional[str] = Field(default=None, index=True)  # e.g., "exter"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Caching fields for external calendar data
    cached_ical_content: Optional[str] = Field(default=None)  # Raw iCal content
    cached_content_hash: Optional[str] = Field(default=None)  # Hash for change detection  
    cache_updated_at: Optional[datetime] = Field(default=None, index=True)  # Cache timestamp
    cache_expires_at: Optional[datetime] = Field(default=None, index=True)  # Cache expiry
    
    # Relationships
    events: List["Event"] = Relationship(back_populates="calendar")
    filtered_calendars: List["FilteredCalendar"] = Relationship(back_populates="source_calendar")


class Event(SQLModel, table=True):
    """Event model matching OpenAPI Event schema"""
    __tablename__ = "events"
    
    id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}", primary_key=True)
    calendar_id: str = Field(foreign_key="calendars.id", index=True)
    title: str = Field()
    start: datetime = Field()
    end: datetime = Field()
    category: str = Field(index=True)  # Indexed for fast filtering
    description: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    
    # Raw iCal data for regeneration if needed
    raw_ical: Optional[str] = Field(default=None)
    
    # Relationship
    calendar: Optional[Calendar] = Relationship(back_populates="events")


class Group(SQLModel, table=True):
    """Group model for organizing events within a domain"""
    __tablename__ = "groups"
    
    id: str = Field(default_factory=lambda: f"grp_{uuid.uuid4().hex[:8]}", primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    domain_id: Optional[str] = Field(default=None, index=True)  # e.g., "exter"
    description: Optional[str] = Field(default=None)
    color: str = Field(default="#3B82F6")  # UI color
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Nested group support
    parent_group_id: Optional[str] = Field(default=None, foreign_key="groups.id", index=True)
    
    # Relationships
    event_type_groups: List["EventTypeGroup"] = Relationship(back_populates="group")
    
    # Self-referential relationships for nested structure
    parent_group: Optional["Group"] = Relationship(
        back_populates="child_groups",
        sa_relationship_kwargs={"remote_side": "Group.id"}
    )
    child_groups: List["Group"] = Relationship(back_populates="parent_group")


class EventTypeGroup(SQLModel, table=True):
    """Association table linking event types to groups"""
    __tablename__ = "event_type_groups"
    
    id: str = Field(default_factory=lambda: f"etg_{uuid.uuid4().hex[:8]}", primary_key=True)
    event_type: str = Field(index=True)  # e.g., "Volleyball", "Youngsterband"
    group_id: str = Field(foreign_key="groups.id", index=True)
    domain_id: str = Field(index=True)  # e.g., "exter" - to scope event types by domain
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships  
    group: Optional["Group"] = Relationship(back_populates="event_type_groups")


class FilteredCalendar(SQLModel, table=True):
    """Filtered Calendar model matching OpenAPI FilteredCalendar schema"""
    __tablename__ = "filtered_calendars"
    
    id: str = Field(default_factory=lambda: f"fc_{uuid.uuid4().hex[:8]}", primary_key=True)
    name: str = Field(min_length=3, max_length=100)
    public_token: str = Field(default_factory=lambda: uuid.uuid4().hex[:12], unique=True, index=True)
    source_calendar_id: str = Field(foreign_key="calendars.id")
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Auto-regeneration tracking
    needs_regeneration: bool = Field(default=False, index=True)  # Flag when source calendar changes
    
    # Filter configuration stored as JSON
    include_events: str = Field(default="[]")  # JSON array of strings
    exclude_events: str = Field(default="[]")  # JSON array of strings  
    filter_mode: FilterMode = Field(default=FilterMode.include)
    
    # Relationship
    source_calendar: Optional[Calendar] = Relationship(back_populates="filtered_calendars")
    
    @property
    def calendar_url(self) -> str:
        return f"https://filter-ical.de/cal/{self.public_token}"
    
    @property 
    def preview_url(self) -> str:
        return f"https://filter-ical.de/preview/{self.public_token}"


# Preferences models removed - using default filter state only