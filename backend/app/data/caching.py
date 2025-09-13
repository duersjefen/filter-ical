"""
Caching Functions - Rich Hickey Style
Pure functions for multi-tier caching with immutable data
No side effects, explicit data flow, composable cache strategies
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from ..models import CachedFilterResult, FilteredCalendar, Event


# === CACHE KEY GENERATION (Pure Functions) ===

def create_cache_key(filtered_calendar_id: str, filter_config_hash: str, 
                    source_content_hash: str, cache_version: str = "v1") -> str:
    """
    Pure function: Generate deterministic cache key
    Returns: Unique cache key for filtered calendar result
    """
    key_components = [
        cache_version,
        filtered_calendar_id,
        filter_config_hash,
        source_content_hash
    ]
    key_string = ":".join(key_components)
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()
    return f"filtered_cal_{key_hash[:16]}"


def create_memory_cache_key(cache_key: str) -> str:
    """
    Pure function: Create memory cache key with prefix
    Returns: Memory cache key
    """
    return f"mem:{cache_key}"


def create_disk_cache_path(cache_key: str, cache_dir: Path) -> Path:
    """
    Pure function: Create disk cache file path
    Returns: Path object for cache file
    """
    # Use first 2 chars for subdirectory to avoid too many files in one dir
    subdir = cache_key[:2]
    return cache_dir / subdir / f"{cache_key}.json"


# === CACHE EXPIRATION (Pure Functions) ===

def is_cache_expired(cached_result: CachedFilterResult) -> bool:
    """
    Pure function: Check if cached result has expired
    Returns: True if cache is expired
    """
    try:
        expires_at = datetime.fromisoformat(cached_result.expires_at)
        return datetime.now() > expires_at
    except (ValueError, AttributeError):
        return True


def calculate_cache_expiry(cache_strategy: str, created_at: datetime) -> datetime:
    """
    Pure function: Calculate cache expiry time based on strategy
    Returns: Expiry datetime
    """
    strategies = {
        'aggressive': timedelta(hours=1),
        'balanced': timedelta(minutes=15),
        'real_time': timedelta(minutes=1),
        'long_term': timedelta(days=1)
    }
    
    duration = strategies.get(cache_strategy, timedelta(minutes=15))
    return created_at + duration


def should_refresh_cache(cached_result: CachedFilterResult, 
                        current_filter_hash: str, 
                        current_source_hash: str) -> Tuple[bool, str]:
    """
    Pure function: Determine if cache needs refresh
    Returns: (should_refresh, reason)
    """
    # Check expiry
    if is_cache_expired(cached_result):
        return True, "expired"
    
    # Check filter configuration change
    if cached_result.filter_config_hash != current_filter_hash:
        return True, "filter_changed"
    
    # Check source content change
    if cached_result.source_content_hash != current_source_hash:
        return True, "source_changed"
    
    return False, "valid"


# === CACHE INVALIDATION (Pure Functions) ===

def find_cache_keys_to_invalidate(all_cache_keys: List[str], 
                                 invalidation_criteria: Dict[str, str]) -> List[str]:
    """
    Pure function: Find cache keys that should be invalidated
    Returns: List of cache keys to invalidate
    """
    keys_to_invalidate = []
    
    for cache_key in all_cache_keys:
        should_invalidate = False
        
        # Check each invalidation criterion
        for criterion, value in invalidation_criteria.items():
            if criterion == 'source_calendar_id' and value in cache_key:
                should_invalidate = True
                break
            elif criterion == 'user_id' and value in cache_key:
                should_invalidate = True
                break
            elif criterion == 'filter_config_id' and value in cache_key:
                should_invalidate = True
                break
        
        if should_invalidate:
            keys_to_invalidate.append(cache_key)
    
    return keys_to_invalidate


def create_cache_invalidation_plan(filtered_calendar: FilteredCalendar,
                                  change_type: str) -> Dict[str, List[str]]:
    """
    Pure function: Create cache invalidation plan
    Returns: Plan with cache keys to invalidate by tier
    """
    plan = {
        'memory_keys': [],
        'disk_keys': [],
        'database_keys': []
    }
    
    if change_type == 'filter_config_updated':
        # Invalidate all caches for this filtered calendar
        base_pattern = f"*{filtered_calendar.id}*"
        plan['memory_keys'] = [f"mem:{base_pattern}"]
        plan['disk_keys'] = [base_pattern]
        plan['database_keys'] = [filtered_calendar.id]
        
    elif change_type == 'source_calendar_updated':
        # Invalidate all filtered calendars from this source
        source_pattern = f"*{filtered_calendar.source_calendar_id}*"
        plan['memory_keys'] = [f"mem:{source_pattern}"]
        plan['disk_keys'] = [source_pattern]
        plan['database_keys'] = [filtered_calendar.source_calendar_id]
        
    elif change_type == 'filtered_calendar_deleted':
        # Invalidate all caches for this specific filtered calendar
        calendar_pattern = f"*{filtered_calendar.id}*"
        plan['memory_keys'] = [f"mem:{calendar_pattern}"]
        plan['disk_keys'] = [calendar_pattern]
        plan['database_keys'] = [filtered_calendar.id]
    
    return plan


# === CACHE STORAGE FORMAT (Pure Functions) ===

def serialize_cached_result(cached_result: CachedFilterResult) -> str:
    """
    Pure function: Serialize cached result to JSON string
    Returns: JSON string representation
    """
    data = {
        'cache_key': cached_result.cache_key,
        'filtered_ical_content': cached_result.filtered_ical_content,
        'event_count': cached_result.event_count,
        'created_at': cached_result.created_at,
        'expires_at': cached_result.expires_at,
        'filter_config_hash': cached_result.filter_config_hash,
        'source_content_hash': cached_result.source_content_hash,
        'version': 'v1'
    }
    return json.dumps(data, separators=(',', ':'))


def deserialize_cached_result(json_string: str) -> Optional[CachedFilterResult]:
    """
    Pure function: Deserialize JSON string to cached result
    Returns: CachedFilterResult or None if invalid
    """
    try:
        data = json.loads(json_string)
        
        # Validate required fields
        required_fields = [
            'cache_key', 'filtered_ical_content', 'event_count',
            'created_at', 'expires_at', 'filter_config_hash', 'source_content_hash'
        ]
        
        if not all(field in data for field in required_fields):
            return None
        
        return CachedFilterResult(
            cache_key=data['cache_key'],
            filtered_ical_content=data['filtered_ical_content'],
            event_count=data['event_count'],
            created_at=data['created_at'],
            expires_at=data['expires_at'],
            filter_config_hash=data['filter_config_hash'],
            source_content_hash=data['source_content_hash']
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


# === CACHE STATISTICS (Pure Functions) ===

def calculate_cache_hit_rate(access_logs: List[Dict[str, Any]], 
                           time_window_hours: int = 24) -> Dict[str, float]:
    """
    Pure function: Calculate cache hit rates
    Returns: Dictionary with cache statistics
    """
    cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
    
    # Filter recent access logs
    recent_logs = [
        log for log in access_logs
        if datetime.fromisoformat(log['timestamp']) > cutoff_time
    ]
    
    if not recent_logs:
        return {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'hit_rate_percent': 0.0
        }
    
    total_requests = len(recent_logs)
    cache_hits = sum(1 for log in recent_logs if log.get('cache_hit', False))
    cache_misses = total_requests - cache_hits
    hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
    
    return {
        'total_requests': total_requests,
        'cache_hits': cache_hits,
        'cache_misses': cache_misses,
        'hit_rate_percent': round(hit_rate, 2)
    }


def analyze_cache_performance(cached_results: List[CachedFilterResult]) -> Dict[str, Any]:
    """
    Pure function: Analyze cache performance metrics
    Returns: Performance analysis
    """
    if not cached_results:
        return {
            'total_cached_items': 0,
            'average_event_count': 0,
            'cache_size_distribution': {}
        }
    
    total_items = len(cached_results)
    total_events = sum(result.event_count for result in cached_results)
    average_events = total_events / total_items if total_items > 0 else 0
    
    # Analyze cache size distribution
    size_buckets = {'small': 0, 'medium': 0, 'large': 0, 'huge': 0}
    
    for result in cached_results:
        content_size = len(result.filtered_ical_content)
        if content_size < 10_000:  # < 10KB
            size_buckets['small'] += 1
        elif content_size < 100_000:  # < 100KB
            size_buckets['medium'] += 1
        elif content_size < 1_000_000:  # < 1MB
            size_buckets['large'] += 1
        else:
            size_buckets['huge'] += 1
    
    # Calculate expiry distribution
    now = datetime.now()
    expiry_buckets = {'expired': 0, 'soon': 0, 'fresh': 0}
    
    for result in cached_results:
        try:
            expires_at = datetime.fromisoformat(result.expires_at)
            if expires_at < now:
                expiry_buckets['expired'] += 1
            elif expires_at < now + timedelta(minutes=5):
                expiry_buckets['soon'] += 1
            else:
                expiry_buckets['fresh'] += 1
        except ValueError:
            expiry_buckets['expired'] += 1
    
    return {
        'total_cached_items': total_items,
        'total_cached_events': total_events,
        'average_event_count': round(average_events, 1),
        'cache_size_distribution': size_buckets,
        'expiry_distribution': expiry_buckets
    }


# === CACHE STRATEGY (Pure Functions) ===

def select_cache_strategy(calendar_characteristics: Dict[str, Any]) -> str:
    """
    Pure function: Select optimal cache strategy based on calendar characteristics
    Returns: Cache strategy name
    """
    update_frequency = calendar_characteristics.get('update_frequency_hours', 24)
    event_count = calendar_characteristics.get('event_count', 0)
    access_frequency = calendar_characteristics.get('daily_accesses', 0)
    
    # High-traffic, frequently updated calendars
    if access_frequency > 100 and update_frequency < 2:
        return 'real_time'
    
    # High-traffic, stable calendars
    elif access_frequency > 50 and update_frequency > 12:
        return 'aggressive'
    
    # Low-traffic calendars
    elif access_frequency < 10:
        return 'long_term'
    
    # Default balanced strategy
    else:
        return 'balanced'


def create_cache_warming_plan(filtered_calendars: List[FilteredCalendar],
                            access_patterns: Dict[str, int]) -> List[Dict[str, str]]:
    """
    Pure function: Create cache warming plan for popular calendars
    Returns: List of calendars to pre-warm with priority
    """
    warming_plan = []
    
    for calendar in filtered_calendars:
        access_count = access_patterns.get(calendar.id, 0)
        
        # Determine warming priority
        if access_count > 100:
            priority = 'high'
        elif access_count > 20:
            priority = 'medium'
        elif access_count > 5:
            priority = 'low'
        else:
            continue  # Skip rarely accessed calendars
        
        warming_plan.append({
            'filtered_calendar_id': calendar.id,
            'priority': priority,
            'estimated_access_count': access_count
        })
    
    # Sort by priority and access count
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    warming_plan.sort(
        key=lambda x: (priority_order[x['priority']], x['estimated_access_count']),
        reverse=True
    )
    
    return warming_plan


# === CACHE CLEANUP (Pure Functions) ===

def find_expired_cache_entries(cached_results: List[CachedFilterResult]) -> List[str]:
    """
    Pure function: Find expired cache entries for cleanup
    Returns: List of cache keys to remove
    """
    expired_keys = []
    
    for result in cached_results:
        if is_cache_expired(result):
            expired_keys.append(result.cache_key)
    
    return expired_keys


def calculate_cache_size_limit(available_disk_mb: int, 
                              reserved_percent: float = 0.1) -> int:
    """
    Pure function: Calculate appropriate cache size limit
    Returns: Maximum cache size in bytes
    """
    # Reserve percentage of disk space for other operations
    usable_disk_mb = available_disk_mb * (1.0 - reserved_percent)
    
    # Use up to 50% of usable space for cache
    cache_limit_mb = usable_disk_mb * 0.5
    
    # Convert to bytes
    return int(cache_limit_mb * 1024 * 1024)


def select_cache_entries_for_eviction(cached_results: List[CachedFilterResult],
                                     access_logs: List[Dict[str, Any]],
                                     target_size_bytes: int) -> List[str]:
    """
    Pure function: Select cache entries to evict based on LRU + size
    Returns: List of cache keys to evict
    """
    # Create access frequency map
    access_counts = {}
    for log in access_logs:
        cache_key = log.get('cache_key')
        if cache_key:
            access_counts[cache_key] = access_counts.get(cache_key, 0) + 1
    
    # Score each cache entry for eviction
    scored_entries = []
    for result in cached_results:
        content_size = len(result.filtered_ical_content)
        access_count = access_counts.get(result.cache_key, 0)
        
        # Calculate eviction score (higher = more likely to evict)
        # Factors: low access count, large size, older creation time
        try:
            age_hours = (datetime.now() - datetime.fromisoformat(result.created_at)).total_seconds() / 3600
        except ValueError:
            age_hours = 24  # Default to old if unparseable
        
        # Score formula: prioritize removing large, rarely accessed, old entries
        eviction_score = (content_size * 0.0001) + (age_hours * 0.1) - (access_count * 0.5)
        
        scored_entries.append({
            'cache_key': result.cache_key,
            'size_bytes': content_size,
            'eviction_score': eviction_score
        })
    
    # Sort by eviction score (descending - highest scores first)
    scored_entries.sort(key=lambda x: x['eviction_score'], reverse=True)
    
    # Select entries to evict until we reach target size
    keys_to_evict = []
    size_freed = 0
    
    for entry in scored_entries:
        keys_to_evict.append(entry['cache_key'])
        size_freed += entry['size_bytes']
        
        if size_freed >= target_size_bytes:
            break
    
    return keys_to_evict


# === CACHE HEALTH (Pure Functions) ===

def assess_cache_health(cache_stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure function: Assess overall cache health
    Returns: Health assessment with recommendations
    """
    hit_rate = cache_stats.get('hit_rate_percent', 0)
    expired_count = cache_stats.get('expiry_distribution', {}).get('expired', 0)
    total_items = cache_stats.get('total_cached_items', 0)
    
    # Assess hit rate health
    if hit_rate > 80:
        hit_rate_health = 'excellent'
    elif hit_rate > 60:
        hit_rate_health = 'good'
    elif hit_rate > 40:
        hit_rate_health = 'fair'
    else:
        hit_rate_health = 'poor'
    
    # Assess expiry health
    expired_ratio = (expired_count / total_items * 100) if total_items > 0 else 0
    if expired_ratio < 5:
        expiry_health = 'excellent'
    elif expired_ratio < 15:
        expiry_health = 'good'
    elif expired_ratio < 30:
        expiry_health = 'fair'
    else:
        expiry_health = 'poor'
    
    # Generate recommendations
    recommendations = []
    
    if hit_rate < 60:
        recommendations.append("Consider adjusting cache TTL or warming strategy")
    
    if expired_ratio > 20:
        recommendations.append("Increase cache cleanup frequency")
    
    if total_items > 10000:
        recommendations.append("Consider implementing cache size limits")
    
    return {
        'overall_health': min(hit_rate_health, expiry_health, key=lambda x: {
            'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1
        }[x]),
        'hit_rate_health': hit_rate_health,
        'expiry_health': expiry_health,
        'recommendations': recommendations,
        'metrics': {
            'hit_rate_percent': hit_rate,
            'expired_ratio_percent': round(expired_ratio, 1),
            'total_cached_items': total_items
        }
    }


# === CACHE CONFIGURATION ===

CACHE_STRATEGIES = {
    'aggressive': {
        'memory_ttl_minutes': 5,
        'disk_ttl_minutes': 60,
        'database_ttl_minutes': 1440,  # 24 hours
        'warming_enabled': True
    },
    'balanced': {
        'memory_ttl_minutes': 1,
        'disk_ttl_minutes': 15,
        'database_ttl_minutes': 60,
        'warming_enabled': True
    },
    'real_time': {
        'memory_ttl_minutes': 0.2,  # 12 seconds
        'disk_ttl_minutes': 1,
        'database_ttl_minutes': 5,
        'warming_enabled': False
    },
    'long_term': {
        'memory_ttl_minutes': 60,
        'disk_ttl_minutes': 1440,  # 24 hours
        'database_ttl_minutes': 10080,  # 7 days
        'warming_enabled': False
    }
}