"""
API routes for application settings.

Global admin only - requires authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..core.auth import verify_admin_auth
from ..services.app_settings_service import (
    get_app_settings,
    update_app_settings
)

router = APIRouter()


class AppSettingsResponse(BaseModel):
    """Response model for app settings."""
    footer_visibility: str  # 'everywhere', 'admin_only', 'nowhere'
    show_domain_request: bool


class UpdateAppSettingsRequest(BaseModel):
    """Request model for updating app settings."""
    footer_visibility: Optional[str] = None
    show_domain_request: Optional[bool] = None


@router.get(
    "/api/app-settings",
    response_model=AppSettingsResponse,
    summary="Get application settings"
)
async def get_settings_endpoint(db: Session = Depends(get_db)):
    """
    Get global application settings.

    Public endpoint - no authentication required.
    Frontend needs to check these settings to control UI visibility.
    """
    settings = get_app_settings(db)

    return AppSettingsResponse(
        footer_visibility=settings.footer_visibility,
        show_domain_request=settings.show_domain_request
    )


@router.patch(
    "/api/admin/app-settings",
    response_model=AppSettingsResponse,
    summary="Update application settings (admin only)"
)
async def update_settings_endpoint(
    request: UpdateAppSettingsRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Update global application settings.

    Requires global admin authentication.
    """
    success, error = update_app_settings(
        db,
        footer_visibility=request.footer_visibility,
        show_domain_request=request.show_domain_request
    )

    if not success:
        raise HTTPException(status_code=400, detail=error)

    settings = get_app_settings(db)

    return AppSettingsResponse(
        footer_visibility=settings.footer_visibility,
        show_domain_request=settings.show_domain_request
    )
