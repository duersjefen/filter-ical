"""
Simple password-based authentication for admin endpoints.

Uses HTTP Basic Auth where the password is validated and username is ignored.
"""

import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import settings

security = HTTPBasic()


def verify_admin_password(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """
    Verify admin password from HTTP Basic Auth.

    Username is ignored - only password is validated against ADMIN_PASSWORD env var.

    Args:
        credentials: HTTP Basic Auth credentials

    Returns:
        True if password is correct

    Raises:
        HTTPException: If password is incorrect
    """
    # Use constant-time comparison to prevent timing attacks
    is_password_correct = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        settings.admin_password.encode("utf-8")
    )

    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True
