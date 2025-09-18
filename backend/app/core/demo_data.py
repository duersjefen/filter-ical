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
    """Create demo calendar data for showcasing"""
    return {
        "id": "exter",
        "name": "Exter Kalendar",
        "url": "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics",
        "user_id": "public",
        "created_at": datetime.now()
    }


def create_demo_groups() -> List[Dict[str, Any]]:
    """Create demo group hierarchy for showcasing"""
    return [
        # Top-level groups
        {
            "id": "group_meetings",
            "name": "Meetings",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "All types of meetings and conferences"
        },
        {
            "id": "group_training",
            "name": "Training & Development",
            "domain_id": "exter", 
            "parent_group_id": None,
            "description": "Learning and skill development events"
        },
        {
            "id": "group_social",
            "name": "Social Events",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Team building and social activities"
        },
        
        # Nested groups under Meetings
        {
            "id": "group_meetings_weekly",
            "name": "Weekly Stand-ups",
            "domain_id": "exter",
            "parent_group_id": "group_meetings",
            "description": "Regular team synchronization meetings"
        },
        {
            "id": "group_meetings_quarterly",
            "name": "Quarterly Reviews",
            "domain_id": "exter",
            "parent_group_id": "group_meetings",
            "description": "Business performance reviews"
        },
        
        # Nested groups under Training
        {
            "id": "group_training_tech",
            "name": "Technical Training",
            "domain_id": "exter",
            "parent_group_id": "group_training",
            "description": "Programming and technology workshops"
        },
        {
            "id": "group_training_soft",
            "name": "Soft Skills",
            "domain_id": "exter",
            "parent_group_id": "group_training",
            "description": "Communication and leadership development"
        }
    ]


def create_demo_event_type_assignments() -> List[Dict[str, Any]]:
    """Create demo event type to group assignments"""
    return [
        # Meetings group assignments
        {"group_id": "group_meetings_weekly", "event_type": "Daily Standup", "domain_id": "exter"},
        {"group_id": "group_meetings_weekly", "event_type": "Sprint Planning", "domain_id": "exter"},
        {"group_id": "group_meetings_weekly", "event_type": "Team Sync", "domain_id": "exter"},
        {"group_id": "group_meetings_quarterly", "event_type": "Quarterly Review", "domain_id": "exter"},
        {"group_id": "group_meetings_quarterly", "event_type": "Board Meeting", "domain_id": "exter"},
        
        # Training group assignments  
        {"group_id": "group_training_tech", "event_type": "Code Review Workshop", "domain_id": "exter"},
        {"group_id": "group_training_tech", "event_type": "Architecture Discussion", "domain_id": "exter"},
        {"group_id": "group_training_tech", "event_type": "Technology Training", "domain_id": "exter"},
        {"group_id": "group_training_soft", "event_type": "Leadership Workshop", "domain_id": "exter"},
        {"group_id": "group_training_soft", "event_type": "Communication Training", "domain_id": "exter"},
        
        # Social events
        {"group_id": "group_social", "event_type": "Team Building", "domain_id": "exter"},
        {"group_id": "group_social", "event_type": "Company Party", "domain_id": "exter"},
        {"group_id": "group_social", "event_type": "Holiday Celebration", "domain_id": "exter"}
    ]


def seed_demo_data() -> bool:
    """
    Seed the database with demo data for showcasing
    Returns True if seeding was successful
    """
    try:
        session = get_session_sync()
        
        # 1. Create demo calendar if it doesn't exist
        existing_calendar = session.get(Calendar, "exter")
        if not existing_calendar:
            demo_calendar_data = create_demo_calendar_data()
            demo_calendar = Calendar(**demo_calendar_data)
            session.add(demo_calendar)
            session.commit()
            print("✅ Created demo calendar")
        else:
            print("📋 Demo calendar already exists")
        
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
    Check if demo data should be seeded
    Returns True if no demo groups exist for exter domain
    """
    try:
        session = get_session_sync()
        
        # Check if demo groups exist for exter domain
        existing_groups = session.exec(select(Group).where(Group.domain_id == "exter")).first()
        has_demo_groups = existing_groups is not None
        
        session.close()
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