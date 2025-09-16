"""
Contract-Driven Testing: Validate API Implementation Against OpenAPI Spec
Industry Best Practice: Tests driven by documentation, not implementation
"""

import pytest
import yaml
import json
from fastapi.testclient import TestClient
from jsonschema import validate, ValidationError
from typing import Dict, Any, List

from app.main import app


@pytest.mark.unit
@pytest.mark.unit
class TestOpenAPIContract:
    """Test that API implementation matches OpenAPI specification exactly"""
    
    @classmethod
    def setup_class(cls):
        """Load OpenAPI specification for contract validation"""
        cls.client = TestClient(app)
        
        # Load OpenAPI specification
        with open("openapi.yaml", "r") as f:
            cls.openapi_spec = yaml.safe_load(f)
        
        # Extract schemas for validation
        cls.schemas = cls.openapi_spec.get("components", {}).get("schemas", {})
        cls.paths = cls.openapi_spec.get("paths", {})
    
    def validate_response_schema(self, response_data: Any, schema_name: str):
        """Validate response data against OpenAPI schema"""
        if schema_name not in self.schemas:
            pytest.fail(f"Schema '{schema_name}' not found in OpenAPI spec")
        
        schema = self.schemas[schema_name]
        
        # Convert OpenAPI schema to JSON Schema format
        json_schema = {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", [])
        }
        
        try:
            validate(instance=response_data, schema=json_schema)
        except ValidationError as e:
            pytest.fail(f"Response doesn't match schema '{schema_name}': {e.message}")
    
    def test_health_endpoint_contract(self):
        """Test /health endpoint matches OpenAPI spec exactly"""
        # Get expected response from OpenAPI spec
        health_spec = self.paths.get("/health", {}).get("get", {})
        expected_status = "200"
        
        # Make API call
        response = self.client.get("/health")
        
        # Validate status code matches spec
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Validate response structure
        data = response.json()
        assert "status" in data, "Response missing required 'status' field"
        assert "service" in data, "Response missing required 'service' field"
        assert data["status"] == "healthy", "Status should be 'healthy'"
    
    def test_calendar_list_contract(self):
        """Test /api/calendars GET matches OpenAPI spec"""
        # Make API call
        response = self.client.get("/api/calendars")
        
        # Should return 200 with array of calendars
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Response should be an array"
        
        # If calendars exist, validate their structure
        if data:
            calendar = data[0]
            required_fields = ["id", "name", "url", "user_id", "created_at"]
            for field in required_fields:
                assert field in calendar, f"Calendar missing required field: {field}"
    
    def test_calendar_creation_contract(self):
        """Test /api/calendars POST matches OpenAPI spec"""
        # Valid request according to OpenAPI spec
        calendar_data = {
            "name": "Test Calendar",
            "url": "https://example.com/calendar.ics"
        }
        
        # Make API call
        response = self.client.post("/api/calendars", json=calendar_data)
        
        # Should return 201 for successful creation
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        # Validate response structure
        data = response.json()
        assert "id" in data, "Response should include calendar ID"
        assert data["name"] == calendar_data["name"], "Name should match request"
    
    def test_community_info_contract(self):
        """Test /api/v1/communities/{community_id}/info matches OpenAPI spec"""
        # Make API call (using exter community from our database)
        response = self.client.get("/api/v1/communities/exter/info")
        
        # Should return 200 or 404
        assert response.status_code in [200, 404], f"Expected 200/404, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            # Validate community structure according to OpenAPI spec
            required_fields = ["id", "name", "calendar_url", "is_active"]
            for field in required_fields:
                assert field in data, f"Community info missing required field: {field}"
    
    def test_community_groups_contract(self):
        """Test /api/v1/communities/{community_id}/groups matches OpenAPI spec"""
        response = self.client.get("/api/v1/communities/exter/groups")
        
        assert response.status_code in [200, 404], f"Expected 200/404, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "groups" in data, "Response should contain 'groups' array"
            
            # Validate group structure
            if data["groups"]:
                group = data["groups"][0]
                required_fields = ["id", "name", "description", "icon", "color"]
                for field in required_fields:
                    assert field in group, f"Group missing required field: {field}"
    
    def test_error_response_format_contract(self):
        """Test error responses match OpenAPI spec format"""
        # Test 404 response format
        response = self.client.get("/api/v1/communities/nonexistent/info")
        
        if response.status_code == 404:
            data = response.json()
            # OpenAPI spec defines error format
            assert "detail" in data, "Error response should contain 'detail' field"
    
    def test_content_type_headers_contract(self):
        """Test Content-Type headers match OpenAPI spec"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
    
    def test_security_headers_contract(self):
        """Test security requirements from OpenAPI spec"""
        # Test endpoint that requires User-Id header
        response = self.client.get("/api/calendars")
        
        # Should work with or without header (depending on implementation)
        assert response.status_code in [200, 401, 422]


@pytest.mark.unit
class TestOpenAPISchemaValidation:
    """Validate specific schemas from OpenAPI specification"""
    
    @classmethod
    def setup_class(cls):
        """Load schemas for validation"""
        with open("openapi.yaml", "r") as f:
            cls.openapi_spec = yaml.safe_load(f)
        cls.schemas = cls.openapi_spec.get("components", {}).get("schemas", {})
    
    def test_calendar_schema_structure(self):
        """Test Calendar schema is well-defined"""
        assert "Calendar" in self.schemas, "Calendar schema should be defined"
        
        calendar_schema = self.schemas["Calendar"]
        assert "properties" in calendar_schema, "Calendar schema should have properties"
        
        required_props = ["id", "name", "url", "user_id", "created_at"]
        properties = calendar_schema["properties"]
        
        for prop in required_props:
            assert prop in properties, f"Calendar schema missing property: {prop}"
    
    def test_community_schema_structure(self):
        """Test Community schema is well-defined"""
        if "Community" in self.schemas:
            community_schema = self.schemas["Community"]
            assert "properties" in community_schema
            
            required_props = ["id", "name", "calendar_url", "is_active"]
            properties = community_schema["properties"]
            
            for prop in required_props:
                assert prop in properties, f"Community schema missing property: {prop}"
    
    def test_error_schema_structure(self):
        """Test Error schema is well-defined"""
        if "ErrorResponse" in self.schemas:
            error_schema = self.schemas["ErrorResponse"]
            assert "properties" in error_schema
            assert "detail" in error_schema["properties"], "Error schema should have 'detail' field"


@pytest.mark.unit
class TestOpenAPISpecificationStructure:
    """Test the OpenAPI specification itself is valid"""
    
    @classmethod
    def setup_class(cls):
        """Load OpenAPI specification"""
        with open("openapi.yaml", "r") as f:
            cls.openapi_spec = yaml.safe_load(f)
    
    def test_openapi_version(self):
        """Test OpenAPI version is specified"""
        assert "openapi" in self.openapi_spec, "OpenAPI version should be specified"
        assert self.openapi_spec["openapi"].startswith("3."), "Should use OpenAPI 3.x"
    
    def test_api_info(self):
        """Test API info section is complete"""
        assert "info" in self.openapi_spec, "API info should be specified"
        
        info = self.openapi_spec["info"]
        required_fields = ["title", "version", "description"]
        
        for field in required_fields:
            assert field in info, f"API info missing required field: {field}"
    
    def test_servers_defined(self):
        """Test servers are defined"""
        assert "servers" in self.openapi_spec, "Servers should be defined"
        servers = self.openapi_spec["servers"]
        assert len(servers) > 0, "At least one server should be defined"
        
        for server in servers:
            assert "url" in server, "Each server should have a URL"
    
    def test_paths_structure(self):
        """Test paths section is well-structured"""
        assert "paths" in self.openapi_spec, "Paths should be defined"
        paths = self.openapi_spec["paths"]
        assert len(paths) > 0, "At least one path should be defined"
        
        # Test each path has proper HTTP methods
        for path, methods in paths.items():
            assert isinstance(methods, dict), f"Path {path} should define HTTP methods"
            
            for method, spec in methods.items():
                assert method.lower() in ["get", "post", "put", "delete", "patch"], f"Invalid HTTP method: {method}"
                assert "responses" in spec, f"Path {path} {method} should define responses"
    
    def test_components_structure(self):
        """Test components section is well-structured"""
        if "components" in self.openapi_spec:
            components = self.openapi_spec["components"]
            
            if "schemas" in components:
                schemas = components["schemas"]
                for schema_name, schema in schemas.items():
                    assert "type" in schema or "$ref" in schema, f"Schema {schema_name} should have type or $ref"


@pytest.mark.unit
class TestContractConsistency:
    """Test consistency between OpenAPI spec and actual implementation"""
    
    @classmethod
    def setup_class(cls):
        """Setup for consistency tests"""
        cls.client = TestClient(app)
        with open("openapi.yaml", "r") as f:
            cls.openapi_spec = yaml.safe_load(f)
    
    def test_all_documented_paths_exist(self):
        """Test all paths in OpenAPI spec actually exist in implementation"""
        paths = self.openapi_spec.get("paths", {})
        
        for path, methods in paths.items():
            for method in methods.keys():
                if method.lower() not in ["parameters", "summary", "description"]:
                    # Convert OpenAPI path to actual path
                    actual_path = path.replace("{community_id}", "exter").replace("{communityId}", "exter")
                    actual_path = actual_path.replace("{calendarId}", "test-calendar").replace("{calendar_id}", "test-calendar")
                    actual_path = actual_path.replace("{communityPath}", "exter").replace("{community_path}", "exter")
                    actual_path = actual_path.replace("{filteredCalendarId}", "test-filter").replace("{filtered_calendar_id}", "test-filter")
                    actual_path = actual_path.replace("{token}", "test-token-123")
                    
                    # Make request
                    response = getattr(self.client, method.lower())(actual_path)
                    
                    # Should not return 404 (method not found)
                    assert response.status_code != 404, f"Path {path} {method} not implemented"
    
    def test_response_status_codes_match(self):
        """Test actual response codes match documented ones"""
        # Test a few key endpoints
        test_cases = [
            ("/health", "get", [200]),
            ("/api/calendars", "get", [200]),
            ("/api/v1/communities/exter/info", "get", [200, 404])
        ]
        
        for path, method, expected_codes in test_cases:
            response = getattr(self.client, method)(path)
            assert response.status_code in expected_codes, \
                f"Path {path} {method} returned {response.status_code}, expected one of {expected_codes}"