"""
Tests for Pure Caching Functions
Demonstrates cache strategy and invalidation without side effects
NO MOCKING REQUIRED - Pure functions = predictable cache behavior
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from app.data.caching import (
    # Cache key generation
    create_cache_key,
    create_memory_cache_key,
    create_disk_cache_path,
    # Cache expiration
    is_cache_expired,
    calculate_cache_expiry,
    should_refresh_cache,
    # Cache invalidation
    find_cache_keys_to_invalidate,
    create_cache_invalidation_plan,
    # Cache storage format
    serialize_cached_result,
    deserialize_cached_result,
    # Cache statistics
    calculate_cache_hit_rate,
    analyze_cache_performance,
    # Cache strategy
    select_cache_strategy,
    create_cache_warming_plan,
    # Cache cleanup
    find_expired_cache_entries,
    calculate_cache_size_limit,
    select_cache_entries_for_eviction,
    # Cache health
    assess_cache_health
)
from app.models import CachedFilterResult, FilteredCalendar


# === TEST DATA FIXTURES ===

@pytest.fixture
def sample_cached_result():
    """Sample cached filter result"""
    from datetime import datetime, timedelta
    future_expiry = (datetime.now() + timedelta(hours=1)).isoformat()
    
    return CachedFilterResult(
        cache_key="filtered_cal_abc123",
        filtered_ical_content="BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR",
        event_count=5,
        created_at="2024-01-15T10:00:00",
        expires_at=future_expiry,  # 1 hour from now
        filter_config_hash="filter_hash_123",
        source_content_hash="source_hash_456"
    )


@pytest.fixture
def sample_filtered_calendar():
    """Sample filtered calendar"""
    return FilteredCalendar(
        id="fc123",
        source_calendar_id="cal456",
        filter_config_id="filter789",
        public_token="abc123def456",
        name="Work Events",
        description="Filtered work events",
        user_id="user123",
        created_at="2024-01-15T09:00:00",
        last_accessed="2024-01-15T10:30:00",
        access_count=25,
        cache_key="filtered_cal_abc123",
        cache_expires_at="2024-01-15T11:00:00",
        is_active=True
    )


# === CACHE KEY GENERATION TESTS (Pure Functions) ===

class TestCacheKeyGeneration:
    
    def test_create_cache_key_deterministic(self):
        """Test cache key generation is deterministic"""
        key1 = create_cache_key("cal123", "filter456", "content789")
        key2 = create_cache_key("cal123", "filter456", "content789")
        
        # Same inputs should produce same key
        assert key1 == key2
        
        # Different inputs should produce different keys
        key3 = create_cache_key("cal123", "filter456", "content999")
        assert key1 != key3
    
    def test_create_cache_key_format(self):
        """Test cache key format"""
        key = create_cache_key("cal123", "filter456", "content789", "v2")
        
        assert key.startswith("filtered_cal_")
        assert len(key) == 29  # "filtered_cal_" + 16 hex chars
    
    def test_create_memory_cache_key(self):
        """Test memory cache key creation"""
        cache_key = "filtered_cal_abc123"
        memory_key = create_memory_cache_key(cache_key)
        
        assert memory_key == "mem:filtered_cal_abc123"
    
    def test_create_disk_cache_path(self):
        """Test disk cache path creation"""
        cache_key = "filtered_cal_abc123"
        cache_dir = Path("/tmp/cache")
        
        path = create_disk_cache_path(cache_key, cache_dir)
        
        assert str(path) == "/tmp/cache/fi/filtered_cal_abc123.json"
        assert path.name == "filtered_cal_abc123.json"
        assert path.parent.name == "fi"  # First 2 chars


# === CACHE EXPIRATION TESTS (Pure Functions) ===

class TestCacheExpiration:
    
    def test_is_cache_expired_valid(self, sample_cached_result):
        """Test cache expiration checking for valid cache"""
        # Set expiry to future
        future_expiry = (datetime.now() + timedelta(hours=1)).isoformat()
        expired_result = CachedFilterResult(
            **{**sample_cached_result.__dict__, 'expires_at': future_expiry}
        )
        
        assert is_cache_expired(expired_result) is False
    
    def test_is_cache_expired_expired(self, sample_cached_result):
        """Test cache expiration checking for expired cache"""
        # Set expiry to past
        past_expiry = (datetime.now() - timedelta(hours=1)).isoformat()
        expired_result = CachedFilterResult(
            **{**sample_cached_result.__dict__, 'expires_at': past_expiry}
        )
        
        assert is_cache_expired(expired_result) is True
    
    def test_calculate_cache_expiry(self):
        """Test cache expiry calculation"""
        created_at = datetime(2024, 1, 15, 10, 0, 0)
        
        # Test different strategies
        aggressive_expiry = calculate_cache_expiry("aggressive", created_at)
        assert aggressive_expiry == created_at + timedelta(hours=1)
        
        balanced_expiry = calculate_cache_expiry("balanced", created_at)
        assert balanced_expiry == created_at + timedelta(minutes=15)
        
        real_time_expiry = calculate_cache_expiry("real_time", created_at)
        assert real_time_expiry == created_at + timedelta(minutes=1)
        
        # Test unknown strategy defaults to balanced
        unknown_expiry = calculate_cache_expiry("unknown", created_at)
        assert unknown_expiry == created_at + timedelta(minutes=15)
    
    def test_should_refresh_cache(self, sample_cached_result):
        """Test cache refresh decision logic"""
        # Valid cache - should not refresh
        should_refresh, reason = should_refresh_cache(
            sample_cached_result, 
            "filter_hash_123", 
            "source_hash_456"
        )
        assert should_refresh is False
        assert reason == "valid"
        
        # Expired cache - should refresh
        past_expiry = (datetime.now() - timedelta(hours=1)).isoformat()
        expired_result = CachedFilterResult(
            **{**sample_cached_result.__dict__, 'expires_at': past_expiry}
        )
        should_refresh, reason = should_refresh_cache(
            expired_result, 
            "filter_hash_123", 
            "source_hash_456"
        )
        assert should_refresh is True
        assert reason == "expired"
        
        # Filter changed - should refresh
        should_refresh, reason = should_refresh_cache(
            sample_cached_result, 
            "new_filter_hash", 
            "source_hash_456"
        )
        assert should_refresh is True
        assert reason == "filter_changed"
        
        # Source changed - should refresh
        should_refresh, reason = should_refresh_cache(
            sample_cached_result, 
            "filter_hash_123", 
            "new_source_hash"
        )
        assert should_refresh is True
        assert reason == "source_changed"


# === CACHE INVALIDATION TESTS (Pure Functions) ===

class TestCacheInvalidation:
    
    def test_find_cache_keys_to_invalidate(self):
        """Test finding cache keys for invalidation"""
        all_keys = [
            "filtered_cal_user123_cal456_abc",
            "filtered_cal_user123_cal789_def", 
            "filtered_cal_user456_cal456_ghi",
            "filtered_cal_user789_cal999_jkl"
        ]
        
        # Invalidate by source calendar
        keys_to_invalidate = find_cache_keys_to_invalidate(
            all_keys, 
            {"source_calendar_id": "cal456"}
        )
        
        assert len(keys_to_invalidate) == 2
        assert "filtered_cal_user123_cal456_abc" in keys_to_invalidate
        assert "filtered_cal_user456_cal456_ghi" in keys_to_invalidate
        
        # Invalidate by user
        keys_to_invalidate = find_cache_keys_to_invalidate(
            all_keys, 
            {"user_id": "user123"}
        )
        
        assert len(keys_to_invalidate) == 2
        assert "filtered_cal_user123_cal456_abc" in keys_to_invalidate
        assert "filtered_cal_user123_cal789_def" in keys_to_invalidate
    
    def test_create_cache_invalidation_plan(self, sample_filtered_calendar):
        """Test cache invalidation plan creation"""
        # Test filter config update
        plan = create_cache_invalidation_plan(sample_filtered_calendar, "filter_config_updated")
        
        assert len(plan["memory_keys"]) > 0
        assert len(plan["disk_keys"]) > 0
        assert len(plan["database_keys"]) > 0
        assert sample_filtered_calendar.id in plan["database_keys"]
        
        # Test source calendar update
        plan = create_cache_invalidation_plan(sample_filtered_calendar, "source_calendar_updated")
        
        assert sample_filtered_calendar.source_calendar_id in plan["database_keys"]
        
        # Test filtered calendar deletion
        plan = create_cache_invalidation_plan(sample_filtered_calendar, "filtered_calendar_deleted")
        
        assert sample_filtered_calendar.id in plan["database_keys"]


# === CACHE STORAGE FORMAT TESTS (Pure Functions) ===

class TestCacheStorageFormat:
    
    def test_serialize_cached_result(self, sample_cached_result):
        """Test cached result serialization"""
        json_string = serialize_cached_result(sample_cached_result)
        
        assert isinstance(json_string, str)
        assert "cache_key" in json_string
        assert "filtered_ical_content" in json_string
        assert "event_count" in json_string
        assert "version" in json_string
    
    def test_deserialize_cached_result(self, sample_cached_result):
        """Test cached result deserialization"""
        # Serialize then deserialize
        json_string = serialize_cached_result(sample_cached_result)
        deserialized = deserialize_cached_result(json_string)
        
        assert deserialized is not None
        assert deserialized.cache_key == sample_cached_result.cache_key
        assert deserialized.event_count == sample_cached_result.event_count
        assert deserialized.filtered_ical_content == sample_cached_result.filtered_ical_content
    
    def test_deserialize_invalid_json(self):
        """Test deserialization of invalid JSON"""
        # Invalid JSON
        result = deserialize_cached_result("invalid json")
        assert result is None
        
        # Missing required fields
        incomplete_json = '{"cache_key": "abc123"}'
        result = deserialize_cached_result(incomplete_json)
        assert result is None
        
        # Wrong data types
        wrong_types_json = '{"cache_key": 123, "event_count": "not a number"}'
        result = deserialize_cached_result(wrong_types_json)
        assert result is None


# === CACHE STATISTICS TESTS (Pure Functions) ===

class TestCacheStatistics:
    
    def test_calculate_cache_hit_rate(self):
        """Test cache hit rate calculation"""
        now = datetime.now()
        access_logs = [
            {"timestamp": (now - timedelta(hours=1)).isoformat(), "cache_hit": True},
            {"timestamp": (now - timedelta(hours=2)).isoformat(), "cache_hit": False},
            {"timestamp": (now - timedelta(hours=3)).isoformat(), "cache_hit": True},
            {"timestamp": (now - timedelta(days=2)).isoformat(), "cache_hit": False},  # Outside window
        ]
        
        stats = calculate_cache_hit_rate(access_logs, time_window_hours=24)
        
        assert stats["total_requests"] == 3  # 3 within 24 hours
        assert stats["cache_hits"] == 2
        assert stats["cache_misses"] == 1
        assert stats["hit_rate_percent"] == 66.67
    
    def test_calculate_cache_hit_rate_empty(self):
        """Test cache hit rate calculation with no data"""
        stats = calculate_cache_hit_rate([], time_window_hours=24)
        
        assert stats["total_requests"] == 0
        assert stats["cache_hits"] == 0
        assert stats["cache_misses"] == 0
        assert stats["hit_rate_percent"] == 0.0
    
    def test_analyze_cache_performance(self):
        """Test cache performance analysis"""
        cached_results = [
            CachedFilterResult(
                cache_key="key1",
                filtered_ical_content="a" * 5000,  # 5KB - small
                event_count=10,
                created_at="2024-01-15T10:00:00",
                expires_at=(datetime.now() + timedelta(hours=1)).isoformat(),  # Fresh
                filter_config_hash="hash1",
                source_content_hash="source1"
            ),
            CachedFilterResult(
                cache_key="key2", 
                filtered_ical_content="b" * 50000,  # 50KB - medium
                event_count=50,
                created_at="2024-01-15T10:00:00",
                expires_at=(datetime.now() + timedelta(hours=1)).isoformat(),  # Fresh
                filter_config_hash="hash2",
                source_content_hash="source2"
            ),
            CachedFilterResult(
                cache_key="key3",
                filtered_ical_content="c" * 500000,  # 500KB - large
                event_count=500,
                created_at="2024-01-15T10:00:00",
                expires_at=(datetime.now() - timedelta(hours=1)).isoformat(),  # Expired
                filter_config_hash="hash3",
                source_content_hash="source3"
            )
        ]
        
        analysis = analyze_cache_performance(cached_results)
        
        assert analysis["total_cached_items"] == 3
        assert analysis["total_cached_events"] == 560
        assert analysis["average_event_count"] == 186.7
        assert analysis["cache_size_distribution"]["small"] == 1
        assert analysis["cache_size_distribution"]["medium"] == 1
        assert analysis["cache_size_distribution"]["large"] == 1
        assert analysis["expiry_distribution"]["expired"] == 1
        assert analysis["expiry_distribution"]["fresh"] == 2


# === CACHE STRATEGY TESTS (Pure Functions) ===

class TestCacheStrategy:
    
    def test_select_cache_strategy(self):
        """Test cache strategy selection"""
        # High traffic, frequent updates -> real_time
        characteristics = {
            "update_frequency_hours": 1,
            "event_count": 100,
            "daily_accesses": 150
        }
        strategy = select_cache_strategy(characteristics)
        assert strategy == "real_time"
        
        # High traffic, stable -> aggressive
        characteristics = {
            "update_frequency_hours": 24,
            "event_count": 100,
            "daily_accesses": 100
        }
        strategy = select_cache_strategy(characteristics)
        assert strategy == "aggressive"
        
        # Low traffic -> long_term
        characteristics = {
            "update_frequency_hours": 24,
            "event_count": 50,
            "daily_accesses": 5
        }
        strategy = select_cache_strategy(characteristics)
        assert strategy == "long_term"
        
        # Default case -> balanced
        characteristics = {
            "update_frequency_hours": 12,
            "event_count": 100,
            "daily_accesses": 25
        }
        strategy = select_cache_strategy(characteristics)
        assert strategy == "balanced"
    
    def test_create_cache_warming_plan(self):
        """Test cache warming plan creation"""
        filtered_calendars = [
            FilteredCalendar(
                id="fc1", source_calendar_id="cal1", filter_config_id="f1",
                public_token="token1", name="High Traffic", description="",
                user_id="user1", created_at="", last_accessed="",
                access_count=0, cache_key="", cache_expires_at="", is_active=True
            ),
            FilteredCalendar(
                id="fc2", source_calendar_id="cal2", filter_config_id="f2",
                public_token="token2", name="Medium Traffic", description="",
                user_id="user2", created_at="", last_accessed="",
                access_count=0, cache_key="", cache_expires_at="", is_active=True
            ),
            FilteredCalendar(
                id="fc3", source_calendar_id="cal3", filter_config_id="f3",
                public_token="token3", name="Low Traffic", description="",
                user_id="user3", created_at="", last_accessed="",
                access_count=0, cache_key="", cache_expires_at="", is_active=True
            )
        ]
        
        access_patterns = {
            "fc1": 150,  # High priority
            "fc2": 25,   # Medium priority
            "fc3": 2     # Skip (too low)
        }
        
        warming_plan = create_cache_warming_plan(filtered_calendars, access_patterns)
        
        assert len(warming_plan) == 2  # fc1 and fc2, fc3 skipped
        assert warming_plan[0]["filtered_calendar_id"] == "fc1"
        assert warming_plan[0]["priority"] == "high"
        assert warming_plan[1]["filtered_calendar_id"] == "fc2"
        assert warming_plan[1]["priority"] == "medium"


# === CACHE CLEANUP TESTS (Pure Functions) ===

class TestCacheCleanup:
    
    def test_find_expired_cache_entries(self):
        """Test finding expired cache entries"""
        now = datetime.now()
        cached_results = [
            CachedFilterResult(
                cache_key="key1",
                filtered_ical_content="content1",
                event_count=10,
                created_at=now.isoformat(),
                expires_at=(now + timedelta(hours=1)).isoformat(),  # Valid
                filter_config_hash="hash1",
                source_content_hash="source1"
            ),
            CachedFilterResult(
                cache_key="key2",
                filtered_ical_content="content2", 
                event_count=20,
                created_at=now.isoformat(),
                expires_at=(now - timedelta(hours=1)).isoformat(),  # Expired
                filter_config_hash="hash2",
                source_content_hash="source2"
            )
        ]
        
        expired_keys = find_expired_cache_entries(cached_results)
        
        assert len(expired_keys) == 1
        assert "key2" in expired_keys
    
    def test_calculate_cache_size_limit(self):
        """Test cache size limit calculation"""
        # 1000 MB available, 10% reserved, 50% of usable for cache
        limit = calculate_cache_size_limit(1000, 0.1)
        
        # 1000 * 0.9 * 0.5 = 450 MB = 471,859,200 bytes
        expected = int(1000 * 0.9 * 0.5 * 1024 * 1024)
        assert limit == expected
    
    def test_select_cache_entries_for_eviction(self):
        """Test cache entry eviction selection"""
        now = datetime.now()
        cached_results = [
            CachedFilterResult(
                cache_key="key1",
                filtered_ical_content="a" * 1000,  # Small, recent
                event_count=10,
                created_at=now.isoformat(),
                expires_at=(now + timedelta(hours=1)).isoformat(),
                filter_config_hash="hash1",
                source_content_hash="source1"
            ),
            CachedFilterResult(
                cache_key="key2",
                filtered_ical_content="b" * 10000,  # Large, old
                event_count=100,
                created_at=(now - timedelta(days=1)).isoformat(),
                expires_at=(now + timedelta(hours=1)).isoformat(),
                filter_config_hash="hash2",
                source_content_hash="source2"
            )
        ]
        
        access_logs = [
            {"cache_key": "key1", "timestamp": now.isoformat()},  # Recently accessed
            # key2 not accessed recently
        ]
        
        keys_to_evict = select_cache_entries_for_eviction(
            cached_results, 
            access_logs, 
            target_size_bytes=5000  # Should evict key2 first
        )
        
        # Should evict key2 first (larger, older, less accessed)
        assert "key2" in keys_to_evict


# === CACHE HEALTH TESTS (Pure Functions) ===

class TestCacheHealth:
    
    def test_assess_cache_health_excellent(self):
        """Test cache health assessment - excellent case"""
        cache_stats = {
            "hit_rate_percent": 85,
            "expiry_distribution": {"expired": 2, "soon": 5, "fresh": 93},
            "total_cached_items": 100
        }
        
        health = assess_cache_health(cache_stats)
        
        assert health["overall_health"] == "excellent"
        assert health["hit_rate_health"] == "excellent"
        assert health["expiry_health"] == "excellent"
        assert len(health["recommendations"]) == 0
    
    def test_assess_cache_health_poor(self):
        """Test cache health assessment - poor case"""
        cache_stats = {
            "hit_rate_percent": 25,
            "expiry_distribution": {"expired": 40, "soon": 10, "fresh": 50},
            "total_cached_items": 100
        }
        
        health = assess_cache_health(cache_stats)
        
        assert health["overall_health"] == "poor"
        assert health["hit_rate_health"] == "poor"
        assert health["expiry_health"] == "poor"
        assert len(health["recommendations"]) > 0
        assert any("cache TTL" in rec for rec in health["recommendations"])
        assert any("cleanup frequency" in rec for rec in health["recommendations"])
    
    def test_assess_cache_health_with_recommendations(self):
        """Test cache health recommendations"""
        cache_stats = {
            "hit_rate_percent": 45,  # Fair - triggers TTL recommendation 
            "expiry_distribution": {"expired": 3000, "soon": 500, "fresh": 6500},  # 30% expired - triggers cleanup
            "total_cached_items": 15000  # Large - triggers size limits
        }
        
        health = assess_cache_health(cache_stats)
        
        recommendations = health["recommendations"]
        assert any("cache TTL" in rec for rec in recommendations)
        assert any("cleanup frequency" in rec for rec in recommendations)
        assert any("cache size limits" in rec for rec in recommendations)


# === EDGE CASES AND PERFORMANCE TESTS ===

class TestCacheEdgeCases:
    
    def test_empty_data_handling(self):
        """Test caching functions handle empty data gracefully"""
        # Empty cached results
        analysis = analyze_cache_performance([])
        assert analysis["total_cached_items"] == 0
        
        # Empty access logs
        stats = calculate_cache_hit_rate([])
        assert stats["total_requests"] == 0
        
        # Empty warming plan
        plan = create_cache_warming_plan([], {})
        assert len(plan) == 0
    
    def test_invalid_data_handling(self):
        """Test caching functions handle invalid data gracefully"""
        # Invalid expiry date
        invalid_result = CachedFilterResult(
            cache_key="key1",
            filtered_ical_content="content",
            event_count=10,
            created_at="invalid-date",
            expires_at="invalid-date",
            filter_config_hash="hash1",
            source_content_hash="source1"
        )
        
        # Should treat as expired for safety
        assert is_cache_expired(invalid_result) is True
    
    def test_cache_performance_with_large_data(self):
        """Test cache operations performance with large datasets"""
        # Create 1000 cache entries
        large_dataset = []
        for i in range(1000):
            result = CachedFilterResult(
                cache_key=f"key{i}",
                filtered_ical_content=f"content{i}" * 100,  # ~800 bytes each
                event_count=i % 100,
                created_at="2024-01-15T10:00:00",
                expires_at="2024-01-15T11:00:00",
                filter_config_hash=f"hash{i}",
                source_content_hash=f"source{i}"
            )
            large_dataset.append(result)
        
        # Test performance of analysis
        import time
        start_time = time.time()
        
        analysis = analyze_cache_performance(large_dataset)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly even with large dataset
        assert duration < 1.0  # < 1 second
        assert analysis["total_cached_items"] == 1000


"""
WHAT THESE TESTS DEMONSTRATE ABOUT FUNCTIONAL CACHING:

1. PREDICTABLE CACHE BEHAVIOR
   - Cache operations are deterministic and testable
   - No hidden cache state or side effects
   - Cache strategies are pure functions

2. NO MOCKING FOR CACHE TESTS
   - Can test actual cache key generation and validation
   - Real cache expiry and invalidation logic tested
   - No mocked cache that might hide performance issues

3. COMPOSABLE CACHE STRATEGIES
   - Cache functions combine safely
   - Can test cache pipelines end-to-end
   - Clear cache boundaries and responsibilities

4. PERFORMANCE TESTING
   - Can measure actual cache operation performance
   - Cache overhead quantifiable
   - Eviction strategies verifiable

5. COMPREHENSIVE COVERAGE
   - Can test all cache scenarios and edge cases
   - Cache health monitoring is thorough and reliable
   - No untestable cache-critical code paths

This demonstrates that functional programming enhances caching:
- Predictable cache behavior reduces cache-related bugs
- Pure cache functions are easier to optimize
- Composable cache strategies create flexible caching systems
- Cache health can be precisely measured and improved
"""