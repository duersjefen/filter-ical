"""
Test user flow scenarios that would catch "login" type issues
"""

import pytest
import httpx


@pytest.mark.integration
class TestUserFlow:
    """Test actual user flow scenarios"""
    
    def test_anonymous_user_sees_default_calendars(self):
        """Test that anonymous users see default calendars (simulates page load)"""
        response = httpx.get(
            "http://localhost:3000/api/calendars", 
            headers={"x-user-id": "anonymous"}
        )
        assert response.status_code == 200
        
        calendars = response.json()["calendars"]
        assert len(calendars) >= 4
        
        # All should be default calendars
        for calendar in calendars:
            assert calendar["user_id"] == "default"
    
    def test_different_users_see_different_data(self):
        """Test user isolation (this would catch login/session issues)"""
        client = httpx.Client(base_url="http://localhost:3000")
        
        # User1 creates a calendar
        response = client.post(
            "/api/calendars",
            json={"name": "User1 Private Calendar", "url": "http://user1.com/cal.ics"},
            headers={"x-user-id": "user1"}
        )
        assert response.status_code == 200
        
        # User1 sees their calendar + defaults
        response = client.get("/api/calendars", headers={"x-user-id": "user1"})
        user1_calendars = response.json()["calendars"]
        user1_private = [cal for cal in user1_calendars if cal["user_id"] == "user1"]
        assert len(user1_private) == 1
        
        # User2 only sees defaults (not User1's private calendar)
        response = client.get("/api/calendars", headers={"x-user-id": "user2"})
        user2_calendars = response.json()["calendars"]
        user2_private = [cal for cal in user2_calendars if cal["user_id"] == "user1"]
        assert len(user2_private) == 0  # Should not see User1's calendar
    
    def test_user_header_is_respected(self):
        """Test that the x-user-id header actually affects the response"""
        client = httpx.Client(base_url="http://localhost:3000")
        
        # Create calendar as specific user
        response = client.post(
            "/api/calendars",
            json={"name": "Test Calendar", "url": "http://test.com/cal.ics"},
            headers={"x-user-id": "test_user_123"}
        )
        assert response.status_code == 200
        calendar_id = response.json()["id"]
        
        # Same user can delete it
        response = client.delete(
            f"/api/calendars/{calendar_id}",
            headers={"x-user-id": "test_user_123"}
        )
        assert response.status_code == 200
        
        # Different user cannot delete it (simulate calendar creation again)
        response = client.post(
            "/api/calendars",
            json={"name": "Test Calendar 2", "url": "http://test2.com/cal.ics"},
            headers={"x-user-id": "test_user_123"}
        )
        calendar_id = response.json()["id"]
        
        response = client.delete(
            f"/api/calendars/{calendar_id}",
            headers={"x-user-id": "different_user"}
        )
        assert response.status_code == 404  # Should not be able to delete
    
    def test_missing_user_header_defaults_to_anonymous(self):
        """Test behavior when user header is missing"""
        response = httpx.get("http://localhost:3000/api/calendars")  # No header
        assert response.status_code == 200
        
        # Should behave like anonymous user
        calendars = response.json()["calendars"] 
        for calendar in calendars:
            assert calendar["user_id"] == "default"


@pytest.mark.unit
class TestAuthenticationLogic:
    """Unit tests for authentication-related logic"""
    
    def test_user_id_extraction(self):
        """Test user ID extraction from headers"""
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test with explicit user ID
        response = client.get("/api/calendars", headers={"x-user-id": "test123"})
        assert response.status_code == 200
        
        # Test without user ID (should default to anonymous)
        response = client.get("/api/calendars")
        assert response.status_code == 200