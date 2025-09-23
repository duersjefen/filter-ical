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
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create test database session with rollback."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def test_client(test_db_session) -> Generator[TestClient, None, None]:
    """
    Create FastAPI test client with test database.
    
    This overrides the database dependency to use our test database
    instead of the production database.
    """
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    # Create app with test settings
    app = create_application()
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Cleanup
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