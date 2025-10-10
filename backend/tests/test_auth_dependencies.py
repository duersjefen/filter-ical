"""
Unit tests for authentication dependencies.

Tests FastAPI dependencies from app.core.auth module following TDD principles.
"""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_verified_domain
from app.models.domain import Domain


@pytest.mark.unit
class TestGetVerifiedDomain:
    """Test get_verified_domain FastAPI dependency."""

    def test_get_verified_domain_returns_existing_domain(self, db_session):
        """Test that get_verified_domain returns existing domain object."""
        # Create a test domain
        test_domain = Domain(
            domain_key="test_domain",
            name="Test Domain",
            calendar_url="https://example.com/calendar.ics",
            status="active"
        )
        db_session.add(test_domain)
        db_session.commit()

        # Test the dependency
        result = None
        try:
            # Simulate FastAPI dependency injection
            import asyncio
            result = asyncio.run(get_verified_domain(
                domain="test_domain",
                db=db_session
            ))
        except HTTPException:
            pytest.fail("Should not raise HTTPException for existing domain")

        # Verify result
        assert result is not None
        assert result.domain_key == "test_domain"
        assert result.name == "Test Domain"
        assert result.calendar_url == "https://example.com/calendar.ics"
        assert isinstance(result, Domain)

    def test_get_verified_domain_raises_404_for_missing_domain(self, db_session):
        """Test that get_verified_domain raises 404 for non-existent domain."""
        # Test with non-existent domain
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(get_verified_domain(
                domain="nonexistent_domain",
                db=db_session
            ))

        # Verify the exception
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
        assert "nonexistent_domain" in exc_info.value.detail

    def test_get_verified_domain_with_special_characters(self, db_session):
        """Test domain verification with special characters in domain key."""
        # Create domain with special characters
        special_domain = Domain(
            domain_key="test-domain_123",
            name="Special Domain",
            calendar_url="https://example.com/calendar.ics",
            status="active"
        )
        db_session.add(special_domain)
        db_session.commit()

        # Test the dependency
        import asyncio
        result = asyncio.run(get_verified_domain(
            domain="test-domain_123",
            db=db_session
        ))

        assert result is not None
        assert result.domain_key == "test-domain_123"

    def test_get_verified_domain_case_sensitive(self, db_session):
        """Test that domain verification is case-sensitive."""
        # Create domain with lowercase key
        test_domain = Domain(
            domain_key="testdomain",
            name="Test Domain",
            calendar_url="https://example.com/calendar.ics",
            status="active"
        )
        db_session.add(test_domain)
        db_session.commit()

        # Try to access with uppercase - should fail
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(get_verified_domain(
                domain="TestDomain",
                db=db_session
            ))

        assert exc_info.value.status_code == 404

    def test_get_verified_domain_returns_inactive_domain(self, db_session):
        """Test that get_verified_domain returns domain regardless of status."""
        # Create inactive domain
        inactive_domain = Domain(
            domain_key="inactive_domain",
            name="Inactive Domain",
            calendar_url="https://example.com/calendar.ics",
            status="inactive"
        )
        db_session.add(inactive_domain)
        db_session.commit()

        # Should still return the domain (status filtering is router's responsibility)
        import asyncio
        result = asyncio.run(get_verified_domain(
            domain="inactive_domain",
            db=db_session
        ))

        assert result is not None
        assert result.domain_key == "inactive_domain"
        assert result.status == "inactive"

    def test_get_verified_domain_with_empty_string(self, db_session):
        """Test that get_verified_domain handles empty string domain key."""
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(get_verified_domain(
                domain="",
                db=db_session
            ))

        assert exc_info.value.status_code == 404

    def test_get_verified_domain_with_whitespace(self, db_session):
        """Test that get_verified_domain handles whitespace in domain key."""
        # Create domain without whitespace
        test_domain = Domain(
            domain_key="testdomain",
            name="Test Domain",
            calendar_url="https://example.com/calendar.ics",
            status="active"
        )
        db_session.add(test_domain)
        db_session.commit()

        # Try to access with whitespace - should fail
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(get_verified_domain(
                domain=" testdomain ",
                db=db_session
            ))

        assert exc_info.value.status_code == 404

    def test_get_verified_domain_with_slashes(self, db_session):
        """Test domain verification handles domain keys without slashes."""
        # Domain keys should not contain slashes (path separators)
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(get_verified_domain(
                domain="domain/with/slash",
                db=db_session
            ))

        assert exc_info.value.status_code == 404

    def test_get_verified_domain_returns_domain_with_relationships(self, db_session):
        """Test that get_verified_domain returns domain with accessible relationships."""
        # Create domain with owner
        from app.models.user import User

        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.flush()

        test_domain = Domain(
            domain_key="owned_domain",
            name="Owned Domain",
            calendar_url="https://example.com/calendar.ics",
            status="active",
            owner_id=user.id
        )
        db_session.add(test_domain)
        db_session.commit()

        # Get domain
        import asyncio
        result = asyncio.run(get_verified_domain(
            domain="owned_domain",
            db=db_session
        ))

        # Verify relationships are accessible
        assert result is not None
        assert result.owner_id == user.id
        assert result.owner is not None
        assert result.owner.username == "testuser"

    def test_get_verified_domain_multiple_domains_returns_correct_one(self, db_session):
        """Test that get_verified_domain returns the correct domain when multiple exist."""
        # Create multiple domains
        domain1 = Domain(
            domain_key="domain1",
            name="Domain 1",
            calendar_url="https://example.com/cal1.ics",
            status="active"
        )
        domain2 = Domain(
            domain_key="domain2",
            name="Domain 2",
            calendar_url="https://example.com/cal2.ics",
            status="active"
        )
        domain3 = Domain(
            domain_key="domain3",
            name="Domain 3",
            calendar_url="https://example.com/cal3.ics",
            status="active"
        )
        db_session.add_all([domain1, domain2, domain3])
        db_session.commit()

        # Test each domain
        import asyncio
        result1 = asyncio.run(get_verified_domain(domain="domain1", db=db_session))
        result2 = asyncio.run(get_verified_domain(domain="domain2", db=db_session))
        result3 = asyncio.run(get_verified_domain(domain="domain3", db=db_session))

        assert result1.domain_key == "domain1"
        assert result2.domain_key == "domain2"
        assert result3.domain_key == "domain3"


# Fixtures for testing

@pytest.fixture
def db_session():
    """
    Create a test database session.

    Uses in-memory SQLite database for fast, isolated testing.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base

    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)
