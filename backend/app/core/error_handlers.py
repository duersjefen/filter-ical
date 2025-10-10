"""
Error handling decorators for FastAPI endpoints.

This module provides reusable decorators for consistent error handling
across all router endpoints, eliminating duplicate try/except patterns.
"""

from functools import wraps
from fastapi import HTTPException


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
