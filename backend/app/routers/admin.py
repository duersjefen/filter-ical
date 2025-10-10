"""
Admin router - Aggregates all admin endpoints from specialized routers.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.

This router combines:
- admin_auth: Login and password reset
- admin_domain_requests: Approve/reject domain requests
- admin_domains: Direct domain management
- admin_domain_configs: YAML configuration management
"""

from fastapi import APIRouter

# Import specialized admin routers
from . import admin_auth
from . import admin_domain_requests
from . import admin_domains
from . import admin_domain_configs

# Create main admin router
router = APIRouter()

# Include all admin sub-routers
router.include_router(admin_auth.router)
router.include_router(admin_domain_requests.router)
router.include_router(admin_domains.router)
router.include_router(admin_domain_configs.router)
