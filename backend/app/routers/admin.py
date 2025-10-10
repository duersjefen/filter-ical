"""
Admin router - Password-protected endpoints for managing domain requests.

CONTRACT-DRIVEN: Implementation matches OpenAPI specification exactly.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import re
import httpx
import yaml
from pathlib import Path

from ..core.database import get_db
from ..core.auth import verify_admin_password, create_admin_token, verify_admin_auth
from ..models.domain_request import DomainRequest, RequestStatus
from ..models.calendar import Calendar
from ..models.domain import Domain
from ..routers.domain_requests import DomainRequestResponse
from ..data.ical_parser import parse_ical_content
from ..core.config import settings
from ..models.admin_password_reset import AdminPasswordResetToken
import secrets

router = APIRouter()


class AdminLoginRequest(BaseModel):
    """Request body for admin login."""
    password: str


class AdminLoginResponse(BaseModel):
    """Response for successful admin login."""
    token: str
    expires_in_days: int


class ApproveRequestBody(BaseModel):
    """Optional body for approve request."""
    domain_key: Optional[str] = None
    send_email: bool = True
    message: Optional[str] = None


class RejectRequestBody(BaseModel):
    """Optional body for reject request."""
    reason: Optional[str] = None
    send_email: bool = True


def generate_domain_key(username: str, db: Session) -> str:
    """
    Generate a unique domain key from username.

    Args:
        username: User's username
        db: Database session

    Returns:
        Unique domain key
    """
    # Sanitize username to valid domain key format
    base_key = re.sub(r'[^a-z0-9_-]', '_', username.lower())

    # Ensure uniqueness by checking domains table
    domain_key = base_key
    counter = 1
    while db.query(Domain).filter(Domain.domain_key == domain_key).first():
        domain_key = f"{base_key}_{counter}"
        counter += 1

    return domain_key


@router.post(
    "/admin/login",
    response_model=AdminLoginResponse,
    summary="Admin login to get JWT token",
    description="Authenticate with admin password and receive a JWT token valid for 30 days"
)
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with admin password and get a JWT token.

    Returns a token that can be used for 30 days without re-entering the password.
    Password is stored in database (admin_settings table).
    """
    from ..core.config import settings
    from ..models.admin import AdminSettings
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Get admin password from database
    admin_settings = db.query(AdminSettings).filter(AdminSettings.id == 1).first()

    if not admin_settings:
        # First-time login: seed password from .env to database
        # Verify against .env password
        is_password_correct = secrets.compare_digest(
            request.password.encode("utf-8"),
            settings.admin_password.encode("utf-8")
        )

        if is_password_correct:
            # Seed database with .env password
            admin_settings = AdminSettings(
                id=1,
                password_hash=pwd_context.hash(settings.admin_password)
            )
            db.add(admin_settings)
            db.commit()
    else:
        # Verify password against database hash
        is_password_correct = pwd_context.verify(request.password, admin_settings.password_hash)

    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password"
        )

    # Generate JWT token with 30-day expiry
    token = create_admin_token(expiry_days=30)

    return AdminLoginResponse(
        token=token,
        expires_in_days=30
    )


@router.get(
    "/admin/domain-requests",
    response_model=List[DomainRequestResponse],
    summary="List all domain requests (admin only)",
    description="Get all domain requests with optional status filtering"
)
async def list_domain_requests(
    status_filter: Optional[RequestStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
) -> List[DomainRequest]:
    """
    List all domain requests (admin only).

    Requires JWT token or password authentication.
    """
    query = db.query(DomainRequest)

    if status_filter:
        query = query.filter(DomainRequest.status == status_filter)

    # Order by created_at DESC (newest first)
    requests = query.order_by(DomainRequest.created_at.desc()).all()

    return requests


@router.patch(
    "/admin/domain-requests/{request_id}/approve",
    summary="Approve a domain request (admin only)",
    description="Approve the request and automatically create domain calendar"
)
async def approve_domain_request(
    request_id: int,
    body: Optional[ApproveRequestBody] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Approve a domain request and create the domain calendar.

    Requires admin password authentication.
    """
    # Get request
    domain_request = db.query(DomainRequest).filter(DomainRequest.id == request_id).first()
    if not domain_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain request not found"
        )

    # Check if already reviewed
    if domain_request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {domain_request.status.value}"
        )

    # Use requested domain key or allow admin override
    if body and body.domain_key:
        domain_key = body.domain_key
    else:
        domain_key = domain_request.requested_domain_key

    # Check if domain key already exists
    existing_domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Domain key '{domain_key}' already exists"
        )

    try:
        # 1. Create domain record first
        domain = Domain(
            domain_key=domain_key,
            name=f"{domain_request.username}'s Calendar",
            calendar_url=domain_request.calendar_url,
            owner_id=domain_request.user_id,  # Assign requesting user as owner
            admin_password_hash=domain_request.default_password,  # Already encrypted
            user_password_hash=None,
            status='active'
        )
        db.add(domain)
        db.flush()  # Get domain.id before creating calendar

        # 2. Create domain calendar
        calendar = Calendar(
            name=f"{domain_request.username}'s Calendar",
            source_url=domain_request.calendar_url,
            type="domain",
            user_id=None  # Domain calendars have no owner
        )
        db.add(calendar)
        db.flush()  # Get calendar.id

        # 3. Link domain to calendar
        domain.calendar_id = calendar.id

        # 4. Set initial password (already encrypted from domain request)
        domain.admin_password_hash = domain_request.default_password
        domain.user_password_hash = None

        # 5. Update request status
        domain_request.status = RequestStatus.APPROVED
        domain_request.reviewed_at = func.now()
        domain_request.domain_key = domain_key

        db.commit()
        db.refresh(domain)

        # 6. Sync calendar events from source URL
        from ..services.calendar_service import sync_calendar_events
        try:
            success, event_count, error = await sync_calendar_events(db, calendar)
            if success:
                print(f"✅ Synced {event_count} events for domain '{domain_key}'")
            else:
                print(f"⚠️ Failed to sync events for domain '{domain_key}': {error}")
        except Exception as e:
            print(f"⚠️ Exception during calendar sync: {e}")

        # 7. Send email notification if requested
        if body and body.send_email:
            from ..services.email_service import send_domain_approval_email
            try:
                custom_message = body.message if body and body.message else None
                await send_domain_approval_email(domain_request, domain_key, custom_message)
            except Exception as e:
                # Log but don't fail approval if email fails
                print(f"Warning: Failed to send approval email: {e}")

        return {
            "success": True,
            "message": "Domain request approved and domain created",
            "domain_key": domain_key,
            "calendar_id": calendar.id,
            "domain_id": domain.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve request: {str(e)}"
        )


@router.patch(
    "/admin/domain-requests/{request_id}/reject",
    summary="Reject a domain request (admin only)",
    description="Reject the domain request with optional reason"
)
async def reject_domain_request(
    request_id: int,
    body: Optional[RejectRequestBody] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Reject a domain request.

    Requires admin password authentication.
    """
    # Get request
    domain_request = db.query(DomainRequest).filter(DomainRequest.id == request_id).first()
    if not domain_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain request not found"
        )

    # Check if already reviewed
    if domain_request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {domain_request.status.value}"
        )

    try:
        # Update request status
        domain_request.status = RequestStatus.REJECTED
        domain_request.reviewed_at = func.now()

        rejection_reason = ""
        if body and body.reason:
            domain_request.rejection_reason = body.reason
            rejection_reason = body.reason

        db.commit()

        # Send email notification if requested
        if body and body.send_email and rejection_reason:
            from ..services.email_service import send_domain_rejection_email
            try:
                await send_domain_rejection_email(domain_request, rejection_reason)
            except Exception as e:
                # Log but don't fail rejection if email fails
                print(f"Warning: Failed to send rejection email: {e}")

        return {
            "success": True,
            "message": "Domain request rejected"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject request: {str(e)}"
        )


@router.delete(
    "/admin/domains/{domain_key}",
    summary="Delete a domain (admin only)",
    description="Delete domain and all associated data (calendar, auth, filters, groups)"
)
async def delete_domain(
    domain_key: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Delete a domain and cascade delete all related records.

    Requires admin password authentication.
    """
    # Get domain
    domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{domain_key}' not found"
        )

    try:
        # Delete calendar if exists (cascade will handle events)
        if domain.calendar_id:
            db.query(Calendar).filter(Calendar.id == domain.calendar_id).delete()

        # Delete domain (cascade will handle groups, filters, etc via FK)
        db.delete(domain)

        db.commit()

        return {
            "success": True,
            "message": f"Domain '{domain_key}' deleted successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete domain: {str(e)}"
        )


class CreateDomainRequest(BaseModel):
    """Request body for direct domain creation by admin."""
    domain_key: str
    name: str
    calendar_url: str
    admin_password: str  # Required
    user_password: Optional[str] = None
    owner_username: Optional[str] = None


@router.post(
    "/admin/domains",
    status_code=status.HTTP_201_CREATED,
    summary="Create domain directly (admin only)",
    description="Allows admin to create a domain without going through the request/approval process"
)
async def create_domain_directly(
    domain_data: CreateDomainRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Create a domain directly without request/approval process.

    Requires admin authentication. Optionally assign to a user as owner.
    """
    from app.models.user import User
    from app.data.domain_auth import encrypt_password
    from app.core.config import settings

    # Validate domain key format
    if not re.match(r'^[a-z0-9-]+$', domain_data.domain_key):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Domain key must contain only lowercase letters, numbers, and hyphens"
        )

    # Validate URL format
    if not domain_data.calendar_url.startswith(('http://', 'https://')):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Calendar URL must start with http:// or https://"
        )

    # Validate iCal URL by fetching and parsing it
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(domain_data.calendar_url)
            response.raise_for_status()
            ical_content = response.text

        # Parse iCal content to verify it's valid
        success, events, error = parse_ical_content(ical_content)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid iCal URL: {error}"
            )

        if not events:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Calendar URL is valid but contains no events"
            )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to fetch calendar: HTTP {e.response.status_code}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Calendar URL timed out - URL took too long to respond"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to fetch calendar: {str(e)}"
        )
    except HTTPException:
        # Re-raise our own HTTPExceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to validate calendar URL: {str(e)}"
        )

    # Validate admin password length
    if len(domain_data.admin_password) < 4:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Admin password must be at least 4 characters"
        )

    # Check if domain key already exists
    existing_domain = db.query(Domain).filter(Domain.domain_key == domain_data.domain_key).first()
    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Domain key '{domain_data.domain_key}' already exists"
        )

    # Owner assignment removed from creation - domains are created without owner
    # Owner can be assigned later via separate endpoint
    owner_id = None
    owner_username = None

    # Encrypt passwords
    admin_password_hash = encrypt_password(domain_data.admin_password, settings.password_encryption_key)
    user_password_hash = None
    if domain_data.user_password:
        user_password_hash = encrypt_password(domain_data.user_password, settings.password_encryption_key)

    try:
        # 1. Create domain record
        domain = Domain(
            domain_key=domain_data.domain_key,
            name=domain_data.name,
            calendar_url=domain_data.calendar_url,
            owner_id=owner_id,
            admin_password_hash=admin_password_hash,
            user_password_hash=user_password_hash,
            status='active'
        )
        db.add(domain)
        db.flush()  # Get domain.id

        # 2. Create domain calendar
        calendar = Calendar(
            name=domain_data.name,
            source_url=domain_data.calendar_url,
            type="domain",
            user_id=None  # Domain calendars have no user owner
        )
        db.add(calendar)
        db.flush()  # Get calendar.id

        # 3. Link domain to calendar
        domain.calendar_id = calendar.id

        db.commit()
        db.refresh(domain)

        # 4. Sync calendar events from source URL
        from app.services.calendar_service import sync_calendar_events
        try:
            success, event_count, error = await sync_calendar_events(db, calendar)
            if success:
                print(f"✅ Synced {event_count} events for domain '{domain_data.domain_key}'")
            else:
                print(f"⚠️ Failed to sync events for domain '{domain_data.domain_key}': {error}")
        except Exception as e:
            print(f"⚠️ Exception during calendar sync: {e}")

        return {
            "success": True,
            "message": f"Domain '{domain_data.domain_key}' created successfully",
            "domain_key": domain.domain_key,
            "name": domain.name,
            "calendar_url": domain.calendar_url,
            "domain_id": domain.id,
            "calendar_id": calendar.id,
            "owner_username": owner_username,
            "has_admin_password": admin_password_hash is not None,
            "has_user_password": user_password_hash is not None
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create domain: {str(e)}"
        )


@router.get(
    "/admin/users/search",
    summary="Search users (admin only)",
    description="Search for users by username or email"
)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Search for users by username or email.

    Returns matching users for assignment operations.
    """
    from app.models.user import User

    # Search by username or email (case-insensitive)
    users = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) |
        (User.email.ilike(f"%{q}%"))
    ).limit(limit).all()

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
            for user in users
        ]
    }


class AssignOwnerRequest(BaseModel):
    """Request body for assigning domain owner."""
    user_id: Optional[int] = None  # None to remove owner


@router.patch(
    "/admin/domains/{domain_key}/owner",
    summary="Assign domain owner (admin only)",
    description="Assign or remove domain owner"
)
async def assign_domain_owner(
    domain_key: str,
    request: AssignOwnerRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_auth)
):
    """
    Assign or remove domain owner.

    Set user_id to null to remove owner.
    """
    from app.models.user import User

    # Get domain
    domain = db.query(Domain).filter(Domain.domain_key == domain_key).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{domain_key}' not found"
        )

    # If user_id provided, verify user exists
    owner_username = None
    if request.user_id:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        domain.owner_id = user.id
        owner_username = user.username
    else:
        # Remove owner
        domain.owner_id = None

    try:
        db.commit()
        db.refresh(domain)

        return {
            "success": True,
            "message": f"Owner {'assigned' if request.user_id else 'removed'} successfully",
            "domain_key": domain_key,
            "owner_id": domain.owner_id,
            "owner_username": owner_username
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign owner: {str(e)}"
        )


# Domain YAML Configuration Management Endpoints

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
    from ..core.database import get_db
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


class SeedDomainRequest(BaseModel):
    """Request body for seeding domain from YAML."""
    force_reseed: bool = False


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
    from ..data.domain_auth import encrypt_password

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


# Admin Password Reset Endpoints

@router.post(
    "/admin/request-password-reset",
    summary="Request admin password reset email",
    description="Send password reset link to configured admin email address"
)
async def request_admin_password_reset(db: Session = Depends(get_db)):
    """
    Request admin password reset email.

    Sends reset link to ADMIN_EMAIL (info@paiss.me).
    Always returns success to prevent email enumeration.
    """
    try:
        # Check if admin email is configured
        if not settings.admin_email:
            # Still return success to prevent enumeration
            return {
                "success": True,
                "message": "If an admin account exists, a password reset email has been sent"
            }

        # Create reset token
        reset_token = AdminPasswordResetToken.create_token()
        db.add(reset_token)
        db.commit()
        db.refresh(reset_token)

        # Send email
        from ..services.email_service import send_admin_password_reset_email
        try:
            await send_admin_password_reset_email(
                email=settings.admin_email,
                reset_token=reset_token.token
            )
        except Exception as e:
            print(f"⚠️ Failed to send password reset email: {e}")
            # Still return success to prevent enumeration

        return {
            "success": True,
            "message": "If an admin account exists, a password reset email has been sent"
        }

    except Exception as e:
        print(f"⚠️ Password reset request error: {e}")
        # Still return success to prevent enumeration
        return {
            "success": True,
            "message": "If an admin account exists, a password reset email has been sent"
        }


@router.post(
    "/admin/reset-password",
    summary="Reset admin password with token",
    description="Reset admin password using token from email"
)
async def reset_admin_password(
    reset_data: dict,
    db: Session = Depends(get_db)
):
    """
    Reset admin password using token from email.

    Validates token and updates ADMIN_PASSWORD environment variable hint.
    """
    # Validate request
    if "token" not in reset_data or "new_password" not in reset_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="token and new_password are required"
        )

    token_string = reset_data["token"]
    new_password = reset_data["new_password"]

    # Validate password length
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long"
        )

    # Find token
    token = db.query(AdminPasswordResetToken).filter(
        AdminPasswordResetToken.token == token_string
    ).first()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Validate token
    if not token.is_valid:
        if token.used:
            detail = "Reset token has already been used"
        else:
            detail = "Reset token has expired"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

    try:
        from ..models.admin import AdminSettings
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Get or create admin settings
        admin_settings = db.query(AdminSettings).filter(AdminSettings.id == 1).first()

        if not admin_settings:
            # Create admin settings if it doesn't exist (shouldn't happen after migration)
            admin_settings = AdminSettings(
                id=1,
                password_hash=pwd_context.hash(new_password)
            )
            db.add(admin_settings)
        else:
            # Update password hash in database
            admin_settings.password_hash = pwd_context.hash(new_password)

        # Mark token as used
        token.used = 1

        # Commit all changes
        db.commit()

        return {
            "success": True,
            "message": "Admin password reset successfully. Your new password is now active."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )
