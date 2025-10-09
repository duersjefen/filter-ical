"""
Domain request model for custom domain submissions.

Allows users to request their own custom domain calendars with
groups and filters.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class RequestStatus(str, enum.Enum):
    """Domain request status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DomainRequest(Base):
    """
    Domain request model for user submissions.

    Corresponds to DomainRequest schema in OpenAPI spec.
    """
    __tablename__ = "domain_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # Link to User who requested (nullable for backward compat)
    username = Column(String(50), nullable=False, index=True)  # Denormalized for easy display
    email = Column(String(255), nullable=False, index=True)  # Denormalized from user profile
    requested_domain_key = Column(String(100), nullable=False, index=True)  # Requested by user
    calendar_url = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    default_password = Column(String(255), nullable=True)  # Encrypted password for domain (optional)

    # Status tracking
    status = Column(
        SQLEnum(RequestStatus),
        nullable=False,
        default=RequestStatus.PENDING,
        index=True
    )

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Review details
    rejection_reason = Column(Text, nullable=True)
    domain_key = Column(String(100), nullable=True, index=True)  # Final domain_key after approval (may differ from requested)

    def __repr__(self):
        return f"<DomainRequest(id={self.id}, username='{self.username}', status='{self.status.value}')>"
