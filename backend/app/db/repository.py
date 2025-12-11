"""
Repository layer for DynamoDB operations.

Provides a clean interface for CRUD operations on all document types.
Services should use this instead of direct DynamoDB calls.
"""

from datetime import datetime
from typing import Optional
import uuid as uuid_lib

from .dynamodb import (
    get_item,
    put_item,
    delete_item,
    update_item,
    query_by_pk,
    query_by_gsi,
    batch_write,
    batch_delete,
    domain_pk,
    filter_pk,
    admin_pk,
    metadata_sk,
    event_sk,
)
from .models import Domain, Event, Filter, Admin, DomainGroup, AssignmentRule


class Repository:
    """
    Repository for all DynamoDB operations.

    Usage:
        repo = Repository()
        domain = repo.get_domain("exter")
        repo.save_domain(domain)
    """

    # =========================================================================
    # Domain operations
    # =========================================================================

    def get_domain(self, domain_key: str) -> Optional[Domain]:
        """Get domain by key."""
        item = get_item(domain_pk(domain_key), metadata_sk())
        if not item:
            return None
        return Domain.from_dynamo_item(item)

    def save_domain(self, domain: Domain) -> Domain:
        """Save (create or update) a domain."""
        domain.updated_at = datetime.utcnow()
        put_item(domain.to_dynamo_item())
        return domain

    def delete_domain(self, domain_key: str) -> bool:
        """Delete domain and all its events."""
        # Delete events first
        events = query_by_pk(domain_pk(domain_key), "EVENT#")
        if events:
            keys = [(e["PK"], e["SK"]) for e in events]
            batch_delete(keys)

        # Delete domain metadata
        return delete_item(domain_pk(domain_key), metadata_sk())

    def list_domains(self) -> list[Domain]:
        """List all domains (scans table - use sparingly)."""
        # Note: In production, you might want to use a GSI for this
        from .dynamodb import get_table
        table = get_table()
        response = table.scan(
            FilterExpression="begins_with(PK, :pk) AND SK = :sk",
            ExpressionAttributeValues={":pk": "DOMAIN#", ":sk": "METADATA"}
        )
        return [Domain.from_dynamo_item(item) for item in response.get("Items", [])]

    # =========================================================================
    # Group operations (within domain)
    # =========================================================================

    def add_group(self, domain_key: str, name: str) -> Optional[DomainGroup]:
        """Add a group to a domain."""
        domain = self.get_domain(domain_key)
        if not domain:
            return None

        # Generate ID (max existing + 1)
        max_id = max([g.id for g in domain.groups], default=0)
        group = DomainGroup(id=max_id + 1, name=name)
        domain.groups.append(group)
        self.save_domain(domain)
        return group

    def update_group(self, domain_key: str, group_id: int, name: str) -> Optional[DomainGroup]:
        """Update a group name."""
        domain = self.get_domain(domain_key)
        if not domain:
            return None

        for group in domain.groups:
            if group.id == group_id:
                group.name = name
                group.updated_at = datetime.utcnow()
                self.save_domain(domain)
                return group
        return None

    def delete_group(self, domain_key: str, group_id: int) -> bool:
        """Delete a group from a domain."""
        domain = self.get_domain(domain_key)
        if not domain:
            return False

        domain.groups = [g for g in domain.groups if g.id != group_id]
        # Remove assignments to this group
        domain.recurring_assignments = {
            k: v for k, v in domain.recurring_assignments.items() if v != group_id
        }
        self.save_domain(domain)
        return True

    # =========================================================================
    # Assignment rule operations (within group)
    # =========================================================================

    def add_rule(
        self,
        domain_key: str,
        group_id: int,
        rule_type: str,
        rule_value: str
    ) -> Optional[AssignmentRule]:
        """Add a simple assignment rule to a group."""
        domain = self.get_domain(domain_key)
        if not domain:
            return None

        for group in domain.groups:
            if group.id == group_id:
                max_id = max([r.id for r in group.rules], default=0)
                rule = AssignmentRule(
                    id=max_id + 1,
                    type=rule_type,
                    value=rule_value,
                    is_compound=False
                )
                group.rules.append(rule)
                group.updated_at = datetime.utcnow()
                self.save_domain(domain)
                return rule
        return None

    def delete_rule(self, domain_key: str, group_id: int, rule_id: int) -> bool:
        """Delete an assignment rule from a group."""
        domain = self.get_domain(domain_key)
        if not domain:
            return False

        for group in domain.groups:
            if group.id == group_id:
                group.rules = [r for r in group.rules if r.id != rule_id]
                group.updated_at = datetime.utcnow()
                self.save_domain(domain)
                return True
        return False

    # =========================================================================
    # Recurring assignment operations
    # =========================================================================

    def assign_event_to_group(
        self,
        domain_key: str,
        event_title: str,
        group_id: int
    ) -> bool:
        """Assign a recurring event title to a group."""
        domain = self.get_domain(domain_key)
        if not domain:
            return False

        domain.recurring_assignments[event_title] = group_id
        self.save_domain(domain)
        return True

    def unassign_event(self, domain_key: str, event_title: str) -> bool:
        """Remove a recurring event assignment."""
        domain = self.get_domain(domain_key)
        if not domain:
            return False

        if event_title in domain.recurring_assignments:
            del domain.recurring_assignments[event_title]
            self.save_domain(domain)
        return True

    # =========================================================================
    # Event operations
    # =========================================================================

    def get_events(self, domain_key: str) -> list[Event]:
        """Get all events for a domain."""
        items = query_by_pk(domain_pk(domain_key), "EVENT#")
        return [Event.from_dynamo_item(item) for item in items]

    def save_event(self, event: Event) -> Event:
        """Save (create or update) an event."""
        event.updated_at = datetime.utcnow()
        put_item(event.to_dynamo_item())
        return event

    def save_events(self, events: list[Event]) -> list[Event]:
        """Batch save multiple events."""
        now = datetime.utcnow()
        for event in events:
            event.updated_at = now
        items = [e.to_dynamo_item() for e in events]
        batch_write(items)
        return events

    def delete_event(self, domain_key: str, start_date: str, uid: str) -> bool:
        """Delete an event."""
        return delete_item(domain_pk(domain_key), event_sk(start_date, uid))

    def delete_all_events(self, domain_key: str) -> int:
        """Delete all events for a domain."""
        items = query_by_pk(domain_pk(domain_key), "EVENT#")
        if items:
            keys = [(item["PK"], item["SK"]) for item in items]
            batch_delete(keys)
        return len(items)

    # =========================================================================
    # Filter operations
    # =========================================================================

    def get_filter(self, link_uuid: str) -> Optional[Filter]:
        """Get filter by link UUID."""
        item = get_item(filter_pk(link_uuid), metadata_sk())
        if not item:
            return None
        return Filter.from_dynamo_item(item)

    def get_filter_by_uuid(self, link_uuid: str) -> Optional[Filter]:
        """Get filter by link UUID (using GSI if UUID format differs)."""
        # First try direct lookup
        filter_obj = self.get_filter(link_uuid)
        if filter_obj:
            return filter_obj

        # Try GSI lookup (for legacy UUIDs)
        items = query_by_gsi("LinkUuidIndex", "link_uuid", link_uuid)
        if items:
            return Filter.from_dynamo_item(items[0])
        return None

    def save_filter(self, filter_obj: Filter) -> Filter:
        """Save (create or update) a filter."""
        filter_obj.updated_at = datetime.utcnow()
        put_item(filter_obj.to_dynamo_item())
        return filter_obj

    def create_filter(self, domain_key: str, **kwargs) -> Filter:
        """Create a new filter with auto-generated UUID."""
        link_uuid = str(uuid_lib.uuid4())
        filter_obj = Filter(link_uuid=link_uuid, domain_key=domain_key, **kwargs)
        return self.save_filter(filter_obj)

    def delete_filter(self, link_uuid: str) -> bool:
        """Delete a filter."""
        return delete_item(filter_pk(link_uuid), metadata_sk())

    def list_filters_for_domain(self, domain_key: str) -> list[Filter]:
        """List all filters for a domain (scans - use sparingly)."""
        from .dynamodb import get_table
        table = get_table()
        response = table.scan(
            FilterExpression="begins_with(PK, :pk) AND domain_key = :dk",
            ExpressionAttributeValues={":pk": "FILTER#", ":dk": domain_key}
        )
        return [Filter.from_dynamo_item(item) for item in response.get("Items", [])]

    # =========================================================================
    # Admin operations
    # =========================================================================

    def get_admin(self, email: str) -> Optional[Admin]:
        """Get admin by email."""
        item = get_item(admin_pk(email), metadata_sk())
        if not item:
            return None
        return Admin.from_dynamo_item(item)

    def save_admin(self, admin: Admin) -> Admin:
        """Save (create or update) an admin."""
        admin.updated_at = datetime.utcnow()
        put_item(admin.to_dynamo_item())
        return admin

    def delete_admin(self, email: str) -> bool:
        """Delete an admin."""
        return delete_item(admin_pk(email), metadata_sk())

    def get_admin_by_reset_token(self, token: str) -> Optional[Admin]:
        """Find admin by reset token (scans - acceptable for rare operation)."""
        from .dynamodb import get_table
        table = get_table()
        response = table.scan(
            FilterExpression="begins_with(PK, :pk) AND reset_token = :token",
            ExpressionAttributeValues={":pk": "ADMIN#", ":token": token}
        )
        items = response.get("Items", [])
        if items:
            return Admin.from_dynamo_item(items[0])
        return None

    def set_admin_reset_token(
        self,
        email: str,
        token: str,
        expires: datetime
    ) -> Optional[Admin]:
        """Set password reset token for admin."""
        admin = self.get_admin(email)
        if not admin:
            return None

        admin.reset_token = token
        admin.reset_token_expires = expires
        return self.save_admin(admin)

    def clear_admin_reset_token(self, email: str) -> Optional[Admin]:
        """Clear password reset token after use."""
        admin = self.get_admin(email)
        if not admin:
            return None

        admin.reset_token = None
        admin.reset_token_expires = None
        return self.save_admin(admin)


# Singleton instance for convenience
_repository: Optional[Repository] = None


def get_repository() -> Repository:
    """Get singleton repository instance."""
    global _repository
    if _repository is None:
        _repository = Repository()
    return _repository
