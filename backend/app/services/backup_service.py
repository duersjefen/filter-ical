"""
Backup Service for domain configuration snapshots.

Provides backup/restore functionality using domain_config_service for export/import.
"""

from typing import Tuple, List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.calendar import DomainBackup
from .domain_config_service import export_domain_configuration, import_domain_configuration


def create_backup(
    db: Session,
    domain_key: str,
    description: Optional[str] = None,
    created_by: Optional[str] = None,
    backup_type: str = 'manual'
) -> Tuple[bool, Optional[DomainBackup], str]:
    """
    Create a backup snapshot of domain configuration.

    Args:
        db: Database session
        domain_key: Domain identifier
        description: Optional user description
        created_by: Optional username who created backup
        backup_type: Type of backup ('manual', 'auto_pre_reset', etc)

    Returns:
        Tuple of (success, backup_object, error_message)
    """
    try:
        # Export current domain configuration
        success, config_snapshot, error = export_domain_configuration(db, domain_key)
        if not success:
            return False, None, f"Failed to export configuration: {error}"

        # Create backup record
        backup = DomainBackup(
            domain_key=domain_key,
            config_snapshot=config_snapshot,
            created_by=created_by,
            description=description,
            backup_type=backup_type
        )

        db.add(backup)
        db.commit()
        db.refresh(backup)

        return True, backup, ""

    except Exception as e:
        db.rollback()
        return False, None, f"Backup creation failed: {str(e)}"


def list_backups(
    db: Session,
    domain_key: str
) -> Tuple[bool, List[DomainBackup], str]:
    """
    List all backups for a domain, ordered by creation date (newest first).

    Args:
        db: Database session
        domain_key: Domain identifier

    Returns:
        Tuple of (success, list_of_backups, error_message)
    """
    try:
        backups = db.query(DomainBackup).filter(
            DomainBackup.domain_key == domain_key
        ).order_by(desc(DomainBackup.created_at)).all()

        return True, backups, ""

    except Exception as e:
        return False, [], f"Failed to list backups: {str(e)}"


def get_backup(
    db: Session,
    domain_key: str,
    backup_id: int
) -> Tuple[bool, Optional[DomainBackup], str]:
    """
    Get a specific backup by ID.

    Args:
        db: Database session
        domain_key: Domain identifier
        backup_id: Backup ID

    Returns:
        Tuple of (success, backup_object, error_message)
    """
    try:
        backup = db.query(DomainBackup).filter(
            DomainBackup.id == backup_id,
            DomainBackup.domain_key == domain_key
        ).first()

        if not backup:
            return False, None, "Backup not found"

        return True, backup, ""

    except Exception as e:
        return False, None, f"Failed to get backup: {str(e)}"


def delete_backup(
    db: Session,
    domain_key: str,
    backup_id: int
) -> Tuple[bool, str]:
    """
    Delete a backup.

    Args:
        db: Database session
        domain_key: Domain identifier
        backup_id: Backup ID

    Returns:
        Tuple of (success, error_message)
    """
    try:
        backup = db.query(DomainBackup).filter(
            DomainBackup.id == backup_id,
            DomainBackup.domain_key == domain_key
        ).first()

        if not backup:
            return False, "Backup not found"

        db.delete(backup)
        db.commit()

        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Failed to delete backup: {str(e)}"


def restore_backup(
    db: Session,
    domain_key: str,
    backup_id: int,
    created_by: Optional[str] = None
) -> Tuple[bool, Optional[int], str]:
    """
    Restore domain from a backup snapshot.

    Automatically creates a backup of current state before restoring.

    Args:
        db: Database session
        domain_key: Domain identifier
        backup_id: Backup ID to restore from
        created_by: Optional username performing restore

    Returns:
        Tuple of (success, auto_backup_id, error_message)
    """
    try:
        # Get the backup to restore
        backup = db.query(DomainBackup).filter(
            DomainBackup.id == backup_id,
            DomainBackup.domain_key == domain_key
        ).first()

        if not backup:
            return False, None, "Backup not found"

        # Create auto-backup of current state before restoring
        auto_success, auto_backup, auto_error = create_backup(
            db=db,
            domain_key=domain_key,
            description=f"Auto-backup before restoring backup #{backup_id}",
            created_by=created_by,
            backup_type='auto_pre_restore'
        )

        if not auto_success:
            return False, None, f"Failed to create safety backup: {auto_error}"

        # Restore from backup snapshot
        restore_success, restore_error = import_domain_configuration(
            db=db,
            domain_key=domain_key,
            config=backup.config_snapshot
        )

        if not restore_success:
            return False, auto_backup.id, f"Restore failed: {restore_error}"

        return True, auto_backup.id, ""

    except Exception as e:
        db.rollback()
        return False, None, f"Restore operation failed: {str(e)}"
