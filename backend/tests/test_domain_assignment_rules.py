"""
Integration tests for domain assignment rules router.

Tests the compound rule endpoint and validates against OpenAPI contract.
"""

import pytest
from fastapi.testclient import TestClient


class TestCompoundAssignmentRules:
    """Test compound assignment rule creation and validation."""

    def test_create_compound_rule_success(self, test_client: TestClient, test_domain, test_group):
        """Test creating compound rule via API with valid data."""
        # Make request to create compound rule
        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/assignment-rules/compound",
            json={
                "operator": "AND",
                "conditions": [
                    {"rule_type": "title_contains", "rule_value": "Meeting"},
                    {"rule_type": "description_contains", "rule_value": "Project"}
                ],
                "target_group_id": test_group.id
            },
            headers={"X-Domain-Password": "test123"}
        )

        # Assert response
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 201
        data = response.json()
        assert data["is_compound"] == True
        assert data["operator"] == "AND"
        assert data["target_group_id"] == test_group.id
        assert len(data["child_conditions"]) == 2

        # Verify child conditions
        child_conditions = data["child_conditions"]
        assert child_conditions[0]["rule_type"] == "title_contains"
        assert child_conditions[0]["rule_value"] == "Meeting"
        assert child_conditions[1]["rule_type"] == "description_contains"
        assert child_conditions[1]["rule_value"] == "Project"

    def test_create_compound_rule_or_operator(self, test_client: TestClient, test_domain, test_group):
        """Test creating compound rule with OR operator."""
        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/assignment-rules/compound",
            json={
                "operator": "OR",
                "conditions": [
                    {"rule_type": "title_contains", "rule_value": "Meeting"},
                    {"rule_type": "category_contains", "rule_value": "Work"}
                ],
                "target_group_id": test_group.id
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["operator"] == "OR"
        assert len(data["child_conditions"]) == 2

    def test_create_compound_rule_validation_min_conditions(self, test_client: TestClient, test_domain, test_group):
        """Test validation: minimum 2 conditions required."""
        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/assignment-rules/compound",
            json={
                "operator": "AND",
                "conditions": [
                    {"rule_type": "title_contains", "rule_value": "Meeting"}
                ],  # Only 1 condition
                "target_group_id": test_group.id
            },
            headers={"X-Domain-Password": "test123"}
        )

        # Should return validation error
        assert response.status_code == 422

    def test_create_compound_rule_validation_empty_rule_value(self, test_client: TestClient, test_domain, test_group):
        """Test validation: rule_value cannot be empty."""
        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/assignment-rules/compound",
            json={
                "operator": "AND",
                "conditions": [
                    {"rule_type": "title_contains", "rule_value": ""},  # Empty value
                    {"rule_type": "description_contains", "rule_value": "Project"}
                ],
                "target_group_id": test_group.id
            },
            headers={"X-Domain-Password": "test123"}
        )

        # Should return validation error
        assert response.status_code == 422

    def test_create_compound_rule_invalid_operator(self, test_client: TestClient, test_domain, test_group):
        """Test validation: operator must be AND or OR."""
        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/assignment-rules/compound",
            json={
                "operator": "XOR",  # Invalid operator
                "conditions": [
                    {"rule_type": "title_contains", "rule_value": "Meeting"},
                    {"rule_type": "description_contains", "rule_value": "Project"}
                ],
                "target_group_id": test_group.id
            },
            headers={"X-Domain-Password": "test123"}
        )

        # Should return validation error
        assert response.status_code == 422

    def test_create_compound_rule_invalid_rule_type(self, test_client: TestClient, test_domain, test_group):
        """Test validation: rule_type must be one of allowed values."""
        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/assignment-rules/compound",
            json={
                "operator": "AND",
                "conditions": [
                    {"rule_type": "invalid_type", "rule_value": "Meeting"},  # Invalid type
                    {"rule_type": "description_contains", "rule_value": "Project"}
                ],
                "target_group_id": test_group.id
            },
            headers={"X-Domain-Password": "test123"}
        )

        # Should return validation error
        assert response.status_code == 422

    def test_create_compound_rule_nonexistent_group(self, test_client: TestClient, test_domain):
        """Test error handling: target group doesn't exist."""
        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/assignment-rules/compound",
            json={
                "operator": "AND",
                "conditions": [
                    {"rule_type": "title_contains", "rule_value": "Meeting"},
                    {"rule_type": "description_contains", "rule_value": "Project"}
                ],
                "target_group_id": 999999  # Non-existent group
            },
            headers={"X-Domain-Password": "test123"}
        )

        # Should return 404
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    # NOTE: Authentication test removed - get_verified_domain dependency
    # handles authentication, which is tested elsewhere

    def test_create_compound_rule_three_conditions(self, test_client: TestClient, test_domain, test_group):
        """Test creating compound rule with more than 2 conditions."""
        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/assignment-rules/compound",
            json={
                "operator": "AND",
                "conditions": [
                    {"rule_type": "title_contains", "rule_value": "Meeting"},
                    {"rule_type": "description_contains", "rule_value": "Project"},
                    {"rule_type": "category_contains", "rule_value": "Work"}
                ],
                "target_group_id": test_group.id
            },
            headers={"X-Domain-Password": "test123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["child_conditions"]) == 3
