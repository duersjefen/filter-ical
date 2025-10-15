"""
Contract tests for /admin/users/* endpoints.

These tests validate that the implementation matches the OpenAPI specification
exactly. They check request/response schemas, status codes, and API contracts.

IMPORTANT: These tests assume the implementation is complete. Tests may fail
initially if the endpoints are not yet implemented by Agents 1 & 2.
"""

import pytest
from fastapi.testclient import TestClient


class TestAdminUsersListContract:
    """Contract tests for GET /admin/users endpoint."""

    @pytest.mark.future
    def test_list_users_requires_auth(self, test_client: TestClient):
        """Test that listing users requires authentication."""
        response = test_client.get("/admin/users")
        assert response.status_code == 401
        assert response.headers.get("content-type") == "application/json"

    @pytest.mark.future
    def test_list_users_response_structure(self, test_client: TestClient, admin_token: str):
        """Test that list users response matches OpenAPI schema."""
        response = test_client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        # Validate response structure per OpenAPI spec
        assert "users" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data

        assert isinstance(data["users"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["total_pages"], int)

    @pytest.mark.future
    def test_list_users_item_structure(self, test_client: TestClient, admin_token: str):
        """Test that user items match AdminUserResponse schema."""
        response = test_client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        if data["users"]:
            user = data["users"][0]
            # Required fields per OpenAPI spec
            assert "id" in user
            assert "username" in user
            assert "email" in user  # nullable
            assert "role" in user
            assert "has_password" in user
            assert "account_locked" in user
            assert "failed_login_attempts" in user
            assert "created_at" in user
            assert "updated_at" in user
            assert "owned_domains_count" in user
            assert "admin_domains_count" in user
            assert "calendars_count" in user
            assert "filters_count" in user

            # Validate types
            assert isinstance(user["id"], int)
            assert isinstance(user["username"], str)
            assert user["email"] is None or isinstance(user["email"], str)
            assert user["role"] in ["user", "global_admin"]
            assert isinstance(user["has_password"], bool)
            assert isinstance(user["account_locked"], bool)
            assert isinstance(user["failed_login_attempts"], int)

    @pytest.mark.future
    def test_list_users_pagination_params(self, test_client: TestClient, admin_token: str):
        """Test that pagination parameters work correctly."""
        response = test_client.get(
            "/admin/users?page=1&limit=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 10
        assert len(data["users"]) <= 10

    @pytest.mark.future
    def test_list_users_search_param(self, test_client: TestClient, admin_token: str):
        """Test that search parameter is accepted."""
        response = test_client.get(
            "/admin/users?search=test",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.future
    def test_list_users_role_filter(self, test_client: TestClient, admin_token: str):
        """Test that role filter parameter works."""
        response = test_client.get(
            "/admin/users?role=user",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        # All returned users should have the filtered role
        for user in data["users"]:
            assert user["role"] == "user"


class TestAdminUserDetailContract:
    """Contract tests for GET /admin/users/{userId} endpoint."""

    @pytest.mark.future
    def test_get_user_requires_auth(self, test_client: TestClient):
        """Test that getting user details requires authentication."""
        response = test_client.get("/admin/users/1")
        assert response.status_code == 401

    @pytest.mark.future
    def test_get_user_not_found(self, test_client: TestClient, admin_token: str):
        """Test that non-existent user returns 404."""
        response = test_client.get(
            "/admin/users/999999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_get_user_response_structure(self, test_client: TestClient, admin_token: str, test_user):
        """Test that user detail response matches AdminUserDetailResponse schema."""
        response = test_client.get(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        user = response.json()

        # Required fields per OpenAPI spec
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "role" in user
        assert "has_password" in user
        assert "account_locked" in user
        assert "failed_login_attempts" in user
        assert "account_locked_until" in user  # nullable
        assert "created_at" in user
        assert "updated_at" in user
        assert "owned_domains" in user
        assert "admin_domains" in user
        assert "calendars" in user
        assert "filters" in user

        # Validate types
        assert isinstance(user["owned_domains"], list)
        assert isinstance(user["admin_domains"], list)
        assert isinstance(user["calendars"], list)
        assert isinstance(user["filters"], list)


class TestAdminUserUpdateContract:
    """Contract tests for PATCH /admin/users/{userId} endpoint."""

    @pytest.mark.future
    def test_update_user_requires_auth(self, test_client: TestClient):
        """Test that updating user requires authentication."""
        response = test_client.patch("/admin/users/1", json={"email": "new@example.com"})
        assert response.status_code == 401

    @pytest.mark.future
    def test_update_user_email(self, test_client: TestClient, admin_token: str, test_user):
        """Test updating user email."""
        response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"email": "newemail@example.com"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data
        assert "user" in data
        assert data["user"]["email"] == "newemail@example.com"

    @pytest.mark.future
    def test_update_user_password(self, test_client: TestClient, admin_token: str, test_user):
        """Test admin can set user password without current password."""
        response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"password": "NewSecurePass123"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["user"]["has_password"] is True

    @pytest.mark.future
    def test_update_user_role(self, test_client: TestClient, admin_token: str, test_user):
        """Test updating user role."""
        response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "global_admin"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["user"]["role"] == "global_admin"

    @pytest.mark.future
    def test_update_user_invalid_role(self, test_client: TestClient, admin_token: str, test_user):
        """Test that invalid role returns 400."""
        response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "invalid_role"}
        )
        assert response.status_code == 400

    @pytest.mark.future
    def test_update_user_not_found(self, test_client: TestClient, admin_token: str):
        """Test that updating non-existent user returns 404."""
        response = test_client.patch(
            "/admin/users/999999",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"email": "test@example.com"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_update_user_duplicate_email(self, test_client: TestClient, admin_token: str, test_user):
        """Test that duplicate email returns 409."""
        # Create another user first
        response = test_client.post(
            "/api/users/register",
            json={"username": "otheruser", "email": "other@example.com"}
        )

        # Try to update test_user to use the same email
        response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"email": "other@example.com"}
        )
        assert response.status_code == 409


class TestAdminUserDeleteContract:
    """Contract tests for DELETE /admin/users/{userId} endpoint."""

    @pytest.mark.future
    def test_delete_user_requires_auth(self, test_client: TestClient):
        """Test that deleting user requires authentication."""
        response = test_client.delete("/admin/users/1")
        assert response.status_code == 401

    @pytest.mark.future
    def test_delete_user_not_found(self, test_client: TestClient, admin_token: str):
        """Test that deleting non-existent user returns 404."""
        response = test_client.delete(
            "/admin/users/999999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_delete_user_success(self, test_client: TestClient, admin_token: str, test_user):
        """Test successful user deletion."""
        response = test_client.delete(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data
        assert "deleted_calendars" in data
        assert "deleted_domains" in data

        assert isinstance(data["deleted_calendars"], int)
        assert isinstance(data["deleted_domains"], int)

    @pytest.mark.future
    def test_delete_user_cascade_calendars(self, test_client: TestClient, admin_token: str, test_user):
        """Test deleting user with cascade delete calendars option."""
        response = test_client.delete(
            f"/admin/users/{test_user.id}?delete_calendars=true",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.future
    def test_delete_user_cascade_domains(self, test_client: TestClient, admin_token: str, test_user):
        """Test deleting user with cascade delete domains option."""
        response = test_client.delete(
            f"/admin/users/{test_user.id}?delete_domains=true",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


class TestAdminUserUnlockContract:
    """Contract tests for POST /admin/users/{userId}/unlock endpoint."""

    @pytest.mark.future
    def test_unlock_user_requires_auth(self, test_client: TestClient):
        """Test that unlocking user requires authentication."""
        response = test_client.post("/admin/users/1/unlock")
        assert response.status_code == 401

    @pytest.mark.future
    def test_unlock_user_not_found(self, test_client: TestClient, admin_token: str):
        """Test that unlocking non-existent user returns 404."""
        response = test_client.post(
            "/admin/users/999999/unlock",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    @pytest.mark.future
    def test_unlock_user_success(self, test_client: TestClient, admin_token: str, test_user):
        """Test successful account unlock."""
        response = test_client.post(
            f"/admin/users/{test_user.id}/unlock",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data
        assert isinstance(data["message"], str)
