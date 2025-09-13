/**
 * Pure Calendar Data Functions - Rich Hickey Style for Frontend
 * Pure functions for calendar data validation and transformation
 * No side effects, explicit data flow, composable functions
 */

// === CALENDAR VALIDATION (Pure Functions) ===

/**
 * Pure function: Validate calendar form data
 * @param {Object} calendar - Calendar data {name, url}
 * @returns {Object} {isValid: boolean, errors: string[]}
 */
export function validateCalendarData(calendar) {
  const errors = []
  
  if (!calendar.name || !calendar.name.trim()) {
    errors.push('Calendar name is required')
  }
  
  if (calendar.name && calendar.name.trim().length > 100) {
    errors.push('Calendar name must be less than 100 characters')
  }
  
  if (!calendar.url || !calendar.url.trim()) {
    errors.push('Calendar URL is required')
  }
  
  if (calendar.url && !isValidUrlFormat(calendar.url)) {
    errors.push('Please enter a valid URL starting with http:// or https://')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Pure function: Check if URL format is valid
 * @param {string} url - URL to validate
 * @returns {boolean} - True if valid URL format
 */
export function isValidUrlFormat(url) {
  try {
    const urlObj = new URL(url)
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
  } catch {
    return false
  }
}

/**
 * Pure function: Normalize calendar data for API
 * @param {Object} calendar - Raw calendar data
 * @returns {Object} - Normalized calendar data
 */
export function normalizeCalendarData(calendar) {
  return {
    name: calendar.name?.trim() || '',
    url: calendar.url?.trim() || ''
  }
}

// === CALENDAR TRANSFORMATIONS (Pure Functions) ===

/**
 * Pure function: Transform API calendar response to display format
 * @param {Object} apiCalendar - Calendar from API
 * @returns {Object} - Display-ready calendar
 */
export function calendarToDisplayFormat(apiCalendar) {
  return {
    id: apiCalendar.id,
    name: apiCalendar.name,
    url: apiCalendar.url,
    displayName: apiCalendar.name,
    shortUrl: truncateUrl(apiCalendar.url, 50),
    domain: extractDomain(apiCalendar.url)
  }
}

/**
 * Pure function: Extract domain from URL
 * @param {string} url - Full URL
 * @returns {string} - Domain or 'Unknown'
 */
export function extractDomain(url) {
  try {
    return new URL(url).hostname
  } catch {
    return 'Unknown'
  }
}

/**
 * Pure function: Truncate URL for display
 * @param {string} url - Full URL
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated URL
 */
export function truncateUrl(url, maxLength = 50) {
  if (!url || url.length <= maxLength) return url
  return url.substring(0, maxLength - 3) + '...'
}

/**
 * Pure function: Sort calendars by name
 * @param {Array} calendars - Array of calendars
 * @returns {Array} - Sorted calendars (new array)
 */
export function sortCalendarsByName(calendars) {
  return [...calendars].sort((a, b) => 
    a.name.localeCompare(b.name, undefined, { sensitivity: 'base' })
  )
}

/**
 * Pure function: Filter calendars by search term
 * @param {Array} calendars - Array of calendars
 * @param {string} searchTerm - Search term
 * @returns {Array} - Filtered calendars (new array)
 */
export function filterCalendars(calendars, searchTerm) {
  if (!searchTerm || !searchTerm.trim()) {
    return [...calendars]
  }
  
  const term = searchTerm.toLowerCase().trim()
  return calendars.filter(calendar => 
    calendar.name.toLowerCase().includes(term) ||
    calendar.url.toLowerCase().includes(term)
  )
}

// === FORM STATE TRANSFORMATIONS (Pure Functions) ===

/**
 * Pure function: Create empty calendar form data
 * @returns {Object} - Empty calendar form
 */
export function createEmptyCalendar() {
  return {
    name: '',
    url: ''
  }
}

/**
 * Pure function: Reset form with validation cleared
 * @param {Object} currentForm - Current form state
 * @returns {Object} - Reset form state
 */
export function resetCalendarForm(currentForm) {
  return {
    ...createEmptyCalendar(),
    // Preserve any form metadata if it exists
    ...(currentForm.metadata && { metadata: currentForm.metadata })
  }
}

// === API RESPONSE TRANSFORMATIONS (Pure Functions) ===

/**
 * Pure function: Transform API error to user-friendly message
 * @param {Error} error - API error
 * @returns {string} - User-friendly error message
 */
export function transformApiError(error) {
  if (!error) return 'An unexpected error occurred'
  
  // Handle network errors
  if (!error.response) {
    return 'Network error. Please check your connection and try again.'
  }
  
  // Handle specific status codes
  const status = error.response.status
  const message = error.response.data?.message || error.message
  
  switch (status) {
    case 400:
      return message || 'Invalid request. Please check your input.'
    case 401:
      return 'Authentication required. Please log in.'
    case 404:
      return 'Resource not found.'
    case 429:
      return 'Too many requests. Please wait a moment and try again.'
    case 500:
      return 'Server error. Please try again later.'
    default:
      return message || `Error ${status}: Something went wrong.`
  }
}

/**
 * Pure function: Create API request headers
 * @param {string} userId - User ID
 * @returns {Object} - Request headers
 */
export function createApiHeaders(userId = 'anonymous') {
  return {
    'x-user-id': userId,
    'Content-Type': 'application/json'
  }
}

// === STATE MANAGEMENT HELPERS (Pure Functions) ===

/**
 * Pure function: Update calendar in list
 * @param {Array} calendars - Current calendars array
 * @param {Object} updatedCalendar - Updated calendar data
 * @returns {Array} - New calendars array with update applied
 */
export function updateCalendarInList(calendars, updatedCalendar) {
  return calendars.map(calendar => 
    calendar.id === updatedCalendar.id ? { ...calendar, ...updatedCalendar } : calendar
  )
}

/**
 * Pure function: Remove calendar from list
 * @param {Array} calendars - Current calendars array
 * @param {string} calendarId - ID of calendar to remove
 * @returns {Array} - New calendars array with calendar removed
 */
export function removeCalendarFromList(calendars, calendarId) {
  return calendars.filter(calendar => calendar.id !== calendarId)
}

/**
 * Pure function: Add calendar to list
 * @param {Array} calendars - Current calendars array
 * @param {Object} newCalendar - New calendar to add
 * @returns {Array} - New calendars array with calendar added
 */
export function addCalendarToList(calendars, newCalendar) {
  return [...calendars, newCalendar]
}