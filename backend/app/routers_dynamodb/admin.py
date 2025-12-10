"""
Admin router for DynamoDB backend.

Minimal implementation for serverless testing.
"""

from fastapi import APIRouter

from . import admin_auth

# Create main admin router
router = APIRouter()

# Include admin auth (login, password reset)
router.include_router(admin_auth.router)

# Note: Other admin routes (domain management, user management, etc.)
# will be added as they are migrated to DynamoDB
