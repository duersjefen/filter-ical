#!/usr/bin/env python3
"""
Emergency database repair script for production
Adds missing columns and indexes that should have been created by migration
"""
import sqlite3
import sys
from pathlib import Path

def check_column_exists(cursor, table, column):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def check_index_exists(cursor, index_name):
    """Check if an index exists"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index_name,))
    return cursor.fetchone() is not None

def repair_database(db_path):
    """Repair database by adding missing columns and indexes"""
    print(f"🔧 Repairing database: {db_path}")
    
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current database structure
        print("📋 Checking current database structure...")
        
        # Add missing columns to calendars table
        missing_columns = [
            ('cached_ical_content', 'TEXT'),
            ('cached_content_hash', 'TEXT'),
            ('cache_updated_at', 'DATETIME'),
            ('cache_expires_at', 'DATETIME')
        ]
        
        for column, type_def in missing_columns:
            if not check_column_exists(cursor, 'calendars', column):
                print(f"➕ Adding missing column: calendars.{column}")
                cursor.execute(f"ALTER TABLE calendars ADD COLUMN {column} {type_def}")
            else:
                print(f"✅ Column exists: calendars.{column}")
        
        # Add missing column to filtered_calendars table
        if not check_column_exists(cursor, 'filtered_calendars', 'needs_regeneration'):
            print("➕ Adding missing column: filtered_calendars.needs_regeneration")
            cursor.execute("ALTER TABLE filtered_calendars ADD COLUMN needs_regeneration BOOLEAN DEFAULT 0")
        else:
            print("✅ Column exists: filtered_calendars.needs_regeneration")
        
        # Add missing indexes
        indexes = [
            ('ix_calendars_cache_expires_at', 'CREATE INDEX IF NOT EXISTS ix_calendars_cache_expires_at ON calendars (cache_expires_at)'),
            ('ix_calendars_cache_updated_at', 'CREATE INDEX IF NOT EXISTS ix_calendars_cache_updated_at ON calendars (cache_updated_at)'),
            ('ix_calendars_domain_id', 'CREATE INDEX IF NOT EXISTS ix_calendars_domain_id ON calendars (domain_id)'),
            ('ix_filtered_calendars_needs_regeneration', 'CREATE INDEX IF NOT EXISTS ix_filtered_calendars_needs_regeneration ON filtered_calendars (needs_regeneration)')
        ]
        
        for index_name, create_sql in indexes:
            if not check_index_exists(cursor, index_name):
                print(f"➕ Creating missing index: {index_name}")
                cursor.execute(create_sql)
            else:
                print(f"✅ Index exists: {index_name}")
        
        # Commit changes
        conn.commit()
        print("✅ Database repair completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database repair failed: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function to repair database"""
    # Try different possible database locations
    possible_paths = [
        "/opt/websites/apps/ical-viewer/data/icalviewer.db",
        "./data/icalviewer.db",
        "../data/icalviewer.db"
    ]
    
    if len(sys.argv) > 1:
        possible_paths.insert(0, sys.argv[1])
    
    for db_path in possible_paths:
        if Path(db_path).exists():
            print(f"🎯 Found database at: {db_path}")
            if repair_database(db_path):
                print("🎉 Database repair successful!")
                return 0
            else:
                print("💥 Database repair failed!")
                return 1
    
    print("❌ No database file found at any of the expected locations:")
    for path in possible_paths:
        print(f"   - {path}")
    return 1

if __name__ == "__main__":
    sys.exit(main())