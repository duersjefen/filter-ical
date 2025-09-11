"""
iCal Viewer API - Python FastAPI Backend
Functional programming style with Datomic-inspired immutable database
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

# Simple persistence layer
import pickle
from pathlib import Path

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

# Simple persistent store (keeps existing functional interface)
class PersistentStore:
    def __init__(self, data_dir=None):
        # Allow custom data directory for testing
        self.data_dir = Path(data_dir) if data_dir else Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.store_file = self.data_dir / "store.pkl"
        
        # Load existing data or initialize
        self._data = self._load() or {
            "calendars": {},
            "events_cache": {},  # calendar_id -> events
            "filters": {}  # filter_id -> filter data
        }
        
        # Initialize fixture data if empty
        if not self._data["calendars"]:
            self._init_fixtures()
    
    def _load(self):
        """Load data from disk"""
        if self.store_file.exists():
            try:
                with open(self.store_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading store: {e}")
        return None
    
    def _save(self):
        """Save data to disk"""
        try:
            with open(self.store_file, 'wb') as f:
                pickle.dump(self._data, f)
        except Exception as e:
            print(f"Error saving store: {e}")
    
    def _init_fixtures(self):
        """Initialize with fixture data"""
        fixtures = [
            CalendarEntry("1", "US Federal Holidays", "https://calendar.google.com/calendar/ical/usa__en%40holiday.calendar.google.com/public/basic.ics", "default"),
            CalendarEntry("2", "Google US Holidays", "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics", "default"),
            CalendarEntry("3", "International Holidays", "https://calendar.google.com/calendar/ical/addressbook%23contacts%40group.v.calendar.google.com/public/basic.ics", "default"),
            CalendarEntry("5", "BCC Portal Calendar", "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics", "default")
        ]
        
        for cal in fixtures:
            self._data["calendars"][cal.id] = cal
        self._save()
    
    # Same interface as before
    def get_calendars(self, user_id: str) -> List[CalendarEntry]:
        return [cal for cal in self._data["calendars"].values() 
                if cal.user_id == user_id or cal.user_id == "default"]
    
    def add_calendar(self, name: str, url: str, user_id: str) -> CalendarEntry:
        calendar_id = str(uuid.uuid4())
        calendar = CalendarEntry(calendar_id, name, url, user_id)
        self._data["calendars"][calendar_id] = calendar
        self._save()
        return calendar
    
    def get_calendar(self, calendar_id: str) -> Optional[CalendarEntry]:
        return self._data["calendars"].get(calendar_id)
    
    def delete_calendar(self, calendar_id: str, user_id: str) -> bool:
        calendar = self._data["calendars"].get(calendar_id)
        if calendar and calendar.user_id == user_id:
            del self._data["calendars"][calendar_id]
            # Also clear cached events
            self._data["events_cache"].pop(calendar_id, None)
            self._save()
            return True
        return False
    
    # Event caching
    def cache_events(self, calendar_id: str, events: List[Event]):
        """Cache events for a calendar"""
        self._data["events_cache"][calendar_id] = events
        self._save()
    
    def get_cached_events(self, calendar_id: str) -> Optional[List[Event]]:
        """Get cached events"""
        return self._data["events_cache"].get(calendar_id)
    
    # Filter management
    def get_filters(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all filters for user"""
        return [filter_data for filter_data in self._data["filters"].values() 
                if filter_data["user_id"] == user_id]
    
    def add_filter(self, name: str, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Add new filter"""
        filter_id = str(uuid.uuid4())
        filter_data = {
            "id": filter_id,
            "name": name,
            "config": config,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
        
        self._data["filters"][filter_id] = filter_data
        self._save()
        return filter_data
    
    def delete_filter(self, filter_id: str, user_id: str) -> bool:
        """Delete filter if owned by user"""
        filter_data = self._data["filters"].get(filter_id)
        if filter_data and filter_data["user_id"] == user_id:
            del self._data["filters"][filter_id]
            self._save()
            return True
        return False

# Global persistent store
store = PersistentStore()

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
    
    # Try cached events first
    cached_events = store.get_cached_events(calendar_id)
    if cached_events:
        return {"events": [asdict(event) for event in cached_events]}
    
    # Fetch and cache
    events = await fetch_ical_events(calendar.url)
    if events:
        store.cache_events(calendar_id, events)
    
    return {"events": [asdict(event) for event in events]}

@app.get("/api/filters")
async def get_filters(x_user_id: str = Header("anonymous")):
    filters = store.get_filters(x_user_id)
    return {"filters": filters}

@app.post("/api/filters")
async def create_filter(data: dict, x_user_id: str = Header("anonymous")):
    name = data.get("name", "").strip()
    config = data.get("config", {})
    
    if not name:
        raise HTTPException(status_code=400, detail="Filter name is required")
    
    filter_data = store.add_filter(name, config, x_user_id)
    return {"message": "Filter saved", "id": filter_data["id"]}

@app.delete("/api/filters/{filter_id}")
async def delete_filter(
    filter_id: str,
    x_user_id: str = Header("anonymous")
):
    if store.delete_filter(filter_id, x_user_id):
        return {"message": "Filter deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Filter not found")


# Serve static files (same as Clojure version)
frontend_path = Path(__file__).parent.parent.parent / "frontend" / "resources" / "public"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)