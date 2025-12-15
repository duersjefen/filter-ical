"""
Domain groups router for DynamoDB backend.

Implements group management endpoints.
"""

from fastapi import APIRouter, HTTPException, Body

from .deps import get_repo, get_verified_domain_ddb

router = APIRouter()


@router.get("/{domain}/groups")
async def get_domain_groups(domain: str):
    """Get groups for domain calendar."""
    domain_obj = await get_verified_domain_ddb(domain)

    groups_response = []
    for group in domain_obj.groups:
        groups_response.append({
            "id": group.id,
            "name": group.name,
            "domain_key": domain_obj.domain_key
        })

    return groups_response


@router.post("/{domain}/groups")
async def create_domain_group(domain: str, group_data: dict = Body(...)):
    """Create a new group."""
    await get_verified_domain_ddb(domain)

    if "name" not in group_data:
        raise HTTPException(status_code=400, detail="Group name is required")

    repo = get_repo()
    group = repo.add_group(domain, group_data["name"])

    if not group:
        raise HTTPException(status_code=400, detail="Failed to create group")

    return {
        "id": group.id,
        "name": group.name,
        "domain_key": domain
    }


@router.put("/{domain}/groups/{group_id}")
async def update_domain_group(domain: str, group_id: int, group_data: dict = Body(...)):
    """Update group name."""
    await get_verified_domain_ddb(domain)

    if "name" not in group_data:
        raise HTTPException(status_code=400, detail="Group name is required")

    repo = get_repo()
    group = repo.update_group(domain, group_id, group_data["name"])

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return {
        "id": group.id,
        "name": group.name,
        "domain_key": domain
    }


@router.delete("/{domain}/groups/{group_id}")
async def delete_domain_group(domain: str, group_id: int):
    """Delete a group."""
    await get_verified_domain_ddb(domain)

    repo = get_repo()
    success = repo.delete_group(domain, group_id)

    if not success:
        raise HTTPException(status_code=404, detail="Group not found")

    return {"success": True, "message": "Group deleted"}
