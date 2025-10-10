"""
Admin domain configs router - YAML configuration management.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import re
import yaml

from ..core.database import get_db
from ..core.auth import verify_admin_auth
from ..models.domain import Domain
from ..models.calendar import Calendar
from ..core.config import settings

router = APIRouter()


class SeedDomainRequest(BaseModel):
    """Request body for seeding domain from YAML."""
    force_reseed: bool = False


@router.get(
    "/admin/domain-configs",
    summary="List available domain YAML configurations (admin only)",
    description="Get list of all .yaml files in domains/ directory"
)
async def list_domain_configs(
    _: bool = Depends(verify_admin_auth)
):
    """
    List all available domain configuration YAML files.

    Returns information about each YAML file including whether it's seeded in the database.
    """
    from ..services.domain_config_service import list_available_domain_configs

    domains_dir = settings.domains_config_path.parent
    available_configs = list_available_domain_configs(domains_dir)

    # Check which domains exist in database
    db_gen = get_db()
    db = next(db_gen)

    try:
        configs_info = []
        for domain_key in available_configs:
            # Check if domain exists in database
            domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()

            # Get YAML file info
            yaml_path = domains_dir / f"{domain_key}.yaml"
            file_size = yaml_path.stat().st_size if yaml_path.exists() else 0
            modified_time = datetime.fromtimestamp(yaml_path.stat().st_mtime) if yaml_path.exists() else None

            # Check if has groups seeded
            has_groups = False
            if domain:
                from ..models.calendar import Group
                has_groups = db.query(Group).filter(Group.domain_key == domain_key).count() > 0

            configs_info.append({
                "domain_key": domain_key,
                "file_name": f"{domain_key}.yaml",
                "file_size": file_size,
                "modified_at": modified_time.isoformat() if modified_time else None,
                "exists_in_database": domain is not None,
                "has_groups": has_groups,
                "status": domain.status if domain else None
            })

        return {
            "configs": configs_info,
            "total": len(configs_info)
        }
    finally:
        db.close()


@router.get(
    "/admin/domain-configs/{domain_key}",
    summary="Download/view domain YAML configuration (admin only)",
    description="Get the raw YAML content of a domain configuration file"
)
async def get_domain_config_file(
    domain_key: str,
    format: str = Query("yaml", description="Response format: 'yaml' or 'json'"),
    _: bool = Depends(verify_admin_auth)
):
    """
    Download or view a domain configuration YAML file.

    Returns YAML content by default, or JSON if format=json.
    """
    domains_dir = settings.domains_config_path.parent
    yaml_path = domains_dir / f"{domain_key}.yaml"

    if not yaml_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain configuration file '{domain_key}.yaml' not found"
        )

    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()

        if format == "json":
            # Parse and return as JSON
            config = yaml.safe_load(yaml_content)
            return config
        else:
            # Return raw YAML
            return Response(
                content=yaml_content,
                media_type="application/x-yaml",
                headers={
                    "Content-Disposition": f'attachment; filename="{domain_key}.yaml"'
                }
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read configuration file: {str(e)}"
        )


@router.post(
    "/admin/domain-configs/{domain_key}",
    summary="Upload/update domain YAML configuration (admin only)",
    description="Upload a new or update existing domain configuration YAML file"
)
async def upload_domain_config_file(
    domain_key: str,
    file: UploadFile = File(...),
    _: bool = Depends(verify_admin_auth)
):
    """
    Upload or update a domain configuration YAML file.

    Validates YAML syntax before saving.
    """
    # Validate domain key format
    if not re.match(r'^[a-z0-9_-]+$', domain_key):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Domain key must contain only lowercase letters, numbers, underscores, and hyphens"
        )

    # Read file content
    try:
        content = await file.read()
        yaml_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be UTF-8 encoded text"
        )

    # Validate YAML syntax
    try:
        config = yaml.safe_load(yaml_content)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="YAML file is empty or invalid"
            )
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid YAML syntax: {str(e)}"
        )

    # Validate required sections
    required_sections = ['domain', 'groups', 'assignments', 'rules']
    missing_sections = [s for s in required_sections if s not in config]
    if missing_sections:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing required sections: {', '.join(missing_sections)}"
        )

    # Save to domains directory
    domains_dir = settings.domains_config_path.parent
    yaml_path = domains_dir / f"{domain_key}.yaml"

    try:
        # Create backup if file already exists
        if yaml_path.exists():
            backup_path = domains_dir / f"{domain_key}.yaml.backup"
            yaml_path.rename(backup_path)

        # Write new file
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        return {
            "success": True,
            "message": f"Configuration file '{domain_key}.yaml' uploaded successfully",
            "domain_key": domain_key,
            "file_size": len(yaml_content)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save configuration file: {str(e)}"
        )


@router.post(
    "/admin/domain-configs/{domain_key}/seed",
    summary="Seed database from domain YAML configuration (admin only)",
    description="Create Domain record and seed groups/assignments from YAML file"
)
async def seed_domain_from_config(
    domain_key: str,
    request: Optional[SeedDomainRequest] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Seed database from a domain YAML configuration file.

    Creates Domain record if it doesn't exist, then imports groups/assignments/rules.
    """
    from ..services.domain_config_service import load_domain_configuration, import_domain_configuration

    domains_dir = settings.domains_config_path.parent

    # Load YAML configuration
    success, config, error = load_domain_configuration(domain_key, domains_dir)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration file not found: {error}"
        )

    try:
        # Check if domain exists
        domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()

        # Create Domain record if it doesn't exist
        if not domain:
            domain_config = config.get('domain', {})

            # Create domain record
            domain = Domain(
                domain_key=domain_key,
                name=domain_config.get('name', domain_key),
                calendar_url=domain_config.get('calendar_url', ''),
                status='active'
            )
            db.add(domain)
            db.flush()  # Get domain.id

            # Create calendar
            calendar = Calendar(
                name=domain_config.get('name', domain_key),
                source_url=domain_config.get('calendar_url', ''),
                type="domain",
                user_id=None
            )
            db.add(calendar)
            db.flush()

            # Link domain to calendar
            domain.calendar_id = calendar.id
            db.commit()
            db.refresh(domain)

            # Sync calendar events
            from ..services.calendar_service import sync_calendar_events
            try:
                sync_success, event_count, sync_error = await sync_calendar_events(db, calendar)
                if sync_success:
                    print(f"✅ Synced {event_count} events for domain '{domain_key}'")
                else:
                    print(f"⚠️ Failed to sync events: {sync_error}")
            except Exception as e:
                print(f"⚠️ Calendar sync error: {e}")

        # Check if already has groups
        from ..models.calendar import Group
        existing_groups = db.query(Group).filter(Group.domain_key == domain_key).count()

        force_reseed = request.force_reseed if request else False

        if existing_groups > 0 and not force_reseed:
            return {
                "success": False,
                "message": f"Domain '{domain_key}' already has {existing_groups} groups. Use force_reseed=true to overwrite.",
                "domain_key": domain_key,
                "existing_groups": existing_groups
            }

        # Import configuration (groups, assignments, rules)
        import_success, import_message = import_domain_configuration(db, domain_key, config)
        if not import_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to import configuration: {import_message}"
            )

        # Apply assignment rules
        from ..services.domain_service import auto_assign_events_with_rules
        try:
            rule_success, count, rule_error = await auto_assign_events_with_rules(db, domain_key)
            if rule_success:
                print(f"✅ Applied {count} auto-assignments from rules")
        except Exception as e:
            print(f"⚠️ Rule application error: {e}")

        return {
            "success": True,
            "message": import_message,
            "domain_key": domain_key
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed domain: {str(e)}"
        )


@router.delete(
    "/admin/domain-configs/{domain_key}",
    summary="Delete domain YAML configuration file (admin only)",
    description="Delete a domain configuration YAML file from the server"
)
async def delete_domain_config_file(
    domain_key: str,
    _: bool = Depends(verify_admin_auth)
):
    """
    Delete a domain configuration YAML file.

    WARNING: This only deletes the file, not the database records.
    """
    domains_dir = settings.domains_config_path.parent
    yaml_path = domains_dir / f"{domain_key}.yaml"

    if not yaml_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration file '{domain_key}.yaml' not found"
        )

    # Prevent deleting domains.yaml registry
    if domain_key == "domains":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the domains registry file"
        )

    try:
        # Create backup before deleting
        backup_dir = domains_dir / "deleted"
        backup_dir.mkdir(exist_ok=True)

        backup_path = backup_dir / f"{domain_key}.yaml.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        yaml_path.rename(backup_path)

        return {
            "success": True,
            "message": f"Configuration file '{domain_key}.yaml' deleted (backed up to {backup_path.name})"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete configuration file: {str(e)}"
        )
