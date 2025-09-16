/**
 * MSW API handlers generated from OpenAPI specification
 * Provides realistic mock responses for frontend development
 */

import { http, HttpResponse } from 'msw'

// Mock data that matches OpenAPI schemas
const mockCalendars = [
  {
    id: 'cal_001',
    name: 'Work Calendar',
    url: 'https://example.com/work.ics',
    user_id: 'user123',
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 'cal_002', 
    name: 'Personal Events',
    url: 'https://example.com/personal.ics',
    user_id: 'user123',
    created_at: '2024-01-10T14:20:00Z'
  }
]

const mockEvents = {
  "work_meetings": {
    count: 3,
    events: [
      {
        id: 'evt_001',
        title: 'Team Standup',
        start: '2024-01-20T09:00:00Z',
        end: '2024-01-20T09:30:00Z',
        category: 'work_meetings',
        description: 'Daily team sync',
        location: 'Conference Room A'
      },
      {
        id: 'evt_002',
        title: 'Project Review',
        start: '2024-01-22T14:00:00Z', 
        end: '2024-01-22T15:00:00Z',
        category: 'work_meetings',
        description: 'Quarterly project review',
        location: 'Virtual'
      }
    ]
  },
  "personal": {
    count: 1,
    events: [
      {
        id: 'evt_003',
        title: 'Dentist Appointment',
        start: '2024-01-25T16:00:00Z',
        end: '2024-01-25T17:00:00Z',
        category: 'personal',
        description: 'Regular checkup'
      }
    ]
  }
}

const mockFilteredCalendars = [
  {
    id: 'filtered_001',
    name: 'Work Only',
    source_calendar_id: 'cal_001',
    filter_config: {
      categories: ['work_meetings'],
      exclude_keywords: ['personal']
    },
    user_id: 'user123',
    created_at: '2024-01-16T08:00:00Z'
  }
]

export const handlers = [
  // Calendar Management
  http.get('/api/calendars', ({ request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }
    
    return HttpResponse.json({
      calendars: mockCalendars
    })
  }),

  http.post('/api/calendars', async ({ request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    const body = await request.json()
    
    // Validate required fields per OpenAPI spec
    if (!body.name || body.name.length < 3) {
      return HttpResponse.json(
        { detail: 'Name is required and must be at least 3 characters' },
        { status: 400 }
      )
    }
    
    if (!body.url) {
      return HttpResponse.json(
        { detail: 'Calendar URL is required' },
        { status: 400 }
      )
    }

    // Return new calendar with generated ID (status 201 per OpenAPI spec)
    const newCalendar = {
      id: `cal_${Date.now()}`,
      name: body.name,
      url: body.url,
      user_id: headers['x-user-id'],
      created_at: new Date().toISOString()
    }

    // Add to mock data for subsequent requests
    mockCalendars.push(newCalendar)

    return HttpResponse.json(newCalendar, { status: 201 })
  }),

  http.delete('/api/calendars/:calendarId', ({ params, request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    const calendarIndex = mockCalendars.findIndex(cal => cal.id === params.calendarId)
    if (calendarIndex === -1) {
      return HttpResponse.json(
        { detail: 'Calendar not found' },
        { status: 404 }
      )
    }

    // Remove from mock data
    mockCalendars.splice(calendarIndex, 1)
    
    // Return 204 No Content per OpenAPI spec
    return new HttpResponse(null, { status: 204 })
  }),

  // Calendar Events
  http.get('/api/calendar/:calendarId/events', ({ params, request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    const calendar = mockCalendars.find(cal => cal.id === params.calendarId)
    if (!calendar) {
      return HttpResponse.json(
        { detail: 'Calendar not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      events: mockEvents
    })
  }),

  http.get('/api/calendar/:calendarId/raw-events', ({ params, request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    // Flatten events from all categories for raw endpoint
    const allEvents = Object.values(mockEvents).flatMap(category => category.events)
    
    return HttpResponse.json({
      events: allEvents
    })
  }),

  // Filtered Calendars
  http.get('/api/filtered-calendars', ({ request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    return HttpResponse.json({
      filtered_calendars: mockFilteredCalendars
    })
  }),

  http.post('/api/filtered-calendars', async ({ request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    const body = await request.json()
    
    const newFilteredCalendar = {
      id: `filtered_${Date.now()}`,
      name: body.name,
      source_calendar_id: body.source_calendar_id,
      filter_config: body.filter_config,
      user_id: headers['x-user-id'],
      created_at: new Date().toISOString()
    }

    mockFilteredCalendars.push(newFilteredCalendar)
    
    return HttpResponse.json(newFilteredCalendar, { status: 201 })
  }),

  http.delete('/api/filtered-calendars/:filteredCalendarId', ({ params, request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    const index = mockFilteredCalendars.findIndex(fc => fc.id === params.filteredCalendarId)
    if (index === -1) {
      return HttpResponse.json(
        { detail: 'Filtered calendar not found' },
        { status: 404 }
      )
    }

    mockFilteredCalendars.splice(index, 1)
    return new HttpResponse(null, { status: 204 })
  }),

  // User Preferences
  http.get('/api/user/preferences', ({ request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    return HttpResponse.json({
      success: true,
      preferences: {
        theme: 'light',
        language: 'en',
        timezone: 'UTC'
      }
    })
  }),

  http.put('/api/user/preferences', async ({ request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    await request.json() // Consume body
    
    return HttpResponse.json({
      success: true
    })
  }),

  // Health endpoint
  http.get('/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString()
    })
  }),

  // iCal Generation
  http.post('/api/calendar/:calendarId/generate', async ({ params, request }) => {
    const headers = Object.fromEntries(request.headers.entries())
    if (!headers['x-user-id']) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      )
    }

    const body = await request.json()
    
    // Generate mock iCal content
    const icalContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Mock Calendar//Mock Event//EN
BEGIN:VEVENT
UID:mock-event-1
DTSTART:20240120T090000Z
DTEND:20240120T093000Z
SUMMARY:Team Standup
DESCRIPTION:Daily team sync
LOCATION:Conference Room A
END:VEVENT
END:VCALENDAR`

    return new HttpResponse(icalContent, {
      headers: {
        'Content-Type': 'text/calendar; charset=utf-8',
        'Content-Disposition': 'attachment; filename="filtered-calendar.ics"'
      }
    })
  })
]