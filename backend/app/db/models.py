"""
Pydantic models for DynamoDB documents.

Uses denormalized document design - relationships embedded as nested objects.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# =============================================================================
# Nested models (embedded in parent documents)
# =============================================================================

class RuleCondition(BaseModel):
    """Single condition for an assignment rule."""
    type: str  # 'title_contains', 'description_contains', 'category_contains'
    value: str


class AssignmentRule(BaseModel):
    """
    Assignment rule for auto-grouping events.

    Can be simple (single condition) or compound (multiple conditions with AND/OR).
    """
    id: int
    type: Optional[str] = None  # 'title_contains', etc. (None for compound)
    value: Optional[str] = None  # Match value (None for compound)
    operator: str = "AND"  # 'AND' or 'OR' for compound rules
    is_compound: bool = False
    conditions: list[RuleCondition] = Field(default_factory=list)  # Child conditions


class DomainGroup(BaseModel):
    """Group within a domain for organizing events."""
    id: int
    name: str
    rules: list[AssignmentRule] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Top-level document models
# =============================================================================

class Domain(BaseModel):
    """
    Domain document - contains all domain configuration.

    Denormalized: groups and rules embedded, not separate items.
    """
    # Key fields (for DynamoDB)
    domain_key: str  # Used in PK: DOMAIN#{domain_key}

    # Domain configuration
    name: str
    calendar_url: str
    status: str = "active"  # 'active', 'inactive', 'pending'

    # Authentication (bcrypt hashed)
    admin_password_hash: Optional[str] = None
    user_password_hash: Optional[str] = None

    # Embedded groups (denormalized)
    groups: list[DomainGroup] = Field(default_factory=list)

    # Recurring event to group mapping: {"Event Title": group_id}
    recurring_assignments: dict[str, int] = Field(default_factory=dict)

    # Ownership
    owner_id: Optional[int] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dynamo_item(self) -> dict:
        """Convert to DynamoDB item format."""
        return {
            "PK": f"DOMAIN#{self.domain_key}",
            "SK": "METADATA",
            "domain_key": self.domain_key,
            "name": self.name,
            "calendar_url": self.calendar_url,
            "status": self.status,
            "admin_password_hash": self.admin_password_hash,
            "user_password_hash": self.user_password_hash,
            "groups": [g.model_dump() for g in self.groups],
            "recurring_assignments": self.recurring_assignments,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dynamo_item(cls, item: dict) -> "Domain":
        """Create from DynamoDB item."""
        groups = [DomainGroup(**g) for g in item.get("groups", [])]
        return cls(
            domain_key=item["domain_key"],
            name=item["name"],
            calendar_url=item["calendar_url"],
            status=item.get("status", "active"),
            admin_password_hash=item.get("admin_password_hash"),
            user_password_hash=item.get("user_password_hash"),
            groups=groups,
            recurring_assignments=item.get("recurring_assignments", {}),
            owner_id=item.get("owner_id"),
            created_at=datetime.fromisoformat(item["created_at"]) if item.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(item["updated_at"]) if item.get("updated_at") else datetime.utcnow(),
        )


class Event(BaseModel):
    """
    Calendar event.

    Stored as separate items for volume (many events per domain).
    """
    # Key fields
    domain_key: str  # For PK: DOMAIN#{domain_key}
    uid: str  # iCal UID
    start_date: str  # ISO date for SK sorting: EVENT#{date}#{uid}

    # Event data
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = None

    # Additional iCal fields
    other_fields: dict = Field(default_factory=dict)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dynamo_item(self) -> dict:
        """Convert to DynamoDB item format."""
        return {
            "PK": f"DOMAIN#{self.domain_key}",
            "SK": f"EVENT#{self.start_date}#{self.uid}",
            "domain_key": self.domain_key,
            "uid": self.uid,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "description": self.description,
            "location": self.location,
            "other_fields": self.other_fields,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dynamo_item(cls, item: dict) -> "Event":
        """Create from DynamoDB item."""
        # Extract start_date from SK: EVENT#{date}#{uid}
        sk_parts = item["SK"].split("#")
        start_date = sk_parts[1] if len(sk_parts) > 1 else ""

        return cls(
            domain_key=item["domain_key"],
            uid=item["uid"],
            start_date=start_date,
            title=item["title"],
            start_time=datetime.fromisoformat(item["start_time"]),
            end_time=datetime.fromisoformat(item["end_time"]) if item.get("end_time") else None,
            description=item.get("description"),
            location=item.get("location"),
            other_fields=item.get("other_fields", {}),
            created_at=datetime.fromisoformat(item["created_at"]) if item.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(item["updated_at"]) if item.get("updated_at") else datetime.utcnow(),
        )


class Filter(BaseModel):
    """
    User filter configuration for iCal export.

    Each filter has a unique link_uuid for the /ical/{uuid}.ics endpoint.
    """
    # Key fields
    link_uuid: str  # PK: FILTER#{link_uuid}

    # Associated domain
    domain_key: str

    # Filter configuration
    name: str = "My Filter"
    subscribed_group_ids: list[int] = Field(default_factory=list)
    unselected_event_titles: list[str] = Field(default_factory=list)
    include_future_events: bool = False

    # Owner (optional)
    user_id: Optional[int] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dynamo_item(self) -> dict:
        """Convert to DynamoDB item format."""
        return {
            "PK": f"FILTER#{self.link_uuid}",
            "SK": "METADATA",
            "link_uuid": self.link_uuid,  # Also stored for GSI
            "domain_key": self.domain_key,
            "name": self.name,
            "subscribed_group_ids": self.subscribed_group_ids,
            "unselected_event_titles": self.unselected_event_titles,
            "include_future_events": self.include_future_events,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dynamo_item(cls, item: dict) -> "Filter":
        """Create from DynamoDB item."""
        return cls(
            link_uuid=item["link_uuid"],
            domain_key=item["domain_key"],
            name=item.get("name", "My Filter"),
            subscribed_group_ids=item.get("subscribed_group_ids", []),
            unselected_event_titles=item.get("unselected_event_titles", []),
            include_future_events=item.get("include_future_events", False),
            user_id=item.get("user_id"),
            created_at=datetime.fromisoformat(item["created_at"]) if item.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(item["updated_at"]) if item.get("updated_at") else datetime.utcnow(),
        )


class Admin(BaseModel):
    """
    Admin user for the application.

    Supports password reset tokens.
    """
    # Key fields
    email: str  # PK: ADMIN#{email}

    # Authentication
    password_hash: str

    # Password reset
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dynamo_item(self) -> dict:
        """Convert to DynamoDB item format."""
        return {
            "PK": f"ADMIN#{self.email}",
            "SK": "METADATA",
            "email": self.email,
            "password_hash": self.password_hash,
            "reset_token": self.reset_token,
            "reset_token_expires": self.reset_token_expires.isoformat() if self.reset_token_expires else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dynamo_item(cls, item: dict) -> "Admin":
        """Create from DynamoDB item."""
        return cls(
            email=item["email"],
            password_hash=item["password_hash"],
            reset_token=item.get("reset_token"),
            reset_token_expires=datetime.fromisoformat(item["reset_token_expires"]) if item.get("reset_token_expires") else None,
            created_at=datetime.fromisoformat(item["created_at"]) if item.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(item["updated_at"]) if item.get("updated_at") else datetime.utcnow(),
        )
