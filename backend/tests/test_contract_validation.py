"""
Contract validation tests - ensure API responses match OpenAPI specification exactly
Industry standard practice: All API responses must be validated against contract

Current API: Public-first access with simplified event type filtering
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

    # ===============================================
    # Calendar Management Tests
    # ===============================================
    
    @pytest.mark.unit
    def test_get_calendars_contract(self):
        """Test GET /api/calendars conforms to contract"""
        response = self.client.get("/api/calendars")
        
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
        
        response = self.client.post("/api/calendars", json=calendar_data)
        
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
        self.client.delete(f"/api/calendars/{data['id']}")
    
    @pytest.mark.unit
    def test_delete_calendar_contract(self):
        """Test DELETE /api/calendars/{calendar_id} conforms to contract"""
        # Create a calendar first
        calendar_data = {
            "name": "Test Delete Calendar",
            "url": "https://example.com/test-delete.ics"
        }
        create_response = self.client.post("/api/calendars", json=calendar_data)
        calendar_id = create_response.json()["id"]
        
        # Delete the calendar
        response = self.client.delete(f"/api/calendars/{calendar_id}")
        
        assert response.status_code == 204  # Per OpenAPI spec
        # 204 responses should have no content
        assert response.content == b''

    # ===============================================
    # Calendar Data Tests
    # ===============================================
    
    @pytest.mark.unit
    def test_get_calendar_events_contract(self):
        """Test GET /api/calendar/{calendar_id}/events conforms to contract"""
        # Create a calendar first
        calendar_data = {
            "name": "Test Events Calendar",
            "url": "https://example.com/test-events.ics"
        }
        create_response = self.client.post("/api/calendars", json=calendar_data)
        calendar_id = create_response.json()["id"]
        
        # Get events (will be empty but should follow contract)
        response = self.client.get(f"/api/calendar/{calendar_id}/events")
        
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
                assert "event_type" in event
                # description and location are optional
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response(
            "/api/calendar/{calendar_id}/events", 
            "GET", 
            200, 
            data
        )
        
        # Clean up
        self.client.delete(f"/api/calendars/{calendar_id}")

    @pytest.mark.unit
    def test_get_calendar_raw_events_contract(self):
        """Test GET /api/calendar/{calendar_id}/raw-events conforms to contract"""
        # Create a calendar first
        calendar_data = {
            "name": "Test Raw Events Calendar",
            "url": "https://example.com/test-raw-events.ics"
        }
        create_response = self.client.post("/api/calendars", json=calendar_data)
        calendar_id = create_response.json()["id"]
        
        # Get raw events
        response = self.client.get(f"/api/calendar/{calendar_id}/raw-events")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate contract-compliant structure
        assert "events" in data
        assert isinstance(data["events"], list)
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response(
            "/api/calendar/{calendar_id}/raw-events", 
            "GET", 
            200, 
            data
        )
        
        # Clean up
        self.client.delete(f"/api/calendars/{calendar_id}")

    # ===============================================
    # iCal Generation Tests  
    # ===============================================
    
    @pytest.mark.unit
    def test_generate_ical_contract(self):
        """Test POST /api/calendar/{calendar_id}/generate conforms to contract"""
        # Create a calendar first
        calendar_data = {"name": "iCal Generation Test", "url": "https://example.com/generate.ics"}
        create_response = self.client.post("/api/calendars", json=calendar_data)
        calendar_id = create_response.json()["id"]
        
        # Generate iCal content with correct format per OpenAPI spec
        generation_data = {
            "selected_event_types": ["Work", "Meeting"],  # Updated to match OpenAPI
            "filter_mode": "include"
        }
        
        response = self.client.post(
            f"/api/calendar/{calendar_id}/generate", 
            json=generation_data
        )
        
        assert response.status_code == 200
        # Should return text/calendar content type
        assert "text/calendar" in response.headers.get("content-type", "")
        
        # Basic iCal format validation
        content = response.text
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content
        
        # Clean up
        self.client.delete(f"/api/calendars/{calendar_id}")

    # ===============================================
    # Domain Configuration Tests
    # ===============================================
    
    @pytest.mark.unit
    def test_get_domains_contract(self):
        """Test GET /api/domains conforms to contract"""
        response = self.client.get("/api/domains")
        assert response.status_code == 200
        data = response.json()
        
        # Validate contract-compliant structure
        assert "domains" in data
        assert isinstance(data["domains"], list)
        
        # Each domain should have proper structure
        for domain in data["domains"]:
            assert "id" in domain
            assert "name" in domain  
            assert "calendar_url" in domain
        
        # Validate against OpenAPI schema
        self.validate_endpoint_response("/api/domains", "GET", 200, data)

    @pytest.mark.unit
    def test_get_domain_by_id_contract(self):
        """Test GET /api/domains/{domain_id} conforms to contract"""
        # First get available domains
        domains_response = self.client.get("/api/domains")
        domains_data = domains_response.json()
        
        if domains_data["domains"]:
            # Test with first available domain
            domain_id = domains_data["domains"][0]["id"]
            response = self.client.get(f"/api/domains/{domain_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate required fields per contract
            assert "id" in data
            assert "name" in data
            assert "calendar_url" in data
            
            # Validate against OpenAPI schema (use template path)
            self.validate_endpoint_response("/api/domains/{domain_id}", "GET", 200, data)

    # ===============================================
    # Public Calendar Access Tests
    # ===============================================
    
    @pytest.mark.unit  
    def test_public_calendar_access_contract(self):
        """Test GET /cal/{token} conforms to contract (404 expected for invalid token)"""
        # Test with invalid token - should return 404
        response = self.client.get("/cal/invalid_token")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)

    # ===============================================
    # Error Response Tests
    # ===============================================
    
    @pytest.mark.unit
    def test_error_responses_contract(self):
        """Test error responses conform to contract"""
        # Test 404 Not Found
        response = self.client.get("/api/calendar/nonexistent/events")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        
        # Test 400 Bad Request - invalid calendar data
        invalid_calendar = {"name": ""}  # Missing required fields
        response = self.client.post("/api/calendars", json=invalid_calendar)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)

    # ===============================================
    # Health Check Tests
    # ===============================================
    
    @pytest.mark.unit
    def test_health_endpoint_exists(self):
        """Test health endpoint is available (not in OpenAPI but required)"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])