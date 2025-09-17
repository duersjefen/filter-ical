/**
 * Date utility functions for calendar formatting
 * Extracted from useCalendar composable for reusability
 */

/**
 * Parse iCal date format to JavaScript Date object
 * @param {string} dateString - iCal formatted date string
 * @returns {Date|null} - Parsed date or null if invalid
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
 * Format a date string for display with time if available
 * @param {string} dateString - iCal formatted date string
 * @returns {string} - Formatted date string
 */
export function formatDateTime(dateString) {
  const date = parseIcalDate(dateString)
  if (!date) return 'No date'
  
  try {
    // Format based on whether it has time component
    const hasTime = dateString && (dateString.includes('T') || dateString.includes(':'))
    
    if (hasTime) {
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric', 
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      })
    } else {
      return date.toLocaleDateString('en-US', {
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
 * Format a date range for an event
 * @param {Object} event - Event object with dtstart and dtend
 * @returns {string} - Formatted date range string
 */
export function formatDateRange(event) {
  if (!event) return 'No event'
  
  // Handle both API field names (start/end) and iCal field names (dtstart/dtend)
  const startField = event.start || event.dtstart
  const endField = event.end || event.dtend
  
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
    
    if (hasTime && startDate.getTime() !== endDate.getTime()) {
      // Same day with different times - show time range
      const startTimeStr = startDate.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      })
      const endTimeStr = endDate.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      })
      const dateStr = startDate.toLocaleDateString('en-US', {
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
    const startStr = startDate.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: startDate.getFullYear() !== endDate.getFullYear() ? 'numeric' : undefined
    })
    
    const endStr = endDate.toLocaleDateString('en-US', {
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