"""
Domain admins router for admin user management.

Implements admin management endpoints from OpenAPI specification.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.error_handlers import handle_endpoint_errors
from ..core.auth import require_user_auth, get_verified_domain
from ..models.domain import Domain

router = APIRouter()


@router.get("/{domain}/admins")
@handle_endpoint_errors
async def list_domain_admins(
    domain_obj: Domain = Depends(get_verified_domain),
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """List all admins for a domain (owner or admin access required)."""
    # Check if user is owner or admin
    is_owner = domain_obj.owner_id == user_id
    is_admin = any(admin.id == user_id for admin in domain_obj.admins)

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Only domain owner or admins can view admin list."
        )

    # Get owner info
    owner_info = None
    if domain_obj.owner:
        owner_info = {
            "id": domain_obj.owner.id,
            "username": domain_obj.owner.username,
            "email": domain_obj.owner.email
        }

    # Get admin list
    admins_list = []
    for admin in domain_obj.admins:
        admins_list.append({
            "id": admin.id,
            "username": admin.username,
            "email": admin.email
        })

    return {
        "owner": owner_info,
        "admins": admins_list
    }


@router.post("/{domain}/admins")
@handle_endpoint_errors
async def add_domain_admin(
    domain_obj: Domain = Depends(get_verified_domain),
    request_data: dict = None,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Add a user as admin for the domain (owner access required)."""
    try:
        # Check if user is owner
        if domain_obj.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Only domain owner can add admins."
            )

        # Validate request
        if "username" not in request_data:
            raise HTTPException(status_code=400, detail="username is required")

        username = request_data["username"].strip()

        # Find user to add as admin
        from ..models.user import User
        user_to_add = db.query(User).filter(User.username == username).first()
        if not user_to_add:
            raise HTTPException(status_code=400, detail=f"User '{username}' not found")

        # Check if already admin
        if user_to_add in domain_obj.admins:
            raise HTTPException(status_code=409, detail=f"User '{username}' is already an admin")

        # Check if trying to add owner as admin
        if user_to_add.id == domain_obj.owner_id:
            raise HTTPException(status_code=400, detail="Domain owner is already admin by default")

        # Add admin
        domain_obj.admins.append(user_to_add)
        db.commit()

        return {
            "success": True,
            "message": f"User '{username}' added as admin"
        }
    except Exception as e:
        db.rollback()
        raise


@router.delete("/{domain}/admins/{username}")
@handle_endpoint_errors
async def remove_domain_admin(
    username: str,
    domain_obj: Domain = Depends(get_verified_domain),
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """Remove a user from domain admins (owner access required)."""
    try:
        # Check if user is owner
        if domain_obj.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Only domain owner can remove admins."
            )

        # Find user to remove
        from ..models.user import User
        user_to_remove = db.query(User).filter(User.username == username).first()
        if not user_to_remove:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

        # Check if user is admin
        if user_to_remove not in domain_obj.admins:
            raise HTTPException(status_code=404, detail=f"User '{username}' is not an admin")

        # Remove admin
        domain_obj.admins.remove(user_to_remove)
        db.commit()

        return {
            "success": True,
            "message": f"User '{username}' removed from admins"
        }
    except Exception as e:
        db.rollback()
        raise
