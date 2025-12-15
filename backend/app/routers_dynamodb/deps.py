"""
Shared dependencies for DynamoDB routers.
"""

from fastapi import HTTPException
from ..db.repository import get_repository, Repository
from ..db.models import Domain


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
