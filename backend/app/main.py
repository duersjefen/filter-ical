"""
iCal Viewer API - Python FastAPI Backend
Functional programming style with immutable data structures
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import httpx
from icalendar import Calendar
import recurring_ical_events
from datetime import datetime, date
import uuid
import json

# Immutable data structures (Clojure-inspired)
@dataclass(frozen=True)
class CalendarEntry:
    id: str
    name: str
    url: str
    user_id: str

@dataclass(frozen=True) 
class Event:
    uid: str
    summary: str
    dtstart: str
    dtend: str
    location: Optional[str]
    description: Optional[str]
    raw: str

@dataclass(frozen=True)
class Filter:
    id: str
    name: str
    calendar_id: str
    types: List[str]
    user_id: str

# Pure functions for data transformation
def parse_date_to_string(dt: Any) -> str:
    """Pure function: Convert various date formats to YYYYMMDD string"""
    if isinstance(dt, datetime):
        return dt.strftime("%Y%m%d")
    elif isinstance(dt, date):
        return dt.strftime("%Y%m%d")
    elif hasattr(dt, 'dt'):
        return parse_date_to_string(dt.dt)
    else:
        return str(dt)[:8] if str(dt) else ""

def ical_component_to_event(component) -> Event:
    """Pure function: Transform iCal component to Event dataclass"""
    return Event(
        uid=str(component.get('UID', '')),
        summary=str(component.get('SUMMARY', '')),
        dtstart=parse_date_to_string(component.get('DTSTART')),
        dtend=parse_date_to_string(component.get('DTEND')),
        location=str(component.get('LOCATION', '')) if component.get('LOCATION') else None,
        description=str(component.get('DESCRIPTION', '')) if component.get('DESCRIPTION') else None,
        raw=component.to_ical().decode('utf-8', errors='ignore')
    )

def parse_ical_content(content: str) -> List[Event]:
    """Pure function: Parse iCal content into events"""
    try:
        calendar = Calendar.from_ical(content)
        events = []
        
        # Get recurring events for next 2 years
        start_date = date.today()
        end_date = date(start_date.year + 2, 12, 31)
        
        recurring_events = recurring_ical_events.of(calendar).between(start_date, end_date)
        
        for event in recurring_events:
            events.append(ical_component_to_event(event))
            
        return events
    except Exception as e:
        print(f"Error parsing iCal: {e}")
        return []

async def fetch_ical_events(url: str) -> List[Event]:
    """Pure function: Fetch and parse iCal from URL"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return parse_ical_content(response.text)
    except Exception as e:
        print(f"Error fetching iCal from {url}: {e}")
        return []

# In-memory storage (functional style with immutable updates)
class FunctionalStore:
    def __init__(self):
        self._calendars: Dict[str, CalendarEntry] = {}
        self._filters: Dict[str, Filter] = {}
        
        # Initialize with existing fixture data
        fixture_calendars = [
            CalendarEntry("1", "US Federal Holidays", "https://calendar.google.com/calendar/ical/usa__en%40holiday.calendar.google.com/public/basic.ics", "default"),
            CalendarEntry("2", "Google US Holidays", "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics", "default"),  
            CalendarEntry("3", "International Holidays", "https://calendar.google.com/calendar/ical/addressbook%23contacts%40group.v.calendar.google.com/public/basic.ics", "default"),
            CalendarEntry("5", "BCC Portal Calendar", "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics", "default")
        ]
        
        for cal in fixture_calendars:
            self._calendars[cal.id] = cal
    
    def get_calendars(self, user_id: str) -> List[CalendarEntry]:
        return [cal for cal in self._calendars.values() if cal.user_id == user_id or cal.user_id == "default"]
    
    def add_calendar(self, name: str, url: str, user_id: str) -> CalendarEntry:
        calendar_id = str(uuid.uuid4())
        calendar = CalendarEntry(calendar_id, name, url, user_id)
        # Functional update - create new state
        self._calendars = {**self._calendars, calendar_id: calendar}
        return calendar
    
    def get_calendar(self, calendar_id: str) -> Optional[CalendarEntry]:
        return self._calendars.get(calendar_id)
    
    def delete_calendar(self, calendar_id: str, user_id: str) -> bool:
        calendar = self._calendars.get(calendar_id)
        if calendar and calendar.user_id == user_id:
            # Functional update - create new state without deleted item
            self._calendars = {k: v for k, v in self._calendars.items() if k != calendar_id}
            return True
        return False

# Global store instance
store = FunctionalStore()

# FastAPI app
app = FastAPI(title="iCal Viewer API", version="2.0.0")

# API Routes (functional style)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ical-viewer"}

@app.get("/")
async def root():
    return RedirectResponse(url="/app")

@app.get("/api/calendars")
async def get_calendars(x_user_id: str = Header("anonymous")):
    calendars = store.get_calendars(x_user_id)
    return {"calendars": [asdict(cal) for cal in calendars]}

@app.post("/api/calendars")
async def create_calendar(
    data: dict,
    x_user_id: str = Header("anonymous")
):
    name = data.get("name", "").strip()
    url = data.get("url", "").strip()
    
    if not name or not url:
        raise HTTPException(status_code=400, detail="Name and URL are required")
    
    calendar = store.add_calendar(name, url, x_user_id)
    return {"message": "Calendar added successfully", "id": calendar.id}

@app.delete("/api/calendars/{calendar_id}")
async def delete_calendar(
    calendar_id: str,
    x_user_id: str = Header("anonymous")
):
    if store.delete_calendar(calendar_id, x_user_id):
        return {"message": "Calendar deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Calendar not found")

@app.get("/api/calendar/{calendar_id}/events")
async def get_calendar_events(
    calendar_id: str,
    x_user_id: str = Header("anonymous")
):
    calendar = store.get_calendar(calendar_id)
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    events = await fetch_ical_events(calendar.url)
    return {"events": [asdict(event) for event in events]}

@app.get("/api/filters")
async def get_filters(x_user_id: str = Header("anonymous")):
    return {"filters": []}

@app.post("/api/filters")
async def create_filter(data: dict, x_user_id: str = Header("anonymous")):
    return {"message": "Filter saved", "id": str(uuid.uuid4())}

@app.delete("/api/filters/{filter_id}")
async def delete_filter(filter_id: str, x_user_id: str = Header("anonymous")):
    return {"message": "Filter deleted"}

# Serve static files (same as Clojure version)
frontend_path = Path(__file__).parent.parent.parent / "frontend" / "resources" / "public"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)