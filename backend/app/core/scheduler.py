"""
Background task scheduler for calendar sync and cache warming.

IMPERATIVE SHELL - I/O orchestration with scheduled background tasks.
"""

import asyncio
from pathlib import Path
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from ..services.cache_service import warm_domain_cache
from ..services.domain_service import ensure_domain_calendar_exists, load_domains_config


# Global scheduler instance
_scheduler: BackgroundScheduler = None


def get_scheduler() -> BackgroundScheduler:
    """
    Get or create background scheduler.
    
    Returns:
        BackgroundScheduler instance
        
    I/O Operation - Scheduler management.
    """
    global _scheduler
    
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    
    return _scheduler


def get_domain_keys() -> List[str]:
    """
    Get list of configured domain keys from domains.yaml.
    
    Returns:
        List of domain keys
        
    I/O Operation - File read with configuration parsing.
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


def sync_domain_calendars_task():
    """
    Background task to sync all domain calendars and warm cache.
    
    This runs every 5 minutes to keep data fresh.
    
    I/O Operation - Database and cache operations.
    """
    try:
        print("🔄 Starting scheduled domain calendar sync...")
        
        # Get all configured domains
        domain_keys = get_domain_keys()
        if not domain_keys:
            print("⚠️ No domains configured for sync")
            return
        
        # Create database session
        db_generator = get_db()
        db: Session = next(db_generator)
        
        try:
            # Load domains configuration
            success, config, error = load_domains_config(settings.domains_config_path)
            if not success:
                print(f"❌ Failed to load domains config: {error}")
                return
            
            # Process each domain
            synced_count = 0
            cached_count = 0
            
            for domain_key in domain_keys:
                try:
                    # Ensure domain calendar exists and is synced
                    success, calendar, sync_error = asyncio.run(
                        ensure_domain_calendar_exists(db, domain_key, config)
                    )
                    
                    if success:
                        print(f"✅ Synced domain calendar: {domain_key}")
                        synced_count += 1
                        
                        # Warm cache for this domain
                        cache_success = warm_domain_cache(db, domain_key)
                        if cache_success:
                            print(f"🔥 Warmed cache for domain: {domain_key}")
                            cached_count += 1
                        else:
                            print(f"⚠️ Cache warming failed for domain: {domain_key}")
                    else:
                        print(f"❌ Failed to sync domain {domain_key}: {sync_error}")
                
                except Exception as domain_error:
                    print(f"❌ Error processing domain {domain_key}: {domain_error}")
                    continue
            
            print(f"📊 Sync completed: {synced_count} calendars synced, {cached_count} caches warmed")
            
        finally:
            # Ensure database session is closed
            db.close()
            
    except Exception as e:
        print(f"❌ Background sync task error: {e}")


def start_scheduler():
    """
    Start the background scheduler with domain sync task.
    
    I/O Operation - Scheduler startup.
    """
    try:
        scheduler = get_scheduler()
        
        # Add the domain sync task
        scheduler.add_job(
            sync_domain_calendars_task,
            trigger=IntervalTrigger(minutes=settings.actual_sync_interval_minutes),
            id="domain_calendar_sync",
            name="Domain Calendar Sync and Cache Warming",
            replace_existing=True
        )
        
        # Start the scheduler
        scheduler.start()
        print(f"🕒 Scheduler started: syncing every {settings.actual_sync_interval_minutes} minutes")
        
    except Exception as e:
        print(f"❌ Failed to start scheduler: {e}")


def stop_scheduler():
    """
    Stop the background scheduler.
    
    I/O Operation - Scheduler shutdown.
    """
    try:
        scheduler = get_scheduler()
        if scheduler.running:
            scheduler.shutdown(wait=True)
            print("🛑 Scheduler stopped")
            
    except Exception as e:
        print(f"❌ Failed to stop scheduler: {e}")


def trigger_manual_sync():
    """
    Trigger manual sync for testing/debugging.
    
    I/O Operation - Manual task execution.
    """
    try:
        print("🔄 Triggering manual domain sync...")
        sync_domain_calendars_task()
        print("✅ Manual sync completed")
        
    except Exception as e:
        print(f"❌ Manual sync failed: {e}")