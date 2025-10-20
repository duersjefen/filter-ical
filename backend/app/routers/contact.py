"""
Contact form router - IMPERATIVE SHELL.

Handles contact form submissions and sends emails to admin.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from ..core.rate_limit import limiter
from ..services.email_service import send_contact_form_email

router = APIRouter()


class ContactRequest(BaseModel):
    """Contact form submission schema."""
    name: str = Field(..., min_length=2, max_length=100, description="Sender's name")
    email: EmailStr = Field(..., max_length=200, description="Sender's email for reply")
    subject: str = Field(..., min_length=5, max_length=200, description="Subject line for the message")
    message: str = Field(..., min_length=20, max_length=2000, description="Detailed message content")


@router.post(
    "/contact",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
@limiter.limit("5/hour")  # Limit to 5 contact form submissions per hour per IP
async def submit_contact_form(
    request: Request,
    contact_data: ContactRequest
):
    """
    Submit contact form.

    Sends an email to the admin with the contact message.
    Rate limited to prevent spam (5 requests per hour per IP).
    """
    # Send email to admin
    success, error_msg = await send_contact_form_email(
        name=contact_data.name,
        email=contact_data.email,
        subject=contact_data.subject,
        message=contact_data.message
    )

    if not success:
        # Log the error but don't expose details to user
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message. Please try again later or contact us directly at info@paiss.me"
        )

    return {
        "success": True,
        "message": "Thank you for your message! We'll get back to you soon."
    }
