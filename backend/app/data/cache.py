"""
Pure functions for cache key generation and data transformation.

FUNCTIONAL CORE - No side effects, fully testable.
All cache business logic without I/O operations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


def generate_domain_events_cache_key(domain_key: str) -> str:
    """
    Generate cache key for domain events.
    
    Args:
        domain_key: Domain identifier
        
    Returns:
        Cache key string
        
    Pure function - deterministic key generation.
    """
    return f"domain_events:{domain_key}"


def generate_domain_groups_cache_key(domain_key: str) -> str:
    """
    Generate cache key for domain groups.
    
    Args:
        domain_key: Domain identifier
        
    Returns:
        Cache key string
        
    Pure function - deterministic key generation.
    """
    return f"domain_groups:{domain_key}"


def generate_cache_metadata_key(domain_key: str) -> str:
    """
    Generate cache key for domain cache metadata.
    
    Args:
        domain_key: Domain identifier
        
    Returns:
        Cache key string
        
    Pure function - deterministic key generation.
    """
    return f"domain_cache_meta:{domain_key}"


def prepare_domain_events_for_cache(domain_events_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare domain events response for caching.
    
    Args:
        domain_events_response: Domain events response from domain service
        
    Returns:
        Cache-ready data structure
        
    Pure function - data transformation.
    """
    # Add cache metadata
    cache_data = {
        **domain_events_response,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "cache_version": "1.0"
    }
    
    return cache_data


def create_cache_metadata(domain_key: str, last_updated: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Create cache metadata structure.
    
    Args:
        domain_key: Domain identifier
        last_updated: When the data was last updated
        
    Returns:
        Cache metadata dictionary
        
    Pure function - creates metadata structure.
    """
    now = datetime.now(timezone.utc)
    
    return {
        "domain_key": domain_key,
        "last_updated": (last_updated or now).isoformat(),
        "cache_created": now.isoformat(),
        "version": "1.0"
    }


def is_cache_stale(cache_metadata: Dict[str, Any], max_age_seconds: int = 300) -> bool:
    """
    Check if cache data is stale based on metadata.
    
    Args:
        cache_metadata: Cache metadata dictionary
        max_age_seconds: Maximum age in seconds (default 5 minutes)
        
    Returns:
        True if cache is stale, False otherwise
        
    Pure function - staleness calculation.
    """
    try:
        cache_created = datetime.fromisoformat(cache_metadata["cache_created"].replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        age_seconds = (now - cache_created).total_seconds()
        return age_seconds > max_age_seconds
    except (KeyError, ValueError, TypeError):
        # If we can't parse metadata, consider cache stale
        return True


def extract_cache_statistics(cached_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract statistics from cached domain events data.
    
    Args:
        cached_data: Cached domain events response
        
    Returns:
        Statistics dictionary
        
    Pure function - data analysis.
    """
    stats = {
        "total_groups": len(cached_data.get("groups", [])),
        "total_ungrouped_events": len(cached_data.get("ungrouped_events", [])),
        "cached_at": cached_data.get("cached_at"),
        "cache_version": cached_data.get("cache_version", "unknown")
    }
    
    # Count total events across all groups and ungrouped
    total_events = 0
    
    for group in cached_data.get("groups", []):
        for recurring_event in group.get("recurring_events", []):
            total_events += recurring_event.get("event_count", 0)
    
    for recurring_event in cached_data.get("ungrouped_events", []):
        total_events += recurring_event.get("event_count", 0)
    
    stats["total_events"] = total_events
    
    return stats


def validate_cached_domain_events(cached_data: Dict[str, Any]) -> bool:
    """
    Validate cached domain events data structure.
    
    Args:
        cached_data: Cached domain events data
        
    Returns:
        True if valid structure, False otherwise
        
    Pure function - data validation.
    """
    try:
        # Check required keys
        if "groups" not in cached_data or "ungrouped_events" not in cached_data:
            return False
        
        # Check data types
        if not isinstance(cached_data["groups"], list):
            return False
        
        if not isinstance(cached_data["ungrouped_events"], list):
            return False
        
        # Check cache metadata
        if "cached_at" not in cached_data or "cache_version" not in cached_data:
            return False
        
        return True
    except Exception:
        return False


def get_cache_keys_for_domain(domain_key: str) -> List[str]:
    """
    Get all cache keys associated with a domain.
    
    Args:
        domain_key: Domain identifier
        
    Returns:
        List of cache keys for the domain
        
    Pure function - key enumeration.
    """
    return [
        generate_domain_events_cache_key(domain_key),
        generate_domain_groups_cache_key(domain_key),
        generate_cache_metadata_key(domain_key)
    ]