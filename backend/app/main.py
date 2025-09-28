"""
Main FastAPI application with contract-first development.

This follows the architectural principle from CLAUDE.md:
"OpenAPI specifications are immutable contracts that enable unlimited backend refactoring freedom"

Integrated with Docker workflow for rapid development.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
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
    # Startup - Rapid development approach
    print("🚀 Starting iCal Viewer API...")
    print(f"🌍 Environment: {settings.environment.value}")
    print("📋 Contract-first development active")
    
    # Create tables directly for rapid development (no Alembic complexity)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
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
                        session, domain_key, domains_config
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
    
    # Seed domain configurations from YAML files
    if settings.should_seed_demo_data:
        print("🌱 Development environment - loading domain configurations from YAML...")
        try:
            from .services.domain_config_service import seed_domain_from_yaml, list_available_domain_configs
            
            # Get available domain configurations
            domains_dir = settings.domains_config_path.parent
            available_configs = list_available_domain_configs(domains_dir)
            
            if available_configs:
                # Use dependency injection pattern - get session through DI
                from .core.database import get_db
                db_gen = get_db()
                session = next(db_gen)
                try:
                    for domain_key in available_configs:
                        success, error = seed_domain_from_yaml(session, domain_key)
                        if success:
                            print(f"✅ Domain '{domain_key}' configuration loaded from YAML")
                        else:
                            print(f"⚠️ Domain '{domain_key}' seeding issue: {error}")
                    # Commit changes to ensure they're visible to other sessions
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
    print("🛑 Shutting down iCal Viewer API")


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
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
    
    # Import and include routers
    from .routers import calendars, domains, ical_export, test
    app.include_router(calendars.router, prefix="/calendars", tags=["calendars"])
    app.include_router(domains.router, prefix="/domains", tags=["domains"])
    app.include_router(ical_export.router, prefix="/ical", tags=["ical_export"])
    app.include_router(test.router, prefix="/test", tags=["test"])
    
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