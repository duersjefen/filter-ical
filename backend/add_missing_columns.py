#!/usr/bin/env python3
"""
Development utility to add missing database columns.
Run this when schema changes are made during development.
"""

import sqlite3
from pathlib import Path

def add_include_future_events_column():
    """Add include_future_events column to filters table."""
    db_path = Path(__file__).parent / "data" / "calendar.db"

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(filters)")
        columns = [row[1] for row in cursor.fetchall()]

        if "include_future_events" in columns:
            print("✅ Column 'include_future_events' already exists")
            conn.close()
            return True

        # Add the column
        print("➕ Adding 'include_future_events' column to filters table...")
        cursor.execute("""
            ALTER TABLE filters
            ADD COLUMN include_future_events BOOLEAN DEFAULT 0
        """)

        conn.commit()
        conn.close()

        print("✅ Column added successfully!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding missing database columns...")
    add_include_future_events_column()
    print("✅ Done!")