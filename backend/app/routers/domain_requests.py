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
from ..models.domain_request import DomainRequest, RequestStatus
from ..services.email_service import send_domain_request_notification

router = APIRouter()


# Pydantic models matching OpenAPI schema
class DomainRequestCreate(BaseModel):
    """Schema for creating a domain request - matches OpenAPI spec."""
    username: str = Field(..., min_length=3, max_length=50)
    calendar_url: str = Field(..., min_length=10, max_length=1000)
    description: str = Field(..., min_length=10, max_length=500)

    @field_validator('calendar_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL looks like a valid iCal URL."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Calendar URL must start with http:// or https://')
        return v


class DomainRequestResponse(BaseModel):
    """Schema for domain request response - matches OpenAPI spec."""
    id: int
    username: str
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
        # Create domain request
        domain_request = DomainRequest(
            username=request_data.username.strip(),
            calendar_url=request_data.calendar_url.strip(),
            description=request_data.description.strip(),
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
