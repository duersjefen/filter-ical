/**
 * Pure Function Tests for Calendar Data
 * Demonstrates Rich Hickey's functional principles in frontend testing
 * 
 * These tests require NO mocking, NO setup, NO Vue/Pinia dependencies
 * Pure functions = predictable testing
 */

// Import pure functions
import {
  validateCalendarData,
  isValidUrlFormat,
  normalizeCalendarData,
  calendarToDisplayFormat,
  extractDomain,
  truncateUrl,
  sortCalendarsByName,
  filterCalendars,
  createEmptyCalendar,
  resetCalendarForm,
  transformApiError,
  createApiHeaders,
  updateCalendarInList,
  removeCalendarFromList,
  addCalendarToList
} from '../composables/useCalendarData.js'

// === VALIDATION TESTS (Pure Functions) ===

describe('validateCalendarData', () => {
  test('should validate correct calendar data', () => {
    const calendar = { name: 'Test Calendar', url: 'https://example.com/cal.ics' }
    const result = validateCalendarData(calendar)
    
    expect(result.isValid).toBe(true)
    expect(result.errors).toHaveLength(0)
  })
  
  test('should reject empty name', () => {
    const calendar = { name: '', url: 'https://example.com/cal.ics' }
    const result = validateCalendarData(calendar)
    
    expect(result.isValid).toBe(false)
    expect(result.errors).toContain('Calendar name is required')
  })
  
  test('should reject empty URL', () => {
    const calendar = { name: 'Test', url: '' }
    const result = validateCalendarData(calendar)
    
    expect(result.isValid).toBe(false)
    expect(result.errors).toContain('Calendar URL is required')
  })
  
  test('should reject invalid URL format', () => {
    const calendar = { name: 'Test', url: 'not-a-url' }
    const result = validateCalendarData(calendar)
    
    expect(result.isValid).toBe(false)
    expect(result.errors).toContain('Please enter a valid URL starting with http:// or https://')
  })
})

describe('isValidUrlFormat', () => {
  test('should accept valid HTTPS URLs', () => {
    expect(isValidUrlFormat('https://example.com')).toBe(true)
  })
  
  test('should accept valid HTTP URLs', () => {
    expect(isValidUrlFormat('http://example.com')).toBe(true)
  })
  
  test('should reject invalid URLs', () => {
    expect(isValidUrlFormat('not-a-url')).toBe(false)
    expect(isValidUrlFormat('ftp://example.com')).toBe(false)
    expect(isValidUrlFormat('')).toBe(false)
  })
})

// === TRANSFORMATION TESTS (Pure Functions) ===

describe('normalizeCalendarData', () => {
  test('should trim whitespace from name and URL', () => {
    const calendar = { name: '  Test Calendar  ', url: '  https://example.com  ' }
    const result = normalizeCalendarData(calendar)
    
    expect(result.name).toBe('Test Calendar')
    expect(result.url).toBe('https://example.com')
  })
  
  test('should handle missing properties', () => {
    const calendar = {}
    const result = normalizeCalendarData(calendar)
    
    expect(result.name).toBe('')
    expect(result.url).toBe('')
  })
})

describe('calendarToDisplayFormat', () => {
  test('should transform API calendar to display format', () => {
    const apiCalendar = {
      id: '123',
      name: 'Test Calendar',
      url: 'https://example.com/calendar.ics'
    }
    
    const result = calendarToDisplayFormat(apiCalendar)
    
    expect(result.id).toBe('123')
    expect(result.name).toBe('Test Calendar')
    expect(result.displayName).toBe('Test Calendar')
    expect(result.domain).toBe('example.com')
    expect(result.shortUrl).toBe('https://example.com/calendar.ics')
  })
})

describe('extractDomain', () => {
  test('should extract domain from URL', () => {
    expect(extractDomain('https://example.com/path')).toBe('example.com')
    expect(extractDomain('http://subdomain.example.org:8080/cal')).toBe('subdomain.example.org')
  })
  
  test('should handle invalid URLs', () => {
    expect(extractDomain('not-a-url')).toBe('Unknown')
  })
})

describe('truncateUrl', () => {
  test('should truncate long URLs', () => {
    const longUrl = 'https://example.com/very/long/path/to/calendar.ics'
    const result = truncateUrl(longUrl, 20)
    
    expect(result).toBe('https://example.co...')
    expect(result.length).toBe(20)
  })
  
  test('should not truncate short URLs', () => {
    const shortUrl = 'https://example.com'
    const result = truncateUrl(shortUrl, 50)
    
    expect(result).toBe(shortUrl)
  })
})

// === ARRAY TRANSFORMATION TESTS (Immutable) ===

describe('sortCalendarsByName', () => {
  test('should sort calendars by name alphabetically', () => {
    const calendars = [
      { name: 'Zebra Calendar' },
      { name: 'Alpha Calendar' },
      { name: 'Beta Calendar' }
    ]
    
    const sorted = sortCalendarsByName(calendars)
    
    expect(sorted[0].name).toBe('Alpha Calendar')
    expect(sorted[1].name).toBe('Beta Calendar')
    expect(sorted[2].name).toBe('Zebra Calendar')
    
    // Original array should be unchanged (immutable)
    expect(calendars[0].name).toBe('Zebra Calendar')
  })
})

describe('filterCalendars', () => {
  const calendars = [
    { name: 'Work Calendar', url: 'https://work.com/cal' },
    { name: 'Personal Calendar', url: 'https://personal.com/cal' },
    { name: 'Sports Events', url: 'https://sports.com/events' }
  ]
  
  test('should filter by name', () => {
    const filtered = filterCalendars(calendars, 'work')
    
    expect(filtered).toHaveLength(1)
    expect(filtered[0].name).toBe('Work Calendar')
  })
  
  test('should filter by URL', () => {
    const filtered = filterCalendars(calendars, 'sports.com')
    
    expect(filtered).toHaveLength(1)
    expect(filtered[0].name).toBe('Sports Events')
  })
  
  test('should return all calendars for empty search', () => {
    const filtered = filterCalendars(calendars, '')
    
    expect(filtered).toHaveLength(3)
    // Should be new array (immutable)
    expect(filtered).not.toBe(calendars)
  })
})

// === STATE MANAGEMENT TESTS (Immutable) ===

describe('updateCalendarInList', () => {
  test('should update calendar immutably', () => {
    const calendars = [
      { id: '1', name: 'Calendar 1' },
      { id: '2', name: 'Calendar 2' }
    ]
    
    const updated = updateCalendarInList(calendars, { id: '2', name: 'Updated Calendar 2' })
    
    expect(updated[1].name).toBe('Updated Calendar 2')
    // Original should be unchanged
    expect(calendars[1].name).toBe('Calendar 2')
    // Should be new array
    expect(updated).not.toBe(calendars)
  })
})

describe('removeCalendarFromList', () => {
  test('should remove calendar immutably', () => {
    const calendars = [
      { id: '1', name: 'Calendar 1' },
      { id: '2', name: 'Calendar 2' },
      { id: '3', name: 'Calendar 3' }
    ]
    
    const updated = removeCalendarFromList(calendars, '2')
    
    expect(updated).toHaveLength(2)
    expect(updated.find(cal => cal.id === '2')).toBeUndefined()
    // Original should be unchanged
    expect(calendars).toHaveLength(3)
    // Should be new array
    expect(updated).not.toBe(calendars)
  })
})

describe('addCalendarToList', () => {
  test('should add calendar immutably', () => {
    const calendars = [
      { id: '1', name: 'Calendar 1' }
    ]
    
    const newCalendar = { id: '2', name: 'Calendar 2' }
    const updated = addCalendarToList(calendars, newCalendar)
    
    expect(updated).toHaveLength(2)
    expect(updated[1]).toBe(newCalendar)
    // Original should be unchanged
    expect(calendars).toHaveLength(1)
    // Should be new array
    expect(updated).not.toBe(calendars)
  })
})

// === ERROR HANDLING TESTS (Pure Functions) ===

describe('transformApiError', () => {
  test('should handle network errors', () => {
    const error = { message: 'Network Error' }
    const result = transformApiError(error)
    
    expect(result).toBe('Network error. Please check your connection and try again.')
  })
  
  test('should handle 400 status', () => {
    const error = {
      response: {
        status: 400,
        data: { message: 'Invalid calendar data' }
      }
    }
    
    const result = transformApiError(error)
    expect(result).toBe('Invalid calendar data')
  })
  
  test('should handle 404 status', () => {
    const error = { response: { status: 404 } }
    const result = transformApiError(error)
    
    expect(result).toBe('Resource not found.')
  })
})

describe('createApiHeaders', () => {
  test('should create headers with default user', () => {
    const headers = createApiHeaders()
    
    expect(headers['x-user-id']).toBe('anonymous')
    expect(headers['Content-Type']).toBe('application/json')
  })
  
  test('should create headers with custom user', () => {
    const headers = createApiHeaders('user123')
    
    expect(headers['x-user-id']).toBe('user123')
  })
})

/**
 * WHAT THESE TESTS DEMONSTRATE:
 * 
 * 1. NO MOCKING REQUIRED
 *    - All functions are pure, so no external dependencies to mock
 *    - Tests run in isolation without Vue/Pinia/HTTP setup
 * 
 * 2. PREDICTABLE BEHAVIOR
 *    - Same input always produces same output
 *    - No hidden state or side effects to worry about
 * 
 * 3. IMMUTABLE OPERATIONS
 *    - Array operations return new arrays, don't mutate originals
 *    - Object transformations create new objects
 * 
 * 4. EASY TO DEBUG
 *    - Test failures point directly to the problematic transformation
 *    - No complex object state to understand
 * 
 * 5. FAST EXECUTION
 *    - No async operations or external dependencies
 *    - Tests run in milliseconds, not seconds
 * 
 * This is the power of Rich Hickey's functional programming principles applied to frontend development.
 */