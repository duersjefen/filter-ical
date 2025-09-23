"""
Unit tests for grouping functions.

Tests pure functions from app.data.grouping module.
Critical for domain organization and event grouping logic.
"""

import pytest
import yaml
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.data.grouping import (
    load_domain_config,
    get_domain_config,
    create_group_data,
    create_recurring_event_group_data,
    create_assignment_rule_data,
    apply_assignment_rules,
    build_domain_events_response,
    validate_group_data,
    validate_assignment_rule_data,
    _extract_categories_from_raw_ical,
    _event_matches_rule
)


@pytest.mark.unit
class TestDomainConfiguration:
    """Test domain configuration functions."""
    
    def test_load_domain_config_valid(self):
        """Test loading valid domain configuration."""
        yaml_content = """
domains:
  test_domain:
    name: "Test Domain"
    description: "Test domain for testing"
  another_domain:
    name: "Another Domain"
"""
        
        success, config, error = load_domain_config(yaml_content)
        
        assert success is True
        assert error == ""
        assert "domains" in config
        assert "test_domain" in config["domains"]
        assert config["domains"]["test_domain"]["name"] == "Test Domain"
    
    def test_load_domain_config_invalid_yaml(self):
        """Test loading invalid YAML content."""
        invalid_yaml = """
domains:
  test_domain:
    name: "Test Domain"
    invalid: [unclosed
"""
        
        success, config, error = load_domain_config(invalid_yaml)
        
        assert success is False
        assert config == {}
        assert "Failed to parse domain configuration" in error
    
    def test_load_domain_config_missing_domains_key(self):
        """Test loading YAML without domains key."""
        yaml_content = """
other_config:
  setting: value
"""
        
        success, config, error = load_domain_config(yaml_content)
        
        assert success is False
        assert config == {}
        assert "missing 'domains' key" in error
    
    def test_load_domain_config_empty(self):
        """Test loading empty YAML content."""
        success, config, error = load_domain_config("")
        
        assert success is False
        assert config == {}
        assert "missing 'domains' key" in error
    
    def test_get_domain_config_existing(self):
        """Test getting configuration for existing domain."""
        config = {
            "domains": {
                "test_domain": {
                    "name": "Test Domain",
                    "description": "Test description"
                }
            }
        }
        
        domain_config = get_domain_config("test_domain", config)
        
        assert domain_config is not None
        assert domain_config["name"] == "Test Domain"
        assert domain_config["description"] == "Test description"
        assert domain_config["id"] == "test_domain"  # Added by function
    
    def test_get_domain_config_nonexistent(self):
        """Test getting configuration for non-existent domain."""
        config = {
            "domains": {
                "other_domain": {
                    "name": "Other Domain"
                }
            }
        }
        
        domain_config = get_domain_config("nonexistent", config)
        
        assert domain_config is None
    
    def test_get_domain_config_empty_config(self):
        """Test getting domain config from empty configuration."""
        config = {}
        
        domain_config = get_domain_config("test_domain", config)
        
        assert domain_config is None


@pytest.mark.unit
class TestDataCreation:
    """Test data creation functions."""
    
    def test_create_group_data(self):
        """Test creating group data."""
        result = create_group_data("test_domain", "Test Group")
        
        assert result["domain_key"] == "test_domain"
        assert result["name"] == "Test Group"
        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["updated_at"], datetime)
        assert result["created_at"].tzinfo == timezone.utc
        assert result["updated_at"].tzinfo == timezone.utc
    
    def test_create_group_data_strips_whitespace(self):
        """Test that group name is stripped of whitespace."""
        result = create_group_data("test_domain", "  Test Group  ")
        
        assert result["name"] == "Test Group"
    
    def test_create_recurring_event_group_data(self):
        """Test creating recurring event group assignment data."""
        result = create_recurring_event_group_data("test_domain", "Weekly Meeting", 123)
        
        assert result["domain_key"] == "test_domain"
        assert result["recurring_event_title"] == "Weekly Meeting"
        assert result["group_id"] == 123
        assert isinstance(result["created_at"], datetime)
        assert result["created_at"].tzinfo == timezone.utc
    
    def test_create_recurring_event_group_data_strips_whitespace(self):
        """Test that event title is stripped of whitespace."""
        result = create_recurring_event_group_data("test_domain", "  Weekly Meeting  ", 123)
        
        assert result["recurring_event_title"] == "Weekly Meeting"
    
    def test_create_assignment_rule_data(self):
        """Test creating assignment rule data."""
        result = create_assignment_rule_data("test_domain", "title_contains", "meeting", 456)
        
        assert result["domain_key"] == "test_domain"
        assert result["rule_type"] == "title_contains"
        assert result["rule_value"] == "meeting"
        assert result["target_group_id"] == 456
        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["updated_at"], datetime)
        assert result["created_at"].tzinfo == timezone.utc
        assert result["updated_at"].tzinfo == timezone.utc
    
    def test_create_assignment_rule_data_strips_whitespace(self):
        """Test that rule value is stripped of whitespace."""
        result = create_assignment_rule_data("test_domain", "title_contains", "  meeting  ", 456)
        
        assert result["rule_value"] == "meeting"


@pytest.mark.unit
class TestAssignmentRules:
    """Test assignment rule application."""
    
    @pytest.fixture
    def sample_events(self):
        """Sample events for rule testing."""
        return [
            {
                "id": 1,
                "title": "Weekly Team Meeting",
                "description": "Regular team sync"
            },
            {
                "id": 2,
                "title": "Weekly Team Meeting",
                "description": "Regular team sync"
            },
            {
                "id": 3,
                "title": "Project Review",
                "description": "Review project progress"
            },
            {
                "id": 4,
                "title": "Daily Standup",
                "description": "Daily meeting for updates"
            }
        ]
    
    @pytest.fixture
    def assignment_rules(self):
        """Sample assignment rules."""
        return [
            {
                "rule_type": "title_contains",
                "rule_value": "meeting",
                "target_group_id": 1
            },
            {
                "rule_type": "description_contains",
                "rule_value": "project",
                "target_group_id": 2
            },
            {
                "rule_type": "title_contains",
                "rule_value": "standup",
                "target_group_id": 3
            }
        ]
    
    def test_apply_assignment_rules_basic(self, sample_events, assignment_rules):
        """Test basic assignment rule application."""
        result = apply_assignment_rules(sample_events, assignment_rules)
        
        assert len(result) == 3
        assert 1 in result  # "meeting" rule matches "Weekly Team Meeting"
        assert 2 in result  # "project" rule matches "Project Review"
        assert 3 in result  # "standup" rule matches "Daily Standup"
        
        # Check group 1 assignments
        assert "Weekly Team Meeting" in result[1]
        assert len(result[1]) == 1  # Only unique titles
        
        # Check group 2 assignments
        assert "Project Review" in result[2]
        
        # Check group 3 assignments
        assert "Daily Standup" in result[3]
    
    def test_apply_assignment_rules_case_insensitive(self):
        """Test that rule matching is case insensitive."""
        events = [
            {"id": 1, "title": "WEEKLY MEETING", "description": ""}
        ]
        rules = [
            {"rule_type": "title_contains", "rule_value": "meeting", "target_group_id": 1}
        ]
        
        result = apply_assignment_rules(events, rules)
        
        assert 1 in result
        assert "WEEKLY MEETING" in result[1]
    
    def test_apply_assignment_rules_first_match_wins(self):
        """Test that first matching rule wins."""
        events = [
            {"id": 1, "title": "Team Meeting", "description": "project discussion"}
        ]
        rules = [
            {"rule_type": "title_contains", "rule_value": "meeting", "target_group_id": 1},
            {"rule_type": "description_contains", "rule_value": "project", "target_group_id": 2}
        ]
        
        result = apply_assignment_rules(events, rules)
        
        # Should only match first rule (group 1)
        assert 1 in result
        assert 2 not in result
        assert "Team Meeting" in result[1]
    
    def test_apply_assignment_rules_no_matches(self):
        """Test assignment rules with no matches."""
        events = [
            {"id": 1, "title": "Random Event", "description": "No matches"}
        ]
        rules = [
            {"rule_type": "title_contains", "rule_value": "meeting", "target_group_id": 1}
        ]
        
        result = apply_assignment_rules(events, rules)
        
        assert result == {}
    
    def test_apply_assignment_rules_empty_events(self):
        """Test assignment rules with empty events."""
        rules = [
            {"rule_type": "title_contains", "rule_value": "meeting", "target_group_id": 1}
        ]
        
        result = apply_assignment_rules([], rules)
        
        assert result == {}
    
    def test_apply_assignment_rules_empty_rules(self, sample_events):
        """Test assignment rules with empty rules."""
        result = apply_assignment_rules(sample_events, [])
        
        assert result == {}
    
    def test_apply_assignment_rules_unknown_rule_type(self):
        """Test assignment rules with unknown rule type."""
        events = [
            {"id": 1, "title": "Test Event", "description": "Test"}
        ]
        rules = [
            {"rule_type": "unknown_type", "rule_value": "test", "target_group_id": 1}
        ]
        
        result = apply_assignment_rules(events, rules)
        
        assert result == {}


@pytest.mark.unit
class TestDomainEventsResponse:
    """Test domain events response building."""
    
    def test_build_domain_events_response_basic(self):
        """Test basic domain events response building."""
        grouped_events = {
            "Weekly Meeting": {
                "title": "Weekly Meeting",
                "event_count": 2,
                "events": [{"id": 1}, {"id": 2}]
            },
            "Daily Standup": {
                "title": "Daily Standup", 
                "event_count": 1,
                "events": [{"id": 3}]
            }
        }
        
        groups_data = [
            {"id": 1, "name": "Meetings"},
            {"id": 2, "name": "Reviews"}
        ]
        
        recurring_assignments = [
            {"group_id": 1, "recurring_event_title": "Weekly Meeting"}
        ]
        
        result = build_domain_events_response(grouped_events, groups_data, recurring_assignments)
        
        assert "groups" in result
        assert "ungrouped_events" in result
        
        # Check groups
        assert len(result["groups"]) == 1
        group = result["groups"][0]
        assert group["id"] == 1
        assert group["name"] == "Meetings"
        assert len(group["recurring_events"]) == 1
        assert group["recurring_events"][0]["title"] == "Weekly Meeting"
        
        # Check ungrouped events
        assert len(result["ungrouped_events"]) == 1
        assert result["ungrouped_events"][0]["title"] == "Daily Standup"
    
    def test_build_domain_events_response_empty_groups(self):
        """Test building response with groups that have no events."""
        grouped_events = {}
        
        groups_data = [
            {"id": 1, "name": "Empty Group"}
        ]
        
        recurring_assignments = [
            {"group_id": 1, "recurring_event_title": "Nonexistent Event"}
        ]
        
        result = build_domain_events_response(grouped_events, groups_data, recurring_assignments)
        
        # Empty groups should not be included
        assert len(result["groups"]) == 0
        assert len(result["ungrouped_events"]) == 0
    
    def test_build_domain_events_response_no_assignments(self):
        """Test building response with no recurring assignments."""
        grouped_events = {
            "Event": {
                "title": "Event",
                "event_count": 1,
                "events": [{"id": 1}]
            }
        }
        
        groups_data = [
            {"id": 1, "name": "Group"}
        ]
        
        recurring_assignments = []
        
        result = build_domain_events_response(grouped_events, groups_data, recurring_assignments)
        
        # No groups should have events
        assert len(result["groups"]) == 0
        # All events should be ungrouped
        assert len(result["ungrouped_events"]) == 1
        assert result["ungrouped_events"][0]["title"] == "Event"


@pytest.mark.unit
class TestValidation:
    """Test validation functions."""
    
    def test_validate_group_data_valid(self):
        """Test validating valid group data."""
        is_valid, error = validate_group_data("Test Group", "test_domain")
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_group_data_empty_name(self):
        """Test validating group data with empty name."""
        is_valid, error = validate_group_data("", "test_domain")
        
        assert is_valid is False
        assert "Group name is required" in error
    
    def test_validate_group_data_whitespace_name(self):
        """Test validating group data with whitespace-only name."""
        is_valid, error = validate_group_data("   ", "test_domain")
        
        assert is_valid is False
        assert "Group name is required" in error
    
    def test_validate_group_data_long_name(self):
        """Test validating group data with too long name."""
        long_name = "x" * 256  # Longer than 255 characters
        is_valid, error = validate_group_data(long_name, "test_domain")
        
        assert is_valid is False
        assert "255 characters or less" in error
    
    def test_validate_group_data_empty_domain_key(self):
        """Test validating group data with empty domain key."""
        is_valid, error = validate_group_data("Test Group", "")
        
        assert is_valid is False
        assert "Domain key is required" in error
    
    def test_validate_group_data_none_values(self):
        """Test validating group data with None values."""
        is_valid, error = validate_group_data(None, None)
        
        assert is_valid is False
        assert "Group name is required" in error
    
    def test_validate_assignment_rule_data_valid_title_contains(self):
        """Test validating valid title_contains rule."""
        is_valid, error = validate_assignment_rule_data("title_contains", "meeting", 1)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_assignment_rule_data_valid_description_contains(self):
        """Test validating valid description_contains rule."""
        is_valid, error = validate_assignment_rule_data("description_contains", "project", 2)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_assignment_rule_data_invalid_rule_type(self):
        """Test validating rule with invalid rule type."""
        is_valid, error = validate_assignment_rule_data("invalid_type", "test", 1)
        
        assert is_valid is False
        assert "Rule type must be one of" in error
        assert "title_contains" in error
        assert "description_contains" in error
    
    def test_validate_assignment_rule_data_empty_rule_value(self):
        """Test validating rule with empty rule value."""
        is_valid, error = validate_assignment_rule_data("title_contains", "", 1)
        
        assert is_valid is False
        assert "Rule value is required" in error
    
    def test_validate_assignment_rule_data_whitespace_rule_value(self):
        """Test validating rule with whitespace-only rule value."""
        is_valid, error = validate_assignment_rule_data("title_contains", "   ", 1)
        
        assert is_valid is False
        assert "Rule value is required" in error
    
    def test_validate_assignment_rule_data_invalid_target_group_id(self):
        """Test validating rule with invalid target group ID."""
        is_valid, error = validate_assignment_rule_data("title_contains", "test", 0)
        
        assert is_valid is False
        assert "positive integer" in error
    
    def test_validate_assignment_rule_data_negative_target_group_id(self):
        """Test validating rule with negative target group ID."""
        is_valid, error = validate_assignment_rule_data("title_contains", "test", -1)
        
        assert is_valid is False
        assert "positive integer" in error
    
    def test_validate_assignment_rule_data_string_target_group_id(self):
        """Test validating rule with string target group ID."""
        is_valid, error = validate_assignment_rule_data("title_contains", "test", "1")
        
        assert is_valid is False
        assert "positive integer" in error
    
    def test_validate_assignment_rule_data_valid_category_contains(self):
        """Test validating valid category_contains rule."""
        is_valid, error = validate_assignment_rule_data("category_contains", "Event", 1)
        
        assert is_valid is True
        assert error == ""


@pytest.mark.unit
class TestCategoryAssignmentRules:
    """Test category-based assignment rule functions."""
    
    def test_extract_categories_from_raw_ical_basic(self):
        """Test extracting categories from raw iCal content."""
        raw_ical = """BEGIN:VEVENT
DTSTART:20250101T100000Z
DTEND:20250101T110000Z
SUMMARY:Test Event
CATEGORY:Event
CATEGORY:Deutschland
DESCRIPTION:Test description
END:VEVENT"""
        
        categories = _extract_categories_from_raw_ical(raw_ical)
        
        assert len(categories) == 2
        assert "Event" in categories
        assert "Deutschland" in categories
    
    def test_extract_categories_from_raw_ical_empty(self):
        """Test extracting categories from empty raw iCal content."""
        categories = _extract_categories_from_raw_ical("")
        assert categories == []
        
        categories = _extract_categories_from_raw_ical(None)
        assert categories == []
    
    def test_extract_categories_from_raw_ical_no_categories(self):
        """Test extracting categories when no CATEGORY lines exist."""
        raw_ical = """BEGIN:VEVENT
DTSTART:20250101T100000Z
SUMMARY:Test Event
END:VEVENT"""
        
        categories = _extract_categories_from_raw_ical(raw_ical)
        assert categories == []
    
    def test_extract_categories_from_raw_ical_mixed_case(self):
        """Test extracting categories with mixed case (iCal is case-insensitive)."""
        raw_ical = """BEGIN:VEVENT
CATEGORY:Event
category:Training
CaTEGORY:Deutschland
END:VEVENT"""
        
        categories = _extract_categories_from_raw_ical(raw_ical)
        # iCal property names are case-insensitive, so all should be extracted
        assert len(categories) == 3
        assert "Event" in categories
        assert "Training" in categories
        assert "Deutschland" in categories
    
    def test_event_matches_rule_category_contains(self):
        """Test event matching with category_contains rule."""
        event = {
            "title": "Test Event",
            "description": "Test description", 
            "raw_ical": """BEGIN:VEVENT
SUMMARY:Test Event
CATEGORY:Event
CATEGORY:Training
END:VEVENT"""
        }
        
        # Test matching rule
        rule = {
            "rule_type": "category_contains",
            "rule_value": "Event",
            "target_group_id": 1
        }
        
        assert _event_matches_rule(event, rule) is True
        
        # Test non-matching rule
        rule_no_match = {
            "rule_type": "category_contains",
            "rule_value": "NonExistent",
            "target_group_id": 1
        }
        
        assert _event_matches_rule(event, rule_no_match) is False
    
    def test_event_matches_rule_category_contains_case_insensitive(self):
        """Test event matching with category_contains rule is case insensitive."""
        event = {
            "title": "Test Event",
            "raw_ical": """BEGIN:VEVENT
SUMMARY:Test Event
CATEGORY:Event
END:VEVENT"""
        }
        
        # Test case insensitive matching
        rule = {
            "rule_type": "category_contains",
            "rule_value": "event",  # lowercase
            "target_group_id": 1
        }
        
        assert _event_matches_rule(event, rule) is True
    
    def test_apply_assignment_rules_with_categories(self):
        """Test applying assignment rules with category-based rules."""
        events = [
            {
                "title": "BCC Community Event",
                "raw_ical": """BEGIN:VEVENT
SUMMARY:BCC Community Event
CATEGORY:Event
END:VEVENT"""
            },
            {
                "title": "Deutschland Training",
                "raw_ical": """BEGIN:VEVENT
SUMMARY:Deutschland Training  
CATEGORY:Deutschland
END:VEVENT"""
            },
            {
                "title": "Regular Meeting",
                "raw_ical": """BEGIN:VEVENT
SUMMARY:Regular Meeting
END:VEVENT"""
            }
        ]
        
        rules = [
            {
                "rule_type": "category_contains",
                "rule_value": "Event",
                "target_group_id": 1
            },
            {
                "rule_type": "category_contains", 
                "rule_value": "Deutschland",
                "target_group_id": 2
            }
        ]
        
        assignments = apply_assignment_rules(events, rules)
        
        assert 1 in assignments
        assert 2 in assignments
        assert "BCC Community Event" in assignments[1]
        assert "Deutschland Training" in assignments[2]
        assert len(assignments) == 2  # Only events with categories get assigned