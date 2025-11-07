"""
Lambda handler for scheduled domain calendar sync task.

This function is triggered by EventBridge every 30 minutes to:
- Sync domain calendars from external sources
- Apply assignment rules to events
- Warm the cache for each domain

Replaces APScheduler background tasks from ECS Fargate deployment.
"""

import asyncio
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.services.cache_service import warm_domain_cache
from app.services.domain_service import (
    ensure_domain_calendar_exists,
    load_domains_config,
    auto_assign_events_with_rules
)


def get_domain_keys() -> List[str]:
    """
    Get list of configured domain keys from domains.yaml.

    Returns:
        List of domain keys
    """
    try:
        success, config, error = load_domains_config(settings.domains_config_path)

        if not success:
            print(f"Failed to load domains config: {error}")
            return []

        domain_keys = list(config.get("domains", {}).keys())
        return domain_keys

    except Exception as e:
        print(f"Error getting domain keys: {e}")
        return []


async def sync_all_domain_calendars(db: Session) -> Dict[str, Any]:
    """
    Sync all domain calendars and warm cache.

    Args:
        db: Database session

    Returns:
        Dictionary with sync results
    """
    print("🔄 Starting scheduled domain calendar sync...")

    # Get all configured domains
    domain_keys = get_domain_keys()
    if not domain_keys:
        print("⚠️ No domains configured for sync")
        return {
            "status": "warning",
            "message": "No domains configured",
            "synced": 0,
            "cached": 0,
        }

    # Load domains configuration
    success, config, error = load_domains_config(settings.domains_config_path)
    if not success:
        print(f"❌ Failed to load domains config: {error}")
        return {
            "status": "error",
            "message": f"Failed to load config: {error}",
            "synced": 0,
            "cached": 0,
        }

    # Process each domain
    synced_count = 0
    cached_count = 0
    errors = []

    for domain_key in domain_keys:
        try:
            # Ensure domain calendar exists and is synced
            success, calendar, sync_error = await ensure_domain_calendar_exists(db, domain_key)

            if success:
                print(f"✅ Synced domain calendar: {domain_key}")
                synced_count += 1

                # Apply assignment rules to newly synced events
                rule_success, assignment_count, rule_error = await auto_assign_events_with_rules(
                    db, domain_key
                )
                if rule_success and assignment_count > 0:
                    print(f"📋 Applied {assignment_count} assignment rules for domain: {domain_key}")
                elif not rule_success:
                    print(f"⚠️ Rule application failed for domain {domain_key}: {rule_error}")
                    errors.append(f"{domain_key}: {rule_error}")

                # Warm cache for this domain
                cache_success = warm_domain_cache(db, domain_key)
                if cache_success:
                    print(f"🔥 Warmed cache for domain: {domain_key}")
                    cached_count += 1
                else:
                    print(f"⚠️ Cache warming failed for domain: {domain_key}")
            else:
                print(f"❌ Failed to sync domain {domain_key}: {sync_error}")
                errors.append(f"{domain_key}: {sync_error}")

        except Exception as domain_error:
            print(f"❌ Error processing domain {domain_key}: {domain_error}")
            errors.append(f"{domain_key}: {str(domain_error)}")
            continue

    print(f"📊 Sync completed: {synced_count} calendars synced, {cached_count} caches warmed")

    return {
        "status": "success" if not errors else "partial",
        "synced": synced_count,
        "cached": cached_count,
        "errors": errors if errors else None,
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for EventBridge scheduled events.

    Args:
        event: EventBridge event (contains schedule info)
        context: Lambda context

    Returns:
        Dictionary with execution results
    """
    print(f"🚀 Lambda sync task started (request ID: {context.request_id})")
    print(f"📅 Event: {event.get('source', 'N/A')} - {event.get('detail-type', 'N/A')}")

    try:
        # Get database session
        db_generator = get_db()
        db: Session = next(db_generator)

        try:
            # Run sync operation
            result = asyncio.run(sync_all_domain_calendars(db))

            # Commit changes
            db.commit()

            print(f"✅ Sync completed successfully: {result}")
            return {
                "statusCode": 200,
                "body": result,
            }

        finally:
            # Ensure database session is closed
            db.close()

    except Exception as e:
        print(f"❌ Sync task error: {e}")
        return {
            "statusCode": 500,
            "body": {
                "status": "error",
                "message": str(e),
            },
        }
