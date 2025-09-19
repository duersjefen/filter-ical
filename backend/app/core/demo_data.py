"""
Demo Data Seeding System
Automatically creates showcase data after clean deployments
"""
from typing import List, Dict, Any
from sqlmodel import Session, select
from datetime import datetime
import uuid

from ..models import Calendar, Group, EventTypeGroup
from ..database import get_session_sync
from .domains import load_domains_config, domain_has_groups


def create_demo_calendar_data() -> Dict[str, Any]:
    """
    Create demo calendar data for showcasing.
    NOTE: This should only be used if domain calendar creation failed.
    Normally, cal_domain_exter is created by ensure_domain_calendars_exist()
    """
    return {
        "id": "cal_domain_exter",
        "name": "Exter Kalendar",
        "url": "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics",
        "user_id": "public",
        "domain_id": "exter",
        "created_at": datetime.now()
    }


def create_demo_groups() -> List[Dict[str, Any]]:
    """Create simple demo groups for KISS card-based interface (no nesting)"""
    return [
        # Simple flat groups - perfect for 3-card layout
        {
            "id": "group_music",
            "name": "🎵 Music Activities",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Bands, concerts, and musical events"
        },
        {
            "id": "group_sports",
            "name": "⚽ Sports & Recreation",
            "domain_id": "exter", 
            "parent_group_id": None,
            "description": "Sports activities and physical recreation"
        },
        {
            "id": "group_youth",
            "name": "👨‍👩‍👧‍👦 Youth & Family",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Activities for children, teenagers and families"
        },
        {
            "id": "group_seniors",
            "name": "👥 Senior Activities",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Programs and events for older adults"
        },
        {
            "id": "group_meetings",
            "name": "💼 Meetings & Events",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Community meetings and special events"
        },
        {
            "id": "group_education",
            "name": "📚 Education & Learning",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Educational activities and workshops"
        }
    ]


def create_demo_event_type_assignments() -> List[Dict[str, Any]]:
    """Create simple event type to group assignments for KISS interface"""
    return [
        # Music Activities - Real event types from Exter calendar
        {"group_id": "group_music", "event_type": "Musik Band", "domain_id": "exter"},
        {"group_id": "group_music", "event_type": "Youngsterband", "domain_id": "exter"},
        {"group_id": "group_music", "event_type": "Concert", "domain_id": "exter"},
        {"group_id": "group_music", "event_type": "Choir Practice", "domain_id": "exter"},
        
        # Sports Activities - Real event types
        {"group_id": "group_sports", "event_type": "Volleyball", "domain_id": "exter"},
        {"group_id": "group_sports", "event_type": "Eiszeit (Jugend)", "domain_id": "exter"},
        {"group_id": "group_sports", "event_type": "Sports Tournament", "domain_id": "exter"},
        {"group_id": "group_sports", "event_type": "Football Training", "domain_id": "exter"},
        
        # Youth & Family Activities - Real event types
        {"group_id": "group_youth", "event_type": "Tweens", "domain_id": "exter"},
        {"group_id": "group_youth", "event_type": "BUK-Abend", "domain_id": "exter"},
        {"group_id": "group_youth", "event_type": "Summer Camp", "domain_id": "exter"},
        {"group_id": "group_youth", "event_type": "Family Day", "domain_id": "exter"},
        
        # Senior Activities - Real event types
        {"group_id": "group_seniors", "event_type": "Ü60 Abend", "domain_id": "exter"},
        {"group_id": "group_seniors", "event_type": "Senior Coffee", "domain_id": "exter"},
        {"group_id": "group_seniors", "event_type": "Walking Group", "domain_id": "exter"},
        
        # Meetings & Events
        {"group_id": "group_meetings", "event_type": "Community Meeting", "domain_id": "exter"},
        {"group_id": "group_meetings", "event_type": "Annual Festival", "domain_id": "exter"},
        {"group_id": "group_meetings", "event_type": "Holiday Celebration", "domain_id": "exter"},
        {"group_id": "group_meetings", "event_type": "Fundraising Event", "domain_id": "exter"},
        
        # Education & Learning
        {"group_id": "group_education", "event_type": "Workshop", "domain_id": "exter"},
        {"group_id": "group_education", "event_type": "Language Class", "domain_id": "exter"},
        {"group_id": "group_education", "event_type": "Computer Course", "domain_id": "exter"}
    ]


def seed_demo_data() -> bool:
    """
    Seed the database with demo data for showcasing
    Returns True if seeding was successful
    """
    try:
        session = get_session_sync()
        
        # 1. Verify domain calendar exists (should be created by ensure_domain_calendars_exist)
        existing_calendar = session.get(Calendar, "cal_domain_exter")
        if not existing_calendar:
            print("⚠️  Domain calendar cal_domain_exter not found!")
            print("💡 Creating fallback demo calendar (ensure_domain_calendars_exist should have created this)")
            demo_calendar_data = create_demo_calendar_data()
            demo_calendar = Calendar(**demo_calendar_data)
            session.add(demo_calendar)
            session.commit()
            print("✅ Created fallback demo calendar")
        else:
            print("✅ Domain calendar cal_domain_exter exists")
        
        # 2. Create demo groups if they don't exist
        demo_groups_data = create_demo_groups()
        created_groups = 0
        
        for group_data in demo_groups_data:
            existing_group = session.get(Group, group_data["id"])
            if not existing_group:
                demo_group = Group(**group_data)
                session.add(demo_group)
                created_groups += 1
        
        if created_groups > 0:
            session.commit()
            print(f"✅ Created {created_groups} demo groups")
        else:
            print("📋 Demo groups already exist")
        
        # 3. Create event type assignments if they don't exist
        demo_assignments_data = create_demo_event_type_assignments()
        created_assignments = 0
        
        for assignment_data in demo_assignments_data:
            # Check if assignment already exists
            existing_assignment = session.exec(select(EventTypeGroup).where(
                EventTypeGroup.group_id == assignment_data["group_id"],
                EventTypeGroup.event_type == assignment_data["event_type"]
            )).first()
            
            if not existing_assignment:
                assignment = EventTypeGroup(
                    id=str(uuid.uuid4()),
                    **assignment_data
                )
                session.add(assignment)
                created_assignments += 1
        
        if created_assignments > 0:
            session.commit()
            print(f"✅ Created {created_assignments} demo event type assignments")
        else:
            print("📋 Demo event type assignments already exist")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error seeding demo data: {e}")
        return False


def should_seed_demo_data() -> bool:
    """
    Check if demo data should be seeded.
    Returns True if no demo groups exist for exter domain.
    
    NOTE: Domain calendar (cal_domain_exter) should be created by ensure_domain_calendars_exist()
    before this function is called during startup.
    """
    try:
        session = get_session_sync()
        
        # Check if demo groups exist for exter domain
        existing_groups = session.exec(select(Group).where(Group.domain_id == "exter")).first()
        has_demo_groups = existing_groups is not None
        
        session.close()
        
        # Seed if demo groups are missing
        return not has_demo_groups
        
    except Exception as e:
        print(f"❌ Error checking demo data: {e}")
        return False


def setup_demo_domain_config():
    """
    Ensure demo domain is configured with groups enabled
    This should be called during application startup
    """
    # This could be enhanced to automatically update domains.yaml
    # For now, we'll add manual instructions
    print("💡 To enable groups for demo data:")
    print("   Add 'demo.company.com' to domains.yaml with groups: true")
    print("   Or create a demo calendar with a supported domain URL")