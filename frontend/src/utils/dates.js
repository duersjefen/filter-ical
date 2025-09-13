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
    
    // Handle iCal format dates (YYYYMMDDTHHMMSSZ or YYYYMMDD)
    if (typeof dateString === 'string') {
      if (dateString.match(/^\d{8}T\d{6}Z?$/)) {
        // Format: 20231215T140000Z
        const year = dateString.substring(0, 4)
        const month = dateString.substring(4, 6)
        const day = dateString.substring(6, 8)
        const hour = dateString.substring(9, 11)
        const minute = dateString.substring(11, 13)
        date = new Date(`${year}-${month}-${day}T${hour}:${minute}:00`)
      } else if (dateString.match(/^\d{8}$/)) {
        // Format: 20231215 (date only)
        const year = dateString.substring(0, 4)
        const month = dateString.substring(4, 6)
        const day = dateString.substring(6, 8)
        date = new Date(`${year}-${month}-${day}`)
      } else {
        // Try parsing as regular date string
        date = new Date(dateString)
      }
    } else {
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
  
  const startDate = parseIcalDate(event.dtstart)
  const endDate = parseIcalDate(event.dtend)
  
  if (!startDate) return 'No start date'
  
  // If no end date or same day, show single date
  if (!endDate || startDate.toDateString() === endDate.toDateString()) {
    return formatDateTime(event.dtstart)
  }
  
  // Multi-day event - show date range
  const hasStartTime = event.dtstart && (event.dtstart.includes('T') || event.dtstart.includes(':'))
  const hasEndTime = event.dtend && (event.dtend.includes('T') || event.dtend.includes(':'))
  
  try {
    // For multi-day events, typically we want just dates without times
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
    
    // If both have times and it's not an all-day event
    if (hasStartTime && hasEndTime) {
      return `${startStr} → ${endStr}`
    }
    
    return `${startStr} – ${endStr}`
  } catch (error) {
    console.warn('Date range formatting error:', error, 'for event:', event)
    return formatDateTime(event.dtstart)
  }
}