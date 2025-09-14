"""
Simple SQLite database functions - following SICP principles
No ORM complexity, just pure functions + SQL
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


def get_db_path() -> Path:
    """Get database file path"""
    return Path("data/app.db")


def init_database() -> None:
    """Initialize database with simple schema"""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                calendar_id TEXT NOT NULL,
                preferences TEXT NOT NULL,  -- JSON
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, calendar_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_user_calendar 
            ON user_preferences(user_id, calendar_id);
        """)


def save_user_preferences(user_id: str, calendar_id: str, preferences: Dict) -> bool:
    """Pure function: save user preferences to database"""
    try:
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_preferences 
                (user_id, calendar_id, preferences, updated_at) 
                VALUES (?, ?, ?, ?)
            """, (user_id, calendar_id, json.dumps(preferences), datetime.now().isoformat()))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error saving preferences: {e}")
        return False


def get_user_preferences(user_id: str, calendar_id: str) -> Optional[Dict]:
    """Pure function: get user preferences from database"""
    try:
        with sqlite3.connect(get_db_path()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT preferences FROM user_preferences 
                WHERE user_id = ? AND calendar_id = ?
            """, (user_id, calendar_id))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['preferences'])
            return None
    except Exception as e:
        print(f"Error loading preferences: {e}")
        return None


def delete_user_preferences(user_id: str, calendar_id: str) -> bool:
    """Pure function: delete user preferences"""
    try:
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("""
                DELETE FROM user_preferences 
                WHERE user_id = ? AND calendar_id = ?
            """, (user_id, calendar_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting preferences: {e}")
        return False


# Helper functions following SICP principles
def validate_preferences(preferences: Dict) -> bool:
    """Pure function: validate preferences structure"""
    required_fields = ["selected_categories", "filter_mode"]
    return all(field in preferences for field in required_fields)


def merge_preferences(existing: Dict, updates: Dict) -> Dict:
    """Pure function: merge preference updates"""
    merged = existing.copy()
    merged.update(updates)
    merged["updated_at"] = datetime.now().isoformat()
    return merged


def delete_all_user_preferences(user_id: str) -> bool:
    """Pure function: delete all preferences for a user (useful for cleanup)"""
    try:
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("""
                DELETE FROM user_preferences 
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting user preferences: {e}")
        return False


def get_all_users() -> list:
    """Pure function: get all unique user IDs (useful for cleanup)"""
    try:
        with sqlite3.connect(get_db_path()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT DISTINCT user_id FROM user_preferences
            """)
            
            rows = cursor.fetchall()
            return [row['user_id'] for row in rows]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []