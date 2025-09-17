"""
Domain Configuration Functions (Functional Core)
Pure functions for domain configuration management.
No I/O operations, just data transformations and validations.
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml


def load_domains_config(config_path: str) -> Dict[str, Any]:
    """
    Load domain configuration from YAML file.
    Pure function - reads file and parses YAML.
    
    Args:
        config_path: Path to the domains.yaml configuration file
        
    Returns:
        Dict containing all domain configurations
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_available_domains(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract list of available domains from configuration.
    Pure function - transforms config data to domain list.
    
    Args:
        config: Domain configuration dictionary
        
    Returns:
        List of domain dictionaries with id, name, calendar_name, calendar_url
    """
    if 'domains' not in config:
        return []
    
    domains = []
    for domain_id, domain_config in config['domains'].items():
        domains.append({
            'id': domain_id,
            'name': domain_config.get('name', domain_id.title()),
            'calendar_url': domain_config.get('calendar_url', '')
        })
    
    return domains


def get_domain_config(config: Dict[str, Any], domain_id: str) -> Optional[Dict[str, str]]:
    """
    Get configuration for a specific domain.
    Pure function - extracts domain config from larger config.
    
    Args:
        config: Domain configuration dictionary
        domain_id: ID of the domain to retrieve
        
    Returns:
        Domain configuration dict or None if domain not found
    """
    if 'domains' not in config or domain_id not in config['domains']:
        return None
    
    domain_config = config['domains'][domain_id]
    return {
        'id': domain_id,
        'name': domain_config.get('name', domain_id.title()),
        'calendar_url': domain_config.get('calendar_url', '')
    }


def validate_domain_config(domain_config: Dict[str, str]) -> tuple[bool, str]:
    """
    Validate domain configuration structure.
    Pure function - validates data structure.
    
    Args:
        domain_config: Domain configuration to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['id', 'name', 'calendar_url']
    
    for field in required_fields:
        if field not in domain_config or not domain_config[field]:
            return False, f"Missing required field: {field}"
    
    # Basic URL validation
    calendar_url = domain_config['calendar_url']
    if not (calendar_url.startswith('http://') or calendar_url.startswith('https://')):
        return False, "calendar_url must be a valid HTTP/HTTPS URL"
    
    return True, ""


def is_valid_domain_id(domain_id: str) -> bool:
    """
    Check if domain ID format is valid.
    Pure function - validates string format.
    
    Args:
        domain_id: Domain ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not domain_id or not isinstance(domain_id, str):
        return False
    
    # Domain ID should be alphanumeric and underscore only
    return domain_id.replace('_', '').isalnum() and len(domain_id) > 0