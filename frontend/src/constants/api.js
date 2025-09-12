// API endpoints and configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'

export const API_ENDPOINTS = {
  // Authentication
  LOGIN: '/login',
  LOGOUT: '/logout',
  
  // Calendars
  CALENDARS: '/calendars',
  CALENDAR_EVENTS: (id) => `/calendars/${id}/events`,
  CALENDAR_DELETE: (id) => `/calendars/${id}`,
  
  // Filters
  FILTERS: '/filters',
  FILTER_DELETE: (id) => `/filters/${id}`,
  
  // Export
  EXPORT_ICAL: '/export/ical',
  
  // Health
  HEALTH: '/health'
}

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503
}