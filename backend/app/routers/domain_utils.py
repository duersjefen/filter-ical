"""
Shared utilities for domain routers.

Provides common helper functions used across domain-related endpoints.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.domain import Domain


def verify_domain_exists(db: Session, domain_key: str) -> Domain:
    """
    Verify that a domain exists in the database.

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        Domain object if found

    Raises:
        HTTPException: If domain not found
    """
    domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_key}' not found")
    return domain
