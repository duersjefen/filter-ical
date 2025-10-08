"""
Authentication service for user account management.

FUNCTIONAL CORE - Pure functions for authentication logic.
IMPERATIVE SHELL - Database operations handled by routers.

Handles:
- Password hashing (bcrypt)
- JWT token creation/verification
- Password reset tokens
"""

import uuid
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional

from ..core.config import settings
from ..models.user import User
from sqlalchemy.orm import Session


# =============================================================================
# User Management (Database Operations)
# =============================================================================

def get_or_create_user_from_username(db: Session, username: str) -> Optional[User]:
    """
    Get existing user by username, or create a new username-only account.

    This handles migration from the old username-based system to the new user accounts.
    Users who had calendars with just a username will automatically get a user account created.

    Args:
        db: Database session
        username: Username string

    Returns:
        User object, or None if username is invalid

    I/O Operation - Database query and potential insert.
    """
    if not username or not isinstance(username, str):
        return None

    username = username.strip()
    if not username:
        return None

    # Check if user already exists
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user

    # Auto-create user for legacy username-based calendars
    # These are username-only accounts (no password) for backward compatibility
    try:
        new_user = User(
            username=username,
            email=None,  # No email for auto-created accounts
            password_hash=None,  # No password - username-only access
            role='user'
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        return None


# =============================================================================
# Password Hashing (Pure Functions)
# =============================================================================

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hash as string

    Pure function - same input always produces different output (due to salt),
    but validation is deterministic.
    """
    salt = bcrypt.gensalt(rounds=12)  # Cost factor 12 (good balance)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against bcrypt hash.

    Args:
        password: Plain text password
        password_hash: Bcrypt hash

    Returns:
        True if password matches hash

    Pure function - deterministic verification.
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


# =============================================================================
# JWT Token Management (Pure Functions)
# =============================================================================

def create_jwt_token(user_id: int, expiry_days: int = 30) -> str:
    """
    Create JWT token for user authentication.

    Args:
        user_id: User ID
        expiry_days: Token expiry in days (default 30)

    Returns:
        JWT token string

    Pure function - creates token with user_id and expiry.
    """
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=expiry_days)

    payload = {
        'user_id': user_id,
        'iat': now.timestamp(),  # Issued at
        'exp': expiry.timestamp()  # Expires at
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def verify_jwt_token(token: str) -> Tuple[bool, Optional[int], str]:
    """
    Verify JWT token and extract user ID.

    Args:
        token: JWT token string

    Returns:
        Tuple of (is_valid, user_id, error_message)

    Pure function - validates token and extracts payload.
    """
    if not token:
        return False, None, "Missing token"

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        user_id = payload.get('user_id')
        if not user_id:
            return False, None, "Invalid token payload"

        return True, user_id, ""

    except jwt.ExpiredSignatureError:
        return False, None, "Token has expired"
    except jwt.InvalidTokenError as e:
        return False, None, f"Invalid token: {str(e)}"


# =============================================================================
# Password Reset Tokens (Pure Functions)
# =============================================================================

def generate_reset_token() -> str:
    """
    Generate secure random reset token.

    Returns:
        UUID4 string

    Pure function - generates cryptographically secure random token.
    """
    return str(uuid.uuid4())


def create_reset_token_expiry(hours: int = 1) -> datetime:
    """
    Create expiry datetime for reset token.

    Args:
        hours: Hours until expiry (default 1)

    Returns:
        Datetime in UTC

    Pure function - calculates expiry time.
    """
    return datetime.now(timezone.utc) + timedelta(hours=hours)


def is_reset_token_valid(user: User, token: str) -> bool:
    """
    Check if reset token is valid and not expired.

    Args:
        user: User object
        token: Reset token to validate

    Returns:
        True if token is valid and not expired

    Pure function - checks token match and expiry.
    """
    # Check token exists and matches
    if not user.reset_token or user.reset_token != token:
        return False

    # Check not expired
    if not user.reset_token_expires:
        return False

    now = datetime.now(timezone.utc)
    # Make expires timezone-aware if it isn't
    expires = user.reset_token_expires
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if now > expires:
        return False

    return True


# =============================================================================
# User Validation (Pure Functions)
# =============================================================================

def is_valid_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid, error_message)

    Pure function - validates username rules.
    """
    if not username:
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 50:
        return False, "Username must be at most 50 characters"

    # Only alphanumeric, underscore, hyphen
    if not all(c.isalnum() or c in ['_', '-'] for c in username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"

    return True, ""


def is_valid_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.

    Args:
        email: Email to validate

    Returns:
        Tuple of (is_valid, error_message)

    Pure function - basic email validation.
    """
    if not email:
        return True, ""  # Email is optional

    if '@' not in email or '.' not in email:
        return False, "Invalid email format"

    if len(email) > 255:
        return False, "Email too long"

    return True, ""


def is_valid_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)

    Pure function - validates password rules.
    """
    if not password:
        return True, ""  # Password is optional

    if len(password) < 4:
        return False, "Password must be at least 4 characters"

    if len(password) > 100:
        return False, "Password too long"

    return True, ""
