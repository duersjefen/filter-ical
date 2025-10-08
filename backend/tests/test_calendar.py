"""
Unit tests for calendar data functions.

Tests pure functions from app.data.calendar module following TDD principles.
All functions tested here are pure - no side effects, predictable outputs.
"""

import pytest
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

from app.data.calendar import (
    create_calendar_data,
    update_calendar_data,
    mark_calendar_fetched,
    create_event_data,
    filter_events_by_date_range,
    sort_events_by_start_time,
    create_filter_data,
    apply_filter_to_events,
    transform_events_for_export,
    validate_filter_data,
    validate_calendar_data
)


@pytest.mark.unit
class TestCalendarDataCreation:
    """Test calendar data creation functions."""
    
    def test_create_calendar_data_basic(self):
        """Test basic calendar data creation."""
        result = create_calendar_data("Test Calendar", "https://example.com/cal.ics")

        assert result["name"] == "Test Calendar"
        assert result["source_url"] == "https://example.com/cal.ics"
        assert result["type"] == "user"
        assert result["domain_key"] is None
        assert result["user_id"] is None
        assert result["last_fetched"] is None
        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["updated_at"], datetime)
    
    def test_create_calendar_data_domain(self):
        """Test domain calendar data creation."""
        result = create_calendar_data(
            "Domain Cal",
            "https://domain.com/cal.ics",
            calendar_type="domain",
            domain_key="test_domain",
            user_id=123
        )

        assert result["type"] == "domain"
        assert result["domain_key"] == "test_domain"
        assert result["user_id"] == 123
    
    def test_create_calendar_data_strips_whitespace(self):
        """Test that name and URL are stripped of whitespace."""
        result = create_calendar_data("  Test  ", "  https://example.com/cal.ics  ")
        
        assert result["name"] == "Test"
        assert result["source_url"] == "https://example.com/cal.ics"


@pytest.mark.unit 
class TestCalendarDataUpdates:
    """Test calendar data update functions."""
    
    def test_update_calendar_data(self):
        """Test calendar data updates."""
        original = {
            "name": "Original",
            "source_url": "https://original.com",
            "created_at": datetime.now(timezone.utc) - timedelta(days=1)
        }
        
        result = update_calendar_data(original, name="Updated", source_url="https://updated.com")
        
        # Original unchanged
        assert original["name"] == "Original"
        assert original["source_url"] == "https://original.com"
        
        # Result has updates
        assert result["name"] == "Updated"
        assert result["source_url"] == "https://updated.com"
        assert result["created_at"] == original["created_at"]
        assert isinstance(result["updated_at"], datetime)
    
    def test_mark_calendar_fetched_default_time(self):
        """Test marking calendar as fetched with default time."""
        original = {"name": "Test", "last_fetched": None}
        
        result = mark_calendar_fetched(original)
        
        assert original["last_fetched"] is None  # Original unchanged
        assert isinstance(result["last_fetched"], datetime)
        assert isinstance(result["updated_at"], datetime)
    
    def test_mark_calendar_fetched_specific_time(self):
        """Test marking calendar as fetched with specific time."""
        fetch_time = datetime.now(timezone.utc) - timedelta(hours=1)
        original = {"name": "Test", "last_fetched": None}
        
        result = mark_calendar_fetched(original, fetch_time)
        
        assert result["last_fetched"] == fetch_time


@pytest.mark.unit
class TestEventDataCreation:
    """Test event data creation functions."""
    
    def test_create_event_data_basic(self):
        """Test basic event data creation."""
        event_input = {
            "title": "Test Event",
            "start_time": datetime.now(timezone.utc),
            "end_time": datetime.now(timezone.utc) + timedelta(hours=1),
            "description": "Test description",
            "location": "Test location",
            "uid": "test-uid-123",
            "raw_ical": "BEGIN:VEVENT..."
        }
        
        result = create_event_data(calendar_id=1, event_data=event_input)
        
        assert result["calendar_id"] == 1
        assert result["title"] == "Test Event"
        assert result["start_time"] == event_input["start_time"]
        assert result["end_time"] == event_input["end_time"]
        assert result["description"] == "Test description"
        assert result["location"] == "Test location"
        assert result["uid"] == "test-uid-123"
        assert result["other_ical_fields"]["raw_ical"] == "BEGIN:VEVENT..."
        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["updated_at"], datetime)
    
    def test_create_event_data_minimal(self):
        """Test event data creation with minimal input."""
        result = create_event_data(calendar_id=2, event_data={})
        
        assert result["calendar_id"] == 2
        assert result["title"] == ""
        assert result["start_time"] is None
        assert result["end_time"] is None
        assert result["description"] == ""
        assert result["location"] is None
        assert result["uid"] == ""


@pytest.mark.unit
class TestEventFiltering:
    """Test event filtering functions - CRITICAL for date filtering bug fix."""
    
    @pytest.fixture
    def sample_events(self):
        """Sample events with different dates."""
        now = datetime.now(timezone.utc)
        return [
            {
                "id": 1,
                "title": "Past Event",
                "start_time": now - timedelta(days=10)
            },
            {
                "id": 2, 
                "title": "Recent Event",
                "start_time": now - timedelta(days=3)
            },
            {
                "id": 3,
                "title": "Future Event", 
                "start_time": now + timedelta(days=5)
            },
            {
                "id": 4,
                "title": "No Start Time"
                # Missing start_time
            }
        ]
    
    def test_filter_events_by_date_range_basic(self, sample_events):
        """Test basic date range filtering."""
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=5)
        end_date = now + timedelta(days=10)
        
        result = filter_events_by_date_range(sample_events, start_date, end_date)
        
        # Should include recent and future events, exclude past event
        assert len(result) == 2
        assert result[0]["title"] == "Recent Event"
        assert result[1]["title"] == "Future Event"
    
    def test_filter_events_by_date_range_one_week_ago(self, sample_events):
        """Test filtering events from one week ago (matches sync logic)."""
        now = datetime.now(timezone.utc)
        one_week_ago = now - timedelta(days=7)
        
        result = filter_events_by_date_range(sample_events, start_date=one_week_ago)
        
        # Should include recent and future events, exclude 10-day-old event
        assert len(result) == 2
        assert result[0]["title"] == "Recent Event"
        assert result[1]["title"] == "Future Event"
    
    def test_filter_events_by_date_range_string_dates(self):
        """Test filtering with string date format."""
        events = [
            {
                "id": 1,
                "title": "String Date Event",
                "start_time": "2025-09-20T10:00:00Z"
            }
        ]
        
        start_date = datetime(2025, 9, 19, tzinfo=timezone.utc)
        end_date = datetime(2025, 9, 21, tzinfo=timezone.utc)
        
        result = filter_events_by_date_range(events, start_date, end_date)
        
        assert len(result) == 1
        assert result[0]["title"] == "String Date Event"
    
    def test_filter_events_by_date_range_invalid_dates(self):
        """Test filtering with invalid date strings."""
        events = [
            {
                "id": 1,
                "title": "Invalid Date",
                "start_time": "invalid-date"
            }
        ]
        
        start_date = datetime.now(timezone.utc) - timedelta(days=1)
        
        result = filter_events_by_date_range(events, start_date=start_date)
        
        # Invalid dates should be excluded
        assert len(result) == 0
    
    def test_filter_events_by_date_range_no_filters(self, sample_events):
        """Test filtering with no date filters."""
        result = filter_events_by_date_range(sample_events)
        
        # Should return all events with start_time (excludes "No Start Time")
        assert len(result) == 3


@pytest.mark.unit
class TestEventSorting:
    """Test event sorting functions."""
    
    def test_sort_events_by_start_time_ascending(self):
        """Test sorting events by start time ascending."""
        now = datetime.now(timezone.utc)
        events = [
            {"title": "Future", "start_time": now + timedelta(days=1)},
            {"title": "Past", "start_time": now - timedelta(days=1)},
            {"title": "Now", "start_time": now},
        ]
        
        result = sort_events_by_start_time(events)
        
        assert result[0]["title"] == "Past"
        assert result[1]["title"] == "Now"
        assert result[2]["title"] == "Future"
    
    def test_sort_events_by_start_time_descending(self):
        """Test sorting events by start time descending."""
        now = datetime.now(timezone.utc)
        events = [
            {"title": "Past", "start_time": now - timedelta(days=1)},
            {"title": "Future", "start_time": now + timedelta(days=1)},
            {"title": "Now", "start_time": now},
        ]
        
        result = sort_events_by_start_time(events, reverse=True)
        
        assert result[0]["title"] == "Future"
        assert result[1]["title"] == "Now"
        assert result[2]["title"] == "Past"
    
    def test_sort_events_missing_start_time(self):
        """Test sorting events with missing start times."""
        now = datetime.now(timezone.utc)
        events = [
            {"title": "Has Time", "start_time": now},
            {"title": "No Time"},
            {"title": "String Time", "start_time": "invalid"},
        ]
        
        result = sort_events_by_start_time(events)
        
        # Events without valid start_time should sort to beginning
        assert result[0]["title"] in ["No Time", "String Time"]
        assert result[2]["title"] == "Has Time"


@pytest.mark.unit
class TestFilterData:
    """Test filter data creation and validation."""
    
    def test_create_filter_data_user_filter(self):
        """Test creating user filter data."""
        result = create_filter_data(
            name="My Filter",
            calendar_id=1,
            user_id=123,
            subscribed_event_ids=[1, 2, 3]
        )

        assert result["name"] == "My Filter"
        assert result["calendar_id"] == 1
        assert result["domain_key"] is None
        assert result["user_id"] == 123
        assert result["subscribed_event_ids"] == [1, 2, 3]
        assert result["subscribed_group_ids"] == []
        assert isinstance(result["link_uuid"], str)
        assert len(result["link_uuid"]) > 10  # Should be a UUID
        assert isinstance(result["created_at"], datetime)
    
    def test_create_filter_data_domain_filter(self):
        """Test creating domain filter data."""
        result = create_filter_data(
            name="Domain Filter",
            domain_key="test_domain",
            subscribed_group_ids=[10, 20]
        )
        
        assert result["domain_key"] == "test_domain"
        assert result["calendar_id"] is None
        assert result["subscribed_group_ids"] == [10, 20]
    
    def test_validate_filter_data_valid_user_filter(self):
        """Test validating valid user filter data."""
        is_valid, error = validate_filter_data(
            name="Test Filter",
            calendar_id=1,
            subscribed_event_ids=[1, 2]
        )
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_filter_data_valid_domain_filter(self):
        """Test validating valid domain filter data."""
        is_valid, error = validate_filter_data(
            name="Domain Filter",
            domain_key="test_domain",
            subscribed_group_ids=[1, 2]
        )
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_filter_data_empty_name(self):
        """Test validating filter with empty name."""
        is_valid, error = validate_filter_data(
            name="",
            calendar_id=1
        )
        
        assert is_valid is False
        assert "name is required" in error
    
    def test_validate_filter_data_both_calendar_and_domain(self):
        """Test validating filter with both calendar_id and domain_key."""
        is_valid, error = validate_filter_data(
            name="Invalid Filter",
            calendar_id=1,
            domain_key="test_domain"
        )
        
        assert is_valid is False
        assert "cannot be both user and domain filter" in error
    
    def test_validate_filter_data_neither_calendar_nor_domain(self):
        """Test validating filter with neither calendar_id nor domain_key."""
        is_valid, error = validate_filter_data(
            name="Invalid Filter"
        )
        
        assert is_valid is False
        assert "must specify either calendar_id or domain_key" in error


@pytest.mark.unit
class TestCalendarValidation:
    """Test calendar validation functions."""
    
    def test_validate_calendar_data_valid(self):
        """Test validating valid calendar data."""
        is_valid, error = validate_calendar_data(
            name="Test Calendar",
            source_url="https://example.com/cal.ics"
        )
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_calendar_data_empty_name(self):
        """Test validating calendar with empty name."""
        is_valid, error = validate_calendar_data(
            name="",
            source_url="https://example.com/cal.ics"
        )
        
        assert is_valid is False
        assert "name is required" in error
    
    def test_validate_calendar_data_invalid_url(self):
        """Test validating calendar with invalid URL."""
        is_valid, error = validate_calendar_data(
            name="Test Calendar",
            source_url="not-a-url"
        )
        
        assert is_valid is False
        assert "valid HTTP/HTTPS URL" in error
    
    def test_validate_calendar_data_invalid_type(self):
        """Test validating calendar with invalid type."""
        is_valid, error = validate_calendar_data(
            name="Test Calendar",
            source_url="https://example.com/cal.ics",
            calendar_type="invalid"
        )
        
        assert is_valid is False
        assert "must be 'user' or 'domain'" in error


@pytest.mark.unit
class TestEventExport:
    """Test event export functions."""
    
    def test_transform_events_for_export_basic(self):
        """Test basic event export transformation."""
        events = [
            {
                "id": 1,
                "title": "Test Event",
                "start_time": datetime(2025, 9, 23, 10, 0, tzinfo=timezone.utc),
                "end_time": datetime(2025, 9, 23, 11, 0, tzinfo=timezone.utc),
                "uid": "test-uid-123",
                "description": "Test description",
                "location": "Test location",
                "other_ical_fields": {"raw_ical": ""}
            }
        ]
        
        result = transform_events_for_export(events, "Test Filter")
        
        assert "BEGIN:VCALENDAR" in result
        assert "END:VCALENDAR" in result
        assert "Test Filter" in result
        assert "BEGIN:VEVENT" in result
        assert "END:VEVENT" in result
        assert "SUMMARY:Test Event" in result
        assert "UID:test-uid-123" in result
    
    def test_apply_filter_to_events(self):
        """Test applying filter to events."""
        events = [
            {"id": 1, "title": "Event 1"},
            {"id": 2, "title": "Event 2"},
            {"id": 3, "title": "Event 3"}
        ]
        
        filter_data = {"subscribed_event_ids": ["Event 1", "Event 3"]}
        
        result = apply_filter_to_events(events, filter_data)
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 3
    
    def test_apply_filter_to_events_empty_filter(self):
        """Test applying empty filter to events."""
        events = [{"id": 1, "title": "Event 1"}]
        filter_data = {"subscribed_event_ids": []}

        result = apply_filter_to_events(events, filter_data)

        assert len(result) == 0

    def test_transform_events_with_dtstart_dtend(self):
        """Test that exported events always have DTSTART and DTEND fields."""
        events = [
            {
                "id": 1,
                "title": "Test Event",
                "start_time": datetime(2025, 9, 30, 18, 0, tzinfo=timezone.utc),
                "end_time": datetime(2025, 9, 30, 19, 0, tzinfo=timezone.utc),
                "uid": "test-uid-123",
                "description": "Test description",
                "location": "Test location",
                "other_ical_fields": {"raw_ical": ""}
            }
        ]

        result = transform_events_for_export(events, "Test Filter")

        # Verify proper iCal structure
        assert "BEGIN:VCALENDAR" in result
        assert "END:VCALENDAR" in result
        assert "BEGIN:VEVENT" in result
        assert "END:VEVENT" in result

        # CRITICAL: Verify DTSTART and DTEND are present
        assert "DTSTART:" in result
        assert "DTEND:" in result
        assert "SUMMARY:Test Event" in result
        assert "UID:test-uid-123" in result

    def test_transform_events_malformed_raw_ical(self):
        """Test that malformed raw_ical without DTSTART gets regenerated."""
        events = [
            {
                "id": 1,
                "title": "Malformed Event",
                "start_time": datetime(2025, 9, 30, 18, 0, tzinfo=timezone.utc),
                "end_time": datetime(2025, 9, 30, 19, 0, tzinfo=timezone.utc),
                "uid": "malformed-uid",
                "description": "Local time: tir 30 september 18:00 - 19:00",
                "location": "Meyenfeld",
                # Malformed raw_ical - missing DTSTART/DTEND
                "other_ical_fields": {
                    "raw_ical": """BEGIN:VEVENT
SUMMARY:Malformed Event
DESCRIPTION:Local time: tir 30 september 18:00 - 19:00
END:VEVENT"""
                }
            }
        ]

        result = transform_events_for_export(events, "Test Filter")

        # Should regenerate with proper DTSTART/DTEND from parsed data
        assert "DTSTART:20250930T180000Z" in result
        assert "DTEND:20250930T190000Z" in result
        assert "SUMMARY:Malformed Event" in result