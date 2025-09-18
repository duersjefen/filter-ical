"""
Background Task Management (I/O Shell)
Handles periodic calendar updates and filter regeneration.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import List
import logging

from ..database import get_session_sync
from ..models import Calendar, FilteredCalendar, Event
from ..core.ical_parser import fetch_ical_content, parse_calendar_events
from ..core.cache import needs_cache_update, create_cache_data
from ..core.domain_calendar import is_domain_calendar
from ..core.filter_regeneration import (
    get_filtered_calendars_needing_regeneration,
    regenerate_single_filtered_calendar,
    mark_all_dependent_filters_for_regeneration
)
from ..core.retry_handler import execute_with_retry, CircuitBreaker
from ..core.cache import is_significant_change


# Configure logging for background tasks
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manages periodic background tasks for calendar updates"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            job_defaults={
                'coalesce': False,
                'max_instances': 1
            }
        )
        
        # Circuit breaker for external calendar fetching
        self.calendar_fetch_circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=300  # 5 minutes
        )
        
    def start(self):
        """Start the background task scheduler"""
        logger.info("🚀 Starting background task scheduler")
        
        # Schedule domain calendar updates every 5 minutes
        self.scheduler.add_job(
            func=self.update_domain_calendars,
            trigger='interval',
            minutes=5,
            id='update_domain_calendars',
            name='Update Domain Calendars'
        )
        
        # Schedule filtered calendar regeneration every minute (to handle pending ones)
        self.scheduler.add_job(
            func=self.regenerate_filtered_calendars,
            trigger='interval',
            minutes=1,
            id='regenerate_filtered_calendars',
            name='Regenerate Filtered Calendars'
        )
        
        # Schedule cache cleanup every hour
        self.scheduler.add_job(
            func=self.cleanup_old_cache_entries,
            trigger='interval',
            hours=1,
            id='cleanup_cache',
            name='Cache Cleanup'
        )
        
        self.scheduler.start()
        logger.info("✅ Background task scheduler started")
        
    def stop(self):
        """Stop the background task scheduler"""
        logger.info("🛑 Stopping background task scheduler")
        self.scheduler.shutdown()
        
    async def update_domain_calendars(self):
        """Update all domain calendars from external sources"""
        logger.info("🔄 Starting domain calendar updates")
        
        session = get_session_sync()
        try:
            # Get all domain calendars
            domain_calendars = session.exec(
                select(Calendar).where(Calendar.domain_id != None)
            ).all()
            
            updated_count = 0
            for calendar in domain_calendars:
                if await self._update_single_calendar(calendar, session):
                    updated_count += 1
            
            logger.info(f"✅ Updated {updated_count}/{len(domain_calendars)} domain calendars")
            
        except Exception as e:
            logger.error(f"❌ Error updating domain calendars: {e}")
        finally:
            session.close()
    
    async def _update_single_calendar(self, calendar: Calendar, session: Session) -> bool:
        """Update a single calendar's cached data and events"""
        try:
            # Check circuit breaker
            if not self.calendar_fetch_circuit_breaker.can_proceed():
                logger.warning(f"⚠️ Circuit breaker open, skipping calendar {calendar.id}")
                return False
            
            # Fetch fresh content with retry logic
            def fetch_operation():
                content, error = fetch_ical_content(calendar.url)
                if error:
                    raise Exception(f"Failed to fetch calendar: {error}")
                return content
            
            fresh_content, error = execute_with_retry(
                fetch_operation,
                max_attempts=2,
                base_delay=5.0,
                operation_name=f"fetch calendar {calendar.id}"
            )
            
            if error:
                self.calendar_fetch_circuit_breaker.on_failure()
                logger.error(f"❌ Failed to fetch calendar {calendar.id} after retries: {error}")
                return False
            
            # Check if content significantly changed (performance optimization)
            old_content = getattr(calendar, 'cached_ical_content', None)
            if not is_significant_change(old_content, fresh_content, threshold=0.98):
                logger.debug(f"📦 Calendar {calendar.id} content unchanged (similarity check)")
                self.calendar_fetch_circuit_breaker.on_success()
                return False
            
            logger.info(f"💾 Updating calendar {calendar.id} with significantly changed content")
            
            # Update cache
            cache_data = create_cache_data(fresh_content)
            for key, value in cache_data.items():
                setattr(calendar, key, value)
            
            # Clear existing events
            existing_events = session.exec(
                select(Event).where(Event.calendar_id == calendar.id)
            ).all()
            for event in existing_events:
                session.delete(event)
            
            # Parse and store new events
            events_data, parse_error = parse_calendar_events(fresh_content, calendar.id)
            if not parse_error and events_data:
                for event_data in events_data:
                    event = Event(**event_data)
                    session.add(event)
            
            # Mark dependent filtered calendars for regeneration
            mark_all_dependent_filters_for_regeneration(calendar.id, session)
            
            session.add(calendar)
            session.commit()
            
            # Record successful fetch
            self.calendar_fetch_circuit_breaker.on_success()
            
            logger.info(f"✅ Calendar {calendar.id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating calendar {calendar.id}: {e}")
            session.rollback()
            return False
    
    async def regenerate_filtered_calendars(self):
        """Regenerate filtered calendars that need updating"""
        session = get_session_sync()
        try:
            # Get filtered calendars that need regeneration
            pending_filters = get_filtered_calendars_needing_regeneration(session)
            
            if not pending_filters:
                return
            
            logger.info(f"🔄 Regenerating {len(pending_filters)} filtered calendars")
            
            regenerated_count = 0
            for filtered_calendar in pending_filters:
                if regenerate_single_filtered_calendar(filtered_calendar, session):
                    regenerated_count += 1
            
            logger.info(f"✅ Regenerated {regenerated_count}/{len(pending_filters)} filtered calendars")
            
        except Exception as e:
            logger.error(f"❌ Error regenerating filtered calendars: {e}")
        finally:
            session.close()
    
    async def cleanup_old_cache_entries(self):
        """Clean up old cached data to prevent database bloat"""
        logger.info("🧹 Starting cache cleanup")
        
        session = get_session_sync()
        try:
            # Find calendars with expired cache entries (older than 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            old_cached_calendars = session.exec(
                select(Calendar).where(
                    Calendar.cached_ical_content != None,
                    Calendar.cache_updated_at < cutoff_time
                )
            ).all()
            
            cleaned_count = 0
            for calendar in old_cached_calendars:
                # Only clean if it's not a domain calendar (we want to keep those cached)
                if not calendar.domain_id:
                    calendar.cached_ical_content = None
                    calendar.cached_content_hash = None
                    calendar.cache_updated_at = None
                    calendar.cache_expires_at = None
                    session.add(calendar)
                    cleaned_count += 1
            
            if cleaned_count > 0:
                session.commit()
                logger.info(f"🧹 Cleaned up {cleaned_count} old cache entries")
            else:
                logger.info("🧹 No old cache entries to clean up")
                
        except Exception as e:
            logger.error(f"❌ Error during cache cleanup: {e}")
            session.rollback()
        finally:
            session.close()
    
    def get_status(self) -> dict:
        """Get current status of background tasks for monitoring"""
        return {
            "scheduler_running": self.scheduler.running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ],
            "circuit_breaker": self.calendar_fetch_circuit_breaker.get_status()
        }


# Global instance
background_manager = BackgroundTaskManager()