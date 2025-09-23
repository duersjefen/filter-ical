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
    print("📋 Contract-first development active")
    
    # Create tables directly for rapid development (no Alembic complexity)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Start background scheduler for domain calendar sync
    start_scheduler()
    
    yield
    
    # Shutdown
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
    app.include_router(calendars.router, prefix="/api/calendars", tags=["calendars"])
    app.include_router(domains.router, prefix="/api/domains", tags=["domains"])
    app.include_router(ical_export.router, prefix="/ical", tags=["ical_export"])
    app.include_router(test.router, prefix="/api/test", tags=["test"])
    
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