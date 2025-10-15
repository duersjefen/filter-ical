"""
User management service for admin panel operations.

FUNCTIONAL CORE - Pure functions for user management logic.
IMPERATIVE SHELL - Database operations handled by routers.

Handles:
- User listing and pagination
- User details retrieval
- User updates (email, password, role)
- User deletion with cascading options
- Account unlocking
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from ..models.user import User
from ..models.calendar import Calendar, Filter
from ..models.domain import Domain
from .auth_service import hash_password, is_valid_email, is_valid_password


def list_users_paginated(
    db: Session,
    page: int = 1,
    limit: int = 20,
    search_query: Optional[str] = None,
    role_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    List users with pagination and filtering.

    Args:
        db: Database session
        page: Page number (1-indexed)
        limit: Results per page (max 100)
        search_query: Optional search term for username/email
        role_filter: Optional role filter ('user', 'global_admin')

    Returns:
        Dict with keys:
        - users: List of user dicts
        - total: Total count of users matching filters
        - page: Current page number
        - limit: Results per page
        - total_pages: Total number of pages

    I/O Operation - Database query with pagination.
    """
    # Validate and normalize inputs
    page = max(1, page)
    limit = min(max(1, limit), 100)
    offset = (page - 1) * limit

    # Build query
    query = db.query(User)

    # Apply role filter
    if role_filter and role_filter in ['user', 'global_admin']:
        query = query.filter(User.role == role_filter)

    # Apply search filter
    if search_query and search_query.strip():
        search_term = f"%{search_query.strip()}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination and order
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    # Convert to dicts
    user_dicts = []
    for user in users:
        user_dicts.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'has_password': user.password_hash is not None,
            'is_locked': user.account_locked_until is not None,
            'failed_login_attempts': user.failed_login_attempts,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        })

    # Calculate total pages
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        'users': user_dicts,
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': total_pages
    }


def get_user_details(db: Session, user_id: int) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Get detailed user information including related data.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Tuple of (success, user_dict, error_message)
        User dict includes:
        - Basic user info
        - Calendars count
        - Filters count
        - Owned domains count
        - Admin domains count

    I/O Operation - Database query with relationships.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, None, f"User {user_id} not found"

    # Count related entities
    calendars_count = db.query(func.count(Calendar.id)).filter(Calendar.user_id == user_id).scalar()
    filters_count = db.query(func.count(Filter.id)).filter(Filter.user_id == user_id).scalar()
    owned_domains_count = db.query(func.count(Domain.id)).filter(Domain.owner_id == user_id).scalar()

    # Count admin domains (from domain_admins association table)
    from ..models.domain_admin import domain_admins
    admin_domains_count = db.query(func.count(domain_admins.c.domain_id)).filter(
        domain_admins.c.user_id == user_id
    ).scalar()

    user_dict = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'has_password': user.password_hash is not None,
        'is_locked': user.account_locked_until is not None,
        'account_locked_until': user.account_locked_until.isoformat() if user.account_locked_until else None,
        'failed_login_attempts': user.failed_login_attempts,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        'calendars_count': calendars_count or 0,
        'filters_count': filters_count or 0,
        'owned_domains_count': owned_domains_count or 0,
        'admin_domains_count': admin_domains_count or 0,
    }

    return True, user_dict, ""


def update_user(
    db: Session,
    user_id: int,
    email: Optional[str] = None,
    password: Optional[str] = None,
    role: Optional[str] = None
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Update user information.

    Args:
        db: Database session
        user_id: User ID
        email: New email (None = no change)
        password: New password (None = no change)
        role: New role (None = no change)

    Returns:
        Tuple of (success, updated_user_dict, error_message)

    I/O Operation - Database update.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, None, f"User {user_id} not found"

    # Validate email if provided
    if email is not None:
        email = email.strip() if email else None
        if email:
            is_valid, error_msg = is_valid_email(email)
            if not is_valid:
                return False, None, error_msg

            # Check for duplicate email
            existing = db.query(User).filter(User.email == email, User.id != user_id).first()
            if existing:
                return False, None, "Email already in use by another user"

            user.email = email
        else:
            user.email = None

    # Validate and update password if provided
    if password is not None:
        if password.strip():
            is_valid, error_msg = is_valid_password(password)
            if not is_valid:
                return False, None, error_msg

            user.password_hash = hash_password(password)
        else:
            user.password_hash = None

    # Validate and update role if provided
    if role is not None:
        if role not in ['user', 'global_admin']:
            return False, None, "Invalid role. Must be 'user' or 'global_admin'"
        user.role = role

    try:
        db.commit()
        db.refresh(user)

        user_dict = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'has_password': user.password_hash is not None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        }

        return True, user_dict, ""
    except Exception as e:
        db.rollback()
        return False, None, f"Failed to update user: {str(e)}"


def delete_user(
    db: Session,
    user_id: int,
    delete_calendars: bool = False,
    delete_domains: bool = False
) -> Tuple[bool, Dict[str, int], str]:
    """
    Delete user with optional cascading deletion of related entities.

    Args:
        db: Database session
        user_id: User ID
        delete_calendars: If True, delete user's calendars (default: False)
        delete_domains: If True, delete user's owned domains (default: False)

    Returns:
        Tuple of (success, deletion_stats_dict, error_message)
        Stats dict contains:
        - calendars_deleted: Number of calendars deleted
        - filters_deleted: Number of filters deleted
        - domains_deleted: Number of domains deleted

    I/O Operation - Database delete with cascading.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, {}, f"User {user_id} not found"

    stats = {
        'calendars_deleted': 0,
        'filters_deleted': 0,
        'domains_deleted': 0
    }

    try:
        # Delete calendars if requested
        if delete_calendars:
            calendars = db.query(Calendar).filter(Calendar.user_id == user_id).all()
            stats['calendars_deleted'] = len(calendars)
            for calendar in calendars:
                db.delete(calendar)

        # Delete filters (always cascade - they're user-specific)
        filters = db.query(Filter).filter(Filter.user_id == user_id).all()
        stats['filters_deleted'] = len(filters)
        for filter_obj in filters:
            db.delete(filter_obj)

        # Delete owned domains if requested
        if delete_domains:
            domains = db.query(Domain).filter(Domain.owner_id == user_id).all()
            stats['domains_deleted'] = len(domains)
            for domain in domains:
                db.delete(domain)
        else:
            # Set domain ownership to NULL instead of deleting
            db.query(Domain).filter(Domain.owner_id == user_id).update({'owner_id': None})

        # Delete user
        db.delete(user)
        db.commit()

        return True, stats, ""
    except Exception as e:
        db.rollback()
        return False, {}, f"Failed to delete user: {str(e)}"


def unlock_user_account(db: Session, user_id: int) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Unlock user account by resetting failed login attempts and lockout.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Tuple of (success, updated_user_dict, error_message)

    I/O Operation - Database update.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, None, f"User {user_id} not found"

    # Reset lockout fields
    user.failed_login_attempts = 0
    user.account_locked_until = None

    try:
        db.commit()
        db.refresh(user)

        user_dict = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_locked': False,
            'failed_login_attempts': 0,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        }

        return True, user_dict, ""
    except Exception as e:
        db.rollback()
        return False, None, f"Failed to unlock user: {str(e)}"
