"""
Admin domain requests router - Approve/reject domain requests.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional

from ..core.database import get_db
from ..core.auth import verify_admin_auth
from ..models.domain_request import DomainRequest, RequestStatus
from ..models.calendar import Calendar
from ..models.domain import Domain
from ..routers.domain_requests import DomainRequestResponse

router = APIRouter()


class ApproveRequestBody(BaseModel):
    """Optional body for approve request."""
    domain_key: Optional[str] = None
    send_email: bool = True
    message: Optional[str] = None


class RejectRequestBody(BaseModel):
    """Optional body for reject request."""
    reason: Optional[str] = None
    send_email: bool = True


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
