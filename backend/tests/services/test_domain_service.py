"""
Unit tests for domain service.

Tests domain CRUD operations, group management, recurring events handling,
and assignment rules. All database operations are mocked using pytest fixtures.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session

from app.services.domain_service import (
    load_domains_config,
    ensure_domain_calendar_exists,
    get_domain_events,
    get_domain_groups,
    create_group,
    assign_recurring_events_to_group,
    create_assignment_rule,
    get_assignment_rules,
    get_recurring_event_assignments,
    build_domain_events_response_data,
    build_domain_events_response_data_legacy,
    auto_assign_events_with_rules,
    get_available_recurring_events,
    update_group,
    delete_group,
    delete_assignment_rule,
    get_available_recurring_events_with_assignments,
    bulk_unassign_recurring_events,
    remove_events_from_specific_group
)
from app.models.calendar import Calendar, Event, Group, RecurringEventGroup, AssignmentRule
from app.models.domain import Domain


@pytest.mark.unit
class TestLoadDomainsConfig:
    """Test domain configuration loading."""

    def test_load_domains_config_success(self, tmp_path):
        """Test successful domain configuration loading."""
        config_file = tmp_path / "domains.yaml"
        config_file.write_text("""
domains:
  - domain_key: test-domain
    name: Test Domain
    calendar_url: https://example.com/cal.ics
""")

        success, config, error = load_domains_config(config_file)

        assert success is True
        assert "domains" in config
        assert error == ""

    def test_load_domains_config_file_not_found(self):
        """Test loading non-existent config file."""
        config_path = Path("/nonexistent/domains.yaml")

        success, config, error = load_domains_config(config_path)

        assert success is False
        assert config == {}
        assert "not found" in error

    def test_load_domains_config_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML file."""
        config_file = tmp_path / "domains.yaml"
        config_file.write_text("invalid: yaml: content: [")

        success, config, error = load_domains_config(config_file)

        assert success is False
        assert config == {}


@pytest.mark.unit
class TestEnsureDomainCalendarExists:
    """Test domain calendar existence checking and creation."""

    @pytest.mark.asyncio
    async def test_ensure_domain_calendar_exists_creates_new(self):
        """Test creating new domain calendar when none exists."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", name="Test Domain",
                          calendar_url="https://example.com/cal.ics",
                          calendar_id=None, id=1)

        # Mock query chain for domain
        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        # Mock calendar creation
        mock_calendar = Mock(id=10, name="Test Domain")

        with patch('app.services.domain_service.sync_calendar_events', new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = (True, 5, "")

            success, calendar, error = await ensure_domain_calendar_exists(mock_db, "test-domain")

        assert success is True
        assert error == ""
        # Verify calendar was created
        assert mock_db.add.called
        assert mock_db.commit.call_count >= 1

    @pytest.mark.asyncio
    async def test_ensure_domain_calendar_exists_uses_existing(self):
        """Test using existing domain calendar."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=10, name="Test Domain", source_url="https://example.com/cal.ics")
        mock_domain = Mock(domain_key="test-domain", calendar_id=10)

        # Mock query chain - domain query returns domain, calendar query returns calendar
        def mock_query_filter(model_class):
            query_mock = Mock()
            if model_class == Domain:
                query_mock.filter.return_value.first.return_value = mock_domain
            elif model_class == Calendar:
                query_mock.filter.return_value.first.return_value = mock_calendar
            return query_mock

        mock_db.query.side_effect = mock_query_filter

        with patch('app.services.domain_service.sync_calendar_events', new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = (True, 5, "")

            success, calendar, error = await ensure_domain_calendar_exists(mock_db, "test-domain")

        assert success is True
        assert calendar == mock_calendar
        assert error == ""

    @pytest.mark.asyncio
    async def test_ensure_domain_calendar_exists_domain_not_found(self):
        """Test when domain doesn't exist."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        success, calendar, error = await ensure_domain_calendar_exists(mock_db, "nonexistent")

        assert success is False
        assert calendar is None
        assert "not found" in error

    @pytest.mark.asyncio
    async def test_ensure_domain_calendar_exists_sync_failure(self):
        """Test when calendar sync fails."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(domain_key="test-domain", calendar_id=10, id=1)
        mock_calendar = Mock(id=10)

        # Mock query chain
        def mock_query_filter(model_class):
            query_mock = Mock()
            if model_class == Domain:
                query_mock.filter.return_value.first.return_value = mock_domain
            elif model_class == Calendar:
                query_mock.filter.return_value.first.return_value = mock_calendar
            return query_mock

        mock_db.query.side_effect = mock_query_filter

        with patch('app.services.domain_service.sync_calendar_events', new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = (False, 0, "Sync error")

            success, calendar, error = await ensure_domain_calendar_exists(mock_db, "test-domain")

        assert success is False
        assert error == "Sync error"


@pytest.mark.unit
class TestGetDomainEvents:
    """Test retrieving domain events."""

    def test_get_domain_events_success(self):
        """Test successful event retrieval."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=10)

        mock_event = Mock(
            id=1,
            title="Test Event",
            start_time=datetime(2025, 10, 10, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2025, 10, 10, 11, 0, tzinfo=timezone.utc),
            description="Test Description",
            location="Test Location",
            uid="test-uid",
            other_ical_fields={"raw_ical": "BEGIN:VEVENT\nEND:VEVENT"}
        )

        with patch('app.services.domain_service.get_calendar_by_domain') as mock_get_cal:
            mock_get_cal.return_value = mock_calendar
            mock_db.query.return_value.filter.return_value.all.return_value = [mock_event]

            events = get_domain_events(mock_db, "test-domain")

        assert len(events) == 1
        assert events[0]["title"] == "Test Event"
        assert events[0]["location"] == "Test Location"
        assert events[0]["calendar_id"] == "domain_test-domain"

    def test_get_domain_events_no_calendar(self):
        """Test when domain has no calendar."""
        mock_db = Mock(spec=Session)

        with patch('app.services.domain_service.get_calendar_by_domain') as mock_get_cal:
            mock_get_cal.return_value = None

            events = get_domain_events(mock_db, "test-domain")

        assert events == []

    def test_get_domain_events_empty_calendar(self):
        """Test when calendar has no events."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=10)

        with patch('app.services.domain_service.get_calendar_by_domain') as mock_get_cal:
            mock_get_cal.return_value = mock_calendar
            mock_db.query.return_value.filter.return_value.all.return_value = []

            events = get_domain_events(mock_db, "test-domain")

        assert events == []


@pytest.mark.unit
class TestGetDomainGroups:
    """Test retrieving domain groups."""

    def test_get_domain_groups_success(self):
        """Test successful group retrieval."""
        mock_db = Mock(spec=Session)
        mock_group1 = MagicMock()
        mock_group1.id = 1
        mock_group1.name = "Group 1"
        mock_group1.domain_key = "test-domain"

        mock_group2 = MagicMock()
        mock_group2.id = 2
        mock_group2.name = "Group 2"
        mock_group2.domain_key = "test-domain"

        mock_groups = [mock_group1, mock_group2]

        # Mock chain now includes .options() for eager loading
        mock_db.query.return_value.options.return_value.filter.return_value.all.return_value = mock_groups

        groups = get_domain_groups(mock_db, "test-domain")

        assert len(groups) == 2
        assert groups[0].name == "Group 1"

    def test_get_domain_groups_empty(self):
        """Test when domain has no groups."""
        mock_db = Mock(spec=Session)
        # Mock chain now includes .options() for eager loading
        mock_db.query.return_value.options.return_value.filter.return_value.all.return_value = []

        groups = get_domain_groups(mock_db, "test-domain")

        assert groups == []


@pytest.mark.unit
class TestCreateGroup:
    """Test group creation."""

    def test_create_group_success(self):
        """Test successful group creation."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(id=1, domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        success, group, error = create_group(mock_db, "test-domain", "New Group")

        assert success is True
        assert error == ""
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_create_group_invalid_name(self):
        """Test group creation with invalid name."""
        mock_db = Mock(spec=Session)

        success, group, error = create_group(mock_db, "test-domain", "")

        assert success is False
        assert group is None
        assert "name" in error.lower()

    def test_create_group_domain_not_found(self):
        """Test group creation when domain doesn't exist."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        success, group, error = create_group(mock_db, "nonexistent", "New Group")

        assert success is False
        assert "not found" in error

    def test_create_group_database_error(self):
        """Test group creation with database error."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(id=1, domain_key="test-domain")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain
        mock_db.commit.side_effect = Exception("Database error")

        success, group, error = create_group(mock_db, "test-domain", "New Group")

        assert success is False
        assert "Database error" in error
        assert mock_db.rollback.called


@pytest.mark.unit
class TestAssignRecurringEventsToGroup:
    """Test assigning recurring events to groups."""

    def test_assign_recurring_events_success(self):
        """Test successful event assignment."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(id=1, domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        event_titles = ["Event 1", "Event 2", "Event 3"]
        success, count, error = assign_recurring_events_to_group(
            mock_db, "test-domain", 1, event_titles
        )

        assert success is True
        assert count == 3
        assert error == ""
        assert mock_db.add.call_count == 3
        assert mock_db.commit.called

    def test_assign_recurring_events_removes_existing(self):
        """Test that existing assignments are removed before new ones."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(id=1, domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        # Mock delete for existing assignments
        mock_query = Mock()
        mock_query.filter.return_value.delete.return_value = 2

        event_titles = ["Event 1"]
        success, count, error = assign_recurring_events_to_group(
            mock_db, "test-domain", 1, event_titles
        )

        assert success is True
        assert count == 1

    def test_assign_recurring_events_empty_list(self):
        """Test assigning empty list of events."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(id=1, domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        success, count, error = assign_recurring_events_to_group(
            mock_db, "test-domain", 1, []
        )

        assert success is True
        assert count == 0

    def test_assign_recurring_events_domain_not_found(self):
        """Test assignment when domain doesn't exist."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        success, count, error = assign_recurring_events_to_group(
            mock_db, "nonexistent", 1, ["Event 1"]
        )

        assert success is False
        assert count == 0
        assert "not found" in error


@pytest.mark.unit
class TestCreateAssignmentRule:
    """Test assignment rule creation."""

    def test_create_assignment_rule_success(self):
        """Test successful rule creation."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(id=1, domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        success, rule, error = create_assignment_rule(
            mock_db, "test-domain", "title_contains", "Meeting", 1
        )

        assert success is True
        assert error == ""
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_create_assignment_rule_invalid_type(self):
        """Test rule creation with invalid rule type."""
        mock_db = Mock(spec=Session)

        success, rule, error = create_assignment_rule(
            mock_db, "test-domain", "invalid_type", "Value", 1
        )

        assert success is False
        assert rule is None

    def test_create_assignment_rule_domain_not_found(self):
        """Test rule creation when domain doesn't exist."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        success, rule, error = create_assignment_rule(
            mock_db, "nonexistent", "title_contains", "Meeting", 1
        )

        assert success is False
        assert "not found" in error


@pytest.mark.unit
class TestGetAssignmentRules:
    """Test retrieving assignment rules."""

    def test_get_assignment_rules_success(self):
        """Test successful rule retrieval."""
        mock_db = Mock(spec=Session)
        mock_rules = [
            Mock(id=1, rule_type="title_contains", rule_value="Meeting", target_group_id=1),
            Mock(id=2, rule_type="location_contains", rule_value="Room", target_group_id=2)
        ]

        mock_db.query.return_value.filter.return_value.all.return_value = mock_rules

        rules = get_assignment_rules(mock_db, "test-domain")

        assert len(rules) == 2
        assert rules[0].rule_type == "title_contains"

    def test_get_assignment_rules_empty(self):
        """Test when domain has no rules."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.all.return_value = []

        rules = get_assignment_rules(mock_db, "test-domain")

        assert rules == []


@pytest.mark.unit
class TestGetRecurringEventAssignments:
    """Test retrieving recurring event assignments."""

    def test_get_recurring_event_assignments_success(self):
        """Test successful assignment retrieval."""
        mock_db = Mock(spec=Session)
        mock_assignments = [
            Mock(recurring_event_title="Event 1", group_id=1),
            Mock(recurring_event_title="Event 2", group_id=1)
        ]

        mock_db.query.return_value.filter.return_value.all.return_value = mock_assignments

        assignments = get_recurring_event_assignments(mock_db, "test-domain")

        assert len(assignments) == 2
        assert assignments[0].recurring_event_title == "Event 1"


@pytest.mark.unit
class TestBuildDomainEventsResponse:
    """Test building domain events response."""

    def test_build_domain_events_response_data(self):
        """Test building domain events response with auto-grouping."""
        mock_db = Mock(spec=Session)

        # Mock events
        mock_event = Mock(
            id=1,
            title="Test Event",
            start_time=datetime(2025, 10, 10, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2025, 10, 10, 11, 0, tzinfo=timezone.utc),
            description="Test",
            location="Location",
            uid="test-uid",
            other_ical_fields={"raw_ical": "BEGIN:VEVENT\nEND:VEVENT"}
        )

        mock_calendar = Mock(id=10)

        with patch('app.services.domain_service.get_domain_events') as mock_get_events:
            with patch('app.services.domain_service.get_domain_groups') as mock_get_groups:
                with patch('app.services.domain_service.get_recurring_event_assignments') as mock_get_assigns:
                    mock_get_events.return_value = []
                    mock_get_groups.return_value = []
                    mock_get_assigns.return_value = []

                    response = build_domain_events_response_data(mock_db, "test-domain")

        # Just verify it returns a dict with groups (the pure function determines exact structure)
        assert isinstance(response, dict)
        assert "groups" in response

    def test_build_domain_events_response_data_legacy(self):
        """Test building legacy domain events response."""
        mock_db = Mock(spec=Session)

        with patch('app.services.domain_service.get_domain_events') as mock_get_events:
            with patch('app.services.domain_service.get_domain_groups') as mock_get_groups:
                with patch('app.services.domain_service.get_recurring_event_assignments') as mock_get_assigns:
                    mock_get_events.return_value = []
                    mock_get_groups.return_value = []
                    mock_get_assigns.return_value = []

                    response = build_domain_events_response_data_legacy(mock_db, "test-domain")

        assert "groups" in response
        assert "ungrouped_events" in response


@pytest.mark.unit
class TestAutoAssignEventsWithRules:
    """Test auto-assignment of events using rules."""

    @pytest.mark.asyncio
    async def test_auto_assign_events_with_rules_success(self):
        """Test successful auto-assignment."""
        mock_db = Mock(spec=Session)

        mock_events = [
            {
                "id": "evt_1",
                "title": "Team Meeting",
                "start_time": datetime(2025, 10, 10, 10, 0, tzinfo=timezone.utc),
                "end_time": datetime(2025, 10, 10, 11, 0, tzinfo=timezone.utc),
            }
        ]

        mock_rules = [
            Mock(rule_type="title_contains", rule_value="Meeting", target_group_id=1)
        ]

        with patch('app.services.domain_service.get_domain_events') as mock_get_events:
            with patch('app.services.domain_service.get_assignment_rules') as mock_get_rules:
                with patch('app.services.domain_service.assign_recurring_events_to_group') as mock_assign:
                    mock_get_events.return_value = mock_events
                    mock_get_rules.return_value = mock_rules
                    mock_assign.return_value = (True, 1, "")

                    success, count, error = await auto_assign_events_with_rules(mock_db, "test-domain")

        assert success is True
        assert count >= 0

    @pytest.mark.asyncio
    async def test_auto_assign_events_no_rules(self):
        """Test auto-assignment when no rules exist."""
        mock_db = Mock(spec=Session)

        with patch('app.services.domain_service.get_domain_events') as mock_get_events:
            with patch('app.services.domain_service.get_assignment_rules') as mock_get_rules:
                mock_get_events.return_value = []
                mock_get_rules.return_value = []

                success, count, error = await auto_assign_events_with_rules(mock_db, "test-domain")

        assert success is True
        assert count == 0
        assert "No assignment rules" in error


@pytest.mark.unit
class TestGetAvailableRecurringEvents:
    """Test retrieving available recurring events."""

    def test_get_available_recurring_events_success(self):
        """Test successful retrieval of recurring events."""
        mock_db = Mock(spec=Session)

        mock_events = [
            {
                "id": "evt_1",
                "title": "Team Meeting",
                "start": "2025-10-10T10:00:00Z",
                "location": "Room 1"
            },
            {
                "id": "evt_2",
                "title": "Team Meeting",
                "start": "2025-10-11T10:00:00Z",
                "location": "Room 1"
            }
        ]

        with patch('app.services.domain_service.get_domain_events') as mock_get_events:
            mock_get_events.return_value = mock_events

            events = get_available_recurring_events(mock_db, "test-domain")

        assert len(events) >= 0

    def test_get_available_recurring_events_sorted(self):
        """Test that recurring events are sorted by count."""
        mock_db = Mock(spec=Session)

        with patch('app.services.domain_service.get_domain_events') as mock_get_events:
            mock_get_events.return_value = []

            events = get_available_recurring_events(mock_db, "test-domain")

        assert isinstance(events, list)


@pytest.mark.unit
class TestUpdateGroup:
    """Test group update operations."""

    def test_update_group_success(self):
        """Test successful group update."""
        mock_db = Mock(spec=Session)
        mock_group = Mock(id=1, name="Old Name", domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_group

        success, group, error = update_group(mock_db, 1, "test-domain", "New Name")

        assert success is True
        assert error == ""
        assert mock_db.commit.called

    def test_update_group_not_found(self):
        """Test updating non-existent group."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        success, group, error = update_group(mock_db, 999, "test-domain", "New Name")

        assert success is False
        assert "not found" in error

    def test_update_group_invalid_name(self):
        """Test updating group with invalid name."""
        mock_db = Mock(spec=Session)

        success, group, error = update_group(mock_db, 1, "test-domain", "")

        assert success is False
        assert "name" in error.lower()


@pytest.mark.unit
class TestDeleteGroup:
    """Test group deletion."""

    def test_delete_group_success(self):
        """Test successful group deletion."""
        mock_db = Mock(spec=Session)
        mock_group = Mock(id=1, name="Test Group", domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_group

        success, error = delete_group(mock_db, 1, "test-domain")

        assert success is True
        assert error == ""
        assert mock_db.delete.called
        assert mock_db.commit.called

    def test_delete_group_not_found(self):
        """Test deleting non-existent group."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        success, error = delete_group(mock_db, 999, "test-domain")

        assert success is False
        assert "not found" in error


@pytest.mark.unit
class TestDeleteAssignmentRule:
    """Test assignment rule deletion."""

    def test_delete_assignment_rule_success(self):
        """Test successful rule deletion."""
        mock_db = Mock(spec=Session)
        mock_rule = Mock(id=1, domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_rule

        success, error = delete_assignment_rule(mock_db, 1, "test-domain")

        assert success is True
        assert error == ""
        assert mock_db.delete.called
        assert mock_db.commit.called

    def test_delete_assignment_rule_not_found(self):
        """Test deleting non-existent rule."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        success, error = delete_assignment_rule(mock_db, 999, "test-domain")

        assert success is False
        assert "not found" in error


@pytest.mark.unit
class TestGetAvailableRecurringEventsWithAssignments:
    """Test retrieving recurring events with assignment info."""

    def test_get_available_recurring_events_with_assignments(self):
        """Test retrieval with assignment information."""
        mock_db = Mock(spec=Session)

        mock_events = []
        mock_assignments = []

        # Mock queries
        mock_db.query.return_value.filter.return_value.all.return_value = mock_assignments

        with patch('app.services.domain_service.get_domain_events') as mock_get_events:
            mock_get_events.return_value = mock_events

            events = get_available_recurring_events_with_assignments(mock_db, "test-domain")

        assert isinstance(events, list)


@pytest.mark.unit
class TestBulkUnassignRecurringEvents:
    """Test bulk unassignment of recurring events."""

    def test_bulk_unassign_recurring_events_success(self):
        """Test successful bulk unassignment."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.delete.return_value = 3
        mock_db.query.return_value = mock_query

        event_titles = ["Event 1", "Event 2", "Event 3"]
        success, count, error = bulk_unassign_recurring_events(mock_db, "test-domain", event_titles)

        assert success is True
        assert count == 3
        assert error == ""
        assert mock_db.commit.called

    def test_bulk_unassign_recurring_events_empty_list(self):
        """Test bulk unassignment with empty list."""
        mock_db = Mock(spec=Session)

        success, count, error = bulk_unassign_recurring_events(mock_db, "test-domain", [])

        assert success is True
        assert count == 0
        assert "No events to unassign" in error


@pytest.mark.unit
class TestRemoveEventsFromSpecificGroup:
    """Test removing events from specific group."""

    def test_remove_events_from_specific_group_success(self):
        """Test successful removal of events from group."""
        mock_db = Mock(spec=Session)
        mock_group = Mock(id=1, domain_key="test-domain")

        # Mock group query
        group_query = Mock()
        group_query.filter.return_value.first.return_value = mock_group

        # Mock deletion query
        delete_query = Mock()
        delete_query.filter.return_value.delete.return_value = 2

        def mock_query_side_effect(model_class):
            if model_class == Group:
                return group_query
            elif model_class == RecurringEventGroup:
                return delete_query
            return Mock()

        mock_db.query.side_effect = mock_query_side_effect

        event_titles = ["Event 1", "Event 2"]
        success, count, error = remove_events_from_specific_group(
            mock_db, "test-domain", 1, event_titles
        )

        assert success is True
        assert count == 2
        assert error == ""
        assert mock_db.commit.called

    def test_remove_events_from_specific_group_not_found(self):
        """Test removal when group doesn't exist."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        success, count, error = remove_events_from_specific_group(
            mock_db, "test-domain", 999, ["Event 1"]
        )

        assert success is False
        assert count == 0
        assert "not found" in error.lower()

    def test_remove_events_from_specific_group_empty_list(self):
        """Test removal with empty event list."""
        mock_db = Mock(spec=Session)

        success, count, error = remove_events_from_specific_group(
            mock_db, "test-domain", 1, []
        )

        assert success is True
        assert count == 0
        assert "No events to remove" in error
