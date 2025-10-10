"""
Domain assignment rules router for auto-assignment management.

Implements assignment rule endpoints from OpenAPI specification.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.error_handlers import handle_endpoint_errors
from ..core.auth import get_verified_domain
from ..models.domain import Domain
from ..services.domain_service import (
    create_assignment_rule, get_assignment_rules,
    auto_assign_events_with_rules, delete_assignment_rule
)

router = APIRouter()


@router.post("/{domain}/assignment-rules")
@handle_endpoint_errors
async def create_domain_assignment_rule(
    domain_obj: Domain = Depends(get_verified_domain),
    rule_data: dict = None,
    db: Session = Depends(get_db)
):
    """Create auto-assignment rule (admin)."""
    # Validate required fields
    required_fields = ["rule_type", "rule_value", "target_group_id"]
    for field in required_fields:
        if field not in rule_data:
            raise HTTPException(status_code=400, detail=f"{field} is required")

    # Create assignment rule
    success, rule, error = create_assignment_rule(
        db, domain_obj.domain_key,
        rule_data["rule_type"],
        rule_data["rule_value"],
        rule_data["target_group_id"]
    )
    if not success:
        raise HTTPException(status_code=400, detail=error)

    # Return rule data matching OpenAPI schema
    return {
        "id": rule.id,
        "rule_type": rule.rule_type,
        "rule_value": rule.rule_value,
        "target_group_id": rule.target_group_id
    }


@router.get("/{domain}/assignment-rules")
@handle_endpoint_errors
async def get_domain_assignment_rules(
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """List assignment rules for domain."""
    # Get assignment rules
    rules = get_assignment_rules(db, domain_obj.domain_key)

    # Transform to OpenAPI schema format
    rules_response = []
    for rule in rules:
        rules_response.append({
            "id": rule.id,
            "rule_type": rule.rule_type,
            "rule_value": rule.rule_value,
            "target_group_id": rule.target_group_id
        })

    return rules_response


@router.post("/{domain}/assignment-rules/apply")
@handle_endpoint_errors
async def apply_domain_assignment_rules(
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Manually trigger assignment rules to be applied to all events (admin)."""
    # Apply assignment rules
    success, assignment_count, error = await auto_assign_events_with_rules(db, domain_obj.domain_key)
    if not success:
        raise HTTPException(status_code=500, detail=f"Rule application failed: {error}")

    return {
        "success": True,
        "message": f"Applied assignment rules to {assignment_count} events",
        "assignment_count": assignment_count
    }


@router.delete("/{domain}/assignment-rules/{rule_id}")
@handle_endpoint_errors
async def delete_domain_assignment_rule(
    rule_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Delete assignment rule (admin)."""
    # Delete rule
    success, error = delete_assignment_rule(db, rule_id, domain_obj.domain_key)
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)

    # Return 204 No Content on successful deletion
    return None
