"""
Tests for error handling decorator.

This test suite validates the handle_endpoint_errors decorator that provides
consistent error handling across all router endpoints.
"""

import pytest
from fastapi import HTTPException

from app.core.error_handlers import handle_endpoint_errors


class TestHandleEndpointErrors:
    """Test suite for handle_endpoint_errors decorator."""

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test that successful execution returns the expected result."""
        @handle_endpoint_errors
        async def successful_endpoint():
            return {"status": "success"}

        result = await successful_endpoint()
        assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_http_exception_is_reraised(self):
        """Test that HTTPException is re-raised without modification."""
        @handle_endpoint_errors
        async def endpoint_with_http_error():
            raise HTTPException(status_code=404, detail="Not found")

        with pytest.raises(HTTPException) as exc_info:
            await endpoint_with_http_error()

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Not found"

    @pytest.mark.asyncio
    async def test_generic_exception_converted_to_500(self):
        """Test that generic exceptions are converted to HTTP 500 errors."""
        @handle_endpoint_errors
        async def endpoint_with_generic_error():
            raise ValueError("Something went wrong")

        with pytest.raises(HTTPException) as exc_info:
            await endpoint_with_generic_error()

        assert exc_info.value.status_code == 500
        assert "Internal server error: Something went wrong" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_error_message_preserved(self):
        """Test that original error messages are preserved in the response."""
        error_message = "Database connection failed"

        @handle_endpoint_errors
        async def endpoint_with_db_error():
            raise ConnectionError(error_message)

        with pytest.raises(HTTPException) as exc_info:
            await endpoint_with_db_error()

        assert exc_info.value.status_code == 500
        assert error_message in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_multiple_http_exception_types(self):
        """Test that different HTTPException status codes are preserved."""
        test_cases = [
            (400, "Bad request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not found"),
            (409, "Conflict"),
        ]

        for status_code, detail in test_cases:
            @handle_endpoint_errors
            async def endpoint():
                raise HTTPException(status_code=status_code, detail=detail)

            with pytest.raises(HTTPException) as exc_info:
                await endpoint()

            assert exc_info.value.status_code == status_code
            assert exc_info.value.detail == detail

    @pytest.mark.asyncio
    async def test_with_function_arguments(self):
        """Test that decorator works with functions that accept arguments."""
        @handle_endpoint_errors
        async def endpoint_with_args(user_id: int, name: str):
            if user_id < 0:
                raise ValueError("Invalid user ID")
            return {"user_id": user_id, "name": name}

        # Test successful execution with args
        result = await endpoint_with_args(1, "Alice")
        assert result == {"user_id": 1, "name": "Alice"}

        # Test error handling with args
        with pytest.raises(HTTPException) as exc_info:
            await endpoint_with_args(-1, "Bob")

        assert exc_info.value.status_code == 500
        assert "Invalid user ID" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_with_keyword_arguments(self):
        """Test that decorator works with keyword arguments."""
        @handle_endpoint_errors
        async def endpoint_with_kwargs(required: str, optional: str = "default"):
            return {"required": required, "optional": optional}

        result = await endpoint_with_kwargs(required="value", optional="custom")
        assert result == {"required": "value", "optional": "custom"}

        result = await endpoint_with_kwargs(required="value")
        assert result == {"required": "value", "optional": "default"}

    @pytest.mark.asyncio
    async def test_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""
        @handle_endpoint_errors
        async def documented_endpoint():
            """This is a documented endpoint."""
            return {"status": "ok"}

        assert documented_endpoint.__name__ == "documented_endpoint"
        assert documented_endpoint.__doc__ == "This is a documented endpoint."

    @pytest.mark.asyncio
    async def test_nested_exceptions(self):
        """Test handling of nested exception scenarios."""
        @handle_endpoint_errors
        async def endpoint_with_nested_error():
            try:
                raise ValueError("Original error")
            except ValueError:
                raise RuntimeError("Wrapped error")

        with pytest.raises(HTTPException) as exc_info:
            await endpoint_with_nested_error()

        assert exc_info.value.status_code == 500
        assert "Wrapped error" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_exception_with_no_message(self):
        """Test handling of exceptions without error messages."""
        @handle_endpoint_errors
        async def endpoint_with_empty_error():
            raise RuntimeError()

        with pytest.raises(HTTPException) as exc_info:
            await endpoint_with_empty_error()

        assert exc_info.value.status_code == 500
        assert "Internal server error" in exc_info.value.detail
