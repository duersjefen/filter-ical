"""
Domain access service for managing user domain unlocking.

IMPERATIVE SHELL - Database operations for domain access.

When a user enters a domain's shared password, we create a user_domain_access
entry so they don't need to re-enter it on future visits.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from ..models.domain import Domain
from ..models.user_domain_access import UserDomainAccess
from ..models.calendar import Calendar
from ..models.domain_admin import domain_admins
from ..services.auth_service import verify_password


def check_user_has_domain_access(
    db: Session,
    user_id: int,
    domain_key: str,
    access_level: str
) -> bool:
    """
    Check if user has access to this domain.

    Access is granted if:
    1. User is the domain owner (always has admin access)
    2. User is in domain_admins table (always has admin access)
    3. No password is set for the requested access level (open access)
    4. User has unlocked the domain via password (user_domain_access entry)

    Args:
        db: Database session
        user_id: User ID
        domain_key: Domain key (e.g., 'university')
        access_level: 'admin' or 'user'

    Returns:
        True if user has access, False otherwise

    I/O Operation - Database query.
    """
    # Get domain entry to find calendar_id
    domain = db.query(Domain).filter(
        Domain.domain_key == domain_key
    ).first()

    if not domain:
        return False

    # PRIORITY CHECK: Owner always has admin access
    if domain.owner_id == user_id and access_level == 'admin':
        return True

    # PRIORITY CHECK: Domain admins always have admin access
    if access_level == 'admin':
        is_domain_admin = db.query(domain_admins).filter(
            domain_admins.c.user_id == user_id,
            domain_admins.c.domain_id == domain.id
        ).first() is not None

        if is_domain_admin:
            return True

    # Check if domain requires password for this access level
    password_required = (
        domain.admin_password_hash if access_level == 'admin'
        else domain.user_password_hash
    )

    # If no password set, allow access
    if not password_required:
        return True

    # Check user_domain_access table (password unlock)
    access = db.query(UserDomainAccess).filter(
        UserDomainAccess.user_id == user_id,
        UserDomainAccess.calendar_id == domain.calendar_id,
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
    # Get domain entry
    domain = db.query(Domain).filter(
        Domain.domain_key == domain_key
    ).first()

    if not domain:
        return False, "Domain not found"

    # Get password hash for this access level
    password_hash = (
        domain.admin_password_hash if access_level == 'admin'
        else domain.user_password_hash
    )

    if not password_hash:
        # No password set, automatically grant access
        try:
            _create_access_entry(db, user_id, domain.calendar_id, access_level)
            return True, ""
        except Exception as e:
            return False, f"Failed to grant access: {str(e)}"

    # Verify password
    if not verify_password(password, password_hash):
        return False, "Invalid password"

    # Create access entry
    try:
        _create_access_entry(db, user_id, domain.calendar_id, access_level)
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
            Domain.domain_key,
            UserDomainAccess.access_level,
            UserDomainAccess.unlocked_at
        )
        .join(UserDomainAccess, Domain.calendar_id == UserDomainAccess.calendar_id)
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
