"""
Domain requests router - Public endpoints for users to submit custom domain requests.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from ..core.database import get_db
from ..core.config import settings
from ..models.domain_request import DomainRequest, RequestStatus
from ..services.email_service import send_domain_request_notification
from ..data.domain_auth import encrypt_password

router = APIRouter()


# Pydantic models matching OpenAPI schema
class DomainRequestCreate(BaseModel):
    """Schema for creating a domain request - matches OpenAPI spec."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=255)
    requested_domain_key: str = Field(..., min_length=3, max_length=100)
    calendar_url: str = Field(..., min_length=10, max_length=1000)
    description: str = Field(..., min_length=10, max_length=500)
    default_password: Optional[str] = Field(None, min_length=4, max_length=100)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Invalid email format')
        return v

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
    description="Users can request their own custom domain calendar to be set up"
)
async def create_domain_request(
    request_data: DomainRequestCreate,
    db: Session = Depends(get_db)
) -> DomainRequest:
    """
    Create a new domain request.

    The request will be pending and an email notification will be sent to the admin.
    """
    try:
        # Encrypt the default password (if provided)
        encrypted_password = None
        if request_data.default_password:
            encrypted_password = encrypt_password(
                request_data.default_password,
                settings.password_encryption_key
            )

        # Create domain request
        domain_request = DomainRequest(
            username=request_data.username.strip(),
            email=request_data.email.strip().lower(),
            requested_domain_key=request_data.requested_domain_key.strip().lower(),
            calendar_url=request_data.calendar_url.strip(),
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

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create domain request: {str(e)}"
        )
