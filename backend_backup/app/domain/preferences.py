"""
Preferences Domain Functions - Pure Business Logic
Rich Hickey: "Functional Core - Pure functions only"
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


def get_user_preferences(user_id: str, calendar_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Pure function to get default user preferences
    
    Args:
        user_id: User identifier
        calendar_id: Optional calendar identifier
        
    Returns:
        Default preferences dictionary
    """
    timestamp = datetime.now().isoformat()
    
    preferences = {
        "user_id": user_id,
        "calendar_id": calendar_id,
        "view_mode": "month",
        "time_zone": "UTC",
        "first_day_of_week": 1,  # Monday
        "show_weekends": True,
        "default_view": "month",
        "event_display_format": "standard",
        "notifications_enabled": True,
        "theme": "light",
        "language": "en",
        "date_format": "YYYY-MM-DD",
        "time_format": "24h",
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    return preferences


def update_user_preferences(current_preferences: Dict[str, Any], 
                          updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure function to update user preferences
    
    Args:
        current_preferences: Current preferences
        updates: Updates to apply
        
    Returns:
        Updated preferences
    """
    # Validate updates
    validated_updates = validate_preference_updates(updates)
    
    # Create new preferences object
    new_preferences = current_preferences.copy()
    new_preferences.update(validated_updates)
    new_preferences["updated_at"] = datetime.now().isoformat()
    
    return new_preferences


def validate_preference_updates(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure function to validate preference updates
    
    Args:
        updates: Raw preference updates
        
    Returns:
        Validated preference updates
    """
    validated = {}
    
    # View mode validation
    if 'view_mode' in updates:
        view_mode = updates['view_mode']
        if view_mode in ['month', 'week', 'day', 'agenda']:
            validated['view_mode'] = view_mode
    
    # Time zone validation
    if 'time_zone' in updates:
        time_zone = updates['time_zone']
        if isinstance(time_zone, str) and len(time_zone) > 0:
            validated['time_zone'] = time_zone
    
    # First day of week validation (0=Sunday, 1=Monday, etc.)
    if 'first_day_of_week' in updates:
        first_day = updates['first_day_of_week']
        if isinstance(first_day, int) and 0 <= first_day <= 6:
            validated['first_day_of_week'] = first_day
    
    # Boolean preferences
    boolean_prefs = ['show_weekends', 'notifications_enabled']
    for pref in boolean_prefs:
        if pref in updates:
            value = updates[pref]
            if isinstance(value, bool):
                validated[pref] = value
    
    # Default view validation
    if 'default_view' in updates:
        default_view = updates['default_view']
        if default_view in ['month', 'week', 'day', 'agenda', 'list']:
            validated['default_view'] = default_view
    
    # Event display format validation
    if 'event_display_format' in updates:
        display_format = updates['event_display_format']
        if display_format in ['standard', 'compact', 'detailed']:
            validated['event_display_format'] = display_format
    
    # Theme validation
    if 'theme' in updates:
        theme = updates['theme']
        if theme in ['light', 'dark', 'auto']:
            validated['theme'] = theme
    
    # Language validation
    if 'language' in updates:
        language = updates['language']
        if isinstance(language, str) and len(language) >= 2:
            validated['language'] = language
    
    # Date format validation
    if 'date_format' in updates:
        date_format = updates['date_format']
        valid_formats = ['YYYY-MM-DD', 'DD/MM/YYYY', 'MM/DD/YYYY', 'DD.MM.YYYY']
        if date_format in valid_formats:
            validated['date_format'] = date_format
    
    # Time format validation
    if 'time_format' in updates:
        time_format = updates['time_format']
        if time_format in ['12h', '24h']:
            validated['time_format'] = time_format
    
    # Calendar-specific preferences
    if 'calendar_color' in updates:
        color = updates['calendar_color']
        if isinstance(color, str) and color.startswith('#') and len(color) == 7:
            validated['calendar_color'] = color
    
    if 'calendar_visible' in updates:
        visible = updates['calendar_visible']
        if isinstance(visible, bool):
            validated['calendar_visible'] = visible
    
    return validated


def merge_preferences(user_prefs: Dict[str, Any], 
                     calendar_prefs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure function to merge user and calendar-specific preferences
    
    Args:
        user_prefs: User-level preferences
        calendar_prefs: Calendar-specific preferences
        
    Returns:
        Merged preferences with calendar overrides
    """
    merged = user_prefs.copy()
    
    # Calendar-specific overrides
    calendar_overrides = [
        'view_mode', 'default_view', 'event_display_format',
        'calendar_color', 'calendar_visible', 'notifications_enabled'
    ]
    
    for key in calendar_overrides:
        if key in calendar_prefs:
            merged[key] = calendar_prefs[key]
    
    return merged


def get_notification_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure function to extract notification-specific preferences
    
    Args:
        preferences: Full preferences dictionary
        
    Returns:
        Notification preferences
    """
    return {
        "enabled": preferences.get("notifications_enabled", True),
        "email_notifications": preferences.get("email_notifications", False),
        "push_notifications": preferences.get("push_notifications", True),
        "reminder_minutes": preferences.get("reminder_minutes", [15, 60]),
        "notification_types": preferences.get("notification_types", ["event_start", "event_reminder"])
    }


def get_display_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure function to extract display-specific preferences
    
    Args:
        preferences: Full preferences dictionary
        
    Returns:
        Display preferences
    """
    return {
        "view_mode": preferences.get("view_mode", "month"),
        "default_view": preferences.get("default_view", "month"),
        "theme": preferences.get("theme", "light"),
        "event_display_format": preferences.get("event_display_format", "standard"),
        "show_weekends": preferences.get("show_weekends", True),
        "first_day_of_week": preferences.get("first_day_of_week", 1),
        "time_zone": preferences.get("time_zone", "UTC"),
        "date_format": preferences.get("date_format", "YYYY-MM-DD"),
        "time_format": preferences.get("time_format", "24h"),
        "language": preferences.get("language", "en")
    }


def validate_timezone(timezone_str: str) -> bool:
    """
    Pure function to validate timezone string
    
    Args:
        timezone_str: Timezone string to validate
        
    Returns:
        True if valid timezone
    """
    # Simplified validation - real implementation would use pytz or similar
    common_timezones = [
        "UTC", "America/New_York", "America/Los_Angeles", "Europe/London",
        "Europe/Paris", "Europe/Berlin", "Asia/Tokyo", "Asia/Shanghai",
        "Australia/Sydney", "America/Chicago", "America/Denver"
    ]
    
    return timezone_str in common_timezones or timezone_str.startswith(("America/", "Europe/", "Asia/", "Australia/", "Africa/"))


def get_calendar_color_options() -> List[str]:
    """
    Pure function to get available calendar color options
    
    Returns:
        List of available color hex codes
    """
    return [
        "#3B82F6",  # Blue
        "#EF4444",  # Red
        "#10B981",  # Green
        "#F59E0B",  # Yellow
        "#8B5CF6",  # Purple
        "#EC4899",  # Pink
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
        "#F97316",  # Orange
        "#6B7280",  # Gray
    ]