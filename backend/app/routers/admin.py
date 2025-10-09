"""
Admin router - Password-protected endpoints for managing domain requests.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import re

from ..core.database import get_db
from ..core.auth import verify_admin_password, create_admin_token, verify_admin_auth
from ..models.domain_request import DomainRequest, RequestStatus
from ..models.calendar import Calendar
from ..models.domain import Domain
from ..routers.domain_requests import DomainRequestResponse
import secrets

router = APIRouter()


class AdminLoginRequest(BaseModel):
    """Request body for admin login."""
    password: str


class AdminLoginResponse(BaseModel):
    """Response for successful admin login."""
    token: str
    expires_in_days: int


class ApproveRequestBody(BaseModel):
    """Optional body for approve request."""
    domain_key: Optional[str] = None
    send_email: bool = True
    message: Optional[str] = None


class RejectRequestBody(BaseModel):
    """Optional body for reject request."""
    reason: Optional[str] = None
    send_email: bool = True


def generate_domain_key(username: str, db: Session) -> str:
    """
    Generate a unique domain key from username.

    Args:
        username: User's username
        db: Database session

    Returns:
        Unique domain key
    """
    # Sanitize username to valid domain key format
    base_key = re.sub(r'[^a-z0-9_-]', '_', username.lower())

    # Ensure uniqueness by checking domains table
    domain_key = base_key
    counter = 1
    while db.query(Domain).filter(Domain.domain_key == domain_key).first():
        domain_key = f"{base_key}_{counter}"
        counter += 1

    return domain_key


@router.post(
    "/admin/login",
    response_model=AdminLoginResponse,
    summary="Admin login to get JWT token",
    description="Authenticate with admin password and receive a JWT token valid for 30 days"
)
async def admin_login(request: AdminLoginRequest):
    """
    Authenticate with admin password and get a JWT token.

    Returns a token that can be used for 30 days without re-entering the password.
    """
    from ..core.config import settings

    # Verify password using constant-time comparison
    is_password_correct = secrets.compare_digest(
        request.password.encode("utf-8"),
        settings.admin_password.encode("utf-8")
    )

    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password"
        )

    # Generate JWT token with 30-day expiry
    token = create_admin_token(expiry_days=30)

    return AdminLoginResponse(
        token=token,
        expires_in_days=30
    )


@router.get(
    "/admin/domain-requests",
    response_model=List[DomainRequestResponse],
    summary="List all domain requests (admin only)",
    description="Get all domain requests with optional status filtering"
)
async def list_domain_requests(
    status_filter: Optional[RequestStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
) -> List[DomainRequest]:
    """
    List all domain requests (admin only).

    Requires JWT token or password authentication.
    """
    query = db.query(DomainRequest)

    if status_filter:
        query = query.filter(DomainRequest.status == status_filter)

    # Order by created_at DESC (newest first)
    requests = query.order_by(DomainRequest.created_at.desc()).all()

    return requests


@router.patch(
    "/admin/domain-requests/{request_id}/approve",
    summary="Approve a domain request (admin only)",
    description="Approve the request and automatically create domain calendar"
)
async def approve_domain_request(
    request_id: int,
    body: Optional[ApproveRequestBody] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Approve a domain request and create the domain calendar.

    Requires admin password authentication.
    """
    # Get request
    domain_request = db.query(DomainRequest).filter(DomainRequest.id == request_id).first()
    if not domain_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain request not found"
        )

    # Check if already reviewed
    if domain_request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {domain_request.status.value}"
        )

    # Use requested domain key or allow admin override
    if body and body.domain_key:
        domain_key = body.domain_key
    else:
        domain_key = domain_request.requested_domain_key

    # Check if domain key already exists
    existing_domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Domain key '{domain_key}' already exists"
        )

    try:
        # 1. Create domain record first
        domain = Domain(
            domain_key=domain_key,
            name=f"{domain_request.username}'s Calendar",
            calendar_url=domain_request.calendar_url,
            owner_id=domain_request.user_id,  # Assign requesting user as owner
            admin_password_hash=domain_request.default_password,  # Already encrypted
            user_password_hash=None,
            status='active'
        )
        db.add(domain)
        db.flush()  # Get domain.id before creating calendar

        # 2. Create domain calendar
        calendar = Calendar(
            name=f"{domain_request.username}'s Calendar",
            source_url=domain_request.calendar_url,
            type="domain",
            user_id=None  # Domain calendars have no owner
        )
        db.add(calendar)
        db.flush()  # Get calendar.id

        # 3. Link domain to calendar
        domain.calendar_id = calendar.id

        # 4. Set initial password (already encrypted from domain request)
        domain.admin_password_hash = domain_request.default_password
        domain.user_password_hash = None

        # 5. Update request status
        domain_request.status = RequestStatus.APPROVED
        domain_request.reviewed_at = func.now()
        domain_request.domain_key = domain_key

        db.commit()
        db.refresh(domain)

        # 6. Sync calendar events from source URL
        from ..services.calendar_service import sync_calendar_events
        try:
            success, event_count, error = await sync_calendar_events(db, calendar)
            if success:
                print(f"✅ Synced {event_count} events for domain '{domain_key}'")
            else:
                print(f"⚠️ Failed to sync events for domain '{domain_key}': {error}")
        except Exception as e:
            print(f"⚠️ Exception during calendar sync: {e}")

        # 7. Send email notification if requested
        if body and body.send_email:
            from ..services.email_service import send_domain_approval_email
            try:
                custom_message = body.message if body and body.message else None
                await send_domain_approval_email(domain_request, domain_key, custom_message)
            except Exception as e:
                # Log but don't fail approval if email fails
                print(f"Warning: Failed to send approval email: {e}")

        return {
            "success": True,
            "message": "Domain request approved and domain created",
            "domain_key": domain_key,
            "calendar_id": calendar.id,
            "domain_id": domain.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve request: {str(e)}"
        )


@router.patch(
    "/admin/domain-requests/{request_id}/reject",
    summary="Reject a domain request (admin only)",
    description="Reject the domain request with optional reason"
)
async def reject_domain_request(
    request_id: int,
    body: Optional[RejectRequestBody] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Reject a domain request.

    Requires admin password authentication.
    """
    # Get request
    domain_request = db.query(DomainRequest).filter(DomainRequest.id == request_id).first()
    if not domain_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain request not found"
        )

    # Check if already reviewed
    if domain_request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {domain_request.status.value}"
        )

    try:
        # Update request status
        domain_request.status = RequestStatus.REJECTED
        domain_request.reviewed_at = func.now()

        rejection_reason = ""
        if body and body.reason:
            domain_request.rejection_reason = body.reason
            rejection_reason = body.reason

        db.commit()

        # Send email notification if requested
        if body and body.send_email and rejection_reason:
            from ..services.email_service import send_domain_rejection_email
            try:
                await send_domain_rejection_email(domain_request, rejection_reason)
            except Exception as e:
                # Log but don't fail rejection if email fails
                print(f"Warning: Failed to send rejection email: {e}")

        return {
            "success": True,
            "message": "Domain request rejected"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject request: {str(e)}"
        )


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


class CreateDomainRequest(BaseModel):
    """Request body for direct domain creation by admin."""
    domain_key: str
    name: str
    calendar_url: str
    admin_password: str  # Required
    user_password: Optional[str] = None
    owner_username: Optional[str] = None


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
    from app.core.config import settings

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


class AssignOwnerRequest(BaseModel):
    """Request body for assigning domain owner."""
    user_id: Optional[int] = None  # None to remove owner


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
