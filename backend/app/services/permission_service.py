"""
Permission service for calendar access control.

FUNCTIONAL CORE - Pure functions for permission management logic.
IMPERATIVE SHELL - Database operations handled by routers.

Handles:
- Calendar permissions (read, write, admin)
- Permission granting and revoking
- Permission checking
- Calendar listing with permission stats
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..models.calendar import Calendar
from ..models.user import User
from ..models.calendar_admin import calendar_admins


# Permission levels in order of access rights
# 'user' = normal access to calendar, 'admin' = admin access to calendar
PERMISSION_LEVELS = ['user', 'admin']


def list_calendar_permissions(db: Session, calendar_id: int) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    List all permissions for a calendar.

    Args:
        db: Database session
        calendar_id: Calendar ID

    Returns:
        Tuple of (success, permissions_list, error_message)
        Each permission dict contains:
        - user_id: User ID
        - username: Username
        - email: User email
        - permission_level: Permission level ('user', 'admin')
        - created_at: When permission was granted

    I/O Operation - Database query.
    """
    # Verify calendar exists
    calendar = db.query(Calendar).filter(Calendar.id == calendar_id).first()
    if not calendar:
        return False, [], f"Calendar {calendar_id} not found"

    # Query permissions with user info
    permissions = db.query(
        calendar_admins.c.user_id,
        calendar_admins.c.permission_level,
        calendar_admins.c.created_at,
        User.username,
        User.email
    ).join(
        User, User.id == calendar_admins.c.user_id
    ).filter(
        calendar_admins.c.calendar_id == calendar_id
    ).order_by(
        User.username
    ).all()

    permission_dicts = []
    for perm in permissions:
        permission_dicts.append({
            'user_id': perm.user_id,
            'username': perm.username,
            'email': perm.email,
            'permission_level': perm.permission_level,
            'created_at': perm.created_at.isoformat() if perm.created_at else None
        })

    return True, permission_dicts, ""


def grant_calendar_permission(
    db: Session,
    calendar_id: int,
    user_id: int,
    permission_level: str
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Grant calendar permission to a user.

    Args:
        db: Database session
        calendar_id: Calendar ID
        user_id: User ID
        permission_level: Permission level ('user', 'admin')

    Returns:
        Tuple of (success, permission_dict, error_message)

    I/O Operation - Database insert or update.
    """
    # Validate permission level
    if permission_level not in PERMISSION_LEVELS:
        return False, None, f"Invalid permission level. Must be one of: {', '.join(PERMISSION_LEVELS)}"

    # Verify calendar exists
    calendar = db.query(Calendar).filter(Calendar.id == calendar_id).first()
    if not calendar:
        return False, None, f"Calendar {calendar_id} not found"

    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, None, f"User {user_id} not found"

    # Check if permission already exists
    existing = db.query(calendar_admins).filter(
        and_(
            calendar_admins.c.calendar_id == calendar_id,
            calendar_admins.c.user_id == user_id
        )
    ).first()

    try:
        if existing:
            # Update existing permission
            db.execute(
                calendar_admins.update().where(
                    and_(
                        calendar_admins.c.calendar_id == calendar_id,
                        calendar_admins.c.user_id == user_id
                    )
                ).values(permission_level=permission_level)
            )
        else:
            # Insert new permission
            db.execute(
                calendar_admins.insert().values(
                    calendar_id=calendar_id,
                    user_id=user_id,
                    permission_level=permission_level
                )
            )

        db.commit()

        # Fetch the created/updated permission
        permission = db.query(
            calendar_admins.c.user_id,
            calendar_admins.c.permission_level,
            calendar_admins.c.created_at,
            User.username,
            User.email
        ).join(
            User, User.id == calendar_admins.c.user_id
        ).filter(
            and_(
                calendar_admins.c.calendar_id == calendar_id,
                calendar_admins.c.user_id == user_id
            )
        ).first()

        permission_dict = {
            'user_id': permission.user_id,
            'username': permission.username,
            'email': permission.email,
            'permission_level': permission.permission_level,
            'created_at': permission.created_at.isoformat() if permission.created_at else None
        }

        return True, permission_dict, ""
    except Exception as e:
        db.rollback()
        return False, None, f"Failed to grant permission: {str(e)}"


def revoke_calendar_permission(db: Session, calendar_id: int, user_id: int) -> Tuple[bool, str]:
    """
    Revoke calendar permission from a user.

    Args:
        db: Database session
        calendar_id: Calendar ID
        user_id: User ID

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database delete.
    """
    # Verify permission exists
    existing = db.query(calendar_admins).filter(
        and_(
            calendar_admins.c.calendar_id == calendar_id,
            calendar_admins.c.user_id == user_id
        )
    ).first()

    if not existing:
        return False, f"Permission not found for user {user_id} on calendar {calendar_id}"

    try:
        db.execute(
            calendar_admins.delete().where(
                and_(
                    calendar_admins.c.calendar_id == calendar_id,
                    calendar_admins.c.user_id == user_id
                )
            )
        )
        db.commit()
        return True, ""
    except Exception as e:
        db.rollback()
        return False, f"Failed to revoke permission: {str(e)}"


def check_calendar_permission(
    db: Session,
    calendar_id: int,
    user_id: int,
    required_level: str = 'user'
) -> bool:
    """
    Check if user has required permission level for calendar.

    Permission hierarchy: admin > user
    User with 'admin' can do anything requiring 'user' access

    Args:
        db: Database session
        calendar_id: Calendar ID
        user_id: User ID
        required_level: Required permission level ('user', 'admin')

    Returns:
        True if user has required permission level or higher

    I/O Operation - Database query.
    """
    # Validate required level
    if required_level not in PERMISSION_LEVELS:
        return False

    # Check if user owns the calendar (implicit admin permission)
    calendar = db.query(Calendar).filter(Calendar.id == calendar_id).first()
    if calendar and calendar.user_id == user_id:
        return True

    # Check explicit permission
    permission = db.query(calendar_admins.c.permission_level).filter(
        and_(
            calendar_admins.c.calendar_id == calendar_id,
            calendar_admins.c.user_id == user_id
        )
    ).first()

    if not permission:
        return False

    # Check permission level hierarchy
    user_level = permission.permission_level
    user_level_index = PERMISSION_LEVELS.index(user_level) if user_level in PERMISSION_LEVELS else -1
    required_level_index = PERMISSION_LEVELS.index(required_level)

    # User must have equal or higher level (higher index = higher permission)
    return user_level_index >= required_level_index


def list_all_calendars_paginated(
    db: Session,
    page: int = 1,
    limit: int = 20,
    calendar_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all calendars with statistics and pagination.

    Args:
        db: Database session
        page: Page number (1-indexed)
        limit: Results per page (max 100)
        calendar_type: Optional filter ('user' or 'domain')

    Returns:
        Dict with keys:
        - calendars: List of calendar dicts
        - total: Total count of calendars
        - page: Current page number
        - limit: Results per page
        - total_pages: Total number of pages

        Each calendar dict contains:
        - id: Calendar ID
        - name: Calendar name
        - type: Calendar type
        - owner_id: Owner user ID
        - owner_username: Owner username
        - events_count: Number of events
        - filters_count: Number of filters
        - permissions_count: Number of permissions granted
        - created_at: Creation timestamp

    I/O Operation - Database query with pagination.
    """
    # Validate and normalize inputs
    page = max(1, page)
    limit = min(max(1, limit), 100)
    offset = (page - 1) * limit

    # Build query
    query = db.query(Calendar)

    # Apply type filter
    if calendar_type and calendar_type in ['user', 'domain']:
        query = query.filter(Calendar.type == calendar_type)

    # Get total count
    total = query.count()

    # Apply pagination and order
    calendars = query.order_by(Calendar.created_at.desc()).offset(offset).limit(limit).all()

    # Build calendar dicts with statistics
    calendar_dicts = []
    for calendar in calendars:
        # Get owner username if exists
        owner_username = None
        if calendar.user_id:
            owner = db.query(User.username).filter(User.id == calendar.user_id).first()
            owner_username = owner.username if owner else None

        # Count events
        from ..models.calendar import Event, Filter
        events_count = db.query(func.count(Event.id)).filter(Event.calendar_id == calendar.id).scalar()

        # Count filters
        filters_count = db.query(func.count(Filter.id)).filter(Filter.calendar_id == calendar.id).scalar()

        # Count permissions
        permissions_count = db.query(func.count(calendar_admins.c.user_id)).filter(
            calendar_admins.c.calendar_id == calendar.id
        ).scalar()

        calendar_dicts.append({
            'id': calendar.id,
            'name': calendar.name,
            'type': calendar.type,
            'source_url': calendar.source_url,
            'owner_id': calendar.user_id,
            'owner_username': owner_username,
            'events_count': events_count or 0,
            'filters_count': filters_count or 0,
            'permissions_count': permissions_count or 0,
            'last_fetched': calendar.last_fetched.isoformat() if calendar.last_fetched else None,
            'created_at': calendar.created_at.isoformat() if calendar.created_at else None,
        })

    # Calculate total pages
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        'calendars': calendar_dicts,
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': total_pages
    }
