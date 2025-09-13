"""
iCal Viewer API - Clean, modular FastAPI Backend
Refactored for maintainability with separated concerns
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, Response
from typing import List, Dict, Optional, Any
from pathlib import Path

# Import pure functions (Functional Core)
from .models import CalendarEntry, Event, Filter
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
from .services.events import generate_ical_content

# Initialize store data (Imperative Shell)
from .storage import PersistentStore
store_instance = PersistentStore()  # For I/O operations only

# FastAPI app
app = FastAPI(title="iCal Viewer API")

# Serve static files from frontend container  
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=static_path), name="static")


# === UTILITY FUNCTIONS ===

def get_user_id_from_header(x_user_id: str = Header("anonymous")) -> str:
    """Extract user ID from header with default"""
    return x_user_id if x_user_id else "anonymous"


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
    
    # Return using pure function
    return calendar_to_dict(calendar)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)