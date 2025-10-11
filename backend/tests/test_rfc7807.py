"""
Tests for RFC 7807 Problem Details implementation.

This test suite validates:
1. ProblemDetail model structure and validation
2. ErrorType registry completeness
3. Global exception handler RFC 7807 compliance
4. ProblemDetailException functionality
5. End-to-end error response format
"""

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.models.problem_details import ProblemDetail, create_problem_detail
from app.core.error_types import ErrorType, ErrorTypeDefinition, get_error_type_from_message
from app.core.exceptions import (
    ProblemDetailException,
    raise_not_found,
    raise_validation_error,
    raise_conflict,
    raise_access_denied,
    raise_unauthorized,
    raise_invalid_credentials,
    raise_internal_error
)
from app.core.error_handlers import http_exception_handler


class TestProblemDetailModel:
    """Test suite for RFC 7807 ProblemDetail model."""

    def test_create_basic_problem_detail(self):
        """Test creating a basic ProblemDetail instance."""
        problem = ProblemDetail(
            type="https://filter-ical.de/errors/test-error",
            title="Test Error",
            status=400,
            detail="This is a test error"
        )

        assert problem.type == "https://filter-ical.de/errors/test-error"
        assert problem.title == "Test Error"
        assert problem.status == 400
        assert problem.detail == "This is a test error"
        assert problem.instance is None
        assert problem.trace_id is not None  # Auto-generated

    def test_problem_detail_with_instance(self):
        """Test ProblemDetail with instance URI."""
        problem = ProblemDetail(
            type="https://filter-ical.de/errors/not-found",
            title="Not Found",
            status=404,
            detail="Resource not found",
            instance="/api/calendars/123"
        )

        assert problem.instance == "/api/calendars/123"

    def test_problem_detail_with_trace_id(self):
        """Test ProblemDetail with custom trace ID."""
        custom_trace_id = "custom-trace-123"
        problem = ProblemDetail(
            type="https://filter-ical.de/errors/test",
            title="Test",
            status=400,
            detail="Test",
            trace_id=custom_trace_id
        )

        assert problem.trace_id == custom_trace_id

    def test_problem_detail_with_extensions(self):
        """Test ProblemDetail with extension fields."""
        problem = create_problem_detail(
            type_url="https://filter-ical.de/errors/validation-error",
            title="Validation Error",
            status=400,
            detail="Name is required",
            field="name",
            required=True
        )

        # Extension fields should be included
        problem_dict = problem.model_dump()
        assert problem_dict["field"] == "name"
        assert problem_dict["required"] is True

    def test_problem_detail_status_validation(self):
        """Test that status code is validated."""
        # Valid status codes
        for status in [100, 200, 400, 404, 500, 599]:
            problem = ProblemDetail(
                type="https://test.com/error",
                title="Test",
                status=status,
                detail="Test"
            )
            assert problem.status == status

    def test_create_problem_detail_factory(self):
        """Test the create_problem_detail factory function."""
        problem = create_problem_detail(
            type_url="https://filter-ical.de/errors/test",
            title="Test Error",
            status=400,
            detail="Test detail",
            instance="/api/test",
            custom_field="custom_value"
        )

        assert problem.type == "https://filter-ical.de/errors/test"
        assert problem.title == "Test Error"
        assert problem.status == 400
        assert problem.detail == "Test detail"
        assert problem.instance == "/api/test"
        assert problem.trace_id is not None

        # Check extension field
        problem_dict = problem.model_dump()
        assert problem_dict["custom_field"] == "custom_value"


class TestErrorTypeRegistry:
    """Test suite for ErrorType registry."""

    def test_error_type_definition_type_url(self):
        """Test that ErrorTypeDefinition generates correct type URLs."""
        error_def = ErrorTypeDefinition(
            slug="test-error",
            title="Test Error",
            status=400
        )

        assert error_def.type_url == "https://filter-ical.de/errors/test-error"

    def test_error_type_definition_create_problem(self):
        """Test creating a problem from an ErrorTypeDefinition."""
        error_def = ErrorTypeDefinition(
            slug="calendar-not-found",
            title="Calendar Not Found",
            status=404
        )

        problem = error_def.create_problem(
            detail="Calendar with ID 'abc123' not found",
            instance="/api/calendars/abc123"
        )

        assert problem.type == "https://filter-ical.de/errors/calendar-not-found"
        assert problem.title == "Calendar Not Found"
        assert problem.status == 404
        assert problem.detail == "Calendar with ID 'abc123' not found"
        assert problem.instance == "/api/calendars/abc123"

    def test_common_error_types_exist(self):
        """Test that commonly used error types exist in the registry."""
        # 400 Bad Request
        assert hasattr(ErrorType, "VALIDATION_ERROR")
        assert hasattr(ErrorType, "INVALID_INPUT")
        assert hasattr(ErrorType, "GROUP_NAME_REQUIRED")

        # 401 Unauthorized
        assert hasattr(ErrorType, "INVALID_CREDENTIALS")
        assert hasattr(ErrorType, "AUTH_REQUIRED")

        # 403 Forbidden
        assert hasattr(ErrorType, "ACCESS_DENIED")
        assert hasattr(ErrorType, "ACCOUNT_LOCKED")

        # 404 Not Found
        assert hasattr(ErrorType, "CALENDAR_NOT_FOUND")
        assert hasattr(ErrorType, "FILTER_NOT_FOUND")
        assert hasattr(ErrorType, "GROUP_NOT_FOUND")
        assert hasattr(ErrorType, "DOMAIN_NOT_FOUND")

        # 409 Conflict
        assert hasattr(ErrorType, "USERNAME_TAKEN")
        assert hasattr(ErrorType, "EMAIL_TAKEN")
        assert hasattr(ErrorType, "DOMAIN_KEY_EXISTS")

        # 500 Internal Server Error
        assert hasattr(ErrorType, "INTERNAL_SERVER_ERROR")
        assert hasattr(ErrorType, "EXPORT_ERROR")
        assert hasattr(ErrorType, "SYNC_ERROR")

    def test_error_type_status_codes(self):
        """Test that error types have correct status codes."""
        assert ErrorType.CALENDAR_NOT_FOUND.status == 404
        assert ErrorType.VALIDATION_ERROR.status == 400
        assert ErrorType.INVALID_CREDENTIALS.status == 401
        assert ErrorType.ACCESS_DENIED.status == 403
        assert ErrorType.USERNAME_TAKEN.status == 409
        assert ErrorType.INTERNAL_SERVER_ERROR.status == 500

    def test_get_error_type_from_message_not_found(self):
        """Test inferring error type from 'not found' messages."""
        test_cases = [
            ("Calendar not found", ErrorType.CALENDAR_NOT_FOUND),
            ("Filter not found", ErrorType.FILTER_NOT_FOUND),
            ("Group not found", ErrorType.GROUP_NOT_FOUND),
            ("Domain not found", ErrorType.DOMAIN_NOT_FOUND),
            ("User not found", ErrorType.USER_NOT_FOUND),
            ("Something not found", ErrorType.RESOURCE_NOT_FOUND),
        ]

        for message, expected_type in test_cases:
            error_type = get_error_type_from_message(message, 404)
            assert error_type == expected_type

    def test_get_error_type_from_message_conflict(self):
        """Test inferring error type from conflict messages."""
        test_cases = [
            ("Username already taken", ErrorType.USERNAME_TAKEN),
            ("Email already exists", ErrorType.EMAIL_TAKEN),
            ("Domain already exists", ErrorType.DOMAIN_KEY_EXISTS),
            ("Something already exists", ErrorType.RESOURCE_CONFLICT),
        ]

        for message, expected_type in test_cases:
            error_type = get_error_type_from_message(message, 409)
            assert error_type == expected_type

    def test_get_error_type_from_message_validation(self):
        """Test inferring error type from validation messages."""
        message = "Name is required"
        error_type = get_error_type_from_message(message, 400)
        assert error_type == ErrorType.VALIDATION_ERROR

    def test_get_error_type_from_message_authentication(self):
        """Test inferring error type from authentication messages."""
        test_cases = [
            ("Invalid username or password", ErrorType.INVALID_CREDENTIALS),
            ("Authentication required", ErrorType.AUTH_REQUIRED),
        ]

        for message, expected_type in test_cases:
            error_type = get_error_type_from_message(message, 401)
            assert error_type == expected_type

    def test_get_error_type_from_message_authorization(self):
        """Test inferring error type from authorization messages."""
        test_cases = [
            ("Access denied", ErrorType.ACCESS_DENIED),
            ("Insufficient permissions", ErrorType.ACCESS_DENIED),
            ("Account locked", ErrorType.ACCOUNT_LOCKED),
        ]

        for message, expected_type in test_cases:
            error_type = get_error_type_from_message(message, 403)
            assert error_type == expected_type


class TestProblemDetailException:
    """Test suite for ProblemDetailException."""

    def test_create_problem_detail_exception(self):
        """Test creating a ProblemDetailException."""
        exc = ProblemDetailException(
            error_type=ErrorType.CALENDAR_NOT_FOUND,
            detail="Calendar not found"
        )

        assert exc.status_code == 404
        assert exc.detail == "Calendar not found"
        assert exc.error_type == ErrorType.CALENDAR_NOT_FOUND

    def test_problem_detail_exception_with_extensions(self):
        """Test ProblemDetailException with extension fields."""
        exc = ProblemDetailException(
            error_type=ErrorType.VALIDATION_ERROR,
            detail="Name is required",
            field="name"
        )

        assert exc.extensions["field"] == "name"

    def test_raise_not_found_helper(self):
        """Test raise_not_found helper function."""
        with pytest.raises(ProblemDetailException) as exc_info:
            raise_not_found(
                ErrorType.CALENDAR_NOT_FOUND,
                "Calendar with ID 'abc' not found",
                "/api/calendars/abc"
            )

        exc = exc_info.value
        assert exc.status_code == 404
        assert exc.detail == "Calendar with ID 'abc' not found"
        assert exc.instance == "/api/calendars/abc"

    def test_raise_validation_error_helper(self):
        """Test raise_validation_error helper function."""
        with pytest.raises(ProblemDetailException) as exc_info:
            raise_validation_error(
                ErrorType.GROUP_NAME_REQUIRED,
                "Group name is required",
                field="name"
            )

        exc = exc_info.value
        assert exc.status_code == 400
        assert exc.detail == "Group name is required"
        assert exc.extensions["field"] == "name"

    def test_raise_conflict_helper(self):
        """Test raise_conflict helper function."""
        with pytest.raises(ProblemDetailException) as exc_info:
            raise_conflict(
                ErrorType.USERNAME_TAKEN,
                "Username 'john' already taken",
                resource="john"
            )

        exc = exc_info.value
        assert exc.status_code == 409
        assert exc.detail == "Username 'john' already taken"
        assert exc.extensions["resource"] == "john"

    def test_raise_access_denied_helper(self):
        """Test raise_access_denied helper function."""
        with pytest.raises(ProblemDetailException) as exc_info:
            raise_access_denied(
                ErrorType.ACCESS_DENIED,
                "Admin access required",
                required_role="admin"
            )

        exc = exc_info.value
        assert exc.status_code == 403
        assert exc.detail == "Admin access required"
        assert exc.extensions["required_role"] == "admin"

    def test_raise_unauthorized_helper(self):
        """Test raise_unauthorized helper function."""
        with pytest.raises(ProblemDetailException) as exc_info:
            raise_unauthorized()

        exc = exc_info.value
        assert exc.status_code == 401
        assert "Authentication required" in exc.detail

    def test_raise_invalid_credentials_helper(self):
        """Test raise_invalid_credentials helper function."""
        with pytest.raises(ProblemDetailException) as exc_info:
            raise_invalid_credentials()

        exc = exc_info.value
        assert exc.status_code == 401
        assert "Invalid username or password" in exc.detail

    def test_raise_internal_error_helper(self):
        """Test raise_internal_error helper function."""
        with pytest.raises(ProblemDetailException) as exc_info:
            raise_internal_error(
                "Database connection failed",
                error_code="DB001"
            )

        exc = exc_info.value
        assert exc.status_code == 500
        assert exc.detail == "Database connection failed"
        assert exc.extensions["error_code"] == "DB001"


class TestHttpExceptionHandler:
    """Test suite for the global HTTP exception handler."""

    @pytest.mark.asyncio
    async def test_handle_regular_http_exception(self):
        """Test handling regular HTTPException."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/calendars/123"

        exc = HTTPException(status_code=404, detail="Calendar not found")
        response = await http_exception_handler(request, exc)

        assert response.status_code == 404

        # Parse the response body
        import json
        body = json.loads(response.body.decode())

        # Verify RFC 7807 structure
        assert "type" in body
        assert "title" in body
        assert "status" in body
        assert "detail" in body
        assert "instance" in body
        assert "trace_id" in body

        # Verify values
        assert body["status"] == 404
        assert body["detail"] == "Calendar not found"
        assert body["instance"] == "/api/calendars/123"
        assert "calendar-not-found" in body["type"]

    @pytest.mark.asyncio
    async def test_handle_problem_detail_exception(self):
        """Test handling ProblemDetailException."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/groups/456"

        exc = ProblemDetailException(
            error_type=ErrorType.GROUP_NOT_FOUND,
            detail="Group with ID '456' not found",
            instance="/api/groups/456"
        )

        response = await http_exception_handler(request, exc)

        assert response.status_code == 404

        # Parse the response body
        import json
        body = json.loads(response.body.decode())

        # Verify RFC 7807 structure
        assert body["type"] == "https://filter-ical.de/errors/group-not-found"
        assert body["title"] == "Group Not Found"
        assert body["status"] == 404
        assert body["detail"] == "Group with ID '456' not found"
        assert body["instance"] == "/api/groups/456"
        assert "trace_id" in body

    @pytest.mark.asyncio
    async def test_handle_exception_with_extensions(self):
        """Test handling exception with extension fields."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"

        exc = ProblemDetailException(
            error_type=ErrorType.VALIDATION_ERROR,
            detail="Invalid email format",
            field="email",
            pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"
        )

        response = await http_exception_handler(request, exc)

        # Parse the response body
        import json
        body = json.loads(response.body.decode())

        # Verify extension fields are included
        assert body["field"] == "email"
        assert body["pattern"] == r"^[\w\.-]+@[\w\.-]+\.\w+$"

    @pytest.mark.asyncio
    async def test_different_status_codes(self):
        """Test handling various HTTP status codes."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"

        test_cases = [
            (400, "Bad request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not found"),
            (409, "Conflict"),
            (500, "Internal server error"),
        ]

        for status_code, detail in test_cases:
            exc = HTTPException(status_code=status_code, detail=detail)
            response = await http_exception_handler(request, exc)

            assert response.status_code == status_code

            import json
            body = json.loads(response.body.decode())
            assert body["status"] == status_code
            assert body["detail"] == detail


class TestRFC7807Compliance:
    """Test suite for RFC 7807 compliance."""

    def test_required_fields_present(self):
        """Test that all required RFC 7807 fields are present."""
        problem = ErrorType.CALENDAR_NOT_FOUND.create_problem(
            detail="Calendar not found",
            instance="/api/calendars/123"
        )

        problem_dict = problem.model_dump()

        # RFC 7807 required fields
        assert "type" in problem_dict
        assert "title" in problem_dict
        assert "status" in problem_dict
        assert "detail" in problem_dict

        # Optional fields (we always include these)
        assert "instance" in problem_dict
        assert "trace_id" in problem_dict

    def test_type_is_uri(self):
        """Test that type is a valid URI."""
        problem = ErrorType.CALENDAR_NOT_FOUND.create_problem(
            detail="Test"
        )

        assert problem.type.startswith("https://")
        assert "filter-ical.de/errors/" in problem.type

    def test_status_matches_http_status(self):
        """Test that status field matches HTTP status code."""
        test_cases = [
            (ErrorType.VALIDATION_ERROR, 400),
            (ErrorType.INVALID_CREDENTIALS, 401),
            (ErrorType.ACCESS_DENIED, 403),
            (ErrorType.CALENDAR_NOT_FOUND, 404),
            (ErrorType.USERNAME_TAKEN, 409),
            (ErrorType.INTERNAL_SERVER_ERROR, 500),
        ]

        for error_type, expected_status in test_cases:
            problem = error_type.create_problem(detail="Test")
            assert problem.status == expected_status

    def test_json_serialization(self):
        """Test that ProblemDetail can be serialized to JSON."""
        problem = ErrorType.CALENDAR_NOT_FOUND.create_problem(
            detail="Calendar not found",
            instance="/api/calendars/123",
            custom_field="custom_value"
        )

        # Should be able to convert to dict (for JSON serialization)
        problem_dict = problem.model_dump()
        assert isinstance(problem_dict, dict)

        # Verify it can be JSON serialized
        import json
        json_str = json.dumps(problem_dict)
        assert isinstance(json_str, str)

        # Verify it can be deserialized
        parsed = json.loads(json_str)
        assert parsed["type"] == problem.type
        assert parsed["detail"] == problem.detail
        assert parsed["custom_field"] == "custom_value"
