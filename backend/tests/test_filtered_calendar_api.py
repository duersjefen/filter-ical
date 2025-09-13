"""
Tests for Filtered Calendar API Endpoints
Comprehensive testing of the new filtered calendar feature
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from app.main import app
from app.models import Event, FilterConfig

client = TestClient(app)

# === TEST DATA FIXTURES ===

@pytest.fixture
def sample_calendar_data():
    """Sample calendar data for testing"""
    return {
        "calendars": {
            "cal1": {
                "id": "cal1",
                "name": "Test Calendar",
                "url": "https://example.com/calendar.ics",
                "user_id": "testuser",
                "created_at": "2024-01-15T10:00:00"
            }
        }
    }

@pytest.fixture  
def sample_events():
    """Sample events for testing"""
    return [
        Event(
            uid="event1",
            summary="Team Meeting",
            dtstart="2024-01-15T09:00:00",
            dtend="2024-01-15T10:00:00",
            location="Conference Room",
            description="Weekly sync",
            raw="BEGIN:VEVENT\nUID:event1\nCATEGORIES:Meeting\nEND:VEVENT"
        ),
        Event(
            uid="event2",
            summary="Code Review",
            dtstart="2024-01-16T14:00:00", 
            dtend="2024-01-16T15:00:00",
            location="Online",
            description="PR review",
            raw="BEGIN:VEVENT\nUID:event2\nCATEGORIES:Development\nEND:VEVENT"
        ),
        Event(
            uid="event3",
            summary="Personal Dentist",
            dtstart="2024-01-17T16:00:00",
            dtend="2024-01-17T17:00:00",
            location="Clinic",
            description="Checkup",
            raw="BEGIN:VEVENT\nUID:event3\nCATEGORIES:Personal\nEND:VEVENT"
        )
    ]


# === FILTERED CALENDAR CRUD TESTS ===

class TestFilteredCalendarCRUD:
    """Test filtered calendar CRUD operations"""
    
    @patch('app.main.get_store_data')
    @patch('app.main.save_store_data')
    def test_create_filtered_calendar_success(self, mock_save, mock_get, sample_calendar_data):
        """Test successful filtered calendar creation"""
        mock_get.return_value = sample_calendar_data
        
        request_data = {
            "source_calendar_id": "cal1",
            "name": "Work Events Only",
            "filter_config": {
                "include_categories": ["Meeting", "Development"],
                "exclude_categories": ["Personal"],
                "filter_mode": "include"
            }
        }
        
        response = client.post(
            "/api/filtered-calendars",
            json=request_data,
            headers={"X-User-ID": "testuser"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "public_token" in data
        assert "calendar_url" in data
        assert "preview_url" in data
        assert data["name"] == "Work Events Only"
        assert data["source_calendar_id"] == "cal1"
        assert "filter-ical.de/cal/" in data["calendar_url"]
        assert data["calendar_url"].endswith(".ics")
        
        # Verify store was called
        mock_save.assert_called_once()

    @patch('app.main.get_store_data')
    def test_create_filtered_calendar_missing_source(self, mock_get):
        """Test creation fails when source calendar missing"""
        mock_get.return_value = {"calendars": {}}
        
        request_data = {
            "source_calendar_id": "nonexistent",
            "name": "Test Filter"
        }
        
        response = client.post(
            "/api/filtered-calendars",
            json=request_data,
            headers={"X-User-ID": "testuser"}
        )
        
        assert response.status_code == 404
        assert "Source calendar not found" in response.json()["detail"]

    def test_create_filtered_calendar_missing_source_id(self):
        """Test creation fails when source_calendar_id missing"""
        request_data = {
            "name": "Test Filter"
        }
        
        response = client.post(
            "/api/filtered-calendars", 
            json=request_data,
            headers={"X-User-ID": "testuser"}
        )
        
        assert response.status_code == 400
        assert "source_calendar_id is required" in response.json()["detail"]

    @patch('app.main.get_store_data')
    def test_get_filtered_calendars(self, mock_get):
        """Test retrieving user's filtered calendars"""
        mock_data = {
            "filtered_calendars": {
                "fc1": {
                    "id": "fc1",
                    "name": "Work Events",
                    "public_token": "abc123def456ghij7890",
                    "user_id": "testuser",
                    "is_active": True,
                    "source_calendar_id": "cal1",
                    "created_at": "2024-01-15T10:00:00"
                },
                "fc2": {
                    "id": "fc2", 
                    "name": "Other User's Calendar",
                    "public_token": "xyz789",
                    "user_id": "otheruser",
                    "is_active": True,
                    "source_calendar_id": "cal2",
                    "created_at": "2024-01-15T11:00:00"
                }
            }
        }
        mock_get.return_value = mock_data
        
        response = client.get(
            "/api/filtered-calendars",
            headers={"X-User-ID": "testuser"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return calendars for testuser
        assert len(data["filtered_calendars"]) == 1
        assert data["filtered_calendars"][0]["name"] == "Work Events"
        assert "calendar_url" in data["filtered_calendars"][0]

    @patch('app.main.get_store_data')
    @patch('app.main.save_store_data')
    def test_update_filtered_calendar(self, mock_save, mock_get):
        """Test updating filtered calendar config"""
        mock_data = {
            "filtered_calendars": {
                "fc1": {
                    "id": "fc1",
                    "name": "Old Name",
                    "user_id": "testuser",
                    "public_token": "abc123def456ghij7890",
                    "filter_config": {
                        "include_categories": ["Meeting"],
                        "filter_mode": "include"
                    }
                }
            }
        }
        mock_get.return_value = mock_data
        
        update_data = {
            "name": "Updated Name",
            "filter_config": {
                "include_categories": ["Meeting", "Development"],
                "exclude_categories": ["Personal"],
                "filter_mode": "include"
            }
        }
        
        response = client.put(
            "/api/filtered-calendars/fc1",
            json=update_data,
            headers={"X-User-ID": "testuser"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Updated Name"
        assert "Development" in data["filter_config"]["include_categories"]
        mock_save.assert_called_once()

    @patch('app.main.get_store_data')
    @patch('app.main.save_store_data') 
    def test_delete_filtered_calendar(self, mock_save, mock_get):
        """Test deleting (deactivating) filtered calendar"""
        mock_data = {
            "filtered_calendars": {
                "fc1": {
                    "id": "fc1",
                    "user_id": "testuser", 
                    "is_active": True
                }
            }
        }
        mock_get.return_value = mock_data
        
        response = client.delete(
            "/api/filtered-calendars/fc1",
            headers={"X-User-ID": "testuser"}
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        mock_save.assert_called_once()


# === PUBLIC CALENDAR SERVING TESTS ===

class TestPublicCalendarServing:
    """Test public calendar serving endpoints"""
    
    @patch('app.main.get_store_data')
    @patch('app.main.fetch_calendar_events')
    def test_serve_filtered_calendar_ics(self, mock_fetch, mock_get, sample_events):
        """Test serving filtered iCal content"""
        token = "abc123def456ghij7890"  # Valid 20-character token
        
        mock_data = {
            "filtered_calendars": {
                "fc1": {
                    "id": "fc1",
                    "public_token": token,
                    "name": "Work Events",
                    "user_id": "testuser",
                    "source_calendar_id": "cal1",
                    "is_active": True,
                    "filter_config": {
                        "include_categories": ["Meeting", "Development"],
                        "exclude_categories": ["Personal"],
                        "filter_mode": "include"
                    }
                }
            },
            "calendars": {
                "cal1": {
                    "id": "cal1",
                    "name": "Source Calendar",
                    "url": "https://example.com/cal.ics",
                    "user_id": "testuser"
                }
            }
        }
        mock_get.return_value = mock_data
        mock_fetch.return_value = (True, sample_events, "Success")
        
        response = client.get(f"/cal/{token}.ics")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/calendar")
        assert "attachment" in response.headers.get("content-disposition", "")
        
        # Verify iCal content structure
        content = response.content.decode()
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content
        assert "Work Events" in content

    def test_serve_filtered_calendar_invalid_token(self):
        """Test serving with invalid token format"""
        invalid_token = "short"  # Too short
        
        response = client.get(f"/cal/{invalid_token}.ics")
        
        assert response.status_code == 400
        assert "Invalid token format" in response.json()["detail"]

    @patch('app.main.get_store_data')
    def test_serve_filtered_calendar_not_found(self, mock_get):
        """Test serving non-existent calendar"""
        token = "abc123def456ghij7890"  # Valid format but not found
        mock_get.return_value = {"filtered_calendars": {}}
        
        response = client.get(f"/cal/{token}.ics")
        
        assert response.status_code == 404
        assert "Calendar not found" in response.json()["detail"]

    @patch('app.main.get_store_data') 
    @patch('app.main.fetch_calendar_events')
    def test_preview_filtered_calendar(self, mock_fetch, mock_get, sample_events):
        """Test calendar preview endpoint"""
        token = "abc123def456ghij7890"
        
        mock_data = {
            "filtered_calendars": {
                "fc1": {
                    "public_token": token,
                    "name": "Work Events",
                    "user_id": "testuser",
                    "source_calendar_id": "cal1",
                    "is_active": True,
                    "filter_config": {
                        "include_categories": ["Meeting"],
                        "filter_mode": "include"
                    }
                }
            },
            "calendars": {
                "cal1": {
                    "id": "cal1",
                    "url": "https://example.com/cal.ics",
                    "user_id": "testuser"
                }
            }
        }
        mock_get.return_value = mock_data
        mock_fetch.return_value = (True, sample_events, "Success")
        
        response = client.get(f"/cal/{token}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["calendar_name"] == "Work Events"
        assert data["total_events"] >= 0
        assert "ics_url" in data
        assert "events" in data
        assert "filter_summary" in data


# === INTEGRATION TESTS ===

class TestFilteredCalendarIntegration:
    """Test end-to-end workflows"""
    
    @patch('app.main.get_store_data')
    @patch('app.main.save_store_data')
    @patch('app.main.fetch_calendar_events')
    def test_complete_workflow(self, mock_fetch, mock_save, mock_get, sample_calendar_data, sample_events):
        """Test complete filtered calendar workflow"""
        mock_get.return_value = sample_calendar_data
        mock_fetch.return_value = (True, sample_events, "Success")
        
        # Step 1: Create filtered calendar
        create_data = {
            "source_calendar_id": "cal1",
            "name": "Work Only",
            "filter_config": {
                "include_categories": ["Meeting", "Development"],
                "filter_mode": "include"
            }
        }
        
        create_response = client.post(
            "/api/filtered-calendars",
            json=create_data,
            headers={"X-User-ID": "testuser"}
        )
        
        assert create_response.status_code == 200
        created_cal = create_response.json()
        token = created_cal["public_token"]
        
        # Step 2: Update store data to include the new filtered calendar
        updated_store = {
            **sample_calendar_data,
            "filtered_calendars": {
                created_cal["id"]: {
                    "id": created_cal["id"],
                    "public_token": token,
                    "name": "Work Only",
                    "user_id": "testuser",
                    "source_calendar_id": "cal1",
                    "is_active": True,
                    "filter_config": create_data["filter_config"]
                }
            }
        }
        mock_get.return_value = updated_store
        
        # Step 3: Test public iCal serving
        ics_response = client.get(f"/cal/{token}.ics")
        assert ics_response.status_code == 200
        assert ics_response.headers["content-type"].startswith("text/calendar")
        
        # Step 4: Test preview
        preview_response = client.get(f"/cal/{token}")
        assert preview_response.status_code == 200
        preview_data = preview_response.json()
        assert preview_data["calendar_name"] == "Work Only"
        
        # Step 5: Test list filtered calendars
        list_response = client.get(
            "/api/filtered-calendars",
            headers={"X-User-ID": "testuser"}
        )
        assert list_response.status_code == 200
        assert len(list_response.json()["filtered_calendars"]) == 1


# === SECURITY TESTS ===

class TestFilteredCalendarSecurity:
    """Test security aspects of filtered calendars"""
    
    def test_user_isolation(self):
        """Test that users can only access their own filtered calendars"""
        # This test would verify user isolation in CRUD operations
        pass
    
    def test_token_validation(self):
        """Test comprehensive token validation"""
        test_cases = [
            ("", 400),  # Empty token
            ("short", 400),  # Too short
            ("a" * 65, 400),  # Too long  
            ("invalid@chars!", 400),  # Invalid characters
            ("abc123def456ghij7890", 404)  # Valid format but not found
        ]
        
        for token, expected_status in test_cases:
            response = client.get(f"/cal/{token}.ics")
            assert response.status_code == expected_status
    
    @patch('app.main.get_store_data')
    @patch('app.main.fetch_calendar_events')
    def test_content_sanitization(self, mock_fetch, mock_get):
        """Test that sensitive content is sanitized"""
        token = "abc123def456ghij7890"
        
        # Create event with sensitive data
        sensitive_event = Event(
            uid="evil@hacker.com",  # Email in UID
            summary="<script>alert('xss')</script>",  # XSS attempt
            dtstart="2024-01-15T09:00:00",
            dtend="2024-01-15T10:00:00",
            location="Secret Location",
            description="Call +1-800-EVIL or visit https://evil.com",  # Phone and URL
            raw="BEGIN:VEVENT\nUID:evil@hacker.com\nEND:VEVENT"
        )
        
        mock_data = {
            "filtered_calendars": {
                "fc1": {
                    "public_token": token,
                    "name": "Test Calendar",
                    "user_id": "testuser", 
                    "source_calendar_id": "cal1",
                    "is_active": True,
                    "filter_config": {"filter_mode": "include"}
                }
            },
            "calendars": {
                "cal1": {
                    "id": "cal1",
                    "url": "https://example.com/cal.ics",
                    "user_id": "testuser"
                }
            }
        }
        mock_get.return_value = mock_data
        mock_fetch.return_value = (True, [sensitive_event], "Success")
        
        response = client.get(f"/cal/{token}.ics")
        
        assert response.status_code == 200
        content = response.content.decode()
        
        # Verify sanitization occurred
        assert "[email-removed]" in content or "evil@hacker.com" not in content
        assert "[url-removed]" in content or "https://evil.com" not in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])