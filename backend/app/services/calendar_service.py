"""
Calendar service for database operations and iCal synchronization.

IMPERATIVE SHELL - Orchestrates pure functions with I/O operations.
"""

import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.calendar import Calendar, Event, Filter
from ..data.calendar import (
    create_calendar_data, update_calendar_data, mark_calendar_fetched,
    create_event_data, create_filter_data, validate_calendar_data,
    validate_filter_data
)
from ..data.ical_parser import parse_ical_content


async def fetch_ical_content(url: str, timeout: int = 30) -> Tuple[bool, str, str]:
    """
    Fetch iCal content from URL.
    
    Args:
        url: iCal URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (success, content, error_message)
        
    I/O Operation - HTTP request with error handling.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return True, response.text, ""
    
    except httpx.TimeoutException:
        return False, "", f"Timeout fetching calendar from {url}"
    except httpx.HTTPStatusError as e:
        return False, "", f"HTTP {e.response.status_code} error fetching calendar"
    except Exception as e:
        return False, "", f"Error fetching calendar: {str(e)}"


def create_calendar(db: Session, name: str, source_url: str,
                   calendar_type: str = "user", domain_key: Optional[str] = None,
                   user_id: Optional[int] = None) -> Tuple[bool, Optional[Calendar], str]:
    """
    Create new calendar in database.

    Args:
        db: Database session
        name: Calendar name
        source_url: iCal source URL
        calendar_type: "user" or "domain"
        domain_key: Domain key for domain calendars
        user_id: User ID for user scoping

    Returns:
        Tuple of (success, calendar_obj, error_message)

    I/O Operation - Database creation with validation.
    """
    # Validate data using pure function
    is_valid, error_msg = validate_calendar_data(name, source_url)
    if not is_valid:
        return False, None, error_msg

    try:
        # Create calendar data using pure function
        calendar_data = create_calendar_data(
            name=name,
            source_url=source_url,
            calendar_type=calendar_type,
            domain_key=domain_key,
            user_id=user_id
        )

        # Create database object
        calendar = Calendar(**calendar_data)
        db.add(calendar)
        db.commit()
        db.refresh(calendar)

        return True, calendar, ""

    except Exception as e:
        db.rollback()
        return False, None, f"Database error: {str(e)}"


def get_calendars(db: Session, user_id: Optional[int] = None) -> List[Calendar]:
    """
    Get calendars from database.

    Args:
        db: Database session
        user_id: Filter by user_id if provided

    Returns:
        List of calendar objects

    I/O Operation - Database query.
    """
    query = db.query(Calendar)

    if user_id:
        query = query.filter(Calendar.user_id == user_id)

    return query.all()


def get_calendar_by_id(db: Session, calendar_id: int,
                      user_id: Optional[int] = None) -> Optional[Calendar]:
    """
    Get calendar by ID.

    Args:
        db: Database session
        calendar_id: Calendar ID
        user_id: Filter by user_id if provided

    Returns:
        Calendar object or None

    I/O Operation - Database query with graceful degradation.
    """
    try:
        query = db.query(Calendar).filter(Calendar.id == calendar_id)

        if user_id:
            query = query.filter(Calendar.user_id == user_id)

        return query.first()
    except Exception as e:
        # Graceful degradation for database issues (e.g., tables not ready in test environment)
        print(f"⚠️ Database query error in get_calendar_by_id: {e}")
        return None


def get_calendar_by_domain(db: Session, domain_key: str) -> Optional[Calendar]:
    """
    Get domain calendar by domain key.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        Calendar object or None
        
    I/O Operation - Database query.
    """
    return db.query(Calendar).filter(
        and_(Calendar.domain_key == domain_key, Calendar.type == "domain")
    ).first()


def delete_calendar(db: Session, calendar_id: int,
                   user_id: Optional[int] = None) -> Tuple[bool, str]:
    """
    Delete calendar from database.

    Args:
        db: Database session
        calendar_id: Calendar ID to delete
        user_id: Verify ownership if provided

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database deletion.
    """
    try:
        calendar = get_calendar_by_id(db, calendar_id, user_id)
        if not calendar:
            return False, "Calendar not found"

        db.delete(calendar)
        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Database error: {str(e)}"


async def sync_calendar_events(db: Session, calendar: Calendar) -> Tuple[bool, int, str]:
    """
    Synchronize calendar events from iCal source.
    
    Args:
        db: Database session
        calendar: Calendar object to sync
        
    Returns:
        Tuple of (success, event_count, error_message)
        
    I/O Operation - Orchestrates HTTP fetch and database updates.
    """
    try:
        # Fetch iCal content
        success, ical_content, error = await fetch_ical_content(calendar.source_url)
        if not success:
            return False, 0, error
        
        # Parse iCal content using pure function
        parse_success, events_data, parse_error = parse_ical_content(ical_content)
        if not parse_success:
            return False, 0, parse_error
        
        # Filter out events older than 1 week (much simpler approach)
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        filtered_events = []
        for event_data in events_data:
            # Check event start time
            start_time = event_data.get('start_time')
            if start_time:
                try:
                    # start_time is already a datetime object from the parser
                    if isinstance(start_time, str):
                        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    # Only keep events from the last week or future
                    if start_time >= one_week_ago:
                        filtered_events.append(event_data)
                except (ValueError, AttributeError):
                    # If we can't parse the date, keep the event to be safe
                    filtered_events.append(event_data)
            else:
                # If no start time, keep the event
                filtered_events.append(event_data)
        
        # Clear existing events for this calendar
        db.query(Event).filter(Event.calendar_id == calendar.id).delete()
        
        # Create new events (only recent/future ones)
        event_count = 0
        for event_data in filtered_events:
            # Transform to database format using pure function
            db_event_data = create_event_data(calendar.id, event_data)
            event = Event(**db_event_data)
            db.add(event)
            event_count += 1
        
        # Update calendar last_fetched using pure function
        updated_calendar_data = mark_calendar_fetched(calendar.__dict__)
        for key, value in updated_calendar_data.items():
            if hasattr(calendar, key):
                setattr(calendar, key, value)
        
        db.commit()
        return True, event_count, ""
        
    except Exception as e:
        db.rollback()
        return False, 0, f"Sync error: {str(e)}"


def get_calendar_events(db: Session, calendar_id: int) -> List[Event]:
    """
    Get events for calendar.
    
    Args:
        db: Database session
        calendar_id: Calendar ID
        
    Returns:
        List of event objects
        
    I/O Operation - Database query.
    """
    return db.query(Event).filter(Event.calendar_id == calendar_id).all()


def create_filter(db: Session, name: str, calendar_id: Optional[int] = None,
                 domain_key: Optional[str] = None, user_id: Optional[int] = None,
                 subscribed_event_ids: Optional[List[int]] = None,
                 subscribed_group_ids: Optional[List[int]] = None,
                 unselected_event_ids: Optional[List[str]] = None,
                 include_future_events: Optional[bool] = None) -> Tuple[bool, Optional[Filter], str]:
    """
    Create filter in database.

    Args:
        db: Database session
        name: Filter name
        calendar_id: Calendar ID for user filters
        domain_key: Domain key for domain filters
        user_id: User ID for user scoping
        subscribed_event_ids: Event IDs/titles to include
        subscribed_group_ids: Group IDs to include (domain filters only)
        unselected_event_ids: Event titles to exclude from groups (domain filters only)
        include_future_events: Include future recurring events (personal calendars only)

    Returns:
        Tuple of (success, filter_obj, error_message)

    I/O Operation - Database creation with validation.
    """
    # Validate data using pure function
    is_valid, error_msg = validate_filter_data(
        name=name,
        calendar_id=calendar_id,
        domain_key=domain_key,
        subscribed_event_ids=subscribed_event_ids,
        subscribed_group_ids=subscribed_group_ids
    )
    if not is_valid:
        return False, None, error_msg

    try:
        # Create filter data using pure function
        filter_data = create_filter_data(
            name=name,
            calendar_id=calendar_id,
            domain_key=domain_key,
            user_id=user_id,
            subscribed_event_ids=subscribed_event_ids,
            subscribed_group_ids=subscribed_group_ids,
            unselected_event_ids=unselected_event_ids,
            include_future_events=include_future_events
        )

        # Create database object
        filter_obj = Filter(**filter_data)
        db.add(filter_obj)
        db.commit()
        db.refresh(filter_obj)

        return True, filter_obj, ""

    except Exception as e:
        db.rollback()
        return False, None, f"Database error: {str(e)}"


def get_filters(db: Session, calendar_id: Optional[int] = None,
               domain_key: Optional[str] = None, user_id: Optional[int] = None) -> List[Filter]:
    """
    Get filters from database.

    Args:
        db: Database session
        calendar_id: Filter by calendar ID
        domain_key: Filter by domain key
        user_id: Filter by user_id

    Returns:
        List of filter objects

    I/O Operation - Database query.
    """
    query = db.query(Filter)

    if calendar_id:
        query = query.filter(Filter.calendar_id == calendar_id)

    if domain_key:
        query = query.filter(Filter.domain_key == domain_key)

    if user_id:
        query = query.filter(Filter.user_id == user_id)

    return query.all()


def get_filter_by_uuid(db: Session, link_uuid: str) -> Optional[Filter]:
    """
    Get filter by UUID for iCal export.
    
    Args:
        db: Database session
        link_uuid: Filter UUID
        
    Returns:
        Filter object or None
        
    I/O Operation - Database query with graceful degradation.
    """
    try:
        return db.query(Filter).filter(Filter.link_uuid == link_uuid).first()
    except Exception as e:
        # Graceful degradation for database issues (e.g., tables not ready in test environment)
        print(f"⚠️ Database query error in get_filter_by_uuid: {e}")
        return None


def get_filter_by_id(db: Session, filter_id: int, calendar_id: Optional[int] = None,
                     domain_key: Optional[str] = None, user_id: Optional[int] = None) -> Optional[Filter]:
    """
    Get filter by ID with ownership verification.

    Args:
        db: Database session
        filter_id: Filter ID
        calendar_id: Calendar ID for user filters
        domain_key: Domain key for domain filters
        user_id: User ID for user scoping

    Returns:
        Filter object or None

    I/O Operation - Database query.
    """
    query = db.query(Filter).filter(Filter.id == filter_id)

    if calendar_id:
        query = query.filter(Filter.calendar_id == calendar_id)

    if domain_key:
        query = query.filter(Filter.domain_key == domain_key)

    if user_id:
        query = query.filter(Filter.user_id == user_id)

    return query.first()


def delete_filter(db: Session, filter_id: int, calendar_id: Optional[int] = None,
                  domain_key: Optional[str] = None, user_id: Optional[int] = None) -> Tuple[bool, str]:
    """
    Delete filter from database.

    Args:
        db: Database session
        filter_id: Filter ID to delete
        calendar_id: Calendar ID for user filters
        domain_key: Domain key for domain filters
        user_id: User ID for user scoping

    Returns:
        Tuple of (success, error_message)

    I/O Operation - Database deletion.
    """
    try:
        filter_obj = get_filter_by_id(db, filter_id, calendar_id, domain_key, user_id)
        if not filter_obj:
            return False, "Filter not found"

        db.delete(filter_obj)
        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Database error: {str(e)}"