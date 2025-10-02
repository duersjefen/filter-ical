"""
Application settings service for database operations.

Singleton pattern - only one settings row exists.
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from ..models.app_settings import AppSettings


def get_app_settings(db: Session) -> AppSettings:
    """
    Get application settings (singleton pattern).

    If no settings exist, creates default settings.

    Args:
        db: Database session

    Returns:
        AppSettings object

    I/O Operation - Database query/create.
    """
    settings = db.query(AppSettings).filter(AppSettings.id == 1).first()

    if not settings:
        # Create default settings
        settings = AppSettings(
            id=1,
            footer_visibility='everywhere',
            show_domain_request=True
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


def update_app_settings(
    db: Session,
    footer_visibility: Optional[str] = None,
    show_domain_request: Optional[bool] = None
) -> Tuple[bool, str]:
    """
    Update application settings.

    Args:
        db: Database session
        footer_visibility: 'everywhere', 'admin_only', or 'nowhere'
        show_domain_request: True or False

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database update.
    """
    try:
        settings = get_app_settings(db)

        if footer_visibility is not None:
            if footer_visibility not in ['everywhere', 'admin_only', 'nowhere']:
                return False, "footer_visibility must be 'everywhere', 'admin_only', or 'nowhere'"
            settings.footer_visibility = footer_visibility

        if show_domain_request is not None:
            settings.show_domain_request = show_domain_request

        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Failed to update settings: {str(e)}"
