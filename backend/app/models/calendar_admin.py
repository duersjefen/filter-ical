"""
Calendar admin association table for many-to-many relationship between users and calendars.

Tracks which users have what permission level for which calendars.
Permissions: 'read', 'write', 'admin'
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.sql import func

from ..core.database import Base

# Association table for calendar admins (many-to-many with permission levels)
calendar_admins = Table(
    "calendar_admins",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("calendar_id", Integer, ForeignKey("calendars.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("permission_level", String(20), nullable=False),  # 'read', 'write', 'admin'
    Column("created_at", DateTime, default=func.now(), nullable=False),
)
