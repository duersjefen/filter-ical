"""
Contract validation tests - ensure API responses match OpenAPI specification exactly
Industry standard practice: All API responses must be validated against contract
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List

import pytest
import requests
from fastapi.testclient import TestClient
from jsonschema import validate, ValidationError
from openapi_spec_validator import validate_spec
from prance import ResolvingParser

from app.main import app


class TestOpenAPIContract:
    """Test suite to validate API contract compliance"""
    
    @classmethod
    def setup_class(cls):
        """Load and validate OpenAPI specification"""
        cls.client = TestClient(app)
        cls.spec_path = Path(__file__).parent.parent / "openapi.yaml"
        
        # Load OpenAPI specification
        with open(cls.spec_path, 'r') as f:
            cls.openapi_spec = yaml.safe_load(f)
        
        # Validate OpenAPI spec itself
        validate_spec(cls.openapi_spec)
        
        # Parse and resolve the specification
        cls.parser = ResolvingParser(str(cls.spec_path))
        cls.resolved_spec = cls.parser.specification
        
        # Extract schemas for validation
        cls.schemas = cls.resolved_spec.get('components', {}).get('schemas', {})
        
        # Test user for authenticated requests
        cls.test_user_headers = {"x-user-id": "test_user_123"}
    
    def validate_response_schema(self, response_data: Any, schema_ref: str) -> None:
        """Validate response data against OpenAPI schema"""
        if schema_ref.startswith('#/components/schemas/'):
            schema_name = schema_ref.split('/')[-1]
            schema = self.schemas.get(schema_name)
            if schema:
                validate(instance=response_data, schema=schema)
            else:
                pytest.fail(f"Schema {schema_name} not found in OpenAPI spec")
    
    def validate_endpoint_response(self, endpoint: str, method: str, status_code: int, response_data: Any) -> None:
        """Validate response against OpenAPI endpoint specification"""
        paths = self.resolved_spec.get('paths', {})
        endpoint_spec = paths.get(endpoint, {})
        method_spec = endpoint_spec.get(method.lower(), {})
        responses = method_spec.get('responses', {})
        
        # Check if status code is documented
        status_str = str(status_code)
        if status_str not in responses:
            pytest.fail(f"Status code {status_code} not documented for {method} {endpoint}")
        
        # Get response schema
        response_spec = responses[status_str]
        content = response_spec.get('content', {})
        json_content = content.get('application/json', {})
        schema = json_content.get('schema', {})
        
        if schema:
            # Resolve schema references
            if '$ref' in schema:
                schema_ref = schema['$ref']
                self.validate_response_schema(response_data, schema_ref)
            else:
                validate(instance=response_data, schema=schema)

    # Test Calendar Management Endpoints
    @pytest.mark.unit
    def test_get_calendars_contract(self):
        """Test GET /api/calendars conforms to contract"""
        response = self.client.get("/api/calendars", headers=self.test_user_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "calendars" in data
        assert isinstance(data["calendars"], list)
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response("/api/calendars", "GET", 200, data)
    
    @pytest.mark.unit
    def test_create_calendar_contract(self):
        """Test POST /api/calendars conforms to contract"""
        calendar_data = {
            "name": "Test Contract Calendar",
            "url": "https://example.com/test-contract.ics"
        }
        
        response = self.client.post(
            "/api/calendars", 
            json=calendar_data, 
            headers=self.test_user_headers
        )
        
        assert response.status_code in [200, 201]  # Per OpenAPI spec
        data = response.json()
        
        # Validate required fields per contract
        assert "id" in data
        assert "name" in data
        assert "url" in data
        assert "user_id" in data
        assert "created_at" in data
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response("/api/calendars", "POST", response.status_code, data)
        
        # Clean up
        self.client.delete(f"/api/calendars/{data['id']}", headers=self.test_user_headers)
    
    @pytest.mark.unit
    def test_delete_calendar_contract(self):
        """Test DELETE /api/calendars/{calendar_id} conforms to contract"""
        # Create a calendar first
        calendar_data = {
            "name": "Test Delete Calendar",
            "url": "https://example.com/test-delete.ics"
        }
        create_response = self.client.post(
            "/api/calendars", 
            json=calendar_data, 
            headers=self.test_user_headers
        )
        calendar_id = create_response.json()["id"]
        
        # Delete the calendar
        response = self.client.delete(
            f"/api/calendars/{calendar_id}", 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 204  # Per OpenAPI spec
        # 204 responses should have no content
        assert response.content == b''
    
    @pytest.mark.unit
    def test_get_calendar_events_contract(self):
        """Test GET /api/calendar/{calendar_id}/events conforms to contract"""
        # Create a calendar first
        calendar_data = {
            "name": "Test Events Calendar",
            "url": "https://example.com/test-events.ics"
        }
        create_response = self.client.post(
            "/api/calendars", 
            json=calendar_data, 
            headers=self.test_user_headers
        )
        calendar_id = create_response.json()["id"]
        
        # Get events (will be empty but should follow contract)
        response = self.client.get(
            f"/api/calendar/{calendar_id}/events", 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate contract-compliant structure
        assert "events" in data
        assert isinstance(data["events"], dict)  # Should be object, not array
        
        # Each event type should have count and events array
        for event_type_name, event_type_data in data["events"].items():
            assert "count" in event_type_data
            assert "events" in event_type_data
            assert isinstance(event_type_data["count"], int)
            assert isinstance(event_type_data["events"], list)
            
            # Each event in the array should be a full Event object
            for event in event_type_data["events"]:
                assert "id" in event
                assert "title" in event
                assert "start" in event
                assert "end" in event
                assert "category" in event
                # description and location are optional
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response(
            "/api/calendar/{calendar_id}/events", 
            "GET", 
            200, 
            data
        )
        
        # Clean up
        self.client.delete(f"/api/calendars/{calendar_id}", headers=self.test_user_headers)
    
    def test_error_responses_contract(self):
        """Test error responses conform to contract"""
        # Test 401 Unauthorized
        response = self.client.get("/api/calendars")  # No headers
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        
        # Test 404 Not Found
        response = self.client.get(
            "/api/calendar/nonexistent/events", 
            headers=self.test_user_headers
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
    
    def test_filtered_calendars_contract(self):
        """Test filtered calendar endpoints conform to contract"""
        # Test GET /api/filtered-calendars
        response = self.client.get("/api/filtered-calendars", headers=self.test_user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "filtered_calendars" in data
        assert isinstance(data["filtered_calendars"], list)
        
        # Validate against schema
        self.validate_endpoint_response("/api/filtered-calendars", "GET", 200, data)
    
    def test_user_preferences_contract(self):
        """Test user preferences endpoints conform to contract"""
        # Test GET /api/user/preferences
        response = self.client.get("/api/user/preferences", headers=self.test_user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "preferences" in data
        assert isinstance(data["success"], bool)
        assert isinstance(data["preferences"], dict)
        
        # Test PUT /api/user/preferences
        preferences_data = {"theme": "dark", "language": "en"}
        response = self.client.put(
            "/api/user/preferences", 
            json=preferences_data, 
            headers=self.test_user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert isinstance(data["success"], bool)
    
    def test_create_filtered_calendar_contract(self):
        """Test POST /api/filtered-calendars conforms to contract"""
        # First create a source calendar
        calendar_data = {
            "name": "Source Calendar for Filter",
            "url": "https://example.com/source.ics"
        }
        create_response = self.client.post(
            "/api/calendars", 
            json=calendar_data, 
            headers=self.test_user_headers
        )
        source_calendar_id = create_response.json()["id"]
        
        # Create filtered calendar
        filtered_data = {
            "name": "Work Only Filter",
            "source_calendar_id": source_calendar_id,
            "filter_config": {
                "categories": ["work"],
                "exclude_keywords": ["personal"]
            }
        }
        
        response = self.client.post(
            "/api/filtered-calendars", 
            json=filtered_data, 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 201  # Per OpenAPI spec
        data = response.json()
        
        # Validate required fields per contract
        assert "id" in data
        assert "name" in data
        assert "source_calendar_id" in data
        assert "filter_config" in data
        assert "user_id" in data
        assert "created_at" in data
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response("/api/filtered-calendars", "POST", 201, data)
        
        # Clean up
        self.client.delete(f"/api/filtered-calendars/{data['id']}", headers=self.test_user_headers)
        self.client.delete(f"/api/calendars/{source_calendar_id}", headers=self.test_user_headers)
    
    def test_update_filtered_calendar_contract(self):
        """Test PUT /api/filtered-calendars/{filtered_calendar_id} conforms to contract"""
        # Setup: Create source calendar and filtered calendar
        calendar_data = {"name": "Update Test Calendar", "url": "https://example.com/update.ics"}
        create_response = self.client.post("/api/calendars", json=calendar_data, headers=self.test_user_headers)
        source_calendar_id = create_response.json()["id"]
        
        filtered_data = {
            "name": "Original Filter",
            "source_calendar_id": source_calendar_id,
            "filter_config": {"categories": ["original"]}
        }
        create_filtered_response = self.client.post("/api/filtered-calendars", json=filtered_data, headers=self.test_user_headers)
        filtered_calendar_id = create_filtered_response.json()["id"]
        
        # Update the filtered calendar
        update_data = {
            "name": "Updated Filter",
            "filter_config": {"categories": ["updated", "new"], "exclude_keywords": ["exclude"]}
        }
        
        response = self.client.put(
            f"/api/filtered-calendars/{filtered_calendar_id}", 
            json=update_data, 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate updated fields
        assert data["name"] == "Updated Filter"
        assert "updated" in data["filter_config"]["categories"]
        assert "new" in data["filter_config"]["categories"]
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response(f"/api/filtered-calendars/{filtered_calendar_id}", "PUT", 200, data)
        
        # Clean up
        self.client.delete(f"/api/filtered-calendars/{filtered_calendar_id}", headers=self.test_user_headers)
        self.client.delete(f"/api/calendars/{source_calendar_id}", headers=self.test_user_headers)
    
    def test_delete_filtered_calendar_contract(self):
        """Test DELETE /api/filtered-calendars/{filtered_calendar_id} conforms to contract"""
        # Setup: Create source calendar and filtered calendar
        calendar_data = {"name": "Delete Test Calendar", "url": "https://example.com/delete.ics"}
        create_response = self.client.post("/api/calendars", json=calendar_data, headers=self.test_user_headers)
        source_calendar_id = create_response.json()["id"]
        
        filtered_data = {
            "name": "Filter to Delete",
            "source_calendar_id": source_calendar_id,
            "filter_config": {"categories": ["test"]}
        }
        create_filtered_response = self.client.post("/api/filtered-calendars", json=filtered_data, headers=self.test_user_headers)
        filtered_calendar_id = create_filtered_response.json()["id"]
        
        # Delete the filtered calendar
        response = self.client.delete(
            f"/api/filtered-calendars/{filtered_calendar_id}", 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 204  # Per OpenAPI spec
        # 204 responses should have no content
        assert response.content == b''
        
        # Verify it's actually deleted
        get_response = self.client.get(f"/api/filtered-calendars/{filtered_calendar_id}", headers=self.test_user_headers)
        assert get_response.status_code == 404
        
        # Clean up source calendar
        self.client.delete(f"/api/calendars/{source_calendar_id}", headers=self.test_user_headers)
    
    def test_get_calendar_preferences_contract(self):
        """Test GET /api/calendars/{calendar_id}/preferences conforms to contract"""
        # Create a calendar first
        calendar_data = {"name": "Preferences Test Calendar", "url": "https://example.com/prefs.ics"}
        create_response = self.client.post("/api/calendars", json=calendar_data, headers=self.test_user_headers)
        calendar_id = create_response.json()["id"]
        
        # Get calendar preferences
        response = self.client.get(
            f"/api/calendars/{calendar_id}/preferences", 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate contract-compliant structure
        assert "success" in data
        assert "preferences" in data
        assert isinstance(data["success"], bool)
        assert isinstance(data["preferences"], dict)
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response(f"/api/calendars/{calendar_id}/preferences", "GET", 200, data)
        
        # Clean up
        self.client.delete(f"/api/calendars/{calendar_id}", headers=self.test_user_headers)
    
    def test_save_calendar_preferences_contract(self):
        """Test PUT /api/calendars/{calendar_id}/preferences conforms to contract"""
        # Create a calendar first
        calendar_data = {"name": "Save Preferences Test", "url": "https://example.com/save-prefs.ics"}
        create_response = self.client.post("/api/calendars", json=calendar_data, headers=self.test_user_headers)
        calendar_id = create_response.json()["id"]
        
        # Save calendar preferences
        preferences_data = {
            "default_view": "month",
            "show_weekends": True,
            "event_color": "#3498db"
        }
        
        response = self.client.put(
            f"/api/calendars/{calendar_id}/preferences", 
            json=preferences_data, 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "success" in data
        assert isinstance(data["success"], bool)
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response(f"/api/calendars/{calendar_id}/preferences", "PUT", 200, data)
        
        # Clean up
        self.client.delete(f"/api/calendars/{calendar_id}", headers=self.test_user_headers)
    
    def test_get_saved_filters_contract(self):
        """Test GET /api/filters conforms to contract"""
        response = self.client.get("/api/filters", headers=self.test_user_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Validate contract-compliant structure
        assert "filters" in data
        assert isinstance(data["filters"], list)
        
        # Each filter should have proper structure
        for filter_item in data["filters"]:
            assert "id" in filter_item
            assert "name" in filter_item
            assert "config" in filter_item
            assert "user_id" in filter_item
            assert "created_at" in filter_item
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response("/api/filters", "GET", 200, data)
    
    def test_create_saved_filter_contract(self):
        """Test POST /api/filters conforms to contract"""
        filter_data = {
            "name": "Work Events Only",
            "config": {
                "categories": ["work", "meetings"],
                "exclude_keywords": ["personal", "vacation"]
            }
        }
        
        response = self.client.post(
            "/api/filters", 
            json=filter_data, 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 201  # Per OpenAPI spec
        data = response.json()
        
        # Validate required fields per contract
        assert "id" in data
        assert "name" in data
        assert "config" in data
        assert "user_id" in data
        assert "created_at" in data
        assert data["name"] == filter_data["name"]
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response("/api/filters", "POST", 201, data)
        
        # Clean up
        self.client.delete(f"/api/filters/{data['id']}", headers=self.test_user_headers)
    
    def test_delete_saved_filter_contract(self):
        """Test DELETE /api/filters/{filter_id} conforms to contract"""
        # Create a filter first
        filter_data = {"name": "Filter to Delete", "config": {"categories": ["test"]}}
        create_response = self.client.post("/api/filters", json=filter_data, headers=self.test_user_headers)
        filter_id = create_response.json()["id"]
        
        # Delete the filter
        response = self.client.delete(
            f"/api/filters/{filter_id}", 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 204  # Per OpenAPI spec
        # 204 responses should have no content
        assert response.content == b''
    
    @pytest.mark.unit
    def test_generate_ical_contract(self):
        """Test POST /api/calendar/{calendar_id}/generate conforms to contract"""
        # Create a calendar first
        calendar_data = {"name": "iCal Generation Test", "url": "https://example.com/generate.ics"}
        create_response = self.client.post("/api/calendars", json=calendar_data, headers=self.test_user_headers)
        calendar_id = create_response.json()["id"]
        
        # Generate iCal content
        generation_data = {
            "selected_events": ["event_1", "event_2"],
            "filter_mode": "include"
        }
        
        response = self.client.post(
            f"/api/calendar/{calendar_id}/generate", 
            json=generation_data, 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 200
        # Should return text/calendar content type
        assert "text/calendar" in response.headers.get("content-type", "")
        
        # Basic iCal format validation
        content = response.text
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content
        
        # Clean up
        self.client.delete(f"/api/calendars/{calendar_id}", headers=self.test_user_headers)
    
    def test_comprehensive_error_responses_contract(self):
        """Test comprehensive error response types conform to contract"""
        # Test 400 Bad Request responses
        # POST calendar with invalid data
        invalid_calendar = {"name": ""}  # Missing required field
        response = self.client.post("/api/calendars", json=invalid_calendar, headers=self.test_user_headers)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        
        # POST filtered calendar with invalid source
        invalid_filtered = {
            "name": "Invalid Filter",
            "source_calendar_id": "nonexistent",
            "filter_config": {}
        }
        response = self.client.post("/api/filtered-calendars", json=invalid_filtered, headers=self.test_user_headers)
        assert response.status_code == 404  # Source calendar not found
        data = response.json()
        assert "detail" in data
        
        # Test various 404 scenarios
        test_404_endpoints = [
            f"/api/calendars/nonexistent/events",
            f"/api/calendars/nonexistent/preferences", 
            f"/api/filtered-calendars/nonexistent",
            f"/api/filters/nonexistent"
        ]
        
        for endpoint in test_404_endpoints:
            response = self.client.get(endpoint, headers=self.test_user_headers)
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert isinstance(data["detail"], str)

    @pytest.mark.unit
    def test_health_endpoint_exists(self):
        """Test health endpoint is available (not in OpenAPI but required)"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestContractCompliance:
    """Test that actual implementation matches contract exactly"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = TestClient(app)
        self.test_user_headers = {"x-user-id": "test_user_123"}
    
    @pytest.mark.integration
    def test_future_events_only_returned(self):
        """Test that only future events are returned by default"""
        # This test would require real calendar data with past events
        # For now, we test the structure compliance
        calendar_data = {
            "name": "Future Events Test",
            "url": "https://example.com/future-test.ics"
        }
        create_response = self.client.post(
            "/api/calendars", 
            json=calendar_data, 
            headers=self.test_user_headers
        )
        calendar_id = create_response.json()["id"]
        
        response = self.client.get(
            f"/api/calendar/{calendar_id}/events", 
            headers=self.test_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Contract compliance: should return grouped events structure
        assert "events" in data
        assert isinstance(data["events"], dict)
        
        # Clean up
        self.client.delete(f"/api/calendars/{calendar_id}", headers=self.test_user_headers)
    
    @pytest.mark.integration
    def test_full_event_objects_returned(self):
        """Test that full event objects are returned, not just IDs"""
        calendar_data = {
            "name": "Full Events Test",
            "url": "https://example.com/full-events-test.ics"
        }
        create_response = self.client.post(
            "/api/calendars", 
            json=calendar_data, 
            headers=self.test_user_headers
        )
        calendar_id = create_response.json()["id"]
        
        response = self.client.get(
            f"/api/calendar/{calendar_id}/events", 
            headers=self.test_user_headers
        )
        
        data = response.json()
        
        # Check contract compliance: events should be full objects
        for event_type_name, event_type_data in data["events"].items():
            assert "events" in event_type_data
            events_list = event_type_data["events"]
            
            for event in events_list:
                # Must be full Event objects, not string IDs
                assert isinstance(event, dict), f"Event should be object, not {type(event)}"
                assert "id" in event, "Event must have id field"
                assert "title" in event, "Event must have title field"
                assert "start" in event, "Event must have start field"
                assert "end" in event, "Event must have end field"
        
        # Clean up
        self.client.delete(f"/api/calendars/{calendar_id}", headers=self.test_user_headers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])