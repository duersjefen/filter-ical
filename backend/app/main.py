"""
iCal Viewer API - Clean, modular FastAPI Backend
Refactored for maintainability with separated concerns
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, Response
from typing import List, Dict, Optional, Any
from pathlib import Path
import asyncio

# Import our modular components
from .models import CalendarEntry, Event, Filter
from .storage import PersistentStore
from .services import CalendarService, FilterService, generate_ical_content

# Initialize storage and services
store = PersistentStore()
calendar_service = CalendarService(store)
filter_service = FilterService(store)

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
    """Get all calendars for the current user"""
    user_id = get_user_id_from_header(x_user_id)
    calendars = calendar_service.get_calendars(user_id)
    return {"calendars": [{"id": c.id, "name": c.name, "url": c.url} for c in calendars]}


@app.post("/api/calendars")
async def create_calendar(
    data: dict, 
    x_user_id: str = Header("anonymous")
):
    """Create a new calendar"""
    user_id = get_user_id_from_header(x_user_id)
    
    name = data.get("name")
    url = data.get("url")
    
    if not name or not url:
        raise HTTPException(status_code=400, detail="Name and URL are required")
    
    # Validate the iCal URL
    is_valid, message = await calendar_service.validate_ical_url(url)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid iCal URL: {message}")
    
    # Create the calendar
    calendar = await calendar_service.create_calendar(name, url, user_id)
    return {"id": calendar.id, "name": calendar.name, "url": calendar.url}


@app.delete("/api/calendars/{calendar_id}")
async def delete_calendar(
    calendar_id: str, 
    x_user_id: str = Header("anonymous")
):
    """Delete a calendar"""
    user_id = get_user_id_from_header(x_user_id)
    
    success = calendar_service.delete_calendar(calendar_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    return {"message": "Calendar deleted"}


@app.get("/api/calendar/{calendar_id}/events")
async def get_calendar_events(
    calendar_id: str, 
    x_user_id: str = Header("anonymous")
):
    """Get events for a specific calendar"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Verify user owns this calendar
    calendars = calendar_service.get_calendars(user_id)
    if not any(c.id == calendar_id for c in calendars):
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    events = await calendar_service.get_calendar_events(calendar_id)
    
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
    """Get event categories for a calendar"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Verify user owns this calendar
    calendars = calendar_service.get_calendars(user_id)
    if not any(c.id == calendar_id for c in calendars):
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    categories = await calendar_service.get_calendar_categories(calendar_id)
    return {"categories": categories}


# === FILTER ENDPOINTS ===

@app.get("/api/filters")
async def get_filters(x_user_id: str = Header("anonymous")):
    """Get all filters for the current user"""
    user_id = get_user_id_from_header(x_user_id)
    filters = filter_service.get_filters(user_id)
    return {"filters": filters}


@app.post("/api/filters")
async def create_filter(data: dict, x_user_id: str = Header("anonymous")):
    """Create a new filter"""
    user_id = get_user_id_from_header(x_user_id)
    
    name = data.get("name", "Untitled Filter")
    config = data.get("config", {})
    
    filter_data = filter_service.create_filter(name, config, user_id)
    return filter_data


@app.delete("/api/filters/{filter_id}")
async def delete_filter(
    filter_id: str, 
    x_user_id: str = Header("anonymous")
):
    """Delete a filter"""
    user_id = get_user_id_from_header(x_user_id)
    
    success = filter_service.delete_filter(filter_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    return {"message": "Filter deleted"}


# === EXPORT ENDPOINTS ===

@app.get("/filter/{calendar_id}")
async def download_filtered_ical(
    calendar_id: str,
    categories: Optional[str] = None,
    mode: Optional[str] = "include",
    x_user_id: str = Header("anonymous")
):
    """Download filtered iCal file"""
    user_id = get_user_id_from_header(x_user_id)
    
    # Verify user owns this calendar
    calendars = calendar_service.get_calendars(user_id)
    calendar = next((c for c in calendars if c.id == calendar_id), None)
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    # Get events
    events = await calendar_service.get_calendar_events(calendar_id)
    if not events:
        raise HTTPException(status_code=404, detail="No events found")
    
    # Parse categories filter
    category_set = set()
    if categories:
        category_list = categories.split(",")
        category_set = {cat.strip() for cat in category_list if cat.strip()}
    
    # Generate iCal content
    ical_content = generate_ical_content(events, calendar.name, category_set)
    
    # Determine filename
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