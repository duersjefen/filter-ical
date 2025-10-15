"""
Integration tests for calendar permissions management.

These tests verify the full workflow of calendar permission operations, including:
- Permission granting (user, admin levels)
- Permission revocation
- Permission listing
- Calendar owner implicit permissions
- Permission level enforcement
- Edge cases and error handling

Unlike contract tests, these test the actual business logic and data persistence.
"""

import pytest
from fastapi.testclient import TestClient


class TestPermissionGrantWorkflow:
    """Integration tests for granting calendar permissions."""

    @pytest.mark.future
    def test_grant_user_permission_to_user(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test granting user permission to a user."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="calowner", email="owner@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create a calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Shared Calendar", "source_url": "https://example.com/cal.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Grant user permission to test_user
        grant_response = test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "user"}
        )
        assert grant_response.status_code == 201
        assert grant_response.json()["success"] is True

        # Verify permission was granted
        list_response = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert list_response.status_code == 200
        permissions = list_response.json()["permissions"]

        user_perm = next((p for p in permissions if p["user"]["id"] == test_user.id), None)
        assert user_perm is not None
        assert user_perm["permission_level"] == "user"


    @pytest.mark.future
    def test_grant_admin_permission_to_user(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test granting admin permission to a user."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="calowner3", email="owner3@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create a calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Admin Calendar", "source_url": "https://example.com/cal3.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Grant admin permission to test_user
        grant_response = test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "admin"}
        )
        assert grant_response.status_code == 201

        # Verify permission level
        list_response = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        permissions = list_response.json()["permissions"]
        user_perm = next((p for p in permissions if p["user"]["id"] == test_user.id), None)
        assert user_perm["permission_level"] == "admin"

    @pytest.mark.future
    def test_grant_permission_to_multiple_users(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test granting permissions to multiple users for the same calendar."""
        from app.models.user import User

        # Create calendar owner and two other users
        owner = User(username="multiowner", email="multiowner@example.com")
        user2 = User(username="user2", email="user2@example.com")
        user3 = User(username="user3", email="user3@example.com")
        test_db.add_all([owner, user2, user3])
        test_db.commit()
        test_db.refresh(owner)
        test_db.refresh(user2)
        test_db.refresh(user3)

        # Create a calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Multi-User Calendar", "source_url": "https://example.com/multi.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Grant different permissions to different users
        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "user"}
        )
        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": user2.id, "permission_level": "admin"}
        )
        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": user3.id, "permission_level": "user"}
        )

        # Verify all permissions
        list_response = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        permissions = list_response.json()["permissions"]
        assert len(permissions) >= 3

        # Check each user has correct permission
        perm_map = {p["user"]["id"]: p["permission_level"] for p in permissions}
        assert perm_map[test_user.id] == "user"
        assert perm_map[user2.id] == "admin"
        assert perm_map[user3.id] == "user"

    @pytest.mark.future
    def test_cannot_grant_duplicate_permission(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test that granting duplicate permission returns 409."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="dupowner", email="dupowner@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create a calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Dup Calendar", "source_url": "https://example.com/dup.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Grant permission first time
        first_grant = test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "user"}
        )
        assert first_grant.status_code == 201

        # Try to grant again (should fail)
        second_grant = test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "admin"}
        )
        assert second_grant.status_code == 409


class TestPermissionRevokeWorkflow:
    """Integration tests for revoking calendar permissions."""

    @pytest.mark.future
    def test_revoke_permission_from_user(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test revoking a granted permission."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="revokeowner", email="revokeowner@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create calendar and grant permission
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Revoke Calendar", "source_url": "https://example.com/revoke.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "user"}
        )

        # Verify permission exists
        list_before = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert any(p["user"]["id"] == test_user.id for p in list_before.json()["permissions"])

        # Revoke permission
        revoke_response = test_client.delete(
            f"/admin/calendars/{calendar_id}/permissions/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert revoke_response.status_code == 200
        assert revoke_response.json()["success"] is True

        # Verify permission was removed
        list_after = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert not any(p["user"]["id"] == test_user.id for p in list_after.json()["permissions"])

    @pytest.mark.future
    def test_revoke_non_existent_permission_returns_404(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test that revoking non-existent permission returns 404."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="nopermowner", email="nopermowner@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create calendar (but don't grant permission)
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "No Perm Calendar", "source_url": "https://example.com/noperm.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Try to revoke non-existent permission
        revoke_response = test_client.delete(
            f"/admin/calendars/{calendar_id}/permissions/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert revoke_response.status_code == 404

    @pytest.mark.future
    def test_revoke_permission_is_idempotent(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test that revoking already revoked permission returns appropriate response."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="idempotowner", email="idempotowner@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create calendar and grant permission
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Idempot Calendar", "source_url": "https://example.com/idempot.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "user"}
        )

        # Revoke first time
        first_revoke = test_client.delete(
            f"/admin/calendars/{calendar_id}/permissions/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert first_revoke.status_code == 200

        # Revoke second time (should return 404)
        second_revoke = test_client.delete(
            f"/admin/calendars/{calendar_id}/permissions/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert second_revoke.status_code == 404


class TestCalendarOwnerPermissions:
    """Integration tests for calendar owner implicit permissions."""

    @pytest.mark.future
    def test_calendar_owner_has_implicit_admin_permission(self, test_client: TestClient, admin_token: str, test_db):
        """Test that calendar owner has implicit admin permission (not explicitly stored)."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="implicitowner", email="implicitowner@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create a calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Owner Calendar", "source_url": "https://example.com/owner.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # List permissions
        list_response = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        permissions = list_response.json()["permissions"]

        # Owner should not appear in explicit permissions list
        # (implicit permission via ownership, not stored in calendar_permissions table)
        assert not any(p["user"]["id"] == owner.id for p in permissions)

        # But calendar should show owner in calendar details
        calendar_details = list_response.json()["calendar"]
        assert calendar_details["owner"]["id"] == owner.id

    @pytest.mark.future
    def test_cannot_revoke_owner_permission(self, test_client: TestClient, admin_token: str, test_db):
        """Test that attempting to revoke owner's implicit permission fails."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="cannotrevoke", email="cannotrevoke@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create a calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Protected Calendar", "source_url": "https://example.com/protected.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Try to revoke owner's permission (should return 404 since no explicit permission exists)
        revoke_response = test_client.delete(
            f"/admin/calendars/{calendar_id}/permissions/{owner.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert revoke_response.status_code == 404


class TestPermissionListing:
    """Integration tests for listing calendar permissions."""

    @pytest.mark.future
    def test_list_permissions_for_calendar(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test listing all permissions for a calendar."""
        from app.models.user import User

        # Create calendar owner and users
        owner = User(username="listowner", email="listowner@example.com")
        user2 = User(username="listuser2", email="listuser2@example.com")
        user3 = User(username="listuser3", email="listuser3@example.com")
        test_db.add_all([owner, user2, user3])
        test_db.commit()
        test_db.refresh(owner)
        test_db.refresh(user2)
        test_db.refresh(user3)

        # Create calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "List Calendar", "source_url": "https://example.com/list.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Grant permissions to multiple users
        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "user"}
        )
        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": user2.id, "permission_level": "admin"}
        )
        test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": user3.id, "permission_level": "user"}
        )

        # List permissions
        list_response = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert list_response.status_code == 200
        data = list_response.json()

        # Verify structure
        assert "calendar" in data
        assert "permissions" in data
        assert len(data["permissions"]) == 3

        # Verify each permission includes granted_at timestamp
        for perm in data["permissions"]:
            assert "granted_at" in perm
            assert perm["granted_at"] is not None

    @pytest.mark.future
    def test_list_permissions_for_calendar_with_no_permissions(self, test_client: TestClient, admin_token: str, test_db):
        """Test listing permissions for calendar with no granted permissions."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="emptyowner", email="emptyowner@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create calendar (no permissions granted)
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Empty Calendar", "source_url": "https://example.com/empty.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # List permissions
        list_response = test_client.get(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert list_response.status_code == 200
        data = list_response.json()

        assert data["permissions"] == []
        assert data["calendar"]["id"] == calendar_id


class TestPermissionEdgeCases:
    """Integration tests for edge cases and error conditions."""

    @pytest.mark.future
    def test_grant_permission_to_non_existent_user(self, test_client: TestClient, admin_token: str, test_db):
        """Test granting permission to non-existent user returns 404."""
        from app.models.user import User

        # Create calendar owner
        owner = User(username="edgeowner", email="edgeowner@example.com")
        test_db.add(owner)
        test_db.commit()
        test_db.refresh(owner)

        # Create calendar
        calendar_response = test_client.post(
            "/api/calendars",
            json={"name": "Edge Calendar", "source_url": "https://example.com/edge.ics"},
            params={"username": owner.username}
        )
        calendar_id = calendar_response.json()["id"]

        # Try to grant permission to non-existent user
        grant_response = test_client.post(
            f"/admin/calendars/{calendar_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": 999999, "permission_level": "user"}
        )
        assert grant_response.status_code == 404

    @pytest.mark.future
    def test_grant_permission_for_non_existent_calendar(self, test_client: TestClient, admin_token: str, test_user):
        """Test granting permission for non-existent calendar returns 404."""
        grant_response = test_client.post(
            "/admin/calendars/999999/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "user"}
        )
        assert grant_response.status_code == 404

    @pytest.mark.future
    def test_list_permissions_for_non_existent_calendar(self, test_client: TestClient, admin_token: str):
        """Test listing permissions for non-existent calendar returns 404."""
        list_response = test_client.get(
            "/admin/calendars/999999/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert list_response.status_code == 404

    @pytest.mark.future
    def test_domain_calendar_permissions(self, test_client: TestClient, admin_token: str, test_user, test_db):
        """Test that permissions can be granted for domain calendars (type='domain')."""
        from app.models.calendar import Calendar
        from app.models.domain import Domain

        # Create domain
        domain = Domain(
            domain_key="testdomain",
            name="Test Domain",
            calendar_url="https://example.com/domain.ics",
            status="active"
        )
        test_db.add(domain)
        test_db.commit()
        test_db.refresh(domain)

        # Create domain calendar
        domain_calendar = Calendar(
            name="Domain Calendar",
            source_url="https://example.com/domain.ics",
            type="domain",
            user_id=None  # Domain calendars have no owner
        )
        test_db.add(domain_calendar)
        test_db.commit()
        test_db.refresh(domain_calendar)

        # Grant permission on domain calendar
        grant_response = test_client.post(
            f"/admin/calendars/{domain_calendar.id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"user_id": test_user.id, "permission_level": "user"}
        )
        assert grant_response.status_code == 201

        # Verify permission was granted
        list_response = test_client.get(
            f"/admin/calendars/{domain_calendar.id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        permissions = list_response.json()["permissions"]
        assert any(p["user"]["id"] == test_user.id for p in permissions)
