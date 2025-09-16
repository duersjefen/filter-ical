"""
Database configuration and session management for SQLite
Following 2025 best practices for FastAPI + SQLModel + SQLite
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from pathlib import Path
import sqlite3

# SQLite database file location
DATABASE_DIR = Path(__file__).parent.parent / "data"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_FILE = DATABASE_DIR / "icalviewer.db"

# SQLite connection string with optimizations
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Create engine with SQLite-specific optimizations
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Required for FastAPI
        "timeout": 20
    },
    echo=False  # Set to True for SQL debugging
)

# Enable WAL mode and foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        # Enable Write-Ahead Logging for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys=ON")
        # Optimize SQLite settings
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

def create_db_and_tables():
    """Create database tables from SQLModel models"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency for getting database sessions
    Generator function for FastAPI dependency injection
    """
    with Session(engine) as session:
        yield session