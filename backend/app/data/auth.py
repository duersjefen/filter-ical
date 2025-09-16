"""
Community Authentication - Pure functions for community login/session management
No I/O operations, only data transformations
"""

import hashlib
import secrets
import uuid
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta


def hash_password(password: str) -> str:
    """Create a secure hash of a password"""
    salt = secrets.token_hex(32)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == password_hash
    except ValueError:
        # Invalid hash format
        return False


def validate_community_credentials(password: str, community_password_hash: str) -> Tuple[bool, str]:
    """Validate community login credentials - pure function"""
    if not password:
        return False, "Password is required"
    
    if not community_password_hash:
        return False, "Community not configured"
    
    if not verify_password(password, community_password_hash):
        return False, "Invalid password"
    
    return True, "Valid credentials"


def create_community_session_data(user_id: str, community_id: str) -> Dict[str, Any]:
    """Create session data for community user - pure function"""
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=24)  # 24 hour session
    
    session_data = {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "community_id": community_id,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "last_accessed": now.isoformat(),
        "is_active": True
    }
    
    return session_data


def validate_community_session(session_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate if community session is still valid - pure function"""
    if not session_data:
        return False, "No session data"
    
    if not session_data.get("is_active", False):
        return False, "Session is inactive"
    
    try:
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        now = datetime.utcnow()
        
        if now > expires_at:
            return False, "Session expired"
        
        return True, "Valid session"
    
    except (ValueError, KeyError):
        return False, "Invalid session format"


def generate_user_id() -> str:
    """Generate a unique user ID for community sessions"""
    return f"community_user_{str(uuid.uuid4())[:8]}"


def create_community_login_response(session_id: str, user_id: str, community_name: str) -> Dict[str, Any]:
    """Create standardized login response - pure function"""
    return {
        "success": True,
        "session_id": session_id,
        "user_id": user_id,
        "community_name": community_name,
        "message": "Login successful"
    }