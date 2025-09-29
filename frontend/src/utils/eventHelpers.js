/**
 * Event classification and grouping utilities
 * Pure functions for event processing logic
 */
import i18n from '@/i18n'

/**
 * Generate a unique identifier for an event
 * Priority: UID > title+start+end > title+start+description_hash
 */
export function generateEventIdentifier(event) {
  // First priority: use UID if available
  if (event.uid) {
    return event.uid
  }
  
  // Second priority: use title + start + end
  const title = event.title || event.summary || 'untitled'
  const start = event.start || event.dtstart || ''
  const end = event.end || event.dtend || ''
  
  if (start && end) {
    return `${title}-${start}-${end}`
  }
  
  // Third priority: use title + start + description hash
  if (start) {
    const description = event.description || ''
    const descHash = description ? description.length.toString() : '0'
    return `${title}-${start}-${descHash}`
  }
  
  // Fallback: title + description hash
  const description = event.description || ''
  const descHash = description ? description.length.toString() : '0'
  return `${title}-${descHash}`
}

/**
 * Get the key used for filtering events by title
 */
export function getRecurringEventKey(event) {
  return event.title || event.summary || i18n.global.t('dateTime.untitledEvent')
}

/**
 * Get the key used for grouping events by type in preview
 */
export function getEventGroupKey(event) {
  return event.title || event.summary || i18n.global.t('dateTime.unknownEventType')
}

/**
 * Transform recurring events object to sorted array
 */
export function transformRecurringEventsToArray(recurringEventsData) {
  if (!recurringEventsData) return []
  if (Array.isArray(recurringEventsData)) return recurringEventsData
  
  return Object.entries(recurringEventsData)
    .filter(([name, recurringEventData]) => recurringEventData != null && name != null) // Filter out null entries
    .map(([name, recurringEventData]) => {
      const count = recurringEventData.count || 0
      const typeEvents = recurringEventData.events || []
      
      return {
        name,
        count,
        events: typeEvents
      }
    })
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
}

/**
 * Filter recurring events by search term
 */
export function filterRecurringEventsBySearch(recurringEvents, searchTerm) {
  if (!searchTerm.trim()) return recurringEvents
  
  const searchLower = searchTerm.toLowerCase()
  return recurringEvents.filter(recurringEvent => 
    recurringEvent && recurringEvent.name && recurringEvent.name.toLowerCase().includes(searchLower)
  )
}

/**
 * Separate recurring events by count (main vs single)
 */
export function categorizeRecurringEvents(recurringEvents) {
  const main = recurringEvents.filter(event => event && typeof event.count === 'number' && event.count > 1)
  const single = recurringEvents.filter(event => event && typeof event.count === 'number' && event.count === 1)
  
  return { main, single }
}

/**
 * Calculate total count for selected recurring events
 */
export function calculateSelectedRecurringEventsCount(recurringEvents, selectedRecurringEventNames) {
  return recurringEvents
    .filter(recurringEvent => selectedRecurringEventNames.includes(recurringEvent.name))
    .reduce((sum, recurringEvent) => sum + recurringEvent.count, 0)
}

/**
 * Filter events by selected recurring event names
 */
export function filterEventsBySelection(events, selectedRecurringEventNames) {
  if (selectedRecurringEventNames.length === 0) return []
  
  const selectedSet = new Set(selectedRecurringEventNames)
  return events.filter(event => {
    const recurringEventKey = getRecurringEventKey(event)
    return selectedSet.has(recurringEventKey)
  })
}

/**
 * Filter out past events, keeping only future events
 */
export function filterFutureEvents(events) {
  const now = new Date()
  
  return events.filter(event => {
    const eventStart = event.start || event.dtstart
    if (!eventStart) return true // Keep events without start dates
    
    return new Date(eventStart) >= now
  })
}

/**
 * Calculate recurring event statistics
 */
export function calculateRecurringEventStats(recurringEvents) {
  const { main, single } = categorizeRecurringEvents(recurringEvents)
  
  return {
    totalRecurringEvents: recurringEvents.length,
    recurringRecurringEvents: main.length,
    uniqueRecurringEvents: single.length,
    totalEvents: recurringEvents.reduce((sum, event) => sum + event.count, 0),
    recurringEvents: main.reduce((sum, event) => sum + event.count, 0),
    uniqueEvents: single.length
  }
}

/**
 * Classify recurring event type
 */
export function classifyRecurringEvent(recurringEvents, recurringEventName) {
  const recurringEvent = recurringEvents.find(et => et.name === recurringEventName)
  if (!recurringEvent) return 'unknown'
  
  return recurringEvent.count === 1 ? 'unique' : 'recurring'
}