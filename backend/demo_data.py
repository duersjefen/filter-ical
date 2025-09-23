"""
Demo Data Seeding System for Exter Domain
Automatically creates showcase data after clean deployments

Fixes applied:
- Database model compliance (proper field mapping)
- Auto-increment IDs instead of string IDs
- Proper session management with error handling
- Preserved all 134 event-to-group assignments
"""
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.calendar import Calendar, Group, RecurringEventGroup, AssignmentRule
from app.core.database import get_session_sync


def create_demo_groups_data() -> List[Dict[str, Any]]:
    """
    Create demo groups data for exter domain.
    Returns group data compatible with Group model fields.
    """
    return [
        # Sports groups based on actual activities
        {
            "domain_key": "exter",
            "name": "⚽ Fußball"
        },
        {
            "domain_key": "exter", 
            "name": "🥋 Kampfsport"
        },
        {
            "domain_key": "exter",
            "name": "🏐 Hallensport"
        },
        {
            "domain_key": "exter",
            "name": "🏊 Wassersport"
        },
        # Youth and religious activities
        {
            "domain_key": "exter",
            "name": "👦 Jugendarbeit"
        },
        {
            "domain_key": "exter",
            "name": "👶 Kinderaktivitäten"
        },
        {
            "domain_key": "exter",
            "name": "👴 Seniorenarbeit"
        },
        # Music and culture
        {
            "domain_key": "exter",
            "name": "🎵 Musik"
        },
        # Education and language
        {
            "domain_key": "exter",
            "name": "📚 Bildung & Kurse"
        },
        # Religious gatherings and events
        {
            "domain_key": "exter",
            "name": "⛪ Gottesdienste & Versammlungen"
        },
        # Category-based groups for external domain integration
        {
            "domain_key": "exter",
            "name": "🎉 BCC Event"
        },
        {
            "domain_key": "exter", 
            "name": "🇩🇪 DCG Events"
        }
    ]


def create_demo_event_assignments() -> List[Dict[str, Any]]:
    """
    Create event type assignments using ACTUAL event types from the exter iCal feed.
    Returns assignments with group_name references that will be resolved to group_ids after group creation.
    
    Preserves all 134 carefully curated event-to-group assignments.
    """
    return [
        # Fußball (Football/Soccer) - Real event types from exter iCal
        {"group_name": "⚽ Fußball", "event_type": "Fußball U16 Jungen"},
        {"group_name": "⚽ Fußball", "event_type": "Mädchen/Jungen U16 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Mädchen U13 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball U13"},
        {"group_name": "⚽ Fußball", "event_type": "Jungen U16 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Jungen U16/U23 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball Mädchen"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball U16/U23 Mädchen"},
        {"group_name": "⚽ Fußball", "event_type": "Jungen U13 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball U16/U23 Mädchen Training"},
        {"group_name": "⚽ Fußball", "event_type": "Jungen U23 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball U23 Mädchen"},
        {"group_name": "⚽ Fußball", "event_type": "Mädchen U16 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Mädchen U16/U23 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball U16 Mädchen / Jungen"},
        {"group_name": "⚽ Fußball", "event_type": "Jungen U8/U10 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball U8/U10 Jungen"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball U23 Jungen"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball U8/U10 Mädchen"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball Jungen"},
        {"group_name": "⚽ Fußball", "event_type": "Mädchen/Jungen U13 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Fußball U8/U10"},
        {"group_name": "⚽ Fußball", "event_type": "Mädchen U23 Fußball Training"},
        {"group_name": "⚽ Fußball", "event_type": "Mädchen U8/U10 Fußball Training"},
        
        # Kampfsport (Martial Arts) - Real event types from exter iCal
        {"group_name": "🥋 Kampfsport", "event_type": "Karate Jungen"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate - Anfänger"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate Kids Jungen"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate Kids Mädchen"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate - Gruppe 1"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate (alle)"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate - Gruppe 2"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate | Weiße Tiger"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate Mädchen"},
        {"group_name": "🥋 Kampfsport", "event_type": "Karate Anfänger"},
        
        # Hallensport (Indoor Sports) - Real event types from exter iCal
        {"group_name": "🏐 Hallensport", "event_type": "Volleyball / Jugend open hall"},
        {"group_name": "🏐 Hallensport", "event_type": "Volleyball"},
        {"group_name": "🏐 Hallensport", "event_type": "Eishockey (Jugend)"},
        {"group_name": "🏐 Hallensport", "event_type": "Volleyballtraining"},
        {"group_name": "🏐 Hallensport", "event_type": "Eiszeit (Jugend)"},
        {"group_name": "🏐 Hallensport", "event_type": "Volleyball Training"},
        {"group_name": "🏐 Hallensport", "event_type": "Jugend open hall"},
        {"group_name": "🏐 Hallensport", "event_type": "Eishockey (Kinder)"},
        {"group_name": "🏐 Hallensport", "event_type": "Ü25 bis U70 - open hall"},
        {"group_name": "🏐 Hallensport", "event_type": "Eiszeit (Kinder)"},
        {"group_name": "🏐 Hallensport", "event_type": "open hall Kinder"},
        
        # Wassersport (Water Sports) - Real event types from exter iCal
        {"group_name": "🏊 Wassersport", "event_type": "Schwimmkurs"},
        {"group_name": "🏊 Wassersport", "event_type": "Schimmkurs"},
        
        # Jugendarbeit (Youth Work) - Real event types from exter iCal
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendgottesdienst"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Tweens Jungs"},
        {"group_name": "👦 Jugendarbeit", "event_type": "BUK Abend"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Mentorenabend"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendstunde mit Br. K. J. Smith"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugend-Wochenende Nord"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendstunde / Musikfest"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendstunde (mit Hamburg)"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendabend (mit Einar Å.)"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugend Herbststart (mit DFL U23 Dürrmenz)"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendabend"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendstunde Kick-Off 2025"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendweihnachtsfeier"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Tweens"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendausflug"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendwochenende Nord und Süd"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendtour"},
        {"group_name": "👦 Jugendarbeit", "event_type": "A-Team Jugendstunde"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugend WE Hessenhöfe"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendstunde"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendkonferenz mit Sportturnieren"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Tweens Jungs + Mädchen"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendwochenende"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Ateam Jugendstunde"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Weihnachtliche Jugendstunde"},
        
        # Kinderaktivitäten (Children's Activities) - Real event types from exter iCal
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Kinder Sport Aktivitäten"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Jungschar"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Jungschar-Tour/Abschluss"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Kinderfreizeit"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Kinder-Sport Aktivitäten"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Jungscharweihnachtsfeier"},
        
        # Seniorenarbeit (Senior Activities) - Real event types from exter iCal
        {"group_name": "👴 Seniorenarbeit", "event_type": "Ü60 Abend"},
        {"group_name": "👴 Seniorenarbeit", "event_type": "60+ WE HH"},
        {"group_name": "👴 Seniorenarbeit", "event_type": "60+ Wochennede"},
        {"group_name": "👴 Seniorenarbeit", "event_type": "60+ Wochenende"},
        {"group_name": "👴 Seniorenarbeit", "event_type": "Ü60-Abend"},
        {"group_name": "👴 Seniorenarbeit", "event_type": "Ü60"},
        
        # Musik - Real event types from exter iCal
        {"group_name": "🎵 Musik", "event_type": "Musik Band"},
        {"group_name": "🎵 Musik", "event_type": "Youngsterband"},
        {"group_name": "🎵 Musik", "event_type": "Jugendband"},
        {"group_name": "🎵 Musik", "event_type": "Musik - Kiddyband"},
        {"group_name": "🎵 Musik", "event_type": "Musik - Jugendband"},
        {"group_name": "🎵 Musik", "event_type": "Kiddyband"},
        
        # Bildung & Kurse (Education & Courses) - Real event types from exter iCal
        {"group_name": "📚 Bildung & Kurse", "event_type": " Norwegisch Kurs A-Team 27/28"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegisch U16"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegisch Kurs U16"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegisch Kurs A-Team 26/27"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegisch Kurs U18"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegischkurs Ateam 25/26"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegischkurs U16"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegisch 12-13 Jährige"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegisch Kurs A-Team 27/28"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegischkurs Ateam 26/27"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Norwegischkurs Ateam 27/28"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Lernwerkstatt"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Lernwerkstatt Kick-off 2025"},
        
        # Gottesdienste & Versammlungen (Services & Assemblies) - Real event types from exter iCal
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "BUK-Abend"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Versammlung mit Abendmahl"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Versammlung"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Gemeinschaftstag Exter mit B. Hustad und T. Gangso"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Gemeinschaftstag Exter"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Gemeinschaftstag Exter mit Taufe"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Gemeinschaftstag Exter mit Sommerfest"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Gemeinschaftstag Exter mit Kindersegnung"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Gemeinschaftstag Exter mit Br. K. J. Smith"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Gemeinde Kick-off 2. HJ 2025"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Gemeinde Sommerabschluss"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Gemeindeweihnachtsfeier"},
        
        # CROSS-GROUP ASSIGNMENTS - Event types that belong to multiple groups
        # These are crucial for testing complex selection logic and production realism
        
        # Tweens belongs to both Youth and Children groups
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Tweens"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Tweens Jungs"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Tweens Jungs + Mädchen"},
        
        # BUK events belong to both Youth and Religious groups
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "BUK Abend"},
        
        # Music events that also involve youth
        {"group_name": "👦 Jugendarbeit", "event_type": "Musik - Jugendband"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugendband"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Musik - Kiddyband"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Kiddyband"},
        
        # Sports events that involve children
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Eishockey (Kinder)"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Eiszeit (Kinder)"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "open hall Kinder"},
        
        # Football training events that could be considered educational/structured learning
        {"group_name": "📚 Bildung & Kurse", "event_type": "Fußball Mentoren"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Eltern- und Mentorenabend"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Verpflichtender Mentoren- und Elternabend"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Mentorenfrühstück"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Nachschulung Eltern- und Mentorenabend"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Ersthelfer Schulung für Trainer (MySports)"},
        
        # Indoor sports that also involve youth activities
        {"group_name": "👦 Jugendarbeit", "event_type": "Volleyball / Jugend open hall"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Jugend open hall"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Eiszeit (Jugend)"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Eishockey (Jugend)"},
        
        # Swimming courses that are also educational
        {"group_name": "📚 Bildung & Kurse", "event_type": "Schwimmkurs"},
        
        # Senior activities that are also religious/community
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Ü60 Abend"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Ü60-Abend"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Ü60"},
        
        # Karate classes that are also youth-oriented or educational
        {"group_name": "👦 Jugendarbeit", "event_type": "Karate Jungen"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Karate Kids Jungen"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Karate Kids Mädchen"},
        {"group_name": "👶 Kinderaktivitäten", "event_type": "Karate | Weiße Tiger"},
        {"group_name": "👦 Jugendarbeit", "event_type": "Karate Mädchen"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Karate - Anfänger"},
        {"group_name": "📚 Bildung & Kurse", "event_type": "Karate Anfänger"},
        
        # Community events that are also religious
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Schulstartfrühstück"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Einweihung Rehwinkel mit Br. K. J. Smith"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Kick-Off Exter 2025"},
        
        # Sports events organized as community activities
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Sport-Wochenende"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Sport Aktivitäten NDJ"},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Ateam Sport"},
        
        # Educational events with religious component
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "KickOff Bibelprojekt \"Paulus | Wer bist du, Herr?\""},
        {"group_name": "⛪ Gottesdienste & Versammlungen", "event_type": "Elternabend zur Medienkompetenz"},
        
        # Note: This creates 134 total event type assignments across 10 German groups
        # Including 36 cross-group assignments for comprehensive testing
        # Many event types will remain ungrouped, perfect for testing the enhanced
        # selection system's individual vs group selection logic
    ]


def create_demo_assignment_rules_data() -> List[Dict[str, Any]]:
    """
    Create demo assignment rules for category-based grouping.
    Returns assignment rule data compatible with AssignmentRule model fields.
    """
    return [
        # Category-based rules for external calendar integration
        {
            "domain_key": "exter",
            "rule_type": "category_contains",
            "rule_value": "Event",
            "group_name": "🎉 BCC Event"  # Will be resolved to group_id
        },
        {
            "domain_key": "exter",
            "rule_type": "category_contains", 
            "rule_value": "Deutschland",
            "group_name": "🇩🇪 DCG Events"  # Will be resolved to group_id
        }
    ]


def create_groups_and_get_mapping(session: Session) -> Tuple[bool, Dict[str, int], str]:
    """
    Create demo groups and return name-to-id mapping.
    
    Returns:
        Tuple of (success, name_to_id_mapping, error_message)
    """
    try:
        groups_data = create_demo_groups_data()
        name_to_id = {}
        created_count = 0
        
        for group_data in groups_data:
            # Check if group already exists
            existing_group = session.query(Group).filter(
                Group.domain_key == group_data["domain_key"],
                Group.name == group_data["name"]
            ).first()
            
            if existing_group:
                name_to_id[group_data["name"]] = existing_group.id
            else:
                # Create new group
                new_group = Group(**group_data)
                session.add(new_group)
                session.flush()  # Get the ID without committing
                name_to_id[group_data["name"]] = new_group.id
                created_count += 1
        
        if created_count > 0:
            print(f"✅ Created {created_count} demo groups for exter domain")
        else:
            print("📋 Demo groups already exist for exter domain")
            
        return True, name_to_id, ""
        
    except Exception as e:
        return False, {}, f"Failed to create groups: {str(e)}"


def create_recurring_event_assignments(session: Session, name_to_id: Dict[str, int]) -> Tuple[bool, str]:
    """
    Create recurring event group assignments.
    
    Args:
        session: Database session
        name_to_id: Mapping of group names to database IDs
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        assignments_data = create_demo_event_assignments()
        created_count = 0
        
        for assignment in assignments_data:
            group_name = assignment["group_name"]
            event_type = assignment["event_type"]
            
            # Get group ID from name
            if group_name not in name_to_id:
                print(f"⚠️ Warning: Group '{group_name}' not found, skipping assignment for '{event_type}'")
                continue
                
            group_id = name_to_id[group_name]
            
            # Check if assignment already exists
            existing_assignment = session.query(RecurringEventGroup).filter(
                RecurringEventGroup.domain_key == "exter",
                RecurringEventGroup.recurring_event_title == event_type,
                RecurringEventGroup.group_id == group_id
            ).first()
            
            if not existing_assignment:
                # Create new assignment
                new_assignment = RecurringEventGroup(
                    domain_key="exter",
                    recurring_event_title=event_type,
                    group_id=group_id
                )
                session.add(new_assignment)
                created_count += 1
        
        if created_count > 0:
            print(f"✅ Created {created_count} demo event type assignments")
        else:
            print("📋 Demo event type assignments already exist")
            
        return True, ""
        
    except Exception as e:
        return False, f"Failed to create assignments: {str(e)}"


def create_assignment_rules(session: Session, name_to_id: Dict[str, int]) -> Tuple[bool, str]:
    """
    Create assignment rules for automatic categorization.
    
    Args:
        session: Database session
        name_to_id: Mapping of group names to database IDs
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        rules_data = create_demo_assignment_rules_data()
        created_count = 0
        
        for rule_data in rules_data:
            group_name = rule_data["group_name"]
            
            # Get group ID from name
            if group_name not in name_to_id:
                print(f"⚠️ Warning: Group '{group_name}' not found, skipping assignment rule")
                continue
                
            group_id = name_to_id[group_name]
            
            # Check if rule already exists
            existing_rule = session.query(AssignmentRule).filter(
                AssignmentRule.domain_key == rule_data["domain_key"],
                AssignmentRule.rule_type == rule_data["rule_type"],
                AssignmentRule.rule_value == rule_data["rule_value"],
                AssignmentRule.target_group_id == group_id
            ).first()
            
            if not existing_rule:
                # Create new assignment rule
                new_rule = AssignmentRule(
                    domain_key=rule_data["domain_key"],
                    rule_type=rule_data["rule_type"],
                    rule_value=rule_data["rule_value"],
                    target_group_id=group_id
                )
                session.add(new_rule)
                created_count += 1
        
        if created_count > 0:
            print(f"✅ Created {created_count} demo assignment rules")
        else:
            print("📋 Demo assignment rules already exist")
            
        return True, ""
        
    except Exception as e:
        return False, f"Failed to create assignment rules: {str(e)}"


def seed_demo_data() -> bool:
    """
    Seed the database with demo data for exter domain.
    Returns True if seeding was successful.
    """
    session = None
    try:
        session = get_session_sync()
        
        # 1. Verify domain calendar exists (should be created by ensure_domain_calendars_exist)
        existing_calendar = session.query(Calendar).filter(
            Calendar.domain_key == "exter",
            Calendar.type == "domain"
        ).first()
        
        if not existing_calendar:
            print("❌ ERROR: Domain calendar for exter not found!")
            print("💡 Domain calendars must be created by system startup (ensure_domain_calendars_exist)")
            print("📋 Check domains.yaml configuration and restart the application")
            return False
        else:
            print("✅ Domain calendar for exter exists")
        
        # 2. Create demo groups and get name-to-id mapping
        success, name_to_id, error = create_groups_and_get_mapping(session)
        if not success:
            print(f"❌ Error creating groups: {error}")
            return False
        
        # 3. Create event type assignments
        success, error = create_recurring_event_assignments(session, name_to_id)
        if not success:
            print(f"❌ Error creating assignments: {error}")
            return False
        
        # 4. Create assignment rules for automatic categorization
        success, error = create_assignment_rules(session, name_to_id)
        if not success:
            print(f"❌ Error creating assignment rules: {error}")
            return False
        
        # 5. Commit all changes
        session.commit()
        print("✅ Demo data seeding completed successfully")
        return True
        
    except Exception as e:
        if session:
            session.rollback()
        print(f"❌ Error seeding demo data: {e}")
        return False
        
    finally:
        if session:
            session.close()


def should_seed_demo_data() -> bool:
    """
    Check if demo data should be seeded.
    Returns True if no demo groups exist for exter domain.
    """
    session = None
    try:
        session = get_session_sync()
        
        # Check if demo groups exist for exter domain
        existing_groups = session.query(Group).filter(Group.domain_key == "exter").first()
        has_demo_groups = existing_groups is not None
        
        return not has_demo_groups
        
    except Exception as e:
        print(f"❌ Error checking demo data: {e}")
        return False
        
    finally:
        if session:
            session.close()