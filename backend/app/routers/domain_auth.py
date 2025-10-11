"""
Domain authentication router - API endpoints for password-protected domains.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ..core.database import get_db
from ..core.auth import verify_admin_password, verify_admin_auth, require_user_auth
from ..core.messages import ErrorMessages, SuccessMessages
from ..services.domain_auth_service import (
    verify_domain_password,
    set_admin_password,
    set_user_password,
    remove_admin_password,
    remove_user_password,
    check_password_status,
    verify_token,
    get_all_domains_auth_status,
    get_decrypted_password
)
from ..services.domain_access_service import (
    check_user_has_domain_access,
    unlock_domain_for_user
)

router = APIRouter()


# Request/Response Models

class VerifyPasswordRequest(BaseModel):
    """Request body for password verification."""
    password: str


class VerifyPasswordResponse(BaseModel):
    """Response for successful password verification."""
    success: bool
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
    owner_id: Optional[int]
    owner_username: Optional[str]
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
            detail=ErrorMessages.AUTHORIZATION_HEADER_REQUIRED,
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.INVALID_AUTHORIZATION_HEADER,
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = authorization.replace("Bearer ", "")

    valid, token_data = verify_token(token, domain, "admin")

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.INVALID_OR_EXPIRED_TOKEN,
            headers={"WWW-Authenticate": "Bearer"}
        )

    return token_data


# Domain-level Endpoints

@router.post(
    "/api/domains/{domain}/auth/verify-admin",
    response_model=VerifyPasswordResponse,
    summary="Verify admin password (requires login)"
)
async def verify_admin_password_endpoint(
    domain: str,
    request: VerifyPasswordRequest,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """
    Verify admin password for domain and save access to user account.

    Requires user to be logged in. Password access is saved to database
    and follows the user across devices.
    """
    # Check if they already have access
    has_access = check_user_has_domain_access(db, user_id, domain, "admin")
    if has_access:
        return VerifyPasswordResponse(
            success=True,
            message=SuccessMessages.AUTH_ALREADY_AUTHENTICATED
        )

    # Verify password and save access
    unlock_success, error = unlock_domain_for_user(db, user_id, domain, request.password, "admin")

    if unlock_success:
        return VerifyPasswordResponse(
            success=True,
            message=SuccessMessages.AUTH_SUCCESSFUL
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )


@router.post(
    "/api/domains/{domain}/auth/verify-user",
    response_model=VerifyPasswordResponse,
    summary="Verify user password (requires login)"
)
async def verify_user_password_endpoint(
    domain: str,
    request: VerifyPasswordRequest,
    user_id: int = Depends(require_user_auth),
    db: Session = Depends(get_db)
):
    """
    Verify user password for domain and save access to user account.

    Requires user to be logged in. Password access is saved to database
    and follows the user across devices.
    """
    # Check if they already have access
    has_access = check_user_has_domain_access(db, user_id, domain, "user")
    if has_access:
        return VerifyPasswordResponse(
            success=True,
            message=SuccessMessages.AUTH_ALREADY_AUTHENTICATED
        )

    # Verify password and save access
    unlock_success, error = unlock_domain_for_user(db, user_id, domain, request.password, "user")

    if unlock_success:
        return VerifyPasswordResponse(
            success=True,
            message=SuccessMessages.AUTH_SUCCESSFUL
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
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
        return {"success": True, "message": SuccessMessages.ADMIN_PASSWORD_SET}
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
        return {"success": True, "message": SuccessMessages.USER_PASSWORD_SET}
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
        return {"success": True, "message": SuccessMessages.ADMIN_PASSWORD_REMOVED}
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
        return {"success": True, "message": SuccessMessages.USER_PASSWORD_REMOVED}
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
    _: bool = Depends(verify_admin_auth)
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
    _: bool = Depends(verify_admin_auth)
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
        return {"success": True, "message": SuccessMessages.NO_CHANGES_REQUESTED}

    return {"success": True, "message": ", ".join(results)}


@router.get(
    "/api/admin/domains/{domain}/password/{password_type}",
    summary="Get decrypted password for domain (global admin only)"
)
async def get_domain_password_endpoint(
    domain: str,
    password_type: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Get decrypted password for a domain.

    Requires global admin password authentication.
    password_type must be 'admin' or 'user'.
    """
    success, result = get_decrypted_password(db, domain, password_type)

    if success:
        return {"success": True, "password": result}
    else:
        raise HTTPException(status_code=400, detail=result)
