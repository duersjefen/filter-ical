"""
Tests for Pure Filtering Functions
Demonstrates Rich Hickey's functional principles in testing
NO MOCKING REQUIRED - Pure functions = predictable testing
"""

import pytest
from datetime import datetime, timedelta
from app.data.filtering import (
    # Validation functions
    validate_filter_config,
    normalize_filter_config,
    # Individual filter functions
    filter_by_categories,
    filter_by_keywords,
    filter_by_date_range,
    filter_by_duration,
    filter_by_location,
    filter_by_attendee,
    # Composite functions
    apply_filter_config,
    create_filter_pipeline,
    # Helper functions
    extract_category_from_event,
    extract_categories_from_raw_ical,
    parse_event_datetime,
    calculate_event_duration_minutes,
    create_filter_config_hash,
    filter_stats_summary
)
from app.models import FilterConfig, Event


# === TEST DATA FIXTURES ===

@pytest.fixture
def sample_events():
    """Sample events for testing"""
    return [
        Event(
            uid="event1",
            summary="Team Meeting",
            dtstart="2024-01-15T09:00:00",
            dtend="2024-01-15T10:00:00",
            location="Conference Room A",
            description="Weekly team sync",
            raw="BEGIN:VEVENT\nUID:event1\nSUMMARY:Team Meeting\nCATEGORIES:Meeting\nEND:VEVENT"
        ),
        Event(
            uid="event2", 
            summary="Lunch with Client",
            dtstart="2024-01-15T12:00:00",
            dtend="2024-01-15T13:30:00",
            location="Downtown Restaurant",
            description="Client relationship meeting",
            raw="BEGIN:VEVENT\nUID:event2\nSUMMARY:Lunch with Client\nCATEGORIES:Social,Business\nEND:VEVENT"
        ),
        Event(
            uid="event3",
            summary="Code Review",
            dtstart="2024-01-16T14:00:00", 
            dtend="2024-01-16T15:00:00",
            location="Online",
            description="Review pull requests",
            raw="BEGIN:VEVENT\nUID:event3\nSUMMARY:Code Review\nCATEGORIES:Development\nEND:VEVENT"
        ),
        Event(
            uid="event4",
            summary="Personal Dentist Appointment",
            dtstart="2024-01-17T16:00:00",
            dtend="2024-01-17T17:00:00", 
            location="Medical Center",
            description="Regular checkup",
            raw="BEGIN:VEVENT\nUID:event4\nSUMMARY:Personal Dentist Appointment\nCATEGORIES:Personal\nEND:VEVENT"
        )
    ]


@pytest.fixture
def sample_filter_config():
    """Sample filter configuration"""
    return FilterConfig(
        id="filter1",
        name="Work Events Only",
        user_id="user123",
        include_categories=["Meeting", "Development"],
        exclude_categories=["Personal"],
        include_keywords=["team", "code"],
        exclude_keywords=["dentist"],
        date_range_start="2024-01-15T00:00:00",
        date_range_end="2024-01-16T23:59:59",
        date_range_type="absolute",
        location_filter=None,
        attendee_filter=None,
        organizer_filter=None,
        min_duration_minutes=30,
        max_duration_minutes=120,
        filter_mode="include",
        match_all=False,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00"
    )


# === VALIDATION TESTS (Pure Functions) ===

class TestFilterValidation:
    
    def test_validate_valid_filter_config(self, sample_filter_config):
        """Test validation of correct filter configuration"""
        is_valid, errors = validate_filter_config(sample_filter_config)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_filter_config_missing_name(self, sample_filter_config):
        """Test validation fails for missing name"""
        invalid_config = FilterConfig(
            **{**sample_filter_config.__dict__, 'name': ''}
        )
        
        is_valid, errors = validate_filter_config(invalid_config)
        
        assert is_valid is False
        assert "Filter name is required" in errors
    
    def test_validate_filter_config_invalid_dates(self, sample_filter_config):
        """Test validation fails for invalid date range"""
        invalid_config = FilterConfig(
            **{**sample_filter_config.__dict__, 
               'date_range_start': '2024-01-20T00:00:00',
               'date_range_end': '2024-01-15T00:00:00'}  # End before start
        )
        
        is_valid, errors = validate_filter_config(invalid_config)
        
        assert is_valid is False
        assert "Start date must be before end date" in errors
    
    def test_normalize_filter_config(self, sample_filter_config):
        """Test filter config normalization"""
        unnormalized_config = FilterConfig(
            **{**sample_filter_config.__dict__,
               'name': '  Work Events  ',
               'include_keywords': ['  TEAM  ', 'code', '', '  review  '],
               'exclude_keywords': ['', '  PERSONAL  ']}
        )
        
        normalized = normalize_filter_config(unnormalized_config)
        
        assert normalized.name == "Work Events"
        assert normalized.include_keywords == ["team", "code", "review"]
        assert normalized.exclude_keywords == ["personal"]


# === INDIVIDUAL FILTER TESTS (Pure Functions) ===

class TestCategoryFiltering:
    
    def test_filter_by_categories_include(self, sample_events):
        """Test including specific categories"""
        filtered = filter_by_categories(sample_events, ["Meeting"], [])
        
        assert len(filtered) == 1
        assert filtered[0].summary == "Team Meeting"
    
    def test_filter_by_categories_exclude(self, sample_events):
        """Test excluding specific categories"""
        filtered = filter_by_categories(sample_events, [], ["Personal"])
        
        # Should exclude personal events
        assert len(filtered) == 3
        assert not any("Personal" in event.summary for event in filtered)
    
    def test_filter_by_categories_include_and_exclude(self, sample_events):
        """Test both include and exclude filters"""
        filtered = filter_by_categories(
            sample_events, 
            ["Meeting", "Social", "Development"], 
            ["Personal"]
        )
        
        # Should include Meeting/Social/Development but exclude Personal
        assert len(filtered) == 3
        summaries = [event.summary for event in filtered]
        assert "Personal Dentist Appointment" not in summaries
    
    def test_filter_by_categories_no_filters(self, sample_events):
        """Test with no category filters returns all events"""
        filtered = filter_by_categories(sample_events, [], [])
        
        assert len(filtered) == len(sample_events)
        assert filtered == sample_events  # Should be same list


class TestKeywordFiltering:
    
    def test_filter_by_keywords_include(self, sample_events):
        """Test including events with specific keywords"""
        filtered = filter_by_keywords(sample_events, ["team", "client"], [], False)
        
        assert len(filtered) == 2
        summaries = [event.summary.lower() for event in filtered]
        assert any("team" in s for s in summaries)
        assert any("client" in s for s in summaries)
    
    def test_filter_by_keywords_exclude(self, sample_events):
        """Test excluding events with specific keywords"""
        filtered = filter_by_keywords(sample_events, [], ["personal"], False)
        
        # Should exclude events with "personal" in summary/description
        assert len(filtered) == 3
        assert not any("personal" in event.summary.lower() for event in filtered)
    
    def test_filter_by_keywords_match_all_true(self, sample_events):
        """Test match_all=True requires all keywords"""
        # Only "Lunch with Client" has both "client" and "meeting" context
        filtered = filter_by_keywords(
            sample_events, 
            ["client", "relationship"], 
            [], 
            match_all=True
        )
        
        assert len(filtered) == 1
        assert filtered[0].summary == "Lunch with Client"
    
    def test_filter_by_keywords_match_all_false(self, sample_events):
        """Test match_all=False requires any keyword"""
        filtered = filter_by_keywords(
            sample_events, 
            ["team", "client"], 
            [], 
            match_all=False
        )
        
        # Should find events with either "team" OR "client"
        assert len(filtered) == 2
    
    def test_filter_by_keywords_searches_description(self, sample_events):
        """Test keyword filtering searches in description"""
        filtered = filter_by_keywords(sample_events, ["sync"], [], False)
        
        # Should find "Team Meeting" which has "sync" in description
        assert len(filtered) == 1
        assert filtered[0].summary == "Team Meeting"


class TestDateFiltering:
    
    def test_filter_by_date_range_absolute(self, sample_events):
        """Test absolute date range filtering"""
        # Filter for Jan 15 only
        filtered = filter_by_date_range(
            sample_events,
            "2024-01-15T00:00:00",
            "2024-01-15T23:59:59",
            "absolute"
        )
        
        assert len(filtered) == 2  # Team Meeting and Lunch events
        dates = [event.dtstart[:10] for event in filtered]
        assert all(date == "2024-01-15" for date in dates)
    
    def test_filter_by_date_range_start_only(self, sample_events):
        """Test filtering with only start date"""
        filtered = filter_by_date_range(
            sample_events,
            "2024-01-16T00:00:00",
            None,
            "absolute"
        )
        
        # Should include events on/after Jan 16
        assert len(filtered) == 2  # Code Review and Dentist
        dates = [event.dtstart[:10] for event in filtered]
        assert all(date >= "2024-01-16" for date in dates)
    
    def test_filter_by_date_range_end_only(self, sample_events):
        """Test filtering with only end date"""
        filtered = filter_by_date_range(
            sample_events,
            None,
            "2024-01-16T23:59:59",  # End of Jan 16
            "absolute"
        )
        
        # Should include events before/on Jan 16
        assert len(filtered) == 3  # All except Dentist (Jan 17)
    
    def test_filter_by_date_range_no_dates(self, sample_events):
        """Test no date filtering returns all events"""
        filtered = filter_by_date_range(sample_events, None, None, "absolute")
        
        assert len(filtered) == len(sample_events)
        assert filtered == sample_events


class TestDurationFiltering:
    
    def test_filter_by_duration_range(self, sample_events):
        """Test filtering by duration range"""
        # Filter for events 60-90 minutes
        filtered = filter_by_duration(sample_events, 60, 90)
        
        # Team Meeting (60 min), Lunch (90 min), Code Review (60 min), Dentist (60 min)
        assert len(filtered) == 4
    
    def test_filter_by_duration_min_only(self, sample_events):
        """Test filtering with minimum duration only"""
        filtered = filter_by_duration(sample_events, 90, None)
        
        # Only Lunch with Client is 90+ minutes
        assert len(filtered) == 1
        assert filtered[0].summary == "Lunch with Client"
    
    def test_filter_by_duration_max_only(self, sample_events):
        """Test filtering with maximum duration only"""
        filtered = filter_by_duration(sample_events, None, 60)
        
        # All events are 60 minutes or less except Lunch
        assert len(filtered) == 3
        summaries = [event.summary for event in filtered]
        assert "Lunch with Client" not in summaries


class TestLocationFiltering:
    
    def test_filter_by_location_exact_match(self, sample_events):
        """Test exact location matching"""
        filtered = filter_by_location(sample_events, "Online")
        
        assert len(filtered) == 1
        assert filtered[0].summary == "Code Review"
    
    def test_filter_by_location_regex_pattern(self, sample_events):
        """Test regex pattern location filtering"""
        # Find events in rooms (Conference Room, Restaurant, etc.)
        filtered = filter_by_location(sample_events, r".*Room.*")
        
        assert len(filtered) == 1
        assert filtered[0].location == "Conference Room A"
    
    def test_filter_by_location_case_insensitive(self, sample_events):
        """Test case insensitive location filtering"""
        filtered = filter_by_location(sample_events, "conference")
        
        assert len(filtered) == 1
        assert "Conference Room" in filtered[0].location


# === COMPOSITE FILTER TESTS (Pure Functions) ===

class TestCompositeFiltering:
    
    def test_apply_filter_config_complete(self, sample_events, sample_filter_config):
        """Test applying complete filter configuration"""
        filtered = apply_filter_config(sample_events, sample_filter_config)
        
        # Should match work-related events within date range
        assert len(filtered) >= 1
        # Verify no personal events
        assert not any("Personal" in event.summary for event in filtered)
    
    def test_create_filter_pipeline(self, sample_events):
        """Test creating and using filter pipeline"""
        config1 = FilterConfig(
            id="f1", name="Step 1", user_id="user", 
            include_categories=["Meeting", "Development", "Social"], exclude_categories=[],
            include_keywords=[], exclude_keywords=[],
            date_range_start=None, date_range_end=None, date_range_type="absolute",
            location_filter=None, attendee_filter=None, organizer_filter=None,
            min_duration_minutes=None, max_duration_minutes=None,
            filter_mode="include", match_all=False,
            created_at="2024-01-01T00:00:00", updated_at="2024-01-01T00:00:00"
        )
        
        config2 = FilterConfig(
            id="f2", name="Step 2", user_id="user",
            include_categories=[], exclude_categories=["Personal"],
            include_keywords=[], exclude_keywords=[],
            date_range_start=None, date_range_end=None, date_range_type="absolute",
            location_filter=None, attendee_filter=None, organizer_filter=None,
            min_duration_minutes=None, max_duration_minutes=None,
            filter_mode="exclude", match_all=False,
            created_at="2024-01-01T00:00:00", updated_at="2024-01-01T00:00:00"
        )
        
        pipeline = create_filter_pipeline([config1, config2])
        filtered = pipeline(sample_events)
        
        # Should apply both filters in sequence
        assert len(filtered) == 3  # Exclude personal events
        assert not any("Personal" in event.summary for event in filtered)


# === HELPER FUNCTION TESTS (Pure Functions) ===

class TestHelperFunctions:
    
    def test_extract_category_from_event(self, sample_events):
        """Test category extraction from event"""
        # Test with raw iCal data
        meeting_event = sample_events[0]
        category = extract_category_from_event(meeting_event)
        assert category == "Meeting"
        
        # Test with summary-based detection
        event_without_category = Event(
            uid="test", summary="Training Session", dtstart="", dtend="",
            location=None, description=None, raw=""
        )
        category = extract_category_from_event(event_without_category)
        assert category == "Learning"
    
    def test_extract_categories_from_raw_ical(self):
        """Test extracting categories from raw iCal"""
        raw_ical = """BEGIN:VEVENT
UID:test@example.com
SUMMARY:Test Event
CATEGORIES:Meeting,Important
DTSTART:20240115T090000Z
END:VEVENT"""
        
        categories = extract_categories_from_raw_ical(raw_ical)
        assert categories == ["Meeting", "Important"]
    
    def test_parse_event_datetime(self):
        """Test parsing various datetime formats"""
        # ISO format
        dt1 = parse_event_datetime("2024-01-15T09:00:00")
        assert dt1 == datetime(2024, 1, 15, 9, 0, 0)
        
        # UTC format
        dt2 = parse_event_datetime("2024-01-15T09:00:00Z")
        assert dt2.year == 2024
        assert dt2.month == 1
        assert dt2.day == 15
        
        # Date only
        dt3 = parse_event_datetime("2024-01-15")
        assert dt3 == datetime(2024, 1, 15, 0, 0, 0)
        
        # Invalid format
        dt4 = parse_event_datetime("invalid-date")
        assert dt4 is None
    
    def test_calculate_event_duration_minutes(self):
        """Test duration calculation"""
        event = Event(
            uid="test",
            summary="Test Event",
            dtstart="2024-01-15T09:00:00",
            dtend="2024-01-15T10:30:00",
            location=None,
            description=None,
            raw=""
        )
        
        duration = calculate_event_duration_minutes(event)
        assert duration == 90  # 1.5 hours = 90 minutes
    
    def test_create_filter_config_hash(self, sample_filter_config):
        """Test filter config hash generation"""
        hash1 = create_filter_config_hash(sample_filter_config)
        
        # Same config should produce same hash
        hash2 = create_filter_config_hash(sample_filter_config)
        assert hash1 == hash2
        
        # Different config should produce different hash
        modified_config = FilterConfig(
            **{**sample_filter_config.__dict__, 'include_categories': ['Different']}
        )
        hash3 = create_filter_config_hash(modified_config)
        assert hash1 != hash3
    
    def test_filter_stats_summary(self, sample_events, sample_filter_config):
        """Test filtering statistics generation"""
        filtered_events = apply_filter_config(sample_events, sample_filter_config)
        stats = filter_stats_summary(sample_events, filtered_events, sample_filter_config)
        
        assert stats['original_event_count'] == len(sample_events)
        assert stats['filtered_event_count'] == len(filtered_events)
        assert stats['events_removed'] == len(sample_events) - len(filtered_events)
        assert 0 <= stats['reduction_percent'] <= 100
        assert stats['filter_name'] == sample_filter_config.name
        assert isinstance(stats['active_filters'], dict)


# === EDGE CASE TESTS (Pure Functions) ===

class TestEdgeCases:
    
    def test_empty_events_list(self, sample_filter_config):
        """Test filtering empty events list"""
        filtered = apply_filter_config([], sample_filter_config)
        assert filtered == []
    
    def test_events_with_missing_fields(self):
        """Test filtering events with missing fields"""
        incomplete_events = [
            Event(uid="1", summary="", dtstart="", dtend="", location=None, description=None, raw=""),
            Event(uid="2", summary="Test", dtstart="invalid-date", dtend="", location="", description="", raw="")
        ]
        
        # Should not crash, should handle gracefully
        filtered = filter_by_date_range(incomplete_events, "2024-01-01T00:00:00", "2024-01-31T00:00:00", "absolute")
        assert isinstance(filtered, list)
    
    def test_filter_config_with_empty_values(self):
        """Test filter config with empty/None values"""
        minimal_config = FilterConfig(
            id="minimal", name="Minimal Filter", user_id="user",
            include_categories=[], exclude_categories=[],
            include_keywords=[], exclude_keywords=[],
            date_range_start=None, date_range_end=None, date_range_type="absolute",
            location_filter=None, attendee_filter=None, organizer_filter=None,
            min_duration_minutes=None, max_duration_minutes=None,
            filter_mode="include", match_all=False,
            created_at="2024-01-01T00:00:00", updated_at="2024-01-01T00:00:00"
        )
        
        # Should validate successfully
        is_valid, errors = validate_filter_config(minimal_config)
        assert is_valid is True
        assert len(errors) == 0


# === PERFORMANCE TESTS (Pure Functions) ===

class TestPerformance:
    
    def test_large_event_list_performance(self):
        """Test filtering performance with large event list"""
        # Create 1000 test events
        large_event_list = []
        for i in range(1000):
            event = Event(
                uid=f"event{i}",
                summary=f"Event {i}" + (" Meeting" if i % 3 == 0 else " Task"),
                dtstart=f"2024-01-{(i % 28) + 1:02d}T09:00:00",
                dtend=f"2024-01-{(i % 28) + 1:02d}T10:00:00",
                location="Office" if i % 2 == 0 else "Remote",
                description=f"Description {i}",
                raw=f"BEGIN:VEVENT\nUID:event{i}\nCATEGORIES:{'Meeting' if i % 3 == 0 else 'Task'}\nEND:VEVENT"
            )
            large_event_list.append(event)
        
        # Test performance of filtering (should complete quickly)
        import time
        start_time = time.time()
        
        filtered = filter_by_keywords(large_event_list, ["Meeting"], [], False)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (< 1 second)
        assert duration < 1.0
        # Should filter correctly
        assert len(filtered) == 334  # Approximately 1000/3 events with "Meeting"
    
    def test_complex_filter_chain_performance(self, sample_events):
        """Test performance of complex filter chains"""
        # Create multiple filter configs
        configs = []
        for i in range(10):
            config = FilterConfig(
                id=f"filter{i}", name=f"Filter {i}", user_id="user",
                include_categories=["Meeting"] if i % 2 == 0 else ["Development"],
                exclude_categories=[],
                include_keywords=[],
                exclude_keywords=[],
                date_range_start=None, date_range_end=None, date_range_type="absolute",
                location_filter=None, attendee_filter=None, organizer_filter=None,
                min_duration_minutes=None, max_duration_minutes=None,
                filter_mode="include", match_all=False,
                created_at="2024-01-01T00:00:00", updated_at="2024-01-01T00:00:00"
            )
            configs.append(config)
        
        # Create and test pipeline
        pipeline = create_filter_pipeline(configs)
        
        import time
        start_time = time.time()
        
        filtered = pipeline(sample_events)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly even with complex pipeline
        assert duration < 0.1  # < 100ms
        assert isinstance(filtered, list)


"""
WHAT THESE TESTS DEMONSTRATE ABOUT FUNCTIONAL PROGRAMMING:

1. NO MOCKING REQUIRED
   - All functions are pure, so no external dependencies to mock
   - Tests run in complete isolation
   - No setup/teardown complexity

2. PREDICTABLE BEHAVIOR  
   - Same input always produces same output
   - No hidden state to worry about
   - Tests are deterministic

3. EASY TO DEBUG
   - Test failures point directly to the problematic transformation
   - No complex object state to understand
   - Clear input/output relationships

4. COMPREHENSIVE COVERAGE
   - Can test all edge cases easily
   - Performance tests are straightforward
   - Composability tests verify function combinations work

5. FAST EXECUTION
   - No I/O operations or external dependencies
   - Tests run in milliseconds
   - Can run thousands of test cases quickly

This is the power of Rich Hickey's functional programming approach:
Complex business logic becomes simple, testable, composable functions.
"""