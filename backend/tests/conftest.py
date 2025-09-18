"""
Test configuration for contract validation tests
Ensures proper database setup with new schema
"""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from sqlmodel import SQLModel

# Load testing environment before importing app modules
load_dotenv(Path(__file__).parent.parent / ".env.testing")

# Import after environment is set
from app.database import engine, create_db_and_tables, get_session
from app.models import Calendar, Event
from datetime import datetime, timedelta


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database with fresh schema"""
    # Ensure we're in testing mode
    os.environ["TESTING"] = "true"
    
    # Create all tables with the new schema
    SQLModel.metadata.drop_all(engine)  # Clean slate
    create_db_and_tables()  # Create with new schema
    
    yield
    
    # Cleanup after tests
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def session():
    """Provide a database session for tests"""
    return next(get_session())


@pytest.fixture
def sample_calendar_with_events(session):
    """Create a sample calendar with test events"""
    # Create test calendar
    calendar = Calendar(
        id="test_cal_123",
        name="Test Calendar",
        url="https://example.com/test.ics",
        user_id="public"
    )
    session.add(calendar)
    session.commit()
    session.refresh(calendar)
    
    # Add sample events
    work_event = Event(
        title="Work Event",
        start=datetime.utcnow() + timedelta(days=1),
        end=datetime.utcnow() + timedelta(days=1, hours=1),
        calendar_id=calendar.id,
        category="Work"
    )
    
    personal_event = Event(
        title="Personal Event", 
        start=datetime.utcnow() + timedelta(days=2),
        end=datetime.utcnow() + timedelta(days=2, hours=2),
        calendar_id=calendar.id,
        category="Personal"
    )
    
    session.add_all([work_event, personal_event])
    session.commit()
    
    return calendar