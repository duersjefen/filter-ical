"""
Test configuration and fixtures for contract-first testing.

This follows industry best practices for FastAPI testing with:
- Isolated test database
- FastAPI TestClient  
- Contract validation fixtures
- Clean test data setup/teardown
"""

import pytest
import yaml
from pathlib import Path
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from openapi_core import Spec, validate_request, validate_response

from app.main import create_application
from app.core.database import Base, get_db
from app.core.config import settings


# FastAPI adapters for openapi-core 0.18
class FastAPIRequestAdapter:
    """Adapter to make FastAPI TestClient requests compatible with openapi-core protocols."""
    
    def __init__(self, request):
        self._request = request
    
    @property
    def method(self):
        return self._request.method
    
    @property
    def url(self):
        return str(self._request.url)
    
    @property
    def headers(self):
        return dict(self._request.headers)
    
    @property
    def content_type(self):
        return self._request.headers.get('content-type', '')
    
    @property
    def body(self):
        # For TestClient, we can get the body from the request
        return getattr(self._request, '_body', b'')
    
    @property
    def data(self):
        return self.body


class FastAPIResponseAdapter:
    """Adapter to make FastAPI responses compatible with openapi-core protocols."""
    
    def __init__(self, response):
        self._response = response
    
    @property
    def status_code(self):
        return self._response.status_code
    
    @property
    def headers(self):
        return dict(self._response.headers)
    
    @property
    def content_type(self):
        return self._response.headers.get('content-type', '')
    
    @property
    def body(self):
        return self._response.content
    
    @property
    def data(self):
        return self.body


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    # Use in-memory SQLite for speed
    # StaticPool ensures all connections share the same in-memory database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Import all models to register them with SQLAlchemy
    from app.models import (
        Calendar, Event, Group, RecurringEventGroup, AssignmentRule, Filter,
        DomainRequest, Domain, AppSettings, User, UserDomainAccess, DomainBackup
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


# Removed test_db_session - test_client now uses test_db_engine directly


@pytest.fixture(scope="function")
def test_client(test_db_engine) -> Generator[TestClient, None, None]:
    """
    Create FastAPI test client with test database.
    
    This overrides the database dependency to use our test database
    instead of the production database.
    """
    # Create a single session that will be shared across all requests
    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    
    # Create ONE session for the entire test
    shared_session = TestingSessionLocal()
    
    def override_get_db():
        try:
            yield shared_session
        finally:
            # Don't close the session here - we'll close it at the end of the test
            pass
    
    # Import FastAPI and create minimal app without lifespan for testing
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.core.config import settings
    
    # Create test app without the problematic lifespan
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        # No lifespan for tests - we'll manage database state ourselves
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Override database dependency BEFORE importing routers
    app.dependency_overrides[get_db] = override_get_db
    
    # Import and include routers
    from app.routers import (
        calendars, domains, ical_export, test, domain_requests, admin,
        domain_assignment_rules, domain_config, domain_backups, domain_admins,
        users, auth, domain_auth, ical, filters, domain_events, domain_groups,
        domain_filters
    )
    # User and auth endpoints (paths already include /api prefix in router)
    app.include_router(users.router, tags=["users"])
    app.include_router(auth.router, tags=["auth"])

    # Calendar endpoints
    app.include_router(calendars.router, prefix="/api/calendars", tags=["calendars"])
    app.include_router(filters.router, prefix="/api/filters", tags=["filters"])

    # Domain endpoints
    app.include_router(domains.router, prefix="/api/domains", tags=["domains"])
    app.include_router(domain_events.router, prefix="/api/domains", tags=["domains"])
    app.include_router(domain_groups.router, prefix="/api/domains", tags=["domains"])
    app.include_router(domain_filters.router, prefix="/api/domains", tags=["domains"])
    app.include_router(domain_assignment_rules.router, prefix="/api/domains", tags=["domains"])
    app.include_router(domain_config.router, prefix="/api/domains", tags=["domains"])
    app.include_router(domain_backups.router, prefix="/api/domains", tags=["domains"])
    app.include_router(domain_admins.router, prefix="/api/domains", tags=["domains"])
    app.include_router(domain_auth.router, prefix="/api/domains", tags=["domains"])

    # iCal endpoints
    app.include_router(ical.router, prefix="/api/ical", tags=["ical"])
    app.include_router(ical_export.router, prefix="/ical", tags=["ical_export"])

    # Admin and test endpoints
    app.include_router(domain_requests.router, prefix="/api", tags=["domain_requests"])
    app.include_router(admin.router, prefix="/api", tags=["admin"])
    app.include_router(test.router, prefix="/test", tags=["test"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {"status": "healthy", "app": settings.app_name}
    
    with TestClient(app) as client:
        yield client
    
    # Cleanup - now we can safely close the session
    shared_session.close()
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def openapi_spec() -> Dict[str, Any]:
    """Load OpenAPI specification for contract testing."""
    spec_path = Path(__file__).parent.parent / "openapi.yaml"
    with open(spec_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def openapi_validator(openapi_spec) -> Spec:
    """Create OpenAPI validator for contract testing."""
    return Spec.from_dict(openapi_spec)


@pytest.fixture
def sample_calendar_data():
    """Sample calendar data for testing."""
    return {
        "name": "Test Calendar",
        "source_url": "https://example.com/test.ics"
    }


@pytest.fixture
def sample_domain_filter_data():
    """Sample domain filter data for testing."""
    return {
        "name": "Test Domain Filter",
        "subscribed_event_ids": [1, 2],
        "subscribed_group_ids": [1]
    }


@pytest.fixture
def sample_user_filter_data():
    """Sample user filter data for testing."""
    return {
        "name": "Test User Filter",
        "subscribed_event_ids": [1, 2, 3]
    }


@pytest.fixture
def test_db(test_db_engine):
    """Provide database session for tests that need direct DB access."""
    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user(test_db):
    """Create a test user in the database."""
    from app.models.user import User
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role="user"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_token():
    """Generate admin JWT token for testing."""
    from app.core.auth import create_admin_token
    return create_admin_token(expiry_days=1)


@pytest.fixture
def sample_filter(test_db, test_user):
    """Create a sample filter with calendar and events for testing iCal export."""
    from app.models import Calendar, Filter, Event
    from datetime import datetime, timezone, timedelta

    # Create a calendar
    calendar = Calendar(
        name="Test Calendar",
        source_url="https://example.com/test.ics",
        type="user",
        user_id=test_user.id,
        last_fetched=datetime.now(timezone.utc)
    )
    test_db.add(calendar)
    test_db.commit()
    test_db.refresh(calendar)

    # Add some test events
    now = datetime.now(timezone.utc)
    for i in range(3):
        event = Event(
            calendar_id=calendar.id,
            title=f"Test Event {i+1}",
            start_time=now + timedelta(days=i),
            end_time=now + timedelta(days=i, hours=1),
            description=f"Description for event {i+1}",
            location="Test Location",
            uid=f"test-event-{i+1}@example.com",
            updated_at=now,
            other_ical_fields={}
        )
        test_db.add(event)

    test_db.commit()

    # Create a filter for the calendar
    filter_obj = Filter(
        name="Test Filter",
        calendar_id=calendar.id,
        link_uuid="550e8400-e29b-41d4-a716-446655440000",
        subscribed_event_ids=[],
        unselected_event_ids=[],
        include_future_events=True
    )
    test_db.add(filter_obj)
    test_db.commit()
    test_db.refresh(filter_obj)

    return filter_obj


@pytest.fixture
def test_domain(test_client):
    """Create a test domain with password for assignment rule testing.

    Uses the test_client's shared session to avoid cross-session issues.
    """
    from app.models.domain import Domain
    from app.core.database import get_db
    import bcrypt

    # Get the shared session from test_client
    shared_session = next(test_client.app.dependency_overrides[get_db]())

    # Clear any existing domain with the same key (for test isolation)
    existing_domain = shared_session.query(Domain).filter(Domain.domain_key == "testdomain").first()
    if existing_domain:
        shared_session.delete(existing_domain)
        shared_session.commit()

    # Hash password using bcrypt (same as domain_auth_service)
    password_hash = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    domain = Domain(
        name="Test Domain",
        domain_key="testdomain",
        calendar_url="https://example.com/test.ics",
        admin_password_hash=password_hash,
        status="active"
    )
    shared_session.add(domain)
    shared_session.commit()
    shared_session.refresh(domain)
    return domain


@pytest.fixture
def test_group(test_client, test_domain):
    """Create a test group for assignment rule testing.

    Uses the test_client's shared session to avoid cross-session issues.
    """
    from app.models.calendar import Group
    from app.core.database import get_db

    # Get the shared session from test_client
    shared_session = next(test_client.app.dependency_overrides[get_db]())

    group = Group(
        domain_id=test_domain.id,
        domain_key=test_domain.domain_key,
        name="Test Group"
    )
    shared_session.add(group)
    shared_session.commit()
    shared_session.refresh(group)
    return group