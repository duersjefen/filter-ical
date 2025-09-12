"""
Tests for persistence layer - ensure data survives restarts
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import PersistentStore, CalendarEntry


@pytest.mark.unit
class TestPersistentStore:
    """Test the pickle-based persistence layer"""
    
    def setup_method(self):
        """Create temporary directory for each test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_store_initialization(self):
        """Test store initializes empty (no default fixtures)"""
        store = PersistentStore(data_dir=self.temp_dir)
        
        # Store should start empty
        calendars = store.get_calendars("any_user")
        assert len(calendars) == 0
        
        # Should be able to add calendars normally
        calendar = store.add_calendar("Test Calendar", "http://example.com/cal.ics", "testuser")
        assert calendar.name == "Test Calendar"
        
        # User should see only their calendars
        user_calendars = store.get_calendars("testuser")
        assert len(user_calendars) == 1
        assert user_calendars[0].name == "Test Calendar"
    
    def test_data_persistence_across_restarts(self):
        """Test data survives store restarts"""
        # Create store and add calendar
        store1 = PersistentStore(data_dir=self.temp_dir)
        original_count = len(store1.get_calendars("test_user"))
        
        calendar = store1.add_calendar("Test Calendar", "http://test.com", "test_user")
        assert len(store1.get_calendars("test_user")) == original_count + 1
        
        # Create new store instance (simulating restart)
        store2 = PersistentStore(data_dir=self.temp_dir)
        calendars = store2.get_calendars("test_user")
        
        # Data should persist
        assert len(calendars) == original_count + 1
        test_cal = next((cal for cal in calendars if cal.name == "Test Calendar"), None)
        assert test_cal is not None
        assert test_cal.url == "http://test.com"
    
    def test_filter_persistence(self):
        """Test filter CRUD operations persist"""
        store = PersistentStore(data_dir=self.temp_dir)
        
        # Create filter
        config = {"keywordFilter": "meeting", "sortBy": "date"}
        filter_data = store.add_filter("Work Meetings", config, "test_user")
        
        # Get filters
        filters = store.get_filters("test_user")
        assert len(filters) == 1
        assert filters[0]["name"] == "Work Meetings"
        assert filters[0]["config"]["keywordFilter"] == "meeting"
        
        # Delete filter
        assert store.delete_filter(filter_data["id"], "test_user") == True
        assert len(store.get_filters("test_user")) == 0
        
        # Can't delete other user's filter
        other_filter = store.add_filter("Other Filter", config, "other_user")
        assert store.delete_filter(other_filter["id"], "test_user") == False
        assert len(store.get_filters("other_user")) == 1


@pytest.mark.integration
class TestPersistenceIntegration:
    """Integration tests for persistence with the full application"""
    
    def test_api_persistence_integration(self):
        """Test that API operations persist correctly"""
        # This would test the full API with persistence
        # Implementation depends on how we want to structure integration tests
        pass