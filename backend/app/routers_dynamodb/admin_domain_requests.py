"""
Admin domain requests router for DynamoDB backend.

Implements admin management of domain requests.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional

from .deps import get_repo, require_admin_auth
from ..db.models import Domain, DomainGroup
from .admin_domain_configs import fetch_and_parse_ical

router = APIRouter()


# =============================================================================
# Request/Response schemas
# =============================================================================

class DomainRequestListItem(BaseModel):
    """Schema for domain request in list."""
    id: str
    requester_email: str
    requester_name: Optional[str]
    requested_domain_key: str
    calendar_url: str
    description: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]


class ApproveRequest(BaseModel):
    """Schema for approving a domain request."""
    domain_key: Optional[str] = None  # If different from requested


class RejectRequest(BaseModel):
    """Schema for rejecting a domain request."""
    reason: str


# =============================================================================
# Routes
# =============================================================================

@router.get(
    "/admin/domain-requests",
    response_model=list[DomainRequestListItem],
    summary="List all domain requests"
)
async def list_domain_requests(
    status_filter: Optional[str] = None,
    _admin: str = Depends(require_admin_auth)
):
    """List all domain requests, optionally filtered by status."""
    repo = get_repo()
    requests = repo.list_domain_requests(status=status_filter)

    return [
        DomainRequestListItem(
            id=req.request_id,
            requester_email=req.requester_email,
            requester_name=req.requester_name,
            requested_domain_key=req.requested_domain_key,
            calendar_url=req.calendar_url,
            description=req.description,
            status=req.status,
            created_at=req.created_at,
            reviewed_at=req.reviewed_at
        )
        for req in requests
    ]


@router.get(
    "/admin/domain-requests/{request_id}",
    summary="Get domain request details"
)
async def get_domain_request(
    request_id: str,
    _admin: str = Depends(require_admin_auth)
):
    """Get full details of a domain request."""
    repo = get_repo()
    request = repo.get_domain_request(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain request not found"
        )

    return {
        "id": request.request_id,
        "requester_email": request.requester_email,
        "requester_name": request.requester_name,
        "requested_domain_key": request.requested_domain_key,
        "calendar_url": request.calendar_url,
        "description": request.description,
        "status": request.status,
        "created_at": request.created_at.isoformat(),
        "reviewed_at": request.reviewed_at.isoformat() if request.reviewed_at else None,
        "rejection_reason": request.rejection_reason,
        "approved_domain_key": request.approved_domain_key,
        "has_admin_password": request.default_password_hash is not None,
        "has_user_password": request.user_password_hash is not None
    }


@router.patch(
    "/admin/domain-requests/{request_id}/approve",
    summary="Approve a domain request"
)
async def approve_domain_request(
    request_id: str,
    data: ApproveRequest = None,
    _admin: str = Depends(require_admin_auth)
):
    """
    Approve a domain request and create the domain.

    This will:
    1. Create the domain with the requested settings
    2. Fetch events from the calendar URL
    3. Update the request status to 'approved'
    """
    repo = get_repo()
    request = repo.get_domain_request(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain request not found"
        )

    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve request with status '{request.status}'"
        )

    # Determine final domain key
    domain_key = (data.domain_key if data and data.domain_key else request.requested_domain_key).lower()

    # Check if domain already exists
    existing = repo.get_domain(domain_key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Domain key '{domain_key}' already exists"
        )

    # Create the domain
    domain = Domain(
        domain_key=domain_key,
        name=domain_key.replace("-", " ").title(),
        calendar_url=request.calendar_url,
        status="active",
        admin_password_hash=request.default_password_hash,
        user_password_hash=request.user_password_hash,
        groups=[],  # Start with no custom groups (auto-groups will be created on first load)
        recurring_assignments={}
    )

    repo.save_domain(domain)

    # Fetch and import events
    event_count = 0
    try:
        from ..db.models import Event
        events_data = await fetch_and_parse_ical(request.calendar_url)

        event_objs = []
        for e in events_data:
            event_objs.append(Event(
                domain_key=domain_key,
                uid=e["uid"],
                start_date=e.get("start_date", ""),
                title=e["title"],
                start_time=e.get("start_time", datetime.utcnow()),
                end_time=e.get("end_time"),
                description=e.get("description"),
                location=e.get("location"),
            ))

        if event_objs:
            repo.save_events(event_objs)
            event_count = len(event_objs)

    except Exception as e:
        # Don't fail if event import fails - domain is still created
        print(f"Warning: Failed to import events: {e}")

    # Update request status
    repo.update_domain_request_status(
        request_id=request_id,
        status="approved",
        approved_domain_key=domain_key
    )

    return {
        "success": True,
        "message": f"Domain '{domain_key}' created successfully",
        "domain_key": domain_key,
        "event_count": event_count
    }


@router.patch(
    "/admin/domain-requests/{request_id}/reject",
    summary="Reject a domain request"
)
async def reject_domain_request(
    request_id: str,
    data: RejectRequest,
    _admin: str = Depends(require_admin_auth)
):
    """Reject a domain request with a reason."""
    repo = get_repo()
    request = repo.get_domain_request(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain request not found"
        )

    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject request with status '{request.status}'"
        )

    # Update request status
    repo.update_domain_request_status(
        request_id=request_id,
        status="rejected",
        rejection_reason=data.reason
    )

    return {
        "success": True,
        "message": "Domain request rejected"
    }


@router.delete(
    "/admin/domain-requests/{request_id}",
    summary="Delete a domain request"
)
async def delete_domain_request(
    request_id: str,
    _admin: str = Depends(require_admin_auth)
):
    """Delete a domain request (any status)."""
    repo = get_repo()
    request = repo.get_domain_request(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain request not found"
        )

    repo.delete_domain_request(request_id)

    return {
        "success": True,
        "message": "Domain request deleted"
    }
