"""
Domain model - Unified source of truth for domain configuration.

Consolidates:
- Domain configuration (replaces domains.yaml)
- Authentication (replaces domain_auth table)
- Calendar linkage

This is the authoritative source for all domain-related data.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Domain(Base):
    """
    Unified domain model - single source of truth.

    Replaces:
    - domains.yaml configuration files
    - domain_auth table

    Each domain has:
    - domain_key: URL slug (e.g., 'exter' for /exter route)
    - name: Display name
    - calendar_url: Source iCal URL
    - calendar_id: Link to synced Calendar record
    - owner_id: User who owns the domain
    - Optional admin/user passwords (Fernet encrypted)

    Corresponds to domain requirements in OpenAPI spec.
    """
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    domain_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    calendar_url = Column(Text, nullable=False)

    # Ownership (nullable for backward compatibility with existing domains)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Calendar linkage (nullable until first sync creates calendar)
    calendar_id = Column(Integer, ForeignKey("calendars.id", ondelete="SET NULL"), nullable=True, unique=True, index=True)

    # Authentication (merged from DomainAuth)
    admin_password_hash = Column(String(255), nullable=True)  # Fernet encrypted
    user_password_hash = Column(String(255), nullable=True)   # Fernet encrypted

    # Status tracking
    status = Column(String(50), nullable=False, default='active')  # active, inactive, pending

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_domains")
    calendar = relationship("Calendar", foreign_keys=[calendar_id])
    groups = relationship("Group", back_populates="domain", cascade="all, delete-orphan")
    admins = relationship("User", secondary="domain_admins", back_populates="admin_domains")

    def __repr__(self):
        return f"<Domain(domain_key='{self.domain_key}', name='{self.name}', status='{self.status}')>"
