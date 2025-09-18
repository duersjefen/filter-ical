"""
Calendar Cache Management (Functional Core)
Pure functions for caching external calendar data.
Following Rich Hickey's functional programming principles.
"""
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import hashlib


CACHE_DURATION_MINUTES = 5  # External calendars cached for 5 minutes


def create_content_hash(ical_content: str) -> str:
    """
    Create hash of iCal content for change detection.
    Pure function - same content always produces same hash.
    
    Args:
        ical_content: Raw iCal content string
        
    Returns:
        SHA-256 hash of the content
    """
    return hashlib.sha256(ical_content.encode('utf-8')).hexdigest()


def is_cache_valid(cache_updated_at: Optional[datetime], cache_expires_at: Optional[datetime]) -> bool:
    """
    Check if cached content is still valid.
    Pure function - compares timestamps.
    
    Args:
        cache_updated_at: When cache was last updated
        cache_expires_at: When cache expires
        
    Returns:
        True if cache is still valid, False otherwise
    """
    if not cache_updated_at or not cache_expires_at:
        return False
    
    now = datetime.utcnow()
    return now < cache_expires_at


def calculate_cache_expiry(updated_at: datetime) -> datetime:
    """
    Calculate when cache should expire.
    Pure function - adds cache duration to update time.
    
    Args:
        updated_at: When cache was updated
        
    Returns:
        Datetime when cache expires
    """
    return updated_at + timedelta(minutes=CACHE_DURATION_MINUTES)


def should_update_cache(calendar) -> bool:
    """
    Determine if calendar cache needs updating.
    Pure function - checks cache validity and calendar properties.
    
    Args:
        calendar: Calendar object with cache fields
        
    Returns:
        True if cache should be updated, False otherwise
    """
    # Always update if no cached content
    if not getattr(calendar, 'cached_ical_content', None):
        return True
    
    # Check if cache has expired
    cache_updated_at = getattr(calendar, 'cache_updated_at', None)
    cache_expires_at = getattr(calendar, 'cache_expires_at', None)
    
    return not is_cache_valid(cache_updated_at, cache_expires_at)


def detect_content_change(new_content: str, cached_hash: Optional[str]) -> bool:
    """
    Detect if iCal content has changed since last cache.
    Pure function - compares content hashes.
    
    Args:
        new_content: Newly fetched iCal content
        cached_hash: Previously stored content hash
        
    Returns:
        True if content has changed, False if unchanged
    """
    if not cached_hash:
        return True  # No previous hash means it's new content
    
    new_hash = create_content_hash(new_content)
    return new_hash != cached_hash


def create_cache_data(ical_content: str, updated_at: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Create cache data dictionary for storing in database.
    Pure function - transforms content into cache structure.
    
    Args:
        ical_content: Raw iCal content to cache
        updated_at: When content was fetched (defaults to now)
        
    Returns:
        Dictionary with cache fields for database update
    """
    if updated_at is None:
        updated_at = datetime.utcnow()
    
    return {
        'cached_ical_content': ical_content,
        'cached_content_hash': create_content_hash(ical_content),
        'cache_updated_at': updated_at,
        'cache_expires_at': calculate_cache_expiry(updated_at)
    }


def get_cached_content(calendar) -> Optional[str]:
    """
    Get cached iCal content if valid.
    Pure function - returns cached content only if cache is valid.
    
    Args:
        calendar: Calendar object with cache fields
        
    Returns:
        Cached iCal content if valid, None otherwise
    """
    if should_update_cache(calendar):
        return None
    
    return getattr(calendar, 'cached_ical_content', None)


def needs_cache_update(calendar, fresh_content: str) -> bool:
    """
    Determine if cache needs updating based on content comparison.
    Pure function - combines cache validity and content change detection.
    
    Args:
        calendar: Calendar object with cache fields
        fresh_content: Newly fetched iCal content
        
    Returns:
        True if cache should be updated with new content
    """
    # Always update if cache is expired
    if should_update_cache(calendar):
        return True
    
    # Update if content has changed
    cached_hash = getattr(calendar, 'cached_content_hash', None)
    return detect_content_change(fresh_content, cached_hash)


def calculate_content_similarity(content1: str, content2: str) -> float:
    """
    Calculate similarity between two iCal contents.
    Pure function - returns similarity score between 0.0 and 1.0.
    
    Args:
        content1: First iCal content
        content2: Second iCal content
        
    Returns:
        Similarity score (1.0 = identical, 0.0 = completely different)
    """
    if not content1 or not content2:
        return 0.0
    
    if content1 == content2:
        return 1.0
    
    # Simple similarity based on length difference
    # In a production system, you might use more sophisticated comparison
    len1, len2 = len(content1), len(content2)
    if len1 == 0 or len2 == 0:
        return 0.0
    
    max_len = max(len1, len2)
    min_len = min(len1, len2)
    
    return min_len / max_len


def is_significant_change(old_content: Optional[str], new_content: str, threshold: float = 0.95) -> bool:
    """
    Determine if content change is significant enough to trigger regeneration.
    Pure function - prevents unnecessary regenerations for minor changes.
    
    Args:
        old_content: Previous iCal content
        new_content: New iCal content
        threshold: Similarity threshold (default 0.95 means 95% similar = no regeneration)
        
    Returns:
        True if change is significant and should trigger regeneration
    """
    if not old_content:
        return True  # Always significant if no previous content
    
    if old_content == new_content:
        return False  # No change at all
    
    # Check if change is significant enough
    similarity = calculate_content_similarity(old_content, new_content)
    return similarity < threshold