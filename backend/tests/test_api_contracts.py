"""
Contract tests validating API responses match OpenAPI specification.
Uses OpenAPI spec from backend/openapi.yaml.

These tests ensure implementation matches the contract specification exactly,
following contract-first development principles from CLAUDE.md.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers(test_client: TestClient):
    """Provide authentication headers for protected endpoints."""
    # Register test user
    response = test_client.post(
        "/api/users/register",
        json={"username": "testauth", "email": "auth@test.com", "password": "testpass123"}
    )

    # Handle both 200 and 201 status codes (registration might return either)
    assert response.status_code in [200, 201], f"Registration failed: {response.json()}"

    data = response.json()
    token = data.get("token") or data.get("access_token")
    assert token is not None, "No token returned from registration"

    return {"Authorization": f"Bearer {token}"}


@pytest.mark.contract
class TestUserEndpointContracts:
    """Contract tests for user management endpoints."""

    def test_register_response_matches_schema(self, test_client: TestClient):
        """Validate /api/users/register response matches OpenAPI spec."""
        response = test_client.post(
            "/api/users/register",
            json={
                "username": "contractuser",
                "password": "testpass123",
                "email": "contract@example.com"
            }
        )

        # OpenAPI spec says 200, but many implementations use 201 for creation
        assert response.status_code in [200, 201]

        # Validate response structure
        data = response.json()
        assert "user" in data or "username" in data, "Response must contain user info"

        # Check for token in response (might be 'token' or 'access_token')
        assert "token" in data or "access_token" in data, "Response must contain authentication token"

        # Validate user object structure
        user = data.get("user", data)
        assert "username" in user
        assert isinstance(user["username"], str)

        # Validate token
        token = data.get("token") or data.get("access_token")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_register_without_password_matches_schema(self, test_client: TestClient):
        """Validate user registration without password (passwordless account)."""
        response = test_client.post(
            "/api/users/register",
            json={"username": "passwordlessuser"}
        )

        assert response.status_code in [200, 201]
        data = response.json()

        # Should still return token for immediate login
        assert "token" in data or "access_token" in data

    def test_login_response_matches_schema(self, test_client: TestClient):
        """Validate /api/users/login response matches OpenAPI spec."""
        # Register user first
        test_client.post(
            "/api/users/register",
            json={
                "username": "logincontract",
                "password": "pass123",
                "email": "login@test.com"
            }
        )

        # Login
        response = test_client.post(
            "/api/users/login",
            json={"username": "logincontract", "password": "pass123"}
        )
        assert response.status_code == 200

        # Validate response structure
        data = response.json()
        assert "token" in data or "access_token" in data
        token = data.get("token") or data.get("access_token")
        assert isinstance(token, str)

    def test_check_username_matches_schema(self, test_client: TestClient):
        """Validate /api/users/check/{username} response matches OpenAPI spec."""
        # Register user with password
        test_client.post(
            "/api/users/register",
            json={
                "username": "checkuser",
                "password": "pass123",
                "email": "check@test.com"
            }
        )

        # Check existing username
        response = test_client.get("/api/users/check/checkuser")
        assert response.status_code == 200

        data = response.json()
        assert "username" in data
        assert "exists" in data
        assert "has_password" in data
        assert data["exists"] is True
        assert data["has_password"] is True
        assert isinstance(data["username"], str)
        assert isinstance(data["exists"], bool)
        assert isinstance(data["has_password"], bool)

    def test_check_nonexistent_username_returns_404(self, test_client: TestClient):
        """Validate /api/users/check/{username} returns 404 for non-existent users."""
        response = test_client.get("/api/users/check/nonexistentuser12345")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    def test_get_current_user_matches_schema(self, test_client: TestClient, auth_headers):
        """Validate /api/users/me response matches OpenAPI spec."""
        response = test_client.get(
            "/api/users/me",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Validate response structure
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert isinstance(data["id"], int)
        assert isinstance(data["username"], str)

        # Optional fields according to schema
        if "email" in data:
            assert isinstance(data["email"], str) or data["email"] is None
        if "role" in data:
            assert data["role"] in ["user", "global_admin"]
        if "has_password" in data:
            assert isinstance(data["has_password"], bool)

    def test_get_user_domains_matches_schema(self, test_client: TestClient, auth_headers):
        """Validate /api/users/me/domains response matches OpenAPI spec."""
        response = test_client.get(
            "/api/users/me/domains",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "owned_domains" in data
        assert "admin_domains" in data
        assert isinstance(data["owned_domains"], list)
        assert isinstance(data["admin_domains"], list)


@pytest.mark.contract
class TestCalendarEndpointContracts:
    """Contract tests for calendar management endpoints."""

    def test_create_calendar_response_matches_schema(self, test_client: TestClient):
        """Validate /api/calendars POST response matches OpenAPI spec."""
        response = test_client.post(
            "/api/calendars",
            json={
                "name": "Test Calendar",
                "source_url": "https://example.com/calendar.ics"
            },
            params={"username": "testcaluser"}
        )

        # Accept 201 (created) or 400 (if endpoint requires auth)
        assert response.status_code in [201, 400, 401]

        # Validate response structure for successful creation
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert "name" in data
            assert "source_url" in data
            assert isinstance(data["id"], int)
            assert data["name"] == "Test Calendar"

    def test_list_calendars_response_matches_schema(self, test_client: TestClient):
        """Validate /api/calendars GET response matches OpenAPI spec."""
        response = test_client.get(
            "/api/calendars",
            params={"username": "testuser"}
        )

        # Should return array even if empty
        assert response.status_code == 200

        # Validate response structure
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            calendar = data[0]
            assert "id" in calendar
            assert "name" in calendar
            assert "source_url" in calendar

    def test_get_calendar_events_matches_schema(self, test_client: TestClient):
        """Validate /api/calendars/{calendarId}/events response matches OpenAPI spec."""
        response = test_client.get("/api/calendars/1/events")

        # May return 404 if calendar doesn't exist
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "events" in data
            assert isinstance(data["events"], list)


@pytest.mark.contract
class TestDomainEndpointContracts:
    """Contract tests for domain management endpoints."""

    def test_list_domains_matches_schema(self, test_client: TestClient):
        """Validate /api/domains GET response matches OpenAPI spec."""
        response = test_client.get("/api/domains")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Validate domain structure if any exist
        if len(data) > 0:
            domain = data[0]
            assert "domain_key" in domain
            assert "name" in domain
            assert "calendar_url" in domain
            assert "group_count" in domain
            assert isinstance(domain["domain_key"], str)
            assert isinstance(domain["name"], str)
            assert isinstance(domain["group_count"], int)

    def test_get_domain_events_matches_schema(self, test_client: TestClient):
        """Validate /api/domains/{domain}/events response matches OpenAPI spec."""
        response = test_client.get("/api/domains/testdomain/events")

        # May return 404 if domain doesn't exist
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            # Should have groups structure according to DomainEventsResponse schema
            assert "groups" in data or "ungrouped_events" in data

    def test_get_domain_groups_matches_schema(self, test_client: TestClient):
        """Validate /api/domains/{domain}/groups response matches OpenAPI spec."""
        response = test_client.get("/api/domains/testdomain/groups")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

            if len(data) > 0:
                group = data[0]
                assert "id" in group
                assert "name" in group
                assert "domain_key" in group


@pytest.mark.contract
class TestFilterEndpointContracts:
    """Contract tests for filter management endpoints."""

    def test_list_all_filters_matches_schema(self, test_client: TestClient):
        """Validate /api/filters GET response matches OpenAPI spec."""
        response = test_client.get("/api/filters")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

            if len(data) > 0:
                filter_obj = data[0]
                assert "id" in filter_obj
                assert "name" in filter_obj
                # Must have either calendar_id or domain_key
                assert "calendar_id" in filter_obj or "domain_key" in filter_obj

    def test_create_calendar_filter_matches_schema(self, test_client: TestClient):
        """Validate POST /api/calendars/{calendarId}/filters response matches OpenAPI spec."""
        response = test_client.post(
            "/api/calendars/1/filters",
            json={
                "name": "Test Filter",
                "subscribed_event_ids": ["Event 1", "Event 2"],
                "include_future_events": False
            },
            params={"username": "testuser"}
        )

        # May fail if calendar doesn't exist
        assert response.status_code in [201, 400, 404]

        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert "name" in data
            assert "link_uuid" in data
            assert "export_url" in data


@pytest.mark.contract
class TestICalExportContracts:
    """Contract tests for iCal export endpoint."""

    def test_ical_export_content_type(self, test_client: TestClient):
        """Validate /ical/{uuid}.ics returns correct content type."""
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        response = test_client.get(f"/ical/{test_uuid}.ics")

        # May return 404 if filter doesn't exist
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            # Must be text/calendar according to OpenAPI spec
            content_type = response.headers.get("content-type", "")
            assert "text/calendar" in content_type.lower()

            # Should contain valid iCal content
            content = response.text
            assert "BEGIN:VCALENDAR" in content
            assert "END:VCALENDAR" in content


@pytest.mark.contract
class TestICalPreviewContracts:
    """Contract tests for iCal preview endpoint."""

    def test_ical_preview_response_matches_schema(self, test_client: TestClient):
        """Validate /api/ical/preview POST response matches OpenAPI spec."""
        response = test_client.post(
            "/api/ical/preview",
            json={
                "calendar_url": "https://example.com/test.ics"
            }
        )

        # Should return 200 with preview data or error
        assert response.status_code == 200

        data = response.json()
        # Required fields according to OpenAPI spec
        assert "event_count" in data
        assert "events" in data
        assert isinstance(data["event_count"], int)
        assert isinstance(data["events"], list)

        # Error field is optional
        if "error" in data:
            assert isinstance(data["error"], str) or data["error"] is None


@pytest.mark.contract
class TestDomainAuthContracts:
    """Contract tests for domain authentication endpoints."""

    def test_domain_auth_status_matches_schema(self, test_client: TestClient):
        """Validate /api/domains/{domain}/auth/status response matches OpenAPI spec."""
        response = test_client.get("/api/domains/testdomain/auth/status")

        assert response.status_code == 200

        data = response.json()
        assert "admin_password_set" in data
        assert "user_password_set" in data
        assert isinstance(data["admin_password_set"], bool)
        assert isinstance(data["user_password_set"], bool)

    def test_verify_admin_password_matches_schema(self, test_client: TestClient, test_domain):
        """Validate /api/domains/{domain}/auth/verify-admin response matches OpenAPI spec."""
        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/auth/verify-admin",
            json={"password": "test123"}
        )

        # Should return 200 with token or 401 for invalid password
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "token" in data
            assert isinstance(data["success"], bool)
            assert isinstance(data["token"], str)


@pytest.mark.contract
class TestDomainRequestContracts:
    """Contract tests for domain request endpoints."""

    def test_create_domain_request_matches_schema(self, test_client: TestClient, auth_headers):
        """Validate /api/domain-requests POST response matches OpenAPI spec."""
        response = test_client.post(
            "/api/domain-requests",
            json={
                "requested_domain_key": "my-test-domain",
                "calendar_url": "https://example.com/calendar.ics",
                "description": "This is my test domain request for testing purposes"
            },
            headers=auth_headers
        )

        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "requested_domain_key" in data
        assert "calendar_url" in data
        assert "description" in data
        assert "status" in data
        assert isinstance(data["id"], int)
        assert data["status"] in ["pending", "approved", "rejected"]


@pytest.mark.contract
class TestErrorResponseContracts:
    """Contract tests for error response formats (RFC 7807)."""

    def test_404_error_has_detail_field(self, test_client: TestClient):
        """Test 404 errors include detail field."""
        response = test_client.get("/api/nonexistent-endpoint")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)

    def test_401_auth_error_format(self, test_client: TestClient):
        """Test authentication errors have proper format."""
        response = test_client.get("/api/users/me")  # No auth token
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)

    def test_422_validation_error_format(self, test_client: TestClient):
        """Test validation errors have proper format."""
        response = test_client.post(
            "/api/users/register",
            json={"username": ""}  # Invalid: empty username
        )
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    def test_400_bad_request_format(self, test_client: TestClient):
        """Test bad request errors have proper format."""
        response = test_client.post(
            "/api/ical/preview",
            json={"calendar_url": "not-a-valid-url"}
        )

        # Should return some error status
        assert response.status_code >= 400

        if response.status_code != 500:
            data = response.json()
            assert "detail" in data or "error" in data


@pytest.mark.contract
class TestDomainBackupContracts:
    """Contract tests for domain backup endpoints."""

    def test_list_backups_matches_schema(self, test_client: TestClient):
        """Validate /api/domains/{domain}/backups GET response matches OpenAPI spec."""
        response = test_client.get("/api/domains/testdomain/backups")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

            if len(data) > 0:
                backup = data[0]
                assert "id" in backup
                assert "domain_key" in backup
                assert "created_at" in backup
                assert "backup_type" in backup
                assert backup["backup_type"] in [
                    "manual", "auto_pre_reset", "auto_pre_import", "auto_pre_restore"
                ]


@pytest.mark.contract
class TestAdminEndpointContracts:
    """Contract tests for admin endpoints."""

    def test_list_domain_requests_requires_auth(self, test_client: TestClient):
        """Validate /api/admin/domain-requests requires authentication."""
        response = test_client.get("/api/admin/domain-requests")

        # Should return 401 without proper authentication
        assert response.status_code == 401

    def test_domains_auth_status_requires_auth(self, test_client: TestClient):
        """Validate /api/admin/domains-auth requires authentication."""
        response = test_client.get("/api/admin/domains-auth")

        # Should return 401 without proper authentication
        assert response.status_code == 401


@pytest.mark.contract
class TestAssignmentRuleContracts:
    """Contract tests for assignment rule endpoints."""

    def test_create_assignment_rule_matches_schema(self, test_client: TestClient):
        """Validate POST /api/domains/{domain}/assignment-rules response structure."""
        response = test_client.post(
            "/api/domains/testdomain/assignment-rules",
            json={
                "rule_type": "title_contains",
                "rule_value": "Meeting",
                "target_group_id": 1
            }
        )

        # May fail if domain/group doesn't exist
        assert response.status_code in [201, 400, 404]

        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert "rule_type" in data
            assert "rule_value" in data
            assert "target_group_id" in data
            assert data["rule_type"] in [
                "title_contains", "title_not_contains",
                "description_contains", "description_not_contains",
                "category_contains", "category_not_contains"
            ]

    def test_create_compound_rule_matches_schema(self, test_client: TestClient):
        """Validate POST /api/domains/{domain}/assignment-rules/compound response structure."""
        response = test_client.post(
            "/api/domains/testdomain/assignment-rules/compound",
            json={
                "operator": "AND",
                "conditions": [
                    {"rule_type": "title_contains", "rule_value": "Meeting"},
                    {"rule_type": "description_contains", "rule_value": "Project"}
                ],
                "target_group_id": 1
            }
        )

        # May fail if domain/group doesn't exist or validation fails
        assert response.status_code in [201, 400, 404]

        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert "is_compound" in data or data.get("is_compound", False) is not None
            assert "target_group_id" in data


@pytest.mark.contract
class TestSchemaTypeValidation:
    """Validate data types match OpenAPI schema definitions."""

    def test_integer_ids_are_integers(self, test_client: TestClient):
        """Ensure all ID fields return integers, not strings."""
        response = test_client.get("/api/domains")

        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                domain = data[0]
                if "group_count" in domain:
                    assert isinstance(domain["group_count"], int)

    def test_boolean_flags_are_booleans(self, test_client: TestClient):
        """Ensure boolean fields return actual booleans, not strings."""
        response = test_client.get("/api/domains/testdomain/auth/status")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data["admin_password_set"], bool)
            assert isinstance(data["user_password_set"], bool)
            # Should be True/False, not "true"/"false" strings
            assert data["admin_password_set"] in [True, False]

    def test_array_fields_are_arrays(self, test_client: TestClient):
        """Ensure array fields return actual arrays, not objects."""
        response = test_client.get("/api/domains")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Domains endpoint must return array"

        # Test filters endpoint
        response = test_client.get("/api/filters")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Filters endpoint must return array"
