"""
Storage Layer - Pure persistence operations
No business logic, only data storage and retrieval
"""

import pickle
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Any
from ..models import CalendarEntry, Event, Filter


class PersistentStore:
    """Simple persistent store with functional interface"""
    
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
    
    def _load(self) -> Optional[Dict]:
        """Load data from disk"""
        if self.store_file.exists():
            try:
                with open(self.store_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading store: {e}")
        return None
    
    def _save(self) -> None:
        """Save data to disk"""
        try:
            with open(self.store_file, 'wb') as f:
                pickle.dump(self._data, f)
        except Exception as e:
            print(f"Error saving store: {e}")
    
    # Calendar operations
    def get_calendars(self, user_id: str) -> List[CalendarEntry]:
        """Get all calendars for a user"""
        return [
            CalendarEntry(**cal) for cal in self._data["calendars"].values() 
            if cal["user_id"] == user_id
        ]
    
    def add_calendar(self, name: str, url: str, user_id: str) -> CalendarEntry:
        """Add a new calendar"""
        calendar_id = str(uuid.uuid4())
        calendar_data = {
            "id": calendar_id,
            "name": name,
            "url": url,
            "user_id": user_id
        }
        self._data["calendars"][calendar_id] = calendar_data
        self._save()
        return CalendarEntry(**calendar_data)
    
    def get_calendar(self, calendar_id: str) -> Optional[CalendarEntry]:
        """Get a specific calendar"""
        cal_data = self._data["calendars"].get(calendar_id)
        return CalendarEntry(**cal_data) if cal_data else None
    
    def delete_calendar(self, calendar_id: str, user_id: str) -> bool:
        """Delete a calendar (with user authorization)"""
        if calendar_id not in self._data["calendars"]:
            return False
        
        calendar = self._data["calendars"][calendar_id]
        if calendar["user_id"] != user_id:
            return False
        
        del self._data["calendars"][calendar_id]
        # Clean up related data
        self._data["events_cache"].pop(calendar_id, None)
        self._save()
        return True
    
    # Event caching operations
    def cache_events(self, calendar_id: str, events: List[Event]) -> None:
        """Cache events for a calendar"""
        # Convert events to dict for JSON serialization
        self._data["events_cache"][calendar_id] = [
            {
                "uid": e.uid,
                "summary": e.summary,
                "dtstart": e.dtstart,
                "dtend": e.dtend,
                "location": e.location,
                "description": e.description,
                "raw": e.raw
            } for e in events
        ]
        self._save()
    
    def get_cached_events(self, calendar_id: str) -> Optional[List[Event]]:
        """Get cached events for a calendar"""
        cached = self._data["events_cache"].get(calendar_id)
        return [Event(**event_data) for event_data in cached] if cached else None
    
    # Filter operations
    def get_filters(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all filters for a user"""
        return [
            filter_data for filter_data in self._data["filters"].values()
            if filter_data["user_id"] == user_id
        ]
    
    def add_filter(self, name: str, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Add a new filter"""
        filter_id = str(uuid.uuid4())
        filter_data = {
            "id": filter_id,
            "name": name,
            "config": config,
            "user_id": user_id
        }
        self._data["filters"][filter_id] = filter_data
        self._save()
        return filter_data
    
    def delete_filter(self, filter_id: str, user_id: str) -> bool:
        """Delete a filter (with user authorization)"""
        if filter_id not in self._data["filters"]:
            return False
        
        filter_data = self._data["filters"][filter_id]
        if filter_data["user_id"] != user_id:
            return False
        
        del self._data["filters"][filter_id]
        self._save()
        return True