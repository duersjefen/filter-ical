"""
Calendar Domain Functions - Pure Business Logic
Rich Hickey: "Functional Core - Pure functions only"
"""

from typing import Tuple, Dict, Any, Optional
from datetime import datetime


def validate_calendar_data(name: str, url: str) -> Tuple[bool, Optional[str]]:
    """
    Pure function to validate calendar data
    
    Args:
        name: Calendar name
        url: Calendar URL
        
    Returns:
        (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "Calendar name is required and must be a string"
    
    if not url or not isinstance(url, str):
        return False, "Calendar URL is required and must be a string"
    
    if len(name.strip()) == 0:
        return False, "Calendar name cannot be empty"
    
    if not url.startswith(('http://', 'https://')):
        return False, "Calendar URL must start with http:// or https://"
    
    if len(name) > 200:
        return False, "Calendar name must be less than 200 characters"
    
    return True, None


def create_calendar(name: str, url: str, user_id: str) -> Dict[str, Any]:
    """
    Pure function to create calendar data structure
    
    Args:
        name: Calendar name
        url: Calendar URL  
        user_id: User identifier
        
    Returns:
        Calendar data dictionary
    """
    timestamp = datetime.now().isoformat()
    calendar_id = f"cal_{user_id}_{int(datetime.now().timestamp())}"
    
    return {
        "id": calendar_id,
        "name": name.strip(),
        "url": url.strip(),
        "user_id": user_id,
        "created_at": timestamp,
        "updated_at": timestamp,
        "is_active": True,
        "description": "",
        "color": "#3B82F6"  # Default blue color
    }


def update_calendar(calendar: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure function to update calendar data
    
    Args:
        calendar: Existing calendar data
        updates: Fields to update
        
    Returns:
        Updated calendar data
    """
    updated_calendar = calendar.copy()
    updated_calendar.update(updates)
    updated_calendar["updated_at"] = datetime.now().isoformat()
    
    return updated_calendar


def is_calendar_owner(calendar: Dict[str, Any], user_id: str) -> bool:
    """
    Pure function to check if user owns calendar
    
    Args:
        calendar: Calendar data
        user_id: User identifier
        
    Returns:
        True if user owns calendar
    """
    return calendar.get("user_id") == user_id