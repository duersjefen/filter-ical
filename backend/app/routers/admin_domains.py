"""
Admin domains router - Direct domain management (create, delete, assign owner).

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import re
import httpx

from ..core.database import get_db
from ..core.auth import verify_admin_auth
from ..models.domain import Domain
from ..models.calendar import Calendar
from ..data.ical_parser import parse_ical_content
from ..core.config import settings

router = APIRouter()


class CreateDomainRequest(BaseModel):
    """Request body for direct domain creation by admin."""
    domain_key: str
    name: str
    calendar_url: str
    admin_password: str  # Required
    user_password: Optional[str] = None
    owner_username: Optional[str] = None


class AssignOwnerRequest(BaseModel):
    """Request body for assigning domain owner."""
    user_id: Optional[int] = None  # None to remove owner


@router.delete(
    "/admin/domains/{domain_key}",
    summary="Delete a domain (admin only)",
    description="Delete domain and all associated data (calendar, auth, filters, groups)"
)
async def delete_domain(
    domain_key: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Delete a domain and cascade delete all related records.

    Requires admin password authentication.
    """
    # Get domain
    domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{domain_key}' not found"
        )

    try:
        # Delete calendar if exists (cascade will handle events)
        if domain.calendar_id:
            db.query(Calendar).filter(Calendar.id == domain.calendar_id).delete()

        # Delete domain (cascade will handle groups, filters, etc via FK)
        db.delete(domain)

        db.commit()

        return {
            "success": True,
            "message": f"Domain '{domain_key}' deleted successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete domain: {str(e)}"
        )


@router.post(
    "/admin/domains",
    status_code=status.HTTP_201_CREATED,
    summary="Create domain directly (admin only)",
    description="Allows admin to create a domain without going through the request/approval process"
)
async def create_domain_directly(
    domain_data: CreateDomainRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Create a domain directly without request/approval process.

    Requires admin authentication. Optionally assign to a user as owner.
    """
    from app.models.user import User
    from app.data.domain_auth import encrypt_password

    # Validate domain key format
    if not re.match(r'^[a-z0-9-]+$', domain_data.domain_key):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Domain key must contain only lowercase letters, numbers, and hyphens"
        )

    # Validate URL format
    if not domain_data.calendar_url.startswith(('http://', 'https://')):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Calendar URL must start with http:// or https://"
        )

    # Validate iCal URL by fetching and parsing it
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(domain_data.calendar_url)
            response.raise_for_status()
            ical_content = response.text

        # Parse iCal content to verify it's valid
        success, events, error = parse_ical_content(ical_content)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid iCal URL: {error}"
            )

        if not events:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Calendar URL is valid but contains no events"
            )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to fetch calendar: HTTP {e.response.status_code}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Calendar URL timed out - URL took too long to respond"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to fetch calendar: {str(e)}"
        )
    except HTTPException:
        # Re-raise our own HTTPExceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to validate calendar URL: {str(e)}"
        )

    # Validate admin password length
    if len(domain_data.admin_password) < 4:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Admin password must be at least 4 characters"
        )

    # Check if domain key already exists
    existing_domain = db.query(Domain).filter(Domain.domain_key == domain_data.domain_key).first()
    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Domain key '{domain_data.domain_key}' already exists"
        )

    # Owner assignment removed from creation - domains are created without owner
    # Owner can be assigned later via separate endpoint
    owner_id = None
    owner_username = None

    # Encrypt passwords
    admin_password_hash = encrypt_password(domain_data.admin_password, settings.password_encryption_key)
    user_password_hash = None
    if domain_data.user_password:
        user_password_hash = encrypt_password(domain_data.user_password, settings.password_encryption_key)

    try:
        # 1. Create domain record
        domain = Domain(
            domain_key=domain_data.domain_key,
            name=domain_data.name,
            calendar_url=domain_data.calendar_url,
            owner_id=owner_id,
            admin_password_hash=admin_password_hash,
            user_password_hash=user_password_hash,
            status='active'
        )
        db.add(domain)
        db.flush()  # Get domain.id

        # 2. Create domain calendar
        calendar = Calendar(
            name=domain_data.name,
            source_url=domain_data.calendar_url,
            type="domain",
            user_id=None  # Domain calendars have no user owner
        )
        db.add(calendar)
        db.flush()  # Get calendar.id

        # 3. Link domain to calendar
        domain.calendar_id = calendar.id

        db.commit()
        db.refresh(domain)

        # 4. Sync calendar events from source URL
        from app.services.calendar_service import sync_calendar_events
        try:
            success, event_count, error = await sync_calendar_events(db, calendar)
            if success:
                print(f"✅ Synced {event_count} events for domain '{domain_data.domain_key}'")
            else:
                print(f"⚠️ Failed to sync events for domain '{domain_data.domain_key}': {error}")
        except Exception as e:
            print(f"⚠️ Exception during calendar sync: {e}")

        return {
            "success": True,
            "message": f"Domain '{domain_data.domain_key}' created successfully",
            "domain_key": domain.domain_key,
            "name": domain.name,
            "calendar_url": domain.calendar_url,
            "domain_id": domain.id,
            "calendar_id": calendar.id,
            "owner_username": owner_username,
            "has_admin_password": admin_password_hash is not None,
            "has_user_password": user_password_hash is not None
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create domain: {str(e)}"
        )


@router.get(
    "/admin/users/search",
    summary="Search users (admin only)",
    description="Search for users by username or email"
)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Search for users by username or email.

    Returns matching users for assignment operations.
    """
    from app.models.user import User

    # Search by username or email (case-insensitive)
    users = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) |
        (User.email.ilike(f"%{q}%"))
    ).limit(limit).all()

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
            for user in users
        ]
    }


@router.patch(
    "/admin/domains/{domain_key}/owner",
    summary="Assign domain owner (admin only)",
    description="Assign or remove domain owner"
)
async def assign_domain_owner(
    domain_key: str,
    request: AssignOwnerRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Assign or remove domain owner.

    Set user_id to null to remove owner.
    """
    from app.models.user import User

    # Get domain
    domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{domain_key}' not found"
        )

    # If user_id provided, verify user exists
    owner_username = None
    if request.user_id:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        domain.owner_id = user.id
        owner_username = user.username
    else:
        # Remove owner
        domain.owner_id = None

    try:
        db.commit()
        db.refresh(domain)

        return {
            "success": True,
            "message": f"Owner {'assigned' if request.user_id else 'removed'} successfully",
            "domain_key": domain_key,
            "owner_id": domain.owner_id,
            "owner_username": owner_username
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign owner: {str(e)}"
        )
