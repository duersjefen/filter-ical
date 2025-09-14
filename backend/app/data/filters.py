"""
Pure Filter Operations - Rich Hickey Style
Pure functions for filter validation and transformation
No side effects, explicit data flow, composable functions
"""

from typing import Dict, List, Any, Tuple


# === FILTER VALIDATION (Pure Functions) ===

def is_valid_filter_data(name: str, config: Dict[str, Any]) -> Tuple[bool, str]:
    """Pure function: validate filter creation data"""
    if not name or not name.strip():
        return False, "Filter name is required"
    
    if not isinstance(config, dict):
        return False, "Filter config must be a dictionary"
    
    # Validate common filter config fields
    valid_filter_keys = {
        'categories', 'selectedEventTypes', 'keywordFilter', 
        'dateRange', 'sortBy', 'sortDirection', 'mode'
    }
    
    # Check for unknown keys (warn but don't fail)
    unknown_keys = set(config.keys()) - valid_filter_keys
    if unknown_keys:
        print(f"Warning: Unknown filter config keys: {unknown_keys}")
    
    return True, "Valid filter data"


def normalize_filter_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Pure function: normalize and sanitize filter configuration"""
    normalized = {}
    
    # Handle categories (should be list)
    if 'categories' in config:
        categories = config['categories']
        if isinstance(categories, list):
            normalized['categories'] = [str(cat).strip() for cat in categories if cat]
        elif isinstance(categories, str):
            normalized['categories'] = [categories.strip()] if categories.strip() else []
        else:
            normalized['categories'] = []
    
    # Handle selectedEventTypes (should be list)
    if 'selectedEventTypes' in config:
        event_types = config['selectedEventTypes']
        if isinstance(event_types, list):
            normalized['selectedEventTypes'] = [str(et).strip() for et in event_types if et]
        else:
            normalized['selectedEventTypes'] = []
    
    # Handle keywordFilter (should be string)
    if 'keywordFilter' in config:
        keyword = config['keywordFilter']
        normalized['keywordFilter'] = str(keyword).strip() if keyword else ""
    
    # Handle dateRange (should be dict with start/end)
    if 'dateRange' in config:
        date_range = config['dateRange']
        if isinstance(date_range, dict):
            normalized['dateRange'] = {
                'start': str(date_range.get('start', '')).strip(),
                'end': str(date_range.get('end', '')).strip()
            }
        else:
            normalized['dateRange'] = {'start': '', 'end': ''}
    
    # Handle sortBy (should be string)
    if 'sortBy' in config:
        sort_by = config['sortBy']
        valid_sort_options = ['date', 'title', 'category']
        normalized['sortBy'] = str(sort_by) if sort_by in valid_sort_options else 'date'
    
    # Handle sortDirection (should be string)
    if 'sortDirection' in config:
        sort_dir = config['sortDirection']
        valid_directions = ['asc', 'desc']
        normalized['sortDirection'] = str(sort_dir) if sort_dir in valid_directions else 'asc'
    
    # Handle mode (should be string)
    if 'mode' in config:
        mode = config['mode']
        valid_modes = ['include', 'exclude']
        normalized['mode'] = str(mode) if mode in valid_modes else 'include'
    
    # Copy any other fields as-is
    for key, value in config.items():
        if key not in normalized:
            normalized[key] = value
    
    return normalized


# === FILTER OPERATIONS (Pure Functions) ===

def filter_to_dict(filter_data: Dict[str, Any]) -> Dict[str, Any]:
    """Pure function: convert filter data to API response format"""
    return {
        "id": filter_data.get("id"),
        "name": filter_data.get("name"),
        "config": filter_data.get("config", {}),
        "user_id": filter_data.get("user_id")
    }


def find_filter_by_id(filters: List[Dict[str, Any]], filter_id: str) -> Dict[str, Any]:
    """Pure function: find filter by ID in list"""
    return next((f for f in filters if f.get("id") == filter_id), None)


def filter_filters_by_user(filters: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
    """Pure function: filter filters for specific user"""
    return [f for f in filters if f.get("user_id") == user_id]


def user_owns_filter(filter_data: Dict[str, Any], user_id: str) -> bool:
    """Pure function: check if user owns filter"""
    return filter_data.get("user_id") == user_id


# === FILTER WORKFLOW FUNCTIONS (Pure Functions) ===

def create_filter_workflow(name: str, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Pure function: Create workflow data for filter creation
    Returns workflow context for imperative shell to execute
    """
    return {
        "action": "create_filter",
        "name": name,
        "config": config,
        "user_id": user_id,
        "steps": [
            "validate_filter_data",
            "normalize_config",
            "add_filter_to_store",
            "return_filter_data"
        ]
    }


def delete_filter_workflow(filter_id: str, user_id: str) -> Dict[str, Any]:
    """
    Pure function: Create workflow data for filter deletion  
    Returns workflow context for imperative shell to execute
    """
    return {
        "action": "delete_filter",
        "filter_id": filter_id,
        "user_id": user_id,
        "steps": [
            "find_filter",
            "verify_user_ownership", 
            "remove_filter_from_store",
            "return_success_status"
        ]
    }


def get_filters_workflow(user_id: str) -> Dict[str, Any]:
    """
    Pure function: Create workflow data for getting user filters
    Returns workflow context for imperative shell to execute
    """
    return {
        "action": "get_filters",
        "user_id": user_id,
        "steps": [
            "get_filters_from_store",
            "filter_by_user",
            "format_for_api",
            "return_filter_list"
        ]
    }