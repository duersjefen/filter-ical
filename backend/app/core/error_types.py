"""
Error Type Registry for RFC 7807 Problem Details.

This module defines all error types used in the application with their
corresponding type URLs, HTTP status codes, and standard titles.

Each error type maps to:
- A unique URL that identifies the error type
- An HTTP status code
- A standard title for the error

The type URLs use the application domain to ensure uniqueness and
provide a location where documentation about the error could be hosted.

Organization:
- 400 Bad Request: Client input errors
- 401 Unauthorized: Authentication failures
- 403 Forbidden: Authorization/Permission errors
- 404 Not Found: Resource not found
- 409 Conflict: Resource conflicts
- 500 Internal Server Error: Server errors

Usage:
    from app.core.error_types import ErrorType

    problem = ErrorType.CALENDAR_NOT_FOUND.create_problem(
        detail="Calendar with ID 'abc123' does not exist",
        instance="/api/calendars/abc123"
    )
"""

from typing import Optional, Any
from dataclasses import dataclass
from .problem_details import ProblemDetail, create_problem_detail


# Base URL for error type documentation
ERROR_TYPE_BASE_URL = "https://filter-ical.de/errors"


@dataclass
class ErrorTypeDefinition:
    """
    Definition of an error type for RFC 7807 Problem Details.

    Attributes:
        slug: URL-friendly identifier (e.g., "calendar-not-found")
        title: Human-readable title
        status: HTTP status code
    """
    slug: str
    title: str
    status: int

    @property
    def type_url(self) -> str:
        """Get the full type URL for this error."""
        return f"{ERROR_TYPE_BASE_URL}/{self.slug}"

    def create_problem(
        self,
        detail: str,
        instance: Optional[str] = None,
        trace_id: Optional[str] = None,
        **extensions: Any
    ) -> ProblemDetail:
        """
        Create a ProblemDetail instance for this error type.

        Args:
            detail: Human-readable explanation specific to this occurrence
            instance: URI reference identifying the occurrence (optional)
            trace_id: Unique identifier for tracing (optional, auto-generated)
            **extensions: Additional domain-specific fields

        Returns:
            ProblemDetail instance
        """
        return create_problem_detail(
            type_url=self.type_url,
            title=self.title,
            status=self.status,
            detail=detail,
            instance=instance,
            trace_id=trace_id,
            **extensions
        )


class ErrorType:
    """
    Registry of all error types used in the application.

    Each error type is an ErrorTypeDefinition with a unique URL,
    standard title, and HTTP status code.
    """

    # ==========================================================================
    # 400 BAD REQUEST - Client input errors
    # ==========================================================================

    # Required fields
    CALENDAR_NAME_REQUIRED = ErrorTypeDefinition(
        slug="calendar-name-required",
        title="Calendar Name Required",
        status=400
    )

    SOURCE_URL_REQUIRED = ErrorTypeDefinition(
        slug="source-url-required",
        title="Source URL Required",
        status=400
    )

    FILTER_NAME_REQUIRED = ErrorTypeDefinition(
        slug="filter-name-required",
        title="Filter Name Required",
        status=400
    )

    GROUP_NAME_REQUIRED = ErrorTypeDefinition(
        slug="group-name-required",
        title="Group Name Required",
        status=400
    )

    USERNAME_REQUIRED = ErrorTypeDefinition(
        slug="username-required",
        title="Username Required",
        status=400
    )

    PASSWORD_REQUIRED = ErrorTypeDefinition(
        slug="password-required",
        title="Password Required",
        status=400
    )

    EMAIL_REQUIRED = ErrorTypeDefinition(
        slug="email-required",
        title="Email Required",
        status=400
    )

    # Field validation
    VALIDATION_ERROR = ErrorTypeDefinition(
        slug="validation-error",
        title="Validation Error",
        status=400
    )

    INVALID_FORMAT = ErrorTypeDefinition(
        slug="invalid-format",
        title="Invalid Format",
        status=400
    )

    INVALID_INPUT = ErrorTypeDefinition(
        slug="invalid-input",
        title="Invalid Input",
        status=400
    )

    # Password validation
    PASSWORD_TOO_SHORT = ErrorTypeDefinition(
        slug="password-too-short",
        title="Password Too Short",
        status=400
    )

    PASSWORD_MISMATCH = ErrorTypeDefinition(
        slug="password-mismatch",
        title="Password Mismatch",
        status=400
    )

    # Calendar validation
    CALENDAR_NO_EVENTS = ErrorTypeDefinition(
        slug="calendar-no-events",
        title="Calendar Has No Events",
        status=400
    )

    CALENDAR_URL_TIMEOUT = ErrorTypeDefinition(
        slug="calendar-url-timeout",
        title="Calendar URL Timeout",
        status=400
    )

    # File validation
    FILE_ENCODING_ERROR = ErrorTypeDefinition(
        slug="file-encoding-error",
        title="File Encoding Error",
        status=400
    )

    YAML_FORMAT_ERROR = ErrorTypeDefinition(
        slug="yaml-format-error",
        title="YAML Format Error",
        status=400
    )

    # Token validation
    TOKEN_EXPIRED = ErrorTypeDefinition(
        slug="token-expired",
        title="Token Expired",
        status=400
    )

    TOKEN_INVALID = ErrorTypeDefinition(
        slug="token-invalid",
        title="Invalid Token",
        status=400
    )

    # ==========================================================================
    # 401 UNAUTHORIZED - Authentication failures
    # ==========================================================================

    INVALID_CREDENTIALS = ErrorTypeDefinition(
        slug="invalid-credentials",
        title="Invalid Credentials",
        status=401
    )

    AUTH_REQUIRED = ErrorTypeDefinition(
        slug="auth-required",
        title="Authentication Required",
        status=401
    )

    INVALID_TOKEN = ErrorTypeDefinition(
        slug="invalid-token",
        title="Invalid Authentication Token",
        status=401
    )

    # ==========================================================================
    # 403 FORBIDDEN - Authorization/Permission errors
    # ==========================================================================

    ACCESS_DENIED = ErrorTypeDefinition(
        slug="access-denied",
        title="Access Denied",
        status=403
    )

    INSUFFICIENT_PERMISSIONS = ErrorTypeDefinition(
        slug="insufficient-permissions",
        title="Insufficient Permissions",
        status=403
    )

    ACCOUNT_LOCKED = ErrorTypeDefinition(
        slug="account-locked",
        title="Account Locked",
        status=403
    )

    # ==========================================================================
    # 404 NOT FOUND - Resource not found
    # ==========================================================================

    CALENDAR_NOT_FOUND = ErrorTypeDefinition(
        slug="calendar-not-found",
        title="Calendar Not Found",
        status=404
    )

    FILTER_NOT_FOUND = ErrorTypeDefinition(
        slug="filter-not-found",
        title="Filter Not Found",
        status=404
    )

    GROUP_NOT_FOUND = ErrorTypeDefinition(
        slug="group-not-found",
        title="Group Not Found",
        status=404
    )

    DOMAIN_NOT_FOUND = ErrorTypeDefinition(
        slug="domain-not-found",
        title="Domain Not Found",
        status=404
    )

    USER_NOT_FOUND = ErrorTypeDefinition(
        slug="user-not-found",
        title="User Not Found",
        status=404
    )

    DOMAIN_REQUEST_NOT_FOUND = ErrorTypeDefinition(
        slug="domain-request-not-found",
        title="Domain Request Not Found",
        status=404
    )

    BACKUP_NOT_FOUND = ErrorTypeDefinition(
        slug="backup-not-found",
        title="Backup Not Found",
        status=404
    )

    CONFIG_NOT_FOUND = ErrorTypeDefinition(
        slug="config-not-found",
        title="Configuration Not Found",
        status=404
    )

    RESOURCE_NOT_FOUND = ErrorTypeDefinition(
        slug="resource-not-found",
        title="Resource Not Found",
        status=404
    )

    # ==========================================================================
    # 409 CONFLICT - Resource conflicts
    # ==========================================================================

    USERNAME_TAKEN = ErrorTypeDefinition(
        slug="username-taken",
        title="Username Already Taken",
        status=409
    )

    EMAIL_TAKEN = ErrorTypeDefinition(
        slug="email-taken",
        title="Email Already Taken",
        status=409
    )

    DOMAIN_KEY_EXISTS = ErrorTypeDefinition(
        slug="domain-key-exists",
        title="Domain Key Already Exists",
        status=409
    )

    USER_ALREADY_ADMIN = ErrorTypeDefinition(
        slug="user-already-admin",
        title="User Already Admin",
        status=409
    )

    USER_NOT_ADMIN = ErrorTypeDefinition(
        slug="user-not-admin",
        title="User Not Admin",
        status=409
    )

    RESOURCE_CONFLICT = ErrorTypeDefinition(
        slug="resource-conflict",
        title="Resource Conflict",
        status=409
    )

    # ==========================================================================
    # 500 INTERNAL SERVER ERROR - Server errors
    # ==========================================================================

    INTERNAL_SERVER_ERROR = ErrorTypeDefinition(
        slug="internal-server-error",
        title="Internal Server Error",
        status=500
    )

    DATABASE_ERROR = ErrorTypeDefinition(
        slug="database-error",
        title="Database Error",
        status=500
    )

    EXPORT_ERROR = ErrorTypeDefinition(
        slug="export-error",
        title="Export Error",
        status=500
    )

    IMPORT_ERROR = ErrorTypeDefinition(
        slug="import-error",
        title="Import Error",
        status=500
    )

    CACHE_ERROR = ErrorTypeDefinition(
        slug="cache-error",
        title="Cache Error",
        status=500
    )

    SYNC_ERROR = ErrorTypeDefinition(
        slug="sync-error",
        title="Sync Error",
        status=500
    )

    BACKUP_ERROR = ErrorTypeDefinition(
        slug="backup-error",
        title="Backup Error",
        status=500
    )

    RESTORE_ERROR = ErrorTypeDefinition(
        slug="restore-error",
        title="Restore Error",
        status=500
    )


# Helper function to get error type from message pattern
def get_error_type_from_message(message: str, default_status: int = 500) -> ErrorTypeDefinition:
    """
    Get the appropriate error type based on the error message.

    This is a fallback for cases where the error type is not explicitly specified.
    It tries to match common error message patterns to error types.

    Args:
        message: The error message
        default_status: The default HTTP status code if no match is found

    Returns:
        ErrorTypeDefinition matching the message or a generic error type
    """
    message_lower = message.lower()

    # 404 Not Found patterns
    if "not found" in message_lower:
        if "calendar" in message_lower:
            return ErrorType.CALENDAR_NOT_FOUND
        elif "filter" in message_lower:
            return ErrorType.FILTER_NOT_FOUND
        elif "group" in message_lower:
            return ErrorType.GROUP_NOT_FOUND
        elif "domain" in message_lower:
            return ErrorType.DOMAIN_NOT_FOUND
        elif "user" in message_lower or "username" in message_lower:
            return ErrorType.USER_NOT_FOUND
        elif "backup" in message_lower:
            return ErrorType.BACKUP_NOT_FOUND
        elif "config" in message_lower:
            return ErrorType.CONFIG_NOT_FOUND
        else:
            return ErrorType.RESOURCE_NOT_FOUND

    # 409 Conflict patterns
    elif "already exists" in message_lower or "already taken" in message_lower:
        if "username" in message_lower:
            return ErrorType.USERNAME_TAKEN
        elif "email" in message_lower:
            return ErrorType.EMAIL_TAKEN
        elif "domain" in message_lower:
            return ErrorType.DOMAIN_KEY_EXISTS
        else:
            return ErrorType.RESOURCE_CONFLICT

    # 401 Authentication patterns (check before generic "invalid" pattern)
    elif "invalid credentials" in message_lower or "invalid username or password" in message_lower:
        return ErrorType.INVALID_CREDENTIALS
    elif "authentication required" in message_lower:
        return ErrorType.AUTH_REQUIRED
    elif "invalid token" in message_lower or "token has expired" in message_lower or "missing authentication" in message_lower:
        return ErrorType.AUTH_REQUIRED
    elif "invalid authentication method" in message_lower:
        return ErrorType.AUTH_REQUIRED

    # 400 Validation patterns
    elif "required" in message_lower:
        return ErrorType.VALIDATION_ERROR
    elif "invalid" in message_lower:
        return ErrorType.INVALID_INPUT
    elif "timeout" in message_lower:
        return ErrorType.CALENDAR_URL_TIMEOUT

    # 403 Authorization patterns
    elif "access denied" in message_lower or "permission" in message_lower:
        return ErrorType.ACCESS_DENIED
    elif "locked" in message_lower:
        return ErrorType.ACCOUNT_LOCKED

    # 500 Server error patterns
    elif "export" in message_lower:
        return ErrorType.EXPORT_ERROR
    elif "import" in message_lower:
        return ErrorType.IMPORT_ERROR
    elif "sync" in message_lower:
        return ErrorType.SYNC_ERROR
    elif "backup" in message_lower and "error" in message_lower:
        return ErrorType.BACKUP_ERROR
    elif "restore" in message_lower:
        return ErrorType.RESTORE_ERROR

    # Default based on status code
    if default_status == 404:
        return ErrorType.RESOURCE_NOT_FOUND
    elif default_status == 409:
        return ErrorType.RESOURCE_CONFLICT
    elif default_status == 400:
        return ErrorType.VALIDATION_ERROR
    elif default_status == 401:
        return ErrorType.AUTH_REQUIRED
    elif default_status == 403:
        return ErrorType.ACCESS_DENIED
    else:
        return ErrorType.INTERNAL_SERVER_ERROR
