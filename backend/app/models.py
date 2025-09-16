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


class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"


# Core Calendar Model
class Calendar(SQLModel, table=True):
    """Calendar model matching OpenAPI Calendar schema"""
    __tablename__ = "calendars"
    
    id: str = Field(default_factory=lambda: f"cal_{uuid.uuid4().hex[:8]}", primary_key=True)
    name: str = Field(min_length=3, max_length=100)
    url: str = Field()
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
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


class UserPreference(SQLModel, table=True):
    """User preferences matching OpenAPI user preferences schema"""
    __tablename__ = "user_preferences"
    
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    user_id: str = Field(unique=True, index=True)
    preferences_json: str = Field(default="{}")  # JSON blob for flexible preferences
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CalendarPreference(SQLModel, table=True):
    """Calendar-specific preferences matching OpenAPI CalendarPreferences schema"""
    __tablename__ = "calendar_preferences"
    
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    user_id: str = Field(index=True)
    calendar_id: str = Field(foreign_key="calendars.id")
    
    # Preference fields matching OpenAPI spec exactly
    selected_events: str = Field(default="[]")  # JSON array
    filter_mode: FilterMode = Field(default=FilterMode.include)
    expanded_events: str = Field(default="[]")  # JSON array
    show_single_events: bool = Field(default=False)
    show_events_section: bool = Field(default=True)
    show_selected_only: bool = Field(default=False)
    event_search: str = Field(default="")
    preview_group: str = Field(default="none")
    saved_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Composite unique constraint on user + calendar  
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class SavedFilter(SQLModel, table=True):
    """Saved filter configurations matching OpenAPI SavedFilter schema"""
    __tablename__ = "saved_filters"
    
    id: str = Field(default_factory=lambda: f"sf_{uuid.uuid4().hex[:8]}", primary_key=True)
    user_id: str = Field(index=True)
    name: str = Field(min_length=3, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Filter configuration matching OpenAPI SavedFilterConfig
    selected_event_types: str = Field(default="[]")  # JSON array
    keyword_filter: str = Field(default="")
    date_range_start: Optional[str] = Field(default=None)  # ISO date string
    date_range_end: Optional[str] = Field(default=None)  # ISO date string
    sort_by: str = Field(default="date")
    sort_direction: SortDirection = Field(default=SortDirection.asc)