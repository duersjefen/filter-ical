"""
Domain backups router for backup/restore operations.

Implements backup management endpoints from OpenAPI specification.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import Response
from sqlalchemy.orm import Session
import yaml

from ..core.database import get_db
from ..core.error_handlers import handle_endpoint_errors
from ..core.auth import get_verified_domain
from ..core.messages import SuccessMessages
from ..models.domain import Domain
from ..services.backup_service import (
    create_backup, list_backups, get_backup, delete_backup, restore_backup
)

router = APIRouter()


@router.post("/{domain}/backups")
@handle_endpoint_errors
async def create_domain_backup(
    domain_obj: Domain = Depends(get_verified_domain),
    body: Optional[dict] = Body(None),
    db: Session = Depends(get_db)
):
    """Create a backup snapshot of current domain configuration."""
    # Extract description from body if provided
    description = body.get('description') if body else None

    # Create backup
    backup_success, backup, backup_error = create_backup(
        db=db,
        domain_key=domain_obj.domain_key,
        description=description,
        backup_type='manual'
    )

    if not backup_success:
        raise HTTPException(status_code=500, detail=backup_error)

    # Return backup data matching OpenAPI schema
    return {
        "id": backup.id,
        "domain_key": backup.domain_key,
        "config_snapshot": backup.config_snapshot,
        "created_at": backup.created_at.isoformat() + 'Z' if backup.created_at else None,
        "created_by": backup.created_by,
        "description": backup.description,
        "backup_type": backup.backup_type
    }


@router.get("/{domain}/backups")
@handle_endpoint_errors
async def get_domain_backups(
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """List all backups for a domain, ordered by creation date (newest first)."""
    # Get backups
    list_success, backups, list_error = list_backups(db=db, domain_key=domain_obj.domain_key)

    if not list_success:
        raise HTTPException(status_code=500, detail=list_error)

    # Transform to OpenAPI schema format
    backups_response = []
    for backup in backups:
        backups_response.append({
            "id": backup.id,
            "domain_key": backup.domain_key,
            "config_snapshot": backup.config_snapshot,
            "created_at": backup.created_at.isoformat() + 'Z' if backup.created_at else None,
            "created_by": backup.created_by,
            "description": backup.description,
            "backup_type": backup.backup_type
        })

    return backups_response


@router.delete("/{domain}/backups/{backup_id}")
@handle_endpoint_errors
async def delete_domain_backup(
    backup_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Delete a backup snapshot."""
    # Delete backup
    delete_success, delete_error = delete_backup(
        db=db,
        domain_key=domain_obj.domain_key,
        backup_id=backup_id
    )

    if not delete_success:
        if "not found" in delete_error.lower():
            raise HTTPException(status_code=404, detail=delete_error)
        raise HTTPException(status_code=500, detail=delete_error)

    return {
        "success": True,
        "message": SuccessMessages.BACKUP_DELETED
    }


@router.post("/{domain}/backups/{backup_id}/restore")
@handle_endpoint_errors
async def restore_domain_backup(
    backup_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    db: Session = Depends(get_db)
):
    """Restore domain from a backup snapshot. Automatically creates a backup of current state first."""
    # Restore from backup
    restore_success, auto_backup_id, restore_error = restore_backup(
        db=db,
        domain_key=domain_obj.domain_key,
        backup_id=backup_id
    )

    if not restore_success:
        if "not found" in restore_error.lower():
            raise HTTPException(status_code=404, detail=restore_error)
        raise HTTPException(status_code=500, detail=restore_error)

    return {
        "success": True,
        "message": SuccessMessages.BACKUP_RESTORED,
        "auto_backup_id": auto_backup_id
    }


@router.get("/{domain}/backups/{backup_id}/download")
@handle_endpoint_errors
async def download_domain_backup(
    backup_id: int,
    domain_obj: Domain = Depends(get_verified_domain),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Download a backup as YAML file."""
    # Get backup
    get_success, backup, get_error = get_backup(
        db=db,
        domain_key=domain_obj.domain_key,
        backup_id=backup_id
    )

    if not get_success:
        if "not found" in get_error.lower():
            raise HTTPException(status_code=404, detail=get_error)
        raise HTTPException(status_code=500, detail=get_error)

    # Convert to YAML
    # sort_keys=False preserves dict insertion order (domain, groups, assignments, rules, metadata)
    yaml_content = yaml.dump(backup.config_snapshot, default_flow_style=False, indent=2,
                            allow_unicode=True, encoding=None, sort_keys=False)

    return Response(content=yaml_content, media_type="application/x-yaml")
