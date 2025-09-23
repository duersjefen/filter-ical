"""
Test endpoints for development and debugging.

Development utilities for testing cache and sync functionality.
"""

from fastapi import APIRouter
from ..core.scheduler import trigger_manual_sync

router = APIRouter()


@router.get("/background-update")
async def trigger_background_update():
    """Trigger manual background sync for testing."""
    try:
        trigger_manual_sync()
        return {"status": "success", "message": "Background sync triggered manually"}
    except Exception as e:
        return {"status": "error", "message": f"Sync failed: {str(e)}"}