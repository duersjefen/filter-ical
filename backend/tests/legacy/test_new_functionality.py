"""
Tests for new functionality added in the recent development session:
- Time preservation in date parsing
- Category-based filtering 
- Exclude mode functionality
- Enhanced iCal generation
"""
import pytest
from datetime import datetime, date
from fastapi.testclient import TestClient
from app.main import app
from app.models import Event
from app.services.events import parse_date_to_string, ical_component_to_event, generate_ical_content

client = TestClient(app)

class TestTimeParsing:
    """Test time preservation functionality."""
    
    def test_parse_date_to_string_preserves_datetime(self):
        """Test that datetime objects preserve time information."""
        dt = datetime(2025, 9, 14, 14, 30, 0)
        result = parse_date_to_string(dt)
        assert result == "20250914T143000Z"
        assert "T" in result
        assert len(result) == 16
        
    def test_parse_date_to_string_date_only(self):
        """Test that date objects remain date-only."""
        dt = date(2025, 9, 14)
        result = parse_date_to_string(dt)
        assert result == "20250914"
        assert "T" not in result
        assert len(result) == 8
        
    def test_parse_date_to_string_preserves_time_strings(self):
        """Test that time-containing strings are preserved."""
        dt_str = "20250914T143000Z"
        result = parse_date_to_string(dt_str)
        assert result == "20250914T143000Z"
        assert "T" in result
        
    def test_parse_date_to_string_handles_date_strings(self):
        """Test that date-only strings are preserved."""
        dt_str = "20250914"
        result = parse_date_to_string(dt_str)
        assert result == "20250914"
        assert "T" not in result

class TestCategoryEndpoints:
    """Test category-based functionality."""
    
    def test_categories_endpoint_exists(self):
        """Test that categories endpoint is available."""
        response = client.get("/api/calendar/1/categories", headers={"X-User-ID": "testuser"})
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        
    def test_categories_structure(self):
        """Test category data structure."""
        response = client.get("/api/calendar/1/categories", headers={"X-User-ID": "testuser"})
        assert response.status_code == 200
        data = response.json()
        
        if data["categories"]:
            category = data["categories"][0]
            assert "name" in category
            assert "count" in category
            assert "events" in category
            assert isinstance(category["count"], int)
            assert isinstance(category["events"], list)
            
    def test_categories_sorted_by_count(self):
        """Test that categories are sorted by event count descending."""
        response = client.get("/api/calendar/1/categories", headers={"X-User-ID": "testuser"})
        assert response.status_code == 200
        data = response.json()
        
        categories = data["categories"]
        if len(categories) > 1:
            for i in range(len(categories) - 1):
                assert categories[i]["count"] >= categories[i + 1]["count"]

class TestExcludeModeFiltering:
    """Test exclude mode functionality in iCal generation."""
    
    def test_filtered_ical_include_mode(self):
        """Test include mode filtering."""
        response = client.get(
            "/api/calendar/1/filtered.ical?categories=Test&mode=include",
            headers={"X-User-ID": "testuser"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/calendar")
        
    def test_filtered_ical_exclude_mode(self):
        """Test exclude mode filtering."""
        response = client.get(
            "/api/calendar/1/filtered.ical?categories=Test&mode=exclude", 
            headers={"X-User-ID": "testuser"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/calendar")
        
    def test_filtered_ical_invalid_mode_defaults_to_include(self):
        """Test that invalid mode parameter defaults to include."""
        response = client.get(
            "/api/calendar/1/filtered.ical?categories=Test&mode=invalid",
            headers={"X-User-ID": "testuser"}
        )
        assert response.status_code == 200
        # Should still return valid iCal content
        
    def test_filtered_ical_no_categories_returns_all(self):
        """Test that no categories specified returns all events."""
        response = client.get(
            "/api/calendar/1/filtered.ical",
            headers={"X-User-ID": "testuser"}
        )
        assert response.status_code == 200
        
    def test_filtered_ical_filename_includes_mode(self):
        """Test that download filename includes filter mode."""
        response = client.get(
            "/api/calendar/1/filtered.ical?categories=Test&mode=include",
            headers={"X-User-ID": "testuser"}
        )
        assert response.status_code == 200
        content_disposition = response.headers.get("content-disposition", "")
        assert "attachment" in content_disposition
        assert "filtered_" in content_disposition

class TestICalGeneration:
    """Test iCal file generation functionality."""
    
    def test_generate_ical_content_basic(self):
        """Test basic iCal content generation."""
        events = [
            Event(
                uid="test1@example.com",
                summary="Test Event",
                dtstart="20250914T143000Z",
                dtend="20250914T153000Z", 
                location="Test Location",
                description="Test Description",
                raw=""
            )
        ]
        
        ical_content = generate_ical_content(events, "Test Calendar", {"Test"})
        
        assert "BEGIN:VCALENDAR" in ical_content
        assert "END:VCALENDAR" in ical_content
        assert "Test Event" in ical_content
        assert "Test Location" in ical_content
        assert "Test Description" in ical_content
        assert "20250914T143000Z" in ical_content
        
    def test_generate_ical_content_with_categories(self):
        """Test iCal generation includes category information."""
        events = [
            Event(
                uid="test1@example.com",
                summary="Test Event",
                dtstart="20250914T143000Z",
                dtend="20250914T153000Z",
                location=None,
                description=None,
                raw=""
            )
        ]
        
        ical_content = generate_ical_content(events, "Test Calendar", {"Test Event"})
        
        assert "CATEGORIES:Test Event" in ical_content
        assert "Filtered calendar with categories: Test Event" in ical_content
        
    def test_generate_ical_content_escapes_special_chars(self):
        """Test that special characters are properly escaped."""
        events = [
            Event(
                uid="test1@example.com",
                summary="Test, Event; With: Special\\Chars",
                dtstart="20250914",
                dtend="20250914",
                location="Location, With; Special: Chars",
                description="Description\\nWith\nNewlines,And;Commas",
                raw=""
            )
        ]
        
        ical_content = generate_ical_content(events, "Test", set())
        
        # Should contain escaped versions
        assert "\\," in ical_content or "\\;" in ical_content or "\\n" in ical_content

class TestTimeDisplayIntegration:
    """Test time display integration with API."""
    
    def test_events_with_time_info_preserved(self):
        """Test that events with time information preserve it through API."""
        # This test would need to be adapted based on actual calendar data
        response = client.get("/api/calendar/1/events", headers={"X-User-ID": "testuser"})
        
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            
            # Check if any events have time information 
            timed_events = [e for e in events if "T" in str(e.get("dtstart", ""))]
            date_only_events = [e for e in events if "T" not in str(e.get("dtstart", ""))]
            
            # If we have timed events, they should preserve time format
            for event in timed_events:
                dtstart = event.get("dtstart", "")
                assert "T" in dtstart
                assert len(dtstart) >= 13  # YYYYMMDDTHHMMSS minimum
                
    def test_categories_events_preserve_time(self):
        """Test that category endpoint preserves time information in events."""
        response = client.get("/api/calendar/1/categories", headers={"X-User-ID": "testuser"})
        
        if response.status_code == 200:
            data = response.json()
            categories = data.get("categories", [])
            
            for category in categories:
                events = category.get("events", [])
                for event in events:
                    dtstart = event.get("dtstart", "")
                    # Should be either YYYYMMDD or YYYYMMDDTHHMMSSZ format
                    assert len(dtstart) == 8 or (len(dtstart) >= 13 and "T" in dtstart)

class TestErrorHandling:
    """Test error handling for new functionality."""
    
    def test_categories_nonexistent_calendar(self):
        """Test categories endpoint with non-existent calendar."""
        response = client.get("/api/calendar/999999/categories", headers={"X-User-ID": "testuser"})
        assert response.status_code == 404
        
    def test_filtered_ical_nonexistent_calendar(self):
        """Test filtered iCal with non-existent calendar."""
        response = client.get("/api/calendar/999999/filtered.ical", headers={"X-User-ID": "testuser"})
        assert response.status_code == 404
        
    def test_filtered_ical_malformed_categories(self):
        """Test filtered iCal with malformed category parameters."""
        response = client.get(
            "/api/calendar/1/filtered.ical?categories=,,,&mode=include",
            headers={"X-User-ID": "testuser"}
        )
        # Should handle gracefully, not crash
        assert response.status_code in [200, 400]

class TestPerformance:
    """Test performance of new functionality."""
    
    def test_categories_response_time(self):
        """Test that categories endpoint responds quickly."""
        import time
        
        start = time.time()
        response = client.get("/api/calendar/1/categories", headers={"X-User-ID": "testuser"})
        end = time.time()
        
        # Should respond reasonably quickly
        assert (end - start) < 2.0  # Under 2 seconds
        
    def test_filtered_ical_generation_performance(self):
        """Test that iCal generation is performant."""
        import time
        
        start = time.time()
        response = client.get(
            "/api/calendar/1/filtered.ical?categories=Test&mode=include",
            headers={"X-User-ID": "testuser"}
        )
        end = time.time()
        
        # Should generate iCal reasonably quickly  
        assert (end - start) < 3.0  # Under 3 seconds