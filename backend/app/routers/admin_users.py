"""
Admin users router - User management endpoints for global admin.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from ..core.database import get_db
from ..core.auth import verify_admin_auth
from ..models.user import User
from ..models.calendar import Calendar, Filter
from ..models.domain import Domain
from ..services.auth_service import hash_password

router = APIRouter()


# Response models
class UserInfo(BaseModel):
    id: int
    username: str
    email: Optional[str]


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str
    has_password: bool
    account_locked: bool
    failed_login_attempts: int
    created_at: datetime
    updated_at: datetime
    owned_domains_count: int
    admin_domains_count: int
    calendars_count: int
    filters_count: int


class DomainInfo(BaseModel):
    domain_key: str
    name: str
    calendar_url: str
    status: str
    created_at: datetime


class CalendarInfo(BaseModel):
    id: int
    name: str
    source_url: str
    type: str


class FilterInfo(BaseModel):
    id: int
    name: str
    link_uuid: str


class AdminUserDetailResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str
    has_password: bool
    account_locked: bool
    failed_login_attempts: int
    account_locked_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    owned_domains: List[DomainInfo]
    admin_domains: List[DomainInfo]
    calendars: List[CalendarInfo]
    filters: List[FilterInfo]


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None


@router.get(
    "/admin/users",
    summary="List all users (admin only)",
    description="Get paginated list of all users with search capability"
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of users per page"),
    search: Optional[str] = Query(None, description="Search by username or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    List all users with pagination and search.

    Requires admin authentication.
    """
    # Build query
    query = db.query(User)

    # Apply search filter
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    # Apply role filter
    if role:
        if role not in ['user', 'global_admin']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'user' or 'global_admin'"
            )
        query = query.filter(User.role == role)

    # Get total count
    total = query.count()

    # Calculate pagination
    offset = (page - 1) * limit
    total_pages = (total + limit - 1) // limit

    # Get paginated results
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    # Build response with counts
    users_response = []
    for user in users:
        owned_domains_count = db.query(func.count(Domain.id)).filter(Domain.owner_id == user.id).scalar()
        admin_domains_count = len(user.admin_domains)
        calendars_count = db.query(func.count(Calendar.id)).filter(Calendar.user_id == user.id).scalar()
        filters_count = db.query(func.count(Filter.id)).filter(Filter.user_id == user.id).scalar()

        users_response.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "has_password": user.password_hash is not None,
            "account_locked": user.account_locked_until is not None and user.account_locked_until > datetime.utcnow(),
            "failed_login_attempts": user.failed_login_attempts,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "owned_domains_count": owned_domains_count,
            "admin_domains_count": admin_domains_count,
            "calendars_count": calendars_count,
            "filters_count": filters_count
        })

    return {
        "users": users_response,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.get(
    "/admin/users/{user_id}",
    summary="Get user details (admin only)",
    description="Get detailed information about a user including their calendars, domains, and filters"
)
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Get detailed user information.

    Requires admin authentication.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Get owned domains
    owned_domains = db.query(Domain).filter(Domain.owner_id == user.id).all()
    owned_domains_response = [
        {
            "domain_key": d.domain_key,
            "name": d.name,
            "calendar_url": d.calendar_url,
            "status": d.status,
            "created_at": d.created_at
        }
        for d in owned_domains
    ]

    # Get admin domains
    admin_domains_response = [
        {
            "domain_key": d.domain_key,
            "name": d.name,
            "calendar_url": d.calendar_url,
            "status": d.status,
            "created_at": d.created_at
        }
        for d in user.admin_domains
    ]

    # Get calendars
    calendars = db.query(Calendar).filter(Calendar.user_id == user.id).all()
    calendars_response = [
        {
            "id": c.id,
            "name": c.name,
            "source_url": c.source_url,
            "type": c.type
        }
        for c in calendars
    ]

    # Get filters
    filters = db.query(Filter).filter(Filter.user_id == user.id).all()
    filters_response = [
        {
            "id": f.id,
            "name": f.name,
            "link_uuid": f.link_uuid
        }
        for f in filters
    ]

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "has_password": user.password_hash is not None,
        "account_locked": user.account_locked_until is not None and user.account_locked_until > datetime.utcnow(),
        "failed_login_attempts": user.failed_login_attempts,
        "account_locked_until": user.account_locked_until,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "owned_domains": owned_domains_response,
        "admin_domains": admin_domains_response,
        "calendars": calendars_response,
        "filters": filters_response
    }


@router.patch(
    "/admin/users/{user_id}",
    summary="Update user (admin only)",
    description="Update user profile, role, or password"
)
async def update_user(
    user_id: int,
    update_data: UpdateUserRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Update user profile, role, or password.

    Admin can bypass current password requirement.
    Requires admin authentication.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Update email
    if update_data.email is not None:
        # Check if email is already taken
        existing_user = db.query(User).filter(User.email == update_data.email, User.id != user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address already taken"
            )
        user.email = update_data.email

    # Update password (admin bypass - no current password required)
    if update_data.password is not None:
        if len(update_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters"
            )
        user.password_hash = hash_password(update_data.password)

    # Update role
    if update_data.role is not None:
        if update_data.role not in ['user', 'global_admin']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'user' or 'global_admin'"
            )
        user.role = update_data.role

    try:
        db.commit()
        db.refresh(user)

        # Get counts for response
        owned_domains_count = db.query(func.count(Domain.id)).filter(Domain.owner_id == user.id).scalar()
        admin_domains_count = len(user.admin_domains)
        calendars_count = db.query(func.count(Calendar.id)).filter(Calendar.user_id == user.id).scalar()
        filters_count = db.query(func.count(Filter.id)).filter(Filter.user_id == user.id).scalar()

        return {
            "success": True,
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "has_password": user.password_hash is not None,
                "account_locked": user.account_locked_until is not None and user.account_locked_until > datetime.utcnow(),
                "failed_login_attempts": user.failed_login_attempts,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "owned_domains_count": owned_domains_count,
                "admin_domains_count": admin_domains_count,
                "calendars_count": calendars_count,
                "filters_count": filters_count
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete(
    "/admin/users/{user_id}",
    summary="Delete user (admin only)",
    description="Delete user and optionally cascade delete their data"
)
async def delete_user(
    user_id: int,
    delete_calendars: bool = Query(False, description="If true, delete user's calendars. If false, orphan them."),
    delete_domains: bool = Query(False, description="If true, delete owned domains. If false, remove ownership."),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Delete user and optionally cascade delete their data.

    Requires admin authentication.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    try:
        deleted_calendars = 0
        deleted_domains = 0

        # Handle calendars
        if delete_calendars:
            calendars = db.query(Calendar).filter(Calendar.user_id == user.id).all()
            deleted_calendars = len(calendars)
            for calendar in calendars:
                db.delete(calendar)
        else:
            # Orphan calendars
            db.query(Calendar).filter(Calendar.user_id == user.id).update({"user_id": None})

        # Handle domains
        if delete_domains:
            domains = db.query(Domain).filter(Domain.owner_id == user.id).all()
            deleted_domains = len(domains)
            for domain in domains:
                db.delete(domain)
        else:
            # Remove ownership
            db.query(Domain).filter(Domain.owner_id == user.id).update({"owner_id": None})

        # Delete user filters (always cascade)
        db.query(Filter).filter(Filter.user_id == user.id).delete()

        # Delete user
        db.delete(user)
        db.commit()

        return {
            "success": True,
            "message": "User deleted successfully",
            "deleted_calendars": deleted_calendars,
            "deleted_domains": deleted_domains
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.post(
    "/admin/users/{user_id}/unlock",
    summary="Unlock user account (admin only)",
    description="Reset failed login attempts and unlock account"
)
async def unlock_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Unlock user account and reset failed login attempts.

    Requires admin authentication.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    try:
        user.failed_login_attempts = 0
        user.account_locked_until = None
        db.commit()

        return {
            "success": True,
            "message": "Account unlocked successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlock account: {str(e)}"
        )
