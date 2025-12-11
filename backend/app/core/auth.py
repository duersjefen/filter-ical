"""
Authentication for admin endpoints.

Supports both HTTP Basic Auth (legacy) and JWT tokens.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, TYPE_CHECKING
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import jwt

from .config import settings

# Only import for type checking - actual imports are lazy to support DynamoDB mode
if TYPE_CHECKING:
    from sqlalchemy.orm import Session

security = HTTPBasic()


def verify_admin_password(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """
    Verify admin password from HTTP Basic Auth.

    Username is ignored - only password is validated against ADMIN_PASSWORD env var.

    Args:
        credentials: HTTP Basic Auth credentials

    Returns:
        True if password is correct

    Raises:
        HTTPException: If password is incorrect
    """
    # Use constant-time comparison to prevent timing attacks
    is_password_correct = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        settings.admin_password.encode("utf-8")
    )

    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True


def create_admin_token(expiry_days: int = 30) -> str:
    """
    Create a JWT token for global admin authentication.

    Args:
        expiry_days: Number of days until token expires (default: 30)

    Returns:
        JWT token string
    """
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=expiry_days)

    payload = {
        'role': 'global_admin',
        'iat': now,  # Issued at
        'exp': expiry  # Expires at
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def verify_admin_token(token: str) -> bool:
    """
    Verify a JWT token for global admin authentication.

    Args:
        token: JWT token string

    Returns:
        True if token is valid

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        # Verify role
        if payload.get('role') != 'global_admin':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token role"
            )

        return True

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def verify_admin_auth(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify admin authentication from either JWT token or HTTP Basic Auth.

    Supports two authentication methods:
    1. JWT token: Authorization: Bearer <token>
    2. HTTP Basic Auth: Authorization: Basic <credentials>

    Args:
        authorization: Authorization header value

    Returns:
        True if authenticated

    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication"
        )

    # Check for Bearer token (JWT)
    if authorization.startswith('Bearer '):
        token = authorization.replace('Bearer ', '')
        return verify_admin_token(token)

    # Fall back to Basic Auth (legacy support)
    # This path will be taken when using HTTPBasicCredentials
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication method"
    )


# =============================================================================
# User JWT Authentication (for regular users)
# =============================================================================

def get_current_user_id(authorization: Optional[str] = Header(None)) -> Optional[int]:
    """
    Extract user ID from JWT token (optional - returns None if not authenticated).

    Use this for endpoints that work for both authenticated and anonymous users.

    Args:
        authorization: Authorization header value

    Returns:
        User ID if authenticated, None otherwise
    """
    if not authorization or not authorization.startswith('Bearer '):
        return None

    token = authorization.replace('Bearer ', '')

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload.get('user_id')
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def require_user_auth(authorization: Optional[str] = Header(None)) -> int:
    """
    Require user authentication and return user ID.

    Use this for endpoints that require authentication.

    Args:
        authorization: Authorization header value

    Returns:
        User ID

    Raises:
        HTTPException: If not authenticated or token invalid
    """
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    token = authorization.replace('Bearer ', '')

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get('user_id')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# =============================================================================
# Domain Verification Dependency (SQLAlchemy mode only)
# =============================================================================
# NOTE: This function is only used by SQLAlchemy routers, which only load
# when settings.use_dynamodb is False. The lazy import pattern ensures
# no SQLAlchemy imports happen when using DynamoDB mode.


def _lazy_get_db():
    """Lazy import wrapper for get_db - only called when actually used."""
    from .database import get_db
    yield from get_db()


async def get_verified_domain(domain: str, db=Depends(_lazy_get_db)):
    """
    FastAPI dependency: Verify domain exists and return domain object.

    Raises HTTPException 404 if domain not found.

    Usage in routers:
        @router.get("/{domain}/events")
        async def get_events(domain_obj: Domain = Depends(get_verified_domain)):
            # domain_obj is guaranteed to exist
            pass

    Args:
        domain: Domain key from URL path parameter
        db: Database session (injected lazily)

    Returns:
        Domain object from database

    Raises:
        HTTPException 404: Domain not found
    """
    from sqlalchemy import select
    from ..models.domain import Domain

    stmt = select(Domain).where(Domain.domain_key == domain)
    domain_obj = db.scalar(stmt)

    if not domain_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Domain '{domain}' not found"
        )

    return domain_obj
