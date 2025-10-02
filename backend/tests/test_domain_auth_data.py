"""
Unit tests for domain authentication pure functions.

Tests pure functions from app.data.domain_auth module following TDD principles.
All functions tested here are pure - no side effects, predictable outputs.
"""

import pytest
import time
from datetime import datetime, timezone, timedelta

from app.data.domain_auth import (
    hash_password,
    verify_password,
    create_auth_token,
    decode_auth_token,
    is_token_expired,
    calculate_token_age_days,
    should_refresh_token,
    validate_token_for_domain
)


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification functions."""

    def test_hash_password_creates_valid_hash(self):
        """Test that password hashing creates a valid bcrypt hash."""
        password = "test_password_123"
        hash_result = hash_password(password)

        assert hash_result is not None
        assert len(hash_result) > 0
        assert hash_result.startswith('$2b$')  # bcrypt identifier

    def test_hash_password_different_for_same_input(self):
        """Test that hashing same password twice produces different hashes (salt)."""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different salts

    def test_hash_password_empty_raises_error(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            hash_password("")

    def test_hash_password_with_custom_cost_factor(self):
        """Test password hashing with custom cost factor."""
        password = "test_password"
        hash_result = hash_password(password, cost_factor=10)

        assert hash_result.startswith('$2b$10$')  # Cost factor 10

    def test_verify_password_correct_password(self):
        """Test password verification with correct password."""
        password = "correct_password"
        password_hash = hash_password(password)

        assert verify_password(password, password_hash) is True

    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        password_hash = hash_password(password)

        assert verify_password(wrong_password, password_hash) is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        password_hash = hash_password("something")

        assert verify_password("", password_hash) is False

    def test_verify_password_empty_hash(self):
        """Test password verification with empty hash."""
        assert verify_password("password", "") is False

    def test_verify_password_invalid_hash_format(self):
        """Test password verification with invalid hash format."""
        assert verify_password("password", "not_a_valid_hash") is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "CaseSensitive"
        password_hash = hash_password(password)

        assert verify_password("casesensitive", password_hash) is False
        assert verify_password("CaseSensitive", password_hash) is True


@pytest.mark.unit
class TestJWTTokenCreation:
    """Test JWT token creation functions."""

    SECRET_KEY = "test_secret_key_for_testing"

    def test_create_auth_token_admin(self):
        """Test creating admin-level auth token."""
        token = create_auth_token(
            domain_key="test_domain",
            access_level="admin",
            secret_key=self.SECRET_KEY
        )

        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)

    def test_create_auth_token_user(self):
        """Test creating user-level auth token."""
        token = create_auth_token(
            domain_key="test_domain",
            access_level="user",
            secret_key=self.SECRET_KEY
        )

        assert token is not None
        assert len(token) > 0

    def test_create_auth_token_custom_expiry(self):
        """Test creating token with custom expiry."""
        token = create_auth_token(
            domain_key="test_domain",
            access_level="admin",
            secret_key=self.SECRET_KEY,
            expiry_days=7
        )

        # Decode and check expiry
        decoded = decode_auth_token(token, self.SECRET_KEY)
        assert decoded is not None

        exp_time = datetime.fromtimestamp(decoded['exp'], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(decoded['iat'], tz=timezone.utc)
        diff = exp_time - iat_time

        # Should be approximately 7 days
        assert 6.9 <= diff.days <= 7.1

    def test_create_auth_token_empty_domain_raises_error(self):
        """Test that empty domain_key raises ValueError."""
        with pytest.raises(ValueError, match="domain_key and access_level are required"):
            create_auth_token("", "admin", self.SECRET_KEY)

    def test_create_auth_token_invalid_level_raises_error(self):
        """Test that invalid access_level raises ValueError."""
        with pytest.raises(ValueError, match="access_level must be"):
            create_auth_token("test_domain", "invalid", self.SECRET_KEY)

    def test_create_auth_token_contains_correct_payload(self):
        """Test that token contains correct payload data."""
        domain = "test_domain"
        level = "admin"

        token = create_auth_token(domain, level, self.SECRET_KEY)
        decoded = decode_auth_token(token, self.SECRET_KEY)

        assert decoded['domain_key'] == domain
        assert decoded['access_level'] == level
        assert 'iat' in decoded
        assert 'exp' in decoded


@pytest.mark.unit
class TestJWTTokenDecoding:
    """Test JWT token decoding functions."""

    SECRET_KEY = "test_secret_key_for_testing"

    def test_decode_auth_token_valid(self):
        """Test decoding valid auth token."""
        token = create_auth_token("test_domain", "admin", self.SECRET_KEY)
        decoded = decode_auth_token(token, self.SECRET_KEY)

        assert decoded is not None
        assert decoded['domain_key'] == "test_domain"
        assert decoded['access_level'] == "admin"

    def test_decode_auth_token_empty_returns_none(self):
        """Test that decoding empty token returns None."""
        assert decode_auth_token("", self.SECRET_KEY) is None

    def test_decode_auth_token_invalid_returns_none(self):
        """Test that decoding invalid token returns None."""
        assert decode_auth_token("invalid_token", self.SECRET_KEY) is None

    def test_decode_auth_token_wrong_secret_returns_none(self):
        """Test that decoding with wrong secret returns None."""
        token = create_auth_token("test_domain", "admin", self.SECRET_KEY)
        assert decode_auth_token(token, "wrong_secret") is None

    def test_decode_auth_token_expired_returns_none(self):
        """Test that decoding expired token returns None."""
        # Create token that expires in 0 days (instantly expired)
        token = create_auth_token(
            "test_domain",
            "admin",
            self.SECRET_KEY,
            expiry_days=0
        )

        # Wait a tiny bit to ensure expiry
        time.sleep(0.1)

        decoded = decode_auth_token(token, self.SECRET_KEY)
        assert decoded is None  # Expired tokens return None


@pytest.mark.unit
class TestTokenExpiryChecks:
    """Test token expiry checking functions."""

    def test_is_token_expired_not_expired(self):
        """Test checking non-expired token."""
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=30)

        token_data = {
            'exp': future.timestamp(),
            'iat': now.timestamp()
        }

        assert is_token_expired(token_data) is False

    def test_is_token_expired_expired(self):
        """Test checking expired token."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=1)

        token_data = {
            'exp': past.timestamp(),
            'iat': (past - timedelta(days=30)).timestamp()
        }

        assert is_token_expired(token_data) is True

    def test_is_token_expired_missing_exp_returns_true(self):
        """Test that missing 'exp' field returns True."""
        token_data = {'iat': datetime.now(timezone.utc).timestamp()}
        assert is_token_expired(token_data) is True

    def test_is_token_expired_empty_data_returns_true(self):
        """Test that empty token data returns True."""
        assert is_token_expired({}) is True
        assert is_token_expired(None) is True

    def test_is_token_expired_with_datetime_objects(self):
        """Test expiry check with datetime objects (not timestamps)."""
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=30)

        token_data = {
            'exp': future,
            'iat': now
        }

        assert is_token_expired(token_data) is False


@pytest.mark.unit
class TestTokenAgeCalculation:
    """Test token age calculation functions."""

    def test_calculate_token_age_days_fresh_token(self):
        """Test calculating age of fresh token."""
        now = datetime.now(timezone.utc)

        token_data = {
            'iat': now.timestamp(),
            'exp': (now + timedelta(days=30)).timestamp()
        }

        age = calculate_token_age_days(token_data)
        assert 0 <= age < 0.1  # Less than 0.1 days old

    def test_calculate_token_age_days_old_token(self):
        """Test calculating age of old token."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=25)

        token_data = {
            'iat': issued.timestamp(),
            'exp': (issued + timedelta(days=30)).timestamp()
        }

        age = calculate_token_age_days(token_data)
        assert 24.9 <= age <= 25.1  # Approximately 25 days old

    def test_calculate_token_age_missing_iat_returns_zero(self):
        """Test that missing 'iat' returns 0."""
        token_data = {'exp': datetime.now(timezone.utc).timestamp()}
        assert calculate_token_age_days(token_data) == 0.0

    def test_calculate_token_age_empty_data_returns_zero(self):
        """Test that empty data returns 0."""
        assert calculate_token_age_days({}) == 0.0
        assert calculate_token_age_days(None) == 0.0


@pytest.mark.unit
class TestTokenRefreshLogic:
    """Test token refresh decision functions."""

    def test_should_refresh_token_old_token(self):
        """Test that old token should be refreshed."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=26)

        token_data = {
            'iat': issued.timestamp(),
            'exp': (issued + timedelta(days=30)).timestamp()
        }

        assert should_refresh_token(token_data, refresh_threshold_days=25) is True

    def test_should_refresh_token_fresh_token(self):
        """Test that fresh token should not be refreshed."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=5)

        token_data = {
            'iat': issued.timestamp(),
            'exp': (issued + timedelta(days=30)).timestamp()
        }

        assert should_refresh_token(token_data, refresh_threshold_days=25) is False

    def test_should_refresh_token_expired_returns_false(self):
        """Test that expired token cannot be refreshed."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=31)

        token_data = {
            'iat': issued.timestamp(),
            'exp': (issued + timedelta(days=30)).timestamp()  # Expired
        }

        assert should_refresh_token(token_data) is False

    def test_should_refresh_token_at_threshold(self):
        """Test token exactly at refresh threshold."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=25)

        token_data = {
            'iat': issued.timestamp(),
            'exp': (issued + timedelta(days=30)).timestamp()
        }

        assert should_refresh_token(token_data, refresh_threshold_days=25) is True


@pytest.mark.unit
class TestTokenValidation:
    """Test token validation for domain access."""

    def test_validate_token_for_domain_valid_admin(self):
        """Test validating admin token for domain."""
        now = datetime.now(timezone.utc)

        token_data = {
            'domain_key': 'test_domain',
            'access_level': 'admin',
            'iat': now.timestamp(),
            'exp': (now + timedelta(days=30)).timestamp()
        }

        assert validate_token_for_domain(token_data, 'test_domain', 'admin') is True

    def test_validate_token_for_domain_admin_can_access_user(self):
        """Test that admin token grants user-level access."""
        now = datetime.now(timezone.utc)

        token_data = {
            'domain_key': 'test_domain',
            'access_level': 'admin',
            'iat': now.timestamp(),
            'exp': (now + timedelta(days=30)).timestamp()
        }

        assert validate_token_for_domain(token_data, 'test_domain', 'user') is True

    def test_validate_token_for_domain_user_cannot_access_admin(self):
        """Test that user token cannot access admin routes."""
        now = datetime.now(timezone.utc)

        token_data = {
            'domain_key': 'test_domain',
            'access_level': 'user',
            'iat': now.timestamp(),
            'exp': (now + timedelta(days=30)).timestamp()
        }

        assert validate_token_for_domain(token_data, 'test_domain', 'admin') is False

    def test_validate_token_for_domain_wrong_domain(self):
        """Test validation fails for wrong domain."""
        now = datetime.now(timezone.utc)

        token_data = {
            'domain_key': 'other_domain',
            'access_level': 'admin',
            'iat': now.timestamp(),
            'exp': (now + timedelta(days=30)).timestamp()
        }

        assert validate_token_for_domain(token_data, 'test_domain', 'admin') is False

    def test_validate_token_for_domain_expired_token(self):
        """Test validation fails for expired token."""
        now = datetime.now(timezone.utc)

        token_data = {
            'domain_key': 'test_domain',
            'access_level': 'admin',
            'iat': (now - timedelta(days=31)).timestamp(),
            'exp': (now - timedelta(days=1)).timestamp()  # Expired
        }

        assert validate_token_for_domain(token_data, 'test_domain', 'admin') is False

    def test_validate_token_for_domain_none_token(self):
        """Test validation fails for None token."""
        assert validate_token_for_domain(None, 'test_domain', 'admin') is False

    def test_validate_token_for_domain_missing_fields(self):
        """Test validation fails for token with missing fields."""
        token_data = {'domain_key': 'test_domain'}  # Missing access_level, exp, iat

        assert validate_token_for_domain(token_data, 'test_domain', 'admin') is False
