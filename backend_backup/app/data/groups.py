"""
Community Groups & Categories - Pure functions for group management
Auto-assignment rules and subscription logic
"""

import uuid
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime


def create_default_groups() -> List[Dict[str, Any]]:
    """Create default groups for BCC Exter community"""
    now = datetime.utcnow().isoformat()
    
    return [
        {
            "id": "football",
            "community_id": "exter",
            "name": "Football",
            "description": "All football-related events and activities",
            "icon": "⚽",
            "color": "#22C55E",  # Green
            "assignment_rules": [
                "football", "fußball", "voetbal", "soccer", 
                "mannschaft", "team", "match", "training"
            ],
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "youth",
            "community_id": "exter",
            "name": "Youth & Children",
            "description": "Youth events, children's activities and junior teams",
            "icon": "👦",
            "color": "#3B82F6",  # Blue
            "assignment_rules": [
                "youth", "jugend", "jeugd", "children", "kinder",
                "junior", "u16", "u19", "u21", "bambini", "mädchen", "girls"
            ],
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "events",
            "community_id": "exter",
            "name": "General Events",
            "description": "Community events, social gatherings and general activities",
            "icon": "🎉",
            "color": "#F59E0B",  # Orange
            "assignment_rules": [
                "event", "feier", "party", "social", "community",
                "meeting", "versammlung", "gathering", "celebration"
            ],
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "deutschland",
            "community_id": "exter",
            "name": "Deutschland",
            "description": "German national team and Deutschland events",
            "icon": "🇩🇪",
            "color": "#EF4444",  # Red
            "assignment_rules": [
                "deutschland", "germany", "national", "dfb",
                "german", "deutsch", "nationalmannschaft"
            ],
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "all_categories",
            "community_id": "exter",
            "name": "All Categories",
            "description": "View and manage all event categories individually",
            "icon": "📋",
            "color": "#6B7280",  # Gray
            "assignment_rules": [],  # No auto-assignment, manual management
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
    ]


def normalize_text_for_matching(text: str) -> str:
    """Normalize text for category matching"""
    if not text:
        return ""
    
    # Convert to lowercase and remove special characters
    normalized = re.sub(r'[^a-zA-Z0-9äöüß\s]', '', text.lower())
    # Replace umlauts
    normalized = normalized.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    return normalized


def find_matching_groups(category_name: str, groups: List[Dict[str, Any]]) -> List[str]:
    """Find groups that match a category name based on assignment rules"""
    if not category_name:
        return []
    
    normalized_category = normalize_text_for_matching(category_name)
    matching_groups = []
    
    for group in groups:
        if not group.get("assignment_rules"):
            continue
            
        for rule in group["assignment_rules"]:
            normalized_rule = normalize_text_for_matching(rule)
            if normalized_rule and normalized_rule in normalized_category:
                matching_groups.append(group["id"])
                break  # One match per group is enough
    
    return matching_groups


def create_category_assignments(category_name: str, community_id: str, 
                               matching_group_ids: List[str]) -> List[Dict[str, Any]]:
    """Create category assignment records for matching groups"""
    assignments = []
    now = datetime.utcnow().isoformat()
    
    for group_id in matching_group_ids:
        assignment = {
            "id": str(uuid.uuid4()),
            "community_id": community_id,
            "group_id": group_id,
            "category_name": category_name,
            "assignment_type": "auto",
            "assigned_by": None,
            "assigned_at": now,
            "is_active": True
        }
        assignments.append(assignment)
    
    return assignments


def auto_assign_category_to_groups(category_name: str, community_id: str, 
                                 existing_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Auto-assign a category to appropriate groups based on rules"""
    if not category_name or not existing_groups:
        return []
    
    # Find matching groups
    matching_group_ids = find_matching_groups(category_name, existing_groups)
    
    # If no specific matches, assign to "All Categories" group
    if not matching_group_ids:
        all_categories_group = next((g for g in existing_groups if g["id"] == "all_categories"), None)
        if all_categories_group:
            matching_group_ids = ["all_categories"]
    
    # Create assignments
    return create_category_assignments(category_name, community_id, matching_group_ids)


def create_default_subscription(user_id: str, community_id: str, 
                               available_groups: List[str]) -> Dict[str, Any]:
    """Create default subscription for new community user"""
    now = datetime.utcnow().isoformat()
    
    # By default, subscribe to main groups but not youth (as example)
    default_subscribed_groups = []
    for group_id in available_groups:
        if group_id not in ["youth", "all_categories"]:  # Don't auto-subscribe to youth
            default_subscribed_groups.append(group_id)
    
    return {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "community_id": community_id,
        "subscribed_groups": default_subscribed_groups,
        "explicitly_subscribed_categories": [],
        "explicitly_unsubscribed_categories": [],
        "filter_mode": "include",  # Default to include mode
        "personal_token": str(uuid.uuid4()),
        "created_at": now,
        "updated_at": now,
        "last_accessed": now
    }


def calculate_user_categories(subscription: Dict[str, Any], 
                             category_assignments: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """Calculate which categories a user should receive based on their subscription"""
    if not subscription:
        return [], []
    
    included_categories = set()
    excluded_categories = set()
    
    # Add explicitly subscribed categories
    included_categories.update(subscription.get("explicitly_subscribed_categories", []))
    
    # Add explicitly unsubscribed categories to exclusion list
    excluded_categories.update(subscription.get("explicitly_unsubscribed_categories", []))
    
    # Add categories from subscribed groups
    subscribed_groups = subscription.get("subscribed_groups", [])
    for assignment in category_assignments:
        if assignment["group_id"] in subscribed_groups and assignment["is_active"]:
            category = assignment["category_name"]
            
            # Only include if not explicitly unsubscribed
            if category not in excluded_categories:
                included_categories.add(category)
    
    # Handle filter mode
    filter_mode = subscription.get("filter_mode", "include")
    
    if filter_mode == "include":
        # Include mode: only include specified categories
        return list(included_categories), []
    else:
        # Exclude mode: include all except excluded categories
        return [], list(excluded_categories)


def get_categories_from_events(events: List[Dict[str, Any]]) -> List[str]:
    """Extract unique category names from events"""
    categories = set()
    
    for event in events:
        # Events might have categories in different fields
        category = event.get("category") or event.get("categories") or event.get("summary", "").split("-")[0].strip()
        if category and category != "Unknown":
            categories.add(category)
    
    return sorted(list(categories))


def update_subscription_categories(subscription: Dict[str, Any], 
                                 category_updates: Dict[str, str]) -> Dict[str, Any]:
    """Update user subscription with category changes"""
    updated_subscription = subscription.copy()
    now = datetime.utcnow().isoformat()
    
    explicitly_subscribed = set(updated_subscription.get("explicitly_subscribed_categories", []))
    explicitly_unsubscribed = set(updated_subscription.get("explicitly_unsubscribed_categories", []))
    
    for category, action in category_updates.items():
        if action == "subscribe":
            explicitly_subscribed.add(category)
            explicitly_unsubscribed.discard(category)  # Remove from unsubscribed if present
        elif action == "unsubscribe":
            explicitly_unsubscribed.add(category)
            explicitly_subscribed.discard(category)  # Remove from subscribed if present
        elif action == "reset":
            # Reset to group-based subscription
            explicitly_subscribed.discard(category)
            explicitly_unsubscribed.discard(category)
    
    updated_subscription["explicitly_subscribed_categories"] = list(explicitly_subscribed)
    updated_subscription["explicitly_unsubscribed_categories"] = list(explicitly_unsubscribed)
    updated_subscription["updated_at"] = now
    
    return updated_subscription