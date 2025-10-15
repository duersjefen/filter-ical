"""
Test suite for domain configuration export/import functionality.

Tests the complete round-trip workflow:
1. Export domain configuration as YAML
2. Import the exported YAML back
3. Verify data integrity

Addresses bug: "Failed to import configuration: Missing required section: 'domain'"
"""

import pytest
import yaml
from io import BytesIO
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.domain import Domain
from app.models.calendar import Group, RecurringEventGroup, AssignmentRule


class TestDomainConfigImportMultipart:
    """Test domain configuration import via multipart/form-data (bug fix verification)."""

    def test_import_yaml_with_all_required_sections_succeeds(self, test_client: TestClient, test_domain: Domain, test_db: Session):
        """Import YAML file uploaded as multipart/form-data with all required sections."""
        # Create valid YAML configuration with all required sections
        valid_config = {
            "domain": {
                "name": "Test Domain",
                "calendar_url": "https://example.com/test.ics",
                "description": "Test configuration"
            },
            "groups": [
                {
                    "id": "group_1",
                    "name": "Test Group",
                    "description": "A test group"
                }
            ],
            "assignments": {
                "group_1": ["Event 1", "Event 2"]
            },
            "rules": [
                {
                    "rule_type": "title_contains",
                    "rule_value": "test",
                    "target_group_id": "group_1"
                }
            ],
            "metadata": {
                "version": "1.0"
            }
        }

        yaml_content = yaml.dump(valid_config, default_flow_style=False, allow_unicode=True)

        # Upload as multipart/form-data (simulating frontend behavior)
        files = {
            "config_file": ("test_config.yaml", BytesIO(yaml_content.encode('utf-8')), "application/x-yaml")
        }

        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/import-config",
            files=files
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
        result = response.json()
        assert result["success"] is True

        # Verify data was imported
        groups = test_db.query(Group).filter(Group.domain_key == test_domain.domain_key).all()
        assert len(groups) == 1
        assert groups[0].name == "Test Group"

    def test_import_yaml_missing_domain_section_fails(self, test_client: TestClient, test_domain: Domain):
        """Import fails with clear error when 'domain' section is missing (original bug)."""
        # This is the bug: YAML without 'domain' section should fail gracefully
        invalid_config = {
            "groups": [],
            "assignments": {},
            "rules": []
        }

        yaml_content = yaml.dump(invalid_config, default_flow_style=False)

        files = {
            "config_file": ("invalid.yaml", BytesIO(yaml_content.encode('utf-8')), "application/x-yaml")
        }

        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/import-config",
            files=files
        )

        assert response.status_code == 400
        error_data = response.json()
        assert "domain" in error_data["detail"].lower()

    def test_import_yaml_invalid_syntax_fails(self, test_client: TestClient, test_domain: Domain):
        """Import fails gracefully with invalid YAML syntax."""
        invalid_yaml = b"this is not: valid: yaml: syntax::"

        files = {
            "config_file": ("invalid.yaml", BytesIO(invalid_yaml), "application/x-yaml")
        }

        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/import-config",
            files=files
        )

        assert response.status_code == 400
        error_data = response.json()
        assert "yaml" in error_data["detail"].lower()

    def test_import_json_backward_compatibility(self, test_client: TestClient, test_domain: Domain, test_db: Session):
        """Import configuration sent as JSON (backward compatibility)."""
        valid_config = {
            "domain": {
                "name": "Test Domain",
                "calendar_url": "https://example.com/test.ics"
            },
            "groups": [
                {
                    "id": "json_group",
                    "name": "JSON Group"
                }
            ],
            "assignments": {
                "json_group": ["JSON Event"]
            },
            "rules": []
        }

        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/import-config",
            json=valid_config
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_import_yaml_as_raw_body(self, test_client: TestClient, test_domain: Domain, test_db: Session):
        """Import YAML sent as raw request body with Content-Type: application/x-yaml."""
        valid_config = {
            "domain": {
                "name": "Test Domain",
                "calendar_url": "https://example.com/test.ics"
            },
            "groups": [
                {
                    "id": "raw_group",
                    "name": "Raw YAML Group"
                }
            ],
            "assignments": {
                "raw_group": ["Raw Event"]
            },
            "rules": []
        }

        yaml_content = yaml.dump(valid_config, default_flow_style=False, allow_unicode=True)

        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/import-config",
            content=yaml_content.encode('utf-8'),
            headers={"Content-Type": "application/x-yaml"}
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_import_yaml_without_metadata_succeeds(self, test_client: TestClient, test_domain: Domain, test_db: Session):
        """Import succeeds even without metadata section (metadata is optional, generated by export)."""
        # This is a regression test for the bug where load_domain_configuration
        # required 'metadata' but import_domain_configuration didn't
        config_without_metadata = {
            "domain": {
                "name": "Test Domain",
                "calendar_url": "https://example.com/test.ics",
                "description": "Test configuration"
            },
            "groups": [
                {
                    "id": "test_group",
                    "name": "Test Group",
                    "description": "A test group"
                }
            ],
            "assignments": {
                "test_group": ["Event 1"]
            },
            "rules": []
            # Note: NO metadata section - should still work
        }

        yaml_content = yaml.dump(config_without_metadata, default_flow_style=False, allow_unicode=True)

        files = {
            "config_file": ("config.yaml", BytesIO(yaml_content.encode('utf-8')), "application/x-yaml")
        }

        response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/import-config",
            files=files
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
        result = response.json()
        assert result["success"] is True

        # Verify data was imported
        groups = test_db.query(Group).filter(Group.domain_key == test_domain.domain_key).all()
        assert len(groups) == 1
        assert groups[0].name == "Test Group"

class TestExportImportRoundTrip:
    """Test complete export → re-import workflow (critical user workflow)."""

    def test_export_then_import_yaml_file(self, test_client: TestClient, test_domain: Domain, test_db: Session):
        """
        Export configuration to YAML file, then import it back.
        This is the exact workflow users follow in the UI.

        Reproduces bug: "Failed to import configuration: Missing required section: 'domain'"
        """
        # Setup: Create some test data in database
        group = Group(
            domain_key=test_domain.domain_key,
            name="Test Export Group"
        )
        test_db.add(group)
        test_db.commit()
        test_db.refresh(group)

        # Create an assignment
        assignment = RecurringEventGroup(
            domain_key=test_domain.domain_key,
            recurring_event_title="Test Event",
            group_id=group.id
        )
        test_db.add(assignment)
        test_db.commit()

        # Step 1: Export configuration as YAML (what user downloads)
        export_response = test_client.get(
            f"/api/domains/{test_domain.domain_key}/export-config",
            headers={"Accept": "application/x-yaml"}
        )

        assert export_response.status_code == 200, f"Export failed: {export_response.text}"
        yaml_content = export_response.content

        # Verify it's valid YAML
        exported_config = yaml.safe_load(yaml_content)
        assert exported_config is not None, "Exported YAML is empty"
        assert "domain" in exported_config, "Exported YAML missing 'domain' section"
        assert "groups" in exported_config, "Exported YAML missing 'groups' section"
        assert "assignments" in exported_config, "Exported YAML missing 'assignments' section"
        assert "rules" in exported_config, "Exported YAML missing 'rules' section"

        # Step 2: Clear database (simulate import to fresh state)
        test_db.query(RecurringEventGroup).filter(
            RecurringEventGroup.domain_key == test_domain.domain_key
        ).delete()
        test_db.query(Group).filter(Group.domain_key == test_domain.domain_key).delete()
        test_db.commit()

        # Verify database is empty
        groups_before = test_db.query(Group).filter(Group.domain_key == test_domain.domain_key).all()
        assert len(groups_before) == 0, "Database should be empty before import"

        # Step 3: Import the exported YAML file (what user uploads)
        files = {
            "config_file": ("export.yaml", BytesIO(yaml_content), "application/x-yaml")
        }

        import_response = test_client.post(
            f"/api/domains/{test_domain.domain_key}/import-config",
            files=files
        )

        # This should succeed but currently fails with "Missing required section: 'domain'"
        assert import_response.status_code == 200, \
            f"Import failed with status {import_response.status_code}: {import_response.json()}"

        result = import_response.json()
        assert result["success"] is True, f"Import failed: {result}"

        # Step 4: Verify data was restored
        groups_after = test_db.query(Group).filter(Group.domain_key == test_domain.domain_key).all()
        assert len(groups_after) == 1, f"Expected 1 group after import, got {len(groups_after)}"
        assert groups_after[0].name == "Test Export Group"

        assignments_after = test_db.query(RecurringEventGroup).filter(
            RecurringEventGroup.domain_key == test_domain.domain_key
        ).all()
        assert len(assignments_after) == 1, f"Expected 1 assignment after import, got {len(assignments_after)}"
        assert assignments_after[0].recurring_event_title == "Test Event"
