"""
Domain router for DynamoDB backend.

Implements domain listing and configuration endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException

from .deps import get_repo, get_verified_domain_ddb
from ..db.models import Domain

router = APIRouter()


@router.get("")
async def list_all_domains():
    """
    List all available domains.

    PUBLIC ENDPOINT - No authentication required.
    Returns basic domain information including group counts.
    """
    repo = get_repo()
    domains = repo.list_domains()

    response = []
    for domain in domains:
        if domain.status != "active":
            continue

        response.append({
            "domain_key": domain.domain_key,
            "name": domain.name,
            "calendar_url": domain.calendar_url,
            "group_count": len(domain.groups),
            "has_user_password": domain.user_password_hash is not None and domain.user_password_hash != "",
            "has_admin_password": domain.admin_password_hash is not None and domain.admin_password_hash != ""
        })

    return response


@router.get("/{domain}")
async def get_domain_config(domain: str):
    """
    Get domain configuration.

    PUBLIC ENDPOINT - No authentication required.
    """
    domain_obj = await get_verified_domain_ddb(domain)

    return {
        "success": True,
        "data": {
            "domain_key": domain_obj.domain_key,
            "name": domain_obj.name,
            "calendar_url": domain_obj.calendar_url,
            "status": domain_obj.status,
            "is_owner": False,
            "is_admin": False,
            "has_admin_access": False
        }
    }
