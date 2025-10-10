"""
Admin settings model for database-stored admin configuration.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class AdminSettings(Base):
    """
    Admin settings stored in database.
    Single row table (id=1) containing admin password and configuration.
    """
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
