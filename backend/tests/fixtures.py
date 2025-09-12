"""
Test fixtures for the iCal viewer application
"""
from app.main import CalendarEntry

def get_test_calendars():
    """Get test calendar fixtures for testing"""
    return [
        CalendarEntry("1", "BCC Portal Calendar", "https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics", "default"),
        CalendarEntry("2", "Google US Holidays", "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics", "default")
    ]