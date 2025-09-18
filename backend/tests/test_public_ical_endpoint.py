"""
Test public iCal endpoint (/cal/{token}) with cache-first implementation
End-to-end testing for real-time filtered calendar functionality
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Calendar, Event, FilteredCalendar, FilterMode
from app.core.filters import serialize_json_field
from app.main import app


class TestPublicICalEndpoint:
    """Test suite for public filtered calendar endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_valid_token_returns_ical_content(self, session: Session, sample_calendar_with_events):
        """Test that valid public token returns iCal content"""
        calendar = sample_calendar_with_events
        
        # Create a filtered calendar
        filtered_calendar = FilteredCalendar(
            name="Public Test Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            filter_mode=FilterMode.include,
            needs_regeneration=True,
            public_token="test_token_123"
        )
        session.add(filtered_calendar)
        session.commit()
        
        # Request iCal content via public endpoint
        response = self.client.get(f"/cal/{filtered_calendar.public_token}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/calendar; charset=utf-8"
        
        content = response.text
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content
        assert "VERSION:2.0" in content
        assert "PRODID:" in content
    
    def test_invalid_token_returns_404(self):
        """Test that invalid token returns 404"""
        response = self.client.get("/cal/invalid_token_xyz")
        
        assert response.status_code == 404
        assert "Public calendar not found" in response.json()["detail"]
    
    def test_cached_content_is_served_quickly(self, session: Session, sample_calendar_with_events):
        """Test that cached content is served without regeneration"""
        calendar = sample_calendar_with_events
        
        # Create filtered calendar with cached content
        cached_ical = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//iCal Viewer//Filter-iCal.de//EN
CALSCALE:GREGORIAN
X-WR-CALNAME:Cached Test Filter
BEGIN:VEVENT
DTSTART:20250920T100000Z
DTEND:20250920T110000Z
SUMMARY:Cached Event
UID:cached_event@filter-ical.de
DTSTAMP:20250918T120000Z
CATEGORIES:Work
END:VEVENT
END:VCALENDAR"""
        
        filtered_calendar = FilteredCalendar(
            name="Cached Test Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            filter_mode=FilterMode.include,
            needs_regeneration=False,  # Cache is valid
            cached_ical_content=cached_ical,
            cached_content_hash="test_hash",
            cache_updated_at=datetime.utcnow(),
            public_token="cached_token_456"
        )
        session.add(filtered_calendar)
        session.commit()
        
        # Request iCal content - should serve cached version
        response = self.client.get(f"/cal/{filtered_calendar.public_token}")
        
        assert response.status_code == 200
        assert response.text == cached_ical
        assert "Cached Event" in response.text
    
    def test_needs_regeneration_triggers_fresh_content(self, session: Session, sample_calendar_with_events):
        """Test that needs_regeneration=True generates fresh content"""
        calendar = sample_calendar_with_events
        
        # Add real events to the calendar
        work_event = Event(
            title="Fresh Work Event",
            start=datetime.utcnow() + timedelta(days=1),
            end=datetime.utcnow() + timedelta(days=1, hours=1),
            calendar_id=calendar.id,
            category="Work"
        )
        session.add(work_event)
        session.commit()
        
        # Create filtered calendar with stale cache but needs_regeneration=True
        stale_ical = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//iCal Viewer//Filter-iCal.de//EN
CALSCALE:GREGORIAN
X-WR-CALNAME:Stale Test Filter
BEGIN:VEVENT
DTSTART:20250920T100000Z
DTEND:20250920T110000Z
SUMMARY:Stale Event
UID:stale_event@filter-ical.de
DTSTAMP:20250918T120000Z
CATEGORIES:Work
END:VEVENT
END:VCALENDAR"""
        
        filtered_calendar = FilteredCalendar(
            name="Stale Test Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            filter_mode=FilterMode.include,
            needs_regeneration=True,  # Force regeneration
            cached_ical_content=stale_ical,
            cached_content_hash="stale_hash",
            cache_updated_at=datetime.utcnow() - timedelta(days=1),
            public_token="stale_token_789"
        )
        session.add(filtered_calendar)
        session.commit()
        
        # Request iCal content - should regenerate fresh content
        response = self.client.get(f"/cal/{filtered_calendar.public_token}")
        
        assert response.status_code == 200
        content = response.text
        
        # Should contain fresh event, not stale one
        assert "Fresh Work Event" in content
        assert "Stale Event" not in content
        
        # Should be valid iCal
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content
    
    def test_filtering_works_correctly_in_public_endpoint(self, session: Session, sample_calendar_with_events):
        """Test that event filtering works correctly in public endpoint"""
        calendar = sample_calendar_with_events
        
        # Add events of different types
        work_event = Event(
            title="Work Meeting",
            start=datetime.utcnow() + timedelta(days=1),
            end=datetime.utcnow() + timedelta(days=1, hours=1),
            calendar_id=calendar.id,
            category="Work"
        )
        personal_event = Event(
            title="Personal Appointment",
            start=datetime.utcnow() + timedelta(days=2),
            end=datetime.utcnow() + timedelta(days=2, hours=1),
            calendar_id=calendar.id,
            category="Personal"
        )
        meeting_event = Event(
            title="Team Meeting",
            start=datetime.utcnow() + timedelta(days=3),
            end=datetime.utcnow() + timedelta(days=3, hours=1),
            calendar_id=calendar.id,
            category="Meeting"
        )
        session.add_all([work_event, personal_event, meeting_event])
        session.commit()
        
        # Create filtered calendar that only includes Work and Meeting events
        filtered_calendar = FilteredCalendar(
            name="Work and Meetings Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work", "Meeting"]),
            exclude_events=serialize_json_field([]),
            filter_mode=FilterMode.include,
            needs_regeneration=True,
            public_token="filter_token_abc"
        )
        session.add(filtered_calendar)
        session.commit()
        
        # Request filtered iCal content
        response = self.client.get(f"/cal/{filtered_calendar.public_token}")
        
        assert response.status_code == 200
        content = response.text
        
        # Should include Work and Meeting events
        assert "Work Meeting" in content
        assert "Team Meeting" in content
        
        # Should NOT include Personal event
        assert "Personal Appointment" not in content
        
        # Should be valid iCal
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content
    
    def test_exclude_filter_mode_works_correctly(self, session: Session, sample_calendar_with_events):
        """Test that exclude filter mode works correctly in public endpoint"""
        calendar = sample_calendar_with_events
        
        # Add events of different types
        work_event = Event(
            title="Work Meeting",
            start=datetime.utcnow() + timedelta(days=1),
            end=datetime.utcnow() + timedelta(days=1, hours=1),
            calendar_id=calendar.id,
            category="Work"
        )
        personal_event = Event(
            title="Personal Appointment",
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
            needs_regeneration=True,
            public_token="exclude_token_def"
        )
        session.add(filtered_calendar)
        session.commit()
        
        # Request filtered iCal content
        response = self.client.get(f"/cal/{filtered_calendar.public_token}")
        
        assert response.status_code == 200
        content = response.text
        
        # Should include Personal event
        assert "Personal Appointment" in content
        
        # Should NOT include Work event
        assert "Work Meeting" not in content
        
        # Should be valid iCal
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content
    
    def test_content_disposition_header_for_file_download(self, session: Session, sample_calendar_with_events):
        """Test that Content-Disposition header is set correctly for file downloads"""
        calendar = sample_calendar_with_events
        
        filtered_calendar = FilteredCalendar(
            name="Download Test Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            filter_mode=FilterMode.include,
            needs_regeneration=True,
            public_token="download_token_ghi"
        )
        session.add(filtered_calendar)
        session.commit()
        
        # Request iCal content
        response = self.client.get(f"/cal/{filtered_calendar.public_token}")
        
        assert response.status_code == 200
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]
        assert "Download_Test_Filter.ics" in response.headers["content-disposition"]
    
    def test_empty_filter_returns_valid_empty_calendar(self, session: Session, sample_calendar_with_events):
        """Test that filter with no matching events returns valid empty calendar"""
        calendar = sample_calendar_with_events
        
        # Add only Personal events
        personal_event = Event(
            title="Personal Task",
            start=datetime.utcnow() + timedelta(days=1),
            end=datetime.utcnow() + timedelta(days=1, hours=1),
            calendar_id=calendar.id,
            category="Personal"
        )
        session.add(personal_event)
        session.commit()
        
        # Create filtered calendar that only includes Work events (which don't exist)
        filtered_calendar = FilteredCalendar(
            name="Empty Work Filter",
            source_calendar_id=calendar.id,
            user_id="public",
            include_events=serialize_json_field(["Work"]),
            exclude_events=serialize_json_field([]),
            filter_mode=FilterMode.include,
            needs_regeneration=True,
            public_token="empty_token_jkl"
        )
        session.add(filtered_calendar)
        session.commit()
        
        # Request filtered iCal content
        response = self.client.get(f"/cal/{filtered_calendar.public_token}")
        
        assert response.status_code == 200
        content = response.text
        
        # Should be valid iCal with no events
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content
        assert "VERSION:2.0" in content
        assert "PRODID:" in content
        
        # Should NOT contain any events
        assert "BEGIN:VEVENT" not in content
        assert "Personal Task" not in content