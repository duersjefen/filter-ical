"""
Users router - User account management (register, login, profile).

CONTRACT-DRIVEN: Implementation matches OpenAPI specification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..core.database import get_db
from ..core.auth import get_current_user_id, require_user_auth
from ..models.user import User
from ..services import auth_service

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================

class UserRegisterRequest(BaseModel):
    """Request body for user registration."""
    username: str
    email: Optional[str] = None
    password: Optional[str] = None


class UserLoginRequest(BaseModel):
    """Request body for user login."""
    username: str
    password: Optional[str] = None


class UserResponse(BaseModel):
    """User profile response."""
    id: int
    username: str
    email: Optional[str]
    role: str
    has_password: bool  # True if user has set a password
    created_at: str


class AuthTokenResponse(BaseModel):
    """Authentication token response."""
    token: str
    expires_in_days: int
    user: UserResponse


class UpdateProfileRequest(BaseModel):
    """Request body for updating user profile."""
    email: Optional[str] = None
    password: Optional[str] = None
    current_password: Optional[str] = None  # Required if changing password


# =============================================================================
# User Registration
# =============================================================================

@router.post(
    "/api/users/register",
    response_model=AuthTokenResponse,
    summary="Register new user account",
    description="Create user account. Email and password are optional for username-only accounts."
)
async def register_user(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register new user account.

    Username is required. Email and password are optional:
    - Username only: Cross-device sync but insecure (anyone with username can access)
    - Username + password: Secure cross-device sync with authentication
    """
    # Validate username
    is_valid, error_msg = auth_service.is_valid_username(request.username)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Validate email if provided
    if request.email:
        is_valid, error_msg = auth_service.is_valid_email(request.email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Validate password if provided
    if request.password:
        is_valid, error_msg = auth_service.is_valid_password(request.password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )

    # Check if email already exists (if provided)
    if request.email:
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

    # Hash password if provided
    password_hash = None
    if request.password:
        password_hash = auth_service.hash_password(request.password)

    # Create user
    user = User(
        username=request.username,
        email=request.email,
        password_hash=password_hash,
        role='user'
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create JWT token
    token = auth_service.create_jwt_token(user.id, expiry_days=30)

    return AuthTokenResponse(
        token=token,
        expires_in_days=30,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            has_password=password_hash is not None,
            created_at=user.created_at.isoformat()
        )
    )


# =============================================================================
# User Login
# =============================================================================

@router.post(
    "/api/users/login",
    response_model=AuthTokenResponse,
    summary="Login to user account",
    description="Login with username. Password required only if account has one set."
)
async def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login to user account.

    For username-only accounts, password is not required.
    For password-protected accounts, password must be provided.
    """
    # Get user
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Check if password is required
    if user.password_hash:
        # Password-protected account
        if not request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password required for this account"
            )

        # Verify password
        if not auth_service.verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    else:
        # Username-only account - no password check needed
        pass

    # Create JWT token
    token = auth_service.create_jwt_token(user.id, expiry_days=30)

    return AuthTokenResponse(
        token=token,
        expires_in_days=30,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            has_password=user.password_hash is not None,
            created_at=user.created_at.isoformat()
        )
    )


# =============================================================================
# User Profile
# =============================================================================

@router.get(
    "/api/users/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get authenticated user's profile information"
)
async def get_current_user(
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        has_password=user.password_hash is not None,
        created_at=user.created_at.isoformat()
    )


@router.patch(
    "/api/users/me",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update email or password. Current password required when changing password."
)
async def update_user_profile(
    request: UpdateProfileRequest,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update email if provided
    if request.email is not None:
        # Validate email
        is_valid, error_msg = auth_service.is_valid_email(request.email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # Check if email already taken
        if request.email:  # Non-empty email
            existing = db.query(User).filter(
                User.email == request.email,
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already taken"
                )

        user.email = request.email if request.email else None

    # Update password if provided
    if request.password is not None:
        # Validate new password
        is_valid, error_msg = auth_service.is_valid_password(request.password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # If user already has a password, verify current password
        if user.password_hash:
            if not request.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password required to change password"
                )

            if not auth_service.verify_password(request.current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect"
                )

        # Hash and set new password
        user.password_hash = auth_service.hash_password(request.password)

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        has_password=user.password_hash is not None,
        created_at=user.created_at.isoformat()
    )
