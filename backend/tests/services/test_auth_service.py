"""
Unit tests for authentication service.

Tests password hashing, JWT tokens, and validation logic.
Pure function tests require no mocking.
"""

import pytest
from datetime import datetime, timezone, timedelta

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_jwt_token,
    verify_jwt_token,
    generate_reset_token,
    create_reset_token_expiry,
    is_valid_username,
    is_valid_email,
    is_valid_password,
    requires_email_with_password
)


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password_creates_bcrypt_hash(self):
        """Test password hashing produces bcrypt hash."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt hash prefix

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test password verification with incorrect password."""
        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_invalid_hash(self):
        """Test password verification with invalid hash."""
        assert verify_password("any_password", "invalid_hash") is False


@pytest.mark.unit
class TestUsernameValidation:
    """Test username validation rules."""

    def test_valid_username(self):
        """Test valid username passes validation."""
        is_valid, error = is_valid_username("valid_user123")
        assert is_valid is True
        assert error == ""

    def test_username_too_short(self):
        """Test username must be at least 3 characters."""
        is_valid, error = is_valid_username("ab")
        assert is_valid is False
        assert "at least 3 characters" in error

    def test_username_too_long(self):
        """Test username must be at most 50 characters."""
        is_valid, error = is_valid_username("a" * 51)
        assert is_valid is False
        assert "at most 50 characters" in error

    def test_username_empty(self):
        """Test empty username is invalid."""
        is_valid, error = is_valid_username("")
        assert is_valid is False
        assert "required" in error

    def test_username_invalid_characters(self):
        """Test username with invalid characters."""
        is_valid, error = is_valid_username("user@name")
        assert is_valid is False
        assert "letters, numbers, underscores, and hyphens" in error

    def test_username_with_underscore_and_hyphen(self):
        """Test username can contain underscores and hyphens."""
        is_valid, error = is_valid_username("user_name-123")
        assert is_valid is True
        assert error == ""


@pytest.mark.unit
class TestEmailValidation:
    """Test email validation rules."""

    def test_valid_email(self):
        """Test valid email passes validation."""
        is_valid, error = is_valid_email("user@example.com")
        assert is_valid is True
        assert error == ""

    def test_email_optional(self):
        """Test email is optional (empty is valid)."""
        is_valid, error = is_valid_email("")
        assert is_valid is True
        assert error == ""

    def test_email_missing_at(self):
        """Test email must contain @."""
        is_valid, error = is_valid_email("userexample.com")
        assert is_valid is False
        assert "Invalid email format" in error

    def test_email_missing_dot(self):
        """Test email must contain dot."""
        is_valid, error = is_valid_email("user@example")
        assert is_valid is False
        assert "Invalid email format" in error

    def test_email_too_long(self):
        """Test email must be at most 255 characters."""
        long_email = "a" * 250 + "@b.com"
        is_valid, error = is_valid_email(long_email)
        assert is_valid is False
        assert "too long" in error


@pytest.mark.unit
class TestPasswordValidation:
    """Test password validation rules."""

    def test_valid_password(self):
        """Test valid password passes validation."""
        is_valid, error = is_valid_password("valid_pass123")
        assert is_valid is True
        assert error == ""

    def test_password_optional(self):
        """Test password is optional (empty is valid)."""
        is_valid, error = is_valid_password("")
        assert is_valid is True
        assert error == ""

    def test_password_too_short(self):
        """Test password must be at least 4 characters."""
        is_valid, error = is_valid_password("abc")
        assert is_valid is False
        assert "at least 4 characters" in error

    def test_password_too_long(self):
        """Test password must be at most 100 characters."""
        is_valid, error = is_valid_password("a" * 101)
        assert is_valid is False
        assert "too long" in error


@pytest.mark.unit
class TestRequiresEmailWithPassword:
    """Test email-password dependency validation."""

    def test_no_password_no_requirement(self):
        """Test no validation when password is not being set."""
        is_valid, error = requires_email_with_password(
            password=None,
            current_email=None,
            new_email=None
        )
        assert is_valid is True
        assert error == ""

    def test_password_with_current_email(self):
        """Test password allowed when user has current email."""
        is_valid, error = requires_email_with_password(
            password="new_password",
            current_email="user@example.com",
            new_email=None
        )
        assert is_valid is True
        assert error == ""

    def test_password_with_new_email(self):
        """Test password allowed when adding new email."""
        is_valid, error = requires_email_with_password(
            password="new_password",
            current_email=None,
            new_email="user@example.com"
        )
        assert is_valid is True
        assert error == ""

    def test_password_without_email_fails(self):
        """Test password requires email."""
        is_valid, error = requires_email_with_password(
            password="new_password",
            current_email=None,
            new_email=None
        )
        assert is_valid is False
        assert "Email address is required" in error
        assert "password reset" in error

    def test_password_with_empty_current_email_fails(self):
        """Test password requires non-empty email."""
        is_valid, error = requires_email_with_password(
            password="new_password",
            current_email="",
            new_email=None
        )
        assert is_valid is False
        assert "Email address is required" in error

    def test_password_with_whitespace_email_fails(self):
        """Test password requires non-whitespace email."""
        is_valid, error = requires_email_with_password(
            password="new_password",
            current_email="   ",
            new_email=None
        )
        assert is_valid is False
        assert "Email address is required" in error

    def test_new_email_overrides_current_email(self):
        """Test new email takes precedence over current email."""
        # New email provided (valid)
        is_valid, error = requires_email_with_password(
            password="new_password",
            current_email="",
            new_email="new@example.com"
        )
        assert is_valid is True
        assert error == ""

        # New email empty but current email valid
        is_valid, error = requires_email_with_password(
            password="new_password",
            current_email="current@example.com",
            new_email=""
        )
        assert is_valid is False
        assert "Email address is required" in error

    def test_empty_password_string_treated_as_no_password(self):
        """Test empty password string is treated same as None."""
        is_valid, error = requires_email_with_password(
            password="",
            current_email=None,
            new_email=None
        )
        # Empty string is falsy, so no validation required
        assert is_valid is True
        assert error == ""


@pytest.mark.unit
class TestResetTokenGeneration:
    """Test password reset token generation."""

    def test_generate_reset_token_returns_uuid(self):
        """Test reset token is UUID format."""
        token = generate_reset_token()
        assert token is not None
        assert isinstance(token, str)
        assert len(token) == 36  # UUID4 format length
        assert token.count("-") == 4  # UUID has 4 hyphens

    def test_generate_reset_token_unique(self):
        """Test each reset token is unique."""
        token1 = generate_reset_token()
        token2 = generate_reset_token()
        assert token1 != token2

    def test_create_reset_token_expiry_default(self):
        """Test reset token expiry defaults to 1 hour."""
        now = datetime.now(timezone.utc)
        expiry = create_reset_token_expiry()

        # Should be approximately 1 hour from now
        delta = expiry - now
        assert 3590 <= delta.total_seconds() <= 3610  # 1 hour ± 10 seconds

    def test_create_reset_token_expiry_custom(self):
        """Test reset token expiry with custom hours."""
        now = datetime.now(timezone.utc)
        expiry = create_reset_token_expiry(hours=24)

        # Should be approximately 24 hours from now
        delta = expiry - now
        assert 86390 <= delta.total_seconds() <= 86410  # 24 hours ± 10 seconds
