"""
Unit tests for calendar service.

Tests calendar CRUD operations, event synchronization, filter operations,
and the new apply_filter_to_events service function. All external dependencies
are mocked using pytest fixtures.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
import httpx
from app.core.result import ok, fail

from app.services.calendar_service import (
    fetch_ical_content,
    create_calendar,
    get_calendars,
    get_calendar_by_id,
    get_calendar_by_domain,
    delete_calendar,
    sync_calendar_events,
    get_calendar_events,
    create_filter,
    get_filters,
    get_filter_by_uuid,
    get_filter_by_id,
    delete_filter,
    apply_filter_to_events
)
from app.models.calendar import Calendar, Event, Filter, RecurringEventGroup
from app.models.domain import Domain


@pytest.mark.unit
class TestFetchIcalContent:
    """Test iCal content fetching."""

    @pytest.mark.asyncio
    async def test_fetch_ical_content_success(self):
        """Test successful iCal fetch."""
        mock_response = Mock()
        mock_response.text = "BEGIN:VCALENDAR\nEND:VCALENDAR"
        mock_response.status_code = 200

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            success, content, error = await fetch_ical_content("https://example.com/cal.ics")

        assert success is True
        assert "BEGIN:VCALENDAR" in content
        assert error == ""

    @pytest.mark.asyncio
    async def test_fetch_ical_content_timeout(self):
        """Test iCal fetch timeout."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            success, content, error = await fetch_ical_content("https://example.com/cal.ics", timeout=5)

        assert success is False
        assert content == ""
        assert "Timeout" in error

    @pytest.mark.asyncio
    async def test_fetch_ical_content_http_error(self):
        """Test iCal fetch HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404

        with patch('httpx.AsyncClient') as mock_client:
            mock_get = AsyncMock(side_effect=httpx.HTTPStatusError(
                "Not Found", request=Mock(), response=mock_response
            ))
            mock_client.return_value.__aenter__.return_value.get = mock_get

            success, content, error = await fetch_ical_content("https://example.com/cal.ics")

        assert success is False
        assert content == ""
        assert "HTTP" in error

    @pytest.mark.asyncio
    async def test_fetch_ical_content_generic_error(self):
        """Test iCal fetch generic error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Network error")
            )

            success, content, error = await fetch_ical_content("https://example.com/cal.ics")

        assert success is False
        assert "Error fetching calendar" in error


@pytest.mark.unit
class TestCreateCalendar:
    """Test calendar creation."""

    def test_create_calendar_success(self):
        """Test successful calendar creation."""
        mock_db = Mock(spec=Session)

        success, calendar, error = create_calendar(
            mock_db, "Test Calendar", "https://example.com/cal.ics"
        )

        assert success is True
        assert error == ""
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_create_calendar_domain_type(self):
        """Test domain calendar creation."""
        mock_db = Mock(spec=Session)

        success, calendar, error = create_calendar(
            mock_db, "Domain Cal", "https://example.com/cal.ics",
            calendar_type="domain", user_id=1
        )

        assert success is True
        assert error == ""

    def test_create_calendar_invalid_name(self):
        """Test calendar creation with invalid name."""
        mock_db = Mock(spec=Session)

        success, calendar, error = create_calendar(
            mock_db, "", "https://example.com/cal.ics"
        )

        assert success is False
        assert calendar is None
        assert "name" in error.lower()

    def test_create_calendar_invalid_url(self):
        """Test calendar creation with invalid URL."""
        mock_db = Mock(spec=Session)

        success, calendar, error = create_calendar(
            mock_db, "Test Calendar", ""
        )

        assert success is False
        assert calendar is None
        assert "url" in error.lower()

    def test_create_calendar_database_error(self):
        """Test calendar creation with database error."""
        mock_db = Mock(spec=Session)
        mock_db.commit.side_effect = Exception("Database error")

        success, calendar, error = create_calendar(
            mock_db, "Test Calendar", "https://example.com/cal.ics"
        )

        assert success is False
        assert "Database error" in error
        assert mock_db.rollback.called


@pytest.mark.unit
class TestGetCalendars:
    """Test calendar retrieval."""

    def test_get_calendars_with_user_id(self):
        """Test getting calendars for specific user."""
        mock_db = Mock(spec=Session)
        mock_calendars = [
            Mock(id=1, name="Calendar 1", user_id=1, spec=['id', 'name', 'user_id']),
            Mock(id=2, name="Calendar 2", user_id=1, spec=['id', 'name', 'user_id'])
        ]
        # Set attributes directly to avoid mock confusion
        mock_calendars[0].configure_mock(id=1, name="Calendar 1", user_id=1)
        mock_calendars[1].configure_mock(id=2, name="Calendar 2", user_id=1)

        mock_db.query.return_value.filter.return_value.all.return_value = mock_calendars

        calendars = get_calendars(mock_db, user_id=1)

        assert len(calendars) == 2
        # Just verify we got the right objects back
        assert calendars == mock_calendars

    def test_get_calendars_no_user_id(self):
        """Test getting calendars without user_id returns empty list."""
        mock_db = Mock(spec=Session)

        calendars = get_calendars(mock_db, user_id=None)

        assert calendars == []
        assert not mock_db.query.called

    def test_get_calendars_empty_result(self):
        """Test getting calendars with no results."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.all.return_value = []

        calendars = get_calendars(mock_db, user_id=1)

        assert calendars == []


@pytest.mark.unit
class TestGetCalendarById:
    """Test getting calendar by ID."""

    def test_get_calendar_by_id_success(self):
        """Test successful calendar retrieval by ID."""
        mock_db = Mock(spec=Session)
        mock_calendar = MagicMock()
        mock_calendar.id = 1
        mock_calendar.name = "Test Calendar"
        mock_calendar.user_id = 1

        # Mock the query chain properly - need to handle filter being called multiple times
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.first.return_value = mock_calendar
        mock_db.query.return_value = mock_query

        calendar = get_calendar_by_id(mock_db, 1, user_id=1)

        assert calendar == mock_calendar
        assert calendar.id == 1

    def test_get_calendar_by_id_not_found(self):
        """Test calendar not found."""
        mock_db = Mock(spec=Session)

        # Mock the query chain properly - need to handle filter being called multiple times
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        calendar = get_calendar_by_id(mock_db, 999, user_id=1)

        assert calendar is None

    def test_get_calendar_by_id_without_user_filter(self):
        """Test getting calendar without user filter."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=1, name="Test Calendar")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_calendar

        calendar = get_calendar_by_id(mock_db, 1)

        assert calendar == mock_calendar

    def test_get_calendar_by_id_database_error(self):
        """Test graceful handling of database errors."""
        mock_db = Mock(spec=Session)
        mock_db.query.side_effect = Exception("Database error")

        calendar = get_calendar_by_id(mock_db, 1, user_id=1)

        assert calendar is None


@pytest.mark.unit
class TestGetCalendarByDomain:
    """Test getting calendar by domain."""

    def test_get_calendar_by_domain_success(self):
        """Test successful domain calendar retrieval."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=1, name="Domain Calendar", type="domain")

        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_calendar

        calendar = get_calendar_by_domain(mock_db, "test-domain")

        assert calendar == mock_calendar
        assert calendar.type == "domain"

    def test_get_calendar_by_domain_not_found(self):
        """Test domain calendar not found."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = None

        calendar = get_calendar_by_domain(mock_db, "nonexistent-domain")

        assert calendar is None


@pytest.mark.unit
class TestDeleteCalendar:
    """Test calendar deletion."""

    def test_delete_calendar_success(self):
        """Test successful calendar deletion."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=1, name="Test Calendar")

        with patch('app.services.calendar_service.get_calendar_by_id') as mock_get:
            mock_get.return_value = mock_calendar

            success, error = delete_calendar(mock_db, 1, user_id=1)

        assert success is True
        assert error == ""
        assert mock_db.delete.called
        assert mock_db.commit.called

    def test_delete_calendar_not_found(self):
        """Test deleting non-existent calendar."""
        mock_db = Mock(spec=Session)

        with patch('app.services.calendar_service.get_calendar_by_id') as mock_get:
            mock_get.return_value = None

            success, error = delete_calendar(mock_db, 999, user_id=1)

        assert success is False
        assert "not found" in error

    def test_delete_calendar_database_error(self):
        """Test calendar deletion with database error."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=1)
        mock_db.commit.side_effect = Exception("Database error")

        with patch('app.services.calendar_service.get_calendar_by_id') as mock_get:
            mock_get.return_value = mock_calendar

            success, error = delete_calendar(mock_db, 1, user_id=1)

        assert success is False
        assert "Database error" in error
        assert mock_db.rollback.called


@pytest.mark.unit
class TestSyncCalendarEvents:
    """Test calendar event synchronization."""

    @pytest.mark.asyncio
    async def test_sync_calendar_events_success(self):
        """Test successful event synchronization."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=1, source_url="https://example.com/cal.ics")

        # Use a date within the last week (events older than 1 week are filtered out)
        today = datetime.now(timezone.utc)
        mock_event_data = [
            {
                "title": "Event 1",
                "start_time": today,
                "end_time": today + timedelta(hours=1),
                "description": "Test event",
                "location": "Test location",
                "uid": "event-1"
            }
        ]

        with patch('app.services.calendar_service.fetch_ical_content', new_callable=AsyncMock) as mock_fetch:
            with patch('app.services.calendar_service.parse_ical_content') as mock_parse:
                mock_fetch.return_value = (True, "ical_content", "")
                mock_parse.return_value = ok(mock_event_data)

                success, count, error = await sync_calendar_events(mock_db, mock_calendar)

        assert success is True
        assert count == 1
        assert error == ""
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_sync_calendar_events_fetch_failure(self):
        """Test sync failure when fetch fails."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=1, source_url="https://example.com/cal.ics")

        with patch('app.services.calendar_service.fetch_ical_content', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (False, "", "Fetch error")

            success, count, error = await sync_calendar_events(mock_db, mock_calendar)

        assert success is False
        assert count == 0
        assert error == "Fetch error"

    @pytest.mark.asyncio
    async def test_sync_calendar_events_parse_failure(self):
        """Test sync failure when parsing fails."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=1, source_url="https://example.com/cal.ics")

        with patch('app.services.calendar_service.fetch_ical_content', new_callable=AsyncMock) as mock_fetch:
            with patch('app.services.calendar_service.parse_ical_content') as mock_parse:
                mock_fetch.return_value = (True, "ical_content", "")
                mock_parse.return_value = fail("Parse error")

                success, count, error = await sync_calendar_events(mock_db, mock_calendar)

        assert success is False
        assert count == 0
        assert error == "Parse error"

    @pytest.mark.asyncio
    async def test_sync_calendar_events_filters_old_events(self):
        """Test that old events are filtered out."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=1, source_url="https://example.com/cal.ics")

        old_date = datetime(2020, 1, 1, 10, 0, tzinfo=timezone.utc)
        recent_date = datetime.now(timezone.utc)

        mock_event_data = [
            {
                "title": "Old Event",
                "start_time": old_date,
                "end_time": old_date + timedelta(hours=1),
                "uid": "old-event"
            },
            {
                "title": "Recent Event",
                "start_time": recent_date,
                "end_time": recent_date + timedelta(hours=1),
                "uid": "recent-event"
            }
        ]

        with patch('app.services.calendar_service.fetch_ical_content', new_callable=AsyncMock) as mock_fetch:
            with patch('app.services.calendar_service.parse_ical_content') as mock_parse:
                mock_fetch.return_value = (True, "ical_content", "")
                mock_parse.return_value = ok(mock_event_data)

                success, count, error = await sync_calendar_events(mock_db, mock_calendar)

        assert success is True
        # Should only sync recent event
        assert count == 1

    @pytest.mark.asyncio
    async def test_sync_calendar_events_database_error(self):
        """Test sync with database error."""
        mock_db = Mock(spec=Session)
        mock_calendar = Mock(id=1, source_url="https://example.com/cal.ics")
        mock_db.commit.side_effect = Exception("Database error")

        mock_event_data = [
            {
                "title": "Event 1",
                "start_time": datetime.now(timezone.utc),
                "end_time": datetime.now(timezone.utc) + timedelta(hours=1),
                "uid": "event-1"
            }
        ]

        with patch('app.services.calendar_service.fetch_ical_content', new_callable=AsyncMock) as mock_fetch:
            with patch('app.services.calendar_service.parse_ical_content') as mock_parse:
                mock_fetch.return_value = (True, "ical_content", "")
                mock_parse.return_value = (True, mock_event_data, "")

                success, count, error = await sync_calendar_events(mock_db, mock_calendar)

        assert success is False
        assert "Sync error" in error
        assert mock_db.rollback.called


@pytest.mark.unit
class TestGetCalendarEvents:
    """Test getting calendar events."""

    def test_get_calendar_events_success(self):
        """Test successful event retrieval."""
        mock_db = Mock(spec=Session)
        mock_events = [
            Mock(id=1, title="Event 1", calendar_id=1),
            Mock(id=2, title="Event 2", calendar_id=1)
        ]

        mock_db.query.return_value.filter.return_value.all.return_value = mock_events

        events = get_calendar_events(mock_db, 1)

        assert len(events) == 2
        assert events[0].title == "Event 1"

    def test_get_calendar_events_empty(self):
        """Test getting events from empty calendar."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.all.return_value = []

        events = get_calendar_events(mock_db, 1)

        assert events == []


@pytest.mark.unit
class TestCreateFilter:
    """Test filter creation."""

    def test_create_filter_user_filter_success(self):
        """Test successful user filter creation."""
        mock_db = Mock(spec=Session)

        success, filter_obj, error = create_filter(
            mock_db, "Test Filter", calendar_id=1, user_id=1,
            subscribed_event_ids=[1, 2, 3]
        )

        assert success is True
        assert error == ""
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_create_filter_domain_filter_success(self):
        """Test successful domain filter creation."""
        mock_db = Mock(spec=Session)
        mock_domain = Mock(id=1, domain_key="test-domain")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_domain

        success, filter_obj, error = create_filter(
            mock_db, "Domain Filter", domain_key="test-domain",
            subscribed_group_ids=[1, 2]
        )

        assert success is True
        assert error == ""

    def test_create_filter_invalid_name(self):
        """Test filter creation with invalid name."""
        mock_db = Mock(spec=Session)

        success, filter_obj, error = create_filter(
            mock_db, "", calendar_id=1, user_id=1
        )

        assert success is False
        assert filter_obj is None
        assert "name" in error.lower()

    def test_create_filter_missing_calendar_and_domain(self):
        """Test filter creation without calendar_id or domain_key."""
        mock_db = Mock(spec=Session)

        success, filter_obj, error = create_filter(
            mock_db, "Test Filter", user_id=1
        )

        assert success is False
        assert filter_obj is None

    def test_create_filter_database_error(self):
        """Test filter creation with database error."""
        mock_db = Mock(spec=Session)
        mock_db.commit.side_effect = Exception("Database error")

        success, filter_obj, error = create_filter(
            mock_db, "Test Filter", calendar_id=1, user_id=1
        )

        assert success is False
        assert "Database error" in error
        assert mock_db.rollback.called


@pytest.mark.unit
class TestGetFilters:
    """Test filter retrieval."""

    def test_get_filters_by_calendar(self):
        """Test getting filters by calendar ID."""
        mock_db = Mock(spec=Session)
        mock_filters = [
            Mock(id=1, name="Filter 1", calendar_id=1),
            Mock(id=2, name="Filter 2", calendar_id=1)
        ]

        # get_filters returns query.all() after filtering
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = mock_filters

        filters = get_filters(mock_db, calendar_id=1)

        assert len(filters) == 2
        assert filters == mock_filters

    def test_get_filters_by_domain(self):
        """Test getting filters by domain key."""
        mock_db = Mock(spec=Session)
        mock_filters = [
            Mock(id=1, name="Domain Filter", domain_key="test-domain")
        ]

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = mock_filters

        filters = get_filters(mock_db, domain_key="test-domain")

        assert len(filters) == 1
        assert filters == mock_filters

    def test_get_filters_by_user(self):
        """Test getting filters by user ID."""
        mock_db = Mock(spec=Session)
        mock_filters = [
            Mock(id=1, name="User Filter", user_id=1)
        ]

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = mock_filters

        filters = get_filters(mock_db, user_id=1)

        assert len(filters) == 1
        assert filters == mock_filters


@pytest.mark.unit
class TestGetFilterByUuid:
    """Test getting filter by UUID."""

    def test_get_filter_by_uuid_success(self):
        """Test successful filter retrieval by UUID."""
        mock_db = Mock(spec=Session)
        mock_filter = Mock(id=1, link_uuid="test-uuid-123")

        mock_db.query.return_value.filter.return_value.first.return_value = mock_filter

        filter_obj = get_filter_by_uuid(mock_db, "test-uuid-123")

        assert filter_obj == mock_filter

    def test_get_filter_by_uuid_not_found(self):
        """Test filter not found by UUID."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        filter_obj = get_filter_by_uuid(mock_db, "nonexistent-uuid")

        assert filter_obj is None

    def test_get_filter_by_uuid_database_error(self):
        """Test graceful handling of database errors."""
        mock_db = Mock(spec=Session)
        mock_db.query.side_effect = Exception("Database error")

        filter_obj = get_filter_by_uuid(mock_db, "test-uuid")

        assert filter_obj is None


@pytest.mark.unit
class TestGetFilterById:
    """Test getting filter by ID."""

    def test_get_filter_by_id_success(self):
        """Test successful filter retrieval by ID."""
        mock_db = Mock(spec=Session)
        mock_filter = MagicMock()
        mock_filter.id = 1
        mock_filter.name = "Test Filter"
        mock_filter.calendar_id = 1

        # Need to handle multiple filter() calls in the query chain
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.filter.return_value.first.return_value = mock_filter

        filter_obj = get_filter_by_id(mock_db, 1, calendar_id=1)

        assert filter_obj == mock_filter

    def test_get_filter_by_id_with_domain(self):
        """Test getting filter by ID with domain filter."""
        mock_db = Mock(spec=Session)
        mock_filter = MagicMock()
        mock_filter.id = 1
        mock_filter.name = "Domain Filter"
        mock_filter.domain_key = "test-domain"

        # Need to handle multiple filter() calls in the query chain
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.filter.return_value.first.return_value = mock_filter

        filter_obj = get_filter_by_id(mock_db, 1, domain_key="test-domain")

        assert filter_obj == mock_filter

    def test_get_filter_by_id_not_found(self):
        """Test filter not found by ID."""
        mock_db = Mock(spec=Session)

        # Need to handle multiple filter() calls in the query chain
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.filter.return_value.first.return_value = None

        filter_obj = get_filter_by_id(mock_db, 999, calendar_id=1)

        assert filter_obj is None


@pytest.mark.unit
class TestDeleteFilter:
    """Test filter deletion."""

    def test_delete_filter_success(self):
        """Test successful filter deletion."""
        mock_db = Mock(spec=Session)
        mock_filter = Mock(id=1, name="Test Filter")

        with patch('app.services.calendar_service.get_filter_by_id') as mock_get:
            mock_get.return_value = mock_filter

            success, error = delete_filter(mock_db, 1, calendar_id=1)

        assert success is True
        assert error == ""
        assert mock_db.delete.called
        assert mock_db.commit.called

    def test_delete_filter_not_found(self):
        """Test deleting non-existent filter."""
        mock_db = Mock(spec=Session)

        with patch('app.services.calendar_service.get_filter_by_id') as mock_get:
            mock_get.return_value = None

            success, error = delete_filter(mock_db, 999, calendar_id=1)

        assert success is False
        assert "not found" in error

    def test_delete_filter_database_error(self):
        """Test filter deletion with database error."""
        mock_db = Mock(spec=Session)
        mock_filter = Mock(id=1)
        mock_db.commit.side_effect = Exception("Database error")

        with patch('app.services.calendar_service.get_filter_by_id') as mock_get:
            mock_get.return_value = mock_filter

            success, error = delete_filter(mock_db, 1, calendar_id=1)

        assert success is False
        assert "Database error" in error
        assert mock_db.rollback.called


@pytest.mark.unit
class TestApplyFilterToEvents:
    """Test the NEW apply_filter_to_events service function."""

    def test_apply_filter_to_events_personal_filter(self):
        """Test applying personal calendar filter (no I/O)."""
        mock_db = Mock(spec=Session)

        events = [
            {"id": "evt_1", "title": "Event 1"},
            {"id": "evt_2", "title": "Event 2"},
            {"id": "evt_3", "title": "Event 3"}
        ]

        filter_data = {
            "calendar_id": 1,
            "subscribed_event_ids": ["evt_1", "evt_3"]
        }

        with patch('app.services.calendar_service.apply_filter_pure') as mock_pure:
            mock_pure.return_value = [events[0], events[2]]

            result = apply_filter_to_events(mock_db, events, filter_data)

        # Should call pure function directly without database queries
        mock_pure.assert_called_once()
        assert len(result) == 2

    def test_apply_filter_to_events_domain_filter(self):
        """Test applying domain filter (with I/O for group titles)."""
        mock_db = Mock(spec=Session)

        events = [
            {"id": "evt_1", "title": "Team Meeting"},
            {"id": "evt_2", "title": "Project Review"},
            {"id": "evt_3", "title": "Daily Standup"}
        ]

        filter_data = {
            "domain_key": "test-domain",
            "subscribed_group_ids": [1, 2],
            "unselected_event_ids": []
        }

        # Mock database query for group assignments
        mock_assignments = [
            Mock(recurring_event_title="Team Meeting", group_id=1),
            Mock(recurring_event_title="Project Review", group_id=2)
        ]

        mock_db.query.return_value.filter.return_value.all.return_value = mock_assignments

        with patch('app.services.calendar_service.apply_filter_pure') as mock_pure:
            mock_pure.return_value = [events[0], events[1]]

            result = apply_filter_to_events(mock_db, events, filter_data)

        # Should query database for group titles
        assert mock_db.query.called
        # Should call pure function with resolved group titles
        mock_pure.assert_called_once()
        call_args = mock_pure.call_args
        assert "group_event_titles" in call_args[1]

    def test_apply_filter_to_events_domain_filter_no_groups(self):
        """Test domain filter with no subscribed groups."""
        mock_db = Mock(spec=Session)

        events = [
            {"id": "evt_1", "title": "Event 1"}
        ]

        filter_data = {
            "domain_key": "test-domain",
            "subscribed_group_ids": []
        }

        with patch('app.services.calendar_service.apply_filter_pure') as mock_pure:
            mock_pure.return_value = []

            result = apply_filter_to_events(mock_db, events, filter_data)

        # Should still call pure function
        mock_pure.assert_called_once()

    def test_apply_filter_to_events_empty_events(self):
        """Test applying filter to empty events list."""
        mock_db = Mock(spec=Session)

        filter_data = {
            "calendar_id": 1,
            "subscribed_event_ids": [1, 2]
        }

        with patch('app.services.calendar_service.apply_filter_pure') as mock_pure:
            mock_pure.return_value = []

            result = apply_filter_to_events(mock_db, [], filter_data)

        assert result == []

    def test_apply_filter_to_events_domain_with_unselected(self):
        """Test domain filter with unselected events."""
        mock_db = Mock(spec=Session)

        events = [
            {"id": "evt_1", "title": "Team Meeting"},
            {"id": "evt_2", "title": "Project Review"}
        ]

        filter_data = {
            "domain_key": "test-domain",
            "subscribed_group_ids": [1],
            "unselected_event_ids": ["Team Meeting"]
        }

        mock_assignments = [
            Mock(recurring_event_title="Team Meeting", group_id=1),
            Mock(recurring_event_title="Project Review", group_id=1)
        ]

        mock_db.query.return_value.filter.return_value.all.return_value = mock_assignments

        with patch('app.services.calendar_service.apply_filter_pure') as mock_pure:
            mock_pure.return_value = [events[1]]  # Only Project Review

            result = apply_filter_to_events(mock_db, events, filter_data)

        # Team Meeting should be filtered out by unselected_event_ids
        assert len(result) == 1
