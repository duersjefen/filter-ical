"""
Domain Calendar Setup (I/O Shell)
Ensures domain calendars exist in database on startup.
"""
from sqlmodel import Session, select
from pathlib import Path
import yaml
from typing import List

from ..database import get_session_sync
from ..models import Calendar
from .domain_calendar import get_domain_calendar_id, generate_calendar_id
from .domains import load_domains_config


def ensure_domain_calendars_exist():
    """
    Ensure all configured domain calendars exist in database.
    Creates them if they don't exist, updates URLs if they changed.
    """
    print("🔍 Checking domain calendar configuration...")
    
    try:
        config_path = Path(__file__).parent.parent / "config" / "domains.yaml"
        if not config_path.exists():
            print("⚠️  No domains.yaml config found")
            return
            
        domains_config = load_domains_config(str(config_path))
        if 'domains' not in domains_config:
            print("⚠️  No domains configured")
            return
        
        session = get_session_sync()
        try:
            created_count = 0
            updated_count = 0
            
            for domain_id, domain_config in domains_config['domains'].items():
                calendar_url = domain_config.get('calendar_url', '')
                calendar_name = domain_config.get('name', f"{domain_id.title()} Calendar")
                
                if not calendar_url:
                    print(f"⚠️  Domain {domain_id} has no calendar_url")
                    continue
                
                # Check if domain calendar exists
                domain_calendar_id = get_domain_calendar_id(domain_id)
                existing_calendar = session.exec(
                    select(Calendar).where(Calendar.id == domain_calendar_id)
                ).first()
                
                if existing_calendar:
                    # Update if URL changed
                    if existing_calendar.url != calendar_url:
                        print(f"🔄 Updating domain calendar {domain_id} URL")
                        existing_calendar.url = calendar_url
                        existing_calendar.name = calendar_name
                        # Clear cache to force refresh
                        existing_calendar.cached_ical_content = None
                        existing_calendar.cache_updated_at = None
                        existing_calendar.cache_expires_at = None
                        session.add(existing_calendar)
                        updated_count += 1
                else:
                    # Create new domain calendar
                    print(f"➕ Creating domain calendar for {domain_id}")
                    new_calendar = Calendar(
                        id=domain_calendar_id,
                        name=calendar_name,
                        url=calendar_url,
                        user_id='public',
                        domain_id=domain_id
                    )
                    session.add(new_calendar)
                    created_count += 1
            
            session.commit()
            
            if created_count > 0 or updated_count > 0:
                print(f"✅ Domain calendars: {created_count} created, {updated_count} updated")
            else:
                print("✅ All domain calendars up to date")
                
        except Exception as e:
            print(f"❌ Error setting up domain calendars: {e}")
            session.rollback()
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Error loading domain configuration: {e}")


def list_domain_calendars() -> List[Calendar]:
    """
    Get all domain calendars from database.
    Utility function for monitoring and debugging.
    
    Returns:
        List of domain calendar objects
    """
    session = get_session_sync()
    try:
        domain_calendars = session.exec(
            select(Calendar).where(Calendar.domain_id != None)
        ).all()
        return list(domain_calendars)
    finally:
        session.close()


def force_refresh_domain_calendar(domain_id: str) -> bool:
    """
    Force immediate refresh of a specific domain calendar.
    Clears cache and marks for immediate update.
    
    Args:
        domain_id: Domain identifier (e.g., "exter")
        
    Returns:
        True if calendar was found and marked for refresh
    """
    session = get_session_sync()
    try:
        domain_calendar_id = get_domain_calendar_id(domain_id)
        calendar = session.exec(
            select(Calendar).where(Calendar.id == domain_calendar_id)
        ).first()
        
        if not calendar:
            return False
        
        # Clear cache to force refresh
        calendar.cached_ical_content = None
        calendar.cache_updated_at = None
        calendar.cache_expires_at = None
        calendar.cached_content_hash = None
        
        session.add(calendar)
        session.commit()
        
        print(f"🔄 Domain calendar {domain_id} marked for immediate refresh")
        return True
        
    except Exception as e:
        print(f"❌ Error refreshing domain calendar {domain_id}: {e}")
        session.rollback()
        return False
    finally:
        session.close()