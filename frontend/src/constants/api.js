// API endpoints and configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'

export const API_ENDPOINTS = {
  // Health (no /api prefix)
  HEALTH: '/health',
  
  // Regular calendar management (user-added calendars)
  CALENDARS: '/calendars',
  CALENDAR_DELETE: (id) => `/calendars/${id}`,
  CALENDAR_EVENTS: (id) => `/calendars/${id}/events`,
  
  // Calendar filters  
  CALENDAR_FILTERS: (id) => `/calendars/${id}/filters`,
  CALENDAR_FILTER_DELETE: (calId, filterId) => `/calendars/${calId}/filters/${filterId}`,
  
  // Domain-specific endpoints (auto-created from domains.yaml)
  DOMAINS: '/domains',
  DOMAIN_EVENTS: (domain) => `/domains/${domain}/events`,
  DOMAIN_GROUPS: (domain) => `/domains/${domain}/groups`,
  DOMAIN_FILTERS: (domain) => `/domains/${domain}/filters`,
  DOMAIN_ASSIGNMENT_RULES: (domain) => `/domains/${domain}/assignment-rules`,
  DOMAIN_ASSIGN_RECURRING_EVENTS: (domain, groupId) => `/domains/${domain}/groups/${groupId}/assign-recurring-events`,
  
  // Dynamic iCal Export
  ICAL_EXPORT: (uuid) => `/ical/${uuid}.ics`,
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