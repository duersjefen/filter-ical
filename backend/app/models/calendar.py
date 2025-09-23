"""
Database models for iCal Viewer application.

These models follow the database schema designed for domain integration
and match the OpenAPI specification exactly.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Calendar(Base):
    """
    Calendar model for both user calendars and domain calendars.
    
    Corresponds to Calendar schema in OpenAPI spec.
    """
    __tablename__ = "calendars"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_url = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # 'user' or 'domain'
    domain_key = Column(String(100), nullable=True)  # For domain calendars
    username = Column(String(100), nullable=True)  # Optional user scoping
    last_fetched = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    events = relationship("Event", back_populates="calendar", cascade="all, delete-orphan")
    filters = relationship("Filter", back_populates="calendar", cascade="all, delete-orphan")


class Event(Base):
    """
    Event model for all calendar events (simple datetime approach).
    
    Single table for all events from all calendars (domain and user).
    Uses simple start_time/end_time datetimes - frontend calculates display logic.
    Corresponds to Event schema in OpenAPI spec.
    """
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=False)
    
    # Core event data
    title = Column(String(500), nullable=False, index=True)  # Indexed for grouping recurring events
    start_time = Column(DateTime, nullable=False, index=True)  # Indexed for time filtering
    end_time = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    uid = Column(String(255), nullable=False)  # Original iCal UID
    
    # Additional iCal fields stored as JSON for flexibility
    other_ical_fields = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    calendar = relationship("Calendar", back_populates="events")


class Group(Base):
    """
    Group model for domain calendar event organization.
    
    Corresponds to Group schema in OpenAPI spec.
    """
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_key = Column(String(100), nullable=False, index=True)  # Links to domains.yaml
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    recurring_event_groups = relationship("RecurringEventGroup", back_populates="group", cascade="all, delete-orphan")
    assignment_rules = relationship("AssignmentRule", back_populates="group", cascade="all, delete-orphan")


class RecurringEventGroup(Base):
    """
    Association between recurring event titles and groups.
    
    This enables the Groups -> Recurring Events -> Events hierarchy.
    """
    __tablename__ = "recurring_event_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_key = Column(String(100), nullable=False, index=True)
    recurring_event_title = Column(String(500), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    group = relationship("Group", back_populates="recurring_event_groups")


class AssignmentRule(Base):
    """
    Auto-assignment rules for automatically assigning recurring events to groups.
    
    Corresponds to AssignmentRule schema in OpenAPI spec.
    """
    __tablename__ = "assignment_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_key = Column(String(100), nullable=False, index=True)
    rule_type = Column(String(50), nullable=False)  # 'title_contains', 'description_contains'
    rule_value = Column(String(500), nullable=False)
    target_group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    group = relationship("Group", back_populates="assignment_rules")


class Filter(Base):
    """
    Filter model for both user and domain calendar filters.
    
    Corresponds to Filter schema in OpenAPI spec.
    """
    __tablename__ = "filters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Either calendar_id (user filters) OR domain_key (domain filters)
    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=True)
    domain_key = Column(String(100), nullable=True, index=True)
    
    username = Column(String(100), nullable=True)  # Optional user scoping
    
    # Filter data stored as JSON arrays for flexibility
    subscribed_event_ids = Column(JSON, nullable=True, default=list)  # Array of event IDs
    subscribed_group_ids = Column(JSON, nullable=True, default=list)   # Array of group IDs (domain only)
    
    # Dynamic iCal export
    link_uuid = Column(String(36), nullable=False, unique=True, index=True)  # UUID for /ical/{uuid}.ics
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    calendar = relationship("Calendar", back_populates="filters")
    
    def __init__(self, **kwargs):
        """Auto-generate UUID for new filters."""
        if 'link_uuid' not in kwargs:
            kwargs['link_uuid'] = str(uuid.uuid4())
        super().__init__(**kwargs)