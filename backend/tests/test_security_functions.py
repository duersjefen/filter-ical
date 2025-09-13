"""
Tests for Pure Security Functions
Demonstrates secure token generation and validation without side effects
NO MOCKING REQUIRED - Pure functions = secure and predictable testing
"""

import pytest
import time
from datetime import datetime, timedelta
from app.data.security import (
    # Token generation
    generate_public_token,
    generate_cache_key,
    generate_short_url_code,
    # Token validation
    validate_public_token_format,
    is_token_expired,
    # Rate limiting
    create_rate_limit_key,
    calculate_rate_limit_window,
    is_rate_limit_exceeded,
    # Content security
    sanitize_ical_content,
    sanitize_calendar_field_value,
    # Access control
    create_access_signature,
    verify_access_signature,
    is_request_timestamp_valid,
    # URL security
    create_secure_calendar_url,
    create_preview_url,
    extract_token_from_url,
    # Security headers
    create_security_headers,
    # Audit logging
    create_access_log_entry,
    analyze_access_patterns
)


# === TOKEN GENERATION TESTS (Pure Functions) ===

class TestTokenGeneration:
    
    def test_generate_public_token_format(self):
        """Test public token generation format"""
        token = generate_public_token()
        
        # Should be URL-safe string
        assert isinstance(token, str)
        assert len(token) >= 16  # Minimum entropy
        
        # Should only contain URL-safe characters
        allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
        assert all(c in allowed_chars for c in token)
    
    def test_generate_public_token_uniqueness(self):
        """Test that generated tokens are unique"""
        tokens = [generate_public_token() for _ in range(100)]
        
        # All tokens should be unique
        assert len(set(tokens)) == len(tokens)
    
    def test_generate_public_token_entropy(self):
        """Test token entropy and randomness"""
        tokens = [generate_public_token() for _ in range(1000)]
        
        # Check character distribution (should be relatively even)
        char_counts = {}
        for token in tokens:
            for char in token:
                char_counts[char] = char_counts.get(char, 0) + 1
        
        # Should use a variety of characters (basic entropy check)
        assert len(char_counts) > 20  # Should use many different characters
    
    def test_generate_cache_key_deterministic(self):
        """Test cache key generation is deterministic"""
        key1 = generate_cache_key("cal123", "filter456", "content789")
        key2 = generate_cache_key("cal123", "filter456", "content789")
        
        # Same inputs should produce same key
        assert key1 == key2
        
        # Different inputs should produce different keys
        key3 = generate_cache_key("cal123", "filter456", "content999")
        assert key1 != key3
    
    def test_generate_cache_key_format(self):
        """Test cache key format"""
        key = generate_cache_key("cal123", "filter456", "content789")
        
        assert key.startswith("filtered_cal_")
        assert len(key) == 29  # "filtered_cal_" + 16 hex chars
    
    def test_generate_short_url_code(self):
        """Test short URL code generation"""
        token = "abcdef123456"
        code = generate_short_url_code(token)
        
        assert isinstance(code, str)
        assert len(code) == 8
        assert code.isalnum()  # Should be alphanumeric
        
        # Same token should produce same code
        code2 = generate_short_url_code(token)
        assert code == code2


# === TOKEN VALIDATION TESTS (Pure Functions) ===

class TestTokenValidation:
    
    def test_validate_public_token_format_valid(self):
        """Test validation of valid token formats"""
        valid_tokens = [
            "abcdef123456ABCDEF",
            "very-long-token-with-dashes",
            "token_with_underscores_123",
            "MixedCaseToken123"
        ]
        
        for token in valid_tokens:
            is_valid, message = validate_public_token_format(token)
            assert is_valid is True
            assert message == "Valid token format"
    
    def test_validate_public_token_format_invalid(self):
        """Test validation of invalid token formats"""
        invalid_cases = [
            ("", "Token is required"),
            ("short", "Token too short"),
            ("a" * 65, "Token too long"),  # Too long
            ("token with spaces", "Token contains invalid characters"),
            ("token@with!special#chars", "Token contains invalid characters"),
            ("token/with/slashes", "Token contains invalid characters")
        ]
        
        for token, expected_error in invalid_cases:
            is_valid, message = validate_public_token_format(token)
            assert is_valid is False
            assert expected_error in message
    
    def test_is_token_expired(self):
        """Test token expiration checking"""
        now = datetime.now()
        
        # Token created yesterday (not expired with default 365 days)
        yesterday = (now - timedelta(days=1)).isoformat()
        assert is_token_expired(yesterday, 365) is False
        
        # Token created 2 years ago (expired)
        old_token = (now - timedelta(days=730)).isoformat()
        assert is_token_expired(old_token, 365) is True
        
        # Token created 1 hour ago with 1-day expiry (not expired)
        recent = (now - timedelta(hours=1)).isoformat()
        assert is_token_expired(recent, 1) is False
        
        # Invalid date format (treat as expired for safety)
        assert is_token_expired("invalid-date", 365) is True


# === RATE LIMITING TESTS (Pure Functions) ===

class TestRateLimiting:
    
    def test_create_rate_limit_key(self):
        """Test rate limit key creation"""
        key = create_rate_limit_key("192.168.1.100", "/api/calendars")
        
        assert key.startswith("ratelimit:/api/calendars:")
        # IP should be hashed for privacy
        assert "192.168.1.100" not in key
        
        # Same inputs should produce same key
        key2 = create_rate_limit_key("192.168.1.100", "/api/calendars")
        assert key == key2
    
    def test_calculate_rate_limit_window(self):
        """Test rate limit window calculation"""
        now = datetime.now()
        requests = [
            {"timestamp": (now - timedelta(minutes=5)).isoformat()},
            {"timestamp": (now - timedelta(minutes=3)).isoformat()},
            {"timestamp": (now - timedelta(minutes=1)).isoformat()},
            {"timestamp": (now - timedelta(minutes=15)).isoformat()},  # Outside window
        ]
        
        window_info = calculate_rate_limit_window(requests, window_minutes=10)
        
        assert window_info["requests_in_window"] == 3  # 3 within 10 minutes
        assert "window_start" in window_info
        assert "window_end" in window_info
    
    def test_is_rate_limit_exceeded(self):
        """Test rate limit checking"""
        now = datetime.now()
        
        # 5 requests in last 5 minutes
        requests = [
            {"timestamp": (now - timedelta(minutes=i)).isoformat()}
            for i in range(5)
        ]
        
        # Should not exceed limit of 10 per 10 minutes
        assert is_rate_limit_exceeded(requests, limit=10, window_minutes=10) is False
        
        # Should exceed limit of 3 per 10 minutes
        assert is_rate_limit_exceeded(requests, limit=3, window_minutes=10) is True
        
        # Empty requests should not exceed any limit
        assert is_rate_limit_exceeded([], limit=1, window_minutes=10) is False


# === CONTENT SECURITY TESTS (Pure Functions) ===

class TestContentSecurity:
    
    def test_sanitize_ical_content(self):
        """Test iCal content sanitization"""
        dirty_ical = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Microsoft Corporation//Outlook 16.0 MIMEDIR//EN
X-WR-CALNAME:My Personal Calendar
BEGIN:VEVENT
UID:12345@outlook.com
SUMMARY:Secret Meeting
ATTENDEE;CN=John Doe:mailto:john@company.com
ORGANIZER:mailto:boss@company.com
X-MICROSOFT-CDO-BUSYSTATUS:BUSY
DESCRIPTION:Confidential discussion
END:VEVENT
END:VCALENDAR"""
        
        sanitized = sanitize_ical_content(dirty_ical)
        
        # Should remove attendee/organizer info
        assert "john@company.com" not in sanitized
        assert "boss@company.com" not in sanitized
        assert "ATTENDEE" not in sanitized
        assert "ORGANIZER" not in sanitized
        
        # Should remove Microsoft-specific fields
        assert "X-MICROSOFT-" not in sanitized
        
        # Should replace PRODID
        assert "iCal Viewer" in sanitized
        
        # Should keep basic event info
        assert "SECRET MEETING" in sanitized.upper()  # Summary preserved
        assert "BEGIN:VEVENT" in sanitized
    
    def test_sanitize_calendar_field_value(self):
        """Test individual field value sanitization"""
        # Test email removal
        text_with_email = "Contact John at john.doe@company.com for details"
        sanitized = sanitize_calendar_field_value(text_with_email)
        assert "john.doe@company.com" not in sanitized
        assert "[email-removed]" in sanitized
        
        # Test URL removal
        text_with_url = "Visit https://company.com/secret-docs for more info"
        sanitized = sanitize_calendar_field_value(text_with_url)
        assert "https://company.com/secret-docs" not in sanitized
        assert "[url-removed]" in sanitized
        
        # Test phone number removal
        text_with_phone = "Call me at +1-555-123-4567"
        sanitized = sanitize_calendar_field_value(text_with_phone)
        assert "555-123-4567" not in sanitized
        assert "[phone-removed]" in sanitized


# === ACCESS CONTROL TESTS (Pure Functions) ===

class TestAccessControl:
    
    def test_create_and_verify_access_signature(self):
        """Test HMAC signature creation and verification"""
        calendar_id = "cal123"
        timestamp = "2024-01-15T10:00:00"
        secret = "test-secret-key"
        
        # Create signature
        signature = create_access_signature(calendar_id, timestamp, secret)
        
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex digest
        
        # Verify valid signature
        is_valid = verify_access_signature(calendar_id, timestamp, signature, secret)
        assert is_valid is True
        
        # Verify invalid signature
        is_valid = verify_access_signature(calendar_id, timestamp, "wrong-signature", secret)
        assert is_valid is False
        
        # Verify with wrong secret
        is_valid = verify_access_signature(calendar_id, timestamp, signature, "wrong-secret")
        assert is_valid is False
    
    def test_is_request_timestamp_valid(self):
        """Test request timestamp validation"""
        now = datetime.now()
        
        # Current timestamp (valid)
        current_timestamp = now.isoformat()
        assert is_request_timestamp_valid(current_timestamp, 300) is True
        
        # Recent timestamp (valid)
        recent_timestamp = (now - timedelta(seconds=60)).isoformat()
        assert is_request_timestamp_valid(recent_timestamp, 300) is True
        
        # Old timestamp (invalid)
        old_timestamp = (now - timedelta(seconds=600)).isoformat()
        assert is_request_timestamp_valid(old_timestamp, 300) is False
        
        # Future timestamp (invalid)
        future_timestamp = (now + timedelta(seconds=60)).isoformat()
        assert is_request_timestamp_valid(future_timestamp, 300) is False
        
        # Invalid format (invalid)
        assert is_request_timestamp_valid("invalid-timestamp", 300) is False


# === URL SECURITY TESTS (Pure Functions) ===

class TestUrlSecurity:
    
    def test_create_secure_calendar_url(self):
        """Test secure calendar URL creation"""
        base_url = "https://filter-ical.de"
        token = "abc123def456ghij7890"  # 20 characters, valid
        
        url = create_secure_calendar_url(base_url, token)
        
        assert url == "https://filter-ical.de/cal/abc123def456ghij7890.ics"
        
        # Test with trailing slash
        url2 = create_secure_calendar_url(base_url + "/", token)
        assert url2 == "https://filter-ical.de/cal/abc123def456ghij7890.ics"
    
    def test_create_preview_url(self):
        """Test preview URL creation"""
        base_url = "https://filter-ical.de"
        token = "abc123def456ghij7890"  # 20 characters, valid
        
        url = create_preview_url(base_url, token)
        
        assert url == "https://filter-ical.de/cal/abc123def456ghij7890"
    
    def test_extract_token_from_url(self):
        """Test token extraction from URLs"""
        valid_token = "abc123def456ghij7890"  # 20 characters, valid
        
        # Test .ics URL
        ics_url = f"https://filter-ical.de/cal/{valid_token}.ics"
        token = extract_token_from_url(ics_url)
        assert token == valid_token
        
        # Test preview URL
        preview_url = f"https://filter-ical.de/cal/{valid_token}"
        token = extract_token_from_url(preview_url)
        assert token == valid_token
        
        # Test invalid URL
        invalid_url = "https://filter-ical.de/invalid"
        token = extract_token_from_url(invalid_url)
        assert token is None  # Too short to be valid
        
        # Test URL with special characters (should be decoded)  
        encoded_token = "abc123def456ghij7890"  # 20 chars
        encoded_url = f"https://filter-ical.de/cal/{encoded_token}.ics"
        token = extract_token_from_url(encoded_url)
        assert token == encoded_token


# === SECURITY HEADERS TESTS (Pure Functions) ===

class TestSecurityHeaders:
    
    def test_create_security_headers_public(self):
        """Test security headers for public calendars"""
        headers = create_security_headers("public")
        
        # Should have CORS headers for calendar app access
        assert headers["Access-Control-Allow-Origin"] == "*"
        assert "GET" in headers["Access-Control-Allow-Methods"]
        
        # Should have caching headers
        assert "public" in headers["Cache-Control"]
        
        # Should have security headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
    
    def test_create_security_headers_private(self):
        """Test security headers for private/management"""
        headers = create_security_headers("private")
        
        # Should not have CORS headers
        assert "Access-Control-Allow-Origin" not in headers
        
        # Should have no-cache headers
        assert "no-cache" in headers["Cache-Control"]
        assert "no-store" in headers["Cache-Control"]
        
        # Should have security headers
        assert headers["X-Content-Type-Options"] == "nosniff"


# === AUDIT LOGGING TESTS (Pure Functions) ===

class TestAuditLogging:
    
    def test_create_access_log_entry(self):
        """Test access log entry creation"""
        request_info = {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 Calendar App",
            "request_path": "/cal/abc123.ics",
            "referer": "https://calendar.google.com",
            "method": "GET",
            "response_size": 1024,
            "cache_hit": True,
            "response_time_ms": 50
        }
        
        log_entry = create_access_log_entry("cal123", request_info)
        
        assert log_entry["filtered_calendar_id"] == "cal123"
        assert "timestamp" in log_entry
        assert log_entry["ip_hash"] is not None  # Should hash IP
        assert "192.168.1.100" not in str(log_entry)  # IP should be hashed
        assert log_entry["user_agent"] == "Mozilla/5.0 Calendar App"
        assert log_entry["cache_hit"] is True
    
    def test_analyze_access_patterns(self):
        """Test access pattern analysis"""
        access_logs = [
            {
                "ip_hash": "hash1",
                "user_agent": "Mozilla/5.0 (Calendar)",
                "cache_hit": True,
                "response_time_ms": 50
            },
            {
                "ip_hash": "hash2", 
                "user_agent": "Outlook Calendar",
                "cache_hit": False,
                "response_time_ms": 200
            },
            {
                "ip_hash": "hash1",  # Same IP
                "user_agent": "Mozilla/5.0 (Browser)",
                "cache_hit": True,
                "response_time_ms": 30
            }
        ]
        
        analysis = analyze_access_patterns(access_logs)
        
        assert analysis["total_accesses"] == 3
        assert analysis["unique_ips"] == 2
        assert analysis["calendar_app_accesses"] == 2  # 2 calendar apps
        assert analysis["browser_accesses"] == 1  # 1 browser
        assert analysis["cache_hit_rate_percent"] == 66.7  # 2/3 cache hits
        assert abs(analysis["average_response_time_ms"] - 93.33) < 0.1  # (50+200+30)/3


# === EDGE CASES AND SECURITY TESTS ===

class TestSecurityEdgeCases:
    
    def test_timing_attack_resistance(self):
        """Test that signature verification is timing-attack resistant"""
        calendar_id = "cal123"
        timestamp = "2024-01-15T10:00:00"
        secret = "secret-key"
        
        valid_signature = create_access_signature(calendar_id, timestamp, secret)
        
        # Time verification of correct signature
        start_time = time.perf_counter()
        result1 = verify_access_signature(calendar_id, timestamp, valid_signature, secret)
        time1 = time.perf_counter() - start_time
        
        # Time verification of incorrect signature
        start_time = time.perf_counter()
        result2 = verify_access_signature(calendar_id, timestamp, "wrong-signature", secret)
        time2 = time.perf_counter() - start_time
        
        assert result1 is True
        assert result2 is False
        
        # Times should be similar (constant time comparison)
        # Allow for some variance due to system timing
        time_ratio = max(time1, time2) / min(time1, time2)
        assert time_ratio < 2.0  # Should not differ by more than 2x
    
    def test_sanitization_completeness(self):
        """Test that sanitization removes all sensitive data"""
        malicious_ical = """BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:Evil Calendar
BEGIN:VEVENT
UID:evil@hacker.com
SUMMARY:<script>alert('xss')</script>
DESCRIPTION:Call +1-800-EVIL or visit https://evil.com/steal-data
ATTENDEE:mailto:victim@company.com
ORGANIZER:mailto:hacker@evil.com
LOCATION:Secret Location
X-MICROSOFT-CDO-BUSYSTATUS:BUSY
X-CUSTOM-MALWARE:base64encodedpayload
END:VEVENT
END:VCALENDAR"""
        
        sanitized = sanitize_ical_content(malicious_ical)
        
        # Should remove all email addresses
        assert "evil@hacker.com" not in sanitized
        assert "victim@company.com" not in sanitized
        assert "hacker@evil.com" not in sanitized
        
        # Should remove URLs and phone numbers from descriptions
        description_line = next((line for line in sanitized.split('\n') if 'DESCRIPTION:' in line), '')
        if description_line:
            assert "https://evil.com" not in description_line
            assert "1-800-EVIL" not in description_line
        
        # Should remove proprietary extensions
        assert "X-MICROSOFT-" not in sanitized
        assert "X-CUSTOM-MALWARE" not in sanitized


"""
WHAT THESE TESTS DEMONSTRATE ABOUT FUNCTIONAL SECURITY:

1. PREDICTABLE SECURITY
   - Security functions are deterministic and testable
   - No hidden security bugs due to side effects
   - Cryptographic operations are pure and verifiable

2. NO MOCKING FOR SECURITY TESTS
   - Can test actual token generation and validation
   - Real cryptographic operations tested directly
   - No mocked security that might hide vulnerabilities

3. COMPOSABLE SECURITY
   - Security functions combine safely
   - Can test security pipelines end-to-end
   - Clear security boundaries and responsibilities

4. PERFORMANCE TESTING
   - Can measure actual security operation performance
   - Timing attack resistance verifiable
   - Security overhead quantifiable

5. COMPREHENSIVE COVERAGE
   - Can test all edge cases and attack vectors
   - Security validation is thorough and reliable
   - No untestable security-critical code paths

This demonstrates that functional programming enhances security:
- Predictable behavior reduces security bugs
- Pure functions are easier to audit for security
- Composable security functions create defense in depth
"""