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
from app.database import engine, create_db_and_tables


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