"""
Test suite for domain filter update operations.

Addresses critical bug: Events disappear when updating filters because frontend
only sends visible events, and backend replaces all events with incomplete data.

This test ensures that updating a filter preserves unmodified fields.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.domain import Domain


@pytest.mark.integration
class TestFilterUpdatePreservation:
    """Test that filter updates preserve unmodified data (PATCH semantics)."""

    def test_update_filter_name_only_preserves_events(
        self, test_client: TestClient, test_domain: Domain
    ):
        """
        CRITICAL BUG REGRESSION TEST:
        Updating only the filter name should NOT lose event selections.

        Bug scenario:
        1. User creates filter with 100 events
        2. Later opens filter to edit name
        3. Frontend only loads 20 visible events into selection state
        4. User saves with new name
        5. Backend receives update with only 20 events
        6. Backend overwrites all 100 events with just those 20
        7. Result: 80 events permanently lost

        This test ensures PATCH semantics: only update fields that are sent.
        """
        # Step 1: Create filter with 100 events
        create_response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/filters",
            json={
                "name": "Original Filter",
                "subscribed_event_ids": [f"Event {i}" for i in range(100)],
                "subscribed_group_ids": [],
                "unselected_event_ids": []
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert create_response.status_code == 201, f"Filter creation failed: {create_response.json()}"
        created_filter = create_response.json()
        filter_id = created_filter["id"]

        # Verify filter was created with all 100 events
        assert len(created_filter["subscribed_event_ids"]) == 100
        assert created_filter["name"] == "Original Filter"

        # Step 2: Update only the name (simulating frontend that only loaded 20 events)
        # CRITICAL: Do NOT send subscribed_event_ids
        update_response = test_client.put(
            f"/api/domains/{test_domain.domain_key}/filters/{filter_id}",
            json={
                "name": "Updated Filter Name"
                # NOTE: subscribed_event_ids NOT included - should preserve original!
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert update_response.status_code == 200, f"Filter update failed: {update_response.json()}"
        updated_filter = update_response.json()

        # Step 3: Verify ALL 100 events are still there
        assert updated_filter["name"] == "Updated Filter Name", "Name not updated"
        assert len(updated_filter["subscribed_event_ids"]) == 100, \
            f"Events lost! Expected 100, got {len(updated_filter['subscribed_event_ids'])}"
        assert updated_filter["subscribed_event_ids"] == created_filter["subscribed_event_ids"], \
            "Event list changed when it shouldn't have"

    def test_update_filter_events_replaces_list(
        self, test_client: TestClient, test_domain: Domain
    ):
        """
        Test that explicitly updating events DOES replace the list.
        This verifies we can still update events when needed.
        """
        # Create filter with 100 events
        create_response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/filters",
            json={
                "name": "Filter",
                "subscribed_event_ids": [f"Event {i}" for i in range(100)],
                "subscribed_group_ids": [],
                "unselected_event_ids": []
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert create_response.status_code == 201
        filter_id = create_response.json()["id"]

        # Update with new event list (intentionally different)
        update_response = test_client.put(
            f"/api/domains/{test_domain.domain_key}/filters/{filter_id}",
            json={
                "name": "Filter",
                "subscribed_event_ids": ["Event A", "Event B", "Event C"]  # Explicitly change
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert update_response.status_code == 200
        updated_filter = update_response.json()

        # Verify events were replaced
        assert len(updated_filter["subscribed_event_ids"]) == 3
        assert updated_filter["subscribed_event_ids"] == ["Event A", "Event B", "Event C"]

    def test_update_filter_groups_preserves_events(
        self, test_client: TestClient, test_domain: Domain, test_group
    ):
        """
        Test that updating group subscriptions preserves individual event selections.
        """
        # Create filter with individual events and groups
        create_response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/filters",
            json={
                "name": "Mixed Filter",
                "subscribed_event_ids": ["Event A", "Event B"],
                "subscribed_group_ids": [test_group.id],
                "unselected_event_ids": []
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert create_response.status_code == 201
        filter_id = create_response.json()["id"]

        # Update only groups (not events)
        update_response = test_client.put(
            f"/api/domains/{test_domain.domain_key}/filters/{filter_id}",
            json={
                "subscribed_group_ids": []  # Remove group subscription
                # NOTE: subscribed_event_ids not sent - should preserve
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert update_response.status_code == 200
        updated_filter = update_response.json()

        # Verify individual events preserved, groups updated
        assert len(updated_filter["subscribed_event_ids"]) == 2
        assert updated_filter["subscribed_event_ids"] == ["Event A", "Event B"]
        assert updated_filter["subscribed_group_ids"] == []

    def test_update_all_fields_at_once(
        self, test_client: TestClient, test_domain: Domain
    ):
        """
        Test that updating all fields at once works correctly.
        """
        # Create filter
        create_response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/filters",
            json={
                "name": "Original",
                "subscribed_event_ids": ["A", "B", "C"],
                "subscribed_group_ids": [1, 2],
                "unselected_event_ids": ["X"]
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert create_response.status_code == 201
        filter_id = create_response.json()["id"]

        # Update everything
        update_response = test_client.put(
            f"/api/domains/{test_domain.domain_key}/filters/{filter_id}",
            json={
                "name": "Updated",
                "subscribed_event_ids": ["D", "E"],
                "subscribed_group_ids": [3],
                "unselected_event_ids": ["Y", "Z"]
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert update_response.status_code == 200
        updated_filter = update_response.json()

        # Verify all fields updated
        assert updated_filter["name"] == "Updated"
        assert updated_filter["subscribed_event_ids"] == ["D", "E"]
        assert updated_filter["subscribed_group_ids"] == [3]
        assert updated_filter["unselected_event_ids"] == ["Y", "Z"]
