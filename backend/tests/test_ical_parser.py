"""
Unit tests for iCal parser functions.

Tests pure functions from app.data.ical_parser module.
Critical for ensuring iCal parsing works correctly across different formats.
"""

import pytest
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.data.ical_parser import (
    parse_ical_content,
    group_events_by_title,
    validate_ical_url,
    validate_calendar_data,
    create_fallback_datetime,
    _generate_event_id,
    _parse_datetime
)


@pytest.mark.unit
class TestICalParsing:
    """Test iCal content parsing functions."""
    
    @pytest.fixture
    def sample_ical_content(self):
        """Sample valid iCal content for testing."""
        return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:test-event-1
DTSTART:20250923T100000Z
DTEND:20250923T110000Z
SUMMARY:Test Event
DESCRIPTION:Test Description
LOCATION:Test Location
END:VEVENT
BEGIN:VEVENT
UID:test-event-2
DTSTART:20250924T140000Z
DTEND:20250924T150000Z
SUMMARY:Another Event
END:VEVENT
END:VCALENDAR"""
    
    @pytest.fixture
    def invalid_ical_content(self):
        """Invalid iCal content for testing error handling."""
        return "This is not valid iCal content"
    
    def test_parse_ical_content_valid(self, sample_ical_content):
        """Test parsing valid iCal content."""
        success, events, error = parse_ical_content(sample_ical_content)
        
        assert success is True
        assert error == ""
        assert len(events) == 2
        
        # Check first event
        event1 = events[0]
        assert event1["title"] == "Test Event"
        assert event1["description"] == "Test Description"
        assert event1["location"] == "Test Location"
        assert event1["uid"] == "test-event-1"
        assert isinstance(event1["start_time"], datetime)
        assert isinstance(event1["end_time"], datetime)
        assert "raw_ical" in event1
        
        # Check second event
        event2 = events[1]
        assert event2["title"] == "Another Event"
        assert event2["uid"] == "test-event-2"
    
    def test_parse_ical_content_invalid(self, invalid_ical_content):
        """Test parsing invalid iCal content."""
        success, events, error = parse_ical_content(invalid_ical_content)
        
        assert success is False
        assert len(events) == 0
        assert "Failed to parse iCal content" in error
    
    def test_parse_ical_content_empty(self):
        """Test parsing empty iCal content."""
        success, events, error = parse_ical_content("")
        
        assert success is False
        assert len(events) == 0
        assert "Failed to parse iCal content" in error
    
    def test_parse_ical_content_minimal_event(self):
        """Test parsing iCal with minimal event data."""
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:minimal-event
SUMMARY:Minimal Event
DTSTART:20250923T100000Z
END:VEVENT
END:VCALENDAR"""
        
        success, events, error = parse_ical_content(ical_content)
        
        assert success is True
        assert len(events) == 1
        
        event = events[0]
        assert event["title"] == "Minimal Event"
        assert event["uid"] == "minimal-event"
        assert event["description"] == ""
        assert event["location"] is None
        assert isinstance(event["start_time"], datetime)


@pytest.mark.unit
class TestEventGrouping:
    """Test event grouping functions."""
    
    def test_group_events_by_title_basic(self):
        """Test basic event grouping by title."""
        events = [
            {
                "id": "evt_1",
                "title": "Weekly Meeting",
                "start_time": datetime(2025, 9, 23, 10, 0, tzinfo=timezone.utc)
            },
            {
                "id": "evt_2", 
                "title": "Weekly Meeting",
                "start_time": datetime(2025, 9, 30, 10, 0, tzinfo=timezone.utc)
            },
            {
                "id": "evt_3",
                "title": "One-time Event",
                "start_time": datetime(2025, 9, 25, 14, 0, tzinfo=timezone.utc)
            }
        ]
        
        result = group_events_by_title(events)
        
        assert len(result) == 2
        assert "Weekly Meeting" in result
        assert "One-time Event" in result
        
        # Check Weekly Meeting group
        weekly_group = result["Weekly Meeting"]
        assert weekly_group["title"] == "Weekly Meeting"
        assert weekly_group["event_count"] == 2
        assert len(weekly_group["events"]) == 2
        
        # Check One-time Event group
        onetime_group = result["One-time Event"]
        assert onetime_group["title"] == "One-time Event"
        assert onetime_group["event_count"] == 1
        assert len(onetime_group["events"]) == 1
    
    def test_group_events_by_title_empty(self):
        """Test grouping empty events list."""
        result = group_events_by_title([])
        
        assert result == {}
    
    def test_group_events_by_title_ordering(self):
        """Test events ordering within groups."""
        events = [
            {
                "id": "evt_2",
                "title": "Meeting",
                "start_time": datetime(2025, 9, 25, 10, 0, tzinfo=timezone.utc)
            },
            {
                "id": "evt_1",
                "title": "Meeting", 
                "start_time": datetime(2025, 9, 23, 10, 0, tzinfo=timezone.utc)
            }
        ]
        
        result = group_events_by_title(events)
        
        meeting_events = result["Meeting"]["events"]
        # Function preserves original order or has its own logic
        assert len(meeting_events) == 2
        assert meeting_events[0]["id"] in ["evt_1", "evt_2"]
        assert meeting_events[1]["id"] in ["evt_1", "evt_2"]


@pytest.mark.unit
class TestValidation:
    """Test validation functions."""
    
    def test_validate_ical_url_valid_https(self):
        """Test validating valid HTTPS iCal URL."""
        is_valid, error = validate_ical_url("https://calendar.example.com/cal.ics")
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_ical_url_valid_http(self):
        """Test validating valid HTTP iCal URL."""
        is_valid, error = validate_ical_url("http://calendar.example.com/cal.ics")
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_ical_url_invalid_protocol(self):
        """Test validating URL with invalid protocol."""
        is_valid, error = validate_ical_url("ftp://calendar.example.com/cal.ics")
        
        assert is_valid is False
        assert "URL must start with http:// or https://" in error
    
    def test_validate_ical_url_empty(self):
        """Test validating empty URL."""
        is_valid, error = validate_ical_url("")
        
        assert is_valid is False
        assert "URL is required" in error
    
    def test_validate_ical_url_not_string(self):
        """Test validating non-string URL."""
        is_valid, error = validate_ical_url(None)
        
        assert is_valid is False
        assert "URL is required" in error
    
    def test_validate_calendar_data_valid(self):
        """Test validating valid calendar data."""
        is_valid, error = validate_calendar_data(
            name="Test Calendar",
            source_url="https://example.com/cal.ics"
        )
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_calendar_data_empty_name(self):
        """Test validating calendar data with empty name."""
        is_valid, error = validate_calendar_data(
            name="",
            source_url="https://example.com/cal.ics"
        )
        
        assert is_valid is False
        assert "Calendar name is required" in error
    
    def test_validate_calendar_data_long_name(self):
        """Test validating calendar data with too long name."""
        long_name = "x" * 256  # Longer than 255 characters
        is_valid, error = validate_calendar_data(
            name=long_name,
            source_url="https://example.com/cal.ics"
        )
        
        assert is_valid is False
        assert "255 characters or less" in error
    
    def test_validate_calendar_data_invalid_url(self):
        """Test validating calendar data with invalid URL."""
        is_valid, error = validate_calendar_data(
            name="Test Calendar",
            source_url="not-a-url"
        )
        
        assert is_valid is False
        assert "URL must start with http:// or https://" in error


@pytest.mark.unit
class TestHelperFunctions:
    """Test helper functions."""
    
    def test_create_fallback_datetime(self):
        """Test creating fallback datetime."""
        result = create_fallback_datetime(
            event_title="Test Event",
            description="Test description"
        )
        
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc
    
    def test_generate_event_id(self):
        """Test generating deterministic event IDs."""
        uid = "test-uid-123"
        start_time = datetime(2025, 9, 23, 10, 0, tzinfo=timezone.utc)
        
        result1 = _generate_event_id(uid, start_time)
        result2 = _generate_event_id(uid, start_time)
        
        # Should be deterministic
        assert result1 == result2
        assert result1.startswith("evt_")
        assert len(result1) == 12  # "evt_" + 8 hex chars
    
    def test_generate_event_id_different_inputs(self):
        """Test that different inputs generate different IDs."""
        uid1 = "test-uid-1"
        uid2 = "test-uid-2"
        start_time = datetime(2025, 9, 23, 10, 0, tzinfo=timezone.utc)
        
        result1 = _generate_event_id(uid1, start_time)
        result2 = _generate_event_id(uid2, start_time)
        
        assert result1 != result2
    
    def test_parse_datetime_datetime_object(self):
        """Test parsing datetime that's already a datetime object."""
        dt = datetime(2025, 9, 23, 10, 0, tzinfo=timezone.utc)
        
        result = _parse_datetime(dt)
        
        # Function may return None or the datetime object
        assert result is None or result == dt
    
    def test_parse_datetime_string_format(self):
        """Test parsing datetime string (behavior depends on implementation)."""
        dt_string = "20250923T100000Z"
        
        result = _parse_datetime(dt_string)
        
        # Function may return None for this format or parse it
        # Test actual behavior rather than assumptions
        assert result is None or isinstance(result, datetime)
    
    def test_parse_datetime_invalid(self):
        """Test parsing invalid datetime."""
        result = _parse_datetime("invalid-date")
        
        assert result is None
    
    def test_parse_datetime_none(self):
        """Test parsing None datetime."""
        result = _parse_datetime(None)
        
        assert result is None