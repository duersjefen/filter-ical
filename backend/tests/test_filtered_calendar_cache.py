"""
Test filtered calendar cache-first iCal generation
Validates that real-time updates work properly and iCal content is RFC 5545 compliant
"""
import pytest
import hashlib
from datetime import datetime, timedelta
from sqlmodel import Session

from app.models import Calendar, Event, FilteredCalendar
from app.core.filters import serialize_json_field
from app.core.filter_regeneration import (
    get_cached_filtered_ical,
    get_filtered_ical_cache_first, 
    regenerate_filtered_calendar_content,
    update_filtered_calendar_cache
)
from app.core.filters import serialize_json_field
from app.core.ical_parser import create_ical_from_events


class TestFilteredCalendarCache:
    """Test suite for filtered calendar cache functionality"""
    
    def test_cache_miss_generates_content(self, session: Session, sample_calendar_with_events):
        """Test that cache miss generates fresh iCal content"""
        calendar = sample_calendar_with_events
        
        # Create filtered calendar without cache
        filtered_calendar = FilteredCalendar(
            name="Test Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            selected_groups=serialize_json_field(["grp_work"]),
            selected_events=serialize_json_field([]),
            needs_regeneration=True,
            cached_ical_content=None  # No cache
        )
        session.add(filtered_calendar)
        session.commit()
        session.refresh(filtered_calendar)
        
        # Get content - should generate fresh
        ical_content, error = get_filtered_ical_cache_first(filtered_calendar, session)
        
        assert error is None
        assert ical_content is not None
        assert "BEGIN:VCALENDAR" in ical_content
        assert "END:VCALENDAR" in ical_content
        
        # Verify cache was populated
        session.refresh(filtered_calendar)
        assert filtered_calendar.cached_ical_content is not None
        assert filtered_calendar.cached_content_hash is not None
        assert filtered_calendar.cache_updated_at is not None
        assert not filtered_calendar.needs_regeneration
    
    def test_cache_hit_returns_cached_content(self, session: Session, sample_calendar_with_events):
        """Test that cache hit returns cached content without regeneration"""
        calendar = sample_calendar_with_events
        
        # Create filtered calendar with existing cache
        cached_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
        content_hash = hashlib.sha256(cached_content.encode()).hexdigest()
        
        filtered_calendar = FilteredCalendar(
            name="Cached Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            selected_groups=serialize_json_field(["grp_work"]),
            selected_events=serialize_json_field([]),
            needs_regeneration=False,  # Cache is valid
            cached_ical_content=cached_content,
            cached_content_hash=content_hash,
            cache_updated_at=datetime.utcnow()
        )
        session.add(filtered_calendar)
        session.commit()
        session.refresh(filtered_calendar)
        
        # Get content - should return cached
        ical_content, error = get_filtered_ical_cache_first(filtered_calendar, session)
        
        assert error is None
        assert ical_content == cached_content
    
    def test_cache_invalidation_triggers_regeneration(self, session: Session, sample_calendar_with_events):
        """Test that needs_regeneration=True triggers fresh generation"""
        calendar = sample_calendar_with_events
        
        # Create filtered calendar with stale cache
        stale_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
        
        filtered_calendar = FilteredCalendar(
            name="Stale Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            selected_groups=serialize_json_field(["grp_work"]),
            selected_events=serialize_json_field([]),
            needs_regeneration=True,  # Cache is invalid
            cached_ical_content=stale_content,
            cached_content_hash="old_hash",
            cache_updated_at=datetime.utcnow() - timedelta(days=1)
        )
        session.add(filtered_calendar)
        session.commit()
        session.refresh(filtered_calendar)
        
        # Get content - should regenerate
        ical_content, error = get_filtered_ical_cache_first(filtered_calendar, session)
        
        assert error is None
        assert ical_content != stale_content  # Should be fresh content
        assert "BEGIN:VCALENDAR" in ical_content
        
        # Verify cache was updated
        session.refresh(filtered_calendar)
        assert filtered_calendar.cached_ical_content != stale_content
        assert not filtered_calendar.needs_regeneration
    
    def test_ical_content_is_rfc5545_compliant(self, session: Session, sample_calendar_with_events):
        """Test that generated iCal content follows RFC 5545 standard"""
        calendar = sample_calendar_with_events
        
        filtered_calendar = FilteredCalendar(
            name="RFC Test Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            selected_groups=serialize_json_field(["grp_work"]),
            selected_events=serialize_json_field([]),
            needs_regeneration=True
        )
        session.add(filtered_calendar)
        session.commit()
        session.refresh(filtered_calendar)
        
        # Generate content
        ical_content, error = get_filtered_ical_cache_first(filtered_calendar, session)
        
        assert error is None
        assert ical_content is not None
        
        # Validate RFC 5545 compliance
        lines = ical_content.strip().split('\n')
        
        # Must start with BEGIN:VCALENDAR
        assert lines[0] == "BEGIN:VCALENDAR"
        
        # Must end with END:VCALENDAR
        assert lines[-1] == "END:VCALENDAR"
        
        # Must have VERSION and PRODID
        content_str = ical_content
        assert "VERSION:2.0" in content_str
        assert "PRODID:" in content_str
        assert "CALSCALE:GREGORIAN" in content_str
        
        # Events should have required fields
        if "BEGIN:VEVENT" in content_str:
            assert "DTSTART:" in content_str
            assert "DTEND:" in content_str
            assert "SUMMARY:" in content_str
            assert "UID:" in content_str
            assert "DTSTAMP:" in content_str
    
    def test_filter_mode_include_only_includes_selected_events(self, session: Session, sample_calendar_with_events):
        """Test that include filter mode only includes specified event types"""
        calendar = sample_calendar_with_events
        
        # Create events of different types
        work_event = Event(
            title="Work Meeting",
            start=datetime.utcnow() + timedelta(days=1),
            end=datetime.utcnow() + timedelta(days=1, hours=1),
            calendar_id=calendar.id,
            category="Work"
        )
        personal_event = Event(
            title="Personal Task",
            start=datetime.utcnow() + timedelta(days=2),
            end=datetime.utcnow() + timedelta(days=2, hours=1),
            calendar_id=calendar.id,
            category="Personal"
        )
        session.add_all([work_event, personal_event])
        session.commit()
        
        # Create filtered calendar that only includes Work events
        filtered_calendar = FilteredCalendar(
            name="Work Only Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            selected_groups=serialize_json_field(["grp_work"]),
            selected_events=serialize_json_field([]),
            needs_regeneration=True
        )
        session.add(filtered_calendar)
        session.commit()
        session.refresh(filtered_calendar)
        
        # Generate content
        ical_content, error = get_filtered_ical_cache_first(filtered_calendar, session)
        
        assert error is None
        assert ical_content is not None
        
        # Should include Work event
        assert "Work Meeting" in ical_content
        
        # Should NOT include Personal event
        assert "Personal Task" not in ical_content
    
    def test_filter_mode_exclude_excludes_selected_events(self, session: Session, sample_calendar_with_events):
        """Test that exclude filter mode excludes specified event types"""
        calendar = sample_calendar_with_events
        
        # Create events of different types
        work_event = Event(
            title="Work Meeting",
            start=datetime.utcnow() + timedelta(days=1),
            end=datetime.utcnow() + timedelta(days=1, hours=1),
            calendar_id=calendar.id,
            category="Work"
        )
        personal_event = Event(
            title="Personal Task",
            start=datetime.utcnow() + timedelta(days=2),
            end=datetime.utcnow() + timedelta(days=2, hours=1),
            calendar_id=calendar.id,
            category="Personal"
        )
        session.add_all([work_event, personal_event])
        session.commit()
        
        # Create filtered calendar that excludes Work events
        filtered_calendar = FilteredCalendar(
            name="No Work Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field([]),
            exclude_events=serialize_json_field(["Work"]),
            filter_mode=FilterMode.exclude,
            needs_regeneration=True
        )
        session.add(filtered_calendar)
        session.commit()
        session.refresh(filtered_calendar)
        
        # Generate content
        ical_content, error = get_filtered_ical_cache_first(filtered_calendar, session)
        
        assert error is None
        assert ical_content is not None
        
        # Should include Personal event
        assert "Personal Task" in ical_content
        
        # Should NOT include Work event
        assert "Work Meeting" not in ical_content
    
    def test_cache_update_stores_content_and_hash(self, session: Session, sample_calendar_with_events):
        """Test that cache update properly stores content and hash"""
        calendar = sample_calendar_with_events
        
        filtered_calendar = FilteredCalendar(
            name="Cache Update Test",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            selected_groups=serialize_json_field(["grp_work"]),
            selected_events=serialize_json_field([]),
            needs_regeneration=True
        )
        session.add(filtered_calendar)
        session.commit()
        session.refresh(filtered_calendar)
        
        # Generate test content
        test_content = "BEGIN:VCALENDAR\nVERSION:2.0\nTEST CONTENT\nEND:VCALENDAR"
        expected_hash = hashlib.sha256(test_content.encode()).hexdigest()
        
        # Update cache
        success = update_filtered_calendar_cache(filtered_calendar, test_content, session)
        
        assert success is True
        
        # Verify cache fields were updated
        session.refresh(filtered_calendar)
        assert filtered_calendar.cached_ical_content == test_content
        assert filtered_calendar.cached_content_hash == expected_hash
        assert filtered_calendar.cache_updated_at is not None
        assert not filtered_calendar.needs_regeneration
        
        # Verify updated_at was also updated
        assert filtered_calendar.updated_at is not None