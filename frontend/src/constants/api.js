// API endpoints and configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const API_ENDPOINTS = {
  // Health (no /api prefix)
  HEALTH: '/health',

  // Regular calendar management (user-added calendars)
  CALENDARS: '/api/calendars',
  CALENDAR_DELETE: (id) => `/api/calendars/${id}`,
  CALENDAR_EVENTS: (id) => `/api/calendars/${id}/events`,

  // Calendar filters
  CALENDAR_FILTERS: (id) => `/api/calendars/${id}/filters`,
  CALENDAR_FILTER_DELETE: (calId, filterId) => `/api/calendars/${calId}/filters/${filterId}`,

  // Domain-specific endpoints (auto-created from domains.yaml)
  DOMAINS: '/api/domains',
  DOMAIN_EVENTS: (domain) => `/api/domains/${domain}/events`,
  DOMAIN_GROUPS: (domain) => `/api/domains/${domain}/groups`,
  DOMAIN_FILTERS: (domain) => `/api/domains/${domain}/filters`,
  DOMAIN_ASSIGNMENT_RULES: (domain) => `/api/domains/${domain}/assignment-rules`,
  DOMAIN_ASSIGN_RECURRING_EVENTS: (domain, groupId) => `/api/domains/${domain}/groups/${groupId}/assign-recurring-events`,

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