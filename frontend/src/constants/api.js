// API endpoints and configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const API_ENDPOINTS = {
  // Health (no /api prefix)
  HEALTH: '/health',

  // Regular calendar management (user-added calendars)
  CALENDARS: '/api/calendars',
  CALENDAR_DELETE: (id) => `/api/calendars/${id}`,
  CALENDAR_EVENTS: (id) => `/api/calendars/${id}/events`,
  CALENDAR_SYNC: (id) => `/api/calendars/${id}/sync`,

  // Calendar filters
  CALENDAR_FILTERS: (id) => `/api/calendars/${id}/filters`,
  CALENDAR_FILTER_DELETE: (calId, filterId) => `/api/calendars/${calId}/filters/${filterId}`,

  // User filters across all domains
  USER_FILTERS: '/api/filters',

  // Public calendar view
  PUBLIC_CALENDAR: (token) => `/api/cal/${token}`,

  // Domain-specific endpoints (auto-created from domains.yaml)
  DOMAINS: '/api/domains',
  DOMAIN_EVENTS: (domain) => `/api/domains/${domain}/events`,
  DOMAIN_GROUPS: (domain) => `/api/domains/${domain}/groups`,
  DOMAIN_GROUP: (domain, groupId) => `/api/domains/${domain}/groups/${groupId}`,
  DOMAIN_FILTERS: (domain) => `/api/domains/${domain}/filters`,
  DOMAIN_RECURRING_EVENTS: (domain) => `/api/domains/${domain}/recurring-events`,
  DOMAIN_RECURRING_EVENTS_WITH_ASSIGNMENTS: (domain) => `/api/domains/${domain}/recurring-events-with-assignments`,
  DOMAIN_ASSIGNMENT_RULES: (domain) => `/api/domains/${domain}/assignment-rules`,
  DOMAIN_ASSIGNMENT_RULE: (domain, ruleId) => `/api/domains/${domain}/assignment-rules/${ruleId}`,
  DOMAIN_ASSIGNMENT_RULES_COMPOUND: (domain) => `/api/domains/${domain}/assignment-rules/compound`,
  DOMAIN_ASSIGN_RECURRING_EVENTS: (domain, groupId) => `/api/domains/${domain}/groups/${groupId}/assign-recurring-events`,
  DOMAIN_BULK_ASSIGN_EVENTS: (domain) => `/api/domains/${domain}/bulk-assign-events`,
  DOMAIN_BULK_UNASSIGN_EVENTS: (domain) => `/api/domains/${domain}/bulk-unassign-events`,
  DOMAIN_REMOVE_EVENTS_FROM_GROUP: (domain, groupId) => `/api/domains/${domain}/groups/${groupId}/remove-events`,
  DOMAIN_UNASSIGN_EVENT: (domain) => `/api/domains/${domain}/unassign-event`,

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