"""
Pure Storage Operations - Rich Hickey Style
All functions are pure: take data, return data
No classes, no hidden state, no side effects
"""

import uuid
from typing import List, Dict, Optional, Any, Tuple
from ..models import CalendarEntry, Event


# === PURE DATA TRANSFORMATIONS ===

def empty_store() -> Dict[str, Any]:
    """Create an empty store data structure"""
    return {
        "calendars": {},
        "events_cache": {},
        "filters": {}
    }


def add_calendar_to_store(store_data: Dict[str, Any], name: str, url: str, user_id: str) -> Tuple[Dict[str, Any], CalendarEntry]:
    """Pure function: add calendar to store data, return new store + calendar"""
    calendar_id = str(uuid.uuid4())
    calendar_entry = CalendarEntry(
        id=calendar_id,
        name=name,
        url=url,
        user_id=user_id
    )
    
    # Create new store data (immutable approach)
    new_calendars = {**store_data["calendars"]}
    new_calendars[calendar_id] = {
        "id": calendar_id,
        "name": name,
        "url": url,
        "user_id": user_id
    }
    
    new_store = {
        **store_data,
        "calendars": new_calendars
    }
    
    return new_store, calendar_entry


def get_calendars_from_store(store_data: Dict[str, Any], user_id: str) -> List[CalendarEntry]:
    """Pure function: extract user's calendars from store data"""
    return [
        CalendarEntry(**cal_data) 
        for cal_data in store_data["calendars"].values()
        if cal_data["user_id"] == user_id
    ]


def get_calendar_from_store(store_data: Dict[str, Any], calendar_id: str) -> Optional[CalendarEntry]:
    """Pure function: get specific calendar from store data"""
    cal_data = store_data["calendars"].get(calendar_id)
    return CalendarEntry(**cal_data) if cal_data else None


def remove_calendar_from_store(store_data: Dict[str, Any], calendar_id: str, user_id: str) -> Tuple[Dict[str, Any], bool]:
    """Pure function: remove calendar from store data"""
    calendar = store_data["calendars"].get(calendar_id)
    if not calendar or calendar["user_id"] != user_id:
        return store_data, False
    
    # Create new store without the calendar (immutable)
    new_calendars = {k: v for k, v in store_data["calendars"].items() if k != calendar_id}
    new_events_cache = {k: v for k, v in store_data["events_cache"].items() if k != calendar_id}
    
    new_store = {
        **store_data,
        "calendars": new_calendars,
        "events_cache": new_events_cache
    }
    
    return new_store, True


def cache_events_in_store(store_data: Dict[str, Any], calendar_id: str, events: List[Event]) -> Dict[str, Any]:
    """Pure function: add events to cache in store data"""
    events_data = [
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
    
    new_events_cache = {**store_data["events_cache"]}
    new_events_cache[calendar_id] = events_data
    
    return {
        **store_data,
        "events_cache": new_events_cache
    }


def get_cached_events_from_store(store_data: Dict[str, Any], calendar_id: str) -> Optional[List[Event]]:
    """Pure function: get cached events from store data"""
    cached_data = store_data["events_cache"].get(calendar_id)
    return [Event(**event_data) for event_data in cached_data] if cached_data else None


def add_filter_to_store(store_data: Dict[str, Any], name: str, config: Dict[str, Any], user_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Pure function: add filter to store data"""
    filter_id = str(uuid.uuid4())
    filter_data = {
        "id": filter_id,
        "name": name,
        "config": config,
        "user_id": user_id
    }
    
    new_filters = {**store_data["filters"]}
    new_filters[filter_id] = filter_data
    
    new_store = {
        **store_data,
        "filters": new_filters
    }
    
    return new_store, filter_data


def get_filters_from_store(store_data: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
    """Pure function: get user's filters from store data"""
    return [
        filter_data for filter_data in store_data["filters"].values()
        if filter_data["user_id"] == user_id
    ]


def remove_filter_from_store(store_data: Dict[str, Any], filter_id: str, user_id: str) -> Tuple[Dict[str, Any], bool]:
    """Pure function: remove filter from store data"""
    filter_data = store_data["filters"].get(filter_id)
    if not filter_data or filter_data["user_id"] != user_id:
        return store_data, False
    
    new_filters = {k: v for k, v in store_data["filters"].items() if k != filter_id}
    
    new_store = {
        **store_data,
        "filters": new_filters
    }
    
    return new_store, True