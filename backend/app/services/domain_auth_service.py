"""
Domain authentication service for database operations.

IMPERATIVE SHELL - Orchestrates pure functions with I/O operations.
Handles database queries, password management, and token generation.
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from ..models.domain_auth import DomainAuth
from ..data.domain_auth import (
    encrypt_password,
    decrypt_password,
    verify_password,
    create_auth_token,
    decode_auth_token,
    validate_token_for_domain,
    should_refresh_token
)
from ..core.config import settings


def get_domain_auth(db: Session, domain_key: str) -> Optional[DomainAuth]:
    """
    Get domain auth record from database.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        DomainAuth object or None if not found

    I/O Operation - Database query.
    """
    return db.query(DomainAuth).filter(DomainAuth.domain_key == domain_key).first()


def get_or_create_domain_auth(db: Session, domain_key: str) -> DomainAuth:
    """
    Get or create domain auth record.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        DomainAuth object

    I/O Operation - Database query/create.
    """
    auth = get_domain_auth(db, domain_key)

    if not auth:
        auth = DomainAuth(domain_key=domain_key)
        db.add(auth)
        db.commit()
        db.refresh(auth)

    return auth


def set_admin_password(db: Session, domain_key: str, password: str) -> Tuple[bool, str]:
    """
    Set admin password for domain.

    Args:
        db: Database session
        domain_key: Domain identifier
        password: Plain text password

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database update.
    """
    try:
        if not password or len(password) < 4:
            return False, "Password must be at least 4 characters"

        encrypted = encrypt_password(password, settings.password_encryption_key)
        auth = get_or_create_domain_auth(db, domain_key)
        auth.admin_password_hash = encrypted

        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Failed to set password: {str(e)}"


def set_user_password(db: Session, domain_key: str, password: str) -> Tuple[bool, str]:
    """
    Set user password for domain.

    Args:
        db: Database session
        domain_key: Domain identifier
        password: Plain text password

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database update.
    """
    try:
        if not password or len(password) < 4:
            return False, "Password must be at least 4 characters"

        encrypted = encrypt_password(password, settings.password_encryption_key)
        auth = get_or_create_domain_auth(db, domain_key)
        auth.user_password_hash = encrypted

        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Failed to set password: {str(e)}"


def remove_admin_password(db: Session, domain_key: str) -> Tuple[bool, str]:
    """
    Remove admin password for domain.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database update.
    """
    try:
        auth = get_domain_auth(db, domain_key)

        if not auth:
            return True, ""  # No password to remove

        auth.admin_password_hash = None
        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Failed to remove password: {str(e)}"


def remove_user_password(db: Session, domain_key: str) -> Tuple[bool, str]:
    """
    Remove user password for domain.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database update.
    """
    try:
        auth = get_domain_auth(db, domain_key)

        if not auth:
            return True, ""  # No password to remove

        auth.user_password_hash = None
        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Failed to remove password: {str(e)}"


def verify_domain_password(
    db: Session,
    domain_key: str,
    password: str,
    access_level: str
) -> Tuple[bool, str]:
    """
    Verify password for domain access.

    Args:
        db: Database session
        domain_key: Domain identifier
        password: Plain text password to verify
        access_level: 'admin' or 'user'

    Returns:
        Tuple of (success, jwt_token_or_error)

    I/O Operation - Database query and token generation.
    """
    try:
        if access_level not in ['admin', 'user']:
            return False, "Invalid access level"

        auth = get_domain_auth(db, domain_key)

        # No password set = no protection
        if not auth:
            # Generate token even without password (backward compatibility)
            token = create_auth_token(
                domain_key,
                access_level,
                settings.jwt_secret_key,
                settings.jwt_algorithm
            )
            return True, token

        # Check appropriate password hash
        password_hash = (
            auth.admin_password_hash if access_level == 'admin'
            else auth.user_password_hash
        )

        # No password set for this level = no protection
        if not password_hash:
            token = create_auth_token(
                domain_key,
                access_level,
                settings.jwt_secret_key,
                settings.jwt_algorithm
            )
            return True, token

        # Verify password
        if verify_password(password, password_hash, settings.password_encryption_key):
            token = create_auth_token(
                domain_key,
                access_level,
                settings.jwt_secret_key,
                settings.jwt_algorithm
            )
            return True, token
        else:
            return False, "Invalid password"

    except Exception as e:
        return False, f"Authentication error: {str(e)}"


def verify_token(token: str, domain_key: str, required_level: str) -> Tuple[bool, Optional[dict]]:
    """
    Verify JWT token for domain access.

    Args:
        token: JWT token string
        domain_key: Expected domain identifier
        required_level: 'admin' or 'user'

    Returns:
        Tuple of (valid, token_data)

    Pure function wrapper for service layer.
    """
    try:
        token_data = decode_auth_token(token, settings.jwt_secret_key, settings.jwt_algorithm)

        if not token_data:
            return False, None

        is_valid = validate_token_for_domain(token_data, domain_key, required_level)

        if is_valid:
            return True, token_data
        else:
            return False, None

    except Exception:
        return False, None


def refresh_token_if_needed(token: str) -> Tuple[bool, str]:
    """
    Refresh token if it's old enough (sliding window).

    Args:
        token: JWT token string

    Returns:
        Tuple of (refreshed, new_token_or_original)

    I/O Operation - Token generation if needed.
    """
    try:
        token_data = decode_auth_token(token, settings.jwt_secret_key, settings.jwt_algorithm)

        if not token_data:
            return False, token  # Invalid token, don't refresh

        if should_refresh_token(token_data, refresh_threshold_days=25):
            # Create new token with same claims
            new_token = create_auth_token(
                token_data['domain_key'],
                token_data['access_level'],
                settings.jwt_secret_key,
                settings.jwt_algorithm,
                expiry_days=30
            )
            return True, new_token
        else:
            return False, token  # No refresh needed

    except Exception:
        return False, token


def check_password_status(db: Session, domain_key: str) -> dict:
    """
    Check password status for domain.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        Dict with password status

    I/O Operation - Database query.
    """
    auth = get_domain_auth(db, domain_key)

    if not auth:
        return {
            'admin_password_set': False,
            'user_password_set': False
        }

    return {
        'admin_password_set': auth.admin_password_hash is not None,
        'user_password_set': auth.user_password_hash is not None
    }


def get_all_domains_auth_status(db: Session) -> list:
    """
    Get password status for all domains (global admin view).

    Args:
        db: Database session

    Returns:
        List of domain auth statuses

    I/O Operation - Database query.
    """
    all_auth = db.query(DomainAuth).all()

    return [
        {
            'domain_key': auth.domain_key,
            'admin_password_set': auth.admin_password_hash is not None,
            'user_password_set': auth.user_password_hash is not None,
            'created_at': auth.created_at.isoformat() if auth.created_at else None,
            'updated_at': auth.updated_at.isoformat() if auth.updated_at else None
        }
        for auth in all_auth
    ]


def get_decrypted_password(db: Session, domain_key: str, password_type: str) -> Tuple[bool, str]:
    """
    Get decrypted password for a domain (global admin only).

    Args:
        db: Database session
        domain_key: Domain identifier
        password_type: 'admin' or 'user'

    Returns:
        Tuple of (success, password_or_error)

    I/O Operation - Database query and decryption.
    """
    try:
        auth = get_domain_auth(db, domain_key)

        if not auth:
            return False, "Domain not found"

        if password_type not in ['admin', 'user']:
            return False, "Invalid password type"

        encrypted = (
            auth.admin_password_hash if password_type == 'admin'
            else auth.user_password_hash
        )

        if not encrypted:
            return False, "Password not set"

        try:
            decrypted = decrypt_password(encrypted, settings.password_encryption_key)
            return True, decrypted
        except Exception as e:
            return False, f"Failed to decrypt password: {str(e)}"

    except Exception as e:
        return False, f"Failed to retrieve password: {str(e)}"
