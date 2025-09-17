"""
FastAPI application with contract-first development
IMPERATIVE SHELL: Orchestrates pure functions, handles HTTP, manages database
Override FastAPI's OpenAPI generation with our existing specification
"""
from fastapi import FastAPI, Depends, HTTPException, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import yaml
import json

# Import database and models
from .database import get_session, create_db_and_tables
from .models import (
    Calendar, Event, FilteredCalendar, FilterMode
)

# Import pure functions (Functional Core)
from .core.ical_parser import (
    fetch_ical_content, parse_calendar_events,
    events_to_recurring_types, filter_future_events, create_ical_from_events
)
from .core.filters import (
    filter_events_by_categories, apply_saved_filter_config,
    parse_json_field, serialize_json_field
)
from .middleware.schema_validation import create_validation_middleware
import os

# Load OpenAPI specification to override FastAPI's auto-generation
def load_openapi_spec() -> Dict[str, Any]:
    """Load our contract-first OpenAPI specification"""
    spec_path = Path(__file__).parent.parent / "openapi.yaml" 
    if spec_path.exists():
        with open(spec_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

# Create FastAPI application
app = FastAPI(
    title="iCal Viewer API",
    description="Contract-driven iCal filtering and management API",
    version="2.0.0",
)

# Override OpenAPI generation with our specification
openapi_spec = load_openapi_spec()
if openapi_spec:
    def custom_openapi():
        return openapi_spec
    app.openapi = custom_openapi

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://filter-ical.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Runtime schema validation middleware (development/testing only)
enable_validation = os.getenv('ENABLE_SCHEMA_VALIDATION', 'false').lower() == 'true'
if enable_validation:
    validation_middleware = create_validation_middleware(enable_validation=True)
    app.add_middleware(validation_middleware)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_db_and_tables()
    print("🚀 iCal Viewer API starting with functional architecture")
    print("📋 Contract-driven development with OpenAPI compliance")

# Public access - no authentication required
# All calendars are stored under 'public' user
PUBLIC_USER_ID = 'public'

# Utility function for error responses
def create_error_response(detail: str) -> Dict[str, str]:
    """Create error response matching OpenAPI Error schema"""
    return {"detail": detail}

# ==============================================
# CALENDAR MANAGEMENT ENDPOINTS
# ==============================================

@app.get("/api/calendars")
async def get_calendars(
    session: Session = Depends(get_session)
):
    """Get public calendars - matches OpenAPI spec exactly"""
    calendars = session.exec(
        select(Calendar).where(Calendar.user_id == PUBLIC_USER_ID)
    ).all()
    
    # Transform to OpenAPI response format
    calendar_list = []
    for cal in calendars:
        calendar_list.append({
            "id": cal.id,
            "name": cal.name, 
            "url": cal.url,
            "user_id": cal.user_id,
            "created_at": cal.created_at.isoformat() + "Z"
        })
    
    return {"calendars": calendar_list}

@app.post("/api/calendars", status_code=201)
async def create_calendar(
    calendar_data: dict,
    session: Session = Depends(get_session)
):
    """Create new calendar - matches OpenAPI spec exactly"""
    name = calendar_data.get('name', '').strip()
    url = calendar_data.get('url', '').strip()
    
    # Validation
    if not name or len(name) < 3:
        raise HTTPException(
            status_code=400, 
            detail="Name is required and must be at least 3 characters"
        )
    if not url:
        raise HTTPException(status_code=400, detail="Calendar URL is required")
    
    # Create calendar
    new_calendar = Calendar(
        name=name,
        url=url,
        user_id=PUBLIC_USER_ID
    )
    
    session.add(new_calendar)
    session.commit()
    session.refresh(new_calendar)
    
    # Parse and store events using pure functions
    try:
        ical_content, error = fetch_ical_content(url)
        if error:
            print(f"Warning: Could not fetch calendar events: {error}")
        else:
            events_data, parse_error = parse_calendar_events(ical_content, new_calendar.id)
            if not parse_error and events_data:
                # Store events in database
                for event_data in events_data:
                    event = Event(**event_data)
                    session.add(event)
                session.commit()
                print(f"Successfully parsed {len(events_data)} events with {len(events_to_categories(events_data))} categories")
    except Exception as e:
        print(f"Warning: Could not process calendar events: {e}")
    
    # Return response matching OpenAPI schema
    return {
        "id": new_calendar.id,
        "name": new_calendar.name,
        "url": new_calendar.url, 
        "user_id": new_calendar.user_id,
        "created_at": new_calendar.created_at.isoformat() + "Z"
    }

@app.delete("/api/calendars/{calendar_id}")
async def delete_calendar(
    calendar_id: str,
    session: Session = Depends(get_session)
):
    """Delete calendar - matches OpenAPI spec exactly"""
    calendar = session.exec(
        select(Calendar).where(
            Calendar.id == calendar_id,
            Calendar.user_id == PUBLIC_USER_ID
        )
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    session.delete(calendar)
    session.commit()
    
    return Response(status_code=204)

# ==============================================
# CALENDAR DATA ENDPOINTS  
# ==============================================

@app.get("/api/calendar/{calendar_id}/events")
async def get_calendar_events(
    calendar_id: str,
    session: Session = Depends(get_session)
):
    """Get calendar event types (grouped) - matches OpenAPI spec exactly"""
    # Verify calendar ownership
    calendar = session.exec(
        select(Calendar).where(
            Calendar.id == calendar_id,
            Calendar.user_id == PUBLIC_USER_ID
        )
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get events
    events = session.exec(
        select(Event).where(Event.calendar_id == calendar_id)
    ).all()
    
    # Convert database events to dict format for pure function
    events_data = []
    for event in events:
        events_data.append({
            "id": event.id,
            "category": event.category,
            "title": event.title,
            "start": event.start,
            "end": event.end,
            "description": event.description,
            "location": event.location
        })
    
    # Use pure function to group events by recurring types (identical titles)
    grouped_events = events_to_recurring_types(events_data)
    
    return {"events": grouped_events}

@app.get("/api/calendar/{calendar_id}/raw-events")
async def get_calendar_raw_events(
    calendar_id: str,
    session: Session = Depends(get_session)
):
    """Get individual calendar events as flat array - utility endpoint"""
    # Verify calendar ownership
    calendar = session.exec(
        select(Calendar).where(
            Calendar.id == calendar_id,
            Calendar.user_id == PUBLIC_USER_ID
        )
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get events
    events = session.exec(
        select(Event).where(Event.calendar_id == calendar_id)
    ).all()
    
    # Transform to individual events format
    events_list = []
    for event in events:
        events_list.append({
            "id": event.id,
            "title": event.title,
            "start": event.start.isoformat() + "Z",
            "end": event.end.isoformat() + "Z", 
            "category": event.category,
            "description": event.description,
            "location": event.location
        })
    
    return {"events": events_list}


# ==============================================
# FILTERED CALENDARS ENDPOINTS
# ==============================================

@app.get("/api/filtered-calendars")
async def get_filtered_calendars(
    session: Session = Depends(get_session)
):
    """Get filtered calendars - matches OpenAPI spec exactly"""
    filtered_calendars = session.exec(
        select(FilteredCalendar).where(FilteredCalendar.user_id == PUBLIC_USER_ID)
    ).all()
    
    # Transform to OpenAPI response format
    calendars_list = []
    for fc in filtered_calendars:
        calendars_list.append({
            "id": fc.id,
            "name": fc.name,
            "public_token": fc.public_token,
            "calendar_url": fc.calendar_url,
            "preview_url": fc.preview_url,
            "source_calendar_id": fc.source_calendar_id,
            "filter_config": {
                "include_categories": parse_json_field(fc.include_categories, []),
                "exclude_categories": parse_json_field(fc.exclude_categories, []),
                "filter_mode": fc.filter_mode
            },
            "created_at": fc.created_at.isoformat() + "Z",
            "updated_at": fc.updated_at.isoformat() + "Z"
        })
    
    return {"filtered_calendars": calendars_list}

@app.post("/api/filtered-calendars") 
async def create_filtered_calendar(
    request_data: dict,
    session: Session = Depends(get_session)
):
    """Create filtered calendar - matches OpenAPI spec exactly"""
    source_calendar_id = request_data.get('source_calendar_id')
    name = request_data.get('name', '').strip()
    filter_config = request_data.get('filter_config', {})
    
    # Validation
    if not name or len(name) < 3:
        raise HTTPException(
            status_code=400,
            detail="Name is required and must be at least 3 characters"
        )
    
    # Verify source calendar exists and is owned by user
    source_calendar = session.exec(
        select(Calendar).where(
            Calendar.id == source_calendar_id,
            Calendar.user_id == PUBLIC_USER_ID
        )
    ).first()
    
    if not source_calendar:
        raise HTTPException(status_code=404, detail="Source calendar not found")
    
    # Create filtered calendar
    filtered_calendar = FilteredCalendar(
        name=name,
        source_calendar_id=source_calendar_id,
        user_id=PUBLIC_USER_ID,
        include_categories=serialize_json_field(filter_config.get('include_categories', [])),
        exclude_categories=serialize_json_field(filter_config.get('exclude_categories', [])),
        filter_mode=FilterMode(filter_config.get('filter_mode', 'include'))
    )
    
    session.add(filtered_calendar)
    session.commit()
    session.refresh(filtered_calendar)
    
    # Return response matching OpenAPI schema
    return {
        "id": filtered_calendar.id,
        "name": filtered_calendar.name,
        "public_token": filtered_calendar.public_token,
        "calendar_url": filtered_calendar.calendar_url,
        "preview_url": filtered_calendar.preview_url,
        "source_calendar_id": filtered_calendar.source_calendar_id,
        "filter_config": {
            "include_categories": parse_json_field(filtered_calendar.include_categories, []),
            "exclude_categories": parse_json_field(filtered_calendar.exclude_categories, []),
            "filter_mode": filtered_calendar.filter_mode
        },
        "created_at": filtered_calendar.created_at.isoformat() + "Z",
        "updated_at": filtered_calendar.updated_at.isoformat() + "Z"
    }

@app.put("/api/filtered-calendars/{filtered_calendar_id}")
async def update_filtered_calendar(
    filtered_calendar_id: str,
    request_data: dict,
    session: Session = Depends(get_session)
):
    """Update filtered calendar - matches OpenAPI spec exactly"""
    # Find filtered calendar
    filtered_calendar = session.exec(
        select(FilteredCalendar).where(
            FilteredCalendar.id == filtered_calendar_id,
            FilteredCalendar.user_id == PUBLIC_USER_ID
        )
    ).first()
    
    if not filtered_calendar:
        raise HTTPException(status_code=404, detail="Filtered calendar not found")
    
    # Update fields if provided
    if 'name' in request_data:
        name = request_data['name'].strip()
        if not name or len(name) < 3:
            raise HTTPException(
                status_code=400,
                detail="Name must be at least 3 characters"
            )
        filtered_calendar.name = name
    
    if 'filter_config' in request_data:
        filter_config = request_data['filter_config']
        filtered_calendar.include_categories = serialize_json_field(
            filter_config.get('include_categories', [])
        )
        filtered_calendar.exclude_categories = serialize_json_field(
            filter_config.get('exclude_categories', [])
        )
        filtered_calendar.filter_mode = FilterMode(
            filter_config.get('filter_mode', 'include')
        )
    
    from datetime import datetime
    filtered_calendar.updated_at = datetime.utcnow()
    
    session.add(filtered_calendar)
    session.commit()
    session.refresh(filtered_calendar)
    
    # Return updated calendar
    return {
        "id": filtered_calendar.id,
        "name": filtered_calendar.name,
        "public_token": filtered_calendar.public_token,
        "calendar_url": filtered_calendar.calendar_url,
        "preview_url": filtered_calendar.preview_url,
        "source_calendar_id": filtered_calendar.source_calendar_id,
        "filter_config": {
            "include_categories": parse_json_field(filtered_calendar.include_categories, []),
            "exclude_categories": parse_json_field(filtered_calendar.exclude_categories, []),
            "filter_mode": filtered_calendar.filter_mode
        },
        "created_at": filtered_calendar.created_at.isoformat() + "Z",
        "updated_at": filtered_calendar.updated_at.isoformat() + "Z"
    }

@app.delete("/api/filtered-calendars/{filtered_calendar_id}")
async def delete_filtered_calendar(
    filtered_calendar_id: str,
    session: Session = Depends(get_session)
):
    """Delete filtered calendar - matches OpenAPI spec exactly"""
    filtered_calendar = session.exec(
        select(FilteredCalendar).where(
            FilteredCalendar.id == filtered_calendar_id,
            FilteredCalendar.user_id == PUBLIC_USER_ID
        )
    ).first()
    
    if not filtered_calendar:
        raise HTTPException(status_code=404, detail="Filtered calendar not found")
    
    session.delete(filtered_calendar)
    session.commit()
    
    return Response(status_code=204)

# ==============================================
# PUBLIC ACCESS ENDPOINT
# ==============================================

@app.get("/cal/{token}")
async def get_public_filtered_calendar(
    token: str,
    session: Session = Depends(get_session)
):
    """Get public filtered calendar - matches OpenAPI spec exactly"""
    # Find filtered calendar by public token
    filtered_calendar = session.exec(
        select(FilteredCalendar).where(FilteredCalendar.public_token == token)
    ).first()
    
    if not filtered_calendar:
        raise HTTPException(status_code=404, detail="Public calendar not found or access token invalid")
    
    # Get source calendar events
    events = session.exec(
        select(Event).where(Event.calendar_id == filtered_calendar.source_calendar_id)
    ).all()
    
    # Convert to dict format for pure functions
    events_data = []
    for event in events:
        events_data.append({
            "id": event.id,
            "title": event.title,
            "start": event.start,
            "end": event.end,
            "category": event.category,
            "description": event.description,
            "location": event.location
        })
    
    # Apply filters using pure functions
    include_categories = parse_json_field(filtered_calendar.include_categories, [])
    exclude_categories = parse_json_field(filtered_calendar.exclude_categories, [])
    
    filtered_events = filter_events_by_categories(
        events_data,
        include_categories,
        exclude_categories, 
        filtered_calendar.filter_mode
    )
    
    # Generate iCal content using pure function
    ical_content = create_ical_from_events(filtered_events, filtered_calendar.name)
    
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename={filtered_calendar.name.replace(' ', '_')}.ics"}
    )

# Preferences endpoints removed - using default filter state only

# Saved filters endpoints removed - using default filter state only

# ==============================================
# ICAL GENERATION ENDPOINT
# ==============================================

@app.post("/api/calendar/{calendar_id}/generate")
async def generate_filtered_ical(
    calendar_id: str,
    request_data: dict,
    session: Session = Depends(get_session)
):
    """Generate filtered iCal content - matches OpenAPI spec exactly"""
    # Verify calendar ownership
    calendar = session.exec(
        select(Calendar).where(
            Calendar.id == calendar_id,
            Calendar.user_id == PUBLIC_USER_ID
        )
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get request parameters
    selected_categories = request_data.get('selected_categories', [])
    filter_mode = request_data.get('filter_mode', 'include')
    
    if filter_mode not in ['include', 'exclude']:
        raise HTTPException(status_code=400, detail="filter_mode must be 'include' or 'exclude'")
    
    # Get calendar events
    events = session.exec(
        select(Event).where(Event.calendar_id == calendar_id)
    ).all()
    
    # Convert to dict format for pure functions
    events_data = []
    for event in events:
        events_data.append({
            "id": event.id,
            "title": event.title,
            "start": event.start,
            "end": event.end,
            "category": event.category,
            "description": event.description,
            "location": event.location
        })
    
    # Apply category filter using pure function
    if filter_mode == 'include':
        filtered_events = filter_events_by_categories(
            events_data, selected_categories, [], filter_mode
        )
    else:
        filtered_events = filter_events_by_categories(
            events_data, [], selected_categories, filter_mode
        )
    
    # Generate iCal content using pure function
    ical_content = create_ical_from_events(filtered_events, calendar.name)
    
    return Response(
        content=ical_content,
        media_type="text/calendar"
    )

# ==============================================
# HEALTH CHECK ENDPOINT
# ==============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "iCal Viewer API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)