"""
Domain Configuration Service for YAML-based domain management.

This service replaces demo_data.py with a living configuration system
that can export/import domain configurations as portable YAML files.

IMPERATIVE SHELL - Orchestrates pure functions with I/O operations.
"""

import yaml
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
        
        # Get groups
        groups = db.query(Group).filter(Group.domain_key == domain_key).all()
        groups_config = []
        for group in groups:
            groups_config.append({
                "id": f"group_{group.id}",  # Create stable ID from database ID
                "name": group.name,
                "description": f"Group with {group.id} database ID"
            })
        
        # Get assignments organized by group
        assignments_config = {}
        assignments = db.query(RecurringEventGroup).filter(
            RecurringEventGroup.domain_key == domain_key
        ).all()
        
        for assignment in assignments:
            group_id = f"group_{assignment.group_id}"
            if group_id not in assignments_config:
                assignments_config[group_id] = []
            assignments_config[group_id].append(assignment.recurring_event_title)
        
        # Get assignment rules
        rules = db.query(AssignmentRule).filter(AssignmentRule.domain_key == domain_key).all()
        rules_config = []
        for rule in rules:
            rules_config.append({
                "rule_type": rule.rule_type,
                "rule_value": rule.rule_value,
                "target_group_id": f"group_{rule.target_group_id}",
                "description": f"Auto-assign rule for {rule.rule_type}"
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
        
        # Create groups and build ID mapping
        groups_config = config['groups']
        id_mapping = {}  # config_id -> database_id
        
        for group_config in groups_config:
            config_id = group_config['id']
            group_name = group_config['name']
            
            # Validate group data
            is_valid, error_msg = validate_group_data(group_name, domain_key)
            if not is_valid:
                return False, f"Invalid group '{group_name}': {error_msg}"
            
            # Create group
            group_data = create_group_data(domain_key, group_name)
            new_group = Group(**group_data)
            db.add(new_group)
            db.flush()  # Get database ID
            
            id_mapping[config_id] = new_group.id
        
        # Create assignments
        assignments_config = config['assignments']
        for config_group_id, event_titles in assignments_config.items():
            if config_group_id not in id_mapping:
                return False, f"Unknown group ID in assignments: {config_group_id}"
            
            db_group_id = id_mapping[config_group_id]
            
            for event_title in event_titles:
                assignment_data = create_recurring_event_group_data(
                    domain_key, event_title, db_group_id
                )
                assignment = RecurringEventGroup(**assignment_data)
                db.add(assignment)
        
        # Create assignment rules
        rules_config = config['rules']
        for rule_config in rules_config:
            config_group_id = rule_config['target_group_id']
            if config_group_id not in id_mapping:
                return False, f"Unknown group ID in rules: {config_group_id}"
            
            db_group_id = id_mapping[config_group_id]
            
            # Validate rule data
            is_valid, error_msg = validate_assignment_rule_data(
                rule_config['rule_type'],
                rule_config['rule_value'],
                db_group_id
            )
            if not is_valid:
                return False, f"Invalid assignment rule: {error_msg}"
            
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
        domains_dir = settings.domains_config_path.parent / "domains"
        
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