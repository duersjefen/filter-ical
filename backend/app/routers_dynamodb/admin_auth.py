"""
Admin authentication router for DynamoDB backend.

Handles login and password reset using DynamoDB repository.
"""

import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext

from ..core.auth import create_admin_token
from ..core.config import settings
from ..core.messages import ErrorMessages, SuccessMessages, InfoMessages
from ..db.repository import get_repository
from ..db.models import Admin

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminLoginRequest(BaseModel):
    """Request body for admin login."""
    password: str


class AdminLoginResponse(BaseModel):
    """Response for successful admin login."""
    token: str
    expires_in_days: int


@router.post(
    "/admin/login",
    response_model=AdminLoginResponse,
    summary="Admin login to get JWT token",
    description="Authenticate with admin password and receive a JWT token valid for 30 days"
)
async def admin_login(request: AdminLoginRequest):
    """
    Authenticate with admin password and get a JWT token.
    Uses DynamoDB for admin settings storage.
    """
    repo = get_repository()

    # Get admin from DynamoDB (using configured admin email as key)
    admin = repo.get_admin(settings.admin_email)

    if not admin:
        # First-time login: verify against .env password and create admin
        is_password_correct = secrets.compare_digest(
            request.password.encode("utf-8"),
            settings.admin_password.encode("utf-8")
        )

        if is_password_correct:
            # Create admin in DynamoDB
            admin = Admin(
                email=settings.admin_email,
                password_hash=pwd_context.hash(settings.admin_password)
            )
            repo.save_admin(admin)
    else:
        # Verify password against stored hash
        is_password_correct = pwd_context.verify(request.password, admin.password_hash)

    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.INVALID_ADMIN_PASSWORD
        )

    # Generate JWT token with 30-day expiry
    token = create_admin_token(expiry_days=30)

    return AdminLoginResponse(
        token=token,
        expires_in_days=30
    )


@router.post(
    "/admin/request-password-reset",
    summary="Request admin password reset email",
    description="Send password reset link to configured admin email address"
)
async def request_admin_password_reset():
    """
    Request admin password reset email.
    Sends reset link to ADMIN_EMAIL.
    Always returns success to prevent email enumeration.
    """
    try:
        # Check if admin email is configured
        if not settings.admin_email:
            return {
                "success": True,
                "message": InfoMessages.PASSWORD_RESET_EMAIL_SENT
            }

        repo = get_repository()

        # Create reset token (stored in admin record)
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=1)

        # Update admin with reset token
        admin = repo.get_admin(settings.admin_email)
        if not admin:
            # Create admin if doesn't exist (with placeholder password)
            admin = Admin(
                email=settings.admin_email,
                password_hash=pwd_context.hash(settings.admin_password)
            )

        admin.reset_token = token
        admin.reset_token_expires = expires
        repo.save_admin(admin)

        # Send email
        from ..services.email_service import send_admin_password_reset_email
        try:
            await send_admin_password_reset_email(
                email=settings.admin_email,
                reset_token=token
            )
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            # Still return success to prevent enumeration

        return {
            "success": True,
            "message": InfoMessages.PASSWORD_RESET_EMAIL_SENT
        }

    except Exception as e:
        print(f"Password reset request error: {e}")
        return {
            "success": True,
            "message": InfoMessages.PASSWORD_RESET_EMAIL_SENT
        }


@router.post(
    "/admin/reset-password",
    summary="Reset admin password with token",
    description="Reset admin password using token from email"
)
async def reset_admin_password(reset_data: dict):
    """
    Reset admin password using token from email.
    Validates token and updates password in DynamoDB.
    """
    # Validate request
    if "token" not in reset_data or "new_password" not in reset_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.TOKEN_AND_PASSWORD_REQUIRED
        )

    token_string = reset_data["token"]
    new_password = reset_data["new_password"]

    # Validate password length
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorMessages.PASSWORD_MIN_LENGTH.format(min_length=8)
        )

    repo = get_repository()

    # Find admin by reset token
    admin = repo.get_admin_by_reset_token(token_string)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.INVALID_OR_EXPIRED_RESET_TOKEN
        )

    # Check if token is expired
    if admin.reset_token_expires and admin.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.RESET_TOKEN_EXPIRED
        )

    try:
        # Update password
        admin.password_hash = pwd_context.hash(new_password)

        # Clear reset token
        admin.reset_token = None
        admin.reset_token_expires = None

        repo.save_admin(admin)

        return {
            "success": True,
            "message": SuccessMessages.PASSWORD_RESET_COMPLETE
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.PASSWORD_RESET_FAILED.format(error=str(e))
        )
