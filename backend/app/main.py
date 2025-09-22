"""
FastAPI application with contract-first development
IMPERATIVE SHELL: Orchestrates pure functions, handles HTTP, manages database
Override FastAPI's OpenAPI generation with our existing specification
"""
from fastapi import FastAPI, Depends, HTTPException, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, col, or_, and_
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import json

# Import database and models
from .database import get_session, get_session_sync, create_db_and_tables
from .models import (
    Calendar, Event, FilteredCalendar, Group, EventTypeGroup
)

# Import pure functions (Functional Core)
from .core.ical_parser import (
    fetch_ical_content, parse_calendar_events,
    events_to_recurring_types, filter_future_events, filter_recent_and_future_events, 
    create_ical_from_events, events_to_event_types, split_ungrouped_events_by_type
)
from .core.filters import (
    parse_json_field, serialize_json_field
)
from .core.domains import (
    load_domains_config, get_available_domains as get_domains_list, get_domain_config,
    validate_domain_config, is_valid_domain_id, domain_has_groups
)
from .data.group import (
    build_group_tree, get_event_types_for_group, validate_group_hierarchy
)
from .core.domain_calendar import (
    get_domain_calendar_id, load_domain_calendar_config, is_domain_calendar,
    extract_domain_from_calendar_id, generate_calendar_id, detect_domain_from_url,
    get_calendar_domain_id
)
from .core.cache import (
    should_update_cache, get_cached_content, create_cache_data, 
    needs_cache_update, detect_content_change
)
from .core.filter_regeneration import mark_all_dependent_filters_for_regeneration, get_filtered_ical_cache_first
from .middleware.schema_validation import create_validation_middleware
from .core.background_tasks import background_manager
from .core.domain_setup import ensure_domain_calendars_exist
from .core.demo_data import seed_demo_data, should_seed_demo_data
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

# Runtime schema validation middleware (enabled by default, disabled in production)
is_production = os.getenv('PRODUCTION', 'false').lower() == 'true'
enable_validation = not is_production and os.getenv('DISABLE_SCHEMA_VALIDATION', 'false').lower() != 'true'

if enable_validation:
    validation_middleware = create_validation_middleware(enable_validation=True)
    app.add_middleware(validation_middleware)
    print("🔍 Schema validation middleware enabled")
else:
    print("⚠️ Schema validation middleware disabled (production mode)")

# Create database tables and start background tasks on startup
@app.on_event("startup")
def startup_event():
    create_db_and_tables()
    
    # Check environment mode
    is_testing = os.getenv('TESTING') == 'true'
    is_dev_mode = os.getenv('DEV_MODE') == 'true'
    disable_background_tasks = os.getenv('DISABLE_BACKGROUND_TASKS') == 'true'
    
    if is_testing:
        print("🧪 Running in test mode - background tasks disabled")
    elif disable_background_tasks:
        print("🔧 Development mode - background tasks disabled for stability")
        ensure_domain_calendars_exist()
        
        # Seed demo data if needed (for showcasing)
        if should_seed_demo_data():
            print("🎭 Seeding demo data for showcasing...")
            if seed_demo_data():
                print("✅ Demo data seeded successfully")
            else:
                print("❌ Failed to seed demo data")
        else:
            print("📋 Demo data already exists")
    else:
        # Production or full development mode
        ensure_domain_calendars_exist()
        
        # Seed demo data if needed (for showcasing)
        if should_seed_demo_data():
            print("🎭 Seeding demo data for showcasing...")
            if seed_demo_data():
                print("✅ Demo data seeded successfully")
            else:
                print("❌ Failed to seed demo data")
        else:
            print("📋 Demo data already exists")
        
        background_manager.start()
        print("⏰ Background calendar updates every 5 minutes")
    
    mode_info = "🧪 TEST" if is_testing else ("🔧 DEV" if is_dev_mode else "🚀 PROD")
    print(f"{mode_info} iCal Viewer API starting with functional architecture")
    print("📋 Contract-driven development with OpenAPI compliance")


# Stop background tasks on shutdown
@app.on_event("shutdown") 
def shutdown_event():
    # Only stop background tasks if they were started
    is_testing = os.getenv('TESTING') == 'true'
    disable_background_tasks = os.getenv('DISABLE_BACKGROUND_TASKS') == 'true'
    
    if not is_testing and not disable_background_tasks:
        background_manager.stop()
        print("🛑 Background tasks stopped")
    
    print("🛑 iCal Viewer API shutting down")

# Public access - no authentication required
# Default user ID for backward compatibility
PUBLIC_USER_ID = 'public'

# Utility function for dynamic user ID based on username parameter
def get_user_id(username: Optional[str] = None) -> str:
    """Get user ID from username parameter, fallback to 'public'"""
    if username and username.strip():
        return username.strip()
    return PUBLIC_USER_ID

# Utility function for error responses
def create_error_response(detail: str) -> Dict[str, str]:
    """Create error response matching OpenAPI Error schema"""
    return {"detail": detail}


def create_calendar_with_smart_id(name: str, url: str, user_id: str, domain_id: Optional[str] = None) -> Calendar:
    """
    Create calendar with appropriate ID generation.
    Helper function that properly handles domain calendar detection and ID generation.
    
    Args:
        name: Calendar name
        url: Calendar URL
        user_id: User ID
        domain_id: Optional domain ID (auto-detected if not provided)
        
    Returns:
        Calendar object with appropriate ID
    """
    # Auto-detect domain if not provided
    if domain_id is None:
        domain_id = detect_domain_from_url(url)
    
    # Generate appropriate ID
    calendar_id = generate_calendar_id(domain_id)
    
    return Calendar(
        id=calendar_id,
        name=name,
        url=url,
        user_id=user_id,
        domain_id=domain_id
    )


def fetch_calendar_data_cached(calendar, session) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch calendar data using cache-first approach.
    I/O Shell function - orchestrates pure cache and fetch functions.
    
    Args:
        calendar: Calendar object with cache fields
        session: Database session for updating cache
        
    Returns:
        Tuple of (ical_content, error_message)
    """
    # Try to get cached content first
    cached_content = get_cached_content(calendar)
    if cached_content:
        print(f"📦 Using cached content for calendar {calendar.id}")
        return cached_content, None
    
    # Cache miss or expired - fetch fresh content
    print(f"🔄 Fetching fresh content for calendar {calendar.id}")
    fresh_content, error = fetch_ical_content(calendar.url)
    
    if error:
        return None, error
    
    # Update cache if content changed
    if needs_cache_update(calendar, fresh_content):
        print(f"💾 Updating cache for calendar {calendar.id}")
        cache_data = create_cache_data(fresh_content)
        
        # Update calendar cache fields
        for key, value in cache_data.items():
            setattr(calendar, key, value)
        
        session.add(calendar)
        session.commit()
        
        # Mark dependent filtered calendars for regeneration
        mark_filtered_calendars_for_regeneration(calendar.id, session)
    
    return fresh_content, None


def mark_filtered_calendars_for_regeneration(source_calendar_id: str, session):
    """
    Mark all filtered calendars that depend on source calendar for regeneration.
    I/O Shell function - delegates to pure filter regeneration module.
    
    Args:
        source_calendar_id: ID of the source calendar that changed
        session: Database session
    """
    mark_all_dependent_filters_for_regeneration(source_calendar_id, session)

# ==============================================
# MONITORING ENDPOINTS
# ==============================================

@app.get("/api/system/status")
async def get_system_status():
    """Get system status including background tasks and cache statistics"""
    session = get_session_sync()
    try:
        # Get basic statistics
        total_calendars = len(session.exec(select(Calendar)).all())
        domain_calendars = len(session.exec(select(Calendar).where(Calendar.domain_id != None)).all())
        cached_calendars = len(session.exec(select(Calendar).where(Calendar.cached_ical_content != None)).all())
        pending_regenerations = len(session.exec(select(FilteredCalendar).where(FilteredCalendar.needs_regeneration == True)).all())
        
        return {
            "status": "healthy",
            "statistics": {
                "total_calendars": total_calendars,
                "domain_calendars": domain_calendars,
                "cached_calendars": cached_calendars,
                "pending_filter_regenerations": pending_regenerations
            },
            "background_tasks": background_manager.get_status()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        session.close()


# ==============================================
# CALENDAR MANAGEMENT ENDPOINTS
# ==============================================

@app.get("/api/calendars")
async def get_calendars(
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get calendars for user - matches OpenAPI spec exactly"""
    user_id = get_user_id(username)
    
    # Get only user's personal calendars (exclude domain calendars from personal lists)
    calendars = session.exec(
        select(Calendar).where(
            and_(
                Calendar.user_id == user_id,
                Calendar.domain_id == None  # Exclude domain calendars from personal lists
            )
        )
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
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Create new calendar - matches OpenAPI spec exactly"""
    name = calendar_data.get('name', '').strip()
    url = calendar_data.get('url', '').strip()
    user_id = get_user_id(username)
    
    # Validation
    if not name or len(name) < 3:
        raise HTTPException(
            status_code=400, 
            detail="Name is required and must be at least 3 characters"
        )
    if not url:
        raise HTTPException(status_code=400, detail="Calendar URL is required")
    
    # Create calendar with smart ID generation
    new_calendar = create_calendar_with_smart_id(name, url, user_id)
    
    # Protect domain calendars: They can only be created by system startup, not via API
    if new_calendar.id.startswith('cal_domain_'):
        raise HTTPException(
            status_code=400, 
            detail="Domain calendars are system-managed and cannot be created via API. They are automatically created from domains.yaml configuration."
        )
    
    # Check if calendar with this ID already exists
    existing_calendar = session.get(Calendar, new_calendar.id)
    if existing_calendar:
        # Return existing calendar instead of creating duplicate
        return {
            "id": existing_calendar.id,
            "name": existing_calendar.name,
            "url": existing_calendar.url,
            "user_id": existing_calendar.user_id,
            "created_at": existing_calendar.created_at.isoformat() if existing_calendar.created_at else None
        }
    
    session.add(new_calendar)
    session.commit()
    session.refresh(new_calendar)
    
    # Parse and store events using pure functions
    event_processing_warnings = []
    
    try:
        ical_content, error = fetch_ical_content(url)
        if error:
            warning_msg = f"Could not fetch calendar content: {error}"
            print(f"Warning: {warning_msg}")
            event_processing_warnings.append(warning_msg)
        else:
            events_data, parse_error = parse_calendar_events(ical_content, new_calendar.id)
            if parse_error:
                warning_msg = f"Could not parse calendar events: {parse_error}"
                print(f"Warning: {warning_msg}")
                event_processing_warnings.append(warning_msg)
            elif not events_data or len(events_data) == 0:
                warning_msg = "Calendar URL is valid but contains no events"
                print(f"Warning: {warning_msg}")
                event_processing_warnings.append(warning_msg)
            else:
                # Store events in database
                for event_data in events_data:
                    event = Event(**event_data)
                    session.add(event)
                session.commit()
                print(f"Successfully parsed {len(events_data)} events with {len(events_to_recurring_types(events_data))} event types")
    except Exception as e:
        warning_msg = f"Could not process calendar events: {str(e)}"
        print(f"Warning: {warning_msg}")
        event_processing_warnings.append(warning_msg)
    
    # Return response matching OpenAPI schema with optional warnings
    response = {
        "id": new_calendar.id,
        "name": new_calendar.name,
        "url": new_calendar.url, 
        "user_id": new_calendar.user_id,
        "created_at": new_calendar.created_at.isoformat() + "Z"
    }
    
    # Include warnings if any event processing issues occurred
    if event_processing_warnings:
        response["warnings"] = event_processing_warnings
    
    return response

@app.delete("/api/calendars/{calendar_id}")
async def delete_calendar(
    calendar_id: str,
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Delete calendar - matches OpenAPI spec exactly"""
    user_id = get_user_id(username)
    calendar = session.exec(
        select(Calendar).where(
            Calendar.id == calendar_id,
            Calendar.user_id == user_id
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
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get calendar event types (grouped) - matches OpenAPI spec exactly"""
    print("🚨 DEDUPLICATION FIX IS ACTIVE!")
    # Verify calendar access (personal calendars or domain calendars)
    user_id = get_user_id(username)
    calendar = session.exec(
        select(Calendar).where(
            Calendar.id == calendar_id,
            or_(
                Calendar.user_id == user_id,
                Calendar.domain_id != None  # Allow access to all domain calendars
            )
        )
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get events
    events = session.exec(
        select(Event).where(Event.calendar_id == calendar_id)
    ).all()
    
    # Convert database events to dict format for pure function (keep datetime objects)
    events_data = []
    for event in events:
        events_data.append({
            "id": event.id,
            "event_type": event.title,
            "title": event.title,
            "start": event.start,
            "end": event.end,
            "description": event.description,
            "location": event.location
        })
    
    # KISS: Simple deduplication using string-based event fingerprint
    seen_events = set()
    deduplicated_events = []
    
    for event in events_data:
        # Create simple string fingerprint: title + start time + end time
        fingerprint = f"{event['title']}-{event['start']}-{event['end']}"
        
        if fingerprint not in seen_events:
            seen_events.add(fingerprint)
            deduplicated_events.append(event)
    
    print(f"🔍 Deduplication: {len(events_data)} → {len(deduplicated_events)} events")
    
    # Use pure function to group events by recurring types (identical titles)
    grouped_events = events_to_recurring_types(deduplicated_events)
    
    # Return with proper OpenAPI contract structure
    return {"events": grouped_events}

@app.get("/api/calendar/{calendar_id}/raw-events")
async def get_calendar_raw_events(
    calendar_id: str,
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get individual calendar events as flat array - utility endpoint"""
    # Verify calendar ownership
    user_id = get_user_id(username)
    calendar = session.exec(
        select(Calendar).where(
            Calendar.id == calendar_id,
            Calendar.user_id == user_id
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
            "event_type": event.title,
            "description": event.description,
            "location": event.location
        })
    
    return {"events": events_list}


@app.get("/api/calendar/{calendar_id}/groups")
async def get_calendar_groups(
    calendar_id: str,
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get calendar event types organized by groups - matches OpenAPI spec exactly"""
    # Verify calendar access (personal calendars or domain calendars)
    user_id = get_user_id(username)
    calendar = session.exec(
        select(Calendar).where(
            Calendar.id == calendar_id,
            or_(
                Calendar.user_id == user_id,
                Calendar.domain_id != None  # Allow access to all domain calendars
            )
        )
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Determine domain_id for this calendar using clean logic
    domain_id = get_calendar_domain_id(calendar)
    
    # Load domain configuration to check if groups are enabled
    has_groups_enabled = False
    if domain_id:
        try:
            config_path = Path(__file__).parent.parent / "config" / "domains.yaml"
            domains_config = load_domains_config(str(config_path))
            has_groups_enabled = domain_has_groups(domains_config, domain_id)
        except Exception:
            has_groups_enabled = False
    
    if not has_groups_enabled:
        return {"has_groups": False, "groups": {}, "ungrouped_events": []}
    
    # Get all groups for this domain
    domain_groups = session.exec(
        select(Group).where(Group.domain_id == domain_id)
    ).all()
    
    if not domain_groups:
        return {"has_groups": False, "groups": {}, "ungrouped_events": []}
    
    # Validate group hierarchy for safety
    is_valid, error_msg = validate_group_hierarchy(domain_groups)
    if not is_valid:
        raise HTTPException(status_code=500, detail=f"Invalid group hierarchy: {error_msg}")
    
    # Get all events for this calendar
    calendar_events = session.exec(
        select(Event).where(Event.calendar_id == calendar_id)
    ).all()
    
    # Get all event type group assignments for this domain
    event_type_groups = session.exec(
        select(EventTypeGroup).where(EventTypeGroup.domain_id == domain_id)
    ).all()
    
    # Build events by group mapping
    events_by_group = {}
    assigned_event_categories = set()
    
    for group in domain_groups:
        group_event_types = get_event_types_for_group(group.id, event_type_groups)
        assigned_event_categories.update(group_event_types)
        
        # Find events matching this group's event types
        group_events = [
            event for event in calendar_events 
            if event.category in group_event_types
        ]
        events_by_group[group.id] = group_events
    
    # Build nested group tree structure
    nested_groups = build_group_tree(domain_groups, events_by_group)
    
    # Find ungrouped events (events whose categories are not assigned to any group)
    ungrouped_events = [
        event for event in calendar_events 
        if event.category not in assigned_event_categories
    ]
    
    # Transform ungrouped events to API response format
    ungrouped_events_formatted = [
        {
            'id': event.id,
            'title': event.title,
            'start': event.start.isoformat() + "Z" if hasattr(event.start, 'isoformat') else event.start,
            'end': event.end.isoformat() + "Z" if hasattr(event.end, 'isoformat') else event.end,
            'event_type': event.category,
            'description': event.description,
            'location': event.location
        }
        for event in ungrouped_events
    ]
    
    return {
        "has_groups": True, 
        "groups": nested_groups,
        "ungrouped_events": ungrouped_events_formatted
    }


# Duplicate route removed - this conflicted with the proper grouped events endpoint
# Individual event functionality is available via /api/calendar/{calendar_id}/raw-events


# Manual event assignment endpoints removed - groups now contain event types, not individual events


# Manual event removal endpoints removed - groups now contain event types, not individual events
# Event assignment is now handled through EventTypeGroup model in the database migration


# ==============================================
# FILTERED CALENDARS ENDPOINTS
# ==============================================

@app.get("/api/filtered-calendars")
async def get_filtered_calendars(
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get filtered calendars - matches OpenAPI spec exactly"""
    user_id = get_user_id(username)
    filtered_calendars = session.exec(
        select(FilteredCalendar).where(FilteredCalendar.user_id == user_id)
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
            "selected_groups": parse_json_field(fc.selected_groups, []),
            "selected_events": parse_json_field(fc.selected_events, []),
            "created_at": fc.created_at.isoformat() + "Z",
            "updated_at": fc.updated_at.isoformat() + "Z"
        })
    
    return {"filtered_calendars": calendars_list}

@app.post("/api/filtered-calendars") 
async def create_filtered_calendar(
    request_data: dict,
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Create filtered calendar - matches OpenAPI spec exactly"""
    source_calendar_id = request_data.get('source_calendar_id')
    name = request_data.get('name', '').strip()
    selected_groups = request_data.get('selected_groups', [])
    selected_events = request_data.get('selected_events', [])
    user_id = get_user_id(username)
    
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
            Calendar.user_id == user_id
        )
    ).first()
    
    if not source_calendar:
        raise HTTPException(status_code=404, detail="Source calendar not found")
    
    # Create filtered calendar
    filtered_calendar = FilteredCalendar(
        name=name,
        source_calendar_id=source_calendar_id,
        user_id=user_id,
        selected_groups=serialize_json_field(selected_groups),
        selected_events=serialize_json_field(selected_events),
        needs_regeneration=True  # Flag for initial iCal generation
    )
    
    session.add(filtered_calendar)
    session.commit()
    session.refresh(filtered_calendar)
    
    # Generate initial cached iCal content
    print(f"🔄 Generating initial iCal content for filtered calendar {filtered_calendar.id}")
    ical_content, error = get_filtered_ical_cache_first(filtered_calendar, session)
    
    # Return response matching OpenAPI schema
    return {
        "id": filtered_calendar.id,
        "name": filtered_calendar.name,
        "public_token": filtered_calendar.public_token,
        "calendar_url": filtered_calendar.calendar_url,
        "preview_url": filtered_calendar.preview_url,
        "source_calendar_id": filtered_calendar.source_calendar_id,
        "selected_groups": parse_json_field(filtered_calendar.selected_groups, []),
        "selected_events": parse_json_field(filtered_calendar.selected_events, []),
        "created_at": filtered_calendar.created_at.isoformat() + "Z",
        "updated_at": filtered_calendar.updated_at.isoformat() + "Z"
    }

@app.put("/api/filtered-calendars/{filtered_calendar_id}")
async def update_filtered_calendar(
    filtered_calendar_id: str,
    request_data: dict,
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Update filtered calendar - matches OpenAPI spec exactly"""
    user_id = get_user_id(username)
    
    # Find filtered calendar
    filtered_calendar = session.exec(
        select(FilteredCalendar).where(
            FilteredCalendar.id == filtered_calendar_id,
            FilteredCalendar.user_id == user_id
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
    
    selection_changed = False
    if 'selected_groups' in request_data or 'selected_events' in request_data:
        if 'selected_groups' in request_data:
            filtered_calendar.selected_groups = serialize_json_field(
                request_data['selected_groups']
            )
        if 'selected_events' in request_data:
            filtered_calendar.selected_events = serialize_json_field(
                request_data['selected_events']
            )
        filtered_calendar.needs_regeneration = True  # Mark for cache regeneration
        selection_changed = True
    
    from datetime import datetime
    filtered_calendar.updated_at = datetime.utcnow()
    
    session.add(filtered_calendar)
    session.commit()
    session.refresh(filtered_calendar)
    
    # Regenerate cache if selection changed
    if selection_changed:
        print(f"🔄 Regenerating iCal content for updated filtered calendar {filtered_calendar.id}")
        ical_content, error = get_filtered_ical_cache_first(filtered_calendar, session)
    
    # Return updated calendar
    return {
        "id": filtered_calendar.id,
        "name": filtered_calendar.name,
        "public_token": filtered_calendar.public_token,
        "calendar_url": filtered_calendar.calendar_url,
        "preview_url": filtered_calendar.preview_url,
        "source_calendar_id": filtered_calendar.source_calendar_id,
        "selected_groups": parse_json_field(filtered_calendar.selected_groups, []),
        "selected_events": parse_json_field(filtered_calendar.selected_events, []),
        "created_at": filtered_calendar.created_at.isoformat() + "Z",
        "updated_at": filtered_calendar.updated_at.isoformat() + "Z"
    }

@app.delete("/api/filtered-calendars/{filtered_calendar_id}")
async def delete_filtered_calendar(
    filtered_calendar_id: str,
    username: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Delete filtered calendar - matches OpenAPI spec exactly"""
    user_id = get_user_id(username)
    
    filtered_calendar = session.exec(
        select(FilteredCalendar).where(
            FilteredCalendar.id == filtered_calendar_id,
            FilteredCalendar.user_id == user_id
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
@app.get("/cal/{token}.ics")
async def get_public_filtered_calendar(
    token: str,
    session: Session = Depends(get_session)
):
    """Get public filtered calendar with cache-first approach - matches OpenAPI spec exactly"""
    # Remove .ics extension if present for token lookup
    clean_token = token.replace('.ics', '') if token.endswith('.ics') else token
    
    # Find filtered calendar by public token
    filtered_calendar = session.exec(
        select(FilteredCalendar).where(FilteredCalendar.public_token == clean_token)
    ).first()
    
    if not filtered_calendar:
        raise HTTPException(status_code=404, detail="Public calendar not found or access token invalid")
    
    # Use cache-first approach for iCal content generation
    ical_content, error = get_filtered_ical_cache_first(filtered_calendar, session)
    
    if error:
        raise HTTPException(status_code=500, detail=f"Failed to generate calendar content: {error}")
    
    if not ical_content:
        raise HTTPException(status_code=500, detail="No calendar content available")
    
    # Return cached or freshly generated iCal content
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
    # Verify calendar access (personal calendars or domain calendars)
    calendar = session.exec(
        select(Calendar).where(
            Calendar.id == calendar_id,
            or_(
                Calendar.user_id == PUBLIC_USER_ID,
                Calendar.domain_id != None  # Allow access to all domain calendars
            )
        )
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get request parameters (supporting both groups and individual events)
    selected_groups = request_data.get('selected_groups', [])
    selected_events = request_data.get('selected_events', [])
    
    # Get all events for calendar
    events = session.exec(
        select(Event).where(Event.calendar_id == calendar_id)
    ).all()
    
    # Build final event list based on groups + individual events + backward compatibility
    final_events = []
    
    if selected_groups:
        # Add all events from selected groups (by event types)
        # First, get all event types that belong to selected groups
        group_event_types = session.exec(
            select(EventTypeGroup.event_type)
            .where(col(EventTypeGroup.group_id).in_(selected_groups))
        ).all()
        
        # Then, get all events that have those event types
        if group_event_types:
            group_events = session.exec(
                select(Event)
                .where(col(Event.category).in_(group_event_types))
                .where(Event.calendar_id == calendar_id)
            ).all()
            final_events.extend(group_events)
    
    if selected_events:
        # Add individually selected events
        individual_events = [e for e in events if e.id in selected_events]
        final_events.extend(individual_events)
    
    # Remove duplicates when combining groups and individual events
    if selected_groups or selected_events:
        final_events = list({e.id: e for e in final_events}.values())
    else:
        # If no selection made, return empty calendar (no events)
        final_events = []
    
    # Convert to dict format for pure functions
    events_data = []
    for event in final_events:
        events_data.append({
            "id": event.id,
            "title": event.title,
            "start": event.start,
            "end": event.end,
            "event_type": event.title,
            "description": event.description,
            "location": event.location
        })
    
    # No need for additional filtering - already done above
    filtered_events = events_data
    
    # Generate iCal content using pure function
    ical_content = create_ical_from_events(filtered_events, calendar.name)
    
    return Response(
        content=ical_content,
        media_type="text/calendar"
    )

# ==============================================
# DOMAIN CONFIGURATION ENDPOINTS
# ==============================================

@app.get("/api/domains")
async def list_available_domains():
    """Get available domains - matches OpenAPI spec exactly"""
    try:
        # Load domain configuration from file
        config_path = Path(__file__).parent.parent / "config" / "domains.yaml"
        domains_config = load_domains_config(str(config_path))
        
        # Get available domains using pure function
        domains = get_domains_list(domains_config)
        
        return {"domains": domains}
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=500, 
            detail="Domain configuration file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load domain configuration: {str(e)}"
        )

@app.get("/api/domains/{domain_id}")
async def get_domain_configuration(domain_id: str):
    """Get domain configuration - matches OpenAPI spec exactly"""
    # Validate domain ID format
    if not is_valid_domain_id(domain_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid domain ID format"
        )
    
    try:
        # Load domain configuration from file
        config_path = Path(__file__).parent.parent / "config" / "domains.yaml"
        domains_config = load_domains_config(str(config_path))
        
        # Get specific domain configuration using pure function
        domain_config = get_domain_config(domains_config, domain_id)
        
        if not domain_config:
            raise HTTPException(
                status_code=404,
                detail=f"Domain '{domain_id}' not found"
            )
        
        # Validate domain configuration
        is_valid, error_message = validate_domain_config(domain_config)
        if not is_valid:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid domain configuration: {error_message}"
            )
        
        return domain_config
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Domain configuration file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load domain configuration: {str(e)}"
        )


@app.get("/api/domains/{domain_id}/events")
async def get_domain_events(domain_id: str, event_type: Optional[str] = None):
    """Get real-time events for a domain - matches OpenAPI spec exactly"""
    # Validate domain ID format
    if not is_valid_domain_id(domain_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid domain ID format: {domain_id}"
        )
    
    try:
        # Load domain configuration
        config_path = Path(__file__).parent.parent / "config" / "domains.yaml"
        domains_config = load_domains_config(str(config_path))
        
        # Get specific domain configuration
        domain_config = get_domain_config(domains_config, domain_id)
        if not domain_config:
            raise HTTPException(
                status_code=404,
                detail=f"Domain '{domain_id}' not found"
            )
        
        # Fetch fresh iCal content directly from source
        calendar_url = domain_config.get('calendar_url', '')
        if not calendar_url:
            raise HTTPException(
                status_code=500,
                detail=f"Domain '{domain_id}' has no calendar URL configured"
            )
        
        # Fetch and parse iCal content in real-time
        ical_content, fetch_error = fetch_ical_content(calendar_url)
        if fetch_error or not ical_content:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch calendar data: {fetch_error or 'No content returned'}"
            )
        
        # Parse events from iCal content
        domain_calendar_id = f"domain_{domain_id}"
        events_data, parse_error = parse_calendar_events(ical_content, domain_calendar_id)
        if parse_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse calendar data: {parse_error}"
            )
        
        # Apply consistent filtering: only recent (1 week) + future events
        filtered_events_data = filter_recent_and_future_events(events_data)
        
        # Group events by event type
        events_by_type = {}
        for event in filtered_events_data:
            event_type_name = event.get('event_type', 'Unknown')
            if event_type_name not in events_by_type:
                events_by_type[event_type_name] = {
                    'count': 0,
                    'events': []
                }
            events_by_type[event_type_name]['count'] += 1
            events_by_type[event_type_name]['events'].append(event)
        
        # Apply event_type filter if specified
        if event_type:
            if event_type in events_by_type:
                filtered_events = events_by_type[event_type]['events']
            else:
                filtered_events = []
            events_response = filtered_events
        else:
            events_response = events_by_type
        
        # Create metadata response
        now = datetime.utcnow()
        cache_expires = now + timedelta(minutes=5)  # 5-minute cache
        
        metadata = {
            'domain_id': domain_id,
            'last_updated': now.isoformat() + 'Z',
            'total_events': len(filtered_events_data),
            'source_url': calendar_url,
            'cache_expires': cache_expires.isoformat() + 'Z'
        }
        
        return {
            'events': events_response,
            'metadata': metadata
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Domain configuration file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get domain events: {str(e)}"
        )


@app.get("/api/domains/{domain_id}/groups")
async def get_domain_groups(domain_id: str, session: Session = Depends(get_session)):
    """Get domain-specific event groups - matches OpenAPI spec exactly"""
    print(f"🔍 get_domain_groups called for domain: {domain_id}")
    # Validate domain ID format
    if not is_valid_domain_id(domain_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid domain ID format: {domain_id}"
        )
    
    try:
        # Load domain configuration
        config_path = Path(__file__).parent.parent / "config" / "domains.yaml"
        domains_config = load_domains_config(str(config_path))
        
        # Check if domain exists
        domain_config = get_domain_config(domains_config, domain_id)
        if not domain_config:
            raise HTTPException(
                status_code=404,
                detail=f"Domain '{domain_id}' not found"
            )
        
        # Check if domain has groups enabled
        has_groups = domain_has_groups(domains_config, domain_id)
        if not has_groups:
            return {
                'has_groups': False,
                'domain_id': domain_id,
                'groups': {},
                'ungrouped_event_types': []
            }
        
        # Get real-time events for this domain using the same logic as events endpoint
        # Get calendar URL from domain config
        calendar_url = domain_config.get('calendar_url', '')
        if not calendar_url:
            raise HTTPException(
                status_code=500,
                detail=f"Domain '{domain_id}' has no calendar URL configured"
            )
        
        try:
            # Fetch and parse iCal content in real-time (same as events endpoint)
            ical_content, fetch_error = fetch_ical_content(calendar_url)
            if fetch_error or not ical_content:
                print(f"Warning: Failed to fetch domain events for {domain_id}: {fetch_error}")
                events_by_type = {}
            else:
                # Parse events from iCal content
                domain_calendar_id = f"domain_{domain_id}"
                events_data, parse_error = parse_calendar_events(ical_content, domain_calendar_id)
                if parse_error:
                    print(f"Warning: Failed to parse domain events for {domain_id}: {parse_error}")
                    events_by_type = {}
                else:
                    # Apply consistent filtering: only recent (1 week) + future events
                    filtered_events_data = filter_recent_and_future_events(events_data)
                    # Convert to event types format (same as events endpoint)
                    events_by_type = events_to_event_types(filtered_events_data)
                    
                    print(f"🔍 Debug: Found {len(events_by_type)} event types in domain {domain_id}")
                    for event_type, data in list(events_by_type.items())[:3]:  # Show first 3
                        print(f"  {event_type}: {data.get('count', 0) if isinstance(data, dict) else 0} events")
                
        except Exception as e:
            # If fetching fails, return empty groups with no events
            print(f"Warning: Failed to fetch domain events for {domain_id}: {e}")
            events_by_type = {}
        
        # Get groups for this domain
        groups_query = select(Group).where(Group.domain_id == domain_id)
        domain_groups = session.exec(groups_query).all()
        
        # Build groups with real-time event counts
        all_assigned_event_types = set()
        
        groups_dict = {}
        for group in domain_groups:
            # Get event type assignments for this group
            assignments_query = select(EventTypeGroup).where(
                EventTypeGroup.group_id == group.id
            )
            assignments = session.exec(assignments_query).all()
            
            # Create event types dict for this group with real counts
            # Only include assignments for event types that have recent+future events
            event_types = {}
            for assignment in assignments:
                event_type = assignment.event_type
                
                # Get actual events for this event type from real-time filtered data
                type_events = events_by_type.get(event_type, {})
                event_count = type_events.get('count', 0) if isinstance(type_events, dict) else 0
                
                # Only include this assignment if the event type has recent+future events
                if event_count > 0:
                    all_assigned_event_types.add(event_type)
                    event_types[event_type] = {
                        'name': event_type,
                        'count': event_count,
                        'events': []  # Keep empty for API response size
                    }
            
            groups_dict[group.id] = {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'color': getattr(group, 'color', '#3B82F6'),
                'parent_group_id': group.parent_group_id,
                'event_types': event_types
            }
        
        # Calculate ungrouped event types (event types that exist but aren't assigned to any group)
        ungrouped_event_type_names = []
        for event_type in events_by_type.keys():
            if event_type not in all_assigned_event_types:
                ungrouped_event_type_names.append(event_type)
        
        # Split ungrouped event types into recurring vs unique categories
        # Use the same filtered events for consistency
        ungrouped_split = split_ungrouped_events_by_type(events_by_type, ungrouped_event_type_names, filtered_events_data if 'filtered_events_data' in locals() else [])
        print(f"🔍 Debug: Split ungrouped events into {len(ungrouped_split['recurring'])} recurring and {len(ungrouped_split['unique'])} unique")
        
        return {
            'has_groups': True,
            'domain_id': domain_id,
            'groups': groups_dict,
            'ungrouped_recurring_event_types': ungrouped_split['recurring'],
            'ungrouped_unique_event_types': ungrouped_split['unique'],
            # Keep legacy field for backward compatibility
            'ungrouped_event_types': ungrouped_split['recurring'] + ungrouped_split['unique']
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get domain groups: {str(e)}"
        )


@app.get("/api/domains/{domain_id}/types")
async def get_domain_event_types(domain_id: str):
    """Get available event types for domain - matches OpenAPI spec exactly"""
    # Validate domain ID format
    if not is_valid_domain_id(domain_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid domain ID format: {domain_id}"
        )
    
    try:
        # Load domain configuration
        config_path = Path(__file__).parent.parent / "config" / "domains.yaml"
        domains_config = load_domains_config(str(config_path))
        
        # Get specific domain configuration
        domain_config = get_domain_config(domains_config, domain_id)
        if not domain_config:
            raise HTTPException(
                status_code=404,
                detail=f"Domain '{domain_id}' not found"
            )
        
        # Fetch fresh iCal content to get current event types
        calendar_url = domain_config.get('calendar_url', '')
        if not calendar_url:
            raise HTTPException(
                status_code=500,
                detail=f"Domain '{domain_id}' has no calendar URL configured"
            )
        
        # Fetch and parse iCal content in real-time
        ical_content, fetch_error = fetch_ical_content(calendar_url)
        if fetch_error or not ical_content:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch calendar data: {fetch_error or 'No content returned'}"
            )
        
        # Parse events from iCal content
        domain_calendar_id = f"domain_{domain_id}"
        events_data, parse_error = parse_calendar_events(ical_content, domain_calendar_id)
        if parse_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse calendar data: {parse_error}"
            )
        
        # Analyze event types and their counts (simplified - no last_event tracking to avoid timezone issues)
        event_type_stats = {}
        for event in events_data:
            event_type_name = event.get('title', 'Unknown')  # Use event title as the event type name
            if event_type_name not in event_type_stats:
                event_type_stats[event_type_name] = {
                    'count': 0
                }
            
            event_type_stats[event_type_name]['count'] += 1
        
        # Format response according to contract
        event_types = []
        total_count = 0
        for event_type_name, stats in event_type_stats.items():
            event_type_obj = {
                'name': event_type_name,
                'count': stats['count']
            }
            event_types.append(event_type_obj)
            total_count += stats['count']
        
        # Sort by count (descending) for better UX
        event_types.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'domain_id': domain_id,
            'event_types': event_types,
            'total_count': total_count
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get domain event types: {str(e)}"
        )

# ==============================================
# DOMAIN EVENT TYPE EVENTS ENDPOINT
# ==============================================

@app.get("/api/domains/{domain_id}/types/{event_type}/events")
async def get_domain_event_type_events(domain_id: str, event_type: str):
    """Get individual events for a specific event type in a domain"""
    # Validate domain ID format
    if not is_valid_domain_id(domain_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid domain ID format: {domain_id}"
        )
    
    try:
        # Load domain configuration
        config_path = Path(__file__).parent.parent / "config" / "domains.yaml"
        domains_config = load_domains_config(str(config_path))
        
        # Get specific domain configuration
        domain_config = get_domain_config(domains_config, domain_id)
        if not domain_config:
            raise HTTPException(
                status_code=404,
                detail=f"Domain '{domain_id}' not found"
            )
        
        # Fetch fresh iCal content
        calendar_url = domain_config.get('calendar_url', '')
        if not calendar_url:
            raise HTTPException(
                status_code=404,
                detail=f"No calendar URL configured for domain '{domain_id}'"
            )
        
        # Fetch and parse iCal content
        ical_content, fetch_error = fetch_ical_content(calendar_url)
        if fetch_error or not ical_content:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch calendar data: {fetch_error}"
            )
        
        # Parse events from iCal content
        domain_calendar_id = f"domain_{domain_id}"
        events_data, parse_error = parse_calendar_events(ical_content, domain_calendar_id)
        if parse_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse calendar data: {parse_error}"
            )
        
        # Apply consistent filtering: only recent (1 week) + future events
        recent_and_future_events = filter_recent_and_future_events(events_data)
        
        # Filter events for the specific event type
        filtered_events = []
        for event in recent_and_future_events:
            if event.get('summary', '').strip() == event_type:
                # Format event for response
                formatted_event = {
                    'id': event.get('uid', ''),
                    'title': event.get('summary', ''),
                    'start': event.get('start', ''),
                    'end': event.get('end', ''),
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'is_recurring': bool(event.get('rrule'))
                }
                filtered_events.append(formatted_event)
        
        # Sort events by start date
        filtered_events.sort(key=lambda x: x.get('start', ''))
        
        return {
            'domain_id': domain_id,
            'event_type': event_type,
            'events': filtered_events,
            'count': len(filtered_events)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get events for event type: {str(e)}"
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