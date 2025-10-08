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


class RejectRequestBody(BaseModel):
    """Optional body for reject request."""
    reason: Optional[str] = None


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

        # 4. Create DomainAuth record (for password authentication system)
        from ..models.domain_auth import DomainAuth
        domain_auth = DomainAuth(
            domain_key=domain_key,
            calendar_id=calendar.id,
            admin_password_hash=domain_request.default_password,  # Already encrypted
            user_password_hash=None
        )
        db.add(domain_auth)

        # 5. Update request status
        domain_request.status = RequestStatus.APPROVED
        domain_request.reviewed_at = func.now()
        domain_request.domain_key = domain_key

        db.commit()
        db.refresh(domain)

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
        if body and body.reason:
            domain_request.rejection_reason = body.reason

        db.commit()

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
        # Delete DomainAuth record
        from ..models.domain_auth import DomainAuth
        db.query(DomainAuth).filter(DomainAuth.domain_key == domain_key).delete()

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
