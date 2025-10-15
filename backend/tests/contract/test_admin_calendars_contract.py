"""
Contract tests for /admin/calendars/* endpoints.

These tests validate that the implementation matches the OpenAPI specification
exactly for calendar permissions management.

IMPORTANT: These tests assume the implementation is complete. Tests may fail
initially if the endpoints are not yet implemented by Agents 1 & 2.
"""

import pytest
from fastapi.testclient import TestClient


class TestAdminCalendarsListContract:
    """Contract tests for GET /admin/calendars endpoint."""

    @pytest.mark.future
    def test_list_calendars_requires_auth(self, test_client: TestClient):
        """Test that listing calendars requires authentication."""
        response = test_client.get("/admin/calendars")
        assert response.status_code == 401
        assert response.headers.get("content-type") == "application/json"

    @pytest.mark.future
    def test_list_calendars_response_structure(self, test_client: TestClient, admin_token: str):
        """Test that list calendars response matches OpenAPI schema."""
        response = test_client.get(
            "/admin/calendars",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        # Validate response structure per OpenAPI spec
        assert "calendars" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data

        assert isinstance(data["calendars"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["total_pages"], int)

    @pytest.mark.future
    def test_list_calendars_item_structure(self, test_client: TestClient, admin_token: str):
        """Test that calendar items match AdminCalendarResponse schema."""
        response = test_client.get(
            "/admin/calendars",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        if data["calendars"]:
            calendar = data["calendars"][0]
            # Required fields per OpenAPI spec
            assert "id" in calendar
            assert "name" in calendar
            assert "source_url" in calendar
            assert "type" in calendar
            assert "owner" in calendar  # nullable
            assert "domain" in calendar  # nullable
            assert "events_count" in calendar
            assert "last_fetched" in calendar  # nullable
            assert "created_at" in calendar

            # Validate types
            assert isinstance(calendar["id"], int)
            assert isinstance(calendar["name"], str)
            assert isinstance(calendar["source_url"], str)
            assert calendar["type"] in ["user", "domain"]
            assert isinstance(calendar["events_count"], int)

    @pytest.mark.future
    def test_list_calendars_pagination(self, test_client: TestClient, admin_token: str):
        """Test that pagination parameters work correctly."""
        response = test_client.get(
            "/admin/calendars?page=1&limit=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 10
        assert len(data["calendars"]) <= 10

    @pytest.mark.future
    def test_list_calendars_type_filter(self, test_client: TestClient, admin_token: str):
        """Test that type filter parameter works."""
        response = test_client.get(
            "/admin/calendars?type=user",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        # All returned calendars should have the filtered type
        for calendar in data["calendars"]:
            assert calendar["type"] == "user"


class TestCalendarPermissionsListContract:
    """Contract tests for GET /admin/calendars/{calendarId}/permissions endpoint."""

    @pytest.mark.future
    def test_list_permissions_requires_auth(self, test_client: TestClient):
        """Test that listing permissions requires authentication."""
        response = test_client.get("/admin/calendars/1/permissions")
        assert response.status_code == 401

    @pytest.mark.future
    def test_list_permissions_calendar_not_found(self, test_client: TestClient, admin_token: str):
        """Test that non-existent calendar returns 404."""
        response = test_client.get(
            "/admin/calendars/999999/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_list_permissions_response_structure(self, test_client: TestClient, admin_token: str, test_user):
        """Test that permissions response matches OpenAPI schema."""
        # Create a test calendar first
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        response = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        # Validate response structure per OpenAPI spec
        assert "calendar" in data
        assert "permissions" in data

        assert isinstance(data["permissions"], list)

        # Validate calendar structure
        assert "id" in data["calendar"]
        assert "name" in data["calendar"]
        assert "source_url" in data["calendar"]
        assert "type" in data["calendar"]

    @pytest.mark.future
    def test_list_permissions_item_structure(self, test_client: TestClient, admin_token: str, test_user):
        """Test that permission items match schema."""
        # Create calendar and grant permission
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Grant permission
        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "write"}
        )

        response = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        if data["permissions"]:
            perm = data["permissions"][0]
            # Required fields per OpenAPI spec
            assert "user" in perm
            assert "permission_level" in perm
            assert "granted_at" in perm

            # Validate user structure
            assert "id" in perm["user"]
            assert "username" in perm["user"]
            assert "email" in perm["user"]

            # Validate permission level
            assert perm["permission_level"] in ["read", "write", "admin"]


class TestCalendarPermissionsGrantContract:
    """Contract tests for POST /admin/calendars/{calendarId}/permissions endpoint."""

    @pytest.mark.future
    def test_grant_permission_requires_auth(self, test_client: TestClient):
        """Test that granting permission requires authentication."""
        response = test_client.post(
            "/admin/calendars/1/permissions",
            json={"user_id": 1, "permission_level": "read"}
        )
        assert response.status_code == 401

    @pytest.mark.future
    def test_grant_permission_calendar_not_found(self, test_client: TestClient, admin_token: str):
        """Test that non-existent calendar returns 404."""
        response = test_client.post(
            "/admin/calendars/999999/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": 1, "permission_level": "read"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_grant_permission_user_not_found(self, test_client: TestClient, admin_token: str, test_user):
        """Test that non-existent user returns 404."""
        # Create calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        response = test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": 999999, "permission_level": "read"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_grant_permission_success(self, test_client: TestClient, admin_token: str, test_user):
        """Test successful permission grant."""
        # Create calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        response = test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "write"}
        )
        assert response.status_code == 201
        data = response.json()

        assert data["success"] is True
        assert "message" in data
        assert isinstance(data["message"], str)

    @pytest.mark.future
    def test_grant_permission_invalid_level(self, test_client: TestClient, admin_token: str, test_user):
        """Test that invalid permission level returns 400."""
        # Create calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        response = test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "invalid"}
        )
        assert response.status_code == 400

    @pytest.mark.future
    def test_grant_permission_duplicate(self, test_client: TestClient, admin_token: str, test_user):
        """Test that granting duplicate permission returns 409."""
        # Create calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Grant permission first time
        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "write"}
        )

        # Try to grant again
        response = test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "read"}
        )
        assert response.status_code == 409

    @pytest.mark.future
    def test_grant_permission_levels(self, test_client: TestClient, admin_token: str, test_user):
        """Test that all permission levels are accepted."""
        for level in ["read", "write", "admin"]:
            # Create new calendar for each test
            calendar_response = test_client.post(
                "/api/calendars",
                json={"name": f"Test Calendar {level}", "source_url": "https://example.com/test.ics"},
                params={"username": test_user.username}
            )
            calendar_id = calendar_response.json()["id"]

            response = test_client.post(
                f"/admin/calendars/{calendar_id}/permissions",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"user_id": test_user.id, "permission_level": level}
            )
            assert response.status_code == 201


class TestCalendarPermissionsRevokeContract:
    """Contract tests for DELETE /admin/calendars/{calendarId}/permissions/{userId} endpoint."""

    @pytest.mark.future
    def test_revoke_permission_requires_auth(self, test_client: TestClient):
        """Test that revoking permission requires authentication."""
        response = test_client.delete("/admin/calendars/1/permissions/1")
        assert response.status_code == 401

    @pytest.mark.future
    def test_revoke_permission_calendar_not_found(self, test_client: TestClient, admin_token: str):
        """Test that non-existent calendar returns 404."""
        response = test_client.delete(
            "/admin/calendars/999999/permissions/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_revoke_permission_user_not_found(self, test_client: TestClient, admin_token: str, test_user):
        """Test that non-existent user returns 404."""
        # Create calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        response = test_client.delete(
            f"/admin/calendars/{calendar_id}/permissions/999999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_revoke_permission_not_granted(self, test_client: TestClient, admin_token: str, test_user):
        """Test that revoking non-existent permission returns 404."""
        # Create calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        response = test_client.delete(
            f"/admin/calendars/{calendar_id}/permissions/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_revoke_permission_success(self, test_client: TestClient, admin_token: str, test_user):
        """Test successful permission revocation."""
        # Create calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Grant permission first
        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "write"}
        )

        # Revoke permission
        response = test_client.delete(
            f"/admin/calendars/{calendar_id}/permissions/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data
        assert isinstance(data["message"], str)
