"""
DynamoDB database module for Filter iCal.

This module provides a clean abstraction over DynamoDB using single-table design.
"""

from .dynamodb import get_table, get_client
from .repository import Repository
from .models import (
    Domain,
    DomainGroup,
    AssignmentRule,
    Event,
    Filter,
    Admin,
)

__all__ = [
    "get_table",
    "get_client",
    "Repository",
    "Domain",
    "DomainGroup",
    "AssignmentRule",
    "Event",
    "Filter",
    "Admin",
]
