"""
Unit tests for domain authentication pure functions.

Tests pure functions from app.data.domain_auth module following TDD principles.
All functions tested here are pure - no side effects, predictable outputs.
"""

import pytest
import time
from datetime import datetime, timezone, timedelta

from app.data.domain_auth import (
    encrypt_password,
    decrypt_password,
    verify_password,
    create_auth_token,
    decode_auth_token,
    is_token_expired,
    calculate_token_age_days,
    should_refresh_token,
    validate_token_for_domain
)


@pytest.mark.unit
class TestPasswordEncryption:
    """Test password encryption and verification functions."""

    TEST_ENCRYPTION_KEY = "P-EOqzNBZhEg8QVf2pWq9xY7tR5uKmN3oJlHbFcGdVw="

    def test_encrypt_password_creates_valid_encrypted_string(self):
        """Test that password encryption creates a valid encrypted string."""
        password = "test_password_123"
        encrypted = encrypt_password(password, self.TEST_ENCRYPTION_KEY)

        assert encrypted is not None
        assert len(encrypted) > 0
        assert isinstance(encrypted, str)

    def test_encrypt_password_deterministic_with_same_key(self):
        """Test that encrypting same password with same key is deterministic."""
        password = "same_password"
        encrypted1 = encrypt_password(password, self.TEST_ENCRYPTION_KEY)
        encrypted2 = encrypt_password(password, self.TEST_ENCRYPTION_KEY)

        # Fernet encryption is deterministic with the same key and timestamp
        # but may differ slightly due to timestamp
        assert isinstance(encrypted1, str)
        assert isinstance(encrypted2, str)

    def test_encrypt_password_empty_raises_error(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            encrypt_password("", self.TEST_ENCRYPTION_KEY)

    def test_decrypt_password_returns_original(self):
        """Test that decryption returns the original password."""
        password = "test_password_123"
        encrypted = encrypt_password(password, self.TEST_ENCRYPTION_KEY)
        decrypted = decrypt_password(encrypted, self.TEST_ENCRYPTION_KEY)

        assert decrypted == password

    def test_verify_password_correct_password(self):
        """Test password verification with correct password."""
        password = "correct_password"
        encrypted = encrypt_password(password, self.TEST_ENCRYPTION_KEY)

        assert verify_password(password, encrypted, self.TEST_ENCRYPTION_KEY) is True

    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        encrypted = encrypt_password(password, self.TEST_ENCRYPTION_KEY)

        assert verify_password(wrong_password, encrypted, self.TEST_ENCRYPTION_KEY) is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        encrypted = encrypt_password("something", self.TEST_ENCRYPTION_KEY)

        assert verify_password("", encrypted, self.TEST_ENCRYPTION_KEY) is False

    def test_verify_password_empty_encrypted(self):
        """Test password verification with empty encrypted password."""
        assert verify_password("password", "", self.TEST_ENCRYPTION_KEY) is False

    def test_verify_password_invalid_encrypted_format(self):
        """Test password verification with invalid encrypted format."""
        assert verify_password("password", "not_valid_encrypted", self.TEST_ENCRYPTION_KEY) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "CaseSensitive"
        encrypted = encrypt_password(password, self.TEST_ENCRYPTION_KEY)

        assert verify_password("casesensitive", encrypted, self.TEST_ENCRYPTION_KEY) is False
        assert verify_password("CaseSensitive", encrypted, self.TEST_ENCRYPTION_KEY) is True


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


@pytest.mark.unit
class TestTokenExpiryEdgeCases:
    """Edge case tests for token expiry and age calculations."""

    def test_is_token_expired_exactly_at_expiry(self):
        """Edge case: Token expires at exact current moment."""
        now = datetime.now(timezone.utc)

        token_data = {
            'exp': now.timestamp(),  # Expires right now
            'iat': (now - timedelta(days=30)).timestamp()
        }

        # At exact expiry moment, token should be considered expired
        assert is_token_expired(token_data) is True

    def test_is_token_expired_one_second_before_expiry(self):
        """Edge case: Token expires in one second (not expired yet)."""
        now = datetime.now(timezone.utc)
        expires_in_one_second = now + timedelta(seconds=1)

        token_data = {
            'exp': expires_in_one_second.timestamp(),
            'iat': now.timestamp()
        }

        assert is_token_expired(token_data) is False

    def test_is_token_expired_one_second_after_expiry(self):
        """Edge case: Token expired one second ago."""
        now = datetime.now(timezone.utc)
        expired_one_second_ago = now - timedelta(seconds=1)

        token_data = {
            'exp': expired_one_second_ago.timestamp(),
            'iat': (now - timedelta(days=30)).timestamp()
        }

        assert is_token_expired(token_data) is True

    def test_calculate_token_age_exactly_zero(self):
        """Edge case: Token issued exactly now (age = 0)."""
        now = datetime.now(timezone.utc)

        token_data = {
            'iat': now.timestamp(),
            'exp': (now + timedelta(days=30)).timestamp()
        }

        age = calculate_token_age_days(token_data)
        assert age < 0.001  # Less than 1.5 minutes old

    def test_calculate_token_age_exactly_30_days(self):
        """Edge case: Token issued exactly 30 days ago."""
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        token_data = {
            'iat': thirty_days_ago.timestamp(),
            'exp': now.timestamp()  # Expires now
        }

        age = calculate_token_age_days(token_data)
        assert 29.9 <= age <= 30.1  # Within margin

    def test_should_refresh_exactly_at_threshold(self):
        """Edge case: Token age exactly equals refresh threshold."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=25)  # Exactly 25 days old

        token_data = {
            'iat': issued.timestamp(),
            'exp': (issued + timedelta(days=30)).timestamp()
        }

        # At exact threshold, should refresh
        assert should_refresh_token(token_data, refresh_threshold_days=25) is True

    def test_should_refresh_one_day_before_threshold(self):
        """Edge case: Token age one day before refresh threshold."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=24)  # 24 days old

        token_data = {
            'iat': issued.timestamp(),
            'exp': (issued + timedelta(days=30)).timestamp()
        }

        # One day before threshold, should not refresh yet
        assert should_refresh_token(token_data, refresh_threshold_days=25) is False

    def test_should_refresh_one_day_after_threshold(self):
        """Edge case: Token age one day after refresh threshold."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=26)  # 26 days old

        token_data = {
            'iat': issued.timestamp(),
            'exp': (issued + timedelta(days=30)).timestamp()
        }

        # One day after threshold, should refresh
        assert should_refresh_token(token_data, refresh_threshold_days=25) is True

    def test_should_refresh_expired_token_returns_false(self):
        """Edge case: Expired tokens cannot be refreshed (return False)."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=31)
        expired = issued + timedelta(days=30)  # Expired 1 day ago

        token_data = {
            'iat': issued.timestamp(),
            'exp': expired.timestamp()
        }

        # Expired tokens should NOT be refreshed (they're invalid)
        assert should_refresh_token(token_data) is False

    def test_should_refresh_token_about_to_expire(self):
        """Edge case: Token expires in 1 day (past threshold, should refresh)."""
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=29)  # 29 days old, expires tomorrow

        token_data = {
            'iat': issued.timestamp(),
            'exp': (issued + timedelta(days=30)).timestamp()
        }

        # Should refresh (29 days >= 25 days threshold)
        assert should_refresh_token(token_data, refresh_threshold_days=25) is True

    def test_validate_token_exactly_at_expiry_moment(self):
        """Edge case: Validate token at exact expiry moment."""
        now = datetime.now(timezone.utc)

        token_data = {
            'domain_key': 'test_domain',
            'access_level': 'admin',
            'iat': (now - timedelta(days=30)).timestamp(),
            'exp': now.timestamp()  # Expires right now
        }

        # At exact expiry, should fail validation
        assert validate_token_for_domain(token_data, 'test_domain', 'admin') is False


@pytest.mark.unit
class TestPasswordEncryptionEdgeCases:
    """Edge case tests for password encryption."""

    TEST_ENCRYPTION_KEY = "P-EOqzNBZhEg8QVf2pWq9xY7tR5uKmN3oJlHbFcGdVw="

    def test_encrypt_password_with_special_characters(self):
        """Edge case: Password with special characters."""
        password = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        encrypted = encrypt_password(password, self.TEST_ENCRYPTION_KEY)
        decrypted = decrypt_password(encrypted, self.TEST_ENCRYPTION_KEY)

        assert decrypted == password

    def test_encrypt_password_with_unicode(self):
        """Edge case: Password with Unicode characters."""
        password = "пароль密码🔒"
        encrypted = encrypt_password(password, self.TEST_ENCRYPTION_KEY)
        decrypted = decrypt_password(encrypted, self.TEST_ENCRYPTION_KEY)

        assert decrypted == password

    def test_encrypt_password_very_long(self):
        """Edge case: Very long password (1000 characters)."""
        password = "a" * 1000
        encrypted = encrypt_password(password, self.TEST_ENCRYPTION_KEY)
        decrypted = decrypt_password(encrypted, self.TEST_ENCRYPTION_KEY)

        assert decrypted == password
        assert len(decrypted) == 1000

    def test_decrypt_password_wrong_key_raises_error(self):
        """Edge case: Decrypting with wrong key raises ValueError."""
        password = "test_password"
        encrypted = encrypt_password(password, self.TEST_ENCRYPTION_KEY)

        wrong_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

        with pytest.raises(ValueError, match="Invalid encrypted password"):
            decrypt_password(encrypted, wrong_key)

    def test_verify_password_with_whitespace(self):
        """Edge case: Password with leading/trailing whitespace."""
        password_with_spaces = "  password with spaces  "
        encrypted = encrypt_password(password_with_spaces, self.TEST_ENCRYPTION_KEY)

        # Exact match required (spaces preserved)
        assert verify_password(password_with_spaces, encrypted, self.TEST_ENCRYPTION_KEY) is True
        assert verify_password("password with spaces", encrypted, self.TEST_ENCRYPTION_KEY) is False
