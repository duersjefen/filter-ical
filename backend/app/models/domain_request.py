"""
Domain request model for custom domain submissions.

Allows users to request their own custom domain calendars with
groups and filters.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
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
    username = Column(String(50), nullable=False, index=True)
    calendar_url = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

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
    domain_key = Column(String(100), nullable=True, index=True)  # Set after approval

    def __repr__(self):
        return f"<DomainRequest(id={self.id}, username='{self.username}', status='{self.status.value}')>"
