"""Database configuration and session management for rapid development."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from .config import get_database_url


# Create engine with proper SQLite settings
def create_db_engine(database_url: str):
    """Create database engine with appropriate settings."""
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    
    return create_engine(
        database_url,
        connect_args=connect_args,
        echo=False  # Set to True for SQL logging in development
    )


# Database engine and session
engine = create_db_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy Base class
Base = declarative_base()


def get_db():
    """FastAPI dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables (rapid development approach)."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (for testing)."""
    Base.metadata.drop_all(bind=engine)


def get_session_sync():
    """Get synchronous database session for background tasks and seeding."""
    return SessionLocal()