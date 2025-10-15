"""
Domain assignment rules router for auto-assignment management.

Implements assignment rule endpoints from OpenAPI specification.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Literal

from ..core.database import get_db
from ..core.error_handlers import handle_endpoint_errors
from ..core.auth import get_verified_domain
from ..models.domain import Domain
from ..models.calendar import Group, AssignmentRule
from ..services.domain_service import (
    create_assignment_rule, get_assignment_rules,
    auto_assign_events_with_rules, delete_assignment_rule
)

router = APIRouter()


# Pydantic models for compound rule endpoint
class CompoundRuleCondition(BaseModel):
    """
    Individual condition within a compound rule.

    Supports both positive (contains) and negative (not_contains) matching.
    """
    rule_type: Literal[
        'title_contains', 'title_not_contains',
        'description_contains', 'description_not_contains',
        'category_contains', 'category_not_contains'
    ]
    rule_value: str = Field(min_length=1)


class CompoundRuleCreate(BaseModel):
    """Request body for creating a compound assignment rule."""
    operator: Literal['AND']  # Only AND operator (KISS)
    conditions: List[CompoundRuleCondition] = Field(min_items=2)
    target_group_id: int


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

    # AUTO-APPLY: Apply the newly created rule to matching events
    apply_success, assignment_count, apply_error = await auto_assign_events_with_rules(
        db, domain_obj.domain_key
    )

    # Note: We don't fail the rule creation if application fails
    # Rule is already created, we just inform the user about application status

    # Return rule data matching OpenAPI schema with application results
    return {
        "id": rule.id,
        "rule_type": rule.rule_type,
        "rule_value": rule.rule_value,
        "target_group_id": rule.target_group_id,
        "auto_applied": apply_success,
        "assignment_count": assignment_count if apply_success else 0,
        "apply_error": apply_error if not apply_success else None
    }


@router.get("/{domain}/assignment-rules")
@handle_endpoint_errors
async def get_domain_assignment_rules(
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """List assignment rules for domain."""
    # Get only parent rules (where parent_rule_id IS NULL)
    parent_rules = db.query(AssignmentRule).filter(
        AssignmentRule.domain_key == domain_obj.domain_key,
        AssignmentRule.parent_rule_id == None
    ).all()

    # Transform to OpenAPI schema format
    rules_response = []
    for rule in parent_rules:
        if rule.is_compound:
            # Fetch child conditions for compound rules
            child_rules = db.query(AssignmentRule).filter(
                AssignmentRule.parent_rule_id == rule.id
            ).all()

            child_conditions = [
                {
                    "rule_type": child.rule_type,
                    "rule_value": child.rule_value
                }
                for child in child_rules
            ]

            rules_response.append({
                "id": rule.id,
                "is_compound": True,
                "operator": rule.operator,
                "child_conditions": child_conditions,
                "target_group_id": rule.target_group_id,
                "rule_type": None,
                "rule_value": None
            })
        else:
            # Simple rule
            rules_response.append({
                "id": rule.id,
                "is_compound": False,
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
    # Domain token verification via get_verified_domain is sufficient for admin operations
    # No need for separate user authentication - domain token proves admin access

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


@router.post("/{domain}/assignment-rules/compound", status_code=201)
@handle_endpoint_errors
async def create_compound_assignment_rule(
    rule_data: CompoundRuleCreate,
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Create a compound assignment rule with multiple conditions."""
    # Validate target group exists
    group = db.query(Group).filter(
        Group.id == rule_data.target_group_id,
        Group.domain_id == domain_obj.id
    ).first()

    if not group:
        raise HTTPException(status_code=404, detail="Target group not found")

    # Create parent rule
    parent_rule = AssignmentRule(
        domain_id=domain_obj.id,
        domain_key=domain_obj.domain_key,
        is_compound=True,
        operator=rule_data.operator,
        target_group_id=rule_data.target_group_id,
        rule_type=None,  # NULL for compound rules
        rule_value=None
    )
    db.add(parent_rule)
    db.flush()  # Get parent_rule.id

    # Create child conditions
    for condition in rule_data.conditions:
        child_rule = AssignmentRule(
            domain_id=domain_obj.id,
            domain_key=domain_obj.domain_key,
            parent_rule_id=parent_rule.id,
            is_compound=False,
            rule_type=condition.rule_type,
            rule_value=condition.rule_value,
            target_group_id=rule_data.target_group_id
        )
        db.add(child_rule)

    db.commit()
    db.refresh(parent_rule)

    # AUTO-APPLY: Apply all rules (including the newly created one)
    apply_success, assignment_count, apply_error = await auto_assign_events_with_rules(
        db, domain_obj.domain_key
    )

    # Return with child_conditions populated (follows OpenAPI schema) + application results
    return {
        "id": parent_rule.id,
        "is_compound": True,
        "operator": parent_rule.operator,
        "target_group_id": parent_rule.target_group_id,
        "child_conditions": [
            {
                "id": child.id,
                "rule_type": child.rule_type,
                "rule_value": child.rule_value
            }
            for child in parent_rule.child_conditions
        ],
        "auto_applied": apply_success,
        "assignment_count": assignment_count if apply_success else 0,
        "apply_error": apply_error if not apply_success else None
    }
