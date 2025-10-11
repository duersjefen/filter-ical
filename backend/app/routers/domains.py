"""
Domain router for core domain operations.

Implements domain listing and configuration endpoints from OpenAPI specification.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from ..core.database import get_db
from ..core.error_handlers import handle_endpoint_errors
from ..core.auth import get_current_user_id, get_verified_domain
from ..models.domain import Domain

router = APIRouter()


@router.get("")
@handle_endpoint_errors
async def list_all_domains(db: Session = Depends(get_db)):
    """
    List all available domains.

    PUBLIC ENDPOINT - No authentication required.
    Returns basic domain information including group counts.
    """
    # PERFORMANCE: Eager load groups to avoid N+1 query pattern
    # Before: 1 + N queries (1 for domains, 1 per domain for groups)
    # After: 2 queries total (1 for domains, 1 for all groups)
    domains = db.query(Domain).options(
        selectinload(Domain.groups)
    ).filter(Domain.status == "active").all()

    # Build response with group counts and password status
    response = []
    for domain in domains:
        # Count groups using the FK relationship (domain_id)
        # Migration populate_group_domain_ids ensures all groups have domain_id set
        group_count = len(domain.groups) if domain.groups else 0

        response.append({
            "domain_key": domain.domain_key,
            "name": domain.name,
            "calendar_url": domain.calendar_url,
            "group_count": group_count,
            "has_user_password": domain.user_password_hash is not None and domain.user_password_hash != "",
            "has_admin_password": domain.admin_password_hash is not None and domain.admin_password_hash != ""
        })

    return response


@router.get("/{domain}")
@handle_endpoint_errors
async def get_domain_config(
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user_id)
):
    """Get domain configuration from database with optional user access info."""
    # Determine user's access level if authenticated
    is_owner = False
    is_admin = False
    if user_id:
        is_owner = domain_obj.owner_id == user_id
        is_admin = any(admin.id == user_id for admin in domain_obj.admins)

    return {
        "success": True,
        "data": {
            "id": domain_obj.id,
            "domain_key": domain_obj.domain_key,
            "name": domain_obj.name,
            "calendar_url": domain_obj.calendar_url,
            "status": domain_obj.status,
            "is_owner": is_owner,
            "is_admin": is_admin,
            "has_admin_access": is_owner or is_admin
        }
    }
