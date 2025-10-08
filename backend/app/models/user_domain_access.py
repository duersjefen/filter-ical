"""
User domain access model - tracks which domains users have unlocked.

When a user enters a domain's shared password, we create an entry here
so they don't need to re-enter it on future visits.

This creates a many-to-many relationship between users and domain calendars.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class UserDomainAccess(Base):
    """
    Tracks which users have unlocked which domains.

    When a user successfully enters a domain's password, we create an entry
    to remember they have access. This works with the shared password system -
    users still enter the same domain password, but only once.

    access_level can be 'admin' or 'user' to track which password they used.
    """
    __tablename__ = "user_domain_access"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    calendar_id = Column(Integer, ForeignKey("calendars.id", ondelete="CASCADE"), nullable=False, index=True)
    access_level = Column(String(20), nullable=False)  # 'admin' or 'user'
    unlocked_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="domain_access")
    calendar = relationship("Calendar")

    # Ensure one entry per user per domain per access level
    __table_args__ = (
        UniqueConstraint('user_id', 'calendar_id', 'access_level', name='uq_user_calendar_access'),
    )
