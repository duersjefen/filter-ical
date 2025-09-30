/**
 * Preview Events Composable
 * Provides reactive preview data based on current selections
 * 
 * Uses: selectionStore as single source of truth for selections
 * Returns: Filtered and sorted events for preview display
 */
import { computed } from 'vue'
import { useAppStore } from '../stores/app'
import { useSelectionStore } from '../stores/selectionStore'
import { filterEventsBySelection, filterFutureEvents, generateEventIdentifier } from '../utils/eventHelpers'

export function usePreview() {
  const appStore = useAppStore()
  const selectionStore = useSelectionStore()
  
  // ===============================================
  // CORE PREVIEW DATA COMPUTATION
  // ===============================================
  
  /**
   * Get all events that match the current selection
   * Uses selectionStore as single source of truth and reactive events from app store
   */
  const previewEvents = computed(() => {
    // Use the new reactive events extraction from app store
    const allEvents = appStore.allEventsFromGroups || []
    const selection = selectionStore.selectedRecurringEvents

    console.log('🔍 Preview computing:', {
      allEventsCount: allEvents.length,
      selectionCount: selection.length,
      firstEventTitle: allEvents[0]?.title,
      firstEventFields: allEvents[0] ? Object.keys(allEvents[0]) : []
    })

    const selectedEvents = filterEventsBySelection(allEvents, selection)
    const futureEvents = filterFutureEvents(selectedEvents)

    console.log('📊 Preview filtered:', {
      selectedEventsCount: selectedEvents.length,
      futureEventsCount: futureEvents.length,
      firstFutureEventTitle: futureEvents[0]?.title
    })

    return futureEvents
  })
  
  /**
   * Sorted preview events (by date ascending) with deduplication
   * Removes duplicate events that appear in multiple groups
   */
  const sortedPreviewEvents = computed(() => {
    // Deduplicate using robust content-based identifiers (backup safety net)
    const uniqueEvents = new Map()
    previewEvents.value.forEach(event => {
      const identifier = generateEventIdentifier(event)
      
      if (!uniqueEvents.has(identifier)) {
        uniqueEvents.set(identifier, event)
      }
    })
    
    // Then sort by date
    return [...uniqueEvents.values()].sort((a, b) => {
      const dateA = new Date(a.start || a.dtstart)
      const dateB = new Date(b.start || b.dtstart)
      return dateA - dateB
    })
  })
  
  /**
   * Check if preview should be visible
   * Preview should show when there are actual filtered future events to display
   */
  const hasPreviewEvents = computed(() => {
    return sortedPreviewEvents.value.length > 0
  })
  
  /**
   * Count of preview events
   */
  const previewEventCount = computed(() => {
    return sortedPreviewEvents.value.length
  })
  
  // ===============================================
  // GROUPING FUNCTIONS (PURE)
  // ===============================================
  
  /**
   * Group events by recurring event category with deduplication
   */
  function groupEventsByCategory(events, getRecurringEventKey) {
    const groups = {}
    
    events.forEach(event => {
      const category = getRecurringEventKey(event)
      if (!groups[category]) {
        groups[category] = {
          name: category,
          events: [],
          seenIdentifiers: new Set()
        }
      }
      
      // Use consistent identifier strategy
      const identifier = generateEventIdentifier(event)
      
      // Only add if we haven't seen this identifier in this category
      if (!groups[category].seenIdentifiers.has(identifier)) {
        groups[category].events.push(event)
        groups[category].seenIdentifiers.add(identifier)
      }
    })
    
    // Clean up seenIdentifiers before returning
    return Object.values(groups).map(group => ({
      name: group.name,
      events: group.events
    })).sort((a, b) => b.events.length - a.events.length)
  }
  
  /**
   * Group events by month with deduplication
   */
  function groupEventsByMonth(events) {
    const groups = {}
    
    events.forEach(event => {
      const date = new Date(event.start || event.dtstart)
      const monthKey = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
      
      if (!groups[monthKey]) {
        groups[monthKey] = {
          name: monthKey,
          events: [],
          seenIdentifiers: new Set()
        }
      }
      
      // Use consistent identifier strategy
      const identifier = generateEventIdentifier(event)
      
      // Only add if we haven't seen this identifier in this month
      if (!groups[monthKey].seenIdentifiers.has(identifier)) {
        groups[monthKey].events.push(event)
        groups[monthKey].seenIdentifiers.add(identifier)
      }
    })
    
    // Clean up seenIdentifiers before returning and ensure we have events
    return Object.values(groups)
      .filter(group => group.events.length > 0)
      .map(group => ({
        name: group.name,
        events: group.events
      }))
      .sort((a, b) => {
        const dateA = new Date(a.events[0].start || a.events[0].dtstart)
        const dateB = new Date(b.events[0].start || b.events[0].dtstart)
        return dateA - dateB
      })
  }

  /**
   * Group events by year, then by month with deduplication
   */
  function groupEventsByYear(events) {
    const yearGroups = {}
    
    events.forEach(event => {
      const date = new Date(event.start || event.dtstart)
      const year = date.getFullYear()
      const monthKey = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
      
      // Initialize year group if doesn't exist
      if (!yearGroups[year]) {
        yearGroups[year] = {
          year: year,
          months: {},
          totalEvents: 0
        }
      }
      
      // Initialize month within year if doesn't exist
      if (!yearGroups[year].months[monthKey]) {
        yearGroups[year].months[monthKey] = {
          name: monthKey,
          events: [],
          seenIdentifiers: new Set()
        }
      }
      
      // Use consistent identifier strategy
      const identifier = generateEventIdentifier(event)
      
      // Only add if we haven't seen this identifier in this month
      if (!yearGroups[year].months[monthKey].seenIdentifiers.has(identifier)) {
        yearGroups[year].months[monthKey].events.push(event)
        yearGroups[year].months[monthKey].seenIdentifiers.add(identifier)
        yearGroups[year].totalEvents++
      }
    })
    
    // Convert to final structure and sort
    return Object.values(yearGroups)
      .map(yearGroup => ({
        year: yearGroup.year,
        totalEvents: yearGroup.totalEvents,
        months: Object.values(yearGroup.months)
          .filter(month => month.events.length > 0)
          .map(month => ({
            name: month.name,
            events: month.events
          }))
          .sort((a, b) => {
            const dateA = new Date(a.events[0].start || a.events[0].dtstart)
            const dateB = new Date(b.events[0].start || b.events[0].dtstart)
            return dateA - dateB
          })
      }))
      .filter(yearGroup => yearGroup.months.length > 0)
      .sort((a, b) => a.year - b.year)
  }
  
  // ===============================================
  // COMPUTED GROUPED EVENTS
  // ===============================================
  
  /**
   * Get events grouped by category for display
   */
  const getGroupedEventsByCategory = (getRecurringEventKey) => {
    return computed(() => groupEventsByCategory(sortedPreviewEvents.value, getRecurringEventKey))
  }
  
  /**
   * Get events grouped by month for display
   */
  const getGroupedEventsByMonth = () => {
    return computed(() => groupEventsByMonth(sortedPreviewEvents.value))
  }
  
  // ===============================================
  // RETURN API
  // ===============================================
  
  return {
    // Core data
    previewEvents,
    sortedPreviewEvents,
    hasPreviewEvents,
    previewEventCount,
    
    // Grouping functions
    groupEventsByCategory,
    groupEventsByMonth,
    groupEventsByYear,
    getGroupedEventsByCategory,
    getGroupedEventsByMonth,
    
    // Selection integration
    selectionStore
  }
}