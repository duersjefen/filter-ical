"""
Tests for domain request functionality.

Following TDD approach - these tests will initially fail until we implement
the optional password feature.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_domain_request_data():
    """Base domain request data for testing.

    Note: Using example.com URL which skips iCal validation in the endpoint.
    """
    return {
        "username": "test_user",
        "email": "test@example.com",
        "requested_domain_key": "test-calendar",
        "calendar_url": "https://example.com/calendar.ics",
        "description": "Test calendar for my soccer team with custom groups"
    }


class TestDomainRequestWithPassword:
    """Test domain request submission WITH password."""

    def test_create_domain_request_with_password(self, test_client: TestClient, sample_domain_request_data):
        """Test creating a domain request with a password."""
        data = {**sample_domain_request_data, "default_password": "SecurePass123"}

        response = test_client.post("/api/domain-requests", json=data)

        assert response.status_code == 201
        result = response.json()
        assert result["username"] == "test_user"
        assert result["email"] == "test@example.com"
        assert result["requested_domain_key"] == "test-calendar"
        assert result["status"] == "pending"
        assert "default_password" not in result  # Should not expose password in response

    def test_create_domain_request_with_short_password_fails(self, test_client: TestClient, sample_domain_request_data):
        """Test that passwords shorter than 4 characters are rejected."""
        data = {**sample_domain_request_data, "default_password": "abc"}

        response = test_client.post("/api/domain-requests", json=data)

        assert response.status_code == 422  # Validation error


class TestDomainRequestWithoutPassword:
    """Test domain request submission WITHOUT password (password-free access)."""

    def test_create_domain_request_without_password(self, test_client: TestClient, sample_domain_request_data):
        """Test creating a domain request without a password (password-free domain)."""
        # Do not include default_password field at all
        data = sample_domain_request_data

        response = test_client.post("/api/domain-requests", json=data)

        if response.status_code != 201:
            print(f"Error response: {response.status_code}")
            print(f"Error body: {response.json()}")

        assert response.status_code == 201
        result = response.json()
        assert result["username"] == "test_user"
        assert result["email"] == "test@example.com"
        assert result["requested_domain_key"] == "test-calendar"
        assert result["status"] == "pending"

    def test_create_domain_request_with_empty_password(self, test_client: TestClient, sample_domain_request_data):
        """Test creating a domain request with empty string password."""
        data = {**sample_domain_request_data, "default_password": ""}

        response = test_client.post("/api/domain-requests", json=data)

        # Empty string should be treated as no password
        assert response.status_code == 201

    def test_create_domain_request_with_null_password(self, test_client: TestClient, sample_domain_request_data):
        """Test creating a domain request with null password."""
        data = {**sample_domain_request_data, "default_password": None}

        response = test_client.post("/api/domain-requests", json=data)

        # Null should be accepted as no password
        assert response.status_code == 201


class TestDomainRequestValidation:
    """Test validation rules for domain requests."""

    def test_missing_required_fields_fails(self, test_client: TestClient):
        """Test that missing required fields are rejected."""
        data = {"username": "test_user"}

        response = test_client.post("/api/domain-requests", json=data)

        assert response.status_code == 422

    def test_invalid_email_fails(self, test_client: TestClient, sample_domain_request_data):
        """Test that invalid email format is rejected."""
        data = {**sample_domain_request_data, "email": "not-an-email"}

        response = test_client.post("/api/domain-requests", json=data)

        assert response.status_code == 422

    def test_invalid_domain_key_fails(self, test_client: TestClient, sample_domain_request_data):
        """Test that invalid domain key format is rejected."""
        data = {**sample_domain_request_data, "requested_domain_key": "Invalid_Key_With_Uppercase"}

        response = test_client.post("/api/domain-requests", json=data)

        assert response.status_code == 422

    def test_short_description_fails(self, test_client: TestClient, sample_domain_request_data):
        """Test that descriptions shorter than 10 characters are rejected."""
        data = {**sample_domain_request_data, "description": "Too short"}

        response = test_client.post("/api/domain-requests", json=data)

        assert response.status_code == 422
