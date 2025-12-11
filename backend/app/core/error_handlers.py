"""
Error handling for FastAPI endpoints with RFC 7807 Problem Details.

This module provides:
1. Global exception handler that converts all HTTPException to RFC 7807 format
2. Reusable decorator for consistent error handling across endpoints

RFC 7807 provides machine-readable error responses with:
- type: URI identifying the error type
- title: Human-readable summary
- status: HTTP status code
- detail: Specific explanation
- instance: URI of the request
- trace_id: Unique identifier for debugging
"""

from functools import wraps
from typing import Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from .problem_details import ProblemDetail
from .error_types import ErrorType, get_error_type_from_message


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Global exception handler for HTTPException.

    Converts all HTTPException instances to RFC 7807 Problem Details format.
    This provides consistent, machine-readable error responses across the API.

    For ProblemDetailException instances, uses the specific error type.
    For regular HTTPException, infers the error type from the detail message.

    Args:
        request: The FastAPI request object
        exc: The HTTPException being handled

    Returns:
        JSONResponse with RFC 7807 Problem Details

    Example:
        When an endpoint raises HTTPException(status_code=404, detail="Calendar not found"),
        this handler converts it to:
        {
            "type": "https://filter-ical.de/errors/calendar-not-found",
            "title": "Calendar Not Found",
            "status": 404,
            "detail": "Calendar not found",
            "instance": "/api/calendars/123",
            "trace_id": "550e8400-e29b-41d4-a716-446655440000"
        }
    """
    # Check if this is a ProblemDetailException with explicit error type
    from .exceptions import ProblemDetailException

    if isinstance(exc, ProblemDetailException):
        # Use the explicit error type from ProblemDetailException
        error_type = exc.error_type
        instance = exc.instance if exc.instance else str(request.url.path)
        extensions = exc.extensions
    else:
        # Infer error type from message and status code for regular HTTPException
        error_type = get_error_type_from_message(exc.detail, exc.status_code)
        instance = str(request.url.path)
        extensions = {}

    # Create RFC 7807 problem detail
    problem = error_type.create_problem(
        detail=exc.detail,
        instance=instance,
        **extensions
    )

    # Return JSON response with RFC 7807 format
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(),
        headers=exc.headers if exc.headers else None
    )


def handle_endpoint_errors(func):
    """
    Decorator for consistent error handling across all router endpoints.

    Catches all exceptions except HTTPException (which is intentionally raised).
    Converts unexpected exceptions to HTTP 500 errors with safe error messages.

    This decorator eliminates the need for duplicate try/except blocks in every
    endpoint by centralizing error handling logic.

    Args:
        func: The async endpoint function to wrap.

    Returns:
        The wrapped function with error handling.

    Raises:
        HTTPException: Either re-raised from the endpoint (intentional errors)
                      or created from unexpected exceptions (status 500).

    Examples:
        Basic usage with a simple endpoint:

        >>> @router.get("/items/{item_id}")
        >>> @handle_endpoint_errors
        >>> async def get_item(item_id: int):
        ...     return {"item_id": item_id}

        Handling intentional HTTP errors (re-raised):

        >>> @router.get("/items/{item_id}")
        >>> @handle_endpoint_errors
        >>> async def get_item(item_id: int):
        ...     if item_id < 0:
        ...         raise HTTPException(status_code=400, detail="Invalid ID")
        ...     return {"item_id": item_id}

        Handling unexpected errors (converted to 500):

        >>> @router.get("/items")
        >>> @handle_endpoint_errors
        >>> async def list_items():
        ...     # If this raises any exception, it becomes HTTP 500
        ...     items = database.query_all()  # May raise DatabaseError
        ...     return {"items": items}

    Notes:
        - HTTPException is always re-raised without modification
        - All other exceptions are converted to HTTP 500 with error message
        - Original error messages are preserved in the detail field
        - Works with both sync and async functions (use async for FastAPI)
        - Function metadata (name, docstring) is preserved via @wraps
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTP exceptions (intentional errors)
            raise
        except Exception as e:
            # Convert unexpected exceptions to HTTP 500
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    return wrapper
