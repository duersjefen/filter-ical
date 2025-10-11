"""
Integration tests for RFC 7807 Problem Details in actual API responses.

This test suite validates that the RFC 7807 error format is correctly
applied to real API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_application


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    app = create_application()
    return TestClient(app)


class TestRFC7807Integration:
    """Integration tests for RFC 7807 error responses."""

    def test_404_error_returns_rfc7807_format(self, client):
        """Test that 404 errors return RFC 7807 format."""
        # Try to access a non-existent domain
        response = client.get("/api/domains/nonexistent-domain-key-12345")

        # Should return 404
        assert response.status_code == 404

        # Parse JSON response
        data = response.json()

        # Verify RFC 7807 structure
        assert "type" in data
        assert "title" in data
        assert "status" in data
        assert "detail" in data
        assert "instance" in data
        assert "trace_id" in data

        # Verify values
        assert data["status"] == 404
        assert "https://filter-ical.de/errors/" in data["type"]
        assert data["instance"] == "/api/domains/nonexistent-domain-key-12345"

    def test_401_error_returns_rfc7807_format(self, client):
        """Test that 401 authentication errors return RFC 7807 format."""
        # Try to create a calendar without authentication (requires auth)
        response = client.post(
            "/api/calendars",
            json={"name": "Test", "source_url": "https://example.com/cal.ics"}
        )

        # Should return 401 (authentication required)
        assert response.status_code == 401

        # Parse JSON response
        data = response.json()

        # Verify RFC 7807 structure
        assert "type" in data
        assert "title" in data
        assert "status" in data
        assert "detail" in data
        assert "trace_id" in data

        # Verify values
        assert data["status"] == 401
        assert "https://filter-ical.de/errors/" in data["type"]

    def test_health_check_success_not_rfc7807(self, client):
        """Test that successful responses are not in RFC 7807 format."""
        # Health check should return success response
        response = client.get("/health")

        # Should return 200
        assert response.status_code == 200

        # Parse JSON response
        data = response.json()

        # Should NOT be RFC 7807 format (no error)
        assert "status" in data
        assert data["status"] == "healthy"
        assert "type" not in data  # RFC 7807 field
        assert "trace_id" not in data  # RFC 7807 field

    def test_trace_id_is_uuid(self, client):
        """Test that trace_id is a valid UUID."""
        import uuid

        # Generate an error
        response = client.get("/api/domains/nonexistent-domain-key-12345")
        data = response.json()

        # Verify trace_id is a valid UUID
        try:
            uuid.UUID(data["trace_id"])
        except ValueError:
            pytest.fail(f"trace_id '{data['trace_id']}' is not a valid UUID")

    def test_different_endpoints_same_format(self, client):
        """Test that different endpoints return consistent RFC 7807 format."""
        # Test multiple endpoints that should return errors
        test_cases = [
            ("/api/domains/nonexistent-domain-1", 404),
            ("/api/domains/nonexistent-domain-2", 404),
        ]

        for endpoint, expected_status in test_cases:
            response = client.get(endpoint)
            assert response.status_code == expected_status

            data = response.json()

            # All should have RFC 7807 structure
            assert "type" in data
            assert "title" in data
            assert "status" in data
            assert "detail" in data
            assert "instance" in data
            assert "trace_id" in data

            # Status should match HTTP status
            assert data["status"] == expected_status

    def test_type_url_is_absolute(self, client):
        """Test that type URL is an absolute URI."""
        response = client.get("/api/domains/nonexistent-domain-key-12345")
        data = response.json()

        # Type should be an absolute URL
        assert data["type"].startswith("https://")
        assert "filter-ical.de" in data["type"]

    def test_instance_matches_request_path(self, client):
        """Test that instance field matches the request path."""
        path = "/api/domains/nonexistent-domain-key-12345"
        response = client.get(path)
        data = response.json()

        # Instance should match the request path
        assert data["instance"] == path

    def test_error_content_type_is_json(self, client):
        """Test that error responses have correct Content-Type."""
        response = client.get("/api/domains/nonexistent-domain-key-12345")

        # Content-Type should be application/json
        assert "application/json" in response.headers["content-type"]
