"""
Repository Layer - Imperative Shell for I/O
Rich Hickey: "Push side effects to the edges"
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime

from ..data.schemas import (
    AppState, CommunityData, GroupData, CalendarData, 
    FilterData, SubscriptionData, EventData, FilteredCalendarData
)


class StateRepository:
    """
    Imperative shell for state persistence
    All I/O operations isolated here
    """
    
    def __init__(self, db_path: str = "data/app.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure database schema exists"""
        with self._get_connection() as conn:
            # Communities table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS communities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    url_path TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    calendar_url TEXT NOT NULL,
                    admin_emails TEXT NOT NULL,  -- JSON array
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Groups table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id TEXT PRIMARY KEY,
                    community_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    icon TEXT NOT NULL,
                    color TEXT NOT NULL,
                    assignment_rules TEXT NOT NULL,  -- JSON array
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (community_id) REFERENCES communities (id)
                )
            """)
            
            # Calendars table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS calendars (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Filters table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS filters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    include_categories TEXT NOT NULL,  -- JSON array
                    exclude_categories TEXT NOT NULL,  -- JSON array
                    filter_mode TEXT NOT NULL,
                    calendar_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (calendar_id) REFERENCES calendars (id)
                )
            """)
            
            # Subscriptions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    community_id TEXT NOT NULL,
                    subscribed_groups TEXT NOT NULL,  -- JSON array
                    explicitly_subscribed_categories TEXT NOT NULL,  -- JSON array
                    explicitly_unsubscribed_categories TEXT NOT NULL,  -- JSON array
                    filter_mode TEXT NOT NULL,
                    personal_token TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    FOREIGN KEY (community_id) REFERENCES communities (id)
                )
            """)
            
            # Filtered calendars table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS filtered_calendars (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_calendar_id TEXT NOT NULL,
                    filter_config TEXT NOT NULL,  -- JSON
                    public_token TEXT UNIQUE,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_accessed TEXT,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (source_calendar_id) REFERENCES calendars (id)
                )
            """)
            
            # Events cache table (for performance)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events_cache (
                    calendar_id TEXT NOT NULL,
                    event_data TEXT NOT NULL,  -- JSON
                    cached_at TEXT NOT NULL,
                    PRIMARY KEY (calendar_id)
                )
            """)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def load_state(self) -> AppState:
        """
        Load complete application state from database
        This is the boundary between I/O and pure functions
        """
        with self._get_connection() as conn:
            # Load communities
            communities = {}
            for row in conn.execute("SELECT * FROM communities"):
                communities[row["id"]] = CommunityData(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    url_path=row["url_path"],
                    password_hash=row["password_hash"],
                    calendar_url=row["calendar_url"],
                    admin_emails=json.loads(row["admin_emails"]),
                    is_active=bool(row["is_active"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
            
            # Load groups
            groups = {}
            for row in conn.execute("SELECT * FROM groups"):
                groups[row["id"]] = GroupData(
                    id=row["id"],
                    community_id=row["community_id"],
                    name=row["name"],
                    description=row["description"],
                    icon=row["icon"],
                    color=row["color"],
                    assignment_rules=json.loads(row["assignment_rules"]),
                    is_active=bool(row["is_active"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
            
            # Load calendars
            calendars = {}
            for row in conn.execute("SELECT * FROM calendars"):
                calendars[row["id"]] = CalendarData(
                    id=row["id"],
                    name=row["name"],
                    url=row["url"],
                    user_id=row["user_id"],
                    is_active=bool(row["is_active"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
            
            # Load filters
            filters = {}
            for row in conn.execute("SELECT * FROM filters"):
                filters[row["id"]] = FilterData(
                    id=row["id"],
                    name=row["name"],
                    include_categories=json.loads(row["include_categories"]),
                    exclude_categories=json.loads(row["exclude_categories"]),
                    filter_mode=row["filter_mode"],
                    calendar_id=row["calendar_id"],
                    user_id=row["user_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
            
            # Load subscriptions
            subscriptions = {}
            for row in conn.execute("SELECT * FROM subscriptions"):
                subscriptions[row["id"]] = SubscriptionData(
                    id=row["id"],
                    user_id=row["user_id"],
                    community_id=row["community_id"],
                    subscribed_groups=json.loads(row["subscribed_groups"]),
                    explicitly_subscribed_categories=json.loads(row["explicitly_subscribed_categories"]),
                    explicitly_unsubscribed_categories=json.loads(row["explicitly_unsubscribed_categories"]),
                    filter_mode=row["filter_mode"],
                    personal_token=row["personal_token"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    last_accessed=row["last_accessed"]
                )
            
            # Load filtered calendars
            filtered_calendars = {}
            for row in conn.execute("SELECT * FROM filtered_calendars"):
                filtered_calendars[row["id"]] = FilteredCalendarData(
                    id=row["id"],
                    name=row["name"],
                    source_calendar_id=row["source_calendar_id"],
                    filter_config=json.loads(row["filter_config"]),
                    public_token=row["public_token"],
                    user_id=row["user_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    last_accessed=row["last_accessed"],
                    access_count=int(row["access_count"]),
                    is_active=bool(row["is_active"])
                )
            
            # Load events cache
            events_cache = {}
            for row in conn.execute("SELECT * FROM events_cache"):
                events_data = json.loads(row["event_data"])
                events_cache[row["calendar_id"]] = [
                    EventData(**event) for event in events_data
                ]
        
        return AppState(
            calendars=calendars,
            communities=communities,
            groups=groups,
            filters=filters,
            subscriptions=subscriptions,
            filtered_calendars=filtered_calendars,
            events_cache=events_cache,
            version=0  # Will be managed by the application layer
        )
    
    def save_state(self, state: AppState) -> bool:
        """
        Save complete application state to database
        Atomic transaction - all or nothing
        """
        try:
            with self._get_connection() as conn:
                conn.execute("BEGIN TRANSACTION")
                
                # Clear existing data
                conn.execute("DELETE FROM events_cache")
                conn.execute("DELETE FROM filtered_calendars")
                conn.execute("DELETE FROM subscriptions")
                conn.execute("DELETE FROM filters")
                conn.execute("DELETE FROM groups")
                conn.execute("DELETE FROM calendars")
                conn.execute("DELETE FROM communities")
                
                # Save communities
                for community in state.communities.values():
                    conn.execute("""
                        INSERT INTO communities 
                        (id, name, description, url_path, password_hash, calendar_url, 
                         admin_emails, is_active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        community.id, community.name, community.description,
                        community.url_path, community.password_hash, community.calendar_url,
                        json.dumps(community.admin_emails), community.is_active,
                        community.created_at, community.updated_at
                    ))
                
                # Save groups
                for group in state.groups.values():
                    conn.execute("""
                        INSERT INTO groups 
                        (id, community_id, name, description, icon, color, 
                         assignment_rules, is_active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        group.id, group.community_id, group.name, group.description,
                        group.icon, group.color, json.dumps(group.assignment_rules),
                        group.is_active, group.created_at, group.updated_at
                    ))
                
                # Save calendars
                for calendar in state.calendars.values():
                    conn.execute("""
                        INSERT INTO calendars 
                        (id, name, url, user_id, is_active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        calendar.id, calendar.name, calendar.url, calendar.user_id,
                        calendar.is_active, calendar.created_at, calendar.updated_at
                    ))
                
                # Save filters
                for filter_data in state.filters.values():
                    conn.execute("""
                        INSERT INTO filters 
                        (id, name, include_categories, exclude_categories, filter_mode,
                         calendar_id, user_id, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        filter_data.id, filter_data.name,
                        json.dumps(filter_data.include_categories),
                        json.dumps(filter_data.exclude_categories),
                        filter_data.filter_mode, filter_data.calendar_id,
                        filter_data.user_id, filter_data.created_at, filter_data.updated_at
                    ))
                
                # Save subscriptions
                for subscription in state.subscriptions.values():
                    conn.execute("""
                        INSERT INTO subscriptions 
                        (id, user_id, community_id, subscribed_groups,
                         explicitly_subscribed_categories, explicitly_unsubscribed_categories,
                         filter_mode, personal_token, created_at, updated_at, last_accessed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        subscription.id, subscription.user_id, subscription.community_id,
                        json.dumps(subscription.subscribed_groups),
                        json.dumps(subscription.explicitly_subscribed_categories),
                        json.dumps(subscription.explicitly_unsubscribed_categories),
                        subscription.filter_mode, subscription.personal_token,
                        subscription.created_at, subscription.updated_at, subscription.last_accessed
                    ))
                
                # Save filtered calendars
                for filtered_cal in state.filtered_calendars.values():
                    conn.execute("""
                        INSERT INTO filtered_calendars 
                        (id, name, source_calendar_id, filter_config, public_token,
                         user_id, created_at, updated_at, last_accessed, access_count, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        filtered_cal.id, filtered_cal.name, filtered_cal.source_calendar_id,
                        json.dumps(filtered_cal.filter_config), filtered_cal.public_token,
                        filtered_cal.user_id, filtered_cal.created_at, filtered_cal.updated_at,
                        filtered_cal.last_accessed, filtered_cal.access_count, filtered_cal.is_active
                    ))
                
                # Save events cache
                for calendar_id, events in state.events_cache.items():
                    events_json = json.dumps([
                        {
                            "uid": event.uid,
                            "summary": event.summary,
                            "description": event.description,
                            "location": event.location,
                            "dtstart": event.dtstart,
                            "dtend": event.dtend,
                            "categories": event.categories
                        }
                        for event in events
                    ])
                    conn.execute("""
                        INSERT INTO events_cache (calendar_id, event_data, cached_at)
                        VALUES (?, ?, ?)
                    """, (calendar_id, events_json, datetime.utcnow().isoformat()))
                
                conn.execute("COMMIT")
                return True
                
        except Exception as e:
            conn.execute("ROLLBACK")
            print(f"Error saving state: {e}")
            return False