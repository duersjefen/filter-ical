"""
Domain authentication service for database operations.

IMPERATIVE SHELL - Orchestrates pure functions with I/O operations.
Handles database queries, password management, and token generation.
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from ..models.domain import Domain
from ..data.domain_auth import (
    create_auth_token,
    decode_auth_token,
    validate_token_for_domain,
    should_refresh_token
)
from ..services.auth_service import hash_password, verify_password
from ..core.config import settings


def get_domain_auth(db: Session, domain_key: str) -> Optional[Domain]:
    """
    Get domain record from database.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        Domain object or None if not found

    I/O Operation - Database query.
    """
    return db.query(Domain).filter(Domain.domain_key == domain_key).first()


def get_or_create_domain_auth(db: Session, domain_key: str) -> Domain:
    """
    Get or create domain record.

    Note: This function name is legacy. It now works with the unified Domain model.
    For new domains, they should be created via proper domain creation workflow.
    This is primarily for backward compatibility.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        Domain object

    I/O Operation - Database query/create.
    """
    domain = get_domain_auth(db, domain_key)

    if not domain:
        # Create minimal domain record (primarily for backward compatibility)
        domain = Domain(
            domain_key=domain_key,
            name=f"Domain {domain_key}"  # Default name
        )
        db.add(domain)
        db.commit()
        db.refresh(domain)

    return domain


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

        hashed = hash_password(password)
        domain = get_or_create_domain_auth(db, domain_key)
        domain.admin_password_hash = hashed

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

        hashed = hash_password(password)
        domain = get_or_create_domain_auth(db, domain_key)
        domain.user_password_hash = hashed

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
        domain = get_domain_auth(db, domain_key)

        if not domain:
            return True, ""  # No password to remove

        domain.admin_password_hash = None
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
        domain = get_domain_auth(db, domain_key)

        if not domain:
            return True, ""  # No password to remove

        domain.user_password_hash = None
        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Failed to remove password: {str(e)}"


def verify_domain_password(
    db: Session,
    domain_key: str,
    password: str,
    access_level: str,
    skip_password_check: bool = False
) -> Tuple[bool, str]:
    """
    Verify password for domain access.

    Args:
        db: Database session
        domain_key: Domain identifier
        password: Plain text password to verify
        access_level: 'admin' or 'user'
        skip_password_check: If True, skip password verification (for users with saved access)

    Returns:
        Tuple of (success, jwt_token_or_error)

    I/O Operation - Database query and token generation.
    """
    try:
        if access_level not in ['admin', 'user']:
            return False, "Invalid access level"

        domain = get_domain_auth(db, domain_key)

        # No password set = no protection
        if not domain:
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
            domain.admin_password_hash if access_level == 'admin'
            else domain.user_password_hash
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

        # If skip_password_check, generate token without verification
        # (used for logged-in users with saved domain access)
        if skip_password_check:
            token = create_auth_token(
                domain_key,
                access_level,
                settings.jwt_secret_key,
                settings.jwt_algorithm
            )
            return True, token

        # Verify password
        if verify_password(password, password_hash):
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
    domain = get_domain_auth(db, domain_key)

    if not domain:
        return {
            'admin_password_set': False,
            'user_password_set': False
        }

    return {
        'admin_password_set': domain.admin_password_hash is not None,
        'user_password_set': domain.user_password_hash is not None
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
    all_domains = db.query(Domain).all()

    return [
        {
            'domain_key': domain.domain_key,
            'admin_password_set': domain.admin_password_hash is not None,
            'user_password_set': domain.user_password_hash is not None,
            'owner_id': domain.owner_id,
            'owner_username': domain.owner.username if domain.owner else None,
            'created_at': domain.created_at.isoformat() if domain.created_at else None,
            'updated_at': domain.updated_at.isoformat() if domain.updated_at else None
        }
        for domain in all_domains
    ]


