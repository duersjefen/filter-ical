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
    """Run Alembic migrations programmatically with fallback repair"""
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
        print(f"⚠️  Migration failed: {e}")
        print("🔧 Attempting manual database repair...")
        
        # Fallback: Manual database repair
        try:
            _repair_database_manually()
            print("✅ Manual database repair completed successfully")
        except Exception as repair_error:
            print(f"❌ Manual repair also failed: {repair_error}")
            # Don't fail startup - let the app try to continue

def _repair_database_manually():
    """Manually add missing columns and indexes as fallback"""
    import sqlite3
    from sqlalchemy import text
    
    # Extract database path from engine URL
    db_url = str(engine.url)
    if "sqlite:///" in db_url:
        db_path = db_url.replace("sqlite:///", "")
        
        # Use SQLAlchemy connection instead of direct sqlite3
        with engine.connect() as conn:
            # Check and add missing columns to calendars table
            try:
                conn.execute(text("ALTER TABLE calendars ADD COLUMN cached_ical_content TEXT"))
                print("➕ Added column: calendars.cached_ical_content")
            except:
                pass  # Column already exists
            
            try:
                conn.execute(text("ALTER TABLE calendars ADD COLUMN cached_content_hash TEXT"))
                print("➕ Added column: calendars.cached_content_hash")
            except:
                pass  # Column already exists
            
            try:
                conn.execute(text("ALTER TABLE calendars ADD COLUMN cache_updated_at DATETIME"))
                print("➕ Added column: calendars.cache_updated_at")
            except:
                pass  # Column already exists
            
            try:
                conn.execute(text("ALTER TABLE calendars ADD COLUMN cache_expires_at DATETIME"))
                print("➕ Added column: calendars.cache_expires_at")
            except:
                pass  # Column already exists
            
            try:
                conn.execute(text("ALTER TABLE filtered_calendars ADD COLUMN needs_regeneration BOOLEAN DEFAULT 0"))
                print("➕ Added column: filtered_calendars.needs_regeneration")
            except:
                pass  # Column already exists
                
            # Create indexes (using IF NOT EXISTS)
            indexes = [
                "CREATE INDEX IF NOT EXISTS ix_calendars_cache_expires_at ON calendars (cache_expires_at)",
                "CREATE INDEX IF NOT EXISTS ix_calendars_cache_updated_at ON calendars (cache_updated_at)",
                "CREATE INDEX IF NOT EXISTS ix_calendars_domain_id ON calendars (domain_id)",
                "CREATE INDEX IF NOT EXISTS ix_filtered_calendars_needs_regeneration ON filtered_calendars (needs_regeneration)"
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except:
                    pass  # Index already exists
            
            conn.commit()
    else:
        print("⚠️  Non-SQLite database detected, skipping manual repair")

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