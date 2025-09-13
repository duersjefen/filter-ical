"""
Filter Service - Business logic for filter operations
Handles filter management and event filtering
"""

from typing import List, Dict, Any
from ..storage.persistence import PersistentStore


class FilterService:
    """Business logic for filter operations"""
    
    def __init__(self, store: PersistentStore):
        self.store = store
    
    def get_filters(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all filters for a user"""
        return self.store.get_filters(user_id)
    
    def create_filter(self, name: str, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new filter"""
        return self.store.add_filter(name, config, user_id)
    
    def delete_filter(self, filter_id: str, user_id: str) -> bool:
        """Delete a filter"""
        return self.store.delete_filter(filter_id, user_id)