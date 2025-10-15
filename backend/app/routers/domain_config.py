"""
Domain configuration router for import/export/reset operations.

Implements configuration management endpoints from OpenAPI specification.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
import yaml

from ..core.database import get_db
from ..core.config import settings
from ..core.error_handlers import handle_endpoint_errors
from ..core.auth import get_verified_domain
from ..core.messages import ErrorMessages
from ..models.domain import Domain
from ..services.domain_config_service import (
    export_domain_configuration, import_domain_configuration,
    load_domain_configuration
)

router = APIRouter()


@router.get("/{domain}/export-config")
@handle_endpoint_errors
async def export_domain_config(
    domain_obj: Domain = Depends(get_verified_domain),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Export current domain configuration as YAML (admin)."""
    # Export current domain state
    success, export_config, error = export_domain_configuration(db, domain_obj.domain_key)
    if not success:
        raise HTTPException(status_code=500, detail=f"Export error: {error}")

    # Check if client wants YAML format
    accept_header = request.headers.get('accept', '').lower()
    if 'application/x-yaml' in accept_header or 'text/yaml' in accept_header:
        # Return raw YAML content with proper UTF-8 encoding
        # sort_keys=False preserves dict insertion order (domain, groups, assignments, rules, metadata)
        yaml_content = yaml.dump(export_config, default_flow_style=False, indent=2,
                               allow_unicode=True, encoding=None, sort_keys=False)
        return Response(content=yaml_content, media_type="application/x-yaml")
    else:
        # Return JSON (default)
        return export_config


@router.post("/{domain}/import-config")
@handle_endpoint_errors
async def import_domain_config(
    domain_obj: Domain = Depends(get_verified_domain),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Import domain configuration from YAML (admin)."""
    # Get raw content from request
    content_type = request.headers.get('content-type', '').lower()

    if 'multipart/form-data' in content_type:
        # Handle file upload from form
        from fastapi import UploadFile, File, Form
        form_data = await request.form()

        # Get the uploaded file
        uploaded_file = None
        for field_name, field_value in form_data.items():
            if hasattr(field_value, 'read'):  # It's a file
                uploaded_file = field_value
                break

        if not uploaded_file:
            raise HTTPException(status_code=400, detail="No file uploaded. Please upload a YAML configuration file.")

        # Read file content
        file_content = await uploaded_file.read()
        try:
            config_data = yaml.safe_load(file_content.decode('utf-8'))
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")
        except UnicodeDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid file encoding (expected UTF-8): {str(e)}")

    elif 'application/x-yaml' in content_type or 'text/yaml' in content_type:
        # Parse YAML content
        yaml_content = await request.body()
        try:
            config_data = yaml.safe_load(yaml_content.decode('utf-8'))
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")
    else:
        # Assume JSON (for backward compatibility)
        config_data = await request.json()

    # Validate required fields in import
    if not isinstance(config_data, dict):
        raise HTTPException(status_code=400, detail=ErrorMessages.CONFIGURATION_MUST_BE_OBJECT)

    required_sections = ["domain", "groups", "assignments", "rules"]
    for section in required_sections:
        if section not in config_data:
            raise HTTPException(status_code=400, detail=f"Missing required section: '{section}'")

    # Import configuration
    success, error = import_domain_configuration(db, domain_obj.domain_key, config_data)
    if not success:
        raise HTTPException(status_code=400, detail=f"Import error: {error}")

    return {
        "success": True,
        "message": error  # Contains success message from import function
    }


@router.post("/{domain}/reset-config")
@handle_endpoint_errors
async def reset_domain_config(
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Reset domain to baseline configuration from YAML file (admin)."""
    # Load baseline configuration from YAML file
    domains_dir = settings.domains_config_path.parent
    success, baseline_config, error = load_domain_configuration(domain_obj.domain_key, domains_dir)
    if not success:
        raise HTTPException(status_code=404, detail=f"No baseline configuration found: {error}")

    # Import baseline configuration
    success, error = import_domain_configuration(db, domain_obj.domain_key, baseline_config)
    if not success:
        raise HTTPException(status_code=400, detail=f"Reset error: {error}")

    return {
        "success": True,
        "message": f"Domain '{domain_obj.domain_key}' reset to baseline configuration"
    }
