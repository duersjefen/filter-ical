"""
Railway-Oriented Programming Result Types.

FUNCTIONAL CORE - Pure result types for explicit success/failure handling.
Replaces tuple-based (bool, data, error) pattern with explicit Result[T] types.

Why Result Types:
-----------------
1. Type Safety: IDE knows what you're working with
2. Explicit Error Handling: Can't accidentally ignore errors
3. Cleaner Code: No tuple unpacking, no confusing positions
4. Self-Documenting: result.is_success vs tuple[0]
5. Less Boilerplate: Eliminates repetitive if-checks in routers

Pattern Comparison:
-------------------
OLD (Tuple-based):
    success, data, error = some_function()
    if not success:
        raise HTTPException(400, detail=error)
    return data

NEW (Result-based):
    result = some_function()
    if not result.is_success:
        raise HTTPException(400, detail=result.error)
    return result.value

Usage:
------
# In data layer functions
def create_group(name: str) -> Result[Group]:
    if not name:
        return fail("Group name is required")

    group = {"id": 1, "name": name}
    return ok(group)

# In routers
result = create_group(request.name)
if not result.is_success:
    raise HTTPException(400, detail=result.error)
return result.value
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')


@dataclass
class Success(Generic[T]):
    """
    Successful result containing a value.

    Properties:
        value: The successful result data
        is_success: Always True
        error: Always empty string (for uniform interface)
    """
    value: T
    is_success: bool = True

    @property
    def error(self) -> str:
        """Error message (always empty for Success)."""
        return ""


@dataclass
class Failure:
    """
    Failed result containing an error message.

    Properties:
        error: The error message describing what went wrong
        is_success: Always False
        value: Raises ValueError if accessed (use is_success check first)
    """
    error: str
    is_success: bool = False

    @property
    def value(self):
        """
        Accessing value on Failure is an error.
        Always check is_success before accessing value.
        """
        raise ValueError(f"Cannot access value of Failure: {self.error}")


# Type alias for Result union
Result = Union[Success[T], Failure]


# Helper functions for creating results

def ok(value: T) -> Success[T]:
    """
    Create a successful result.

    Args:
        value: The successful result data

    Returns:
        Success instance containing the value

    Example:
        >>> user = {"id": 1, "name": "Alice"}
        >>> result = ok(user)
        >>> result.is_success
        True
        >>> result.value
        {"id": 1, "name": "Alice"}
    """
    return Success(value)


def fail(error: str) -> Failure:
    """
    Create a failed result.

    Args:
        error: Error message describing the failure

    Returns:
        Failure instance containing the error

    Example:
        >>> result = fail("User not found")
        >>> result.is_success
        False
        >>> result.error
        "User not found"
    """
    return Failure(error)


# Convenience functions for common patterns

def ok_none() -> Success[None]:
    """
    Create a successful result with no value.
    Useful for operations that succeed but return nothing.

    Example:
        >>> result = ok_none()
        >>> result.is_success
        True
        >>> result.value
        None
    """
    return Success(None)


def validate(condition: bool, error_message: str, value: T) -> Result[T]:
    """
    Helper for validation patterns.

    Args:
        condition: Condition that must be true for success
        error_message: Error message if condition is false
        value: Value to return if condition is true

    Returns:
        ok(value) if condition is True, fail(error_message) otherwise

    Example:
        >>> result = validate(len(name) > 0, "Name required", name)
    """
    if condition:
        return ok(value)
    return fail(error_message)
