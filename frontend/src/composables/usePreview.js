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
import { filterEventsBySelection, filterFutureEvents } from '../utils/eventHelpers'

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
    
    const selectedEvents = filterEventsBySelection(allEvents, selection)
    const futureEvents = filterFutureEvents(selectedEvents)
    
    return futureEvents
  })
  
  /**
   * Sorted preview events (by date ascending) with deduplication
   * Removes duplicate events that appear in multiple groups
   */
  const sortedPreviewEvents = computed(() => {
    // First deduplicate by uid to prevent same event showing multiple times
    const uniqueEvents = new Map()
    previewEvents.value.forEach(event => {
      if (event.uid && !uniqueEvents.has(event.uid)) {
        uniqueEvents.set(event.uid, event)
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
          seenUids: new Set()
        }
      }
      
      // Only add if we haven't seen this uid in this category
      if (!groups[category].seenUids.has(event.uid)) {
        groups[category].events.push(event)
        groups[category].seenUids.add(event.uid)
      }
    })
    
    // Clean up seenUids before returning
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
          seenUids: new Set()
        }
      }
      
      // Only add if we haven't seen this uid in this month
      if (!groups[monthKey].seenUids.has(event.uid)) {
        groups[monthKey].events.push(event)
        groups[monthKey].seenUids.add(event.uid)
      }
    })
    
    // Clean up seenUids before returning and ensure we have events
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
    getGroupedEventsByCategory,
    getGroupedEventsByMonth,
    
    // Selection integration
    selectionStore
  }
}