"""
RFC 7807 Problem Details for HTTP APIs.

This module implements the IETF RFC 7807 standard for machine-readable
error responses in HTTP APIs.

RFC 7807 defines a standard format for error responses that includes:
- type: A URI reference that identifies the problem type
- title: A short, human-readable summary of the problem type
- status: The HTTP status code
- detail: A human-readable explanation specific to this occurrence
- instance: A URI reference that identifies the specific occurrence
- trace_id: (Extension) A unique identifier for tracing this error

Reference: https://datatracker.ietf.org/doc/html/rfc7807

Benefits:
- Machine-readable error types for automated error handling
- Consistent error format across all API endpoints
- Better debugging with trace IDs
- Internationalization-ready (type URLs can resolve to localized docs)
- Industry standard (used by GitHub, Stripe, Twilio, etc.)

Example Response:
{
    "type": "https://filter-ical.de/errors/calendar-not-found",
    "title": "Calendar Not Found",
    "status": 404,
    "detail": "Calendar with ID 'abc123' does not exist",
    "instance": "/api/calendars/abc123",
    "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class ProblemDetail(BaseModel):
    """
    RFC 7807 Problem Details for HTTP APIs.

    This is the standard error response format for all API errors.

    Attributes:
        type: URI reference identifying the problem type
        title: Short human-readable summary
        status: HTTP status code
        detail: Human-readable explanation specific to this occurrence
        instance: URI reference identifying the specific occurrence
        trace_id: Unique identifier for tracing (extension field)
    """

    type: str = Field(
        ...,
        description="A URI reference that identifies the problem type",
        example="https://filter-ical.de/errors/calendar-not-found"
    )

    title: str = Field(
        ...,
        description="A short, human-readable summary of the problem type",
        example="Calendar Not Found"
    )

    status: int = Field(
        ...,
        description="The HTTP status code",
        ge=100,
        le=599,
        example=404
    )

    detail: str = Field(
        ...,
        description="A human-readable explanation specific to this occurrence",
        example="Calendar with ID 'abc123' does not exist"
    )

    instance: Optional[str] = Field(
        None,
        description="A URI reference that identifies the specific occurrence",
        example="/api/calendars/abc123"
    )

    trace_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for tracing this error (extension field)",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

    # Extension fields for domain-specific data (RFC 7807 allows this)
    # These can be added dynamically via model_extra
    model_config = {
        "extra": "allow",  # Allow additional fields for domain-specific extensions
        "json_schema_extra": {
            "example": {
                "type": "https://filter-ical.de/errors/validation-error",
                "title": "Validation Error",
                "status": 400,
                "detail": "Calendar name is required",
                "instance": "/api/calendars",
                "trace_id": "550e8400-e29b-41d4-a716-446655440000",
                "field": "name"  # Extension field example
            }
        }
    }


def create_problem_detail(
    type_url: str,
    title: str,
    status: int,
    detail: str,
    instance: Optional[str] = None,
    trace_id: Optional[str] = None,
    **extensions: Any
) -> ProblemDetail:
    """
    Factory function to create a ProblemDetail instance.

    Args:
        type_url: URI reference identifying the problem type
        title: Short human-readable summary
        status: HTTP status code
        detail: Human-readable explanation
        instance: URI reference identifying the occurrence (optional)
        trace_id: Unique identifier for tracing (optional, auto-generated)
        **extensions: Additional domain-specific fields

    Returns:
        ProblemDetail instance

    Example:
        >>> problem = create_problem_detail(
        ...     type_url="https://filter-ical.de/errors/calendar-not-found",
        ...     title="Calendar Not Found",
        ...     status=404,
        ...     detail="Calendar with ID 'abc123' does not exist",
        ...     instance="/api/calendars/abc123"
        ... )
    """
    data = {
        "type": type_url,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
    }

    if trace_id:
        data["trace_id"] = trace_id

    # Add extension fields
    data.update(extensions)

    return ProblemDetail(**data)
