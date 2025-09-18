"""
Database configuration and session management for SQLite
Following 2025 best practices for FastAPI + SQLModel + SQLite
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from pathlib import Path
import sqlite3

# SQLite database configuration - environment-aware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Default database location
    DATABASE_DIR = Path(__file__).parent.parent / "data"
    DATABASE_DIR.mkdir(exist_ok=True)
    DATABASE_FILE = DATABASE_DIR / "icalviewer.db"
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
    """Create database tables from SQLModel models and run migrations"""
    SQLModel.metadata.create_all(engine)
    
    # Run Alembic migrations automatically
    run_migrations()

def run_migrations():
    """Run Alembic migrations programmatically"""
    try:
        from alembic.config import Config
        from alembic import command
        
        # Get the directory containing this file
        backend_dir = Path(__file__).parent.parent
        alembic_cfg = Config(backend_dir / "alembic.ini")
        
        # Set the script location to the absolute path
        alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
        
        # Set the database URL to match our current engine
        alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))
        
        # Run migrations to the latest version
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed successfully")
        
    except Exception as e:
        print(f"⚠️  Migration warning: {e}")
        # Don't fail startup on migration issues - let the app try to continue

def get_session():
    """
    Dependency for getting database sessions
    Generator function for FastAPI dependency injection
    """
    with Session(engine) as session:
        yield session


def get_session_sync():
    """
    Get synchronous database session for background tasks
    Returns a session that must be closed manually
    """
    return Session(engine)