"""
Integration tests for admin user management functionality.

These tests verify the full workflow of user CRUD operations, including:
- User creation via registration
- User listing with search and pagination
- User updates (email, password, role)
- Account locking and unlocking
- Cascade deletion with calendars and domains

Unlike contract tests, these test the actual business logic and data persistence.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone


class TestUserCRUDWorkflow:
    """Integration tests for full user CRUD workflow."""

    @pytest.mark.future
    def test_create_list_update_delete_user(self, test_client: TestClient, admin_token: str):
        """Test complete user lifecycle: create -> list -> update -> delete."""
        # 1. Create user via registration
        register_response = test_client.post(
            "/api/users/register",
            json={
                "username": "integrationuser",
                "email": "integration@example.com",
                "password": "SecurePass123"
            }
        )
        assert register_response.status_code == 200
        user_data = register_response.json()
        user_id = user_data["user"]["id"]

        # 2. List users and verify new user appears
        list_response = test_client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert list_response.status_code == 200
        users = list_response.json()["users"]
        assert any(u["username"] == "integrationuser" for u in users)

        # 3. Update user email
        update_response = test_client.patch(
            f"/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"email": "newemail@example.com"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["user"]["email"] == "newemail@example.com"

        # 4. Delete user
        delete_response = test_client.delete(
            f"/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200

        # 5. Verify user is deleted
        get_response = test_client.get(
            f"/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.status_code == 404

    @pytest.mark.future
    def test_user_detail_includes_related_data(self, test_client: TestClient, admin_token: str, test_user):
        """Test that user detail endpoint includes calendars, domains, and filters."""
        # Create a calendar for the user
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        assert calendar_response.status_code == 201

        # Get user details
        response = test_client.get(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        user = response.json()

        # Verify calendars are included
        assert "calendars" in user
        assert len(user["calendars"]) >= 1
        assert any(c["name"] == "Test Calendar" for c in user["calendars"])

        # Verify owned_domains and admin_domains are included
        assert "owned_domains" in user
        assert "admin_domains" in user
        assert isinstance(user["owned_domains"], list)
        assert isinstance(user["admin_domains"], list)


class TestUserSearchAndPagination:
    """Integration tests for user search and pagination."""

    @pytest.mark.future
    def test_search_users_by_username(self, test_client: TestClient, admin_token: str):
        """Test searching users by username."""
        # Create users with different usernames
        test_client.post("/api/users/register", json={"username": "alice123"})
        test_client.post("/api/users/register", json={"username": "bob456"})
        test_client.post("/api/users/register", json={"username": "alice789"})

        # Search for "alice"
        response = test_client.get(
            "/admin/users?search=alice",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        users = response.json()["users"]

        # Should return users with "alice" in username
        assert len(users) >= 2
        for user in users:
            if user["username"].startswith("alice"):
                assert "alice" in user["username"]

    @pytest.mark.future
    def test_search_users_by_email(self, test_client: TestClient, admin_token: str):
        """Test searching users by email."""
        # Create users with different emails
        test_client.post(
            "/api/users/register",
            json={"username": "user1", "email": "alice@example.com"}
        )
        test_client.post(
            "/api/users/register",
            json={"username": "user2", "email": "bob@test.com"}
        )

        # Search for "example.com"
        response = test_client.get(
            "/admin/users?search=example.com",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        users = response.json()["users"]

        # Should return users with "example.com" in email
        assert any("example.com" in (u.get("email") or "") for u in users)

    @pytest.mark.future
    def test_pagination_works_correctly(self, test_client: TestClient, admin_token: str):
        """Test that pagination returns correct number of users."""
        # Create multiple users
        for i in range(25):
            test_client.post("/api/users/register", json={"username": f"pageuser{i}"})

        # Get first page with limit 10
        page1 = test_client.get(
            "/admin/users?page=1&limit=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert page1.status_code == 200
        page1_data = page1.json()
        assert page1_data["page"] == 1
        assert page1_data["limit"] == 10
        assert len(page1_data["users"]) <= 10
        assert page1_data["total_pages"] >= 3  # At least 25 users / 10 per page

        # Get second page
        page2 = test_client.get(
            "/admin/users?page=2&limit=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert page2.status_code == 200
        page2_data = page2.json()
        assert page2_data["page"] == 2
        assert len(page2_data["users"]) <= 10

        # Verify different users on each page
        page1_ids = {u["id"] for u in page1_data["users"]}
        page2_ids = {u["id"] for u in page2_data["users"]}
        assert page1_ids.isdisjoint(page2_ids)  # No overlap

    @pytest.mark.future
    def test_filter_users_by_role(self, test_client: TestClient, admin_token: str, test_user):
        """Test filtering users by role."""
        # Promote test_user to global_admin
        test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "global_admin"}
        )

        # Filter for global_admin users
        response = test_client.get(
            "/admin/users?role=global_admin",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        users = response.json()["users"]

        # All users should be global_admin
        for user in users:
            assert user["role"] == "global_admin"

        # Verify test_user is in the results
        assert any(u["id"] == test_user.id for u in users)


class TestRoleManagement:
    """Integration tests for user role changes."""

    @pytest.mark.future
    def test_promote_user_to_global_admin(self, test_client: TestClient, admin_token: str, test_user):
        """Test promoting a regular user to global_admin."""
        # Verify initial role
        get_response = test_client.get(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.json()["role"] == "user"

        # Promote to global_admin
        update_response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "global_admin"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["user"]["role"] == "global_admin"

        # Verify role persisted
        get_response = test_client.get(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.json()["role"] == "global_admin"

    @pytest.mark.future
    def test_demote_global_admin_to_user(self, test_client: TestClient, admin_token: str, test_user):
        """Test demoting a global_admin to regular user."""
        # First promote to global_admin
        test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "global_admin"}
        )

        # Then demote back to user
        update_response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "user"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["user"]["role"] == "user"


class TestAccountLockingUnlocking:
    """Integration tests for account locking and unlocking."""

    @pytest.mark.future
    def test_unlock_locked_account(self, test_client: TestClient, admin_token: str, test_db):
        """Test unlocking an account that's been locked due to failed login attempts."""
        from app.models.user import User
        from datetime import timezone

        # Create a locked user
        locked_user = User(
            username="lockeduser",
            email="locked@example.com",
            password_hash="hashed",
            failed_login_attempts=5,
            account_locked_until=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        test_db.add(locked_user)
        test_db.commit()
        test_db.refresh(locked_user)

        # Verify account is locked
        get_response = test_client.get(
            f"/admin/users/{locked_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        user_data = get_response.json()
        assert user_data["account_locked"] is True
        assert user_data["failed_login_attempts"] == 5

        # Unlock the account
        unlock_response = test_client.post(
            f"/admin/users/{locked_user.id}/unlock",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert unlock_response.status_code == 200
        assert unlock_response.json()["success"] is True

        # Verify account is unlocked
        get_response = test_client.get(
            f"/admin/users/{locked_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        user_data = get_response.json()
        assert user_data["account_locked"] is False
        assert user_data["failed_login_attempts"] == 0
        assert user_data["account_locked_until"] is None

    @pytest.mark.future
    def test_unlock_non_locked_account_is_idempotent(self, test_client: TestClient, admin_token: str, test_user):
        """Test that unlocking an already unlocked account is safe."""
        # Unlock account that's not locked
        response = test_client.post(
            f"/admin/users/{test_user.id}/unlock",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True


class TestCascadeDeletion:
    """Integration tests for cascade deletion of user data."""

    @pytest.mark.future
    def test_delete_user_orphans_calendars_by_default(self, test_client: TestClient, admin_token: str, test_user):
        """Test that deleting user orphans calendars (doesn't delete them) by default."""
        # Create a calendar for the user
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "source_url": "https://example.com/test.ics"},
            params={"username": test_user.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Delete user without cascade
        delete_response = test_client.delete(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["deleted_calendars"] == 0  # Not deleted

        # Verify calendar still exists but is orphaned
        calendar_check = test_client.get("/admin/calendars", headers={"Authorization": f"Bearer {admin_token}"})
        calendars = calendar_check.json()["calendars"]
        orphaned_calendar = next((c for c in calendars if c["id"] == calendar_id), None)
        assert orphaned_calendar is not None
        assert orphaned_calendar["owner"] is None  # Orphaned

    @pytest.mark.future
    def test_delete_user_cascades_calendars(self, test_client: TestClient, admin_token: str, test_user):
        """Test that deleting user with delete_calendars=true cascades deletion."""
        # Create calendars for the user
        for i in range(3):
            test_client.post(
                "/api/calendars",
                json={"name": f"Calendar {i}", "source_url": f"https://example.com/cal{i}.ics"},
                params={"username": test_user.username}
            )

        # Delete user with cascade
        delete_response = test_client.delete(
            f"/admin/users/{test_user.id}?delete_calendars=true",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["deleted_calendars"] >= 3

    @pytest.mark.future
    def test_delete_user_with_owned_domains(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test deleting user who owns domains."""
        from app.models.domain import Domain

        # Create a domain owned by the user
        domain = Domain(
            domain_key="testdomain",
            name="Test Domain",
            calendar_url="https://example.com/cal.ics",
            owner_id=test_user.id,
            status="active"
        )
        test_db.add(domain)
        test_db.commit()

        # Delete user without cascade domains
        delete_response = test_client.delete(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["deleted_domains"] == 0  # Domain ownership removed, not deleted

        # Verify domain still exists but is orphaned
        test_db.refresh(domain)
        assert domain.owner_id is None

    @pytest.mark.future
    def test_delete_user_cascades_domains(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test that deleting user with delete_domains=true cascades deletion."""
        from app.models.domain import Domain

        # Create a domain owned by the user
        domain = Domain(
            domain_key="testdomain2",
            name="Test Domain 2",
            calendar_url="https://example.com/cal2.ics",
            owner_id=test_user.id,
            status="active"
        )
        test_db.add(domain)
        test_db.commit()
        domain_id = domain.id

        # Delete user with cascade domains
        delete_response = test_client.delete(
            f"/admin/users/{test_user.id}?delete_domains=true",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["deleted_domains"] >= 1

        # Verify domain is deleted
        test_db.expire_all()
        deleted_domain = test_db.query(Domain).filter(Domain.id == domain_id).first()
        assert deleted_domain is None


class TestPasswordManagement:
    """Integration tests for admin password management."""

    @pytest.mark.future
    def test_admin_can_set_user_password(self, test_client: TestClient, admin_token: str, test_user):
        """Test that admin can set user password without current password."""
        # User initially has no password
        get_response = test_client.get(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        initial_has_password = get_response.json()["has_password"]

        # Admin sets password
        update_response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"password": "NewSecurePass123"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["user"]["has_password"] is True

    @pytest.mark.future
    def test_admin_can_change_user_password(self, test_client: TestClient, admin_token: str, test_user):
        """Test that admin can change existing password."""
        # Set initial password
        test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"password": "InitialPass123"}
        )

        # Change to new password (admin bypass, no current password needed)
        update_response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"password": "ChangedPass456"}
        )
        assert update_response.status_code == 200

        # Verify user can login with new password
        login_response = test_client.post(
            "/api/users/login",
            json={"username": test_user.username, "password": "ChangedPass456"}
        )
        assert login_response.status_code == 200


class TestEmailManagement:
    """Integration tests for email updates."""

    @pytest.mark.future
    def test_update_user_email(self, test_client: TestClient, admin_token: str, test_user):
        """Test updating user email address."""
        update_response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"email": "updated@example.com"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["user"]["email"] == "updated@example.com"

        # Verify email persisted
        get_response = test_client.get(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.json()["email"] == "updated@example.com"

    @pytest.mark.future
    def test_update_email_duplicate_returns_409(self, test_client: TestClient, admin_token: str, test_user):
        """Test that updating to an existing email returns 409."""
        # Create another user with an email
        test_client.post(
            "/api/users/register",
            json={"username": "otheruser", "email": "taken@example.com"}
        )

        # Try to update test_user to use the same email
        update_response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"email": "taken@example.com"}
        )
        assert update_response.status_code == 409

    @pytest.mark.future
    def test_clear_user_email(self, test_client: TestClient, admin_token: str, test_user):
        """Test setting user email to null."""
        update_response = test_client.patch(
            f"/admin/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"email": None}
        )
        assert update_response.status_code == 200
        assert update_response.json()["user"]["email"] is None
