"""
User model for authentication and account management.

Users can be:
- Global admins (role='global_admin') - Access to /admin panel
- Regular users (role='user') - Own calendars and filters

Email and password are optional:
- Username-only: Cross-device sync but insecure (anyone can access)
- Username + password: Secure cross-device sync
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class User(Base):
    """
    User model for authentication and account management.

    Supports two authentication modes:
    1. Username-only (password_hash=None): Insecure but zero friction
    2. Username + password: Secure with bcrypt hashing

    Global admin users have role='global_admin' and access to /admin panel.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)  # Optional
    password_hash = Column(String, nullable=True)  # Optional - bcrypt hash
    role = Column(String(20), nullable=False, default='user')  # 'global_admin' or 'user'

    # Password reset (only for users with email + password)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    calendars = relationship("Calendar", back_populates="user")
    filters = relationship("Filter", back_populates="user")
    domain_access = relationship("UserDomainAccess", back_populates="user", cascade="all, delete-orphan")
