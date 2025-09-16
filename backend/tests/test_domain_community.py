"""
Unit Tests for Community Domain Logic - Pure Functions
Rich Hickey: "Test pure functions without mocking"
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from app.data.schemas import AppState, CommunityData, GroupData
from app.domain.community import (
    create_community, update_community_calendar_url, find_community_by_path,
    get_community_groups, validate_community_data, add_default_groups_to_community
)


@pytest.mark.unit
class TestCommunityCreation:
    """Test pure community creation functions"""
    
    def test_create_community_success(self):
        """Test successful community creation"""
        # Given: Empty state
        empty_state = AppState(
            calendars={}, communities={}, groups={}, 
            filters={}, subscriptions={}, events_cache={}
        )
        
        # When: Creating a community
        with patch('app.domain.community.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = "2024-09-16T05:00:00Z"
            
            result = create_community(
                state=empty_state,
                name="BCC Community Calendar",
                description="Community calendar for BCC events",
                url_path="/exter",
                password_hash="hashed_password",
                calendar_url="https://widgets.bcc.no/ical-xyz/Portal-Calendar.ics",
                admin_emails=["admin@example.com"]
            )
        
        # Then: Community created successfully
        assert result.success is True
        assert result.error_message is None
        assert len(result.events) == 1
        assert result.events[0] == "community_created:exter"
        
        # Verify community data
        assert "exter" in result.new_state.communities
        community = result.new_state.communities["exter"]
        assert community.id == "exter"
        assert community.name == "BCC Community Calendar"
        assert community.url_path == "/exter"
        assert community.calendar_url == "https://widgets.bcc.no/ical-xyz/Portal-Calendar.ics"
        assert community.admin_emails == ["admin@example.com"]
        assert community.is_active is True
        
        # Verify state version incremented
        assert result.new_state.version == 1
    
    def test_create_community_duplicate_id(self):
        """Test creating community with existing ID fails"""
        # Given: State with existing community
        existing_community = CommunityData(
            id="exter", name="Existing", description="Test", url_path="/exter",
            password_hash="hash", calendar_url="http://example.com",
            admin_emails=[], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        state_with_community = AppState(
            calendars={}, communities={"exter": existing_community}, groups={},
            filters={}, subscriptions={}, events_cache={}, version=1
        )
        
        # When: Trying to create duplicate community
        result = create_community(
            state=state_with_community,
            name="New Community",
            description="Should fail",
            url_path="/exter",
            password_hash="password",
            calendar_url="http://example.com",
            admin_emails=[]
        )
        
        # Then: Creation fails
        assert result.success is False
        assert "already exists" in result.error_message
        assert result.new_state == state_with_community  # State unchanged
        assert result.events == []


@pytest.mark.unit
class TestCommunityValidation:
    """Test pure validation functions"""
    
    def test_validate_community_data_success(self):
        """Test valid community data passes validation"""
        is_valid, error = validate_community_data(
            name="BCC Community",
            description="Test description",
            url_path="/exter",
            calendar_url="https://widgets.bcc.no/ical.ics"
        )
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_community_data_empty_name(self):
        """Test empty name fails validation"""
        is_valid, error = validate_community_data(
            name="",
            description="Test",
            url_path="/exter",
            calendar_url="https://example.com/cal.ics"
        )
        
        assert is_valid is False
        assert "name is required" in error
    
    def test_validate_community_data_invalid_url_path(self):
        """Test invalid URL path fails validation"""
        is_valid, error = validate_community_data(
            name="Test Community",
            description="Test",
            url_path="exter",  # Missing leading slash
            calendar_url="https://example.com/cal.ics"
        )
        
        assert is_valid is False
        assert "must start with /" in error
    
    def test_validate_community_data_invalid_calendar_url(self):
        """Test invalid calendar URL fails validation"""
        is_valid, error = validate_community_data(
            name="Test Community",
            description="Test",
            url_path="/exter",
            calendar_url="not-a-url"
        )
        
        assert is_valid is False
        assert "valid HTTP URL" in error


@pytest.mark.unit
class TestCommunityUpdates:
    """Test pure community update functions"""
    
    def test_update_calendar_url_success(self):
        """Test successful calendar URL update"""
        # Given: State with existing community
        existing_community = CommunityData(
            id="exter", name="BCC Community", description="Test", url_path="/exter",
            password_hash="hash", calendar_url="https://old-url.com/cal.ics",
            admin_emails=["admin@example.com"], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        state = AppState(
            calendars={}, communities={"exter": existing_community}, groups={},
            filters={}, subscriptions={}, events_cache={}, version=1
        )
        
        # When: Updating calendar URL
        with patch('app.domain.community.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = "2024-09-16T05:30:00Z"
            
            result = update_community_calendar_url(
                state=state,
                community_id="exter", 
                new_calendar_url="https://widgets.bcc.no/ical-new/Portal-Calendar.ics"
            )
        
        # Then: URL updated successfully
        assert result.success is True
        assert result.events == ["community_calendar_updated:exter"]
        
        # Verify updated community
        updated_community = result.new_state.communities["exter"]
        assert updated_community.calendar_url == "https://widgets.bcc.no/ical-new/Portal-Calendar.ics"
        assert updated_community.updated_at == "2024-09-16T05:30:00Z"
        
        # Verify other fields unchanged
        assert updated_community.name == "BCC Community"
        assert updated_community.created_at == "2024-09-16T04:00:00Z"
        
        # Verify state version incremented
        assert result.new_state.version == 2
    
    def test_update_calendar_url_community_not_found(self):
        """Test updating non-existent community fails"""
        empty_state = AppState(
            calendars={}, communities={}, groups={}, 
            filters={}, subscriptions={}, events_cache={}
        )
        
        result = update_community_calendar_url(
            state=empty_state,
            community_id="nonexistent",
            new_calendar_url="https://example.com/cal.ics"
        )
        
        assert result.success is False
        assert "not found" in result.error_message
        assert result.new_state == empty_state


@pytest.mark.unit
class TestCommunityQueries:
    """Test pure query functions"""
    
    def test_find_community_by_path_success(self):
        """Test successful community lookup by path"""
        # Given: State with community
        community = CommunityData(
            id="exter", name="BCC Community", description="Test", url_path="/exter",
            password_hash="hash", calendar_url="https://example.com/cal.ics",
            admin_emails=[], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        state = AppState(
            calendars={}, communities={"exter": community}, groups={},
            filters={}, subscriptions={}, events_cache={}
        )
        
        # When: Finding community by path
        result = find_community_by_path(state, "/exter")
        
        # Then: Community found
        assert result.success is True
        assert result.data == community
        assert result.error_message is None
    
    def test_find_community_by_path_not_found(self):
        """Test community lookup fails for non-existent path"""
        empty_state = AppState(
            calendars={}, communities={}, groups={}, 
            filters={}, subscriptions={}, events_cache={}
        )
        
        result = find_community_by_path(empty_state, "/nonexistent")
        
        assert result.success is False
        assert result.data is None
        assert "not found" in result.error_message
    
    def test_get_community_groups_success(self):
        """Test getting community groups"""
        # Given: State with community and groups
        community = CommunityData(
            id="exter", name="BCC Community", description="Test", url_path="/exter",
            password_hash="hash", calendar_url="https://example.com/cal.ics",
            admin_emails=[], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        
        group1 = GroupData(
            id="football", community_id="exter", name="Football", description="Football events",
            icon="⚽", color="#22C55E", assignment_rules=["football", "soccer"],
            is_active=True, created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        
        group2 = GroupData(
            id="youth", community_id="exter", name="Youth", description="Youth events",
            icon="👨‍👩‍👧‍👦", color="#3B82F6", assignment_rules=["youth", "children"],
            is_active=True, created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        
        # Group from different community (should be excluded)
        other_group = GroupData(
            id="other", community_id="other_community", name="Other", description="Other",
            icon="🔧", color="#EF4444", assignment_rules=[], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        
        state = AppState(
            calendars={}, communities={"exter": community}, 
            groups={"football": group1, "youth": group2, "other": other_group},
            filters={}, subscriptions={}, events_cache={}
        )
        
        # When: Getting community groups
        result = get_community_groups(state, "exter")
        
        # Then: Only exter community groups returned
        assert result.success is True
        assert len(result.data) == 2
        group_ids = [group.id for group in result.data]
        assert "football" in group_ids
        assert "youth" in group_ids
        assert "other" not in group_ids
    
    def test_get_community_groups_community_not_found(self):
        """Test getting groups for non-existent community"""
        empty_state = AppState(
            calendars={}, communities={}, groups={}, 
            filters={}, subscriptions={}, events_cache={}
        )
        
        result = get_community_groups(empty_state, "nonexistent")
        
        assert result.success is False
        assert "not found" in result.error_message


@pytest.mark.unit
class TestGroupAddition:
    """Test adding default groups to community"""
    
    def test_add_default_groups_success(self):
        """Test successfully adding default groups"""
        # Given: State with community
        community = CommunityData(
            id="exter", name="BCC Community", description="Test", url_path="/exter",
            password_hash="hash", calendar_url="https://example.com/cal.ics",
            admin_emails=[], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        state = AppState(
            calendars={}, communities={"exter": community}, groups={},
            filters={}, subscriptions={}, events_cache={}, version=1
        )
        
        # Default groups to add
        default_groups = [
            {
                "id": "football",
                "name": "Football",
                "description": "All football-related events",
                "icon": "⚽",
                "color": "#22C55E",
                "assignment_rules": ["football", "soccer", "match"],
                "is_active": True,
                "created_at": "2024-09-16T04:00:00Z",
                "updated_at": "2024-09-16T04:00:00Z"
            }
        ]
        
        # When: Adding default groups
        result = add_default_groups_to_community(state, "exter", default_groups)
        
        # Then: Groups added successfully
        assert result.success is True
        assert result.events == ["group_created:football"]
        
        # Verify group added to state
        assert "football" in result.new_state.groups
        football_group = result.new_state.groups["football"]
        assert football_group.community_id == "exter"
        assert football_group.name == "Football"
        assert football_group.assignment_rules == ["football", "soccer", "match"]
        
        # Verify state version incremented
        assert result.new_state.version == 2
    
    def test_add_groups_community_not_found(self):
        """Test adding groups to non-existent community fails"""
        empty_state = AppState(
            calendars={}, communities={}, groups={}, 
            filters={}, subscriptions={}, events_cache={}
        )
        
        result = add_default_groups_to_community(empty_state, "nonexistent", [])
        
        assert result.success is False
        assert "not found" in result.error_message
        assert result.new_state == empty_state