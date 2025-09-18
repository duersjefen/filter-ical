"""
Test demo data seeding functionality
"""
import pytest
from sqlmodel import Session, select

from app.core.demo_data import seed_demo_data, should_seed_demo_data
from app.models import Calendar, Group, EventTypeGroup
from app.database import get_session_sync


def test_demo_data_seeding(setup_test_database):
    """Test that demo data can be seeded correctly"""
    session = get_session_sync()
    
    # Initially, should need seeding
    assert should_seed_demo_data() == True
    
    # Seed the demo data
    success = seed_demo_data()
    assert success == True
    
    # After seeding, should not need seeding
    assert should_seed_demo_data() == False
    
    # Verify demo calendar exists
    demo_calendar = session.get(Calendar, "exter")
    assert demo_calendar is not None
    assert demo_calendar.name == "Exter Kalendar"
    
    # Verify demo groups exist
    demo_groups = session.exec(
        select(Group).where(Group.domain_id == "exter")
    ).all()
    assert len(demo_groups) == 7  # 3 top-level + 4 nested groups
    
    # Check specific groups exist
    group_names = [group.name for group in demo_groups]
    assert "Meetings" in group_names
    assert "Training & Development" in group_names
    assert "Social Events" in group_names
    assert "Weekly Stand-ups" in group_names
    assert "Quarterly Reviews" in group_names
    assert "Technical Training" in group_names
    assert "Soft Skills" in group_names
    
    # Verify event type assignments exist
    event_assignments = session.exec(
        select(EventTypeGroup)
    ).all()
    assert len(event_assignments) == 13  # Total assignments from demo data
    
    # Check specific event type assignments
    assignment_types = [assignment.event_type for assignment in event_assignments]
    assert "Daily Standup" in assignment_types
    assert "Sprint Planning" in assignment_types
    assert "Team Building" in assignment_types
    
    session.close()


def test_demo_data_idempotent(setup_test_database):
    """Test that seeding demo data multiple times doesn't create duplicates"""
    session = get_session_sync()
    
    # Seed twice
    seed_demo_data()
    seed_demo_data()
    
    # Should still have the same number of items
    demo_groups = session.exec(
        select(Group).where(Group.domain_id == "exter")
    ).all()
    assert len(demo_groups) == 7  # No duplicates
    
    event_assignments = session.exec(
        select(EventTypeGroup)
    ).all()
    assert len(event_assignments) == 13  # No duplicates
    
    session.close()


def test_demo_data_group_hierarchy(setup_test_database):
    """Test that demo data creates proper group hierarchy"""
    session = get_session_sync()
    
    seed_demo_data()
    
    # Get all groups
    demo_groups = session.exec(
        select(Group).where(Group.domain_id == "exter")
    ).all()
    
    # Create lookup by ID
    groups_by_id = {group.id: group for group in demo_groups}
    
    # Check parent-child relationships
    meetings_group = groups_by_id["group_meetings"]
    weekly_meetings = groups_by_id["group_meetings_weekly"]
    quarterly_meetings = groups_by_id["group_meetings_quarterly"]
    
    assert meetings_group.parent_group_id is None  # Top level
    assert weekly_meetings.parent_group_id == "group_meetings"  # Child
    assert quarterly_meetings.parent_group_id == "group_meetings"  # Child
    
    training_group = groups_by_id["group_training"]
    tech_training = groups_by_id["group_training_tech"]
    soft_training = groups_by_id["group_training_soft"]
    
    assert training_group.parent_group_id is None  # Top level
    assert tech_training.parent_group_id == "group_training"  # Child
    assert soft_training.parent_group_id == "group_training"  # Child
    
    session.close()