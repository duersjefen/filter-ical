// UI constants and configuration
export const ROUTES = {
  LOGIN: '/login',
  HOME: '/home', 
  CALENDAR: '/calendar',
  CALENDAR_DETAIL: (id) => `/calendar/${id}`
}

export const FILTER_MODES = {
  INCLUDE: 'include',
  EXCLUDE: 'exclude'
}

export const PREVIEW_GROUPS = {
  NONE: 'none',
  CATEGORY: 'category', 
  MONTH: 'month'
}

export const SORT_ORDERS = {
  ASC: 'asc',
  DESC: 'desc'
}

export const EVENT_LIMITS = {
  PREVIEW_DEFAULT: 10,
  PREVIEW_INCREMENT: 10,
  CATEGORY_EVENTS: 5,
  MAX_CATEGORIES: 50
}

export const VALIDATION_RULES = {
  USERNAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 50,
    PATTERN: /^[a-zA-Z0-9_-]+$/
  },
  CALENDAR_NAME: {
    MIN_LENGTH: 1,
    MAX_LENGTH: 100
  },
  CALENDAR_URL: {
    PATTERN: /^https?:\/\/.+\.(ics|ical)(\?.*)?$/i
  }
}