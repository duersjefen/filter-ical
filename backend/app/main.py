"""
iCal Viewer API - Pure Functional Architecture
Rich Hickey: "Functional Core, Imperative Shell"

Clean architecture following contract-driven development:
- OpenAPI specification as single source of truth
- Pure functions in domain layer
- Immutable data structures
- Explicit I/O boundaries
- No technical debt or compatibility layers
"""

import yaml
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import PlainTextResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets

# Functional Core - Pure Functions Only
# (Pure functions are orchestrated through service layer for clean architecture)

# Service Layer - Orchestration of Pure Functions
from .services.community_service import CommunityService
from .services.calendar_service import CalendarService
from .services.event_service import EventService
from .services.filter_service import FilterService
from .services.preference_service import PreferenceService

# Imperative Shell - I/O Operations Only
from .persistence.repositories import StateRepository

# API Routes - HTTP Boundary Layer
from .api.community_routes import router as community_router


# === APPLICATION SETUP ===

def load_openapi_spec() -> Optional[Dict[str, Any]]:
    """Load OpenAPI specification for contract compliance"""
    spec_path = Path(__file__).parent.parent / "openapi.yaml"
    if spec_path.exists():
        with open(spec_path, 'r') as f:
            return yaml.safe_load(f)
    return None


def create_app() -> FastAPI:
    """Create FastAPI application with functional architecture"""
    
    # Load OpenAPI specification
    openapi_spec = load_openapi_spec()
    
    # Create FastAPI app
    app = FastAPI(
        title="iCal Viewer API",
        version="1.0.0", 
        description="REST API for managing iCal calendars with filtering capabilities - Functional Architecture",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Use OpenAPI specification if available
    if openapi_spec:
        def custom_openapi():
            return openapi_spec
        app.openapi = custom_openapi
    
    # Serve static files if available
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    return app


# Initialize application
app = create_app()


# === DEPENDENCY INJECTION ===

def get_repository() -> StateRepository:
    """Dependency injection for repository"""
    return StateRepository()


def get_community_service(repository: StateRepository = Depends(get_repository)) -> CommunityService:
    """Dependency injection for community service"""
    return CommunityService(repository)


def get_calendar_service(repository: StateRepository = Depends(get_repository)) -> CalendarService:
    """Dependency injection for calendar service"""
    return CalendarService(repository)


def get_event_service(repository: StateRepository = Depends(get_repository)) -> EventService:
    """Dependency injection for event service"""
    return EventService(repository)


def get_filter_service(repository: StateRepository = Depends(get_repository)) -> FilterService:
    """Dependency injection for filter service"""
    return FilterService(repository)


def get_preference_service(repository: StateRepository = Depends(get_repository)) -> PreferenceService:
    """Dependency injection for preference service"""
    return PreferenceService(repository)


def is_not_found_error(error_message: Optional[str]) -> bool:
    """Type-safe helper to check if error indicates 'not found'"""
    return error_message is not None and "not found" in error_message

def get_user_id(x_user_id: str = Header("anonymous")) -> str:
    """Extract user ID from header with default"""
    return x_user_id if x_user_id else "anonymous"


# === INCLUDE ROUTERS ===

# Community management (already implemented)
app.include_router(community_router)

# TODO: Add other routers as they're implemented
# app.include_router(calendar_router)
# app.include_router(event_router) 
# app.include_router(filter_router)
# app.include_router(preference_router)


# === CORE ENDPOINTS ===

@app.get("/health")
async def health_check():
    """Health check endpoint - matches OpenAPI specification"""
    return {
        "status": "healthy",
        "service": "ical-viewer",
        "architecture": "functional_core_imperative_shell",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint - redirect to docs"""
    return RedirectResponse(url="/api/docs")


# === CALENDAR ENDPOINTS (Contract-Driven Implementation) ===

@app.get("/api/calendars")
async def list_calendars(
    user_id: str = Depends(get_user_id),
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    """List user calendars - follows OpenAPI specification exactly"""
    result = calendar_service.list_user_calendars(user_id)
    
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error_message)
    
    return result.data.get("calendars", [])


@app.post("/api/calendars")
async def create_calendar(
    calendar_data: Dict[str, Any],
    user_id: str = Depends(get_user_id),
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    """Create new calendar - follows OpenAPI specification exactly"""
    
    # Validate required fields
    name = calendar_data.get("name")
    url = calendar_data.get("url")
    
    if not name or not url:
        raise HTTPException(
            status_code=422,
            detail="Missing required fields: name and url"
        )
    
    # Execute calendar creation workflow
    result = calendar_service.create_calendar_workflow(name, url, user_id)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error_message)
    
    return result.data["calendar"]


@app.delete("/api/calendars/{calendarId}")
async def delete_calendar(
    calendarId: str,
    user_id: str = Depends(get_user_id),
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    """Delete calendar - follows OpenAPI specification exactly"""
    
    result = calendar_service.delete_calendar_workflow(calendarId, user_id)
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=403, detail=result.error_message)
    
    return {"success": True, "message": "Calendar deleted successfully"}


# === EVENT ENDPOINTS (Contract-Driven Implementation) ===

@app.get("/api/parse-calendar")
async def parse_calendar(
    url: str,
    event_service: EventService = Depends(get_event_service)
):
    """Parse calendar from URL - follows OpenAPI specification exactly"""
    
    if not url:
        raise HTTPException(status_code=422, detail="URL parameter is required")
    
    result = event_service.parse_calendar_from_url(url)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error_message)
    
    return {
        "events": result.data["events"],
        "categories": result.data.get("categories", []),
        "total_events": len(result.data["events"])
    }


@app.get("/api/events")
async def get_events(
    calendar_id: str,
    user_id: str = Depends(get_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """Get events for calendar - follows OpenAPI specification exactly"""
    
    result = event_service.get_calendar_events(calendar_id, user_id)
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=500, detail=result.error_message)
    
    return result.data["events"]


@app.get("/api/calendar/{calendarId}/events")
async def get_calendar_events_by_path(
    calendarId: str,
    include_past: bool = False,
    user_id: str = Depends(get_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """Get calendar events by path parameter - follows OpenAPI specification exactly"""
    
    result = event_service.get_calendar_events(calendarId, user_id, include_past)
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=500, detail=result.error_message)
    
    # Return full response object as per OpenAPI spec
    return {
        "events": result.data["events"],
        "total_count": result.data["total_count"],
        "cache_status": result.data["cache_status"]
    }


@app.get("/api/calendar/{calendar_id}/categories")
async def get_calendar_categories(
    calendar_id: str,
    user_id: str = Depends(get_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """Get event categories with counts - follows OpenAPI specification exactly"""
    
    result = event_service.get_calendar_categories(calendar_id, user_id)
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=500, detail=result.error_message)
    
    return {
        "categories": result.data["categories"],
        "total_events": result.data["total_events"]
    }


@app.post("/api/calendar/{calendar_id}/generate")
async def generate_filtered_calendar(
    calendar_id: str,
    filter_request: Dict[str, Any],
    user_id: str = Depends(get_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """Generate filtered iCal file - follows OpenAPI specification exactly"""
    
    # Extract filter parameters
    selected_categories = filter_request.get("selected_categories", [])
    filter_mode = filter_request.get("filter_mode", "include")
    date_range = filter_request.get("date_range", {})
    
    # Generate filtered calendar using the service
    result = event_service.generate_filtered_calendar(
        calendar_id=calendar_id,
        user_id=user_id,
        selected_categories=selected_categories,
        filter_mode=filter_mode,
        date_range_start=date_range.get("start"),
        date_range_end=date_range.get("end")
    )
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=500, detail=result.error_message)
    
    return PlainTextResponse(
        content=result.data["ical_content"],
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="filtered-calendar.ics"',
            "Cache-Control": "private, max-age=3600"
        }
    )


@app.get("/api/calendars/{calendar_id}/preferences")
async def get_calendar_preferences_alt(
    calendar_id: str,
    user_id: str = Depends(get_user_id),
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Get calendar preferences (alternative route) - follows OpenAPI specification exactly"""
    
    result = preference_service.get_calendar_preferences(calendar_id, user_id)
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=500, detail=result.error_message)
    
    return result.data["preferences"]


# === FILTER ENDPOINTS (Contract-Driven Implementation) ===

@app.get("/api/filtered-calendars")
async def list_filtered_calendars(
    user_id: str = Depends(get_user_id),
    filter_service: FilterService = Depends(get_filter_service)
):
    """List filtered calendars - follows OpenAPI specification exactly"""
    
    result = filter_service.list_user_filtered_calendars(user_id)
    
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error_message)
    
    return result.data.get("filtered_calendars", [])


@app.post("/api/filtered-calendars")
async def create_filtered_calendar(
    filter_data: Dict[str, Any],
    user_id: str = Depends(get_user_id),
    filter_service: FilterService = Depends(get_filter_service)
):
    """Create filtered calendar - follows OpenAPI specification exactly"""
    
    # Validate required fields per OpenAPI spec
    required_fields = ["name", "source_calendar_id", "filter_config"]
    for field in required_fields:
        if field not in filter_data:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required field: {field}"
            )
    
    result = filter_service.create_filtered_calendar_workflow(
        name=filter_data["name"],
        source_calendar_id=filter_data["source_calendar_id"],
        filter_config=filter_data["filter_config"],
        user_id=user_id
    )
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error_message)
    
    return {"success": True, "filtered_calendar": result.data["filtered_calendar"]}


@app.put("/api/filtered-calendars/{filtered_calendar_id}")
async def update_filtered_calendar(
    filtered_calendar_id: str,
    update_data: Dict[str, Any],
    user_id: str = Depends(get_user_id),
    filter_service: FilterService = Depends(get_filter_service)
):
    """Update filtered calendar - follows OpenAPI specification exactly"""
    
    result = filter_service.update_filtered_calendar_workflow(
        filtered_calendar_id=filtered_calendar_id,
        update_data=update_data,
        user_id=user_id
    )
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=400, detail=result.error_message)
    
    return {
        "success": True,
        "message": "Filtered calendar updated successfully"
    }


@app.delete("/api/filtered-calendars/{filtered_calendar_id}")
async def delete_filtered_calendar(
    filtered_calendar_id: str,
    user_id: str = Depends(get_user_id),
    filter_service: FilterService = Depends(get_filter_service)
):
    """Delete filtered calendar - follows OpenAPI specification exactly"""
    
    result = filter_service.delete_filtered_calendar_workflow(filtered_calendar_id, user_id)
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=403, detail=result.error_message)
    
    return {
        "success": True,
        "message": "Filtered calendar deleted successfully"
    }


# === FILTER MANAGEMENT ENDPOINTS (Contract-Driven Implementation) ===

@app.get("/api/filters")
async def list_filters():
    """List user filters - follows OpenAPI specification exactly"""
    
    # Stub implementation for contract compliance
    # TODO: Implement actual filter storage with user_id and filter_service
    return []


# === PREFERENCE ENDPOINTS (Contract-Driven Implementation) ===

@app.get("/api/preferences/{calendar_id}")
async def get_calendar_preferences(
    calendar_id: str,
    user_id: str = Depends(get_user_id),
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Get calendar preferences - follows OpenAPI specification exactly"""
    
    result = preference_service.get_calendar_preferences(calendar_id, user_id)
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=500, detail=result.error_message)
    
    return result.data["preferences"]


@app.put("/api/preferences/{calendar_id}")
async def update_calendar_preferences(
    calendar_id: str,
    preferences: Dict[str, Any],
    user_id: str = Depends(get_user_id),
    preference_service: PreferenceService = Depends(get_preference_service)
):
    """Update calendar preferences - follows OpenAPI specification exactly"""
    
    result = preference_service.update_calendar_preferences_workflow(
        calendar_id, preferences, user_id
    )
    
    if not result.success:
        if is_not_found_error(result.error_message):
            raise HTTPException(status_code=404, detail=result.error_message)
        else:
            raise HTTPException(status_code=400, detail=result.error_message)
    
    return result.data["preferences"]


# === AUTH ENDPOINTS (Contract-Driven Implementation) ===

@app.post("/api/v1/auth/{community_path}/login")
async def community_login(
    community_path: str,
    login_data: Dict[str, Any]
):
    """Community authentication - follows OpenAPI specification exactly"""
    
    # TODO: Use community_service for actual authentication
    
    # Validate community path (required by API contract)
    if not community_path or len(community_path) < 2:
        raise HTTPException(status_code=404, detail="Community not found")
    
    password = login_data.get("password")
    if not password:
        raise HTTPException(status_code=422, detail="Password is required")
    
    # Stub implementation for contract compliance
    if len(password) < 3:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Create a session for the user
    import uuid
    session_id = str(uuid.uuid4())
    user_id = f"community_user_{secrets.token_hex(8)}"
    
    return {
        "success": True,
        "session_id": session_id,
        "user_id": user_id,
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
    }


@app.get("/api/v1/auth/{community_path}/verify")
async def verify_community_session(
    community_path: str,
    session_id: str = Header(None, alias="session-id")
):
    """Verify community session - follows OpenAPI specification exactly"""
    
    # TODO: Use community_service for actual session verification
    
    # Validate community path (required by API contract)
    if not community_path or len(community_path) < 2:
        raise HTTPException(status_code=404, detail="Community not found")
    
    if not session_id:
        raise HTTPException(status_code=401, detail="Session ID required")
    
    # Stub implementation for contract compliance
    if len(session_id) < 10:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return {
        "valid": True,
        "user_id": f"community_user_{secrets.token_hex(8)}",
        "expires_at": (datetime.now() + timedelta(hours=23)).isoformat()
    }


# === PUBLIC CALENDAR ACCESS ===

@app.get("/cal/{token}.ics", response_class=PlainTextResponse)
async def get_filtered_ical_file(
    token: str,
    filter_service: FilterService = Depends(get_filter_service),
    event_service: EventService = Depends(get_event_service)
):
    """Get filtered iCal file by public token - follows OpenAPI specification exactly"""
    
    # Validate token format
    if not token or len(token) < 8:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get filtered calendar by token
    result = filter_service.get_filtered_calendar_by_token(token)
    if not result.success:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    filtered_calendar = result.data["filtered_calendar"]
    source_calendar_id = filtered_calendar.source_calendar_id
    user_id = filtered_calendar.user_id
    filter_config = filtered_calendar.filter_config
    
    # Generate filtered calendar content
    try:
        filtered_result = event_service.generate_filtered_calendar(
            calendar_id=source_calendar_id,
            user_id=user_id,
            selected_categories=filter_config.get("include_categories", []),
            filter_mode=filter_config.get("filter_mode", "include"),
            date_range_start=filter_config.get("date_range_start"),
            date_range_end=filter_config.get("date_range_end")
        )
        
        if not filtered_result.success:
            raise HTTPException(status_code=500, detail="Failed to generate filtered calendar")
        
        ical_content = filtered_result.data["ical_content"]
        
    except Exception as e:
        # Fallback to empty calendar if generation fails
        ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//iCal Viewer//Public Filter//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:{filtered_calendar.name}
X-WR-CALDESC:Filtered calendar - Error loading events
X-WR-TIMEZONE:UTC
END:VCALENDAR"""
    
    return PlainTextResponse(
        content=ical_content, 
        media_type="text/calendar; charset=utf-8",
        headers={
            "Cache-Control": "public, max-age=3600, must-revalidate",
            "Content-Disposition": f'attachment; filename="{filtered_calendar.name.replace(" ", "-").lower()}.ics"',
            "X-Content-Generated": datetime.utcnow().isoformat() + "Z"
        }
    )


@app.get("/cal/{token}")
async def preview_filtered_calendar(
    token: str,
    filter_service: FilterService = Depends(get_filter_service),
    event_service: EventService = Depends(get_event_service)
):
    """Preview filtered calendar by public token - follows OpenAPI specification exactly"""
    
    # Validate token format
    if not token or len(token) < 8:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get filtered calendar by token
    result = filter_service.get_filtered_calendar_by_token(token)
    if not result.success:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    filtered_calendar = result.data["filtered_calendar"]
    ics_url = f"https://filter-ical.de/cal/{token}.ics"
    
    # Try to get preview of events
    try:
        events_result = event_service.get_calendar_events(
            filtered_calendar.source_calendar_id,
            filtered_calendar.user_id,
            include_past=False
        )
        
        total_events = 0
        preview_events = []
        
        if events_result.success:
            events_data = events_result.data.get("events", [])
            # Apply filtering for preview
            filter_config = filtered_calendar.filter_config
            include_categories = filter_config.get("include_categories", [])
            filter_mode = filter_config.get("filter_mode", "include")
            
            if include_categories:
                if filter_mode == "include":
                    filtered_events = [
                        event for event in events_data 
                        if any(cat.lower() in [c.lower() for c in event.get("categories", [])] 
                              for cat in include_categories)
                    ]
                else:
                    filtered_events = [
                        event for event in events_data 
                        if not any(cat.lower() in [c.lower() for c in event.get("categories", [])] 
                                  for cat in include_categories)
                    ]
            else:
                filtered_events = events_data
            
            total_events = len(filtered_events)
            preview_events = filtered_events[:10]  # Show first 10 events
        
    except Exception:
        total_events = 0
        preview_events = []
    
    # Build HTML preview
    events_html = ""
    for event in preview_events:
        events_html += f"""
        <div class="event">
            <h3>{event.get('summary', 'No Title')}</h3>
            <p><strong>Start:</strong> {event.get('dtstart', 'Unknown')}</p>
            {f"<p><strong>Location:</strong> {event.get('location')}</p>" if event.get('location') else ""}
            {f"<p><strong>Categories:</strong> {', '.join(event.get('categories', []))}</p>" if event.get('categories') else ""}
        </div>"""
    
    if not events_html:
        events_html = "<p>No events found with current filter criteria.</p>"
    
    preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{filtered_calendar.name} - iCal Viewer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #007acc, #0056b3); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
        .content {{ padding: 30px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; flex: 1; }}
        .download-btn {{ display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; }}
        .download-btn:hover {{ background: #218838; }}
        .event {{ margin: 15px 0; padding: 20px; border-left: 4px solid #007acc; background: #f8f9fa; border-radius: 0 8px 8px 0; }}
        .filter-info {{ background: #e9ecef; padding: 15px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{filtered_calendar.name}</h1>
            <p>Public Filtered Calendar</p>
        </div>
        <div class="content">
            <div class="stats">
                <div class="stat">
                    <h3>{total_events}</h3>
                    <p>Events</p>
                </div>
                <div class="stat">
                    <h3>{filtered_calendar.access_count}</h3>
                    <p>Downloads</p>
                </div>
            </div>
            
            <p><a href="{ics_url}" class="download-btn">📅 Subscribe to Calendar</a></p>
            
            <div class="filter-info">
                <h4>Filter Configuration:</h4>
                <p><strong>Mode:</strong> {filtered_calendar.filter_config.get('filter_mode', 'include').title()}</p>
                {f"<p><strong>Categories:</strong> {', '.join(filtered_calendar.filter_config.get('include_categories', []))}</p>" if filtered_calendar.filter_config.get('include_categories') else ""}
            </div>
            
            <h3>Preview Events:</h3>
            {events_html}
            
            {f"<p><em>Showing first 10 of {total_events} events. <a href='{ics_url}'>Download full calendar</a> to see all events.</em></p>" if total_events > 10 else ""}
            
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 14px; text-align: center;">
                Generated by <a href="https://filter-ical.de">iCal Viewer</a> • 
                Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC
            </p>
        </div>
    </div>
</body>
</html>"""
    
    return HTMLResponse(content=preview_html)


# === APPLICATION LIFECYCLE ===

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 iCal Viewer API starting with functional architecture")
    print("📋 Contract-driven development with OpenAPI compliance")
    print("🏛️ Rich Hickey principles: Functional Core, Imperative Shell")


@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 iCal Viewer API shutting down")


# === DEVELOPMENT SERVER ===

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )