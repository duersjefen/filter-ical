"""
Comprehensive tests for calendar processing functionality.
Tests ICS parsing, filtering, and event processing.
"""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
import tempfile
import os

client = TestClient(app)

@pytest.fixture
def sample_ics_content():
    """Sample ICS calendar content for testing."""
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:test-event-1@example.com
DTSTART:20250915T100000Z
DTEND:20250915T110000Z
SUMMARY:Test Meeting
DESCRIPTION:A test meeting for calendar processing
LOCATION:Conference Room A
END:VEVENT
BEGIN:VEVENT
UID:test-event-2@example.com
DTSTART:20250916T140000Z
DTEND:20250916T150000Z
SUMMARY:Important Workshop
DESCRIPTION:Workshop about important topics
LOCATION:Virtual
END:VEVENT
BEGIN:VEVENT
UID:test-event-3@example.com
DTSTART:20250917T090000Z
DTEND:20250917T120000Z
SUMMARY:Optional Training
DESCRIPTION:Optional training session
LOCATION:Training Room B
END:VEVENT
END:VCALENDAR"""

@pytest.fixture
def sample_ics_file(sample_ics_content):
    """Create a temporary ICS file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ics', delete=False) as f:
        f.write(sample_ics_content)
        f.flush()
        yield f.name
    os.unlink(f.name)

class TestCalendarParsing:
    """Test calendar parsing functionality."""
    
    def test_parse_valid_ics_content(self, sample_ics_content):
        """Test parsing valid ICS content."""
        response = client.post("/api/calendars", 
                             data={"ics_content": sample_ics_content})
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert len(data["events"]) == 3
        
    def test_parse_invalid_ics_content(self):
        """Test parsing invalid ICS content returns appropriate error."""
        invalid_ics = "This is not valid ICS content"
        response = client.post("/api/calendars", 
                             data={"ics_content": invalid_ics})
        assert response.status_code == 400
        
    def test_parse_empty_ics_content(self):
        """Test parsing empty ICS content."""
        response = client.post("/api/calendars", 
                             data={"ics_content": ""})
        assert response.status_code == 400

class TestEventFiltering:
    """Test event filtering functionality."""
    
    def test_filter_events_by_title(self, sample_ics_content):
        """Test filtering events by title keyword."""
        response = client.post("/api/calendars", 
                             data={
                                 "ics_content": sample_ics_content,
                                 "title_filter": "Meeting"
                             })
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 1
        assert "Test Meeting" in data["events"][0]["summary"]
        
    def test_filter_events_by_description(self, sample_ics_content):
        """Test filtering events by description keyword."""
        response = client.post("/api/calendars", 
                             data={
                                 "ics_content": sample_ics_content,
                                 "description_filter": "important"
                             })
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 1
        assert "Important Workshop" in data["events"][0]["summary"]
        
    def test_filter_events_by_location(self, sample_ics_content):
        """Test filtering events by location."""
        response = client.post("/api/calendars", 
                             data={
                                 "ics_content": sample_ics_content,
                                 "location_filter": "Virtual"
                             })
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 1
        assert data["events"][0]["location"] == "Virtual"
        
    def test_filter_events_exclude_optional(self, sample_ics_content):
        """Test excluding events with 'optional' keyword."""
        response = client.post("/api/calendars", 
                             data={
                                 "ics_content": sample_ics_content,
                                 "exclude_keywords": "Optional"
                             })
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 2
        for event in data["events"]:
            assert "Optional" not in event["summary"]
        
    def test_multiple_filters_combined(self, sample_ics_content):
        """Test combining multiple filters."""
        response = client.post("/api/calendars", 
                             data={
                                 "ics_content": sample_ics_content,
                                 "location_filter": "Room",
                                 "exclude_keywords": "Optional"
                             })
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 1
        assert "Conference Room A" in data["events"][0]["location"]

class TestEventProcessing:
    """Test event processing and data extraction."""
    
    def test_event_data_structure(self, sample_ics_content):
        """Test that processed events have correct data structure."""
        response = client.post("/api/calendars", 
                             data={"ics_content": sample_ics_content})
        assert response.status_code == 200
        data = response.json()
        
        event = data["events"][0]
        required_fields = ["summary", "description", "location", "start", "end"]
        for field in required_fields:
            assert field in event, f"Missing required field: {field}"
            
    def test_event_datetime_format(self, sample_ics_content):
        """Test that event datetimes are properly formatted."""
        response = client.post("/api/calendars", 
                             data={"ics_content": sample_ics_content})
        assert response.status_code == 200
        data = response.json()
        
        event = data["events"][0]
        # Should be able to parse as ISO format datetime
        start_time = datetime.fromisoformat(event["start"].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(event["end"].replace('Z', '+00:00'))
        assert start_time < end_time
        
    def test_recurring_events(self):
        """Test processing recurring events."""
        recurring_ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:recurring-event@example.com
DTSTART:20250915T100000Z
DTEND:20250915T110000Z
SUMMARY:Weekly Meeting
RRULE:FREQ=WEEKLY;COUNT=4
DESCRIPTION:Recurring weekly meeting
END:VEVENT
END:VCALENDAR"""
        
        response = client.post("/api/calendars", 
                             data={"ics_content": recurring_ics})
        assert response.status_code == 200
        data = response.json()
        # Should expand recurring events
        assert len(data["events"]) == 4

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_malformed_dates(self):
        """Test handling of malformed date formats."""
        malformed_ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:bad-date@example.com
DTSTART:invalid-date
DTEND:also-invalid
SUMMARY:Bad Date Event
END:VEVENT
END:VCALENDAR"""
        
        response = client.post("/api/calendars", 
                             data={"ics_content": malformed_ics})
        assert response.status_code == 400
        
    def test_missing_required_fields(self):
        """Test handling events with missing required fields."""
        incomplete_ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:incomplete-event@example.com
SUMMARY:Event with no dates
END:VEVENT
END:VCALENDAR"""
        
        response = client.post("/api/calendars", 
                             data={"ics_content": incomplete_ics})
        # Should either handle gracefully or return specific error
        assert response.status_code in [200, 400]
        
    def test_large_calendar_performance(self):
        """Test performance with large calendar files."""
        # Generate ICS with many events
        large_ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Test//Test//EN\n"
        for i in range(100):
            large_ics += f"""BEGIN:VEVENT
UID:event-{i}@example.com
DTSTART:20250915T{10+i%14:02d}0000Z
DTEND:20250915T{11+i%14:02d}0000Z
SUMMARY:Event {i}
DESCRIPTION:Description for event {i}
END:VEVENT
"""
        large_ics += "END:VCALENDAR"
        
        response = client.post("/api/calendars", 
                             data={"ics_content": large_ics})
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 100

class TestIntegration:
    """Integration tests for full calendar workflow."""
    
    def test_complete_calendar_workflow(self, sample_ics_content):
        """Test complete workflow from upload to filtered results."""
        # First, upload and process calendar
        response = client.post("/api/calendars", 
                             data={"ics_content": sample_ics_content})
        assert response.status_code == 200
        
        # Then apply filters
        filtered_response = client.post("/api/calendars", 
                                      data={
                                          "ics_content": sample_ics_content,
                                          "title_filter": "Meeting",
                                          "exclude_keywords": "Optional"
                                      })
        assert filtered_response.status_code == 200
        data = filtered_response.json()
        assert len(data["events"]) == 1
        assert "Test Meeting" in data["events"][0]["summary"]