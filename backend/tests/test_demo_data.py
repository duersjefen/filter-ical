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
    assert len(demo_groups) == 12  # 5 top-level + 7 nested groups
    
    # Check specific groups exist
    group_names = [group.name for group in demo_groups]
    assert "Music Activities" in group_names
    assert "Sports & Recreation" in group_names
    assert "Youth Activities" in group_names
    assert "Senior Activities" in group_names
    assert "Special Events" in group_names
    assert "Bands" in group_names
    assert "Team Sports" in group_names
    assert "Ice Sports" in group_names
    assert "Tweens" in group_names
    
    # Verify event type assignments exist
    event_assignments = session.exec(
        select(EventTypeGroup)
    ).all()
    assert len(event_assignments) == 14  # Total assignments from demo data
    
    # Check specific event type assignments (real Exter events)
    assignment_types = [assignment.event_type for assignment in event_assignments]
    assert "Musik Band" in assignment_types
    assert "Youngsterband" in assignment_types
    assert "Volleyball" in assignment_types
    assert "Eiszeit (Jugend)" in assignment_types
    assert "Tweens" in assignment_types
    assert "Ü60 Abend" in assignment_types
    
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
    assert len(demo_groups) == 12  # No duplicates
    
    event_assignments = session.exec(
        select(EventTypeGroup)
    ).all()
    assert len(event_assignments) == 14  # No duplicates
    
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
    
    # Check parent-child relationships for new structure
    music_group = groups_by_id["group_music"]
    music_bands = groups_by_id["group_music_bands"]
    music_youth = groups_by_id["group_music_youth"]
    
    assert music_group.parent_group_id is None  # Top level
    assert music_bands.parent_group_id == "group_music"  # Child
    assert music_youth.parent_group_id == "group_music"  # Child
    
    sports_group = groups_by_id["group_sports"]
    sports_team = groups_by_id["group_sports_team"]
    sports_ice = groups_by_id["group_sports_ice"]
    
    assert sports_group.parent_group_id is None  # Top level
    assert sports_team.parent_group_id == "group_sports"  # Child
    assert sports_ice.parent_group_id == "group_sports"  # Child
    
    youth_group = groups_by_id["group_youth"]
    youth_tweens = groups_by_id["group_youth_tweens"]
    youth_teens = groups_by_id["group_youth_teens"]
    
    assert youth_group.parent_group_id is None  # Top level
    assert youth_tweens.parent_group_id == "group_youth"  # Child
    assert youth_teens.parent_group_id == "group_youth"  # Child
    
    session.close()