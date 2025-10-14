"""
Database models for Filter iCal application.

These models follow the database schema designed for domain integration
and match the OpenAPI specification exactly.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from ..core.database import Base


class Calendar(Base):
    """
    Calendar model for both user calendars and domain calendars.

    Corresponds to Calendar schema in OpenAPI spec.

    Domain calendars: type='domain', user_id=None, linked via domain_auth table
    User calendars: type='user', user_id=required
    """
    __tablename__ = "calendars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_url = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # 'user' or 'domain'
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Owner (nullable for domain calendars)
    last_fetched = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="calendars")
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
    calendar_id = Column(Integer, ForeignKey("calendars.id", ondelete="CASCADE"), nullable=False)
    
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
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)  # FK to domains table (required)
    domain_key = Column(String(100), nullable=True, index=True)  # Legacy field for backward compatibility
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    domain = relationship("Domain", back_populates="groups")
    recurring_event_groups = relationship("RecurringEventGroup", back_populates="group", cascade="all, delete-orphan")
    assignment_rules = relationship("AssignmentRule", back_populates="group", cascade="all, delete-orphan")


class RecurringEventGroup(Base):
    """
    Association between recurring event titles and groups.

    This enables the Groups -> Recurring Events -> Events hierarchy.
    """
    __tablename__ = "recurring_event_groups"

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=True, index=True)  # New FK to domains table
    domain_key = Column(String(100), nullable=True, index=True)  # Legacy field for backward compatibility
    recurring_event_title = Column(String(500), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    group = relationship("Group", back_populates="recurring_event_groups")


class AssignmentRule(Base):
    """
    Auto-assignment rules for automatically assigning recurring events to groups.

    Supports both simple single-condition rules and compound rules with multiple conditions.
    Compound rules can use AND/OR operators to combine child conditions.

    Corresponds to AssignmentRule schema in OpenAPI spec.
    """
    __tablename__ = "assignment_rules"

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=True, index=True)  # New FK to domains table
    domain_key = Column(String(100), nullable=True, index=True)  # Legacy field for backward compatibility

    # Single condition fields (nullable for compound parent rules)
    rule_type = Column(String(50), nullable=True)  # 'title_contains', 'description_contains', 'category_contains'
    rule_value = Column(String(500), nullable=True)

    # Compound rule fields
    parent_rule_id = Column(Integer, ForeignKey("assignment_rules.id", ondelete="CASCADE"), nullable=True)
    operator = Column(String(10), nullable=False, default="AND")  # 'AND' or 'OR'
    is_compound = Column(Boolean, nullable=False, default=False)

    target_group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    group = relationship("Group", back_populates="assignment_rules")
    child_conditions = relationship("AssignmentRule", backref=backref("parent", remote_side=[id]), cascade="all, delete-orphan")

    def __repr__(self):
        if self.is_compound:
            return f"<AssignmentRule(id={self.id}, compound={self.operator}, conditions={len(self.child_conditions)}, target_group={self.target_group_id})>"
        return f"<AssignmentRule(id={self.id}, {self.rule_type}='{self.rule_value}', target_group={self.target_group_id})>"


class Filter(Base):
    """
    Filter model for both user and domain calendar filters.

    Corresponds to Filter schema in OpenAPI spec.

    User filters: calendar_id + user_id set
    Domain filters: domain_id/domain_key set (user_id optional for anonymous filters)
    """
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    # Either calendar_id (user filters) OR domain_id/domain_key (domain filters)
    calendar_id = Column(Integer, ForeignKey("calendars.id", ondelete="CASCADE"), nullable=True)
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=True, index=True)  # New FK to domains table
    domain_key = Column(String(100), nullable=True, index=True)  # Legacy field for API compatibility

    # Owner (nullable for anonymous domain filters stored in localStorage)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Filter data stored as JSON arrays for flexibility
    subscribed_event_ids = Column(JSON, nullable=True, default=list)  # Array of event IDs/titles
    subscribed_group_ids = Column(JSON, nullable=True, default=list)   # Array of group IDs (domain only)
    unselected_event_ids = Column(JSON, nullable=True, default=list)   # Array of event titles to exclude (domain only)

    # Personal calendar option: include future recurring events
    include_future_events = Column(Boolean, nullable=True, default=False)  # Personal calendars only

    # Dynamic iCal export
    link_uuid = Column(String(36), nullable=False, unique=True, index=True)  # UUID for /ical/{uuid}.ics

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    calendar = relationship("Calendar", back_populates="filters")
    user = relationship("User", back_populates="filters")

    def __init__(self, **kwargs):
        """Auto-generate UUID for new filters."""
        if 'link_uuid' not in kwargs:
            kwargs['link_uuid'] = str(uuid.uuid4())
        super().__init__(**kwargs)


class DomainBackup(Base):
    """
    Domain configuration backup model for snapshot/restore functionality.

    Stores complete domain configuration snapshots to enable:
    - Manual backups by administrators
    - Automatic backups before destructive operations
    - Point-in-time restoration
    - Configuration history and audit trail

    Corresponds to DomainBackup schema in OpenAPI spec.
    """
    __tablename__ = "domain_backups"

    id = Column(Integer, primary_key=True, index=True)
    domain_key = Column(String(100), nullable=False, index=True)

    # Full configuration snapshot stored as JSON (compatible with YAML format)
    config_snapshot = Column(JSON, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    created_by = Column(String(100), nullable=True)  # Username who created backup
    description = Column(Text, nullable=True)  # User-provided description

    # Backup type for filtering and UX
    backup_type = Column(
        String(50),
        nullable=False,
        default='manual'
    )  # 'manual', 'auto_pre_reset', 'auto_pre_import', 'auto_pre_restore'