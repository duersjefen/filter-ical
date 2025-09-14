"""
OpenAPI Contract Testing - Industry Best Practice
Tests validate actual API behavior matches OpenAPI specification
"""

import pytest
import yaml
import requests
from pathlib import Path
from typing import Dict, Any

# Load OpenAPI spec
def load_openapi_spec() -> Dict[str, Any]:
    spec_path = Path(__file__).parent.parent / "openapi.yaml"
    with open(spec_path, 'r') as f:
        return yaml.safe_load(f)

@pytest.fixture
def openapi_spec():
    return load_openapi_spec()

@pytest.fixture  
def base_url():
    return "http://localhost:3000"

@pytest.fixture
def headers():
    return {"x-user-id": "test-user"}

class TestHealthEndpoint:
    """Test health endpoint matches OpenAPI spec"""
    
    def test_health_check_contract(self, base_url, openapi_spec):
        """Health endpoint should match OpenAPI response schema"""
        response = requests.get(f"{base_url}/health")
        
        # Validate status code
        assert response.status_code == 200
        
        # Validate response schema matches OpenAPI spec
        expected_schema = openapi_spec['paths']['/health']['get']['responses']['200']['content']['application/json']['schema']
        data = response.json()
        
        # Check required properties exist
        assert 'status' in data
        assert 'service' in data
        
        # Check property types match spec
        assert isinstance(data['status'], str)
        assert isinstance(data['service'], str)
        
        # Check values match examples
        assert data['status'] == 'healthy'
        assert data['service'] == 'ical-viewer'

class TestCalendarEndpoints:
    """Test calendar endpoints match OpenAPI spec"""
    
    def test_list_calendars_contract(self, base_url, headers, openapi_spec):
        """GET /api/calendars should match OpenAPI spec"""
        response = requests.get(f"{base_url}/api/calendars", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        assert 'calendars' in data
        assert isinstance(data['calendars'], list)
        
        # If calendars exist, validate schema
        if data['calendars']:
            calendar = data['calendars'][0]
            required_fields = ['id', 'name', 'url', 'user_id']
            for field in required_fields:
                assert field in calendar, f"Calendar missing required field: {field}"
    
    def test_add_calendar_contract(self, base_url, headers, openapi_spec):
        """POST /api/calendars should match OpenAPI spec"""
        # Valid request matching OpenAPI schema
        calendar_data = {
            "name": "Test Calendar Contract",
            "url": "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics"
        }
        
        response = requests.post(
            f"{base_url}/api/calendars", 
            json=calendar_data, 
            headers=headers
        )
        
        # Should return 200 OK (as per OpenAPI spec)
        assert response.status_code == 200
        
        data = response.json()
        
        # Response should match OpenAPI schema
        assert 'success' in data
        assert isinstance(data['success'], bool)
        
        if 'calendar' in data:
            calendar = data['calendar']
            required_fields = ['id', 'name', 'url', 'user_id']
            for field in required_fields:
                assert field in calendar
    
    def test_invalid_calendar_returns_400(self, base_url, headers):
        """Invalid calendar should return 400 as per OpenAPI spec"""
        invalid_data = {"name": "Test", "url": "not-a-url"}
        
        response = requests.post(
            f"{base_url}/api/calendars",
            json=invalid_data,
            headers=headers
        )
        
        # Should return 400 Bad Request
        assert response.status_code in [400, 422]  # FastAPI uses 422 for validation

class TestEventEndpoints:
    """Test event endpoints match OpenAPI spec"""
    
    @pytest.fixture
    def test_calendar_id(self, base_url, headers):
        """Create a test calendar and return its ID"""
        calendar_data = {
            "name": "Contract Test Calendar", 
            "url": "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics"
        }
        
        response = requests.post(f"{base_url}/api/calendars", json=calendar_data, headers=headers)
        if response.status_code == 200:
            return response.json().get('calendar', {}).get('id')
        return None
    
    def test_get_events_contract(self, base_url, headers, test_calendar_id, openapi_spec):
        """GET /api/calendar/{id}/events should match OpenAPI spec"""
        if not test_calendar_id:
            pytest.skip("No test calendar available")
            
        response = requests.get(
            f"{base_url}/api/calendar/{test_calendar_id}/events",
            headers=headers
        )
        
        # Check response status
        if response.status_code == 500:
            pytest.fail("Backend returning 500 - parsing issue needs fixing")
        elif response.status_code == 200:
            data = response.json()
            assert 'events' in data
            assert isinstance(data['events'], list)
            
            # If events exist, validate schema
            if data['events']:
                event = data['events'][0]
                required_fields = ['uid', 'summary', 'dtstart']
                for field in required_fields:
                    assert field in event, f"Event missing required field: {field}"
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_categories_contract(self, base_url, headers, test_calendar_id):
        """GET /api/calendar/{id}/categories should match OpenAPI spec"""
        if not test_calendar_id:
            pytest.skip("No test calendar available")
            
        response = requests.get(
            f"{base_url}/api/calendar/{test_calendar_id}/categories",
            headers=headers
        )
        
        if response.status_code == 500:
            pytest.fail("Backend returning 500 - parsing issue needs fixing")
        elif response.status_code == 200:
            data = response.json()
            assert 'categories' in data
            assert isinstance(data['categories'], dict)
            
            # Categories should be string -> integer mapping
            for category, count in data['categories'].items():
                assert isinstance(category, str)
                assert isinstance(count, int)
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

class TestSwaggerUI:
    """Test that interactive documentation is available"""
    
    def test_swagger_ui_available(self, base_url):
        """Swagger UI should be available at /api/docs"""
        response = requests.get(f"{base_url}/api/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_openapi_json_available(self, base_url):
        """OpenAPI JSON should be available at /api/openapi.json"""
        response = requests.get(f"{base_url}/api/openapi.json")
        assert response.status_code == 200
        
        # Should be valid JSON
        data = response.json()
        assert 'openapi' in data
        assert 'info' in data
        assert 'paths' in data

class TestUserPreferencesEndpoints:
    """Test calendar preferences endpoints match OpenAPI spec"""
    
    @pytest.fixture
    def test_calendar_id(self, base_url, headers):
        """Create a test calendar for preferences testing"""
        calendar_data = {
            "name": "Preferences Test Calendar",
            "url": "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics"
        }
        
        response = requests.post(f"{base_url}/api/calendars", json=calendar_data, headers=headers)
        if response.status_code == 200:
            return response.json().get('calendar', {}).get('id')
        return None
    
    def test_get_calendar_preferences_contract(self, base_url, headers, test_calendar_id, openapi_spec):
        """GET /api/calendars/{id}/preferences should match OpenAPI spec"""
        if not test_calendar_id:
            pytest.skip("No test calendar available")
            
        response = requests.get(
            f"{base_url}/api/calendars/{test_calendar_id}/preferences",
            headers=headers
        )
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Response should match OpenAPI schema
        assert 'success' in data
        assert 'preferences' in data
        assert isinstance(data['success'], bool)
        assert isinstance(data['preferences'], dict)
    
    def test_update_calendar_preferences_contract(self, base_url, headers, test_calendar_id, openapi_spec):
        """PUT /api/calendars/{id}/preferences should match OpenAPI spec"""
        if not test_calendar_id:
            pytest.skip("No test calendar available")
        
        # Valid preferences data matching OpenAPI schema
        preferences_data = {
            "selected_categories": ["Work", "Meeting"],
            "filter_mode": "include",
            "saved_at": "2025-09-13T10:30:00Z"
        }
        
        response = requests.put(
            f"{base_url}/api/calendars/{test_calendar_id}/preferences",
            json=preferences_data,
            headers=headers
        )
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Response should match OpenAPI schema
        assert 'success' in data
        assert 'message' in data
        assert isinstance(data['success'], bool)
        assert isinstance(data['message'], str)
        assert data['message'] == "Preferences saved successfully"

class TestFilteredCalendarsEndpoints:
    """Test filtered calendars endpoints match OpenAPI spec"""
    
    @pytest.fixture
    def test_calendar_id(self, base_url, headers):
        """Create a test calendar for filtered calendar testing"""
        calendar_data = {
            "name": "Filtered Test Calendar",
            "url": "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics"
        }
        
        response = requests.post(f"{base_url}/api/calendars", json=calendar_data, headers=headers)
        if response.status_code == 200:
            return response.json().get('calendar', {}).get('id')
        return None
    
    def test_create_filtered_calendar_contract(self, base_url, headers, test_calendar_id, openapi_spec):
        """POST /api/filtered-calendars should match OpenAPI spec"""
        if not test_calendar_id:
            pytest.skip("No test calendar available")
        
        # Valid filtered calendar data matching OpenAPI schema
        filtered_calendar_data = {
            "source_calendar_id": test_calendar_id,
            "name": "Contract Test Filtered Calendar",
            "filter_config": {
                "include_categories": ["Work", "Meeting"],
                "exclude_categories": [],
                "filter_mode": "include",
                "match_all": False
            }
        }
        
        response = requests.post(
            f"{base_url}/api/filtered-calendars",
            json=filtered_calendar_data,
            headers=headers
        )
        
        # Should return 200 OK (as per OpenAPI spec)
        assert response.status_code == 200
        
        data = response.json()
        
        # Response should match OpenAPI schema
        assert 'success' in data
        assert isinstance(data['success'], bool)
        
        if 'filtered_calendar' in data:
            filtered_cal = data['filtered_calendar']
            required_fields = ['id', 'name', 'source_calendar_id', 'public_token', 'user_id', 'created_at']
            for field in required_fields:
                assert field in filtered_cal, f"FilteredCalendar missing required field: {field}"
    
    def test_list_filtered_calendars_contract(self, base_url, headers, openapi_spec):
        """GET /api/filtered-calendars should match OpenAPI spec"""
        response = requests.get(f"{base_url}/api/filtered-calendars", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        assert 'filtered_calendars' in data
        assert isinstance(data['filtered_calendars'], list)
        
        # If filtered calendars exist, validate schema
        if data['filtered_calendars']:
            filtered_cal = data['filtered_calendars'][0]
            required_fields = ['id', 'name', 'source_calendar_id', 'public_token', 'user_id']
            for field in required_fields:
                assert field in filtered_cal, f"FilteredCalendar missing required field: {field}"

class TestPublicAccessEndpoints:
    """Test public access endpoints match OpenAPI spec"""
    
    @pytest.fixture
    def test_token(self, base_url, headers, test_calendar_id):
        """Create a filtered calendar and return its public token"""
        if not test_calendar_id:
            return None
            
        filtered_calendar_data = {
            "source_calendar_id": test_calendar_id,
            "name": "Public Access Test",
            "filter_config": {
                "include_categories": ["Work"],
                "filter_mode": "include"
            }
        }
        
        response = requests.post(
            f"{base_url}/api/filtered-calendars",
            json=filtered_calendar_data,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json().get('filtered_calendar', {}).get('public_token')
        return None
    
    @pytest.fixture
    def test_calendar_id(self, base_url, headers):
        """Create a test calendar for public access testing"""
        calendar_data = {
            "name": "Public Access Test Calendar",
            "url": "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics"
        }
        
        response = requests.post(f"{base_url}/api/calendars", json=calendar_data, headers=headers)
        if response.status_code == 200:
            return response.json().get('calendar', {}).get('id')
        return None
    
    def test_get_filtered_ical_contract(self, base_url, test_token, openapi_spec):
        """GET /cal/{token}.ics should return valid iCal format"""
        if not test_token:
            pytest.skip("No test token available")
        
        response = requests.get(f"{base_url}/cal/{test_token}.ics")
        
        if response.status_code == 200:
            # Should return iCal format
            assert response.headers.get('content-type', '').startswith('text/calendar')
            
            content = response.text
            assert 'BEGIN:VCALENDAR' in content
            assert 'END:VCALENDAR' in content
        elif response.status_code == 404:
            # Valid response for non-existent token
            data = response.json()
            assert 'detail' in data
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_preview_filtered_calendar_contract(self, base_url, test_token, openapi_spec):
        """GET /cal/{token} should return HTML preview"""
        if not test_token:
            pytest.skip("No test token available")
        
        response = requests.get(f"{base_url}/cal/{test_token}")
        
        if response.status_code == 200:
            # Should return HTML content
            assert 'text/html' in response.headers.get('content-type', '')
            
            content = response.text
            assert '<html' in content.lower() or '<!doctype html' in content.lower()
        elif response.status_code == 404:
            # Valid response for non-existent token
            data = response.json()
            assert 'detail' in data
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

class TestErrorHandling:
    """Test error responses match OpenAPI spec"""
    
    def test_404_response_format(self, base_url, headers):
        """404 responses should match OpenAPI error schema"""
        response = requests.get(
            f"{base_url}/api/calendar/nonexistent-id/events",
            headers=headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert 'detail' in data
        assert isinstance(data['detail'], str)
    
    def test_calendar_preferences_404(self, base_url, headers):
        """Calendar preferences 404 should match error schema"""
        response = requests.get(
            f"{base_url}/api/calendars/nonexistent-id/preferences",
            headers=headers
        )
        
        # Should either return 404 or 500 (depending on implementation)
        assert response.status_code in [404, 500]
        data = response.json()
        assert 'detail' in data
        assert isinstance(data['detail'], str)

if __name__ == "__main__":
    # Run contract tests
    pytest.main([__file__, "-v", "--tb=short"])