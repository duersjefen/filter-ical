/**
 * Tests for dateFormatting utilities
 *
 * Following TDD principles from CLAUDE.md:
 * - Unit tests for pure functions
 * - 100% coverage requirement
 * - Test happy paths + edge cases + error cases
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { parseIcalDate, formatDateTime, formatDateRange, analyzeSmartRecurringPattern } from '../../src/utils/dateFormatting'

// Mock i18n
vi.mock('../../src/i18n', () => ({
  default: {
    global: {
      locale: { value: 'en' },
      t: vi.fn((key) => {
        const translations = {
          'dateTime.noDate': 'No date',
          'dateTime.invalidDate': 'Invalid date',
          'dateTime.noEvent': 'No event',
          'dateTime.noStartDate': 'No start date',
          'dateTime.untitledEvent': 'Untitled Event',
          'dateTime.unknownEventType': 'Unknown Event Type',
          'datePatterns.weekdays': 'Weekdays',
          'datePatterns.weekends': 'Weekends',
          'datePatterns.dayNames.monday': 'Monday',
          'datePatterns.dayNames.tuesday': 'Tuesday',
          'datePatterns.dayNames.wednesday': 'Wednesday',
          'datePatterns.dayNames.thursday': 'Thursday',
          'datePatterns.dayNames.friday': 'Friday',
          'datePatterns.dayNames.saturday': 'Saturday',
          'datePatterns.dayNames.sunday': 'Sunday',
          'datePatterns.dayNamesShort.monday': 'Mon',
          'datePatterns.dayNamesShort.tuesday': 'Tue',
          'datePatterns.dayNamesShort.wednesday': 'Wed',
          'datePatterns.dayNamesShort.thursday': 'Thu',
          'datePatterns.dayNamesShort.friday': 'Fri',
          'datePatterns.dayNamesShort.saturday': 'Sat',
          'datePatterns.dayNamesShort.sunday': 'Sun'
        }
        return translations[key] || key
      })
    }
  }
}))

describe('dateFormatting', () => {
  // Suppress console.warn during tests
  const originalWarn = console.warn
  beforeEach(() => {
    console.warn = vi.fn()
  })
  afterEach(() => {
    console.warn = originalWarn
  })

  describe('parseIcalDate', () => {
    it('returns null for null/undefined input', () => {
      expect(parseIcalDate(null)).toBeNull()
      expect(parseIcalDate(undefined)).toBeNull()
      expect(parseIcalDate('')).toBeNull()
    })

    it('parses ISO 8601 format with Z suffix', () => {
      const date = parseIcalDate('2024-01-18T10:00:00Z')
      expect(date).toBeInstanceOf(Date)
      expect(date.getUTCFullYear()).toBe(2024)
      expect(date.getUTCMonth()).toBe(0) // January is 0
      expect(date.getUTCDate()).toBe(18)
      expect(date.getUTCHours()).toBe(10)
    })

    it('parses ISO 8601 format with milliseconds', () => {
      const date = parseIcalDate('2024-01-18T10:00:00.000Z')
      expect(date).toBeInstanceOf(Date)
      expect(date.getUTCFullYear()).toBe(2024)
      expect(date.getUTCMonth()).toBe(0)
      expect(date.getUTCDate()).toBe(18)
    })

    it('parses ISO 8601 format without Z suffix', () => {
      const date = parseIcalDate('2024-01-18T10:00:00')
      expect(date).toBeInstanceOf(Date)
      expect(date.getFullYear()).toBe(2024)
    })

    it('parses iCal format with time (YYYYMMDDTHHMMSSZ)', () => {
      const date = parseIcalDate('20231215T140000Z')
      expect(date).toBeInstanceOf(Date)
      expect(date.getUTCFullYear()).toBe(2023)
      expect(date.getUTCMonth()).toBe(11) // December is 11
      expect(date.getUTCDate()).toBe(15)
      expect(date.getUTCHours()).toBe(14)
    })

    it('parses iCal format without Z suffix', () => {
      const date = parseIcalDate('20231215T140000')
      expect(date).toBeInstanceOf(Date)
      expect(date.getUTCFullYear()).toBe(2023)
    })

    it('parses iCal date-only format (YYYYMMDD)', () => {
      const date = parseIcalDate('20231215')
      expect(date).toBeInstanceOf(Date)
      expect(date.getFullYear()).toBe(2023)
      expect(date.getMonth()).toBe(11)
      expect(date.getDate()).toBe(15)
    })

    it('handles Date objects', () => {
      const inputDate = new Date('2024-01-18T10:00:00Z')
      const date = parseIcalDate(inputDate)
      expect(date).toBeInstanceOf(Date)
      expect(date.getTime()).toBe(inputDate.getTime())
    })

    it('handles non-string, non-Date values', () => {
      const timestamp = 1705572000000 // 2024-01-18T10:00:00Z
      const date = parseIcalDate(timestamp)
      expect(date).toBeInstanceOf(Date)
      expect(date.getTime()).toBe(timestamp)
    })

    it('returns null for invalid date strings', () => {
      expect(parseIcalDate('invalid-date')).toBeNull()
      expect(parseIcalDate('not-a-date')).toBeNull()
    })

    it('falls back to standard Date parsing for unknown formats', () => {
      // Standard JavaScript date string
      const date = parseIcalDate('2024-01-18')
      expect(date).toBeInstanceOf(Date)
      expect(date.getFullYear()).toBe(2024)
    })

    it('returns null when date parsing throws error', () => {
      // Empty object creates an invalid date
      const date = parseIcalDate({})
      expect(date).toBeNull()
    })
  })

  describe('formatDateTime', () => {
    it('returns "No date" for null/undefined input', () => {
      expect(formatDateTime(null)).toBe('No date')
      expect(formatDateTime(undefined)).toBe('No date')
      expect(formatDateTime('')).toBe('No date')
    })

    it('formats date with time component (English)', () => {
      const result = formatDateTime('2024-01-18T10:00:00Z')
      expect(result).toContain('2024')
      expect(result).toContain('Jan')
      expect(result).toContain('18')
      expect(result).toContain(':')
      // Note: Time may differ based on timezone conversion
    })

    it('formats date without time component (English)', () => {
      const result = formatDateTime('20240118')
      expect(result).toContain('2024')
      expect(result).toContain('Jan')
      expect(result).toContain('18')
      expect(result).not.toContain(':')
    })

    it('formats date with time component (German)', async () => {
      const i18n = await import('../../src/i18n')
      i18n.default.global.locale.value = 'de'

      const result = formatDateTime('2024-01-18T10:00:00Z')
      expect(result).toContain('2024')

      i18n.default.global.locale.value = 'en' // Reset
    })

    it('detects time component from T separator', () => {
      const result = formatDateTime('2024-01-18T10:00:00Z')
      expect(result).toContain(':')
    })

    it('detects time component from colon', () => {
      const result = formatDateTime('2024-01-18 10:00:00')
      expect(result).toContain(':')
    })

    it('returns "No date" for invalid date string', () => {
      // Invalid date strings return null from parseIcalDate, so formatDateTime returns "No date"
      const result = formatDateTime('invalid-date')
      expect(result).toBe('No date')
    })
  })

  describe('formatDateRange', () => {
    it('returns "No event" for null/undefined event', () => {
      expect(formatDateRange(null)).toBe('No event')
      expect(formatDateRange(undefined)).toBe('No event')
    })

    it('returns "No start date" when event has no start field', () => {
      const event = { title: 'Test Event' }
      expect(formatDateRange(event)).toBe('No start date')
    })

    it('handles multiple start field names (start)', () => {
      const event = { start: '2024-01-18T10:00:00Z' }
      const result = formatDateRange(event)
      expect(result).toContain('2024')
    })

    it('handles multiple start field names (dtstart)', () => {
      const event = { dtstart: '2024-01-18T10:00:00Z' }
      const result = formatDateRange(event)
      expect(result).toContain('2024')
    })

    it('handles multiple start field names (start_time)', () => {
      const event = { start_time: '2024-01-18T10:00:00Z' }
      const result = formatDateRange(event)
      expect(result).toContain('2024')
    })

    it('handles multiple start field names (startTime)', () => {
      const event = { startTime: '2024-01-18T10:00:00Z' }
      const result = formatDateRange(event)
      expect(result).toContain('2024')
    })

    it('handles multiple start field names (datetime_start)', () => {
      const event = { datetime_start: '2024-01-18T10:00:00Z' }
      const result = formatDateRange(event)
      expect(result).toContain('2024')
    })

    it('handles multiple end field names (end)', () => {
      const event = {
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-18T11:00:00Z'
      }
      const result = formatDateRange(event)
      expect(result).toContain('–')
    })

    it('handles multiple end field names (dtend)', () => {
      const event = {
        start: '2024-01-18T10:00:00Z',
        dtend: '2024-01-18T11:00:00Z'
      }
      const result = formatDateRange(event)
      expect(result).toContain('–')
    })

    it('handles multiple end field names (end_time)', () => {
      const event = {
        start: '2024-01-18T10:00:00Z',
        end_time: '2024-01-18T11:00:00Z'
      }
      const result = formatDateRange(event)
      expect(result).toContain('–')
    })

    it('handles multiple end field names (endTime)', () => {
      const event = {
        start: '2024-01-18T10:00:00Z',
        endTime: '2024-01-18T11:00:00Z'
      }
      const result = formatDateRange(event)
      expect(result).toContain('–')
    })

    it('handles multiple end field names (datetime_end)', () => {
      const event = {
        start: '2024-01-18T10:00:00Z',
        datetime_end: '2024-01-18T11:00:00Z'
      }
      const result = formatDateRange(event)
      expect(result).toContain('–')
    })

    it('formats single date when no end date', () => {
      const event = { start: '2024-01-18T10:00:00Z' }
      const result = formatDateRange(event)
      expect(result).toContain('2024')
      expect(result).toContain('Jan')
    })

    it('formats same-day event with time range', () => {
      const event = {
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-18T11:00:00Z'
      }
      const result = formatDateRange(event)
      // Should contain time range separator
      expect(result).toContain('–')
      // Should contain time format (checking for colon)
      expect(result).toContain(':')
    })

    it('formats same-day event without time (date only)', () => {
      const event = {
        start: '20240118',
        end: '20240118'
      }
      const result = formatDateRange(event)
      expect(result).toContain('2024')
      expect(result).not.toContain(':')
    })

    it('formats same-day event with same start and end times', () => {
      const event = {
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-18T10:00:00Z'
      }
      const result = formatDateRange(event)
      expect(result).toContain('2024')
      // Should not show time range for identical times
    })

    it('formats multi-day event (different days, same year)', () => {
      const event = {
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-20T11:00:00Z'
      }
      const result = formatDateRange(event)
      expect(result).toContain('Jan')
      expect(result).toContain('18')
      expect(result).toContain('20')
      expect(result).toContain('–')
    })

    it('formats multi-day event (different years)', () => {
      const event = {
        start: '2024-12-30T10:00:00Z',
        end: '2025-01-02T11:00:00Z'
      }
      const result = formatDateRange(event)
      expect(result).toContain('2024')
      expect(result).toContain('2025')
      expect(result).toContain('–')
    })

    it('handles formatting errors gracefully', () => {
      console.warn = vi.fn()
      const event = {
        start: 'invalid-date',
        end: '2024-01-20T11:00:00Z'
      }
      const result = formatDateRange(event)
      expect(result).toBe('No start date')
    })

    it('falls back to formatDateTime on range formatting error', () => {
      // Create a scenario that might cause formatting error
      const event = {
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-20T11:00:00Z'
      }

      // Mock toLocaleDateString to throw error
      const originalToLocaleDateString = Date.prototype.toLocaleDateString
      Date.prototype.toLocaleDateString = vi.fn(() => {
        throw new Error('Mock formatting error')
      })

      const result = formatDateRange(event)
      expect(result).toBeTruthy()

      // Restore original function
      Date.prototype.toLocaleDateString = originalToLocaleDateString
    })
  })

  describe('analyzeSmartRecurringPattern', () => {
    const mockT = (key) => {
      const translations = {
        'datePatterns.weekdays': 'Weekdays',
        'datePatterns.weekends': 'Weekends',
        'datePatterns.dayNames.monday': 'Monday',
        'datePatterns.dayNames.tuesday': 'Tuesday',
        'datePatterns.dayNames.wednesday': 'Wednesday',
        'datePatterns.dayNames.thursday': 'Thursday',
        'datePatterns.dayNames.friday': 'Friday',
        'datePatterns.dayNames.saturday': 'Saturday',
        'datePatterns.dayNames.sunday': 'Sunday',
        'datePatterns.dayNamesShort.monday': 'Mon',
        'datePatterns.dayNamesShort.tuesday': 'Tue',
        'datePatterns.dayNamesShort.wednesday': 'Wed',
        'datePatterns.dayNamesShort.thursday': 'Thu',
        'datePatterns.dayNamesShort.friday': 'Fri',
        'datePatterns.dayNamesShort.saturday': 'Sat',
        'datePatterns.dayNamesShort.sunday': 'Sun'
      }
      return translations[key] || key
    }

    it('returns null for null/undefined input', () => {
      expect(analyzeSmartRecurringPattern(null, mockT)).toBeNull()
      expect(analyzeSmartRecurringPattern(undefined, mockT)).toBeNull()
    })

    it('returns null for empty array', () => {
      expect(analyzeSmartRecurringPattern([], mockT)).toBeNull()
    })

    it('returns null for events with no valid dates', () => {
      const events = [
        { start: 'invalid-date' },
        { start: null }
      ]
      expect(analyzeSmartRecurringPattern(events, mockT)).toBeNull()
    })

    it('returns day name for single day pattern', () => {
      const events = [
        { start: '2024-01-15T10:00:00Z' }, // Monday
        { start: '2024-01-22T10:00:00Z' }, // Monday
        { start: '2024-01-29T10:00:00Z' }  // Monday
      ]
      expect(analyzeSmartRecurringPattern(events, mockT)).toBe('Monday')
    })

    it('returns "Weekdays" for weekday pattern (3+ weekdays)', () => {
      const events = [
        { start: '2024-01-15T10:00:00Z' }, // Monday
        { start: '2024-01-16T10:00:00Z' }, // Tuesday
        { start: '2024-01-17T10:00:00Z' }  // Wednesday
      ]
      expect(analyzeSmartRecurringPattern(events, mockT)).toBe('Weekdays')
    })

    it('returns "Weekdays" for all 5 weekdays', () => {
      const events = [
        { start: '2024-01-15T10:00:00Z' }, // Monday
        { start: '2024-01-16T10:00:00Z' }, // Tuesday
        { start: '2024-01-17T10:00:00Z' }, // Wednesday
        { start: '2024-01-18T10:00:00Z' }, // Thursday
        { start: '2024-01-19T10:00:00Z' }  // Friday
      ]
      expect(analyzeSmartRecurringPattern(events, mockT)).toBe('Weekdays')
    })

    it('does not return "Weekdays" for only 2 weekdays', () => {
      const events = [
        { start: '2024-01-15T10:00:00Z' }, // Monday
        { start: '2024-01-16T10:00:00Z' }  // Tuesday
      ]
      const result = analyzeSmartRecurringPattern(events, mockT)
      expect(result).not.toBe('Weekdays')
    })

    it('returns "Weekends" for weekend pattern', () => {
      const events = [
        { start: '2024-01-13T10:00:00Z' }, // Saturday
        { start: '2024-01-14T10:00:00Z' }  // Sunday
      ]
      expect(analyzeSmartRecurringPattern(events, mockT)).toBe('Weekends')
    })

    it('returns "Saturday" for Saturday only', () => {
      const events = [
        { start: '2024-01-13T10:00:00Z' }, // Saturday
        { start: '2024-01-20T10:00:00Z' }  // Saturday
      ]
      // Single day returns day name, not "Weekends"
      expect(analyzeSmartRecurringPattern(events, mockT)).toBe('Saturday')
    })

    it('returns "Sunday" for Sunday only', () => {
      const events = [
        { start: '2024-01-14T10:00:00Z' }, // Sunday
        { start: '2024-01-21T10:00:00Z' }  // Sunday
      ]
      // Single day returns day name, not "Weekends"
      expect(analyzeSmartRecurringPattern(events, mockT)).toBe('Sunday')
    })

    it('returns abbreviated form for 2 specific days', () => {
      const events = [
        { start: '2024-01-15T10:00:00Z' }, // Monday
        { start: '2024-01-17T10:00:00Z' }  // Wednesday
      ]
      const result = analyzeSmartRecurringPattern(events, mockT)
      expect(result).toBe('Mon/Wed')
    })

    it('returns "Weekdays" for 3 weekdays', () => {
      const events = [
        { start: '2024-01-15T10:00:00Z' }, // Monday
        { start: '2024-01-17T10:00:00Z' }, // Wednesday
        { start: '2024-01-19T10:00:00Z' }  // Friday
      ]
      const result = analyzeSmartRecurringPattern(events, mockT)
      // Implementation considers 3+ weekdays as "Weekdays"
      expect(result).toBe('Weekdays')
    })

    it('sorts days in week order (2 specific days)', () => {
      const events = [
        { start: '2024-01-19T10:00:00Z' }, // Friday
        { start: '2024-01-13T10:00:00Z' }  // Saturday
      ]
      const result = analyzeSmartRecurringPattern(events, mockT)
      expect(result).toBe('Fri/Sat')
    })

    it('returns null for 4+ specific days (too many)', () => {
      const events = [
        { start: '2024-01-15T10:00:00Z' }, // Monday
        { start: '2024-01-16T10:00:00Z' }, // Tuesday
        { start: '2024-01-13T10:00:00Z' }, // Saturday
        { start: '2024-01-14T10:00:00Z' }  // Sunday
      ]
      expect(analyzeSmartRecurringPattern(events, mockT)).toBeNull()
    })

    it('handles dtstart field name', () => {
      const events = [
        { dtstart: '2024-01-15T10:00:00Z' }, // Monday
        { dtstart: '2024-01-22T10:00:00Z' }  // Monday
      ]
      expect(analyzeSmartRecurringPattern(events, mockT)).toBe('Monday')
    })

    it('removes duplicates of same day', () => {
      const events = [
        { start: '2024-01-15T10:00:00Z' }, // Monday
        { start: '2024-01-22T10:00:00Z' }, // Monday
        { start: '2024-01-29T10:00:00Z' }  // Monday
      ]
      expect(analyzeSmartRecurringPattern(events, mockT)).toBe('Monday')
    })

    it('filters out events with invalid dates', () => {
      const events = [
        { start: '2024-01-15T10:00:00Z' }, // Monday
        { start: 'invalid' },
        { start: '2024-01-22T10:00:00Z' }  // Monday
      ]
      expect(analyzeSmartRecurringPattern(events, mockT)).toBe('Monday')
    })
  })
})
