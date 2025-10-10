"""
Unit tests for domain authentication service.

Tests password verification, token generation/validation, and authentication flows.
All database and cryptography operations are mocked using pytest fixtures.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.services.domain_auth_service import (
    get_domain_auth,
    get_or_create_domain_auth,
    set_admin_password,
    set_user_password,
    remove_admin_password,
    remove_user_password,
    verify_domain_password,
    verify_token,
    refresh_token_if_needed,
    check_password_status,
    get_all_domains_auth_status,
    get_decrypted_password
)
from app.models.domain import Domain
from app.models.user import User


@pytest.mark.unit
class TestGetDomainAuth:
    """Test domain authentication record retrieval."""

    def test_get_domain_auth_success(self):
        """Test successful domain auth retrieval."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", admin_password_hash="hash123")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        domain = get_domain_auth(mock_db, "test-domain")

        assert domain == mock_domain
        assert domain.domain_key == "test-domain"

    def test_get_domain_auth_not_found(self):
        """Test when domain doesn't exist."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        domain = get_domain_auth(mock_db, "nonexistent")

        assert domain is None


@pytest.mark.unit
class TestGetOrCreateDomainAuth:
    """Test domain authentication record creation."""

    def test_get_or_create_domain_auth_existing(self):
        """Test retrieving existing domain."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        domain = get_or_create_domain_auth(mock_db, "test-domain")

        assert domain == mock_domain
        assert not mock_db.add.called

    def test_get_or_create_domain_auth_new(self):
        """Test creating new domain record."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        domain = get_or_create_domain_auth(mock_db, "new-domain")

        assert mock_db.add.called
        assert mock_db.commit.called


@pytest.mark.unit
class TestSetAdminPassword:
    """Test admin password setting."""

    def test_set_admin_password_success(self):
        """Test successful admin password setting."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", admin_password_hash=None)

        with patch('app.services.domain_auth_service.get_or_create_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.encrypt_password') as mock_encrypt:
                mock_get.return_value = mock_domain
                mock_encrypt.return_value = "encrypted_password"

                success, error = set_admin_password(mock_db, "test-domain", "secure_password")

        assert success is True
        assert error == ""
        assert mock_domain.admin_password_hash == "encrypted_password"
        assert mock_db.commit.called

    def test_set_admin_password_too_short(self):
        """Test password that's too short."""
        mock_db = Mock(spec=Session)

        success, error = set_admin_password(mock_db, "test-domain", "123")

        assert success is False
        assert "at least 4 characters" in error

    def test_set_admin_password_empty(self):
        """Test empty password."""
        mock_db = Mock(spec=Session)

        success, error = set_admin_password(mock_db, "test-domain", "")

        assert success is False
        assert "at least 4 characters" in error

    def test_set_admin_password_database_error(self):
        """Test password setting with database error."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain")
        mock_db.commit.side_effect = Exception("Database error")

        with patch('app.services.domain_auth_service.get_or_create_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.encrypt_password') as mock_encrypt:
                mock_get.return_value = mock_domain
                mock_encrypt.return_value = "encrypted"

                success, error = set_admin_password(mock_db, "test-domain", "password123")

        assert success is False
        assert "Failed to set password" in error
        assert mock_db.rollback.called


@pytest.mark.unit
class TestSetUserPassword:
    """Test user password setting."""

    def test_set_user_password_success(self):
        """Test successful user password setting."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", user_password_hash=None)

        with patch('app.services.domain_auth_service.get_or_create_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.encrypt_password') as mock_encrypt:
                mock_get.return_value = mock_domain
                mock_encrypt.return_value = "encrypted_password"

                success, error = set_user_password(mock_db, "test-domain", "user_password")

        assert success is True
        assert error == ""
        assert mock_domain.user_password_hash == "encrypted_password"
        assert mock_db.commit.called

    def test_set_user_password_too_short(self):
        """Test user password that's too short."""
        mock_db = Mock(spec=Session)

        success, error = set_user_password(mock_db, "test-domain", "abc")

        assert success is False
        assert "at least 4 characters" in error

    def test_set_user_password_database_error(self):
        """Test user password setting with database error."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain")
        mock_db.commit.side_effect = Exception("Database error")

        with patch('app.services.domain_auth_service.get_or_create_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.encrypt_password') as mock_encrypt:
                mock_get.return_value = mock_domain
                mock_encrypt.return_value = "encrypted"

                success, error = set_user_password(mock_db, "test-domain", "password123")

        assert success is False
        assert "Failed to set password" in error


@pytest.mark.unit
class TestRemoveAdminPassword:
    """Test admin password removal."""

    def test_remove_admin_password_success(self):
        """Test successful admin password removal."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", admin_password_hash="hash123")

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = mock_domain

            success, error = remove_admin_password(mock_db, "test-domain")

        assert success is True
        assert error == ""
        assert mock_domain.admin_password_hash is None
        assert mock_db.commit.called

    def test_remove_admin_password_no_domain(self):
        """Test removing password when domain doesn't exist."""
        mock_db = Mock(spec=Session)

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = None

            success, error = remove_admin_password(mock_db, "nonexistent")

        assert success is True
        assert error == ""

    def test_remove_admin_password_database_error(self):
        """Test password removal with database error."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", admin_password_hash="hash")
        mock_db.commit.side_effect = Exception("Database error")

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = mock_domain

            success, error = remove_admin_password(mock_db, "test-domain")

        assert success is False
        assert "Failed to remove password" in error
        assert mock_db.rollback.called


@pytest.mark.unit
class TestRemoveUserPassword:
    """Test user password removal."""

    def test_remove_user_password_success(self):
        """Test successful user password removal."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", user_password_hash="hash123")

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = mock_domain

            success, error = remove_user_password(mock_db, "test-domain")

        assert success is True
        assert error == ""
        assert mock_domain.user_password_hash is None
        assert mock_db.commit.called

    def test_remove_user_password_no_domain(self):
        """Test removing password when domain doesn't exist."""
        mock_db = Mock(spec=Session)

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = None

            success, error = remove_user_password(mock_db, "nonexistent")

        assert success is True
        assert error == ""


@pytest.mark.unit
class TestVerifyDomainPassword:
    """Test domain password verification."""

    def test_verify_domain_password_admin_success(self):
        """Test successful admin password verification."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", admin_password_hash="encrypted_hash")

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.verify_password') as mock_verify:
                with patch('app.services.domain_auth_service.create_auth_token') as mock_token:
                    mock_get.return_value = mock_domain
                    mock_verify.return_value = True
                    mock_token.return_value = "jwt_token_123"

                    success, token = verify_domain_password(
                        mock_db, "test-domain", "correct_password", "admin"
                    )

        assert success is True
        assert token == "jwt_token_123"

    def test_verify_domain_password_user_success(self):
        """Test successful user password verification."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", user_password_hash="encrypted_hash")

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.verify_password') as mock_verify:
                with patch('app.services.domain_auth_service.create_auth_token') as mock_token:
                    mock_get.return_value = mock_domain
                    mock_verify.return_value = True
                    mock_token.return_value = "jwt_token_456"

                    success, token = verify_domain_password(
                        mock_db, "test-domain", "correct_password", "user"
                    )

        assert success is True
        assert token == "jwt_token_456"

    def test_verify_domain_password_wrong_password(self):
        """Test password verification with wrong password."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", admin_password_hash="encrypted_hash")

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.verify_password') as mock_verify:
                mock_get.return_value = mock_domain
                mock_verify.return_value = False

                success, error = verify_domain_password(
                    mock_db, "test-domain", "wrong_password", "admin"
                )

        assert success is False
        assert error == "Invalid password"

    def test_verify_domain_password_no_password_set(self):
        """Test verification when no password is set."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", admin_password_hash=None)

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.create_auth_token') as mock_token:
                mock_get.return_value = mock_domain
                mock_token.return_value = "jwt_token_no_password"

                success, token = verify_domain_password(
                    mock_db, "test-domain", "", "admin"
                )

        assert success is True
        assert token == "jwt_token_no_password"

    def test_verify_domain_password_no_domain(self):
        """Test verification when domain doesn't exist."""
        mock_db = Mock(spec=Session)

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.create_auth_token') as mock_token:
                mock_get.return_value = None
                mock_token.return_value = "jwt_token_new_domain"

                success, token = verify_domain_password(
                    mock_db, "new-domain", "", "admin"
                )

        assert success is True
        assert token == "jwt_token_new_domain"

    def test_verify_domain_password_skip_check(self):
        """Test verification with skip_password_check flag."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", admin_password_hash="hash")

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.create_auth_token') as mock_token:
                mock_get.return_value = mock_domain
                mock_token.return_value = "jwt_token_skip"

                success, token = verify_domain_password(
                    mock_db, "test-domain", "", "admin", skip_password_check=True
                )

        assert success is True
        assert token == "jwt_token_skip"

    def test_verify_domain_password_invalid_access_level(self):
        """Test verification with invalid access level."""
        mock_db = Mock(spec=Session)

        success, error = verify_domain_password(
            mock_db, "test-domain", "password", "invalid_level"
        )

        assert success is False
        assert "Invalid access level" in error


@pytest.mark.unit
class TestVerifyToken:
    """Test JWT token verification."""

    def test_verify_token_success(self):
        """Test successful token verification."""
        mock_token_data = {
            "domain_key": "test-domain",
            "access_level": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(days=30)
        }

        with patch('app.services.domain_auth_service.decode_auth_token') as mock_decode:
            with patch('app.services.domain_auth_service.validate_token_for_domain') as mock_validate:
                mock_decode.return_value = mock_token_data
                mock_validate.return_value = True

                valid, token_data = verify_token("jwt_token", "test-domain", "admin")

        assert valid is True
        assert token_data == mock_token_data

    def test_verify_token_invalid_token(self):
        """Test verification with invalid token."""
        with patch('app.services.domain_auth_service.decode_auth_token') as mock_decode:
            mock_decode.return_value = None

            valid, token_data = verify_token("invalid_token", "test-domain", "admin")

        assert valid is False
        assert token_data is None

    def test_verify_token_wrong_domain(self):
        """Test verification with wrong domain."""
        mock_token_data = {
            "domain_key": "other-domain",
            "access_level": "admin"
        }

        with patch('app.services.domain_auth_service.decode_auth_token') as mock_decode:
            with patch('app.services.domain_auth_service.validate_token_for_domain') as mock_validate:
                mock_decode.return_value = mock_token_data
                mock_validate.return_value = False

                valid, token_data = verify_token("jwt_token", "test-domain", "admin")

        assert valid is False
        assert token_data is None

    def test_verify_token_wrong_access_level(self):
        """Test verification with insufficient access level."""
        mock_token_data = {
            "domain_key": "test-domain",
            "access_level": "user"
        }

        with patch('app.services.domain_auth_service.decode_auth_token') as mock_decode:
            with patch('app.services.domain_auth_service.validate_token_for_domain') as mock_validate:
                mock_decode.return_value = mock_token_data
                mock_validate.return_value = False

                valid, token_data = verify_token("jwt_token", "test-domain", "admin")

        assert valid is False
        assert token_data is None

    def test_verify_token_exception(self):
        """Test verification with exception."""
        with patch('app.services.domain_auth_service.decode_auth_token') as mock_decode:
            mock_decode.side_effect = Exception("Token decode error")

            valid, token_data = verify_token("jwt_token", "test-domain", "admin")

        assert valid is False
        assert token_data is None


@pytest.mark.unit
class TestRefreshTokenIfNeeded:
    """Test token refresh logic."""

    def test_refresh_token_if_needed_refresh(self):
        """Test token refresh when old enough."""
        mock_token_data = {
            "domain_key": "test-domain",
            "access_level": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(days=3)  # Old token
        }

        with patch('app.services.domain_auth_service.decode_auth_token') as mock_decode:
            with patch('app.services.domain_auth_service.should_refresh_token') as mock_should:
                with patch('app.services.domain_auth_service.create_auth_token') as mock_create:
                    mock_decode.return_value = mock_token_data
                    mock_should.return_value = True
                    mock_create.return_value = "new_jwt_token"

                    refreshed, new_token = refresh_token_if_needed("old_jwt_token")

        assert refreshed is True
        assert new_token == "new_jwt_token"

    def test_refresh_token_if_needed_no_refresh(self):
        """Test token when refresh not needed."""
        mock_token_data = {
            "domain_key": "test-domain",
            "access_level": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(days=29)  # Fresh token
        }

        with patch('app.services.domain_auth_service.decode_auth_token') as mock_decode:
            with patch('app.services.domain_auth_service.should_refresh_token') as mock_should:
                mock_decode.return_value = mock_token_data
                mock_should.return_value = False

                refreshed, token = refresh_token_if_needed("jwt_token")

        assert refreshed is False
        assert token == "jwt_token"

    def test_refresh_token_if_needed_invalid_token(self):
        """Test refresh with invalid token."""
        with patch('app.services.domain_auth_service.decode_auth_token') as mock_decode:
            mock_decode.return_value = None

            refreshed, token = refresh_token_if_needed("invalid_token")

        assert refreshed is False
        assert token == "invalid_token"

    def test_refresh_token_if_needed_exception(self):
        """Test refresh with exception."""
        with patch('app.services.domain_auth_service.decode_auth_token') as mock_decode:
            mock_decode.side_effect = Exception("Token error")

            refreshed, token = refresh_token_if_needed("jwt_token")

        assert refreshed is False
        assert token == "jwt_token"


@pytest.mark.unit
class TestCheckPasswordStatus:
    """Test password status checking."""

    def test_check_password_status_both_set(self):
        """Test status when both passwords are set."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(
            domain_key="test-domain",
            admin_password_hash="admin_hash",
            user_password_hash="user_hash"
        )

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = mock_domain

            status = check_password_status(mock_db, "test-domain")

        assert status['admin_password_set'] is True
        assert status['user_password_set'] is True

    def test_check_password_status_only_admin(self):
        """Test status when only admin password is set."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(
            domain_key="test-domain",
            admin_password_hash="admin_hash",
            user_password_hash=None
        )

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = mock_domain

            status = check_password_status(mock_db, "test-domain")

        assert status['admin_password_set'] is True
        assert status['user_password_set'] is False

    def test_check_password_status_no_domain(self):
        """Test status when domain doesn't exist."""
        mock_db = Mock(spec=Session)

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = None

            status = check_password_status(mock_db, "nonexistent")

        assert status['admin_password_set'] is False
        assert status['user_password_set'] is False


@pytest.mark.unit
class TestGetAllDomainsAuthStatus:
    """Test getting all domains auth status."""

    def test_get_all_domains_auth_status_success(self):
        """Test getting status for all domains."""
        mock_db = Mock(spec=Session)
        mock_owner = Mock(username="owner1")

        mock_domains = [
            Mock(
                domain_key="domain-1",
                admin_password_hash="hash1",
                user_password_hash=None,
                owner_id=1,
                owner=mock_owner,
                created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2025, 1, 2, tzinfo=timezone.utc)
            ),
            Mock(
                domain_key="domain-2",
                admin_password_hash=None,
                user_password_hash="hash2",
                owner_id=None,
                owner=None,
                created_at=datetime(2025, 1, 3, tzinfo=timezone.utc),
                updated_at=datetime(2025, 1, 4, tzinfo=timezone.utc)
            )
        ]

        mock_db.query.return_value.all.return_value = mock_domains

        statuses = get_all_domains_auth_status(mock_db)

        assert len(statuses) == 2
        assert statuses[0]['domain_key'] == "domain-1"
        assert statuses[0]['admin_password_set'] is True
        assert statuses[0]['user_password_set'] is False
        assert statuses[0]['owner_username'] == "owner1"
        assert statuses[1]['domain_key'] == "domain-2"
        assert statuses[1]['admin_password_set'] is False
        assert statuses[1]['user_password_set'] is True
        assert statuses[1]['owner_username'] is None

    def test_get_all_domains_auth_status_empty(self):
        """Test getting status when no domains exist."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.all.return_value = []

        statuses = get_all_domains_auth_status(mock_db)

        assert statuses == []


@pytest.mark.unit
class TestGetDecryptedPassword:
    """Test getting decrypted passwords."""

    def test_get_decrypted_password_admin_success(self):
        """Test successful admin password decryption."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(
            domain_key="test-domain",
            admin_password_hash="encrypted_admin_password"
        )

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.decrypt_password') as mock_decrypt:
                mock_get.return_value = mock_domain
                mock_decrypt.return_value = "decrypted_password"

                success, password = get_decrypted_password(mock_db, "test-domain", "admin")

        assert success is True
        assert password == "decrypted_password"

    def test_get_decrypted_password_user_success(self):
        """Test successful user password decryption."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(
            domain_key="test-domain",
            user_password_hash="encrypted_user_password"
        )

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.decrypt_password') as mock_decrypt:
                mock_get.return_value = mock_domain
                mock_decrypt.return_value = "user_password_123"

                success, password = get_decrypted_password(mock_db, "test-domain", "user")

        assert success is True
        assert password == "user_password_123"

    def test_get_decrypted_password_domain_not_found(self):
        """Test decryption when domain doesn't exist."""
        mock_db = Mock(spec=Session)

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = None

            success, error = get_decrypted_password(mock_db, "nonexistent", "admin")

        assert success is False
        assert "Domain not found" in error

    def test_get_decrypted_password_invalid_type(self):
        """Test decryption with invalid password type."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain")

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = mock_domain

            success, error = get_decrypted_password(mock_db, "test-domain", "invalid")

        assert success is False
        assert "Invalid password type" in error

    def test_get_decrypted_password_not_set(self):
        """Test decryption when password not set."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", admin_password_hash=None)

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            mock_get.return_value = mock_domain

            success, error = get_decrypted_password(mock_db, "test-domain", "admin")

        assert success is False
        assert "Password not set" in error

    def test_get_decrypted_password_decryption_failure(self):
        """Test decryption failure."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(
            domain_key="test-domain",
            admin_password_hash="corrupted_hash"
        )

        with patch('app.services.domain_auth_service.get_domain_auth') as mock_get:
            with patch('app.services.domain_auth_service.decrypt_password') as mock_decrypt:
                mock_get.return_value = mock_domain
                mock_decrypt.side_effect = Exception("Decryption error")

                success, error = get_decrypted_password(mock_db, "test-domain", "admin")

        assert success is False
        assert "Failed to decrypt password" in error
