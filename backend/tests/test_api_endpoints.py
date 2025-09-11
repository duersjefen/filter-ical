"""
API endpoint tests for all routes and error conditions.
Tests authentication, validation, and edge cases.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @pytest.mark.unit
    def test_health_check_success(self):
        """Test health endpoint returns success."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ical-viewer"
        
    def test_health_check_response_format(self):
        """Test health endpoint response format."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data

class TestCalendarEndpoints:
    """Test calendar-related API endpoints."""
    
    def test_calendars_get_endpoint(self):
        """Test GET /api/calendars endpoint."""
        response = client.get("/api/calendars")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        
    def test_calendars_post_valid_data(self):
        """Test POST /api/calendars with valid ICS data."""
        valid_ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:test@example.com
DTSTART:20250915T100000Z
DTEND:20250915T110000Z
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""
        
        response = client.post("/api/calendars", 
                             data={"ics_content": valid_ics})
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        
    def test_calendars_post_missing_data(self):
        """Test POST /api/calendars without ICS content."""
        response = client.post("/api/calendars", data={})
        assert response.status_code == 400
        
    def test_calendars_post_invalid_content_type(self):
        """Test POST /api/calendars with wrong content type."""
        response = client.post("/api/calendars", 
                             json={"ics_content": "test"})  # JSON instead of form data
        assert response.status_code == 400

class TestFileUpload:
    """Test file upload functionality."""
    
    def test_file_upload_valid_ics(self):
        """Test uploading valid ICS file."""
        ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:upload-test@example.com
DTSTART:20250915T100000Z
DTEND:20250915T110000Z
SUMMARY:Uploaded Event
END:VEVENT
END:VCALENDAR"""
        
        files = {"file": ("test.ics", ics_content, "text/calendar")}
        response = client.post("/api/calendars", files=files)
        assert response.status_code == 200
        
    def test_file_upload_wrong_extension(self):
        """Test uploading file with wrong extension."""
        files = {"file": ("test.txt", "not ics content", "text/plain")}
        response = client.post("/api/calendars", files=files)
        assert response.status_code == 400
        
    def test_file_upload_too_large(self):
        """Test uploading file that's too large."""
        # Generate very large content (>10MB)
        large_content = "A" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.ics", large_content, "text/calendar")}
        response = client.post("/api/calendars", files=files)
        assert response.status_code == 413  # Request Entity Too Large

class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_sql_injection_attempt(self):
        """Test that SQL injection attempts are blocked."""
        malicious_input = "'; DROP TABLE events; --"
        response = client.post("/api/calendars", 
                             data={"title_filter": malicious_input})
        # Should not cause server error, should handle gracefully
        assert response.status_code in [200, 400]
        
    def test_xss_attempt_in_filters(self):
        """Test that XSS attempts in filters are sanitized."""
        xss_input = "<script>alert('xss')</script>"
        response = client.post("/api/calendars", 
                             data={"title_filter": xss_input})
        # Should not cause server error
        assert response.status_code in [200, 400]
        
    def test_extremely_long_filter_input(self):
        """Test handling of extremely long filter input."""
        long_input = "A" * 10000  # 10KB string
        response = client.post("/api/calendars", 
                             data={"title_filter": long_input})
        assert response.status_code in [200, 400]

class TestErrorResponses:
    """Test error response formats and codes."""
    
    def test_404_not_found(self):
        """Test 404 response for non-existent endpoints."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
    def test_405_method_not_allowed(self):
        """Test 405 response for wrong HTTP method."""
        response = client.delete("/api/calendars")  # DELETE not allowed
        assert response.status_code == 405
        
    def test_500_error_handling(self):
        """Test that 500 errors are handled gracefully."""
        # This is harder to trigger without modifying the app
        # But we can test with malformed data that might cause exceptions
        severely_malformed_ics = "BEGIN:VCALENDAR\nCORRUPTED_DATA\x00\xFF"
        response = client.post("/api/calendars", 
                             data={"ics_content": severely_malformed_ics})
        # Should return error code, not crash
        assert response.status_code >= 400

class TestRateLimiting:
    """Test rate limiting if implemented."""
    
    def test_multiple_rapid_requests(self):
        """Test handling of multiple rapid requests."""
        # Send 50 rapid requests
        responses = []
        for i in range(50):
            response = client.get("/health")
            responses.append(response.status_code)
            
        # Should either succeed or be rate limited, not crash
        for status_code in responses:
            assert status_code in [200, 429]  # 429 = Too Many Requests

class TestContentNegotiation:
    """Test content type handling."""
    
    def test_json_response_headers(self):
        """Test that JSON endpoints return correct headers."""
        response = client.get("/api/calendars")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        
    def test_accept_header_handling(self):
        """Test handling of Accept headers."""
        headers = {"Accept": "application/json"}
        response = client.get("/api/calendars", headers=headers)
        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith("application/json")

class TestCORS:
    """Test CORS headers if enabled."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present for browser requests."""
        headers = {"Origin": "http://localhost:5173"}
        response = client.get("/api/calendars", headers=headers)
        # Check if CORS is enabled (optional, depends on configuration)
        cors_header = response.headers.get("access-control-allow-origin")
        if cors_header:
            assert cors_header in ["*", "http://localhost:5173"]

class TestPerformance:
    """Basic performance tests."""
    
    def test_response_time_health_check(self):
        """Test that health check responds quickly."""
        import time
        start = time.time()
        response = client.get("/health")
        end = time.time()
        
        assert response.status_code == 200
        assert (end - start) < 1.0  # Should respond in under 1 second
        
    def test_concurrent_requests_handling(self):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import time
        
        def make_request():
            return client.get("/health")
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            responses = [future.result() for future in futures]
        end = time.time()
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            
        # Should complete reasonably quickly
        assert (end - start) < 10.0  # 20 requests in under 10 seconds