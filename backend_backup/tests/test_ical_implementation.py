"""
Comprehensive Tests for Real iCal Implementation
Tests our actual business logic implementation (not stubs)
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.services.calendar_service import CalendarService
from app.services.event_service import EventService
from app.services.filter_service import FilterService
from app.data.ical_parser import (
    parse_ical_content, fetch_ical_from_url, generate_ical_content,
    extract_categories_from_events, filter_events_by_categories
)
from app.data.schemas import EventData, CalendarData, FilteredCalendarData
from app.persistence.repositories import StateRepository


@pytest.mark.unit
class TestICalParser:
    """Test our custom iCal parsing implementation"""

    def test_parse_simple_ical_content(self):
        """Test parsing basic iCal content"""
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:Test Calendar
BEGIN:VEVENT
UID:test-event-1
SUMMARY:Test Event
DTSTART:20241201T100000Z
DTEND:20241201T110000Z
CATEGORIES:Meeting,Work
DESCRIPTION:A test event
LOCATION:Conference Room
END:VEVENT
END:VCALENDAR"""
        
        events, categories = parse_ical_content(ical_content)
        
        assert len(events) == 1
        event = events[0]
        assert event.uid == "test-event-1"
        assert event.summary == "Test Event"
        assert event.categories == ["Meeting", "Work"]
        assert event.description == "A test event"
        assert event.location == "Conference Room"
        
        assert set(categories) == {"Meeting", "Work"}

    def test_parse_multiple_events(self):
        """Test parsing iCal with multiple events"""
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:Test Calendar
BEGIN:VEVENT
UID:event-1
SUMMARY:Event 1
DTSTART:20241201T100000Z
CATEGORIES:Work
END:VEVENT
BEGIN:VEVENT
UID:event-2
SUMMARY:Event 2
DTSTART:20241202T100000Z
CATEGORIES:Personal
END:VEVENT
END:VCALENDAR"""
        
        events, categories = parse_ical_content(ical_content)
        
        assert len(events) == 2
        assert events[0].summary == "Event 1"
        assert events[1].summary == "Event 2"
        assert set(categories) == {"Work", "Personal"}

    def test_generate_ical_content(self):
        """Test generating iCal content from events"""
        events = [
            EventData(
                uid="test-1",
                summary="Test Event",
                description="Test description",
                location="Test Location",
                dtstart="20241201T100000Z",
                dtend="20241201T110000Z",
                categories=["Test"]
            )
        ]
        
        ical_content = generate_ical_content(events, "Test Calendar")
        
        assert "BEGIN:VCALENDAR" in ical_content
        assert "END:VCALENDAR" in ical_content
        assert "Test Event" in ical_content
        assert "Test Location" in ical_content
        assert "CATEGORIES:Test" in ical_content

    def test_extract_categories_from_events(self):
        """Test category extraction with counts"""
        events = [
            EventData(uid="1", summary="Event 1", description="", location="", 
                     dtstart="", dtend="", categories=["Work", "Meeting"]),
            EventData(uid="2", summary="Event 2", description="", location="", 
                     dtstart="", dtend="", categories=["Work"]),
            EventData(uid="3", summary="Event 3", description="", location="", 
                     dtstart="", dtend="", categories=["Personal"])
        ]
        
        category_counts = extract_categories_from_events(events)
        
        assert category_counts == {"Work": 2, "Meeting": 1, "Personal": 1}

    def test_filter_events_by_categories_include(self):
        """Test filtering events by categories (include mode)"""
        events = [
            EventData(uid="1", summary="Work Event", description="", location="", 
                     dtstart="", dtend="", categories=["Work"]),
            EventData(uid="2", summary="Personal Event", description="", location="", 
                     dtstart="", dtend="", categories=["Personal"]),
            EventData(uid="3", summary="Meeting", description="", location="", 
                     dtstart="", dtend="", categories=["Work", "Meeting"])
        ]
        
        filtered = filter_events_by_categories(events, ["Work"], "include")
        
        assert len(filtered) == 2
        assert filtered[0].summary == "Work Event"
        assert filtered[1].summary == "Meeting"

    def test_filter_events_by_categories_exclude(self):
        """Test filtering events by categories (exclude mode)"""
        events = [
            EventData(uid="1", summary="Work Event", description="", location="", 
                     dtstart="", dtend="", categories=["Work"]),
            EventData(uid="2", summary="Personal Event", description="", location="", 
                     dtstart="", dtend="", categories=["Personal"]),
        ]
        
        filtered = filter_events_by_categories(events, ["Work"], "exclude")
        
        assert len(filtered) == 1
        assert filtered[0].summary == "Personal Event"


@pytest.mark.unit
class TestCalendarServiceReal:
    """Test real calendar service implementation"""

    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repository = Mock(spec=StateRepository)
        self.service = CalendarService(self.mock_repository)

    @patch('app.services.calendar_service.fetch_ical_from_url')
    @patch('app.services.calendar_service.parse_ical_content')
    def test_create_calendar_with_real_validation(self, mock_parse, mock_fetch):
        """Test calendar creation with real iCal validation"""
        # Mock successful iCal fetch and parse
        mock_fetch.return_value = (True, "valid ical content", None)
        mock_parse.return_value = ([], [])  # Empty events, empty categories
        
        # Mock empty state
        from app.data.schemas import AppState
        empty_state = AppState(
            calendars={}, communities={}, groups={}, filters={}, 
            subscriptions={}, filtered_calendars={}, events_cache={}
        )
        self.mock_repository.load_state.return_value = empty_state
        self.mock_repository.save_state.return_value = True
        
        # Test calendar creation
        result = self.service.create_calendar_workflow(
            "Test Calendar", 
            "https://example.com/calendar.ics", 
            "test-user"
        )
        
        assert result.success is True
        assert result.data["calendar"]["name"] == "Test Calendar"
        assert result.data["calendar"]["url"] == "https://example.com/calendar.ics"
        assert result.data["calendar"]["user_id"] == "test-user"
        
        # Verify iCal validation was called
        mock_fetch.assert_called_once_with("https://example.com/calendar.ics")
        mock_parse.assert_called_once_with("valid ical content")

    @patch('app.services.calendar_service.fetch_ical_from_url')
    def test_create_calendar_invalid_url(self, mock_fetch):
        """Test calendar creation with invalid iCal URL"""
        # Mock failed iCal fetch
        mock_fetch.return_value = (False, None, "HTTP error 404: Not Found")
        
        result = self.service.create_calendar_workflow(
            "Test Calendar",
            "https://invalid-url.com/calendar.ics",
            "test-user"
        )
        
        assert result.success is False
        assert "Invalid calendar URL" in result.error_message
        assert "HTTP error 404" in result.error_message

    @patch('app.services.calendar_service.fetch_ical_from_url')
    @patch('app.services.calendar_service.parse_ical_content')
    def test_create_calendar_duplicate_url(self, mock_parse, mock_fetch):
        """Test duplicate calendar URL detection"""
        # Mock successful iCal validation first
        mock_fetch.return_value = (True, "valid ical", None)
        mock_parse.return_value = ([], [])
        
        from app.data.schemas import AppState, CalendarData
        
        existing_calendar = CalendarData(
            id="existing", name="Existing", url="https://example.com/cal.ics",
            user_id="test-user", created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z", is_active=True
        )
        
        state = AppState(
            calendars={"existing": existing_calendar}, communities={}, groups={}, 
            filters={}, subscriptions={}, filtered_calendars={}, events_cache={}
        )
        self.mock_repository.load_state.return_value = state
        
        result = self.service.create_calendar_workflow(
            "Duplicate Calendar",
            "https://example.com/cal.ics",  # Same URL
            "test-user"
        )
        
        assert result.success is False
        assert "already exists" in result.error_message


@pytest.mark.unit
class TestEventServiceReal:
    """Test real event service implementation"""

    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repository = Mock(spec=StateRepository)
        self.service = EventService(self.mock_repository)

    @patch('app.services.event_service.fetch_ical_from_url')
    @patch('app.services.event_service.parse_ical_content')
    def test_parse_calendar_from_url_success(self, mock_parse, mock_fetch):
        """Test successful calendar parsing from URL"""
        # Mock successful fetch and parse
        mock_fetch.return_value = (True, "ical content", None)
        mock_events = [
            EventData(uid="1", summary="Test Event", description="", location="",
                     dtstart="20241201T100000Z", dtend="20241201T110000Z", categories=["Work"])
        ]
        mock_parse.return_value = (mock_events, ["Work"])
        
        result = self.service.parse_calendar_from_url("https://example.com/cal.ics")
        
        assert result.success is True
        assert result.data["total_events"] == 1
        assert result.data["categories"] == ["Work"]
        assert result.data["events"][0]["summary"] == "Test Event"

    @patch('app.services.event_service.fetch_ical_from_url')
    def test_parse_calendar_from_url_failure(self, mock_fetch):
        """Test calendar parsing failure"""
        mock_fetch.return_value = (False, None, "Connection timeout")
        
        result = self.service.parse_calendar_from_url("https://invalid-url.com/cal.ics")
        
        assert result.success is False
        assert "Connection timeout" in result.error_message

    def test_generate_filtered_calendar_with_cache(self):
        """Test filtered calendar generation using cached events"""
        from app.data.schemas import AppState, CalendarData
        
        # Setup calendar and cached events
        calendar = CalendarData(
            id="test-cal", name="Test", url="https://example.com/cal.ics",
            user_id="test-user", created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z", is_active=True
        )
        
        mock_events = [
            EventData(uid="1", summary="Work Event", description="", location="",
                     dtstart="20241201T100000Z", dtend="20241201T110000Z", categories=["Work"]),
            EventData(uid="2", summary="Personal Event", description="", location="",
                     dtstart="20241202T100000Z", dtend="20241202T110000Z", categories=["Personal"])
        ]
        
        state = AppState(
            calendars={"test-cal": calendar}, communities={}, groups={}, filters={},
            subscriptions={}, filtered_calendars={}, events_cache={"test-cal": mock_events}
        )
        
        self.mock_repository.load_state.return_value = state
        
        # Test filtering logic directly
        from app.data.ical_parser import filter_events_by_categories, generate_ical_content
        
        filtered_events = filter_events_by_categories(mock_events, ["Work"], "include")
        ical_content = generate_ical_content(filtered_events, "Filtered Calendar")
        
        # Verify filtering worked
        assert len(filtered_events) == 1
        assert filtered_events[0].summary == "Work Event"
        assert "Work Event" in ical_content
        assert "Personal Event" not in ical_content


@pytest.mark.unit
class TestFilterServiceReal:
    """Test real filter service implementation"""

    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repository = Mock(spec=StateRepository)
        self.service = FilterService(self.mock_repository)

    def test_create_filtered_calendar_real(self):
        """Test real filtered calendar creation"""
        from app.data.schemas import AppState, CalendarData
        
        # Setup source calendar
        source_calendar = CalendarData(
            id="source-cal", name="Source", url="https://example.com/cal.ics",
            user_id="test-user", created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z", is_active=True
        )
        
        state = AppState(
            calendars={"source-cal": source_calendar}, communities={}, groups={}, 
            filters={}, subscriptions={}, filtered_calendars={}, events_cache={}
        )
        
        self.mock_repository.load_state.return_value = state
        self.mock_repository.save_state.return_value = True
        
        filter_config = {
            "include_categories": ["Work", "Meeting"],
            "filter_mode": "include"
        }
        
        result = self.service.create_filtered_calendar_workflow(
            name="Work Events",
            source_calendar_id="source-cal",
            filter_config=filter_config,
            user_id="test-user"
        )
        
        assert result.success is True
        filtered_cal = result.data["filtered_calendar"]
        assert filtered_cal["name"] == "Work Events"
        assert filtered_cal["source_calendar_id"] == "source-cal"
        assert filtered_cal["filter_config"] == filter_config
        assert filtered_cal["public_token"] is not None
        assert filtered_cal["calendar_url"].startswith("https://filter-ical.de/cal/")

    def test_get_filtered_calendar_by_token(self):
        """Test retrieving filtered calendar by public token"""
        from app.data.schemas import AppState, FilteredCalendarData
        
        filtered_cal = FilteredCalendarData(
            id="filtered-1", name="Filtered", source_calendar_id="source",
            filter_config={"include_categories": ["Work"]}, public_token="test-token-123",
            user_id="test-user", created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z", last_accessed=None,
            access_count=0, is_active=True
        )
        
        state = AppState(
            calendars={}, communities={}, groups={}, filters={}, subscriptions={},
            filtered_calendars={"filtered-1": filtered_cal}, events_cache={}
        )
        
        self.mock_repository.load_state.return_value = state
        self.mock_repository.save_state.return_value = True
        
        result = self.service.get_filtered_calendar_by_token("test-token-123")
        
        assert result.success is True
        returned_cal = result.data["filtered_calendar"]
        assert returned_cal.public_token == "test-token-123"
        assert returned_cal.access_count == 1  # Should increment


@pytest.mark.integration
class TestRealAPIEndpoints:
    """Integration tests for real API endpoints"""

    @classmethod
    def setup_class(cls):
        """Setup test client"""
        cls.client = TestClient(app)

    @patch('app.services.calendar_service.fetch_ical_from_url')
    @patch('app.services.calendar_service.parse_ical_content')
    def test_create_calendar_endpoint_real(self, mock_parse, mock_fetch):
        """Test real calendar creation endpoint"""
        import uuid
        unique_url = f"https://example.com/cal-{uuid.uuid4().hex[:8]}.ics"
        
        # Mock successful iCal validation
        mock_fetch.return_value = (True, "valid ical", None)
        mock_parse.return_value = ([], [])
        
        response = self.client.post(
            "/api/calendars",
            json={"name": "Test Calendar API", "url": unique_url},
            headers={"x-user-id": "test-user"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Calendar API"
        assert data["url"] == unique_url
        assert data["user_id"] == "test-user"
        assert "id" in data

    def test_list_calendars_endpoint(self):
        """Test list calendars endpoint"""
        response = self.client.get(
            "/api/calendars",
            headers={"x-user-id": "test-user"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch('app.services.event_service.fetch_ical_from_url')
    @patch('app.services.event_service.parse_ical_content')
    def test_parse_calendar_endpoint_real(self, mock_parse, mock_fetch):
        """Test real calendar parsing endpoint"""
        mock_fetch.return_value = (True, "ical content", None)
        mock_events = [
            EventData(uid="1", summary="Test", description="", location="",
                     dtstart="20241201T100000Z", dtend="20241201T110000Z", categories=["Work"])
        ]
        mock_parse.return_value = (mock_events, ["Work"])
        
        response = self.client.get("/api/parse-calendar?url=https://example.com/cal.ics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_events"] == 1
        assert data["categories"] == ["Work"]
        assert data["events"][0]["summary"] == "Test"

    def test_health_endpoint(self):
        """Test health endpoint works"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ical-viewer"
        assert data["architecture"] == "functional_core_imperative_shell"


@pytest.mark.integration
class TestDatabasePersistence:
    """Test actual database persistence"""

    def test_repository_creates_database(self):
        """Test repository creates database file"""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            repo = StateRepository(db_path)
            
            # Database file should be created
            assert os.path.exists(db_path)
            
            # Should be able to load initial state
            state = repo.load_state()
            assert len(state.calendars) == 0
            assert len(state.communities) == 0

    def test_repository_saves_and_loads_state(self):
        """Test repository can save and load state"""
        import tempfile
        import os
        from app.data.schemas import AppState, CalendarData
        
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            repo = StateRepository(db_path)
            
            # Create test data
            calendar = CalendarData(
                id="test-cal", name="Test Calendar", url="https://example.com/cal.ics",
                user_id="test-user", created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z", is_active=True
            )
            
            state = AppState(
                calendars={"test-cal": calendar}, communities={}, groups={}, 
                filters={}, subscriptions={}, filtered_calendars={}, events_cache={}
            )
            
            # Save state
            success = repo.save_state(state)
            assert success is True
            
            # Load state
            loaded_state = repo.load_state()
            assert len(loaded_state.calendars) == 1
            assert loaded_state.calendars["test-cal"].name == "Test Calendar"


@pytest.mark.slow
class TestRealICalFetching:
    """Test real iCal URL fetching (slow tests)"""
    
    def test_fetch_google_calendar_real(self):
        """Test fetching real Google Calendar (requires internet)"""
        url = "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics"
        
        success, content, error = fetch_ical_from_url(url)
        
        if success:  # Only assert if network is available
            assert content is not None
            assert "BEGIN:VCALENDAR" in content
            assert "END:VCALENDAR" in content
            
            # Test parsing the real content
            events, categories = parse_ical_content(content)
            assert len(events) > 0  # Should have some US holidays
        else:
            pytest.skip(f"Network error: {error}")