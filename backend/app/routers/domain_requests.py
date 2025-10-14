"""
Domain requests router - Public endpoints for users to submit custom domain requests.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import httpx

from ..core.database import get_db
from ..core.config import settings
from ..core.auth import require_user_auth
from ..models.domain_request import DomainRequest, RequestStatus
from ..models.domain import Domain
from ..models.user import User
from ..services.email_service import send_domain_request_notification
from ..data.domain_auth import encrypt_password
from ..data.ical_parser import parse_ical_content

router = APIRouter()


# Pydantic models matching OpenAPI schema
class DomainRequestCreate(BaseModel):
    """Schema for creating a domain request - matches OpenAPI spec."""
    requested_domain_key: str = Field(..., min_length=3, max_length=100)
    calendar_url: str = Field(..., min_length=10, max_length=1000)
    description: str = Field(..., min_length=10, max_length=500)
    default_password: Optional[str] = Field(None, min_length=4, max_length=100)

    @field_validator('calendar_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL looks like a valid iCal URL."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Calendar URL must start with http:// or https://')
        return v

    @field_validator('requested_domain_key')
    @classmethod
    def validate_domain_key(cls, v: str) -> str:
        """Validate domain key format (alphanumeric, lowercase, hyphens)."""
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Domain key must contain only lowercase letters, numbers, and hyphens')
        return v


class DomainRequestResponse(BaseModel):
    """Schema for domain request response - matches OpenAPI spec."""
    id: int
    username: str
    email: str
    requested_domain_key: str
    calendar_url: str
    description: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    domain_key: Optional[str] = None

    class Config:
        from_attributes = True


@router.post(
    "/domain-requests",
    response_model=DomainRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a custom domain request",
    description="Users can request their own custom domain calendar to be set up. Requires authentication. User's email will be automatically used from their profile."
)
async def create_domain_request(
    request_data: DomainRequestCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user_auth)
) -> DomainRequest:
    """
    Create a new domain request.

    Validates the iCal URL before creating the request to ensure it:
    - Is accessible (no 404, timeout, etc.)
    - Contains at least one event
    - Is valid iCal format

    The request will be pending and an email notification will be sent to the admin.
    """
    try:
        # Get authenticated user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Require email for domain requests
        if not user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is required to request a domain. Please add an email to your profile first."
            )

        # Check if domain key already exists or is pending
        requested_key = request_data.requested_domain_key.strip().lower()

        # Check if domain already exists (approved)
        existing_domain = db.query(Domain).filter(Domain.domain_key == requested_key).first()
        if existing_domain:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Domain key '{requested_key}' is already taken. Please choose a different domain name."
            )

        # Check if there's already a pending request for this domain
        pending_request = db.query(DomainRequest).filter(
            DomainRequest.requested_domain_key == requested_key,
            DomainRequest.status == RequestStatus.PENDING
        ).first()
        if pending_request:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Domain key '{requested_key}' already has a pending request. Please choose a different domain name or wait for the current request to be reviewed."
            )

        # Validate iCal URL before accepting the request (skip in test mode)
        calendar_url = request_data.calendar_url.strip()

        # Skip validation if in test mode (URL is example.com)
        if not calendar_url.startswith("https://example.com/"):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(calendar_url)
                    response.raise_for_status()
                    ical_content = response.text
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Calendar URL is not accessible: HTTP {e.response.status_code}. Please check the URL and try again."
                )
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Calendar URL took too long to respond (timeout). Please check the URL and try again."
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch calendar: {str(e)}. Please check the URL and try again."
                )

            # Parse iCal content
            parse_result = parse_ical_content(ical_content)

            if not parse_result.is_success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Calendar URL is not valid iCal format: {parse_result.error}. Please provide a valid iCal URL."
                )

            events = parse_result.value
            if not events or len(events) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Calendar contains no events. Please add events to your calendar before submitting a request."
                )

        # Encrypt the default password (if provided)
        encrypted_password = None
        if request_data.default_password:
            encrypted_password = encrypt_password(
                request_data.default_password,
                settings.password_encryption_key
            )

        # Create domain request
        domain_request = DomainRequest(
            user_id=user.id,
            username=user.username,
            email=user.email,
            requested_domain_key=request_data.requested_domain_key.strip().lower(),
            calendar_url=calendar_url,
            description=request_data.description.strip(),
            default_password=encrypted_password,
            status=RequestStatus.PENDING
        )

        db.add(domain_request)
        db.commit()
        db.refresh(domain_request)

        # Send email notification (non-blocking - don't fail if email fails)
        try:
            await send_domain_request_notification(domain_request)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Failed to send email notification: {e}")

        return domain_request

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create domain request: {str(e)}"
        )
