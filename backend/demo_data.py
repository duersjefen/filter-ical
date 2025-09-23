"""
Demo Data Seeding System
Automatically creates showcase data after clean deployments
"""
from typing import List, Dict, Any
from sqlmodel import Session, select
import uuid

from ..models import Calendar, Group, EventTypeGroup
from ..database import get_session_sync


# Domain calendar creation removed - now handled only by system startup
# via ensure_domain_calendars_exist() using domains.yaml configuration


def create_demo_groups() -> List[Dict[str, Any]]:
    """Create 10 German groups fitting the actual exter events"""
    return [
        # Sports groups based on actual activities
        {
            "id": "group_fussball",
            "name": "⚽ Fußball",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Fußballtraining und -spiele für alle Altersgruppen"
        },
        {
            "id": "group_kampfsport",
            "name": "🥋 Kampfsport",
            "domain_id": "exter", 
            "parent_group_id": None,
            "description": "Karate und andere Kampfsportarten"
        },
        {
            "id": "group_hallensport",
            "name": "🏐 Hallensport",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Volleyball, Eishockey und andere Hallensportarten"
        },
        {
            "id": "group_wassersport",
            "name": "🏊 Wassersport",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Schwimmkurse und Wassersportaktivitäten"
        },
        # Youth and religious activities
        {
            "id": "group_jugend",
            "name": "👦 Jugendarbeit",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Jugendstunden, Jugendabende und Jugendaktivitäten"
        },
        {
            "id": "group_kinder",
            "name": "👶 Kinderaktivitäten",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Jungschar, Kinder-Sport und Kinderfreizeiten"
        },
        {
            "id": "group_senioren",
            "name": "👴 Seniorenarbeit",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Ü60-Abende und Seniorenaktivitäten"
        },
        # Music and culture
        {
            "id": "group_musik",
            "name": "🎵 Musik",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Musik Band, Youngsterband und musikalische Aktivitäten"
        },
        # Education and language
        {
            "id": "group_bildung",
            "name": "📚 Bildung & Kurse",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "Norwegischkurse, Lernwerkstatt und Bildungsangebote"
        },
        # Religious gatherings and events
        {
            "id": "group_gottesdienst",
            "name": "⛪ Gottesdienste & Versammlungen",
            "domain_id": "exter",
            "parent_group_id": None,
            "description": "BUK-Abende, BCC-Events und religiöse Versammlungen"
        }
    ]


def create_demo_event_type_assignments() -> List[Dict[str, Any]]:
    """Create 40+ event type assignments using ACTUAL event types from the exter iCal feed"""
    return [
        # Fußball (Football/Soccer) - Real event types from exter iCal
        {"group_id": "group_fussball", "event_type": "Fußball U16 Jungen", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Mädchen/Jungen U16 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Mädchen U13 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball U13", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Jungen U16 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Jungen U16/U23 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball Mädchen", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball U16/U23 Mädchen", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Jungen U13 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball U16/U23 Mädchen Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Jungen U23 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball U23 Mädchen", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Mädchen U16 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Mädchen U16/U23 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball U16 Mädchen / Jungen", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Jungen U8/U10 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball U8/U10 Jungen", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball U23 Jungen", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball U8/U10 Mädchen", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball Jungen", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Mädchen/Jungen U13 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Fußball U8/U10", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Mädchen U23 Fußball Training", "domain_id": "exter"},
        {"group_id": "group_fussball", "event_type": "Mädchen U8/U10 Fußball Training", "domain_id": "exter"},
        
        # Kampfsport (Martial Arts) - Real event types from exter iCal
        {"group_id": "group_kampfsport", "event_type": "Karate Jungen", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate - Anfänger", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate Kids Jungen", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate Kids Mädchen", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate - Gruppe 1", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate (alle)", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate - Gruppe 2", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate | Weiße Tiger", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate Mädchen", "domain_id": "exter"},
        {"group_id": "group_kampfsport", "event_type": "Karate Anfänger", "domain_id": "exter"},
        
        # Hallensport (Indoor Sports) - Real event types from exter iCal
        {"group_id": "group_hallensport", "event_type": "Volleyball / Jugend open hall", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "Volleyball", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "Eishockey (Jugend)", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "Volleyballtraining", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "Eiszeit (Jugend)", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "Volleyball Training", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "Jugend open hall", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "Eishockey (Kinder)", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "Ü25 bis U70 - open hall", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "Eiszeit (Kinder)", "domain_id": "exter"},
        {"group_id": "group_hallensport", "event_type": "open hall Kinder", "domain_id": "exter"},
        
        # Wassersport (Water Sports) - Real event types from exter iCal
        {"group_id": "group_wassersport", "event_type": "Schwimmkurs", "domain_id": "exter"},
        {"group_id": "group_wassersport", "event_type": "Schimmkurs", "domain_id": "exter"},
        
        # Jugendarbeit (Youth Work) - Real event types from exter iCal
        {"group_id": "group_jugend", "event_type": "Jugendgottesdienst", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Tweens Jungs", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "BUK Abend", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Mentorenabend", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendstunde mit Br. K. J. Smith", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugend-Wochenende Nord", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendstunde / Musikfest", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendstunde (mit Hamburg)", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendabend (mit Einar Å.)", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugend Herbststart (mit DFL U23 Dürrmenz)", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendabend", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendstunde Kick-Off 2025", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendweihnachtsfeier", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Tweens", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendausflug", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendwochenende Nord und Süd", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendtour", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "A-Team Jugendstunde", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugend WE Hessenhöfe", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendstunde", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendkonferenz mit Sportturnieren", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Tweens Jungs + Mädchen", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendwochenende", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Ateam Jugendstunde", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Weihnachtliche Jugendstunde", "domain_id": "exter"},
        
        # Kinderaktivitäten (Children's Activities) - Real event types from exter iCal
        {"group_id": "group_kinder", "event_type": "Kinder Sport Aktivitäten", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Jungschar", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Jungschar-Tour/Abschluss", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Kinderfreizeit", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Kinder-Sport Aktivitäten", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Jungscharweihnachtsfeier", "domain_id": "exter"},
        
        # Seniorenarbeit (Senior Activities) - Real event types from exter iCal
        {"group_id": "group_senioren", "event_type": "Ü60 Abend", "domain_id": "exter"},
        {"group_id": "group_senioren", "event_type": "60+ WE HH", "domain_id": "exter"},
        {"group_id": "group_senioren", "event_type": "60+ Wochennede", "domain_id": "exter"},
        {"group_id": "group_senioren", "event_type": "60+ Wochenende", "domain_id": "exter"},
        {"group_id": "group_senioren", "event_type": "Ü60-Abend", "domain_id": "exter"},
        {"group_id": "group_senioren", "event_type": "Ü60", "domain_id": "exter"},
        
        # Musik - Real event types from exter iCal
        {"group_id": "group_musik", "event_type": "Musik Band", "domain_id": "exter"},
        {"group_id": "group_musik", "event_type": "Youngsterband", "domain_id": "exter"},
        {"group_id": "group_musik", "event_type": "Jugendband", "domain_id": "exter"},
        {"group_id": "group_musik", "event_type": "Musik - Kiddyband", "domain_id": "exter"},
        {"group_id": "group_musik", "event_type": "Musik - Jugendband", "domain_id": "exter"},
        {"group_id": "group_musik", "event_type": "Kiddyband", "domain_id": "exter"},
        
        # Bildung & Kurse (Education & Courses) - Real event types from exter iCal
        {"group_id": "group_bildung", "event_type": " Norwegisch Kurs A-Team 27/28", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegisch U16", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegisch Kurs U16", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegisch Kurs A-Team 26/27", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegisch Kurs U18", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegischkurs Ateam 25/26", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegischkurs U16", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegisch 12-13 Jährige", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegisch Kurs A-Team 27/28", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegischkurs Ateam 26/27", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Norwegischkurs Ateam 27/28", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Lernwerkstatt", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Lernwerkstatt Kick-off 2025", "domain_id": "exter"},
        
        # Gottesdienste & Versammlungen (Services & Assemblies) - Real event types from exter iCal
        {"group_id": "group_gottesdienst", "event_type": "BUK-Abend", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Versammlung mit Abendmahl", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Versammlung", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Gemeinschaftstag Exter mit B. Hustad und T. Gangso", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Gemeinschaftstag Exter", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Gemeinschaftstag Exter mit Taufe", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Gemeinschaftstag Exter mit Sommerfest", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Gemeinschaftstag Exter mit Kindersegnung", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Gemeinschaftstag Exter mit Br. K. J. Smith", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Gemeinde Kick-off 2. HJ 2025", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Gemeinde Sommerabschluss", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Gemeindeweihnachtsfeier", "domain_id": "exter"},
        
        # CROSS-GROUP ASSIGNMENTS - Event types that belong to multiple groups
        # These are crucial for testing complex selection logic and production realism
        
        # Tweens belongs to both Youth and Children groups
        {"group_id": "group_kinder", "event_type": "Tweens", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Tweens Jungs", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Tweens Jungs + Mädchen", "domain_id": "exter"},
        
        # BUK events belong to both Youth and Religious groups
        {"group_id": "group_gottesdienst", "event_type": "BUK Abend", "domain_id": "exter"},
        
        # Music events that also involve youth
        {"group_id": "group_jugend", "event_type": "Musik - Jugendband", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugendband", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Musik - Kiddyband", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Kiddyband", "domain_id": "exter"},
        
        # Sports events that involve children
        {"group_id": "group_kinder", "event_type": "Eishockey (Kinder)", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Eiszeit (Kinder)", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "open hall Kinder", "domain_id": "exter"},
        
        # Football training events that could be considered educational/structured learning
        {"group_id": "group_bildung", "event_type": "Fußball Mentoren", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Eltern- und Mentorenabend", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Verpflichtender Mentoren- und Elternabend", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Mentorenfrühstück", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Nachschulung Eltern- und Mentorenabend", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Ersthelfer Schulung für Trainer (MySports)", "domain_id": "exter"},
        
        # Indoor sports that also involve youth activities
        {"group_id": "group_jugend", "event_type": "Volleyball / Jugend open hall", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Jugend open hall", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Eiszeit (Jugend)", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Eishockey (Jugend)", "domain_id": "exter"},
        
        # Swimming courses that are also educational
        {"group_id": "group_bildung", "event_type": "Schwimmkurs", "domain_id": "exter"},
        
        # Senior activities that are also religious/community
        {"group_id": "group_gottesdienst", "event_type": "Ü60 Abend", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Ü60-Abend", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Ü60", "domain_id": "exter"},
        
        # Karate classes that are also youth-oriented or educational
        {"group_id": "group_jugend", "event_type": "Karate Jungen", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Karate Kids Jungen", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Karate Kids Mädchen", "domain_id": "exter"},
        {"group_id": "group_kinder", "event_type": "Karate | Weiße Tiger", "domain_id": "exter"},
        {"group_id": "group_jugend", "event_type": "Karate Mädchen", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Karate - Anfänger", "domain_id": "exter"},
        {"group_id": "group_bildung", "event_type": "Karate Anfänger", "domain_id": "exter"},
        
        # Community events that are also religious
        {"group_id": "group_gottesdienst", "event_type": "Schulstartfrühstück", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Einweihung Rehwinkel mit Br. K. J. Smith", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Kick-Off Exter 2025", "domain_id": "exter"},
        
        # Sports events organized as community activities
        {"group_id": "group_gottesdienst", "event_type": "Sport-Wochenende", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Sport Aktivitäten NDJ", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Ateam Sport", "domain_id": "exter"},
        
        # Educational events with religious component
        {"group_id": "group_gottesdienst", "event_type": "KickOff Bibelprojekt \"Paulus | Wer bist du, Herr?\"", "domain_id": "exter"},
        {"group_id": "group_gottesdienst", "event_type": "Elternabend zur Medienkompetenz", "domain_id": "exter"},
        
        # Note: This creates 134 total event type assignments across 10 German groups
        # Including 36 cross-group assignments for comprehensive testing
        # Many event types will remain ungrouped, perfect for testing the enhanced
        # selection system's individual vs group selection logic
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
            print("❌ ERROR: Domain calendar cal_domain_exter not found!")
            print("💡 Domain calendars must be created by system startup (ensure_domain_calendars_exist)")
            print("📋 Check domains.yaml configuration and restart the application")
            session.close()
            return False
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