"""
Data Models - Immutable dataclasses (Clojure-inspired)
Pure data structures with no business logic
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class CalendarEntry:
    """Immutable calendar entry"""
    id: str
    name: str
    url: str
    user_id: str


@dataclass(frozen=True) 
class Event:
    """Immutable event data structure"""
    uid: str
    summary: str
    dtstart: str
    dtend: str
    location: Optional[str]
    description: Optional[str]
    raw: str


@dataclass(frozen=True)
class Filter:
    """Immutable filter configuration"""
    id: str
    name: str
    calendar_id: str
    types: List[str]
    user_id: str