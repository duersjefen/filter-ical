"""
Users router - User account management (register, login, profile).

CONTRACT-DRIVEN: Implementation matches OpenAPI specification.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone

from ..core.database import get_db
from ..core.auth import get_current_user_id, require_user_auth, verify_admin_auth
from ..core.rate_limit import limiter
from ..core.messages import ErrorMessages, SuccessMessages
from ..models.user import User
from ..models.domain import Domain
from ..services import auth_service
from ..services.domain_auth_service import set_admin_password, set_user_password, check_password_status
from ..services.domain_access_service import get_user_unlocked_domains

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================

class UserRegisterRequest(BaseModel):
    """
    Request body for user registration.

    Password is OPTIONAL - you can register with just a username for quick setup.
    However, username-only accounts are insecure (anyone with your username can access).

    For security, provide both username AND password.
    """
    username: str
    email: Optional[str] = None  # Optional - only needed for password reset
    password: Optional[str] = None  # Optional - but recommended for security


class UserLoginRequest(BaseModel):
    """
    Request body for user login.

    Password is OPTIONAL - only required if your account has a password set.
    Username-only accounts can login without a password.
    """
    username: str
    password: Optional[str] = None  # Optional for username-only accounts


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


class SetDomainPasswordsRequest(BaseModel):
    """Request body for domain owners to set passwords."""
    admin_password: Optional[str] = None
    user_password: Optional[str] = None


# =============================================================================
# User Registration
# =============================================================================

@router.post(
    "/api/users/register",
    response_model=AuthTokenResponse,
    summary="Register new user account",
    description="Password is OPTIONAL. Register with just username for quick setup (insecure), or add password for security."
)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register new user account.

    Username is required. Email and password are optional:
    - Username only: Cross-device sync but insecure (anyone with username can access)
    - Username + password: Secure cross-device sync with authentication
    """
    # Validate username
    is_valid, error_msg = auth_service.is_valid_username(user_data.username)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Validate email if provided
    if user_data.email:
        is_valid, error_msg = auth_service.is_valid_email(user_data.email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Validate password if provided
    if user_data.password:
        is_valid, error_msg = auth_service.is_valid_password(user_data.password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # Require email when password is set
        if not user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.EMAIL_REQUIRED_FOR_PASSWORD
            )

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ErrorMessages.USERNAME_TAKEN
        )

    # Check if email already exists (if provided)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorMessages.EMAIL_REGISTERED
            )

    # Hash password if provided
    password_hash = None
    if user_data.password:
        password_hash = auth_service.hash_password(user_data.password)

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
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
    description="Password is OPTIONAL. Only required if your account has a password. Username-only accounts login without password."
)
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login to user account.

    For username-only accounts, password is not required.
    For password-protected accounts, password must be provided.

    Account lockout: 5 failed attempts = 15 minute lockout
    """
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    # Get user
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.INVALID_USERNAME_OR_PASSWORD
        )

    # Check if account is locked
    if user.account_locked_until:
        now = datetime.now(timezone.utc)
        if user.account_locked_until > now:
            minutes_remaining = int((user.account_locked_until - now).total_seconds() / 60)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked due to too many failed login attempts. Try again in {minutes_remaining} minutes."
            )
        else:
            # Lockout expired - reset
            user.account_locked_until = None
            user.failed_login_attempts = 0
            db.commit()

    # Check if password is required
    if user.password_hash:
        # Password-protected account
        if not login_data.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessages.PASSWORD_REQUIRED_FOR_ACCOUNT
            )

        # Verify password
        if not auth_service.verify_password(login_data.password, user.password_hash):
            # Failed login - increment counter
            user.failed_login_attempts += 1

            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                # Lock account
                user.account_locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account locked due to too many failed login attempts. Try again in {LOCKOUT_DURATION_MINUTES} minutes."
                )

            db.commit()
            attempts_remaining = MAX_FAILED_ATTEMPTS - user.failed_login_attempts
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid username or password. {attempts_remaining} attempts remaining before lockout."
            )
    else:
        # Username-only account - no password check needed
        pass

    # Successful login - reset failed attempts
    user.failed_login_attempts = 0
    user.account_locked_until = None
    db.commit()

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
# Username Check (for login UX)
# =============================================================================

@router.get(
    "/api/users/check/{username}",
    summary="Check username password requirement",
    description="Check if username exists and requires password. Used for login UX."
)
@limiter.limit("20/minute")
async def check_username(
    request: Request,
    username: str,
    db: Session = Depends(get_db)
):
    """
    Check if username exists and whether it requires a password.

    This endpoint enables better UX by showing users whether they need
    to enter a password before they attempt login.

    Returns 404 if username doesn't exist.

    Security note: This endpoint reveals which usernames exist in the system.
    This is acceptable for this application because usernames are already public
    (used for public calendar sharing). For applications requiring username privacy,
    this endpoint should not be implemented.
    """
    # Get user
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.USERNAME_NOT_FOUND
        )

    return {
        "username": user.username,
        "exists": True,
        "has_password": user.password_hash is not None
    }


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
            detail=ErrorMessages.USER_NOT_FOUND
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
            detail=ErrorMessages.USER_NOT_FOUND
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
                    detail=ErrorMessages.EMAIL_TAKEN
                )

        user.email = request.email if request.email else None

    # Update password if provided
    if request.password is not None:
        # Validate new password
        is_valid, error_msg = auth_service.is_valid_password(request.password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # Require email when setting password
        if not user.email and request.email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.EMAIL_REQUIRED_FOR_PASSWORD
            )

        # If user already has a password, verify current password
        if user.password_hash:
            if not request.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorMessages.CURRENT_PASSWORD_REQUIRED
                )

            if not auth_service.verify_password(request.current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ErrorMessages.CURRENT_PASSWORD_INCORRECT
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


@router.get(
    "/api/users/me/domains",
    summary="Get user's domains",
    description="Get all domains the user interacts with: owned, admin, password-access, and filter domains"
)
async def get_user_domains(
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Get user's owned, admin, password-access, and filter domains."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.USER_NOT_FOUND
        )

    # Get owned domains
    owned_domains = []
    for domain in user.owned_domains:
        owned_domains.append({
            "domain_key": domain.domain_key,
            "name": domain.name,
            "calendar_url": domain.calendar_url,
            "status": domain.status,
            "created_at": domain.created_at.isoformat()
        })

    # Get admin domains (where user is admin but not owner)
    admin_domains = []
    for domain in user.admin_domains:
        if domain.owner_id != user.id:  # Exclude domains where user is owner
            admin_domains.append({
                "domain_key": domain.domain_key,
                "name": domain.name,
                "calendar_url": domain.calendar_url,
                "status": domain.status,
                "created_at": domain.created_at.isoformat()
            })

    # Get password-access domains (from UserDomainAccess)
    password_access_domains = []
    for access in user.domain_access:
        if access.calendar_id:
            # Find domain by calendar_id
            domain = db.query(Domain).filter(Domain.calendar_id == access.calendar_id).first()
            if domain:
                # Skip if already in owned or admin
                if domain.owner_id == user.id or domain in user.admin_domains:
                    continue
                password_access_domains.append({
                    "domain_key": domain.domain_key,
                    "name": domain.name,
                    "access_level": access.access_level,
                    "unlocked_at": access.unlocked_at.isoformat()
                })

    # Get filter domains (domains where user has filters)
    filter_domains = []
    seen_domain_keys = set()
    for filter_obj in user.filters:
        if filter_obj.domain_key:
            # Skip if already in other lists
            if filter_obj.domain_key in [d["domain_key"] for d in owned_domains + admin_domains + password_access_domains]:
                continue
            if filter_obj.domain_key not in seen_domain_keys:
                seen_domain_keys.add(filter_obj.domain_key)
                # Get domain info
                domain = db.query(Domain).filter(Domain.domain_key == filter_obj.domain_key).first()
                if domain:
                    filter_domains.append({
                        "domain_key": domain.domain_key,
                        "name": domain.name,
                        "filter_count": len([f for f in user.filters if f.domain_key == domain.domain_key])
                    })

    return {
        "owned_domains": owned_domains,
        "admin_domains": admin_domains,
        "password_access_domains": password_access_domains,
        "filter_domains": filter_domains
    }


@router.get(
    "/api/users/me/unlocked-domains",
    summary="Get user's unlocked domains (password-authenticated access)",
    description="Returns all domains the user has unlocked by entering admin or user passwords. This access persists across devices."
)
async def get_user_unlocked_domains_endpoint(
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """
    Get all domains user has unlocked by entering passwords.

    Returns list of domains with access_level and unlock timestamp.
    This is account-based access that follows the user across devices.
    """
    unlocked = get_user_unlocked_domains(db, user_id)
    return {"unlocked_domains": unlocked}


@router.patch(
    "/api/users/me/domains/{domain}/passwords",
    summary="Set domain passwords (owner or global admin only)"
)
async def set_domain_passwords_as_owner(
    domain: str,
    request: SetDomainPasswordsRequest,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Set or change domain passwords (owner or global admin access).

    - Domain owner can set passwords for domains they own
    - Global admin can set passwords for any domain
    """
    # Get domain
    domain_obj = db.query(Domain).filter(Domain.domain_key == domain).first()
    if not domain_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.DOMAIN_NOT_FOUND.format(domain=domain)
        )

    # Check authorization: user is owner OR global admin
    is_owner = domain_obj.owner_id == user_id
    is_global_admin = False
    try:
        verify_admin_auth(authorization)
        is_global_admin = True
    except:
        pass

    if not is_owner and not is_global_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMessages.ACCESS_DENIED_OWNER_OR_GLOBAL_ADMIN
        )

    results = []

    # Handle admin password
    if request.admin_password:
        success, error = set_admin_password(db, domain, request.admin_password)
        if not success:
            raise HTTPException(status_code=400, detail=f"Admin password set failed: {error}")
        results.append("Admin password set")

    # Handle user password
    if request.user_password:
        success, error = set_user_password(db, domain, request.user_password)
        if not success:
            raise HTTPException(status_code=400, detail=f"User password set failed: {error}")
        results.append("User password set")

    if not results:
        return {"success": True, "message": SuccessMessages.NO_CHANGES_REQUESTED}

    return {"success": True, "message": ", ".join(results)}
