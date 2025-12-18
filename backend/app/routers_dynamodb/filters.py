"""
User-level filter router for DynamoDB backend.

Returns filters for authenticated users. Since DynamoDB mode
doesn't have full user auth yet, returns empty array for anonymous.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_user_filters():
    """
    Get all filters for a user.

    For DynamoDB mode without user auth, returns empty array.
    Frontend uses this to check if user has any saved filters.
    """
    # DynamoDB mode: No user auth yet, return empty list
    # This prevents 404 errors and lets the frontend work
    return []
