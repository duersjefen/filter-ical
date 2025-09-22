"""
Filtered Calendar Regeneration (Functional Core + I/O Shell)
Pure functions for regenerating filtered calendar iCal content.
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlmodel import Session, select
from datetime import datetime

from ..models import FilteredCalendar, Event, Calendar
from .filters import apply_saved_filter_config, parse_json_field
from .ical_parser import create_ical_from_events


def get_filtered_events_from_db(
    source_calendar_id: str, 
    filter_config: Dict[str, Any],
    session: Session
) -> List[Dict[str, Any]]:
    """
    Get events from database and apply filter configuration.
    I/O Shell function - orchestrates database access and pure filtering.
    
    Args:
        source_calendar_id: ID of source calendar
        filter_config: Filter configuration dict
        session: Database session
        
    Returns:
        List of filtered event dictionaries
    """
    # Get events from database
    events = session.exec(
        select(Event).where(Event.calendar_id == source_calendar_id)
    ).all()
    
    # Convert to dict format for pure functions
    events_data = []
    for event in events:
        events_data.append({
            "id": event.id,
            "title": event.title,
            "start": event.start,
            "end": event.end,
            "event_type": event.event_type,
            "description": event.description,
            "location": event.location
        })
    
    # Apply consistent date filtering: only recent (1 week) + future events
    from ..core.ical_parser import filter_recent_and_future_events
    recent_and_future_events = filter_recent_and_future_events(events_data)
    
    # Apply filter configuration using pure function
    filtered_events = apply_saved_filter_config(recent_and_future_events, filter_config)
    
    return filtered_events


def get_cached_filtered_ical(filtered_calendar: FilteredCalendar) -> Optional[str]:
    """
    Pure function: Get cached iCal content if it exists and is valid.
    Returns None if cache is empty or needs regeneration.
    
    Args:
        filtered_calendar: FilteredCalendar object
        
    Returns:
        Cached iCal content or None if needs regeneration
    """
    # Check if cache exists and calendar doesn't need regeneration
    if (filtered_calendar.cached_ical_content and 
        not filtered_calendar.needs_regeneration and
        filtered_calendar.cache_updated_at):
        return filtered_calendar.cached_ical_content
    
    return None


def get_filtered_ical_cache_first(filtered_calendar: FilteredCalendar, session: Session) -> Tuple[Optional[str], Optional[str]]:
    """
    Cache-first iCal content retrieval with automatic regeneration.
    I/O Shell function - orchestrates cache check and regeneration.
    
    Args:
        filtered_calendar: FilteredCalendar object to get content for
        session: Database session
        
    Returns:
        Tuple of (ical_content, error_message)
    """
    # Try to get cached content first
    cached_content = get_cached_filtered_ical(filtered_calendar)
    if cached_content:
        print(f"📦 Using cached iCal content for filtered calendar {filtered_calendar.id}")
        return cached_content, None
    
    # Cache miss or needs regeneration - generate fresh content
    print(f"🔄 Regenerating iCal content for filtered calendar {filtered_calendar.id}")
    fresh_content, error = regenerate_filtered_calendar_content(filtered_calendar, session)
    
    if error:
        return None, error
    
    # Update cache with fresh content
    success = update_filtered_calendar_cache(filtered_calendar, fresh_content, session)
    if not success:
        return fresh_content, "Warning: Failed to update cache"
    
    return fresh_content, None


def regenerate_filtered_calendar_content(filtered_calendar: FilteredCalendar, session: Session) -> Tuple[Optional[str], Optional[str]]:
    """
    Regenerate iCal content for a filtered calendar.
    I/O Shell function - orchestrates data fetching and iCal generation.
    
    Args:
        filtered_calendar: FilteredCalendar object to regenerate
        session: Database session
        
    Returns:
        Tuple of (ical_content, error_message)
    """
    try:
        # Parse filter configuration
        include_events = parse_json_field(filtered_calendar.include_events, [])
        exclude_events = parse_json_field(filtered_calendar.exclude_events, [])
        
        filter_config = {
            'include_events': include_events,
            'exclude_events': exclude_events,
            'filter_mode': filtered_calendar.filter_mode
        }
        
        # Get filtered events from database
        filtered_events = get_filtered_events_from_db(
            filtered_calendar.source_calendar_id,
            filter_config,
            session
        )
        
        # Generate iCal content using pure function
        ical_content = create_ical_from_events(filtered_events, filtered_calendar.name)
        
        return ical_content, None
        
    except Exception as e:
        return None, f"Error regenerating filtered calendar: {str(e)}"


def update_filtered_calendar_cache(
    filtered_calendar: FilteredCalendar, 
    ical_content: str,
    session: Session
) -> bool:
    """
    Update filtered calendar with new iCal content and cache timestamps.
    I/O Shell function - handles database updates.
    
    Args:
        filtered_calendar: FilteredCalendar to update
        ical_content: New iCal content 
        session: Database session
        
    Returns:
        True if update successful, False otherwise
    """
    try:
        import hashlib
        
        # Store generated iCal content in cache fields
        filtered_calendar.cached_ical_content = ical_content
        filtered_calendar.cached_content_hash = hashlib.sha256(ical_content.encode()).hexdigest()
        filtered_calendar.cache_updated_at = datetime.utcnow()
        
        # Clear regeneration flag and update timestamps
        filtered_calendar.needs_regeneration = False
        filtered_calendar.updated_at = datetime.utcnow()
        
        session.add(filtered_calendar)
        session.commit()
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating filtered calendar {filtered_calendar.id}: {e}")
        session.rollback()
        return False


def get_filtered_calendars_needing_regeneration(session: Session) -> List[FilteredCalendar]:
    """
    Get all filtered calendars that need regeneration.
    I/O Shell function - database query.
    
    Args:
        session: Database session
        
    Returns:
        List of FilteredCalendar objects needing regeneration
    """
    return session.exec(
        select(FilteredCalendar).where(FilteredCalendar.needs_regeneration == True)
    ).all()


def regenerate_single_filtered_calendar(filtered_calendar: FilteredCalendar, session: Session) -> bool:
    """
    Regenerate a single filtered calendar's content.
    I/O Shell function - orchestrates regeneration process.
    
    Args:
        filtered_calendar: FilteredCalendar to regenerate
        session: Database session
        
    Returns:
        True if regeneration successful, False otherwise
    """
    try:
        print(f"🔄 Regenerating filtered calendar {filtered_calendar.id} ({filtered_calendar.name})")
        
        # Regenerate iCal content
        ical_content, error = regenerate_filtered_calendar_content(filtered_calendar, session)
        
        if error:
            print(f"❌ Failed to regenerate filtered calendar {filtered_calendar.id}: {error}")
            return False
        
        # Update cache and flags
        success = update_filtered_calendar_cache(filtered_calendar, ical_content, session)
        
        if success:
            print(f"✅ Filtered calendar {filtered_calendar.id} regenerated successfully")
        
        return success
        
    except Exception as e:
        print(f"❌ Error regenerating filtered calendar {filtered_calendar.id}: {e}")
        return False


def mark_all_dependent_filters_for_regeneration(source_calendar_id: str, session: Session) -> int:
    """
    Mark all filtered calendars that depend on a source calendar for regeneration.
    I/O Shell function - updates database flags.
    
    Args:
        source_calendar_id: ID of the source calendar that changed
        session: Database session
        
    Returns:
        Number of filtered calendars marked for regeneration
    """
    try:
        filtered_calendars = session.exec(
            select(FilteredCalendar).where(FilteredCalendar.source_calendar_id == source_calendar_id)
        ).all()
        
        count = 0
        for fc in filtered_calendars:
            if not fc.needs_regeneration:  # Only mark if not already marked
                fc.needs_regeneration = True
                fc.updated_at = datetime.utcnow()
                session.add(fc)
                count += 1
        
        if count > 0:
            session.commit()
            print(f"🔄 Marked {count} filtered calendars for regeneration")
        
        return count
        
    except Exception as e:
        print(f"❌ Error marking filtered calendars for regeneration: {e}")
        session.rollback()
        return 0