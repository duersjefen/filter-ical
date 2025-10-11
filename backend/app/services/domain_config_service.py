"""
Domain Configuration Service for YAML-based domain management.

This service replaces demo_data.py with a living configuration system
that can export/import domain configurations as portable YAML files.

IMPERATIVE SHELL - Orchestrates pure functions with I/O operations.
"""

import yaml
import re
import unicodedata
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..models.calendar import Calendar, Group, RecurringEventGroup, AssignmentRule
from ..core.config import settings
from ..data.grouping import (
    validate_group_data, validate_assignment_rule_data,
    create_group_data, create_recurring_event_group_data, create_assignment_rule_data
)


def generate_semantic_id(group_name: str, existing_ids: set = None) -> str:
    """
    Generate a semantic ID from group name that matches domain YAML format.
    
    Args:
        group_name: Display name of the group (e.g., "⚽ Fußball")
        existing_ids: Set of existing IDs to avoid conflicts
        
    Returns:
        Semantic ID (e.g., "fussball")
        
    Pure function - deterministic ID generation.
    """
    if existing_ids is None:
        existing_ids = set()
    
    # Remove emojis and special characters
    # First normalize Unicode characters
    normalized = unicodedata.normalize('NFKD', group_name)
    
    # Remove emojis by filtering out emoji Unicode ranges
    no_emoji = ''.join(char for char in normalized 
                      if not (0x1F600 <= ord(char) <= 0x1F64F or  # Emoticons
                             0x1F300 <= ord(char) <= 0x1F5FF or   # Misc Symbols
                             0x1F680 <= ord(char) <= 0x1F6FF or   # Transport
                             0x1F1E0 <= ord(char) <= 0x1F1FF or   # Flags
                             0x2600 <= ord(char) <= 0x26FF or    # Misc symbols
                             0x2700 <= ord(char) <= 0x27BF))     # Dingbats
    
    # Handle specific German and Norwegian characters before ASCII conversion
    char_replacements = {
        'ß': 'ss',       # German eszett
        'ä': 'ae',       # German a-umlaut  
        'ö': 'oe',       # German o-umlaut
        'ü': 'ue',       # German u-umlaut
        'Ä': 'Ae',       # German A-umlaut
        'Ö': 'Oe',       # German O-umlaut
        'Ü': 'Ue',       # German U-umlaut
        'å': 'aa',       # Norwegian a-ring
        'ø': 'oe',       # Norwegian o-slash
        'æ': 'ae',       # Norwegian ae-ligature
        'Å': 'Aa',       # Norwegian A-ring
        'Ø': 'Oe',       # Norwegian O-slash
        'Æ': 'Ae',       # Norwegian AE-ligature
    }
    
    # Apply character replacements
    text_with_replacements = no_emoji
    for char, replacement in char_replacements.items():
        text_with_replacements = text_with_replacements.replace(char, replacement)
    
    # Convert to lowercase and remove remaining accents
    ascii_text = unicodedata.normalize('NFKD', text_with_replacements).encode('ascii', 'ignore').decode('ascii')
    
    # Replace spaces and special characters with underscores
    clean_text = re.sub(r'[^\w\s]', '', ascii_text.lower())
    slug = re.sub(r'\s+', '_', clean_text.strip())
    
    # Remove multiple consecutive underscores
    slug = re.sub(r'_+', '_', slug).strip('_')
    
    # Handle empty result
    if not slug:
        slug = 'group'
    
    # Ensure uniqueness
    base_slug = slug
    counter = 1
    while slug in existing_ids:
        slug = f"{base_slug}_{counter}"
        counter += 1
    
    return slug


def load_domains_registry(domains_path: Path) -> Tuple[bool, Dict[str, Any], str]:
    """
    Load the domains registry (domains.yaml) that lists all available domains.
    
    Args:
        domains_path: Path to domains/domains.yaml file
        
    Returns:
        Tuple of (success, domains_dict, error_message)
        
    I/O Operation - File reading with error handling.
    """
    try:
        if not domains_path.exists():
            return False, {}, f"Domains registry not found: {domains_path}"
        
        with open(domains_path, 'r') as f:
            registry_content = f.read()
        
        registry = yaml.safe_load(registry_content)
        if not registry or 'domains' not in registry:
            return False, {}, "Invalid domains registry: missing 'domains' key"
        
        return True, registry, ""
        
    except yaml.YAMLError as e:
        return False, {}, f"Failed to parse domains registry: {str(e)}"
    except Exception as e:
        return False, {}, f"Error reading domains registry: {str(e)}"


def load_domain_configuration(domain_key: str, domains_dir: Path) -> Tuple[bool, Dict[str, Any], str]:
    """
    Load a specific domain's complete configuration from {domain_key}.yaml.
    
    Args:
        domain_key: Domain identifier (e.g., 'exter')
        domains_dir: Path to domains directory
        
    Returns:
        Tuple of (success, config_dict, error_message)
        
    I/O Operation - File reading with validation.
    """
    try:
        config_path = domains_dir / f"{domain_key}.yaml"
        
        if not config_path.exists():
            return False, {}, f"Domain configuration not found: {config_path}"
        
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        config = yaml.safe_load(config_content)
        if not config:
            return False, {}, f"Empty domain configuration: {config_path}"
        
        # Validate required sections
        required_sections = ['domain', 'groups', 'assignments', 'rules', 'metadata']
        for section in required_sections:
            if section not in config:
                return False, {}, f"Missing required section '{section}' in {domain_key}.yaml"
        
        return True, config, ""
        
    except yaml.YAMLError as e:
        return False, {}, f"Failed to parse domain configuration: {str(e)}"
    except Exception as e:
        return False, {}, f"Error reading domain configuration: {str(e)}"


def export_domain_configuration(db: Session, domain_key: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Export current domain state from database to YAML-compatible format.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        
    Returns:
        Tuple of (success, config_dict, error_message)
        
    I/O Operation - Database query and data transformation.
    """
    try:
        from datetime import datetime, timezone
        
        # Get domain calendar info (from domains registry)
        success, domains_registry, error = load_domains_registry(settings.domains_config_path.parent / "domains.yaml")
        if not success:
            return False, {}, f"Cannot load domains registry: {error}"
        
        domain_info = domains_registry.get('domains', {}).get(domain_key)
        if not domain_info:
            return False, {}, f"Domain '{domain_key}' not found in registry"
        
        # Get groups and create semantic ID mapping
        groups = db.query(Group).filter(Group.domain_key == domain_key).all()
        groups_config = []
        db_id_to_semantic_id = {}  # Map database ID to semantic ID
        existing_semantic_ids = set()
        
        for group in groups:
            # Generate semantic ID from group name
            semantic_id = generate_semantic_id(group.name, existing_semantic_ids)
            existing_semantic_ids.add(semantic_id)
            db_id_to_semantic_id[group.id] = semantic_id
            
            groups_config.append({
                "id": semantic_id,
                "name": group.name,
                "description": f"Group for {group.name.replace('🏐', 'volleyball').replace('⚽', 'football').replace('🥋', 'martial arts').replace('🏊', 'swimming').replace('👦', 'youth').replace('👶', 'children').replace('👴', 'seniors').replace('🎵', 'music').replace('📚', 'education').replace('⛪', 'religious').replace('🎉', 'events').replace('🇩🇪', 'German')} activities"
            })
        
        # Get assignments organized by group using semantic IDs
        assignments_config = {}
        assignments = db.query(RecurringEventGroup).filter(
            RecurringEventGroup.domain_key == domain_key
        ).all()
        
        for assignment in assignments:
            semantic_id = db_id_to_semantic_id.get(assignment.group_id)
            if semantic_id:
                if semantic_id not in assignments_config:
                    assignments_config[semantic_id] = []
                assignments_config[semantic_id].append(assignment.recurring_event_title)
        
        # Get assignment rules using semantic IDs  
        rules = db.query(AssignmentRule).filter(AssignmentRule.domain_key == domain_key).all()
        rules_config = []
        for rule in rules:
            semantic_id = db_id_to_semantic_id.get(rule.target_group_id)
            if semantic_id:
                rules_config.append({
                    "rule_type": rule.rule_type,
                    "rule_value": rule.rule_value,
                    "target_group_id": semantic_id,
                    "description": f"Auto-assign {rule.rule_type} containing '{rule.rule_value}'"
                })
        
        # Build complete configuration
        export_config = {
            "domain": {
                "name": domain_info.get("name", domain_key),
                "calendar_url": domain_info.get("calendar_url", ""),
                "description": f"Exported configuration for {domain_key}",
                "timezone": "Europe/Oslo",
                "language": "en"
            },
            "groups": groups_config,
            "assignments": assignments_config,
            "rules": rules_config,
            "metadata": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "exported_by": "admin_panel",
                "version": "1.0",
                "source": "database_export",
                "total_groups": len(groups_config),
                "total_assignments": sum(len(events) for events in assignments_config.values()),
                "total_rules": len(rules_config)
            }
        }
        
        return True, export_config, ""
        
    except Exception as e:
        return False, {}, f"Export error: {str(e)}"


def import_domain_configuration(db: Session, domain_key: str, config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Import domain configuration from YAML format into database.
    
    Args:
        db: Database session
        domain_key: Domain identifier
        config: Configuration dictionary from YAML
        
    Returns:
        Tuple of (success, error_message)
        
    I/O Operation - Database creation with validation.
    """
    try:
        # Validate configuration structure
        required_sections = ['domain', 'groups', 'assignments', 'rules']
        for section in required_sections:
            if section not in config:
                return False, f"Missing required section: {section}"
        
        # Clear existing configuration for domain
        db.query(RecurringEventGroup).filter(RecurringEventGroup.domain_key == domain_key).delete()
        db.query(AssignmentRule).filter(AssignmentRule.domain_key == domain_key).delete() 
        db.query(Group).filter(Group.domain_key == domain_key).delete()
        
        # Create groups and build ID mapping (supports both semantic IDs and legacy group_X format)
        groups_config = config['groups']
        id_mapping = {}  # semantic_id -> database_id
        
        for group_config in groups_config:
            semantic_id = group_config['id']  # Can be "fussball" or "group_1" 
            group_name = group_config['name']
            
            # Validate group data
            validation_result = validate_group_data(group_name, domain_key)
            if not validation_result.is_success:
                return False, f"Invalid group '{group_name}' (ID: {semantic_id}): {validation_result.error}"
            
            # Create group
            group_data = create_group_data(domain_key, group_name)
            new_group = Group(**group_data)
            db.add(new_group)
            db.flush()  # Get database ID
            
            id_mapping[semantic_id] = new_group.id
        
        # Create assignments using semantic IDs
        assignments_config = config['assignments']
        for semantic_group_id, event_titles in assignments_config.items():
            if semantic_group_id not in id_mapping:
                return False, f"Unknown group ID in assignments: {semantic_group_id} (available: {list(id_mapping.keys())})"
            
            db_group_id = id_mapping[semantic_group_id]
            
            for event_title in event_titles:
                assignment_data = create_recurring_event_group_data(
                    domain_key, event_title, db_group_id
                )
                assignment = RecurringEventGroup(**assignment_data)
                db.add(assignment)
        
        # Create assignment rules using semantic IDs
        rules_config = config['rules']
        for rule_config in rules_config:
            semantic_group_id = rule_config['target_group_id']
            if semantic_group_id not in id_mapping:
                return False, f"Unknown group ID in rules: {semantic_group_id} (available: {list(id_mapping.keys())})"
            
            db_group_id = id_mapping[semantic_group_id]
            
            # Validate rule data
            validation_result = validate_assignment_rule_data(
                rule_config['rule_type'],
                rule_config['rule_value'],
                db_group_id
            )
            if not validation_result.is_success:
                return False, f"Invalid assignment rule: {validation_result.error}"
            
            # Create rule
            rule_data = create_assignment_rule_data(
                domain_key,
                rule_config['rule_type'],
                rule_config['rule_value'],
                db_group_id
            )
            rule = AssignmentRule(**rule_data)
            db.add(rule)
        
        # Commit all changes
        db.commit()
        
        total_groups = len(groups_config)
        total_assignments = sum(len(events) for events in assignments_config.values())
        total_rules = len(rules_config)
        
        return True, f"Successfully imported {total_groups} groups, {total_assignments} assignments, {total_rules} rules"
        
    except Exception as e:
        db.rollback()
        return False, f"Import error: {str(e)}"


def seed_domain_from_yaml(db: Session, domain_key: str) -> Tuple[bool, str]:
    """
    Seed domain from its YAML configuration file (replaces demo_data.py).
    
    Args:
        db: Database session  
        domain_key: Domain identifier
        
    Returns:
        Tuple of (success, error_message)
        
    I/O Operation - Load and import domain configuration.
    """
    try:
        domains_dir = settings.domains_config_path.parent
        
        # Load domain configuration
        success, config, error = load_domain_configuration(domain_key, domains_dir)
        if not success:
            return False, f"Failed to load {domain_key} configuration: {error}"
        
        # Check if domain already has data
        existing_groups = db.query(Group).filter(Group.domain_key == domain_key).first()
        if existing_groups:
            print(f"📋 Domain '{domain_key}' already has configuration data")
            return True, "Domain already configured"
        
        # Import configuration
        success, error = import_domain_configuration(db, domain_key, config)
        if not success:
            return False, f"Failed to import {domain_key} configuration: {error}"
        
        print(f"✅ Successfully seeded domain '{domain_key}' from YAML configuration")
        return True, "Domain seeded successfully"
        
    except Exception as e:
        return False, f"Seeding error: {str(e)}"


def list_available_domain_configs(domains_dir: Path) -> List[str]:
    """
    List all available domain configuration files.
    
    Args:
        domains_dir: Path to domains directory
        
    Returns:
        List of domain keys that have configuration files
        
    I/O Operation - Directory listing.
    """
    try:
        domain_files = []
        if domains_dir.exists():
            for file_path in domains_dir.glob("*.yaml"):
                if file_path.name != "domains.yaml":  # Skip the registry file
                    domain_key = file_path.stem
                    domain_files.append(domain_key)
        
        return sorted(domain_files)
        
    except Exception as e:
        print(f"Warning: Error listing domain configs: {e}")
        return []