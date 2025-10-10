"""
Domain events router for event retrieval.

Implements event-related endpoints from OpenAPI specification.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.error_handlers import handle_endpoint_errors
from ..core.auth import get_verified_domain
from ..models.domain import Domain
from ..services.cache_service import get_or_build_domain_events

router = APIRouter()


@router.get("/{domain}/events")
@handle_endpoint_errors
async def get_domain_events(
    domain_obj: Domain = Depends(get_verified_domain),
    username: Optional[str] = Query(None),
    force_refresh: bool = Query(False, description="Force refresh cache"),
    db: Session = Depends(get_db)
):
    """Get domain calendar events (grouped structure) - cached for performance."""
    # Get cached domain events or build if needed
    success, response_data, error = get_or_build_domain_events(db, domain_obj.domain_key, force_refresh)

    if not success:
        raise HTTPException(status_code=500, detail=f"Cache error: {error}")

    return response_data
