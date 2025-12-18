"""
Main FastAPI application with contract-first development.

This follows the architectural principle from CLAUDE.md:
"OpenAPI specifications are immutable contracts that enable unlimited backend refactoring freedom"

Supports both SQLAlchemy (legacy) and DynamoDB (serverless) backends.
Set USE_DYNAMODB=true to use DynamoDB mode.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .core.config import settings
from .core.rate_limit import limiter
from .core.error_handlers import http_exception_handler
from .core.request_size_limiter import RequestSizeLimiter
from .core.content_type_validator import ContentTypeValidator

# Only import SQLAlchemy components if not using DynamoDB
if not settings.use_dynamodb:
    from .core.database import Base, engine
    from .core.scheduler import start_scheduler, stop_scheduler


def load_openapi_spec() -> Optional[Dict[str, Any]]:
    """
    Load our custom OpenAPI specification for contract compliance.
    
    This is the core of contract-first development - our OpenAPI spec
    defines what FastAPI should expose, not the other way around.
    """
    spec_path = settings.openapi_spec_path
    if spec_path.exists():
        with open(spec_path, 'r') as f:
            return yaml.safe_load(f)
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Filter iCal...")
    print(f"🌍 Environment: {settings.environment.value}")
    print(f"💾 Database: {'DynamoDB' if settings.use_dynamodb else 'SQLAlchemy'}")
    print("📋 Contract-first development active")

    # Security validation - ensure JWT secret is configured properly in all environments except testing
    if not settings.is_testing:
        if settings.jwt_secret_key == "change-me-in-production-use-strong-random-key":
            raise RuntimeError(
                "🚨 SECURITY ERROR: JWT_SECRET_KEY is using default value! "
                "Set JWT_SECRET_KEY environment variable to a strong random key."
            )
        if len(settings.jwt_secret_key) < 32:
            raise RuntimeError(
                "🚨 SECURITY ERROR: JWT_SECRET_KEY must be at least 32 characters long"
            )
        print("✅ JWT secret key validated")

    # DynamoDB mode - simpler startup
    if settings.use_dynamodb:
        print(f"📦 DynamoDB table: {settings.dynamodb_table_name}")
        # Verify DynamoDB connection
        try:
            from .db import get_table
            table = get_table()
            # Simple check - will fail if table doesn't exist
            print(f"✅ DynamoDB table connected: {table.name}")
        except Exception as e:
            print(f"⚠️ DynamoDB connection warning: {e}")

        yield
        print("🛑 Shutting down Filter iCal")
        return

    # SQLAlchemy mode - existing initialization
    # Database migrations are managed by Alembic
    # In Lambda, create tables if they don't exist (simpler than running alembic)
    if settings.is_lambda:
        try:
            # Import all models to ensure they're registered with Base
            from . import models  # noqa: F401
            Base.metadata.create_all(bind=engine)
            print("✅ Database tables ensured (Lambda auto-create)")
        except Exception as e:
            print(f"⚠️ Database setup warning: {e}")
    else:
        print("✅ Using Alembic for database migrations (run manually in dev)")

    # Ensure domain calendars exist (from domains.yaml configuration)
    from .services.domain_service import load_domains_config, ensure_domain_calendar_exists

    try:
        success, domains_config, error = load_domains_config(settings.domains_config_path)
        if success and domains_config:
            # Use dependency injection pattern - get session through DI
            from .core.database import get_db
            db_gen = get_db()
            session = next(db_gen)
            try:
                for domain_key in domains_config.get('domains', {}):
                    domain_success, calendar, domain_error = await ensure_domain_calendar_exists(
                        session, domain_key
                    )
                    if domain_success:
                        print(f"✅ Domain calendar '{domain_key}' ready")
                    else:
                        print(f"⚠️ Domain calendar '{domain_key}' issue: {domain_error}")
                # Commit changes to ensure they're visible to other sessions
                session.commit()
            finally:
                session.close()
    except Exception as e:
        print(f"⚠️ Domain calendar setup warning: {e}")

    # Seed domain configurations from YAML files (seed-if-empty, runs in all environments)
    if settings.should_auto_seed_empty_domains:
        print("🌱 Auto-seeding empty domains from YAML configurations...")
        try:
            from .services.domain_config_service import seed_domain_from_yaml, list_available_domain_configs
            from .services.domain_service import auto_assign_events_with_rules

            # Get available domain configurations
            domains_dir = settings.domains_config_path.parent
            available_configs = list_available_domain_configs(domains_dir)

            if available_configs:
                # Use dependency injection pattern - get session through DI
                from .core.database import get_db
                db_gen = get_db()
                session = next(db_gen)
                try:
                    # Track which domains were freshly seeded
                    freshly_seeded = []

                    for domain_key in available_configs:
                        success, message = seed_domain_from_yaml(session, domain_key)
                        if success:
                            print(f"✅ Domain '{domain_key}' configuration loaded from YAML")
                            # Track if this was a fresh seed (not "already configured")
                            if "already configured" not in message.lower():
                                freshly_seeded.append(domain_key)
                        else:
                            print(f"⚠️ Domain '{domain_key}' seeding issue: {message}")

                    # Commit changes to ensure they're visible to other sessions
                    session.commit()

                    # Apply assignment rules for freshly seeded domains
                    for domain_key in freshly_seeded:
                        print(f"🎯 Applying assignment rules for '{domain_key}'...")
                        rule_success, count, error = await auto_assign_events_with_rules(session, domain_key)
                        if rule_success:
                            print(f"✅ Applied {count} auto-assignments from rules")
                        else:
                            print(f"⚠️ Rule application warning for '{domain_key}': {error}")
                        session.commit()

                finally:
                    session.close()
            else:
                print("📋 No domain configuration files found")

        except Exception as e:
            print(f"⚠️ Domain YAML seeding warning: {e}")

    # Start background scheduler for domain calendar sync (configurable)
    if settings.should_enable_background_tasks:
        print(f"⏰ Starting background scheduler (sync every {settings.actual_sync_interval_minutes} minutes)")
        start_scheduler()
    else:
        print("⏰ Background tasks disabled (testing environment)")

    yield

    # Shutdown
    if settings.should_enable_background_tasks:
        stop_scheduler()
    print("🛑 Shutting down Filter iCal")


def create_application() -> FastAPI:
    """
    Create FastAPI application with contract-first approach.
    
    The revolutionary aspect: We override FastAPI's auto-generated spec
    with our contract, ensuring implementation matches specification exactly.
    """
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # RFC 7807 Problem Details - Global exception handler for consistent error format
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Security headers middleware
    from .core.security_headers import SecurityHeadersMiddleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Add request size limiter
    app.add_middleware(RequestSizeLimiter, max_size=10_000_000)

    # Add Content-Type validator
    app.add_middleware(ContentTypeValidator)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Accept-Language",
            "X-Requested-With"
        ],
        expose_headers=["Content-Type", "X-Total-Count"],
        max_age=600
    )
    
    # Load our custom OpenAPI specification
    openapi_spec = load_openapi_spec()
    if openapi_spec:
        def custom_openapi():
            """Override FastAPI's auto-generated OpenAPI with our contract."""
            return openapi_spec
        
        # This is the magic! Our contract defines the API behavior
        app.openapi = custom_openapi
        print("📋 Contract loaded: OpenAPI specification overrides auto-generation")
    
    # Import and include routers based on database mode
    if settings.use_dynamodb:
        # DynamoDB mode - full serverless backend
        from .routers_dynamodb import (
            admin as admin_ddb,
            domains as domains_ddb,
            domain_events as domain_events_ddb,
            domain_groups as domain_groups_ddb,
            domain_filters as domain_filters_ddb,
            domain_auth as domain_auth_ddb,
            domain_assignments as domain_assignments_ddb,
            admin_domains as admin_domains_ddb,
            admin_domain_configs as admin_domain_configs_ddb,
            ical_export as ical_export_ddb,
            app_settings as app_settings_ddb,
            filters as filters_ddb,
        )
        # Admin routes
        app.include_router(admin_ddb.router, prefix="/api", tags=["admin"])
        app.include_router(admin_domains_ddb.router, prefix="/api", tags=["admin"])
        app.include_router(admin_domain_configs_ddb.router, prefix="/api", tags=["admin"])
        # Public domain routes
        app.include_router(domains_ddb.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_events_ddb.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_groups_ddb.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_filters_ddb.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_auth_ddb.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_assignments_ddb.router, prefix="/api/domains", tags=["domains"])
        # iCal export
        app.include_router(ical_export_ddb.router, prefix="/ical", tags=["ical_export"])
        # App settings (public endpoint for UI configuration)
        app.include_router(app_settings_ddb.router, tags=["app-settings"])
        # User filters (returns empty for anonymous - user auth not yet implemented)
        app.include_router(filters_ddb.router, prefix="/api/filters", tags=["filters"])
        print("📌 Using DynamoDB routers (full serverless mode)")
    else:
        # SQLAlchemy mode - full feature set
        from .routers import (
            calendars, domains, ical_export, test, filters, domain_requests, admin,
            domain_auth, app_settings, users, auth, ical,
            domain_events, domain_groups, domain_assignment_rules, domain_filters,
            domain_config, domain_backups, domain_admins, contact
        )
        app.include_router(calendars.router, prefix="/api/calendars", tags=["calendars"])
        app.include_router(domains.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_events.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_groups.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_assignment_rules.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_filters.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_config.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_backups.router, prefix="/api/domains", tags=["domains"])
        app.include_router(domain_admins.router, prefix="/api/domains", tags=["domains"])
        app.include_router(ical_export.router, prefix="/ical", tags=["ical_export"])
        app.include_router(ical.router, prefix="/api", tags=["ical"])
        app.include_router(filters.router, prefix="/api/filters", tags=["filters"])
        app.include_router(test.router, prefix="/test", tags=["test"])
        app.include_router(domain_requests.router, prefix="/api", tags=["domain-requests"])
        app.include_router(admin.router, prefix="/api", tags=["admin"])
        app.include_router(domain_auth.router, tags=["domain-auth"])
        app.include_router(app_settings.router, tags=["app-settings"])
        app.include_router(users.router, tags=["users"])
        app.include_router(auth.router, tags=["auth"])
        app.include_router(contact.router, prefix="/api", tags=["contact"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {"status": "healthy", "app": settings.app_name}
    
    return app


# Create the application instance
app = create_application()


# For development server (Docker handles this but useful for debugging)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )