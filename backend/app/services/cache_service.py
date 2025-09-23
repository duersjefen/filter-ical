"""
Cache service for domain events and data management.

IMPERATIVE SHELL - Orchestrates pure functions with Redis I/O operations.
"""

from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from ..core.redis import set_cache, get_cache, delete_cache, cache_exists
from ..core.config import settings
from ..data.cache import (
    generate_domain_events_cache_key, generate_cache_metadata_key,
    prepare_domain_events_for_cache, create_cache_metadata,
    is_cache_stale, validate_cached_domain_events, get_cache_keys_for_domain
)
from .domain_service import build_domain_events_response_data


def cache_domain_events(db: Session, domain_key: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Build and cache domain events data.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        Tuple of (success, cached_data, error_message)
        
    I/O Operation - Database read + Redis write.
    """
    try:
        # Build domain events response from database
        domain_events_response = build_domain_events_response_data(db, domain_key)
        
        # Prepare data for caching using pure function
        cache_data = prepare_domain_events_for_cache(domain_events_response)
        
        # Try to cache the domain events data (graceful degradation if Redis unavailable)
        events_cache_key = generate_domain_events_cache_key(domain_key)
        cache_success = set_cache(events_cache_key, cache_data, settings.cache_ttl_seconds)
        
        # Try to cache metadata (graceful degradation if Redis unavailable)
        metadata_cache_key = generate_cache_metadata_key(domain_key)
        metadata = create_cache_metadata(domain_key)
        metadata_success = set_cache(metadata_cache_key, metadata, settings.cache_ttl_seconds)
        
        # Always return the data, even if caching failed (graceful degradation)
        return True, cache_data, ""
        
    except Exception as e:
        return False, None, f"Cache domain events error: {str(e)}"


def get_cached_domain_events(domain_key: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Get cached domain events data.
    
    Args:
        domain_key: Domain identifier
        
    Returns:
        Tuple of (success, cached_data, error_message)
        
    I/O Operation - Redis read with validation.
    """
    try:
        # Get cached events data
        events_cache_key = generate_domain_events_cache_key(domain_key)
        cached_data = get_cache(events_cache_key)
        
        if not cached_data:
            return False, None, "No cached data found"
        
        # Validate cached data structure
        if not validate_cached_domain_events(cached_data):
            return False, None, "Invalid cached data structure"
        
        return True, cached_data, ""
        
    except Exception as e:
        return False, None, f"Get cached domain events error: {str(e)}"


def is_domain_cache_valid(domain_key: str) -> bool:
    """
    Check if domain cache is valid and not stale.
    
    Args:
        domain_key: Domain identifier
        
    Returns:
        True if cache is valid and fresh, False otherwise
        
    I/O Operation - Redis read with staleness check.
    """
    try:
        # Check if events cache exists
        events_cache_key = generate_domain_events_cache_key(domain_key)
        if not cache_exists(events_cache_key):
            return False
        
        # Get cache metadata
        metadata_cache_key = generate_cache_metadata_key(domain_key)
        metadata = get_cache(metadata_cache_key)
        
        if not metadata:
            return False
        
        # Check if cache is stale using pure function
        if is_cache_stale(metadata, settings.cache_ttl_seconds):
            return False
        
        return True
        
    except Exception:
        return False


def invalidate_domain_cache(domain_key: str) -> bool:
    """
    Invalidate all cache data for a domain.
    
    Args:
        domain_key: Domain identifier
        
    Returns:
        Success status
        
    I/O Operation - Redis delete operations.
    """
    try:
        # Get all cache keys for domain using pure function
        cache_keys = get_cache_keys_for_domain(domain_key)
        
        # Delete all cache keys
        success_count = 0
        for key in cache_keys:
            if delete_cache(key):
                success_count += 1
        
        # Consider successful if at least one key was deleted
        return success_count > 0
        
    except Exception as e:
        print(f"Invalidate domain cache error: {e}")
        return False


def get_or_build_domain_events(db: Session, domain_key: str, force_refresh: bool = False) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Get cached domain events or build and cache if needed.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        force_refresh: Force rebuild cache even if valid
        
    Returns:
        Tuple of (success, domain_events_data, error_message)
        
    I/O Operation - Cache-first data retrieval with fallback.
    """
    try:
        # Check if we should use cache
        if not force_refresh and is_domain_cache_valid(domain_key):
            # Try to get cached data
            success, cached_data, error = get_cached_domain_events(domain_key)
            if success and cached_data:
                return True, cached_data, ""
        
        # Cache is invalid or force refresh requested - rebuild and cache
        success, fresh_data, error = cache_domain_events(db, domain_key)
        
        if not success:
            return False, None, error
        
        return True, fresh_data, ""
        
    except Exception as e:
        return False, None, f"Get or build domain events error: {str(e)}"


def warm_domain_cache(db: Session, domain_key: str) -> bool:
    """
    Pre-warm cache for a domain (background task).
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        Success status
        
    I/O Operation - Cache warming for performance.
    """
    try:
        success, _, error = cache_domain_events(db, domain_key)
        if not success:
            print(f"Cache warming failed for domain {domain_key}: {error}")
        return success
        
    except Exception as e:
        print(f"Cache warming error for domain {domain_key}: {e}")
        return False