"""
Application settings router for DynamoDB backend.

Provides endpoints for reading/updating global app settings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from ..core.auth import verify_admin_auth
from ..db.repository import get_repository

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
async def get_settings_endpoint():
    """
    Get global application settings.

    Public endpoint - no authentication required.
    Frontend needs to check these settings to control UI visibility.
    """
    repo = get_repository()
    settings = repo.get_app_settings()

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
    _: bool = Depends(verify_admin_auth)
):
    """
    Update global application settings.

    Requires global admin authentication.
    """
    # Validate footer_visibility if provided
    if request.footer_visibility is not None:
        if request.footer_visibility not in ['everywhere', 'admin_only', 'nowhere']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="footer_visibility must be 'everywhere', 'admin_only', or 'nowhere'"
            )

    repo = get_repository()
    settings = repo.update_app_settings(
        footer_visibility=request.footer_visibility,
        show_domain_request=request.show_domain_request
    )

    return AppSettingsResponse(
        footer_visibility=settings.footer_visibility,
        show_domain_request=settings.show_domain_request
    )
