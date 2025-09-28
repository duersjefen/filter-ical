/**
 * Date Parsing and Formatting Utilities
 * Pure functions for handling iCal date formats with i18n support
 */

import i18n from '@/i18n'

/**
 * Parse various iCal date formats into JavaScript Date objects
 */
export function parseIcalDate(dateString) {
  if (!dateString) return null
  
  try {
    let date
    
    if (typeof dateString === 'string') {
      // Primary: Handle ISO 8601 format (web API standard)
      if (dateString.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/)) {
        // Format: 2024-01-18T10:00:00Z or 2024-01-18T10:00:00.000Z
        date = new Date(dateString)
      }
      // Secondary: Handle iCal format dates (YYYYMMDDTHHMMSSZ or YYYYMMDD)
      else if (dateString.match(/^\d{8}T\d{6}Z?$/)) {
        // Format: 20231215T140000Z
        const year = dateString.substring(0, 4)
        const month = dateString.substring(4, 6)
        const day = dateString.substring(6, 8)
        const hour = dateString.substring(9, 11)
        const minute = dateString.substring(11, 13)
        const second = dateString.substring(13, 15)
        date = new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}Z`)
      } else if (dateString.match(/^\d{8}$/)) {
        // Format: 20231215 (date only)
        const year = dateString.substring(0, 4)
        const month = dateString.substring(4, 6)
        const day = dateString.substring(6, 8)
        date = new Date(`${year}-${month}-${day}`)
      } else {
        // Fallback: Try parsing as any date string
        date = new Date(dateString)
      }
    } else {
      // Handle Date objects or other types
      date = new Date(dateString)
    }
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return null
    }
    
    return date
  } catch (error) {
    console.warn('Date parsing error:', error, 'for date:', dateString)
    return null
  }
}

/**
 * Get current locale from i18n system
 */
function getCurrentLocale() {
  return i18n.global.locale.value || 'en'
}

/**
 * Format a date string for display with i18n support
 */
export function formatDateTime(dateString) {
  const date = parseIcalDate(dateString)
  if (!date) return 'No date'
  
  try {
    const locale = getCurrentLocale()
    // Format based on whether it has time component
    const hasTime = dateString && (dateString.includes('T') || dateString.includes(':'))
    
    if (hasTime) {
      return date.toLocaleDateString(locale === 'de' ? 'de-DE' : 'en-US', {
        weekday: 'short',
        year: 'numeric', 
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      })
    } else {
      return date.toLocaleDateString(locale === 'de' ? 'de-DE' : 'en-US', {
        weekday: 'short',
        year: 'numeric', 
        month: 'short',
        day: 'numeric'
      })
    }
  } catch (error) {
    console.warn('Date formatting error:', error, 'for date:', dateString)
    return 'Invalid date'
  }
}

/**
 * Format a date range for events
 */
export function formatDateRange(event) {
  if (!event) return 'No event'
  
  // Handle multiple possible API field names
  const startField = event.start || event.dtstart || event.start_time || event.startTime || event.datetime_start
  const endField = event.end || event.dtend || event.end_time || event.endTime || event.datetime_end
  
  
  const startDate = parseIcalDate(startField)
  const endDate = parseIcalDate(endField)
  
  if (!startDate) return 'No start date'
  
  // If no end date, show single date/time
  if (!endDate) {
    return formatDateTime(startField)
  }
  
  // Check if it's the same day (comparing just the date part)
  const startDateOnly = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate())
  const endDateOnly = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate())
  const isSameDay = startDateOnly.getTime() === endDateOnly.getTime()
  
  // If same day, show single date with time range if applicable
  if (isSameDay) {
    const hasTime = startField && (startField.includes('T') || startField.includes(':'))
    const locale = getCurrentLocale()
    const localeStr = locale === 'de' ? 'de-DE' : 'en-US'
    
    if (hasTime && startDate.getTime() !== endDate.getTime()) {
      // Same day with different times - show time range
      const startTimeStr = startDate.toLocaleTimeString(localeStr, { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      })
      const endTimeStr = endDate.toLocaleTimeString(localeStr, { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      })
      const dateStr = startDate.toLocaleDateString(localeStr, {
        weekday: 'short',
        year: 'numeric',
        month: 'short', 
        day: 'numeric'
      })
      return `${dateStr}, ${startTimeStr}–${endTimeStr}`
    } else {
      // Same day, show single date
      return formatDateTime(startField)
    }
  }
  
  // Multi-day event - show date range
  try {
    const locale = getCurrentLocale()
    const localeStr = locale === 'de' ? 'de-DE' : 'en-US'
    
    const startStr = startDate.toLocaleDateString(localeStr, {
      month: 'short',
      day: 'numeric',
      year: startDate.getFullYear() !== endDate.getFullYear() ? 'numeric' : undefined
    })
    
    const endStr = endDate.toLocaleDateString(localeStr, {
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    })
    
    return `${startStr} – ${endStr}`
  } catch (error) {
    console.warn('Date range formatting error:', error, 'for event:', event)
    return formatDateTime(startField)
  }
}

/**
 * Analyze events to determine if they represent a true recurring pattern
 * Returns smart pattern descriptions based on actual event distribution
 */
export function analyzeSmartRecurringPattern(events, t) {
  if (!events || events.length === 0) return null
  
  const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
  const weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
  const weekends = ['saturday', 'sunday']
  
  // Get unique days of the week with event counts
  const dayFrequency = {}
  const eventDates = []
  
  events.forEach(event => {
    const date = new Date(event.start || event.dtstart)
    if (!isNaN(date.getTime())) {
      const dayName = dayNames[date.getDay()]
      dayFrequency[dayName] = (dayFrequency[dayName] || 0) + 1
      eventDates.push(date)
    }
  })
  
  const uniqueDays = Object.keys(dayFrequency)
  
  if (uniqueDays.length === 0) return null
  
  // Calculate time span of events
  if (eventDates.length > 0) {
    eventDates.sort((a, b) => a.getTime() - b.getTime())
    const timeSpanWeeks = (eventDates[eventDates.length - 1].getTime() - eventDates[0].getTime()) / (1000 * 60 * 60 * 24 * 7)
    
    // For truly recurring patterns, require:
    // 1. Multiple events spanning at least 2 weeks OR
    // 2. At least 3 events in the same day category
    const isActuallyRecurring = (timeSpanWeeks >= 2 && events.length >= 3) || 
                               (uniqueDays.length === 1 && events.length >= 3)
    
    if (uniqueDays.length === 1) {
      const day = uniqueDays[0]
      if (isActuallyRecurring) {
        // Truly recurring on the same day
        return `${t('datePatterns.every')} ${t(`datePatterns.dayNames.${day}`)}`
      } else {
        // Just happens to be on the same day, not actually recurring
        return `${t('datePatterns.eventsOn')} ${t(`datePatterns.dayNames.${day}`)}`
      }
    }
    
    // Check if it's all weekdays (and actually recurring)
    if (uniqueDays.every(day => weekdays.includes(day)) && uniqueDays.length >= 3 && isActuallyRecurring) {
      return t('datePatterns.weekdays')
    }
    
    // Check if it's weekends (and actually recurring)
    if (uniqueDays.every(day => weekends.includes(day)) && isActuallyRecurring) {
      return t('datePatterns.weekends')
    }
    
    // Multiple days but not clearly a pattern, or not recurring enough
    if (uniqueDays.length <= 3) {
      // Use abbreviated form for space
      const shortDays = uniqueDays.map(day => t(`datePatterns.dayNamesShort.${day}`))
      return shortDays.join('/')
    }
  }
  
  return null // Too complex or irregular pattern
}