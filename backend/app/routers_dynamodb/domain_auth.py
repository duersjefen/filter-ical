"""
Domain authentication router for DynamoDB backend.

Implements password verification and management endpoints.
"""

import bcrypt
from fastapi import APIRouter, HTTPException, Body

from .deps import get_repo, get_verified_domain_ddb

router = APIRouter()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


@router.get("/api/domains/{domain}/auth/status")
async def get_auth_status(domain: str):
    """Get authentication status for a domain."""
    domain_obj = await get_verified_domain_ddb(domain)

    return {
        "has_admin_password": domain_obj.admin_password_hash is not None and domain_obj.admin_password_hash != "",
        "has_user_password": domain_obj.user_password_hash is not None and domain_obj.user_password_hash != ""
    }


@router.post("/api/domains/{domain}/auth/verify-admin")
async def verify_admin_password(domain: str, data: dict = Body(...)):
    """Verify admin password for a domain."""
    domain_obj = await get_verified_domain_ddb(domain)

    password = data.get("password", "")

    if not domain_obj.admin_password_hash:
        raise HTTPException(status_code=400, detail="No admin password set for this domain")

    if not verify_password(password, domain_obj.admin_password_hash):
        raise HTTPException(status_code=401, detail="Invalid admin password")

    return {"success": True, "message": "Admin password verified"}


@router.post("/api/domains/{domain}/auth/verify-user")
async def verify_user_password(domain: str, data: dict = Body(...)):
    """Verify user password for a domain."""
    domain_obj = await get_verified_domain_ddb(domain)

    password = data.get("password", "")

    if not domain_obj.user_password_hash:
        # No password set = public access
        return {"success": True, "message": "No password required"}

    if not verify_password(password, domain_obj.user_password_hash):
        raise HTTPException(status_code=401, detail="Invalid user password")

    return {"success": True, "message": "User password verified"}


@router.patch("/api/domains/{domain}/auth/set-admin-password")
async def set_admin_password(domain: str, data: dict = Body(...)):
    """Set or update admin password for a domain."""
    domain_obj = await get_verified_domain_ddb(domain)

    password = data.get("password", "")

    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")

    domain_obj.admin_password_hash = hash_password(password)

    repo = get_repo()
    repo.save_domain(domain_obj)

    return {"success": True, "message": "Admin password updated"}


@router.patch("/api/domains/{domain}/auth/set-user-password")
async def set_user_password(domain: str, data: dict = Body(...)):
    """Set or update user password for a domain."""
    domain_obj = await get_verified_domain_ddb(domain)

    password = data.get("password")

    if password is None:
        # Clear password (make public)
        domain_obj.user_password_hash = None
    elif len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
    else:
        domain_obj.user_password_hash = hash_password(password)

    repo = get_repo()
    repo.save_domain(domain_obj)

    return {"success": True, "message": "User password updated"}
