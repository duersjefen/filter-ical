"""
Application settings model.

Global settings for the application that can be configured by admins.
Singleton pattern - only one row exists in the database.
"""

from sqlalchemy import Column, Integer, String, Boolean
from .calendar import Base


class AppSettings(Base):
    """Global application settings model."""

    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)

    # Footer visibility: 'everywhere', 'admin_only', 'nowhere'
    footer_visibility = Column(String, nullable=False, default='everywhere')

    # Show domain request card: True/False
    show_domain_request = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<AppSettings(id={self.id}, footer_visibility='{self.footer_visibility}', show_domain_request={self.show_domain_request})>"
