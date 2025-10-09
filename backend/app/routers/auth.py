"""
Authentication router - Password reset endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.database import get_db
from ..core.rate_limit import limiter
from ..models.user import User
from ..services import auth_service
from ..services.email_service import send_password_reset_email

router = APIRouter()


class PasswordResetRequestBody(BaseModel):
    """Request body for password reset request."""
    email: str


class PasswordResetBody(BaseModel):
    """Request body for password reset."""
    token: str
    new_password: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


@router.post(
    "/api/auth/request-reset",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Send password reset email to user"
)
@limiter.limit("3/minute")
async def request_password_reset(
    request: Request,
    body: PasswordResetRequestBody,
    db: Session = Depends(get_db)
):
    """
    Request password reset email.

    Always returns success to prevent email enumeration attacks.
    """
    # Find user by email
    user = db.query(User).filter(User.email == body.email).first()

    if user and user.password_hash:  # Only for users with passwords
        # Generate reset token
        reset_token = auth_service.generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = auth_service.create_reset_token_expiry(hours=1)

        db.commit()

        # Send email
        await send_password_reset_email(user.email, user.username, reset_token)

    # Always return success (security: don't reveal if email exists)
    return MessageResponse(message="If that email is registered, a reset link has been sent")


@router.post(
    "/api/auth/reset-password",
    response_model=MessageResponse,
    summary="Reset password with token",
    description="Reset user password using token from email"
)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    body: PasswordResetBody,
    db: Session = Depends(get_db)
):
    """Reset password using token."""
    # Find user with this token
    user = db.query(User).filter(User.reset_token == body.token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Validate token
    if not auth_service.is_reset_token_valid(user, body.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Validate new password
    is_valid, error_msg = auth_service.is_valid_password(body.new_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Update password and clear reset token
    user.password_hash = auth_service.hash_password(body.new_password)
    user.reset_token = None
    user.reset_token_expires = None

    db.commit()

    return MessageResponse(message="Password reset successfully")


@router.get(
    "/api/auth/verify-token/{token}",
    response_model=MessageResponse,
    summary="Verify reset token",
    description="Check if reset token is valid"
)
async def verify_reset_token(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    """Verify if reset token is valid."""
    user = db.query(User).filter(User.reset_token == token).first()

    if not user or not auth_service.is_reset_token_valid(user, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    return MessageResponse(message="Token is valid")
