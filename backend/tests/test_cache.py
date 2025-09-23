"""
Unit tests for cache functions.

Tests pure functions from app.data.cache module.
Critical for Redis cache key generation and data validation.
"""

import pytest
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

from app.data.cache import (
    generate_domain_events_cache_key,
    generate_domain_groups_cache_key,
    generate_cache_metadata_key,
    prepare_domain_events_for_cache,
    create_cache_metadata,
    is_cache_stale,
    extract_cache_statistics,
    validate_cached_domain_events,
    get_cache_keys_for_domain
)


@pytest.mark.unit
class TestCacheKeyGeneration:
    """Test cache key generation functions."""
    
    def test_generate_domain_events_cache_key(self):
        """Test generating domain events cache key."""
        result = generate_domain_events_cache_key("test_domain")
        
        assert result == "domain_events:test_domain"
        assert isinstance(result, str)
    
    def test_generate_domain_events_cache_key_special_chars(self):
        """Test generating cache key with special characters."""
        result = generate_domain_events_cache_key("test-domain_123")
        
        assert result == "domain_events:test-domain_123"
    
    def test_generate_domain_groups_cache_key(self):
        """Test generating domain groups cache key."""
        result = generate_domain_groups_cache_key("test_domain")
        
        assert result == "domain_groups:test_domain"
        assert isinstance(result, str)
    
    def test_generate_domain_groups_cache_key_different_domain(self):
        """Test generating cache key for different domain."""
        result = generate_domain_groups_cache_key("another_domain")
        
        assert result == "domain_groups:another_domain"
    
    def test_generate_cache_metadata_key(self):
        """Test generating cache metadata key."""
        result = generate_cache_metadata_key("test_domain")
        
        assert result == "domain_cache_meta:test_domain"
        assert isinstance(result, str)
    
    def test_cache_key_deterministic(self):
        """Test that cache key generation is deterministic."""
        domain_key = "test_domain"
        
        result1 = generate_domain_events_cache_key(domain_key)
        result2 = generate_domain_events_cache_key(domain_key)
        
        assert result1 == result2
    
    def test_get_cache_keys_for_domain(self):
        """Test getting all cache keys for a domain."""
        domain_key = "test_domain"
        
        result = get_cache_keys_for_domain(domain_key)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert "domain_events:test_domain" in result
        assert "domain_groups:test_domain" in result
        assert "domain_cache_meta:test_domain" in result
    
    def test_get_cache_keys_for_domain_different_domains(self):
        """Test cache keys are different for different domains."""
        keys1 = get_cache_keys_for_domain("domain1")
        keys2 = get_cache_keys_for_domain("domain2")
        
        # No overlap between different domain keys
        assert set(keys1).isdisjoint(set(keys2))


@pytest.mark.unit
class TestDataPreparation:
    """Test data preparation functions."""
    
    def test_prepare_domain_events_for_cache_basic(self):
        """Test basic domain events preparation for cache."""
        domain_events_response = {
            "groups": [
                {"id": 1, "name": "Group 1", "recurring_events": []}
            ],
            "ungrouped_events": [
                {"title": "Event 1", "event_count": 1, "events": []}
            ]
        }
        
        result = prepare_domain_events_for_cache(domain_events_response)
        
        # Original data preserved
        assert result["groups"] == domain_events_response["groups"]
        assert result["ungrouped_events"] == domain_events_response["ungrouped_events"]
        
        # Cache metadata added
        assert "cached_at" in result
        assert "cache_version" in result
        assert result["cache_version"] == "1.0"
        
        # Check timestamp format
        cached_at = result["cached_at"]
        assert isinstance(cached_at, str)
        # Should be ISO format with timezone
        datetime.fromisoformat(cached_at.replace('Z', '+00:00'))
    
    def test_prepare_domain_events_for_cache_preserves_original(self):
        """Test that preparation doesn't modify original data."""
        original_data = {
            "groups": [{"id": 1, "name": "Group"}],
            "ungrouped_events": []
        }
        original_copy = {**original_data}
        
        result = prepare_domain_events_for_cache(original_data)
        
        # Original data unchanged
        assert original_data == original_copy
        # Result is new object
        assert result is not original_data
    
    def test_prepare_domain_events_for_cache_empty_data(self):
        """Test preparing empty domain events data."""
        empty_data = {"groups": [], "ungrouped_events": []}
        
        result = prepare_domain_events_for_cache(empty_data)
        
        assert result["groups"] == []
        assert result["ungrouped_events"] == []
        assert "cached_at" in result
        assert "cache_version" in result


@pytest.mark.unit
class TestCacheMetadata:
    """Test cache metadata functions."""
    
    def test_create_cache_metadata_default_time(self):
        """Test creating cache metadata with default time."""
        result = create_cache_metadata("test_domain")
        
        assert result["domain_key"] == "test_domain"
        assert result["version"] == "1.0"
        assert "last_updated" in result
        assert "cache_created" in result
        
        # Both should be recent timestamps
        last_updated = datetime.fromisoformat(result["last_updated"].replace('Z', '+00:00'))
        cache_created = datetime.fromisoformat(result["cache_created"].replace('Z', '+00:00'))
        
        assert last_updated.tzinfo == timezone.utc
        assert cache_created.tzinfo == timezone.utc
        
        # Should be close to now
        now = datetime.now(timezone.utc)
        assert abs((now - last_updated).total_seconds()) < 5
        assert abs((now - cache_created).total_seconds()) < 5
    
    def test_create_cache_metadata_specific_time(self):
        """Test creating cache metadata with specific last_updated time."""
        specific_time = datetime(2025, 9, 20, 10, 0, 0, tzinfo=timezone.utc)
        
        result = create_cache_metadata("test_domain", specific_time)
        
        assert result["domain_key"] == "test_domain"
        last_updated = datetime.fromisoformat(result["last_updated"].replace('Z', '+00:00'))
        
        assert last_updated == specific_time
    
    def test_create_cache_metadata_different_domains(self):
        """Test creating metadata for different domains."""
        metadata1 = create_cache_metadata("domain1")
        metadata2 = create_cache_metadata("domain2")
        
        assert metadata1["domain_key"] == "domain1"
        assert metadata2["domain_key"] == "domain2"
        assert metadata1["domain_key"] != metadata2["domain_key"]


@pytest.mark.unit
class TestCacheStalenessCheck:
    """Test cache staleness checking functions."""
    
    def test_is_cache_stale_fresh_cache(self):
        """Test cache staleness check for fresh cache."""
        # Create metadata with recent timestamp
        now = datetime.now(timezone.utc)
        cache_metadata = {
            "cache_created": now.isoformat(),
            "version": "1.0"
        }
        
        # Check with 5 minute (300 second) max age
        result = is_cache_stale(cache_metadata, max_age_seconds=300)
        
        assert result is False  # Should not be stale
    
    def test_is_cache_stale_old_cache(self):
        """Test cache staleness check for old cache."""
        # Create metadata with old timestamp
        old_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        cache_metadata = {
            "cache_created": old_time.isoformat(),
            "version": "1.0"
        }
        
        # Check with 5 minute (300 second) max age
        result = is_cache_stale(cache_metadata, max_age_seconds=300)
        
        assert result is True  # Should be stale
    
    def test_is_cache_stale_edge_case(self):
        """Test cache staleness at exact boundary."""
        # Create metadata exactly at max age
        boundary_time = datetime.now(timezone.utc) - timedelta(seconds=300)
        cache_metadata = {
            "cache_created": boundary_time.isoformat(),
            "version": "1.0"
        }
        
        # Should be considered stale if exactly at boundary
        result = is_cache_stale(cache_metadata, max_age_seconds=300)
        
        assert result is True
    
    def test_is_cache_stale_missing_cache_created(self):
        """Test cache staleness with missing cache_created field."""
        cache_metadata = {"version": "1.0"}  # Missing cache_created
        
        result = is_cache_stale(cache_metadata, max_age_seconds=300)
        
        assert result is True  # Should be considered stale
    
    def test_is_cache_stale_invalid_timestamp(self):
        """Test cache staleness with invalid timestamp."""
        cache_metadata = {
            "cache_created": "invalid-timestamp",
            "version": "1.0"
        }
        
        result = is_cache_stale(cache_metadata, max_age_seconds=300)
        
        assert result is True  # Should be considered stale
    
    def test_is_cache_stale_empty_metadata(self):
        """Test cache staleness with empty metadata."""
        result = is_cache_stale({}, max_age_seconds=300)
        
        assert result is True  # Should be considered stale
    
    def test_is_cache_stale_with_z_suffix(self):
        """Test cache staleness with Z suffix timestamp."""
        # Create a timestamp from 1 minute ago (should not be stale)
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        # Create ISO format without timezone, then add Z
        timestamp_z = one_minute_ago.replace(tzinfo=None).isoformat() + "Z"
        cache_metadata = {
            "cache_created": timestamp_z,
            "version": "1.0"
        }
        
        result = is_cache_stale(cache_metadata, max_age_seconds=300)
        
        assert result is False  # Should handle Z suffix correctly and not be stale


@pytest.mark.unit
class TestCacheValidation:
    """Test cache validation functions."""
    
    def test_validate_cached_domain_events_valid(self):
        """Test validation of valid cached domain events."""
        cached_data = {
            "groups": [
                {"id": 1, "name": "Group 1", "recurring_events": []}
            ],
            "ungrouped_events": [
                {"title": "Event", "event_count": 1, "events": []}
            ],
            "cached_at": "2025-09-23T10:00:00+00:00",
            "cache_version": "1.0"
        }
        
        result = validate_cached_domain_events(cached_data)
        
        assert result is True
    
    def test_validate_cached_domain_events_missing_groups(self):
        """Test validation with missing groups field."""
        cached_data = {
            "ungrouped_events": [],
            "cached_at": "2025-09-23T10:00:00+00:00",
            "cache_version": "1.0"
        }
        
        result = validate_cached_domain_events(cached_data)
        
        assert result is False
    
    def test_validate_cached_domain_events_missing_ungrouped_events(self):
        """Test validation with missing ungrouped_events field."""
        cached_data = {
            "groups": [],
            "cached_at": "2025-09-23T10:00:00+00:00",
            "cache_version": "1.0"
        }
        
        result = validate_cached_domain_events(cached_data)
        
        assert result is False
    
    def test_validate_cached_domain_events_wrong_groups_type(self):
        """Test validation with wrong groups data type."""
        cached_data = {
            "groups": "not a list",  # Should be list
            "ungrouped_events": [],
            "cached_at": "2025-09-23T10:00:00+00:00",
            "cache_version": "1.0"
        }
        
        result = validate_cached_domain_events(cached_data)
        
        assert result is False
    
    def test_validate_cached_domain_events_wrong_ungrouped_events_type(self):
        """Test validation with wrong ungrouped_events data type."""
        cached_data = {
            "groups": [],
            "ungrouped_events": "not a list",  # Should be list
            "cached_at": "2025-09-23T10:00:00+00:00",
            "cache_version": "1.0"
        }
        
        result = validate_cached_domain_events(cached_data)
        
        assert result is False
    
    def test_validate_cached_domain_events_missing_cache_metadata(self):
        """Test validation with missing cache metadata."""
        cached_data = {
            "groups": [],
            "ungrouped_events": []
            # Missing cached_at and cache_version
        }
        
        result = validate_cached_domain_events(cached_data)
        
        assert result is False
    
    def test_validate_cached_domain_events_exception_handling(self):
        """Test validation with data that causes exceptions."""
        # None should cause exception in key access
        result = validate_cached_domain_events(None)
        
        assert result is False


@pytest.mark.unit
class TestCacheStatistics:
    """Test cache statistics extraction."""
    
    def test_extract_cache_statistics_basic(self):
        """Test extracting statistics from cached data."""
        cached_data = {
            "groups": [
                {
                    "id": 1,
                    "name": "Group 1",
                    "recurring_events": [
                        {"title": "Event 1", "event_count": 3},
                        {"title": "Event 2", "event_count": 2}
                    ]
                },
                {
                    "id": 2,
                    "name": "Group 2", 
                    "recurring_events": [
                        {"title": "Event 3", "event_count": 1}
                    ]
                }
            ],
            "ungrouped_events": [
                {"title": "Event 4", "event_count": 4},
                {"title": "Event 5", "event_count": 1}
            ],
            "cached_at": "2025-09-23T10:00:00+00:00",
            "cache_version": "1.0"
        }
        
        result = extract_cache_statistics(cached_data)
        
        assert result["total_groups"] == 2
        assert result["total_ungrouped_events"] == 2
        assert result["total_events"] == 11  # 3+2+1+4+1
        assert result["cached_at"] == "2025-09-23T10:00:00+00:00"
        assert result["cache_version"] == "1.0"
    
    def test_extract_cache_statistics_empty_data(self):
        """Test extracting statistics from empty cached data."""
        cached_data = {
            "groups": [],
            "ungrouped_events": [],
            "cached_at": "2025-09-23T10:00:00+00:00",
            "cache_version": "1.0"
        }
        
        result = extract_cache_statistics(cached_data)
        
        assert result["total_groups"] == 0
        assert result["total_ungrouped_events"] == 0
        assert result["total_events"] == 0
        assert result["cached_at"] == "2025-09-23T10:00:00+00:00"
        assert result["cache_version"] == "1.0"
    
    def test_extract_cache_statistics_missing_fields(self):
        """Test extracting statistics with missing fields."""
        cached_data = {
            "groups": [{"id": 1, "name": "Group", "recurring_events": []}]
            # Missing ungrouped_events, cached_at, cache_version
        }
        
        result = extract_cache_statistics(cached_data)
        
        assert result["total_groups"] == 1
        assert result["total_ungrouped_events"] == 0  # Default for missing field
        assert result["total_events"] == 0
        assert result["cached_at"] is None
        assert result["cache_version"] == "unknown"
    
    def test_extract_cache_statistics_missing_event_counts(self):
        """Test extracting statistics with missing event_count fields."""
        cached_data = {
            "groups": [
                {
                    "id": 1,
                    "name": "Group",
                    "recurring_events": [
                        {"title": "Event 1"},  # Missing event_count
                        {"title": "Event 2", "event_count": 5}
                    ]
                }
            ],
            "ungrouped_events": [
                {"title": "Event 3"}  # Missing event_count
            ],
            "cached_at": "2025-09-23T10:00:00+00:00",
            "cache_version": "1.0"
        }
        
        result = extract_cache_statistics(cached_data)
        
        assert result["total_events"] == 5  # Only counts where event_count exists
    
    def test_extract_cache_statistics_no_recurring_events(self):
        """Test statistics with groups that have no recurring_events."""
        cached_data = {
            "groups": [
                {"id": 1, "name": "Empty Group"}  # Missing recurring_events
            ],
            "ungrouped_events": [
                {"title": "Event", "event_count": 2}
            ],
            "cached_at": "2025-09-23T10:00:00+00:00",
            "cache_version": "1.0"
        }
        
        result = extract_cache_statistics(cached_data)
        
        assert result["total_groups"] == 1
        assert result["total_events"] == 2  # Only from ungrouped events