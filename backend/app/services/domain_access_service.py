"""
Domain access service for managing user domain unlocking.

IMPERATIVE SHELL - Database operations for domain access.

When a user enters a domain's shared password, we create a user_domain_access
entry so they don't need to re-enter it on future visits.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from ..models.domain_auth import DomainAuth
from ..models.user_domain_access import UserDomainAccess
from ..models.calendar import Calendar
from ..services.domain_auth_service import decrypt_password


def check_user_has_domain_access(
    db: Session,
    user_id: int,
    domain_key: str,
    access_level: str
) -> bool:
    """
    Check if user has already unlocked this domain.

    Args:
        db: Database session
        user_id: User ID
        domain_key: Domain key (e.g., 'university')
        access_level: 'admin' or 'user'

    Returns:
        True if user has access, False otherwise

    I/O Operation - Database query.
    """
    # Get domain_auth entry to find calendar_id
    domain_auth = db.query(DomainAuth).filter(
        DomainAuth.domain_key == domain_key
    ).first()

    if not domain_auth:
        return False

    # Check if domain requires password for this access level
    password_required = (
        domain_auth.admin_password_hash if access_level == 'admin'
        else domain_auth.user_password_hash
    )

    # If no password set, allow access
    if not password_required:
        return True

    # Check user_domain_access table
    access = db.query(UserDomainAccess).filter(
        UserDomainAccess.user_id == user_id,
        UserDomainAccess.calendar_id == domain_auth.calendar_id,
        UserDomainAccess.access_level == access_level
    ).first()

    return access is not None


def unlock_domain_for_user(
    db: Session,
    user_id: int,
    domain_key: str,
    password: str,
    access_level: str
) -> tuple[bool, str]:
    """
    Verify password and grant user access to domain.

    Creates user_domain_access entry if password is correct.

    Args:
        db: Database session
        user_id: User ID
        domain_key: Domain key
        password: Plain text password to verify
        access_level: 'admin' or 'user'

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database query and insert.
    """
    # Get domain_auth entry
    domain_auth = db.query(DomainAuth).filter(
        DomainAuth.domain_key == domain_key
    ).first()

    if not domain_auth:
        return False, "Domain not found"

    # Get password hash for this access level
    password_hash = (
        domain_auth.admin_password_hash if access_level == 'admin'
        else domain_auth.user_password_hash
    )

    if not password_hash:
        # No password set, automatically grant access
        try:
            _create_access_entry(db, user_id, domain_auth.calendar_id, access_level)
            return True, ""
        except Exception as e:
            return False, f"Failed to grant access: {str(e)}"

    # Verify password
    try:
        decrypted_password = decrypt_password(password_hash)
        if decrypted_password != password:
            return False, "Invalid password"
    except Exception as e:
        return False, f"Password verification failed: {str(e)}"

    # Create access entry
    try:
        _create_access_entry(db, user_id, domain_auth.calendar_id, access_level)
        return True, ""
    except Exception as e:
        return False, f"Failed to grant access: {str(e)}"


def get_user_unlocked_domains(
    db: Session,
    user_id: int
) -> List[dict]:
    """
    Get all domains user has unlocked.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of domain info dicts with keys: domain_key, access_level, unlocked_at

    I/O Operation - Database query with joins.
    """
    # Query user_domain_access with joins to get domain_key
    results = (
        db.query(
            DomainAuth.domain_key,
            UserDomainAccess.access_level,
            UserDomainAccess.unlocked_at
        )
        .join(UserDomainAccess, DomainAuth.calendar_id == UserDomainAccess.calendar_id)
        .filter(UserDomainAccess.user_id == user_id)
        .all()
    )

    return [
        {
            "domain_key": row.domain_key,
            "access_level": row.access_level,
            "unlocked_at": row.unlocked_at.isoformat() if row.unlocked_at else None
        }
        for row in results
    ]


def _create_access_entry(
    db: Session,
    user_id: int,
    calendar_id: int,
    access_level: str
) -> None:
    """
    Create user_domain_access entry (internal helper).

    Idempotent - silently succeeds if entry already exists.

    Args:
        db: Database session
        user_id: User ID
        calendar_id: Calendar ID
        access_level: 'admin' or 'user'

    Raises:
        Exception if database operation fails

    I/O Operation - Database insert.
    """
    # Check if already exists
    existing = db.query(UserDomainAccess).filter(
        UserDomainAccess.user_id == user_id,
        UserDomainAccess.calendar_id == calendar_id,
        UserDomainAccess.access_level == access_level
    ).first()

    if existing:
        return  # Already has access

    # Create new access entry
    access = UserDomainAccess(
        user_id=user_id,
        calendar_id=calendar_id,
        access_level=access_level
    )

    db.add(access)
    db.commit()
