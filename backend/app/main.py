"""
iCal Viewer API - Clean, modular FastAPI Backend
Refactored for maintainability with separated concerns
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, Response
import yaml
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import uuid

# Import pure functions (Functional Core)
from .models import CalendarEntry, Event, Filter, FilteredCalendar, FilterConfig
from .data.calendar import (
    validate_calendar_data, find_calendar_by_id, calendar_to_dict
)
from .data.store import (
    add_calendar_to_store, get_calendars_from_store,
    remove_calendar_from_store,
    cache_events_in_store, get_cached_events_from_store,
    add_filter_to_store, get_filters_from_store, remove_filter_from_store
)
from .data.http import (
    validate_ical_url_http, fetch_calendar_events, extract_event_categories
)
from .data.filters import (
    is_valid_filter_data, normalize_filter_config
)
from .data.filtering import (
    apply_filter_config, create_filter_config_hash
)
from .data.security import (
    generate_public_token, sanitize_ical_content, 
    create_secure_calendar_url, extract_token_from_url,
    validate_public_token_format, create_security_headers
)
from .data.caching import (
    create_cache_key, is_cache_expired, should_refresh_cache
)
from .services.events import generate_ical_content

# Initialize store data (Imperative Shell)
from .storage import PersistentStore
store_instance = PersistentStore()  # For I/O operations only

# FastAPI app
# Load OpenAPI spec
def load_openapi_spec():
    spec_path = Path(__file__).parent.parent / "openapi.yaml"
    if spec_path.exists():
        with open(spec_path, 'r') as f:
            return yaml.safe_load(f)
    return None

openapi_spec = load_openapi_spec()

app = FastAPI(
    title="iCal Viewer API",
    version="1.0.0",
    description="REST API for managing iCal calendars with filtering capabilities",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Set custom OpenAPI spec if available
if openapi_spec:
    def custom_openapi():
        return openapi_spec
    app.openapi = custom_openapi

# Serve static files from frontend container  
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=static_path), name="static")


# === UTILITY FUNCTIONS ===

def get_user_id_from_header(x_user_id: str = Header("anonymous")) -> str:
    """Extract user ID from header with default"""
    return x_user_id if x_user_id else "anonymous"


def find_calendar_in_store(store_data: dict, calendar_id: str, user_id: str) -> Optional[dict]:
    """Helper function to find calendar in store data"""
    calendars = store_data.get("calendars", {})
    calendar_data = calendars.get(calendar_id)
    
    if calendar_data and calendar_data.get("user_id") == user_id:
        return calendar_data
    return None


# === IMPERATIVE SHELL HELPERS ===

def get_store_data():
    """Get current store data - I/O boundary"""
    return store_instance._data


def save_store_data(new_data):
    """Save store data - I/O boundary"""
    store_instance._data = new_data
    store_instance._save()


# === API ROUTES ===

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ical-viewer"}

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")


# === CALENDAR ENDPOINTS ===

@app.get("/api/calendars")
async def get_calendars(x_user_id: str = Header("anonymous")):
    """Get all calendars for the current user - Functional approach"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Use pure function to get calendars
    calendars = get_calendars_from_store(store_data, user_id)
    
    # Transform to API format using pure functions
    calendar_dicts = [calendar_to_dict(c) for c in calendars]
    
    return {"calendars": calendar_dicts}


@app.post("/api/calendars")
async def create_calendar(
    data: dict, 
    x_user_id: str = Header("anonymous")
):
    """Create a new calendar - Functional approach"""
    user_id = get_user_id_from_header(x_user_id)
    
    name = data.get("name")
    url = data.get("url")
    
    # Validate input data using pure function
    is_valid_input, validation_message = validate_calendar_data(name, url)
    if not is_valid_input:
        raise HTTPException(status_code=400, detail=validation_message)
    
    # Validate the iCal URL using pure function (I/O operation)
    is_valid_url, url_message = await validate_ical_url_http(url)
    if not is_valid_url:
        raise HTTPException(status_code=400, detail=f"Invalid iCal URL: {url_message}")
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Create calendar using pure function
    new_store_data, calendar = add_calendar_to_store(store_data, name, url, user_id)
    
    # Save updated store data (I/O)
    save_store_data(new_store_data)
    
    # Return using pure function - match OpenAPI spec format
    return {
        "success": True,
        "calendar": calendar_to_dict(calendar)
    }


@app.delete("/api/calendars/{calendar_id}")
async def delete_calendar(
    calendar_id: str, 
    x_user_id: str = Header("anonymous")
):
    """Delete a calendar - Functional approach"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Delete calendar using pure function
    new_store_data, success = remove_calendar_from_store(store_data, calendar_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Save updated store data (I/O)
    save_store_data(new_store_data)
    
    return {"message": "Calendar deleted"}


@app.get("/api/calendar/{calendar_id}/events")
async def get_calendar_events(
    calendar_id: str, 
    x_user_id: str = Header("anonymous")
):
    """Get events for a specific calendar - Functional approach"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Get user calendars and verify ownership using pure functions
    user_calendars = get_calendars_from_store(store_data, user_id)
    calendar = find_calendar_by_id(user_calendars, calendar_id)
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Try to get cached events first using pure function
    cached_events = get_cached_events_from_store(store_data, calendar_id)
    
    if cached_events:
        events = cached_events
    else:
        # Fetch fresh events using pure function (I/O operation)
        success, events, error_msg = await fetch_calendar_events(calendar.url)
        if not success:
            raise HTTPException(status_code=500, detail=f"Error fetching events: {error_msg}")
        
        # Cache events using pure function
        if events:
            new_store_data = cache_events_in_store(store_data, calendar_id, events)
            save_store_data(new_store_data)
    
    return {
        "events": [
            {
                "uid": e.uid,
                "summary": e.summary,
                "dtstart": e.dtstart,
                "dtend": e.dtend,
                "location": e.location,
                "description": e.description
            } for e in events
        ]
    }


@app.get("/api/calendar/{calendar_id}/categories")
async def get_calendar_categories(
    calendar_id: str, 
    x_user_id: str = Header("anonymous")
):
    """Get event categories for a calendar - Functional approach"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Verify user owns this calendar using pure functions
    user_calendars = get_calendars_from_store(store_data, user_id)
    calendar = find_calendar_by_id(user_calendars, calendar_id)
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get events (try cache first)
    cached_events = get_cached_events_from_store(store_data, calendar_id)
    
    if cached_events:
        events = cached_events
    else:
        # Fetch fresh events (I/O operation)
        success, events, error_msg = await fetch_calendar_events(calendar.url)
        if not success:
            raise HTTPException(status_code=500, detail=f"Error fetching events: {error_msg}")
        
        # Cache events
        if events:
            new_store_data = cache_events_in_store(store_data, calendar_id, events)
            save_store_data(new_store_data)
    
    # Extract categories using pure function
    categories = extract_event_categories(events)
    return {"categories": categories}


# === FILTER ENDPOINTS ===

@app.get("/api/filters")
async def get_filters(x_user_id: str = Header("anonymous")):
    """Get all filters for the current user - Functional approach"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Get filters using pure function
    filters = get_filters_from_store(store_data, user_id)
    
    return {"filters": filters}


@app.post("/api/filters")
async def create_filter(data: dict, x_user_id: str = Header("anonymous")):
    """Create a new filter - Functional approach"""
    user_id = get_user_id_from_header(x_user_id)
    
    name = data.get("name", "Untitled Filter")
    config = data.get("config", {})
    
    # Validate filter data using pure function
    is_valid, validation_message = is_valid_filter_data(name, config)
    if not is_valid:
        raise HTTPException(status_code=400, detail=validation_message)
    
    # Normalize config using pure function
    normalized_config = normalize_filter_config(config)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Add filter using pure function
    new_store_data, filter_data = add_filter_to_store(store_data, name, normalized_config, user_id)
    
    # Save updated store data (I/O)
    save_store_data(new_store_data)
    
    return filter_data


@app.delete("/api/filters/{filter_id}")
async def delete_filter(
    filter_id: str, 
    x_user_id: str = Header("anonymous")
):
    """Delete a filter - Functional approach"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Delete filter using pure function
    new_store_data, success = remove_filter_from_store(store_data, filter_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    # Save updated store data (I/O)
    save_store_data(new_store_data)
    
    return {"message": "Filter deleted"}


# === EXPORT ENDPOINTS ===

@app.get("/filter/{calendar_id}")
async def download_filtered_ical(
    calendar_id: str,
    categories: Optional[str] = None,
    mode: Optional[str] = "include",
    x_user_id: str = Header("anonymous")
):
    """Download filtered iCal file - Functional approach"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Verify user owns this calendar using pure functions
    user_calendars = get_calendars_from_store(store_data, user_id)
    calendar = find_calendar_by_id(user_calendars, calendar_id)
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get events (try cache first)
    cached_events = get_cached_events_from_store(store_data, calendar_id)
    
    if cached_events:
        events = cached_events
    else:
        # Fetch fresh events (I/O operation)
        success, events, error_msg = await fetch_calendar_events(calendar.url)
        if not success:
            raise HTTPException(status_code=500, detail=f"Error fetching events: {error_msg}")
        
        # Cache events
        if events:
            new_store_data = cache_events_in_store(store_data, calendar_id, events)
            save_store_data(new_store_data)
    
    if not events:
        raise HTTPException(status_code=404, detail="No events found")
    
    # Parse categories filter (pure operation)
    category_set = set()
    if categories:
        category_list = categories.split(",")
        category_set = {cat.strip() for cat in category_list if cat.strip()}
    
    # Generate iCal content using pure function
    ical_content = generate_ical_content(events, calendar.name, category_set)
    
    # Determine filename (pure operation)
    mode_suffix = f"-{mode}" if mode != "include" else ""
    categories_suffix = f"-{len(category_set)}cats" if category_set else ""
    filename = f"{calendar.name.replace(' ', '_')}{mode_suffix}{categories_suffix}.ics"
    
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# === FILTERED CALENDAR ENDPOINTS ===

@app.post("/api/filtered-calendars")
async def create_filtered_calendar(data: dict, x_user_id: str = Header("anonymous")):
    """Create a new filtered calendar with persistent public URL"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Extract and validate input data
    source_calendar_id = data.get("source_calendar_id")
    filter_name = data.get("name", "Filtered Calendar")
    filter_config_data = data.get("filter_config", {})
    
    if not source_calendar_id:
        raise HTTPException(status_code=400, detail="source_calendar_id is required")
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    # Find source calendar using helper function
    source_calendar = find_calendar_in_store(store_data, source_calendar_id, user_id)
    if not source_calendar:
        raise HTTPException(status_code=404, detail="Source calendar not found")
    
    # Validate and normalize filter config using pure functions
    is_valid, validation_message = is_valid_filter_data(filter_name, filter_config_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=validation_message)
    
    normalized_config = normalize_filter_config(filter_config_data)
    
    # Create FilterConfig model with all required fields
    import uuid
    current_time = datetime.now().isoformat()
    filter_config = FilterConfig(
        id=str(uuid.uuid4()),
        name=filter_name,
        user_id=user_id,
        include_categories=normalized_config.get("include_categories", []),
        exclude_categories=normalized_config.get("exclude_categories", []),
        include_keywords=normalized_config.get("include_keywords", []),
        exclude_keywords=normalized_config.get("exclude_keywords", []),
        date_range_start=normalized_config.get("date_range_start"),
        date_range_end=normalized_config.get("date_range_end"),
        date_range_type=normalized_config.get("date_range_type", "absolute"),
        location_filter=normalized_config.get("location_filter"),
        attendee_filter=normalized_config.get("attendee_filter"),
        organizer_filter=normalized_config.get("organizer_filter"),
        min_duration_minutes=normalized_config.get("min_duration_minutes"),
        max_duration_minutes=normalized_config.get("max_duration_minutes"),
        filter_mode=normalized_config.get("filter_mode", "include"),
        match_all=normalized_config.get("match_all", False),
        created_at=current_time,
        updated_at=current_time
    )
    
    # Generate secure public token using pure function
    public_token = generate_public_token()
    
    # Create filter config hash using pure function
    filter_config_hash = create_filter_config_hash(filter_config)
    
    # Create filtered calendar model using pure function
    filtered_calendar = FilteredCalendar(
        id=str(uuid.uuid4()),
        source_calendar_id=source_calendar_id,
        filter_config_id=filter_config.id,
        public_token=public_token,
        name=filter_name,
        description=None,
        user_id=user_id,
        created_at=current_time,
        last_accessed=None,
        access_count=0,
        cache_key=None,
        cache_expires_at=None,
        is_active=True
    )
    
    # Generate filtered iCal content to store in database
    # Get events for the source calendar
    cached_events = get_cached_events_from_store(store_data, source_calendar_id)
    
    if not cached_events:
        # Fetch fresh events if not cached
        success, events, error_msg = await fetch_calendar_events(source_calendar["url"])
        if not success:
            raise HTTPException(status_code=500, detail=f"Error fetching events: {error_msg}")
        
        # Cache the events
        new_store_data = cache_events_in_store(store_data, source_calendar_id, events)
        save_store_data(new_store_data)
        cached_events = events
    
    # Apply filters to get filtered events
    filtered_events = apply_filter_config(cached_events, normalized_config)
    
    # Generate filtered iCal content
    filtered_content = generate_ical_content(filtered_events, filter_name, set())
    
    # Store in persistent database using PersistentStore methods
    filtered_calendar_data = store_instance.add_filtered_calendar(
        token=public_token,
        name=filter_name,
        source_calendar_id=source_calendar_id,
        filter_config=normalized_config,
        user_id=user_id,
        filtered_content=filtered_content
    )
    
    # Create URLs using pure functions
    base_url = "https://filter-ical.de"  # TODO: Get from config
    calendar_url = create_secure_calendar_url(base_url, public_token)
    preview_url = f"{base_url}/preview/{public_token}"
    
    return {
        "id": filtered_calendar.id,
        "name": filter_name,
        "public_token": public_token,
        "calendar_url": calendar_url,
        "preview_url": preview_url,
        "source_calendar_id": source_calendar_id,
        "filter_config": filtered_calendar_data["filter_config"],
        "created_at": filtered_calendar_data["created_at"]
    }


@app.get("/api/filtered-calendars")
async def get_filtered_calendars(x_user_id: str = Header("anonymous")):
    """Get all filtered calendars for the current user"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get filtered calendars from persistent store
    filtered_calendar_list = store_instance.get_filtered_calendars(user_id)
    
    filtered_calendars = []
    for filtered_cal_data in filtered_calendar_list:
        # Create URLs using pure functions
        base_url = "https://filter-ical.de"  # TODO: Get from config
        public_token = filtered_cal_data["token"]  # Note: using "token" key from database
        
        filtered_calendars.append({
            "id": filtered_cal_data["token"],  # Using token as ID for compatibility
            "name": filtered_cal_data["name"],
            "public_token": public_token,
            "source_calendar_id": filtered_cal_data["source_calendar_id"],
            "filter_config": filtered_cal_data["filter_config"],
            "created_at": filtered_cal_data["created_at"],
            "calendar_url": create_secure_calendar_url(base_url, public_token),
            "preview_url": f"{base_url}/preview/{public_token}"
        })
    
    return {"filtered_calendars": filtered_calendars}


@app.put("/api/filtered-calendars/{filtered_calendar_id}")
async def update_filtered_calendar(
    filtered_calendar_id: str,
    data: dict,
    x_user_id: str = Header("anonymous")
):
    """Update a filtered calendar's filter configuration"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    filtered_calendars = store_data.get("filtered_calendars", {})
    if filtered_calendar_id not in filtered_calendars:
        raise HTTPException(status_code=404, detail="Filtered calendar not found")
    
    filtered_cal_data = filtered_calendars[filtered_calendar_id]
    if filtered_cal_data.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Filtered calendar not found")
    
    # Extract new filter config
    new_filter_config_data = data.get("filter_config", {})
    new_name = data.get("name", filtered_cal_data["name"])
    
    # Validate and normalize filter config using pure functions
    is_valid, validation_message = is_valid_filter_data(new_name, new_filter_config_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=validation_message)
    
    normalized_config = normalize_filter_config(new_filter_config_data)
    
    # Create updated FilterConfig model
    current_time = datetime.now().isoformat()
    updated_filter_config = FilterConfig(
        id=str(uuid.uuid4()),
        name=new_name,
        user_id=user_id,
        include_categories=normalized_config.get("include_categories", []),
        exclude_categories=normalized_config.get("exclude_categories", []),
        include_keywords=normalized_config.get("include_keywords", []),
        exclude_keywords=normalized_config.get("exclude_keywords", []),
        date_range_start=normalized_config.get("date_range_start"),
        date_range_end=normalized_config.get("date_range_end"),
        date_range_type=normalized_config.get("date_range_type", "absolute"),
        location_filter=normalized_config.get("location_filter"),
        attendee_filter=normalized_config.get("attendee_filter"),
        organizer_filter=normalized_config.get("organizer_filter"),
        min_duration_minutes=normalized_config.get("min_duration_minutes"),
        max_duration_minutes=normalized_config.get("max_duration_minutes"),
        filter_mode=normalized_config.get("filter_mode", "include"),
        match_all=normalized_config.get("match_all", False),
        created_at=filtered_cal_data.get("created_at", current_time),
        updated_at=current_time
    )
    
    # Generate new filter config hash using pure function
    new_filter_config_hash = create_filter_config_hash(updated_filter_config)
    
    # Update the stored data
    filtered_cal_data["name"] = new_name
    filtered_cal_data["filter_config"] = updated_filter_config.__dict__
    filtered_cal_data["filter_config_hash"] = new_filter_config_hash
    filtered_cal_data["updated_at"] = updated_filter_config.created_at
    
    # Save updated store data (I/O)
    save_store_data(store_data)
    
    # Return updated data with URLs
    base_url = "https://filter-ical.de"  # TODO: Get from config
    public_token = filtered_cal_data["public_token"]
    
    return {
        **filtered_cal_data,
        "calendar_url": create_secure_calendar_url(base_url, public_token),
        "preview_url": f"{base_url}/preview/{public_token}"
    }


@app.delete("/api/filtered-calendars/{filtered_calendar_id}")
async def delete_filtered_calendar(
    filtered_calendar_id: str,
    x_user_id: str = Header("anonymous")
):
    """Delete (deactivate) a filtered calendar"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Get current store data (I/O)
    store_data = get_store_data()
    
    filtered_calendars = store_data.get("filtered_calendars", {})
    if filtered_calendar_id not in filtered_calendars:
        raise HTTPException(status_code=404, detail="Filtered calendar not found")
    
    filtered_cal_data = filtered_calendars[filtered_calendar_id]
    if filtered_cal_data.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Filtered calendar not found")
    
    # Mark as inactive instead of deleting (for audit trail)
    filtered_cal_data["is_active"] = False
    filtered_cal_data["deleted_at"] = filtered_cal_data.get("updated_at", filtered_cal_data.get("created_at", datetime.now().isoformat()))
    
    # Save updated store data (I/O)
    save_store_data(store_data)
    
    return {"message": "Filtered calendar deleted successfully"}


# === PUBLIC CALENDAR SERVING ===

@app.get("/cal/{token}.ics")
async def serve_filtered_calendar_ics(token: str):
    """Serve filtered iCal content via public URL"""
    
    # Validate token format using pure function
    is_valid_token, error_msg = validate_public_token_format(token)
    if not is_valid_token:
        raise HTTPException(status_code=400, detail=f"Invalid token format: {error_msg}")
    
    # Get filtered calendar from persistent store
    filtered_calendar = store_instance.get_filtered_calendar(token)
    
    if not filtered_calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Use pre-computed filtered content from database
    ical_content = filtered_calendar["filtered_content"]
    
    # Sanitize content for public consumption using pure function
    sanitized_content = sanitize_ical_content(ical_content)
    
    # Create security headers using pure function
    headers = create_security_headers("public")
    headers["Content-Disposition"] = f"attachment; filename=\"{filtered_calendar['name'].replace(' ', '_')}.ics\""
    
    return Response(
        content=sanitized_content,
        media_type="text/calendar",
        headers=headers
    )


@app.get("/cal/{token}")
async def preview_filtered_calendar(token: str):
    """Preview filtered calendar in browser"""
    
    # Validate token format using pure function
    is_valid_token, error_msg = validate_public_token_format(token)
    if not is_valid_token:
        raise HTTPException(status_code=400, detail=f"Invalid token format: {error_msg}")
    
    # Get filtered calendar from persistent store
    filtered_calendar = store_instance.get_filtered_calendar(token)
    
    if not filtered_calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get store data for finding source calendar
    store_data = get_store_data()
    
    # Get source calendar
    source_calendar_id = filtered_calendar["source_calendar_id"]
    source_calendar = find_calendar_in_store(store_data, source_calendar_id, filtered_calendar["user_id"])
    
    if not source_calendar:
        raise HTTPException(status_code=404, detail="Source calendar not found")
    
    # Fetch fresh events from source calendar (I/O)
    success, events, error_msg = await fetch_calendar_events(source_calendar["url"])
    if not success or not events:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar events: {error_msg}")
    
    # Apply filter using pure function
    filter_config_data = filtered_calendar["filter_config"]
    # Create FilterConfig from stored data
    filter_config = FilterConfig(
        id=filter_config_data.get("id", str(uuid.uuid4())),
        name=filter_config_data.get("name", ""),
        user_id=filter_config_data.get("user_id", ""),
        include_categories=filter_config_data.get("include_categories", []),
        exclude_categories=filter_config_data.get("exclude_categories", []),
        include_keywords=filter_config_data.get("include_keywords", []),
        exclude_keywords=filter_config_data.get("exclude_keywords", []),
        date_range_start=filter_config_data.get("date_range_start"),
        date_range_end=filter_config_data.get("date_range_end"),
        date_range_type=filter_config_data.get("date_range_type", "absolute"),
        location_filter=filter_config_data.get("location_filter"),
        attendee_filter=filter_config_data.get("attendee_filter"),
        organizer_filter=filter_config_data.get("organizer_filter"),
        min_duration_minutes=filter_config_data.get("min_duration_minutes"),
        max_duration_minutes=filter_config_data.get("max_duration_minutes"),
        filter_mode=filter_config_data.get("filter_mode", "include"),
        match_all=filter_config_data.get("match_all", False),
        created_at=filter_config_data.get("created_at", datetime.now().isoformat()),
        updated_at=filter_config_data.get("updated_at", datetime.now().isoformat())
    )
    filtered_events = apply_filter_config(events, filter_config)
    
    # Create URLs using pure functions
    base_url = "https://filter-ical.de"  # TODO: Get from config
    ics_url = create_secure_calendar_url(base_url, token)
    
    # Return preview data
    return {
        "calendar_name": filtered_calendar["name"],
        "total_events": len(filtered_events),
        "ics_url": ics_url,
        "events": [
            {
                "summary": event.summary,
                "start": event.dtstart,
                "end": event.dtend,
                "location": event.location
            }
            for event in filtered_events[:10]  # Limit preview to 10 events
        ],
        "filter_summary": {
            "include_categories": filter_config_data.get("include_categories", []),
            "exclude_categories": filter_config_data.get("exclude_categories", []),
            "keywords": filter_config_data.get("include_keywords", [])
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)