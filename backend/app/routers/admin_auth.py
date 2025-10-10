"""
Admin authentication router - Login and password reset endpoints.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import secrets

from ..core.database import get_db
from ..core.auth import create_admin_token
from ..core.config import settings
from ..models.admin_password_reset import AdminPasswordResetToken

router = APIRouter()


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
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with admin password and get a JWT token.

    Returns a token that can be used for 30 days without re-entering the password.
    Password is stored in database (admin_settings table).
    """
    from ..models.admin import AdminSettings
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Get admin password from database
    admin_settings = db.query(AdminSettings).filter(AdminSettings.id == 1).first()

    if not admin_settings:
        # First-time login: seed password from .env to database
        # Verify against .env password
        is_password_correct = secrets.compare_digest(
            request.password.encode("utf-8"),
            settings.admin_password.encode("utf-8")
        )

        if is_password_correct:
            # Seed database with .env password
            admin_settings = AdminSettings(
                id=1,
                password_hash=pwd_context.hash(settings.admin_password)
            )
            db.add(admin_settings)
            db.commit()
    else:
        # Verify password against database hash
        is_password_correct = pwd_context.verify(request.password, admin_settings.password_hash)

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


@router.post(
    "/admin/request-password-reset",
    summary="Request admin password reset email",
    description="Send password reset link to configured admin email address"
)
async def request_admin_password_reset(db: Session = Depends(get_db)):
    """
    Request admin password reset email.

    Sends reset link to ADMIN_EMAIL (info@paiss.me).
    Always returns success to prevent email enumeration.
    """
    try:
        # Check if admin email is configured
        if not settings.admin_email:
            # Still return success to prevent enumeration
            return {
                "success": True,
                "message": "If an admin account exists, a password reset email has been sent"
            }

        # Create reset token
        reset_token = AdminPasswordResetToken.create_token()
        db.add(reset_token)
        db.commit()
        db.refresh(reset_token)

        # Send email
        from ..services.email_service import send_admin_password_reset_email
        try:
            await send_admin_password_reset_email(
                email=settings.admin_email,
                reset_token=reset_token.token
            )
        except Exception as e:
            print(f"⚠️ Failed to send password reset email: {e}")
            # Still return success to prevent enumeration

        return {
            "success": True,
            "message": "If an admin account exists, a password reset email has been sent"
        }

    except Exception as e:
        print(f"⚠️ Password reset request error: {e}")
        # Still return success to prevent enumeration
        return {
            "success": True,
            "message": "If an admin account exists, a password reset email has been sent"
        }


@router.post(
    "/admin/reset-password",
    summary="Reset admin password with token",
    description="Reset admin password using token from email"
)
async def reset_admin_password(
    reset_data: dict,
    db: Session = Depends(get_db)
):
    """
    Reset admin password using token from email.

    Validates token and updates ADMIN_PASSWORD environment variable hint.
    """
    # Validate request
    if "token" not in reset_data or "new_password" not in reset_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="token and new_password are required"
        )

    token_string = reset_data["token"]
    new_password = reset_data["new_password"]

    # Validate password length
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long"
        )

    # Find token
    token = db.query(AdminPasswordResetToken).filter(
        AdminPasswordResetToken.token == token_string
    ).first()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Validate token
    if not token.is_valid:
        if token.used:
            detail = "Reset token has already been used"
        else:
            detail = "Reset token has expired"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

    try:
        from ..models.admin import AdminSettings
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Get or create admin settings
        admin_settings = db.query(AdminSettings).filter(AdminSettings.id == 1).first()

        if not admin_settings:
            # Create admin settings if it doesn't exist (shouldn't happen after migration)
            admin_settings = AdminSettings(
                id=1,
                password_hash=pwd_context.hash(new_password)
            )
            db.add(admin_settings)
        else:
            # Update password hash in database
            admin_settings.password_hash = pwd_context.hash(new_password)

        # Mark token as used
        token.used = 1

        # Commit all changes
        db.commit()

        return {
            "success": True,
            "message": "Admin password reset successfully. Your new password is now active."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )
