"""
Contract Compliance Tests

These tests validate that all API endpoints comply with the OpenAPI specification.
They ensure the backend-frontend contract is maintained and detect violations.
"""

import json
import pytest
import yaml
from pathlib import Path
from fastapi.testclient import TestClient
from jsonschema import validate, ValidationError
from prance import ResolvingParser

from app.main import app


class TestContractCompliance:
    """Test suite to validate API responses against OpenAPI contract"""
    
    @classmethod
    def setup_class(cls):
        """Load OpenAPI specification for contract validation"""
        cls.client = TestClient(app)
        
        # Load OpenAPI specification
        spec_path = Path(__file__).parent.parent / "openapi.yaml"
        if spec_path.exists():
            # Parse and resolve the specification
            parser = ResolvingParser(str(spec_path))
            cls.openapi_spec = parser.specification
            cls.schemas = cls.openapi_spec.get('components', {}).get('schemas', {})
        else:
            pytest.fail("OpenAPI specification not found")
    
    def _get_endpoint_response_schema(self, path: str, method: str, status_code: int):
        """Get the expected response schema for an endpoint"""
        paths = self.openapi_spec.get('paths', {})
        
        # Handle path parameters by trying exact match first, then pattern matching
        endpoint_spec = paths.get(path)
        if not endpoint_spec:
            # Try pattern matching for paths with parameters
            for pattern_path, spec in paths.items():
                if self._match_path_pattern(path, pattern_path):
                    endpoint_spec = spec
                    break
        
        if not endpoint_spec:
            return None
            
        method_spec = endpoint_spec.get(method.lower(), {})
        responses = method_spec.get('responses', {})
        
        # Check for exact status code or default
        status_str = str(status_code)
        if status_str in responses:
            response_spec = responses[status_str]
        elif 'default' in responses:
            response_spec = responses['default']
        else:
            return None
            
        # Get JSON schema
        content = response_spec.get('content', {})
        json_content = content.get('application/json', {})
        return json_content.get('schema', {})
    
    def _match_path_pattern(self, actual_path: str, pattern_path: str) -> bool:
        """Match actual path against OpenAPI path pattern with parameters"""
        actual_parts = actual_path.split('/')
        pattern_parts = pattern_path.split('/')
        
        if len(actual_parts) != len(pattern_parts):
            return False
            
        for actual, pattern in zip(actual_parts, pattern_parts):
            if pattern.startswith('{') and pattern.endswith('}'):
                # This is a path parameter, any value matches
                continue
            elif actual != pattern:
                # Literal path segment must match exactly
                return False
                
        return True
    
    def _validate_response_schema(self, response_data, schema, endpoint, method, status_code):
        """Validate response data against schema"""
        try:
            validate(instance=response_data, schema=schema)
            return True, None
        except ValidationError as e:
            error_msg = f"Schema validation failed for {method} {endpoint} (status {status_code}): {e.message}"
            return False, error_msg
    
    def test_calendars_endpoint_compliance(self):
        """Test /api/calendars endpoint contract compliance"""
        response = self.client.get("/api/calendars")
        
        # Should return 200
        assert response.status_code == 200
        
        # Validate against OpenAPI schema
        schema = self._get_endpoint_response_schema("/api/calendars", "GET", 200)
        assert schema is not None, "OpenAPI schema not found for GET /api/calendars"
        
        response_data = response.json()
        is_valid, error_msg = self._validate_response_schema(
            response_data, schema, "/api/calendars", "GET", 200
        )
        
        assert is_valid, f"Contract violation: {error_msg}"
    
    def test_calendar_events_endpoint_compliance(self):
        """Test /api/calendar/{calendar_id}/events endpoint contract compliance"""
        # Use a known calendar ID from the test data
        calendar_id = "cal_domain_exter"
        endpoint = f"/api/calendar/{calendar_id}/events"
        
        response = self.client.get(endpoint)
        
        # Should return 200
        assert response.status_code == 200
        
        # Validate against OpenAPI schema
        schema = self._get_endpoint_response_schema(
            f"/api/calendar/{calendar_id}/events", "GET", 200
        )
        assert schema is not None, f"OpenAPI schema not found for GET {endpoint}"
        
        response_data = response.json()
        is_valid, error_msg = self._validate_response_schema(
            response_data, schema, endpoint, "GET", 200
        )
        
        assert is_valid, f"Contract violation: {error_msg}"
    
    def test_calendar_groups_endpoint_compliance(self):
        """Test /api/calendar/{calendar_id}/groups endpoint contract compliance"""
        calendar_id = "cal_domain_exter"
        endpoint = f"/api/calendar/{calendar_id}/groups"
        
        response = self.client.get(endpoint)
        
        # Should return 200
        assert response.status_code == 200
        
        # Validate against OpenAPI schema
        schema = self._get_endpoint_response_schema(
            f"/api/calendar/{calendar_id}/groups", "GET", 200
        )
        assert schema is not None, f"OpenAPI schema not found for GET {endpoint}"
        
        response_data = response.json()
        is_valid, error_msg = self._validate_response_schema(
            response_data, schema, endpoint, "GET", 200
        )
        
        assert is_valid, f"Contract violation: {error_msg}"
    
    def test_event_date_format_compliance(self):
        """Test that all event dates are in ISO 8601 format with Z suffix"""
        calendar_id = "cal_domain_exter"
        response = self.client.get(f"/api/calendar/{calendar_id}/events")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that response has proper structure
        assert "events" in data, "Response missing 'events' property"
        
        # Check date formats in all events
        for event_type_name, event_type_data in data["events"].items():
            assert "events" in event_type_data, f"Event type '{event_type_name}' missing 'events' array"
            
            for event in event_type_data["events"]:
                # Check required Event schema fields
                assert "id" in event, f"Event missing 'id' field"
                assert "title" in event, f"Event missing 'title' field"
                assert "start" in event, f"Event missing 'start' field"
                assert "end" in event, f"Event missing 'end' field"
                assert "event_type" in event, f"Event missing 'event_type' field"
                
                # Check ISO 8601 format with Z suffix
                assert event["start"].endswith("Z"), f"Event start time not in ISO format: {event['start']}"
                assert event["end"].endswith("Z"), f"Event end time not in ISO format: {event['end']}"
                
                # Check date format validity
                try:
                    # Should be parseable as ISO format
                    from datetime import datetime
                    datetime.fromisoformat(event["start"].replace('Z', '+00:00'))
                    datetime.fromisoformat(event["end"].replace('Z', '+00:00'))
                except ValueError as e:
                    pytest.fail(f"Invalid date format in event {event['id']}: {e}")
    
    def test_all_endpoints_return_valid_json(self):
        """Test that all major endpoints return valid JSON"""
        endpoints = [
            "/api/calendars",
            "/api/calendar/cal_domain_exter/events",
            "/api/calendar/cal_domain_exter/groups",
            "/api/filtered-calendars",
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.status_code in [200, 404], f"Unexpected status for {endpoint}: {response.status_code}"
            
            if response.status_code == 200:
                try:
                    response.json()
                except json.JSONDecodeError:
                    pytest.fail(f"Endpoint {endpoint} returned invalid JSON")
    
    @pytest.mark.parametrize("endpoint,method", [
        ("/api/calendars", "GET"),
        ("/api/calendar/cal_domain_exter/events", "GET"),
        ("/api/calendar/cal_domain_exter/groups", "GET"),
    ])
    def test_response_content_type(self, endpoint, method):
        """Test that all endpoints return correct Content-Type header"""
        response = self.client.request(method, endpoint)
        
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert "application/json" in content_type, f"Wrong content type for {endpoint}: {content_type}"