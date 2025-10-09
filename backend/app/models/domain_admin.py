"""
Domain admin association table for many-to-many relationship between users and domains.

Tracks which users are admins for which domains.
"""

from sqlalchemy import Column, Integer, ForeignKey, Table, DateTime
from sqlalchemy.sql import func

from ..core.database import Base

# Association table for domain admins (many-to-many)
domain_admins = Table(
    "domain_admins",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("domain_id", Integer, ForeignKey("domains.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, default=func.now(), nullable=False),
)
