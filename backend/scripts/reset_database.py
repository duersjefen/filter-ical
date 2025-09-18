#!/usr/bin/env python3
"""
Clean Database Reset Script
For use during development and early deployment (no users yet)
"""
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, DATABASE_URL
from app.models import SQLModel

def reset_database():
    """
    Clean database reset - drops all tables and recreates from models
    WARNING: This destroys all data! Only use when no users exist.
    """
    print("🗄️  Clean Database Reset")
    print("=" * 50)
    
    print(f"📍 Database URL: {DATABASE_URL}")
    
    # Drop all existing tables
    print("🧹 Dropping all existing tables...")
    SQLModel.metadata.drop_all(engine)
    print("✅ All tables dropped")
    
    # Create fresh tables from models
    print("🔨 Creating fresh tables from models...")
    SQLModel.metadata.create_all(engine)
    print("✅ Fresh database schema created")
    
    print("")
    print("🎉 Database reset complete!")
    print("💡 All tables now match your latest model definitions")

if __name__ == "__main__":
    reset_database()