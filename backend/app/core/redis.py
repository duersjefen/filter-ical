"""
Redis connection and management for caching.

IMPERATIVE SHELL - I/O operations for Redis caching.
"""

import json
from typing import Dict, Any, Optional
from .config import settings

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    print("⚠️ Redis not available - caching disabled")
    REDIS_AVAILABLE = False
    redis = None  # Set to None when not available

# Global Redis connection
_redis_client = None


def get_redis_client():
    """
    Get or create Redis client connection.
    
    Returns:
        Redis client instance or None if Redis not available
        
    I/O Operation - Redis connection management.
    """
    global _redis_client
    
    if not REDIS_AVAILABLE or redis is None:
        return None
    
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    return _redis_client


def set_cache(key: str, data: Dict[str, Any], expire_seconds: int = 300) -> bool:
    """
    Set cache data in Redis.
    
    Args:
        key: Cache key
        data: Data to cache (will be JSON serialized)
        expire_seconds: Cache expiration time (default 5 minutes)
        
    Returns:
        Success status
        
    I/O Operation - Redis write.
    """
    if not REDIS_AVAILABLE:
        return False
    
    try:
        client = get_redis_client()
        if client is None:
            return False
        json_data = json.dumps(data, default=str)  # default=str handles datetime serialization
        client.setex(key, expire_seconds, json_data)
        return True
    except Exception as e:
        print(f"Redis cache set error: {e}")
        return False


def get_cache(key: str) -> Optional[Dict[str, Any]]:
    """
    Get cache data from Redis.
    
    Args:
        key: Cache key
        
    Returns:
        Cached data or None if not found/error
        
    I/O Operation - Redis read.
    """
    if not REDIS_AVAILABLE:
        return None
    
    try:
        client = get_redis_client()
        if client is None:
            return None
        json_data = client.get(key)
        
        if json_data:
            return json.loads(json_data)
        return None
    except Exception as e:
        print(f"Redis cache get error: {e}")
        return None


def delete_cache(key: str) -> bool:
    """
    Delete cache key from Redis.
    
    Args:
        key: Cache key to delete
        
    Returns:
        Success status
        
    I/O Operation - Redis delete.
    """
    if not REDIS_AVAILABLE:
        return False
    
    try:
        client = get_redis_client()
        if client is None:
            return False
        client.delete(key)
        return True
    except Exception as e:
        print(f"Redis cache delete error: {e}")
        return False


def cache_exists(key: str) -> bool:
    """
    Check if cache key exists in Redis.
    
    Args:
        key: Cache key to check
        
    Returns:
        True if key exists, False otherwise
        
    I/O Operation - Redis existence check.
    """
    if not REDIS_AVAILABLE:
        return False
    
    try:
        client = get_redis_client()
        if client is None:
            return False
        return client.exists(key) > 0
    except Exception as e:
        print(f"Redis cache exists error: {e}")
        return False


def get_cache_ttl(key: str) -> int:
    """
    Get time-to-live for cache key.
    
    Args:
        key: Cache key
        
    Returns:
        TTL in seconds, -1 if key has no expiration, -2 if key doesn't exist
        
    I/O Operation - Redis TTL check.
    """
    if not REDIS_AVAILABLE:
        return -2
    
    try:
        client = get_redis_client()
        if client is None:
            return -2
        return client.ttl(key)
    except Exception as e:
        print(f"Redis cache TTL error: {e}")
        return -2