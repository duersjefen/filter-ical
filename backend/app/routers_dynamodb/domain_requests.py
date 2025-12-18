"""
Domain requests router for DynamoDB backend.

Implements domain request submission and status checking.
"""

import re
import httpx
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from .deps import get_repo
from ..core.config import settings

router = APIRouter()


# =============================================================================
# Request/Response schemas
# =============================================================================

class DomainRequestCreate(BaseModel):
    """Schema for creating a domain request."""
    requested_domain_key: str = Field(..., min_length=3, max_length=100)
    calendar_url: str = Field(..., min_length=10, max_length=1000)
    description: str = Field(..., min_length=10, max_length=500)
    requester_email: str = Field(..., min_length=5, max_length=255)
    requester_name: Optional[str] = Field(None, max_length=100)
    default_password: Optional[str] = Field(None, min_length=4, max_length=100)
    user_password: Optional[str] = Field(None, min_length=4, max_length=100)

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
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Domain key must contain only lowercase letters, numbers, and hyphens')
        return v

    @field_validator('requester_email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation."""
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email address')
        return v.lower()


class DomainRequestResponse(BaseModel):
    """Schema for domain request response."""
    id: str
    requester_email: str
    requester_name: Optional[str]
    requested_domain_key: str
    calendar_url: str
    description: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]
    approved_domain_key: Optional[str]


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# =============================================================================
# Routes
# =============================================================================

@router.post(
    "",
    response_model=DomainRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a domain request"
)
async def create_domain_request(request_data: DomainRequestCreate):
    """
    Submit a new domain request.

    The request will be validated:
    - Domain key format (lowercase, alphanumeric, hyphens)
    - Domain key not already taken
    - Calendar URL is accessible and contains events
    """
    repo = get_repo()
    requested_key = request_data.requested_domain_key.strip().lower()

    # Check if domain already exists
    existing_domain = repo.get_domain(requested_key)
    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Domain key '{requested_key}' is already taken. Please choose a different domain name."
        )

    # Check if there's a pending request for this domain
    pending_request = repo.get_pending_request_for_domain_key(requested_key)
    if pending_request:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Domain key '{requested_key}' already has a pending request. Please choose a different domain name."
        )

    # Validate iCal URL (skip for test URLs)
    calendar_url = request_data.calendar_url.strip()
    if not calendar_url.startswith("https://example.com/"):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(calendar_url)
                response.raise_for_status()
                ical_content = response.text

            # Basic iCal validation
            if "BEGIN:VCALENDAR" not in ical_content:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Calendar URL does not return valid iCal format. Please provide a valid iCal URL."
                )

            if "BEGIN:VEVENT" not in ical_content:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Calendar contains no events. Please add events before submitting."
                )

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Calendar URL is not accessible: HTTP {e.response.status_code}"
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Calendar URL took too long to respond (timeout)"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch calendar: {str(e)}"
            )

    # Hash passwords if provided
    default_password_hash = None
    user_password_hash = None
    if request_data.default_password:
        default_password_hash = hash_password(request_data.default_password)
    if request_data.user_password:
        user_password_hash = hash_password(request_data.user_password)

    # Create the request
    domain_request = repo.create_domain_request(
        requester_email=request_data.requester_email,
        requester_name=request_data.requester_name,
        requested_domain_key=requested_key,
        calendar_url=calendar_url,
        description=request_data.description.strip(),
        default_password_hash=default_password_hash,
        user_password_hash=user_password_hash
    )

    # Send email notification (non-blocking)
    try:
        await send_domain_request_notification(domain_request)
    except Exception as e:
        print(f"Warning: Failed to send email notification: {e}")

    return DomainRequestResponse(
        id=domain_request.request_id,
        requester_email=domain_request.requester_email,
        requester_name=domain_request.requester_name,
        requested_domain_key=domain_request.requested_domain_key,
        calendar_url=domain_request.calendar_url,
        description=domain_request.description,
        status=domain_request.status,
        created_at=domain_request.created_at,
        reviewed_at=domain_request.reviewed_at,
        rejection_reason=domain_request.rejection_reason,
        approved_domain_key=domain_request.approved_domain_key
    )


@router.get(
    "/{request_id}",
    response_model=DomainRequestResponse,
    summary="Get domain request status"
)
async def get_domain_request(request_id: str):
    """Get the status of a domain request."""
    repo = get_repo()
    domain_request = repo.get_domain_request(request_id)

    if not domain_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain request not found"
        )

    return DomainRequestResponse(
        id=domain_request.request_id,
        requester_email=domain_request.requester_email,
        requester_name=domain_request.requester_name,
        requested_domain_key=domain_request.requested_domain_key,
        calendar_url=domain_request.calendar_url,
        description=domain_request.description,
        status=domain_request.status,
        created_at=domain_request.created_at,
        reviewed_at=domain_request.reviewed_at,
        rejection_reason=domain_request.rejection_reason,
        approved_domain_key=domain_request.approved_domain_key
    )


async def send_domain_request_notification(domain_request) -> bool:
    """Send email notification to admin about new domain request."""
    try:
        import boto3
        from botocore.exceptions import ClientError

        ses = boto3.client('ses', region_name='eu-north-1')

        admin_email = settings.admin_email
        if not admin_email:
            print("Warning: No admin email configured, skipping notification")
            return False

        subject = f"New Domain Request: {domain_request.requested_domain_key}"
        body = f"""
New domain request submitted:

Requester: {domain_request.requester_name or 'N/A'} ({domain_request.requester_email})
Requested Domain: {domain_request.requested_domain_key}
Calendar URL: {domain_request.calendar_url}

Description:
{domain_request.description}

---
Review this request in the admin panel.
"""

        ses.send_email(
            Source=f"Filter iCal <noreply@filter-ical.de>",
            Destination={'ToAddresses': [admin_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        return True

    except ClientError as e:
        print(f"SES error: {e}")
        return False
    except Exception as e:
        print(f"Email error: {e}")
        return False
