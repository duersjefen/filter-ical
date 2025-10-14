"""
Unit tests for domain access service.

Tests user access checking for domain owners, domain admins, and password-based access.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from app.services.domain_access_service import check_user_has_domain_access
from app.models.domain import Domain
from app.models.user_domain_access import UserDomainAccess


@pytest.mark.unit
class TestCheckUserHasDomainAccess:
    """Test domain access checking logic."""

    def test_owner_has_admin_access(self):
        """Test that domain owner always has admin access."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(spec=Domain)
        mock_domain.id = 1
        mock_domain.owner_id = 42  # User ID 42 is the owner
        mock_domain.calendar_id = 100
        mock_domain.admin_password_hash = "some_encrypted_password"

        # Setup query chain
        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        # Owner (user_id=42) should have admin access even if password is set
        result = check_user_has_domain_access(mock_db, 42, "test-domain", "admin")

        assert result is True

    def test_owner_does_not_have_user_access_without_password(self):
        """Test that domain owner needs user password if set."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(spec=Domain)
        mock_domain.id = 1
        mock_domain.owner_id = 42  # User ID 42 is the owner
        mock_domain.calendar_id = 100
        mock_domain.admin_password_hash = None
        mock_domain.user_password_hash = "some_encrypted_password"

        # Setup query chain for domain
        domain_query_mock = MagicMock()
        domain_query_mock.filter.return_value.first.return_value = mock_domain

        # Setup query chain for user_domain_access (not found)
        access_query_mock = MagicMock()
        access_query_mock.filter.return_value.first.return_value = None

        # Configure mock_db.query to return different mocks based on the model
        def query_side_effect(model):
            if model == Domain:
                return domain_query_mock
            elif model == UserDomainAccess:
                return access_query_mock
            return MagicMock()

        mock_db.query.side_effect = query_side_effect

        # Owner requesting user-level access should need password unlock
        result = check_user_has_domain_access(mock_db, 42, "test-domain", "user")

        assert result is False

    def test_domain_admin_has_admin_access(self):
        """Test that domain admin (via domain_admins table) has admin access."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(spec=Domain)
        mock_domain.id = 1
        mock_domain.owner_id = 99  # Different user
        mock_domain.calendar_id = 100
        mock_domain.admin_password_hash = "some_encrypted_password"

        # Setup query chain for domain
        domain_query_mock = MagicMock()
        domain_query_mock.filter.return_value.first.return_value = mock_domain

        # Setup query chain for domain_admins (user is admin)
        admin_query_mock = MagicMock()
        admin_query_mock.filter.return_value.first.return_value = Mock()  # Entry exists

        # Configure mock_db.query to return different mocks
        def query_side_effect(table_or_model):
            if hasattr(table_or_model, '__tablename__') and table_or_model.__tablename__ == 'domains':
                return domain_query_mock
            else:
                return admin_query_mock

        mock_db.query.side_effect = query_side_effect

        # User 42 is in domain_admins table, should have admin access
        result = check_user_has_domain_access(mock_db, 42, "test-domain", "admin")

        assert result is True

    def test_no_password_set_grants_access(self):
        """Test that no password grants access to everyone."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(spec=Domain)
        mock_domain.id = 1
        mock_domain.owner_id = 99  # Different user
        mock_domain.calendar_id = 100
        mock_domain.admin_password_hash = None  # No password set
        mock_domain.user_password_hash = None

        # Setup query chain for domain
        domain_query_mock = MagicMock()
        domain_query_mock.filter.return_value.first.return_value = mock_domain

        # Setup query chain for domain_admins (user is not admin)
        admin_query_mock = MagicMock()
        admin_query_mock.filter.return_value.first.return_value = None

        # Configure mock_db.query to return different mocks
        def query_side_effect(table_or_model):
            if hasattr(table_or_model, '__tablename__'):
                if table_or_model.__tablename__ == 'domains':
                    return domain_query_mock
            return admin_query_mock

        mock_db.query.side_effect = query_side_effect

        # User 42 is neither owner nor admin, but no password is set
        result = check_user_has_domain_access(mock_db, 42, "test-domain", "admin")

        assert result is True

    def test_password_unlock_grants_access(self):
        """Test that user_domain_access entry grants access."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(spec=Domain)
        mock_domain.id = 1
        mock_domain.owner_id = 99  # Different user
        mock_domain.calendar_id = 100
        mock_domain.admin_password_hash = "encrypted_password"

        # Setup query chain for domain
        domain_query_mock = MagicMock()
        domain_query_mock.filter.return_value.first.return_value = mock_domain

        # Setup query chain for domain_admins (user is not admin)
        admin_query_mock = MagicMock()
        admin_query_mock.filter.return_value.first.return_value = None

        # Setup query chain for user_domain_access (entry exists - unlocked)
        access_query_mock = MagicMock()
        mock_access = Mock(spec=UserDomainAccess)
        access_query_mock.filter.return_value.first.return_value = mock_access

        # Configure mock_db.query to return different mocks
        call_count = [0]
        def query_side_effect(table_or_model):
            call_count[0] += 1
            if hasattr(table_or_model, '__tablename__'):
                if table_or_model.__tablename__ == 'domains':
                    return domain_query_mock
            # First call after domain is domain_admins, second is user_domain_access
            if call_count[0] == 2:
                return admin_query_mock
            else:
                return access_query_mock

        mock_db.query.side_effect = query_side_effect

        # User 42 has unlocked the domain via password
        result = check_user_has_domain_access(mock_db, 42, "test-domain", "admin")

        assert result is True

    def test_no_access_without_unlock(self):
        """Test that user without unlock has no access when password is set."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(spec=Domain)
        mock_domain.id = 1
        mock_domain.owner_id = 99  # Different user
        mock_domain.calendar_id = 100
        mock_domain.admin_password_hash = "encrypted_password"

        # Setup query chain for domain
        domain_query_mock = MagicMock()
        domain_query_mock.filter.return_value.first.return_value = mock_domain

        # Setup query chain for domain_admins (user is not admin)
        admin_query_mock = MagicMock()
        admin_query_mock.filter.return_value.first.return_value = None

        # Setup query chain for user_domain_access (no entry - not unlocked)
        access_query_mock = MagicMock()
        access_query_mock.filter.return_value.first.return_value = None

        # Configure mock_db.query to return different mocks
        call_count = [0]
        def query_side_effect(table_or_model):
            call_count[0] += 1
            if hasattr(table_or_model, '__tablename__'):
                if table_or_model.__tablename__ == 'domains':
                    return domain_query_mock
            # First call after domain is domain_admins, second is user_domain_access
            if call_count[0] == 2:
                return admin_query_mock
            else:
                return access_query_mock

        mock_db.query.side_effect = query_side_effect

        # User 42 has no unlock and is not owner/admin
        result = check_user_has_domain_access(mock_db, 42, "test-domain", "admin")

        assert result is False

    def test_domain_not_found(self):
        """Test that non-existent domain returns False."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = check_user_has_domain_access(mock_db, 42, "nonexistent", "admin")

        assert result is False
