"""
Domain authentication router - API endpoints for password-protected domains.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ..core.database import get_db
from ..core.auth import verify_admin_password
from ..services.domain_auth_service import (
    verify_domain_password,
    set_admin_password,
    set_user_password,
    remove_admin_password,
    remove_user_password,
    check_password_status,
    verify_token,
    get_all_domains_auth_status
)

router = APIRouter()


# Request/Response Models

class VerifyPasswordRequest(BaseModel):
    """Request body for password verification."""
    password: str


class VerifyPasswordResponse(BaseModel):
    """Response for successful password verification."""
    success: bool
    token: str
    message: str


class SetPasswordRequest(BaseModel):
    """Request body for setting passwords."""
    password: str


class PasswordStatusResponse(BaseModel):
    """Response for password status check."""
    admin_password_set: bool
    user_password_set: bool


class DomainAuthStatusResponse(BaseModel):
    """Response for domain auth status (global admin)."""
    domain_key: str
    admin_password_set: bool
    user_password_set: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class SetDomainPasswordsRequest(BaseModel):
    """Request body for global admin setting domain passwords."""
    admin_password: Optional[str] = None
    user_password: Optional[str] = None
    remove_admin_password: bool = False
    remove_user_password: bool = False


# Helper function for JWT verification

def verify_domain_admin_jwt(
    domain: str,
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Verify JWT token for domain admin access.

    Args:
        domain: Domain key from path
        authorization: Bearer token from header

    Returns:
        Token data dict

    Raises:
        HTTPException: If token invalid or unauthorized
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = authorization.replace("Bearer ", "")

    valid, token_data = verify_token(token, domain, "admin")

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return token_data


# Domain-level Endpoints

@router.post(
    "/api/domains/{domain}/auth/verify-admin",
    response_model=VerifyPasswordResponse,
    summary="Verify admin password and get JWT token"
)
async def verify_admin_password_endpoint(
    domain: str,
    request: VerifyPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Verify admin password for domain and return JWT token.

    Returns JWT token with 30-day expiry if password correct.
    If no password set, returns token without verification (backward compatibility).
    """
    success, result = verify_domain_password(db, domain, request.password, "admin")

    if success:
        return VerifyPasswordResponse(
            success=True,
            token=result,
            message="Authentication successful"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result
        )


@router.post(
    "/api/domains/{domain}/auth/verify-user",
    response_model=VerifyPasswordResponse,
    summary="Verify user password and get JWT token"
)
async def verify_user_password_endpoint(
    domain: str,
    request: VerifyPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user password for domain and return JWT token.

    Returns JWT token with 30-day expiry if password correct.
    If no password set, returns token without verification (backward compatibility).
    """
    success, result = verify_domain_password(db, domain, request.password, "user")

    if success:
        return VerifyPasswordResponse(
            success=True,
            token=result,
            message="Authentication successful"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result
        )


@router.patch(
    "/api/domains/{domain}/auth/set-admin-password",
    summary="Set admin password for domain (requires admin JWT)"
)
async def set_admin_password_endpoint(
    domain: str,
    request: SetPasswordRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_domain_admin_jwt)
):
    """
    Set or change admin password for domain.

    Requires valid admin JWT token.
    Password must be at least 8 characters.
    """
    success, error = set_admin_password(db, domain, request.password)

    if success:
        return {"success": True, "message": "Admin password set successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )


@router.patch(
    "/api/domains/{domain}/auth/set-user-password",
    summary="Set user password for domain (requires admin JWT)"
)
async def set_user_password_endpoint(
    domain: str,
    request: SetPasswordRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_domain_admin_jwt)
):
    """
    Set or change user password for domain.

    Requires valid admin JWT token.
    Password must be at least 8 characters.
    """
    success, error = set_user_password(db, domain, request.password)

    if success:
        return {"success": True, "message": "User password set successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )


@router.delete(
    "/api/domains/{domain}/auth/remove-admin-password",
    summary="Remove admin password for domain (requires admin JWT)"
)
async def remove_admin_password_endpoint(
    domain: str,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_domain_admin_jwt)
):
    """
    Remove admin password protection for domain.

    Requires valid admin JWT token.
    """
    success, error = remove_admin_password(db, domain)

    if success:
        return {"success": True, "message": "Admin password removed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )


@router.delete(
    "/api/domains/{domain}/auth/remove-user-password",
    summary="Remove user password for domain (requires admin JWT)"
)
async def remove_user_password_endpoint(
    domain: str,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_domain_admin_jwt)
):
    """
    Remove user password protection for domain.

    Requires valid admin JWT token.
    """
    success, error = remove_user_password(db, domain)

    if success:
        return {"success": True, "message": "User password removed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )


@router.get(
    "/api/domains/{domain}/auth/status",
    response_model=PasswordStatusResponse,
    summary="Check password status for domain (no auth required)"
)
async def get_password_status_endpoint(
    domain: str,
    db: Session = Depends(get_db)
):
    """
    Check if domain has passwords set.

    Public endpoint - no authentication required.
    Used by frontend to determine if password prompt needed.
    """
    status = check_password_status(db, domain)
    return PasswordStatusResponse(**status)


# Global Admin Endpoints

@router.get(
    "/api/admin/domains-auth",
    response_model=List[DomainAuthStatusResponse],
    summary="Get auth status for all domains (global admin only)"
)
async def get_all_domains_auth_endpoint(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """
    Get password status for all domains.

    Requires global admin password authentication.
    """
    statuses = get_all_domains_auth_status(db)
    return [DomainAuthStatusResponse(**s) for s in statuses]


@router.patch(
    "/api/admin/domains/{domain}/passwords",
    summary="Set domain passwords (global admin only)"
)
async def set_domain_passwords_endpoint(
    domain: str,
    request: SetDomainPasswordsRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """
    Set or remove domain passwords (global admin access).

    Requires global admin password authentication.
    Can set/remove both admin and user passwords in one request.
    """
    results = []

    # Handle admin password
    if request.remove_admin_password:
        success, error = remove_admin_password(db, domain)
        if not success:
            raise HTTPException(status_code=400, detail=f"Admin password removal failed: {error}")
        results.append("Admin password removed")
    elif request.admin_password:
        success, error = set_admin_password(db, domain, request.admin_password)
        if not success:
            raise HTTPException(status_code=400, detail=f"Admin password set failed: {error}")
        results.append("Admin password set")

    # Handle user password
    if request.remove_user_password:
        success, error = remove_user_password(db, domain)
        if not success:
            raise HTTPException(status_code=400, detail=f"User password removal failed: {error}")
        results.append("User password removed")
    elif request.user_password:
        success, error = set_user_password(db, domain, request.user_password)
        if not success:
            raise HTTPException(status_code=400, detail=f"User password set failed: {error}")
        results.append("User password set")

    if not results:
        return {"success": True, "message": "No changes requested"}

    return {"success": True, "message": ", ".join(results)}
