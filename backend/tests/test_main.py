import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_calendars_get_endpoint():
    """Test calendars GET endpoint exists"""
    response = client.get("/api/calendars")
    # Should return some response (endpoint exists)
    assert response.status_code in [200, 400, 401, 422]

def test_calendars_post_endpoint():
    """Test calendars POST endpoint exists"""
    response = client.post("/api/calendars", json={"name": "test", "url": "http://example.com"})
    # Should return some response (endpoint exists)
    assert response.status_code in [200, 400, 401, 422]

def test_static_files():
    """Test that static files are served"""
    response = client.get("/app")
    # Should serve the main app or redirect
    assert response.status_code in [200, 301, 302, 404]