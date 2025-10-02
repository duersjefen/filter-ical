"""
Domain authentication model for password-protected domain access.

This model stores password hashes for domain-level authentication,
enabling two-tier access control:
- Admin password: Protects /{domain}/admin routes
- User password: Protects /{domain} public calendar routes

Security is isolated from domain configuration (YAML files).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from ..core.database import Base


class DomainAuth(Base):
    """
    Domain authentication model for password-based access control.

    Each domain can have optional admin and user passwords.
    Passwords are stored as bcrypt hashes for security.

    Corresponds to domain authentication requirements.
    """
    __tablename__ = "domain_auth"

    id = Column(Integer, primary_key=True, index=True)
    domain_key = Column(String(100), unique=True, nullable=False, index=True)

    # Optional password hashes (nullable = password not set)
    admin_password_hash = Column(String, nullable=True)  # Protects admin routes
    user_password_hash = Column(String, nullable=True)   # Protects public routes

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
