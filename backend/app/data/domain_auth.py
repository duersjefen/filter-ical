"""
Pure functions for domain authentication.

FUNCTIONAL CORE - All functions are pure and deterministic.
No I/O operations, no side effects - only data transformations.

Security:
- JWT with HS256 for session tokens
- 30-day token expiry with sliding window

Note: Password hashing (bcrypt) is handled in auth_service.py
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any


# JWT Token Functions

def create_auth_token(
    domain_key: str,
    access_level: str,
    secret_key: str,
    algorithm: str = "HS256",
    expiry_days: int = 30
) -> str:
    """
    Create a JWT authentication token for domain access.

    Args:
        domain_key: Domain identifier
        access_level: 'admin' or 'user'
        secret_key: JWT signing secret
        algorithm: JWT algorithm (default: HS256)
        expiry_days: Token expiry in days (default: 30)

    Returns:
        JWT token string

    Pure function - deterministic token generation.
    """
    if not domain_key or not access_level:
        raise ValueError("domain_key and access_level are required")

    if access_level not in ['admin', 'user']:
        raise ValueError("access_level must be 'admin' or 'user'")

    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=expiry_days)

    payload = {
        'domain_key': domain_key,
        'access_level': access_level,
        'iat': now,  # Issued at
        'exp': expiry  # Expires at
    }

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def decode_auth_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256"
) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT authentication token.

    Args:
        token: JWT token string
        secret_key: JWT signing secret
        algorithm: JWT algorithm (default: HS256)

    Returns:
        Token payload dict if valid, None if invalid or expired

    Pure function - deterministic decoding.
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token format, signature, or other errors
        return None


def is_token_expired(token_data: Dict[str, Any]) -> bool:
    """
    Check if a decoded token is expired.

    Args:
        token_data: Decoded JWT payload

    Returns:
        True if token is expired

    Pure function - time-based comparison.
    """
    if not token_data or 'exp' not in token_data:
        return True

    expiry = token_data['exp']

    # Handle both datetime objects and unix timestamps
    if isinstance(expiry, datetime):
        expiry_time = expiry
    else:
        expiry_time = datetime.fromtimestamp(expiry, tz=timezone.utc)

    now = datetime.now(timezone.utc)
    return now >= expiry_time


def calculate_token_age_days(token_data: Dict[str, Any]) -> float:
    """
    Calculate the age of a token in days.

    Args:
        token_data: Decoded JWT payload

    Returns:
        Token age in days (fractional)

    Pure function - time-based calculation.
    """
    if not token_data or 'iat' not in token_data:
        return 0.0

    issued_at = token_data['iat']

    # Handle both datetime objects and unix timestamps
    if isinstance(issued_at, datetime):
        issued_time = issued_at
    else:
        issued_time = datetime.fromtimestamp(issued_at, tz=timezone.utc)

    now = datetime.now(timezone.utc)
    age = now - issued_time
    return age.total_seconds() / 86400  # Convert seconds to days


def should_refresh_token(token_data: Dict[str, Any], refresh_threshold_days: int = 25) -> bool:
    """
    Determine if a token should be refreshed (sliding window).

    Algorithm (Sliding Window Token Refresh):
    ==========================================
    Tokens have 30-day expiry, but we refresh at 25 days to maintain
    continuous access without forcing re-authentication.

    Token Lifecycle:
    ----------------
    Day 0:   Token created, 30-day expiry set
    Day 1-24: Token accepted, no refresh needed
    Day 25-29: Token accepted, refresh suggested (sliding window)
    Day 30+:   Token expired, authentication required

    Why This Approach:
    ------------------
    - Prevents session interruption for active users
    - Balances security (regular rotation) with UX (no forced re-auth)
    - 5-day buffer prevents edge cases near expiry
    - Expired tokens cannot be refreshed (security requirement)

    Security Rationale:
    -------------------
    - Regular token rotation limits damage from token theft
    - Sliding window keeps active users continuously authenticated
    - Hard expiry enforces re-authentication for inactive users
    - Cannot refresh expired tokens (forces fresh authentication)

    Example:
    --------
    >>> token_data = {"iat": 1609459200, "exp": 1612051200}  # 30-day token
    >>> # Day 24: Token age = 24 days
    >>> should_refresh_token(token_data, refresh_threshold_days=25)
    False  # Not old enough yet
    >>> # Day 26: Token age = 26 days
    >>> should_refresh_token(token_data, refresh_threshold_days=25)
    True  # Time to refresh
    >>> # Day 31: Token expired
    >>> should_refresh_token(token_data, refresh_threshold_days=25)
    False  # Expired tokens cannot be refreshed

    Args:
        token_data: Decoded JWT payload
        refresh_threshold_days: Refresh tokens older than this (default: 25 days)

    Returns:
        True if token should be refreshed

    Pure function - age-based decision.
    Security: Implements sliding window expiry for better UX.
    """
    if is_token_expired(token_data):
        return False  # Expired tokens cannot be refreshed

    age = calculate_token_age_days(token_data)
    return age >= refresh_threshold_days


def validate_token_for_domain(
    token_data: Optional[Dict[str, Any]],
    expected_domain: str,
    required_level: str
) -> bool:
    """
    Validate that a token grants access to a specific domain and level.

    Args:
        token_data: Decoded JWT payload (or None if invalid)
        expected_domain: Domain key to check access for
        required_level: 'admin' or 'user'

    Returns:
        True if token grants required access

    Pure function - validation logic.
    """
    if not token_data:
        return False

    # Check token hasn't expired
    if is_token_expired(token_data):
        return False

    # Check domain matches
    if token_data.get('domain_key') != expected_domain:
        return False

    # Check access level (admin can access user routes, but not vice versa)
    token_level = token_data.get('access_level')

    if required_level == 'admin':
        return token_level == 'admin'
    elif required_level == 'user':
        return token_level in ['admin', 'user']  # Admin has user-level access too

    return False
