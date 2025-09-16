"""
Integration Tests for Community Service Layer
Rich Hickey: "Test service orchestration with mock I/O"
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.services.community_service import (
    CommunityService, CommunityCreateRequest, CommunityUpdateRequest, ServiceResult
)
from app.data.schemas import AppState, CommunityData
from app.persistence.repositories import StateRepository


class TestCommunityService:
    """Test service layer orchestration"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repository = Mock(spec=StateRepository)
        self.service = CommunityService(self.mock_repository)
    
    def test_create_community_workflow_success(self):
        """Test successful community creation workflow"""
        # Given: Valid request and empty state
        request = CommunityCreateRequest(
            name="BCC Community Calendar",
            description="Community calendar for BCC events",
            url_path="/exter",
            password="bcc2024",
            calendar_url="https://widgets.bcc.no/ical-xyz/Portal-Calendar.ics",
            admin_emails=["admin@example.com"]
        )
        
        empty_state = AppState(
            calendars={}, communities={}, groups={}, 
            filters={}, subscriptions={}, events_cache={}
        )
        
        # Mock repository calls
        self.mock_repository.load_state.return_value = empty_state
        self.mock_repository.save_state.return_value = True
        
        # When: Creating community
        with patch('app.services.community_service.create_default_groups') as mock_groups:
            mock_groups.return_value = [
                {
                    "id": "football",
                    "name": "Football", 
                    "description": "Football events",
                    "icon": "⚽",
                    "color": "#22C55E",
                    "assignment_rules": ["football"],
                    "is_active": True,
                    "created_at": "2024-09-16T04:00:00Z",
                    "updated_at": "2024-09-16T04:00:00Z"
                }
            ]
            
            with patch('hashlib.sha256') as mock_hash:
                mock_hash.return_value.hexdigest.return_value = "hashed_password"
                
                result = self.service.create_community_workflow(request, "hashed_password")
        
        # Then: Community created successfully
        assert result.success is True
        assert result.data is not None
        assert result.data["community"]["id"] == "exter"
        assert result.data["community"]["name"] == "BCC Community Calendar"
        
        # Verify groups were created (count from events)
        group_events = [e for e in result.events if e.startswith("group_created")]
        assert len(group_events) == 1
        
        # Verify repository interactions
        self.mock_repository.load_state.assert_called_once()
        self.mock_repository.save_state.assert_called_once()
    
    def test_create_community_workflow_validation_error(self):
        """Test community creation with validation error"""
        # Given: Invalid request (empty name)
        request = CommunityCreateRequest(
            name="",  # Invalid empty name
            description="Test",
            url_path="/exter",
            password="password",
            calendar_url="https://example.com/cal.ics",
            admin_emails=[]
        )
        
        # When: Creating community
        result = self.service.create_community_workflow(request, "hashed_password")
        
        # Then: Validation fails
        assert result.success is False
        assert "name is required" in result.error_message
        
        # Verify no repository calls made
        self.mock_repository.load_state.assert_not_called()
        self.mock_repository.save_state.assert_not_called()
    
    def test_create_community_workflow_duplicate_community(self):
        """Test creating duplicate community fails"""
        # Given: Request for existing community
        request = CommunityCreateRequest(
            name="BCC Community",
            description="Test",
            url_path="/exter",
            password="password",
            calendar_url="https://example.com/cal.ics",
            admin_emails=[]
        )
        
        existing_community = CommunityData(
            id="exter", name="Existing", description="Test", url_path="/exter",
            password_hash="hash", calendar_url="http://example.com",
            admin_emails=[], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        
        state_with_community = AppState(
            calendars={}, communities={"exter": existing_community}, groups={},
            filters={}, subscriptions={}, events_cache={}
        )
        
        self.mock_repository.load_state.return_value = state_with_community
        
        # When: Creating duplicate community
        result = self.service.create_community_workflow(request, "hashed_password")
        
        # Then: Creation fails
        assert result.success is False
        assert "already exists" in result.error_message
        
        # Verify save not called
        self.mock_repository.save_state.assert_not_called()
    
    def test_create_community_workflow_save_failure(self):
        """Test handling save failure"""
        # Given: Valid request but save fails
        request = CommunityCreateRequest(
            name="BCC Community",
            description="Test",
            url_path="/exter",
            password="password",
            calendar_url="https://example.com/cal.ics",
            admin_emails=[]
        )
        
        empty_state = AppState(
            calendars={}, communities={}, groups={}, 
            filters={}, subscriptions={}, events_cache={}
        )
        
        self.mock_repository.load_state.return_value = empty_state
        self.mock_repository.save_state.return_value = False  # Save fails
        
        # When: Creating community
        with patch('app.services.community_service.create_default_groups') as mock_groups:
            mock_groups.return_value = []
            result = self.service.create_community_workflow(request, "hashed_password")
        
        # Then: Service reports failure
        assert result.success is False
        assert "Failed to persist" in result.error_message
    
    def test_update_calendar_url_workflow_success(self):
        """Test successful calendar URL update"""
        # Given: Existing community and update request
        existing_community = CommunityData(
            id="exter", name="BCC Community", description="Test", url_path="/exter",
            password_hash="hash", calendar_url="https://old-url.com/cal.ics",
            admin_emails=[], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        
        state = AppState(
            calendars={}, communities={"exter": existing_community}, groups={},
            filters={}, subscriptions={}, events_cache={}
        )
        
        request = CommunityUpdateRequest(
            calendar_url="https://widgets.bcc.no/ical-new/Portal-Calendar.ics"
        )
        
        self.mock_repository.load_state.return_value = state
        self.mock_repository.save_state.return_value = True
        
        # When: Updating calendar URL
        result = self.service.update_calendar_url_workflow("exter", request)
        
        # Then: Update successful
        assert result.success is True
        assert result.data["community"]["calendar_url"] == "https://widgets.bcc.no/ical-new/Portal-Calendar.ics"
        assert result.events == ["community_calendar_updated:exter"]
        
        # Verify repository interactions
        self.mock_repository.load_state.assert_called_once()
        self.mock_repository.save_state.assert_called_once()
    
    def test_get_community_by_path_workflow_success(self):
        """Test successful community retrieval"""
        # Given: Existing community
        community = CommunityData(
            id="exter", name="BCC Community", description="Test", url_path="/exter",
            password_hash="hash", calendar_url="https://example.com/cal.ics",
            admin_emails=["admin@example.com"], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        
        state = AppState(
            calendars={}, communities={"exter": community}, groups={},
            filters={}, subscriptions={}, events_cache={}
        )
        
        self.mock_repository.load_state.return_value = state
        
        # When: Getting community by path
        result = self.service.get_community_by_path_workflow("/exter")
        
        # Then: Community retrieved
        assert result.success is True
        assert result.data["community"]["id"] == "exter"
        assert result.data["community"]["name"] == "BCC Community"
        assert result.data["community"]["admin_emails"] == ["admin@example.com"]
        
        # Verify repository interaction
        self.mock_repository.load_state.assert_called_once()
    
    def test_get_community_groups_workflow_success(self):
        """Test successful community groups retrieval"""
        # Given: Community with groups
        from app.data.schemas import GroupData
        
        community = CommunityData(
            id="exter", name="BCC Community", description="Test", url_path="/exter",
            password_hash="hash", calendar_url="https://example.com/cal.ics",
            admin_emails=[], is_active=True,
            created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        
        group = GroupData(
            id="football", community_id="exter", name="Football", description="Football events",
            icon="⚽", color="#22C55E", assignment_rules=["football"],
            is_active=True, created_at="2024-09-16T04:00:00Z", updated_at="2024-09-16T04:00:00Z"
        )
        
        state = AppState(
            calendars={}, communities={"exter": community}, groups={"football": group},
            filters={}, subscriptions={}, events_cache={}
        )
        
        self.mock_repository.load_state.return_value = state
        
        # When: Getting community groups
        result = self.service.get_community_groups_workflow("exter")
        
        # Then: Groups retrieved
        assert result.success is True
        assert len(result.data["groups"]) == 1
        assert result.data["groups"][0]["id"] == "football"
        assert result.data["groups"][0]["name"] == "Football"
        assert result.data["groups"][0]["community_id"] == "exter"
        
        # Verify repository interaction
        self.mock_repository.load_state.assert_called_once()


class TestServiceResultModel:
    """Test ServiceResult data model"""
    
    def test_service_result_success(self):
        """Test creating successful result"""
        result = ServiceResult(
            success=True,
            data={"community": {"id": "test"}},
            events=["created"]
        )
        
        assert result.success is True
        assert result.data["community"]["id"] == "test"
        assert result.events == ["created"]
        assert result.error_message is None
    
    def test_service_result_failure(self):
        """Test creating failure result"""
        result = ServiceResult(
            success=False,
            error_message="Validation failed"
        )
        
        assert result.success is False
        assert result.error_message == "Validation failed"
        assert result.data is None
        assert result.events == []  # Default empty list


class TestRequestModels:
    """Test Pydantic request models for OpenAPI"""
    
    def test_community_create_request_valid(self):
        """Test valid community creation request"""
        request = CommunityCreateRequest(
            name="BCC Community Calendar",
            description="Community calendar for BCC events",
            url_path="/exter",
            password="bcc2024",
            calendar_url="https://widgets.bcc.no/ical-xyz/Portal-Calendar.ics",
            admin_emails=["admin@example.com"]
        )
        
        assert request.name == "BCC Community Calendar"
        assert request.url_path == "/exter"
        assert request.admin_emails == ["admin@example.com"]
    
    def test_community_update_request_valid(self):
        """Test valid community update request"""
        request = CommunityUpdateRequest(
            calendar_url="https://widgets.bcc.no/ical-new/Portal-Calendar.ics"
        )
        
        assert request.calendar_url == "https://widgets.bcc.no/ical-new/Portal-Calendar.ics"
    
    def test_community_create_request_validation(self):
        """Test request validation with missing fields"""
        with pytest.raises(ValueError):
            # Missing required fields should raise validation error
            CommunityCreateRequest(
                name="Test"
                # Missing other required fields
            )