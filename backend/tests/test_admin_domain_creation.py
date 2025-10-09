"""
Tests for admin direct domain creation endpoint.

Following TDD: These tests define the expected behavior before implementation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.domain import Domain
from app.models.calendar import Calendar
from app.core.config import settings


class TestAdminDomainCreation:
    """Test suite for admin domain creation endpoint."""

    def test_create_domain_as_admin_success(self, test_client: TestClient, admin_token: str, test_db: Session):
        """Admin can create a domain directly without a request."""
        response = test_client.post(
            "/admin/domains",
            json={
                "domain_key": "test-admin-domain",
                "name": "Test Admin Domain",
                "calendar_url": "https://example.com/calendar.ics",
                "admin_password": "admin123",
                "user_password": "user123",
                "owner_username": None  # Optional - domain without owner
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["domain_key"] == "test-admin-domain"
        assert data["name"] == "Test Admin Domain"
        assert data["calendar_url"] == "https://example.com/calendar.ics"
        assert "domain_id" in data
        assert "calendar_id" in data

        # Verify domain was created in database
        domain = test_db.query(Domain).filter(Domain.domain_key == "test-admin-domain").first()
        assert domain is not None
        assert domain.name == "Test Admin Domain"
        assert domain.calendar_url == "https://example.com/calendar.ics"
        assert domain.status == "active"

    def test_create_domain_with_owner(self, test_client: TestClient, admin_token: str, test_user, test_db: Session):
        """Admin can create a domain and assign it to a specific user."""
        response = test_client.post(
            "/admin/domains",
            json={
                "domain_key": "owned-domain",
                "name": "Owned Domain",
                "calendar_url": "https://example.com/calendar.ics",
                "owner_username": test_user.username
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["domain_key"] == "owned-domain"
        assert data["owner_username"] == test_user.username

        # Verify domain owner
        domain = test_db.query(Domain).filter(Domain.domain_key == "owned-domain").first()
        assert domain.owner_id == test_user.id

    def test_create_domain_duplicate_key_fails(self, test_client: TestClient, admin_token: str, test_db: Session):
        """Cannot create a domain with a duplicate domain_key."""
        # Create first domain
        test_client.post(
            "/admin/domains",
            json={
                "domain_key": "duplicate-test",
                "name": "First Domain",
                "calendar_url": "https://example.com/calendar1.ics"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Try to create second domain with same key
        response = test_client.post(
            "/admin/domains",
            json={
                "domain_key": "duplicate-test",
                "name": "Second Domain",
                "calendar_url": "https://example.com/calendar2.ics"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_create_domain_invalid_domain_key(self, test_client: TestClient, admin_token: str):
        """Domain key must be lowercase alphanumeric with hyphens only."""
        response = test_client.post(
            "/admin/domains",
            json={
                "domain_key": "Invalid Domain!",
                "name": "Invalid Domain",
                "calendar_url": "https://example.com/calendar.ics"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 422  # Validation error

    def test_create_domain_requires_admin_auth(self, test_client: TestClient):
        """Regular users cannot create domains directly."""
        response = test_client.post(
            "/admin/domains",
            json={
                "domain_key": "unauthorized",
                "name": "Unauthorized Domain",
                "calendar_url": "https://example.com/calendar.ics"
            }
        )

        assert response.status_code == 401  # Unauthorized

    def test_create_domain_invalid_owner_username(self, test_client: TestClient, admin_token: str):
        """Cannot assign domain to non-existent user."""
        response = test_client.post(
            "/admin/domains",
            json={
                "domain_key": "bad-owner",
                "name": "Bad Owner Domain",
                "calendar_url": "https://example.com/calendar.ics",
                "owner_username": "nonexistent_user_12345"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404
        assert "user not found" in response.json()["detail"].lower()

    def test_create_domain_invalid_url(self, test_client: TestClient, admin_token: str):
        """Calendar URL must be a valid HTTP/HTTPS URL."""
        response = test_client.post(
            "/admin/domains",
            json={
                "domain_key": "bad-url",
                "name": "Bad URL Domain",
                "calendar_url": "not-a-url"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 422  # Validation error

    def test_create_domain_without_admin_password_fails(self, test_client: TestClient, admin_token: str):
        """Admin password is required."""
        response = test_client.post(
            "/admin/domains",
            json={
                "domain_key": "no-password-domain",
                "name": "No Password Domain",
                "calendar_url": "https://example.com/calendar.ics"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 422  # Validation error

    def test_create_domain_with_short_admin_password_fails(self, test_client: TestClient, admin_token: str):
        """Admin password must be at least 4 characters."""
        response = test_client.post(
            "/admin/domains",
            json={
                "domain_key": "short-pass-domain",
                "name": "Short Password Domain",
                "calendar_url": "https://example.com/calendar.ics",
                "admin_password": "abc"  # Only 3 chars
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 422  # Validation error
