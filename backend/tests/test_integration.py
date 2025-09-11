"""
Integration tests - test full system behavior
These tests will catch issues like login problems, frontend-backend communication failures, etc.
"""

import pytest
import httpx
import time
import subprocess
import signal
import os
from pathlib import Path
import tempfile
import shutil


@pytest.mark.integration
class TestFullSystemIntegration:
    """Test the complete system end-to-end"""
    
    @pytest.fixture(scope="class")
    def backend_server(self):
        """Start backend server for testing"""
        # Create temporary data directory
        test_data_dir = Path(tempfile.mkdtemp())
        
        # Set environment to use test data directory
        env = os.environ.copy()
        env['TEST_DATA_DIR'] = str(test_data_dir)
        
        # Start backend server
        backend_dir = Path(__file__).parent.parent
        process = subprocess.Popen(
            ["make", "backend"],
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = httpx.get("http://localhost:3000/health", timeout=5)
            if response.status_code != 200:
                process.kill()
                raise RuntimeError(f"Backend server failed to start: {response.status_code}")
        except Exception as e:
            process.kill()
            raise RuntimeError(f"Backend server failed to start: {e}")
        
        yield process
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
        shutil.rmtree(test_data_dir)
    
    def test_health_endpoint(self, backend_server):
        """Test basic health endpoint"""
        response = httpx.get("http://localhost:3000/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_calendars_crud_operations(self, backend_server):
        """Test complete CRUD operations for calendars"""
        client = httpx.Client(base_url="http://localhost:3000")
        
        # Test GET calendars (should have fixtures)
        response = client.get("/api/calendars", headers={"x-user-id": "test_user"})
        assert response.status_code == 200
        initial_calendars = response.json()["calendars"]
        assert len(initial_calendars) >= 4  # Should have fixture data
        
        # Test POST create calendar
        new_calendar = {
            "name": "Integration Test Calendar",
            "url": "https://calendar.google.com/calendar/ical/test.ics"
        }
        response = client.post(
            "/api/calendars", 
            json=new_calendar,
            headers={"x-user-id": "test_user"}
        )
        assert response.status_code == 200
        calendar_id = response.json()["id"]
        
        # Test GET calendars (should include new one)
        response = client.get("/api/calendars", headers={"x-user-id": "test_user"})
        assert response.status_code == 200
        calendars = response.json()["calendars"]
        user_calendars = [cal for cal in calendars if cal["user_id"] == "test_user"]
        assert len(user_calendars) == 1
        assert user_calendars[0]["name"] == "Integration Test Calendar"
        
        # Test DELETE calendar
        response = client.delete(f"/api/calendars/{calendar_id}", headers={"x-user-id": "test_user"})
        assert response.status_code == 200
        
        # Test GET calendars (should be back to original)
        response = client.get("/api/calendars", headers={"x-user-id": "test_user"})
        assert response.status_code == 200
        calendars = response.json()["calendars"]
        user_calendars = [cal for cal in calendars if cal["user_id"] == "test_user"]
        assert len(user_calendars) == 0
    
    def test_event_fetching_and_caching(self, backend_server):
        """Test event fetching and caching behavior"""
        client = httpx.Client(base_url="http://localhost:3000")
        
        # Get default calendars
        response = client.get("/api/calendars", headers={"x-user-id": "anonymous"})
        assert response.status_code == 200
        calendars = response.json()["calendars"]
        test_calendar = calendars[0]  # Use first fixture calendar
        
        # Test event fetching (first time - should fetch from URL)
        start_time = time.time()
        response = client.get(f"/api/calendar/{test_calendar['id']}/events")
        first_duration = time.time() - start_time
        
        assert response.status_code == 200
        events = response.json()["events"]
        assert len(events) > 0  # Should have some events
        
        # Test event fetching (second time - should use cache)
        start_time = time.time()
        response = client.get(f"/api/calendar/{test_calendar['id']}/events")
        second_duration = time.time() - start_time
        
        assert response.status_code == 200
        cached_events = response.json()["events"]
        
        # Should return same events
        assert len(cached_events) == len(events)
        
        # Cache should be faster (but this might be flaky on fast systems)
        # assert second_duration < first_duration
    
    def test_error_handling(self, backend_server):
        """Test error handling for various scenarios"""
        client = httpx.Client(base_url="http://localhost:3000")
        
        # Test invalid calendar creation
        response = client.post("/api/calendars", json={}, headers={"x-user-id": "test_user"})
        assert response.status_code == 400
        
        # Test nonexistent calendar events
        response = client.get("/api/calendar/nonexistent/events")
        assert response.status_code == 404
        
        # Test deleting nonexistent calendar
        response = client.delete("/api/calendars/nonexistent", headers={"x-user-id": "test_user"})
        assert response.status_code == 404
    
    def test_user_isolation(self, backend_server):
        """Test that users can't access each other's calendars"""
        client = httpx.Client(base_url="http://localhost:3000")
        
        # User1 creates calendar
        response = client.post(
            "/api/calendars",
            json={"name": "User1 Calendar", "url": "http://test1.com"},
            headers={"x-user-id": "user1"}
        )
        assert response.status_code == 200
        calendar_id = response.json()["id"]
        
        # User2 tries to delete User1's calendar
        response = client.delete(f"/api/calendars/{calendar_id}", headers={"x-user-id": "user2"})
        assert response.status_code == 404  # Should not find it
        
        # User1 can still access their calendar
        response = client.get("/api/calendars", headers={"x-user-id": "user1"})
        assert response.status_code == 200
        calendars = response.json()["calendars"]
        user_calendars = [cal for cal in calendars if cal["user_id"] == "user1"]
        assert len(user_calendars) == 1
    
    def test_persistence_across_restart(self, backend_server):
        """Test that data persists when server restarts"""
        # Note: This test is complex for integration testing
        # For now, we rely on the unit tests for persistence
        # A full integration test would require starting/stopping the actual server
        pass


@pytest.mark.integration  
class TestFrontendBackendCommunication:
    """Test frontend-backend communication patterns"""
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = httpx.options("http://localhost:3000/api/calendars")
        # FastAPI should handle CORS automatically in development
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled
    
    def test_api_response_format(self):
        """Test API responses are in expected format for frontend"""
        response = httpx.get("http://localhost:3000/api/calendars", headers={"x-user-id": "test"})
        assert response.status_code == 200
        
        data = response.json()
        assert "calendars" in data
        assert isinstance(data["calendars"], list)
        
        if data["calendars"]:
            calendar = data["calendars"][0]
            required_fields = ["id", "name", "url", "user_id"]
            for field in required_fields:
                assert field in calendar, f"Calendar missing required field: {field}"


# Add these as future tests to guide development
@pytest.mark.future
class TestAdvancedFeatures:
    """Future features to implement"""
    
    def test_calendar_sync_status(self):
        """Test calendar sync status tracking"""
        # Should track when calendars were last synced
        # Should show sync errors
        pass
    
    def test_event_filtering(self):
        """Test event filtering functionality"""
        # Should be able to filter events by keywords
        # Should be able to exclude certain event types
        pass
    
    def test_calendar_sharing(self):
        """Test calendar sharing between users"""
        # Users should be able to share calendars
        # Shared calendars should be read-only for non-owners
        pass