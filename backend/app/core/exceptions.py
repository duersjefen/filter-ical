"""
Custom exceptions with RFC 7807 Problem Details support.

This module provides custom exception classes that work seamlessly with
the RFC 7807 error handling system. These exceptions carry error type
information and are converted to proper Problem Details responses by
the global exception handler.

Usage:
    from app.core.exceptions import ProblemDetailException
    from app.core.error_types import ErrorType

    # Raise an exception with a specific error type
    raise ProblemDetailException(
        error_type=ErrorType.CALENDAR_NOT_FOUND,
        detail="Calendar with ID 'abc123' does not exist"
    )

    # Or use the shorthand helper functions
    from app.core.exceptions import raise_not_found, raise_validation_error

    raise_not_found(ErrorType.CALENDAR_NOT_FOUND, "Calendar not found")
    raise_validation_error(ErrorType.GROUP_NAME_REQUIRED, "Group name is required")
"""

from typing import Optional, Any, Dict
from fastapi import HTTPException
from .error_types import ErrorTypeDefinition, ErrorType


class ProblemDetailException(HTTPException):
    """
    HTTPException subclass that carries RFC 7807 error type information.

    This exception includes the error type definition, which is used by the
    global exception handler to create proper RFC 7807 Problem Details responses.

    Attributes:
        error_type: The ErrorTypeDefinition for this error
        detail: Human-readable explanation
        instance: URI identifying the specific occurrence (optional)
        extensions: Additional domain-specific fields
    """

    def __init__(
        self,
        error_type: ErrorTypeDefinition,
        detail: Optional[str] = None,
        instance: Optional[str] = None,
        **extensions: Any
    ):
        """
        Create a ProblemDetailException.

        Args:
            error_type: The ErrorTypeDefinition for this error
            detail: Human-readable explanation (uses error type title if not provided)
            instance: URI identifying the specific occurrence
            **extensions: Additional domain-specific fields
        """
        self.error_type = error_type
        self.instance = instance
        self.extensions = extensions

        # Use provided detail or fall back to error type title
        detail_text = detail if detail else error_type.title

        # Initialize HTTPException with status code and detail
        super().__init__(
            status_code=error_type.status,
            detail=detail_text
        )

        # Store the error type slug in headers for the exception handler
        # This allows the handler to identify the specific error type
        if not self.headers:
            self.headers = {}
        self.headers["X-Error-Type"] = error_type.slug


# Helper functions for common error scenarios

def raise_not_found(error_type: ErrorTypeDefinition, detail: str, instance: Optional[str] = None) -> None:
    """
    Raise a 404 Not Found exception.

    Args:
        error_type: The ErrorTypeDefinition (should be a 404 error type)
        detail: Human-readable explanation
        instance: URI identifying the specific occurrence
    """
    raise ProblemDetailException(error_type=error_type, detail=detail, instance=instance)


def raise_validation_error(error_type: ErrorTypeDefinition, detail: str, field: Optional[str] = None) -> None:
    """
    Raise a 400 Validation Error exception.

    Args:
        error_type: The ErrorTypeDefinition (should be a 400 error type)
        detail: Human-readable explanation
        field: The field that failed validation (extension field)
    """
    extensions = {"field": field} if field else {}
    raise ProblemDetailException(error_type=error_type, detail=detail, **extensions)


def raise_conflict(error_type: ErrorTypeDefinition, detail: str, resource: Optional[str] = None) -> None:
    """
    Raise a 409 Conflict exception.

    Args:
        error_type: The ErrorTypeDefinition (should be a 409 error type)
        detail: Human-readable explanation
        resource: The resource that has a conflict (extension field)
    """
    extensions = {"resource": resource} if resource else {}
    raise ProblemDetailException(error_type=error_type, detail=detail, **extensions)


def raise_access_denied(error_type: ErrorTypeDefinition, detail: str, required_role: Optional[str] = None) -> None:
    """
    Raise a 403 Access Denied exception.

    Args:
        error_type: The ErrorTypeDefinition (should be a 403 error type)
        detail: Human-readable explanation
        required_role: The role required for access (extension field)
    """
    extensions = {"required_role": required_role} if required_role else {}
    raise ProblemDetailException(error_type=error_type, detail=detail, **extensions)


def raise_unauthorized(detail: str = "Authentication required") -> None:
    """
    Raise a 401 Unauthorized exception.

    Args:
        detail: Human-readable explanation
    """
    raise ProblemDetailException(error_type=ErrorType.AUTH_REQUIRED, detail=detail)


def raise_invalid_credentials(detail: str = "Invalid username or password") -> None:
    """
    Raise a 401 Invalid Credentials exception.

    Args:
        detail: Human-readable explanation
    """
    raise ProblemDetailException(error_type=ErrorType.INVALID_CREDENTIALS, detail=detail)


def raise_internal_error(detail: str, error_code: Optional[str] = None) -> None:
    """
    Raise a 500 Internal Server Error exception.

    Args:
        detail: Human-readable explanation
        error_code: Internal error code for tracking (extension field)
    """
    extensions = {"error_code": error_code} if error_code else {}
    raise ProblemDetailException(error_type=ErrorType.INTERNAL_SERVER_ERROR, detail=detail, **extensions)
