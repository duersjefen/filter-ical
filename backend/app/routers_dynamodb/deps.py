"""
Shared dependencies for DynamoDB routers.
"""

from typing import Optional
from fastapi import HTTPException, Header
from ..db.repository import get_repository, Repository
from ..db.models import Domain
from ..core.auth import verify_admin_auth


def get_repo() -> Repository:
    """Get the repository instance."""
    return get_repository()


async def get_verified_domain_ddb(domain: str) -> Domain:
    """
    Verify domain exists and return domain object.

    Raises 404 if domain not found.
    """
    repo = get_repo()
    domain_obj = repo.get_domain(domain)
    if not domain_obj:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
    if domain_obj.status != "active":
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' is not active")
    return domain_obj


def require_admin_auth(authorization: Optional[str] = Header(None)) -> bool:
    """
    Dependency to require admin authentication.

    Uses the existing verify_admin_auth from core.auth.

    Usage:
        @router.get("/admin/something")
        async def admin_endpoint(_admin: str = Depends(require_admin_auth)):
            ...
    """
    return verify_admin_auth(authorization)
