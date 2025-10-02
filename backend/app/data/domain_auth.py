"""
Pure functions for domain authentication.

FUNCTIONAL CORE - All functions are pure and deterministic.
No I/O operations, no side effects - only data transformations.

Security:
- Fernet (AES) for password encryption (two-way, retrievable)
- JWT with HS256 for session tokens
- 30-day token expiry with sliding window

NOTE: Passwords are encrypted (not hashed) to allow admin retrieval.
This is a security trade-off for admin convenience.
"""

from cryptography.fernet import Fernet, InvalidToken
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any


# Password Encryption Functions

def encrypt_password(password: str, encryption_key: str) -> str:
    """
    Encrypt a password using Fernet (AES encryption).

    Args:
        password: Plain text password
        encryption_key: Fernet encryption key (base64-encoded 32-byte key)

    Returns:
        Encrypted password as string

    Pure function - encryption with key.
    """
    if not password:
        raise ValueError("Password cannot be empty")

    if not encryption_key:
        raise ValueError("Encryption key cannot be empty")

    try:
        fernet = Fernet(encryption_key.encode())
        password_bytes = password.encode('utf-8')
        encrypted = fernet.encrypt(password_bytes)
        return encrypted.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to encrypt password: {str(e)}")


def decrypt_password(encrypted_password: str, encryption_key: str) -> str:
    """
    Decrypt a password using Fernet (AES encryption).

    Args:
        encrypted_password: Encrypted password string
        encryption_key: Fernet encryption key (base64-encoded 32-byte key)

    Returns:
        Decrypted password as plain text

    Pure function - decryption with key.
    """
    if not encrypted_password:
        raise ValueError("Encrypted password cannot be empty")

    if not encryption_key:
        raise ValueError("Encryption key cannot be empty")

    try:
        fernet = Fernet(encryption_key.encode())
        encrypted_bytes = encrypted_password.encode('utf-8')
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    except InvalidToken:
        raise ValueError("Invalid encrypted password or wrong encryption key")
    except Exception as e:
        raise ValueError(f"Failed to decrypt password: {str(e)}")


def verify_password(password: str, encrypted_password: str, encryption_key: str) -> bool:
    """
    Verify a password against an encrypted password.

    Args:
        password: Plain text password to verify
        encrypted_password: Encrypted password to compare against
        encryption_key: Fernet encryption key

    Returns:
        True if password matches

    Pure function - decryption and comparison.
    """
    if not password or not encrypted_password:
        return False

    try:
        decrypted = decrypt_password(encrypted_password, encryption_key)
        return password == decrypted
    except Exception:
        # Invalid encrypted password or decryption failed
        return False


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
