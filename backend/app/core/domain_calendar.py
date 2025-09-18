"""
Domain Calendar Management (Functional Core)
Pure functions for managing domain-specific calendars.
"""
from typing import Optional, Dict, Any
from pathlib import Path
import yaml
import uuid


def get_domain_calendar_id(domain_id: str) -> str:
    """
    Generate consistent calendar ID for a domain.
    Pure function - always returns the same ID for the same domain.
    
    Args:
        domain_id: Domain identifier (e.g., "exter")
        
    Returns:
        Consistent calendar ID for the domain
    """
    return f"cal_domain_{domain_id}"


def load_domain_calendar_config(domain_id: str) -> Optional[Dict[str, str]]:
    """
    Load calendar configuration for a specific domain.
    Pure function - reads domain config and extracts calendar info.
    
    Args:
        domain_id: Domain identifier
        
    Returns:
        Dict with calendar configuration or None if not found
    """
    try:
        config_path = Path(__file__).parent.parent.parent / "config" / "domains.yaml"
        with open(config_path, 'r') as f:
            domains_config = yaml.safe_load(f)
        
        if 'domains' not in domains_config or domain_id not in domains_config['domains']:
            return None
        
        domain_config = domains_config['domains'][domain_id]
        
        return {
            'id': get_domain_calendar_id(domain_id),
            'name': domain_config.get('name', f"{domain_id.title()} Calendar"),
            'url': domain_config.get('calendar_url', ''),
            'domain_id': domain_id,
            'user_id': 'public'
        }
    except Exception:
        return None


def is_domain_calendar(calendar_id: str) -> bool:
    """
    Check if calendar ID belongs to a domain calendar.
    Pure function - checks ID format.
    
    Args:
        calendar_id: Calendar ID to check
        
    Returns:
        True if it's a domain calendar ID
    """
    return calendar_id.startswith("cal_domain_")


def extract_domain_from_calendar_id(calendar_id: str) -> Optional[str]:
    """
    Extract domain ID from domain calendar ID.
    Pure function - parses calendar ID.
    
    Args:
        calendar_id: Domain calendar ID
        
    Returns:
        Domain ID or None if not a domain calendar
    """
    if not is_domain_calendar(calendar_id):
        return None
    
    return calendar_id.replace("cal_domain_", "")


def generate_calendar_id(domain_id: Optional[str] = None) -> str:
    """
    Generate appropriate calendar ID based on context.
    Pure function - generates consistent IDs.
    
    Args:
        domain_id: If provided, creates domain calendar ID, otherwise regular calendar ID
        
    Returns:
        Calendar ID string
    """
    if domain_id:
        return get_domain_calendar_id(domain_id)
    else:
        return f"cal_{uuid.uuid4().hex[:8]}"


def detect_domain_from_url(calendar_url: str) -> Optional[str]:
    """
    Detect if a calendar URL matches a known domain configuration.
    Pure function - compares URL against domain configs.
    
    Args:
        calendar_url: Calendar URL to check
        
    Returns:
        Domain ID if URL matches a known domain, otherwise None
    """
    try:
        config_path = Path(__file__).parent.parent.parent / "config" / "domains.yaml"
        with open(config_path, 'r') as f:
            domains_config = yaml.safe_load(f)
        
        if 'domains' not in domains_config:
            return None
            
        for domain_id, domain_config in domains_config['domains'].items():
            domain_calendar_url = domain_config.get('calendar_url', '')
            if domain_calendar_url and domain_calendar_url == calendar_url:
                return domain_id
                
        return None
    except Exception:
        return None


def get_calendar_domain_id(calendar) -> Optional[str]:
    """
    Get domain ID for a calendar object.
    Pure function - determines domain from calendar properties.
    
    Args:
        calendar: Calendar object with id, domain_id attributes
        
    Returns:
        Domain ID if this is a domain calendar, otherwise None
    """
    # First check if calendar has explicit domain_id field
    if hasattr(calendar, 'domain_id') and calendar.domain_id:
        return calendar.domain_id
    
    # Check if calendar ID indicates it's a domain calendar
    if hasattr(calendar, 'id') and is_domain_calendar(calendar.id):
        return extract_domain_from_calendar_id(calendar.id)
    
    # Not a domain calendar
    return None