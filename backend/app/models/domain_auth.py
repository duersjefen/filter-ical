"""
Domain authentication model for password-protected domain access.

This model stores:
- domain_key: The URL slug for the domain (e.g., 'university' for /university)
- calendar_id: Link to the domain's calendar
- password_hash: Shared passwords for domain access (admin and user levels)

This is the authoritative source for domain_key (not the calendars table).
Enables two-tier access control:
- Admin password: Protects /{domain}/admin routes
- User password: Protects /{domain} public calendar routes

Security is isolated from domain configuration (YAML files).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from ..core.database import Base


class DomainAuth(Base):
    """
    Domain authentication and configuration model.

    Links domain_key (URL slug) to calendar and manages access control.
    Each domain can have optional admin and user passwords (shared).
    Passwords are stored as encrypted strings (Fernet encryption).

    Corresponds to domain authentication requirements.
    """
    __tablename__ = "domain_auth"

    id = Column(Integer, primary_key=True, index=True)
    domain_key = Column(String(100), unique=True, nullable=False, index=True)  # URL slug
    calendar_id = Column(Integer, ForeignKey("calendars.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Optional password hashes (nullable = password not set)
    admin_password_hash = Column(String, nullable=True)  # Protects admin routes (Fernet encrypted)
    user_password_hash = Column(String, nullable=True)   # Protects public routes (Fernet encrypted)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
