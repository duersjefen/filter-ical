"""
Security Functions - Rich Hickey Style  
Pure functions for token generation, validation, and security
No side effects, explicit data flow, composable functions
"""

import secrets
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
from urllib.parse import quote, unquote


# === TOKEN GENERATION (Pure Functions) ===

def generate_public_token() -> str:
    """
    Pure function: Generate cryptographically secure public token
    Returns: URL-safe token with high entropy (128 bits)
    """
    # Generate 16 random bytes (128 bits of entropy)
    random_bytes = secrets.token_bytes(16)
    # Convert to URL-safe base64 (no padding needed for 16 bytes)
    token = secrets.urlsafe_base64_encode(random_bytes).decode('ascii')
    # Remove padding if present (shouldn't be for 16 bytes, but safety first)
    return token.rstrip('=')


def generate_cache_key(filtered_calendar_id: str, filter_config_hash: str, 
                      source_content_hash: str) -> str:
    """
    Pure function: Generate deterministic cache key
    Returns: Unique cache key for filtered calendar result
    """
    # Combine all relevant data
    key_data = f"{filtered_calendar_id}:{filter_config_hash}:{source_content_hash}"
    # Create SHA256 hash for consistent length
    hash_obj = hashlib.sha256(key_data.encode('utf-8'))
    return f"filtered_cal_{hash_obj.hexdigest()[:16]}"


def generate_short_url_code(public_token: str) -> str:
    """
    Pure function: Generate short URL code from public token
    Returns: Short (8-character) URL-safe code
    """
    # Create hash of the token
    hash_obj = hashlib.sha256(public_token.encode('utf-8'))
    # Take first 8 characters for short code
    return hash_obj.hexdigest()[:8]


# === TOKEN VALIDATION (Pure Functions) ===

def validate_public_token_format(token: str) -> Tuple[bool, str]:
    """
    Pure function: Validate token format and security requirements
    Returns: (is_valid, error_message)
    """
    if not token:
        return False, "Token is required"
    
    if len(token) < 16:
        return False, "Token too short (minimum 16 characters)"
    
    if len(token) > 64:
        return False, "Token too long (maximum 64 characters)"
    
    # Check for URL-safe characters only
    allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
    if not all(c in allowed_chars for c in token):
        return False, "Token contains invalid characters"
    
    return True, "Valid token format"


def is_token_expired(created_at: str, expires_after_days: int = 365) -> bool:
    """
    Pure function: Check if token has expired
    Returns: True if token is expired
    """
    try:
        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        expiry_date = created_date + timedelta(days=expires_after_days)
        return datetime.now() > expiry_date.replace(tzinfo=None)
    except (ValueError, AttributeError):
        # Invalid date format, treat as expired for safety
        return True


# === RATE LIMITING (Pure Functions) ===

def create_rate_limit_key(ip_address: str, endpoint: str) -> str:
    """
    Pure function: Create rate limiting key
    Returns: Key for rate limit tracking
    """
    # Hash IP address for privacy
    ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
    return f"ratelimit:{endpoint}:{ip_hash}"


def calculate_rate_limit_window(requests: List[Dict], window_minutes: int) -> Dict[str, any]:
    """
    Pure function: Calculate rate limit status for time window
    Returns: Dict with rate limit information
    """
    now = datetime.now()
    window_start = now - timedelta(minutes=window_minutes)
    
    # Filter requests within window
    recent_requests = [
        req for req in requests 
        if datetime.fromisoformat(req['timestamp']) > window_start
    ]
    
    return {
        "requests_in_window": len(recent_requests),
        "window_start": window_start.isoformat(),
        "window_end": now.isoformat(),
        "oldest_request": recent_requests[0]['timestamp'] if recent_requests else None,
        "newest_request": recent_requests[-1]['timestamp'] if recent_requests else None
    }


def is_rate_limit_exceeded(requests: List[Dict], limit: int, window_minutes: int) -> bool:
    """
    Pure function: Check if rate limit is exceeded
    Returns: True if rate limit exceeded
    """
    window_info = calculate_rate_limit_window(requests, window_minutes)
    return window_info["requests_in_window"] >= limit


# === CONTENT SECURITY (Pure Functions) ===

def sanitize_ical_content(ical_content: str) -> str:
    """
    Pure function: Sanitize iCal content for public consumption
    Returns: Cleaned iCal content with sensitive data removed
    """
    lines = ical_content.split('\n')
    sanitized_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Remove potentially sensitive fields
        if line.startswith(('X-WR-CALNAME:', 'X-ORIGINAL-URL:', 'X-WR-CALDESC:')):
            # Keep these but sanitize values
            field, _, value = line.partition(':')
            sanitized_value = sanitize_calendar_field_value(value)
            sanitized_lines.append(f"{field}:{sanitized_value}")
        elif line.startswith('PRODID:'):
            # Replace with our own PRODID
            sanitized_lines.append('PRODID:-//iCal Viewer//Filtered Calendar//EN')
        elif line.startswith(('X-MS-', 'X-MICROSOFT-', 'X-OUTLOOK-')):
            # Remove Microsoft-specific extensions
            continue
        elif line.startswith('ATTENDEE'):
            # Remove attendee information for privacy
            continue
        elif line.startswith('ORGANIZER'):
            # Remove organizer information for privacy  
            continue
        else:
            sanitized_lines.append(line)
    
    return '\n'.join(sanitized_lines)


def sanitize_calendar_field_value(value: str) -> str:
    """
    Pure function: Sanitize individual field values
    Returns: Sanitized field value
    """
    # Remove email addresses
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    value = re.sub(email_pattern, '[email-removed]', value)
    
    # Remove URLs (except for very basic ones)
    url_pattern = r'https?://[^\s<>"\']*'
    value = re.sub(url_pattern, '[url-removed]', value)
    
    # Remove phone numbers
    phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
    value = re.sub(phone_pattern, '[phone-removed]', value)
    
    return value


# === ACCESS CONTROL (Pure Functions) ===

def create_access_signature(filtered_calendar_id: str, timestamp: str, secret_key: str) -> str:
    """
    Pure function: Create HMAC signature for access verification
    Returns: HMAC signature for request validation
    """
    message = f"{filtered_calendar_id}:{timestamp}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_access_signature(filtered_calendar_id: str, timestamp: str, 
                          signature: str, secret_key: str) -> bool:
    """
    Pure function: Verify HMAC signature for access
    Returns: True if signature is valid
    """
    expected_signature = create_access_signature(filtered_calendar_id, timestamp, secret_key)
    return hmac.compare_digest(signature, expected_signature)


def is_request_timestamp_valid(timestamp: str, max_age_seconds: int = 300) -> bool:
    """
    Pure function: Validate request timestamp to prevent replay attacks
    Returns: True if timestamp is within acceptable range
    """
    try:
        request_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        current_time = datetime.now()
        age = (current_time - request_time.replace(tzinfo=None)).total_seconds()
        return 0 <= age <= max_age_seconds
    except (ValueError, AttributeError):
        return False


# === URL SECURITY (Pure Functions) ===

def create_secure_calendar_url(base_url: str, public_token: str) -> str:
    """
    Pure function: Create secure public calendar URL
    Returns: Full URL for calendar access
    """
    # Ensure token is URL-safe
    safe_token = quote(public_token, safe='-_')
    return f"{base_url.rstrip('/')}/cal/{safe_token}.ics"


def create_preview_url(base_url: str, public_token: str) -> str:
    """
    Pure function: Create preview URL for calendar
    Returns: Preview URL for browser viewing
    """
    safe_token = quote(public_token, safe='-_')
    return f"{base_url.rstrip('/')}/cal/{safe_token}"


def extract_token_from_url(url: str) -> Optional[str]:
    """
    Pure function: Extract token from calendar URL
    Returns: Token if found, None otherwise
    """
    try:
        # Handle both .ics and non-.ics URLs
        if url.endswith('.ics'):
            token = url.split('/')[-1][:-4]  # Remove .ics extension
        else:
            token = url.split('/')[-1]
        
        # URL decode the token
        decoded_token = unquote(token)
        
        # Validate extracted token
        is_valid, _ = validate_public_token_format(decoded_token)
        return decoded_token if is_valid else None
    except (IndexError, AttributeError):
        return None


# === SECURITY HEADERS (Pure Functions) ===

def create_security_headers(calendar_type: str = 'public') -> Dict[str, str]:
    """
    Pure function: Create appropriate security headers
    Returns: Dictionary of security headers
    """
    base_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    if calendar_type == 'public':
        # Public calendar headers (accessible to calendar apps)
        base_headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, HEAD',
            'Access-Control-Max-Age': '3600',
            'Cache-Control': 'public, max-age=300'  # 5 minute cache
        })
    else:
        # Private/management headers
        base_headers.update({
            'Cache-Control': 'private, no-cache, no-store',
            'Pragma': 'no-cache'
        })
    
    return base_headers


# === AUDIT LOGGING (Pure Functions) ===

def create_access_log_entry(filtered_calendar_id: str, request_info: Dict[str, str]) -> Dict[str, any]:
    """
    Pure function: Create access log entry
    Returns: Structured log entry for audit trail
    """
    # Hash IP address for privacy
    ip_hash = hashlib.sha256(
        request_info.get('ip_address', '').encode()
    ).hexdigest()[:16] if request_info.get('ip_address') else None
    
    return {
        'filtered_calendar_id': filtered_calendar_id,
        'timestamp': datetime.now().isoformat(),
        'ip_hash': ip_hash,
        'user_agent': request_info.get('user_agent'),
        'request_path': request_info.get('request_path'),
        'referer': request_info.get('referer'),
        'method': request_info.get('method', 'GET'),
        'response_size': request_info.get('response_size', 0),
        'cache_hit': request_info.get('cache_hit', False),
        'response_time_ms': request_info.get('response_time_ms', 0)
    }


def analyze_access_patterns(access_logs: List[Dict]) -> Dict[str, any]:
    """
    Pure function: Analyze access patterns for security insights
    Returns: Analysis of access patterns
    """
    if not access_logs:
        return {'total_accesses': 0, 'unique_ips': 0, 'analysis': 'No data available'}
    
    # Count unique IPs
    unique_ips = set(log.get('ip_hash') for log in access_logs if log.get('ip_hash'))
    
    # Analyze user agents
    user_agents = [log.get('user_agent', '') for log in access_logs]
    calendar_app_agents = sum(1 for ua in user_agents if any(
        app in ua.lower() for app in ['calendar', 'outlook', 'ical', 'caldav']
    ))
    
    # Analyze access frequency
    total_accesses = len(access_logs)
    
    # Calculate cache hit rate
    cache_hits = sum(1 for log in access_logs if log.get('cache_hit', False))
    cache_hit_rate = (cache_hits / total_accesses * 100) if total_accesses > 0 else 0
    
    return {
        'total_accesses': total_accesses,
        'unique_ips': len(unique_ips),
        'calendar_app_accesses': calendar_app_agents,
        'browser_accesses': total_accesses - calendar_app_agents,
        'cache_hit_rate_percent': round(cache_hit_rate, 1),
        'average_response_time_ms': sum(
            log.get('response_time_ms', 0) for log in access_logs
        ) / total_accesses if total_accesses > 0 else 0
    }


# === SECURITY CONSTANTS ===

SECURITY_LIMITS = {
    'max_token_age_days': 365,
    'max_request_age_seconds': 300,
    'rate_limit_per_minute': 100,
    'rate_limit_per_hour': 1000,
    'max_calendar_size_mb': 10,
    'max_events_per_calendar': 10000,
    'token_min_length': 16,
    'token_max_length': 64
}

ALLOWED_USER_AGENTS = [
    'calendar', 'ical', 'caldav', 'outlook', 'thunderbird', 
    'apple', 'google', 'mozilla', 'microsoft'
]

BLOCKED_USER_AGENTS = [
    'bot', 'crawler', 'spider', 'scraper', 'wget', 'curl'
]