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
   * Uses selectionStore as single source of truth
   */
  const previewEvents = computed(() => {
    const allEvents = appStore.events || []
    const selection = selectionStore.selectedRecurringEvents
    
    // DEBUG: Log data for troubleshooting
    console.log('🔍 Preview Debug:', {
      allEventsCount: allEvents.length,
      selection: selection,
      selectionLength: selection.length,
      appStoreEvents: !!appStore.events,
      appStoreEventsCount: appStore.events?.length || 0
    })
    
    const selectedEvents = filterEventsBySelection(allEvents, selection)
    const futureEvents = filterFutureEvents(selectedEvents)
    
    console.log('🔍 Preview Results:', {
      selectedEventsCount: selectedEvents.length,
      futureEventsCount: futureEvents.length
    })
    
    return futureEvents
  })
  
  /**
   * Sorted preview events (by date ascending)
   */
  const sortedPreviewEvents = computed(() => {
    return [...previewEvents.value].sort((a, b) => {
      const dateA = new Date(a.start || a.dtstart)
      const dateB = new Date(b.start || b.dtstart)
      return dateA - dateB
    })
  })
  
  /**
   * Check if preview should be visible
   */
  const hasPreviewEvents = computed(() => {
    return selectionStore.selectedRecurringEvents.length > 0
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
   * Group events by recurring event category
   */
  function groupEventsByCategory(events, getRecurringEventKey) {
    const groups = {}
    
    events.forEach(event => {
      const category = getRecurringEventKey(event)
      if (!groups[category]) {
        groups[category] = {
          name: category,
          events: []
        }
      }
      groups[category].events.push(event)
    })
    
    return Object.values(groups).sort((a, b) => b.events.length - a.events.length)
  }
  
  /**
   * Group events by month
   */
  function groupEventsByMonth(events) {
    const groups = {}
    
    events.forEach(event => {
      const date = new Date(event.start || event.dtstart)
      const monthKey = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
      
      if (!groups[monthKey]) {
        groups[monthKey] = {
          name: monthKey,
          events: []
        }
      }
      groups[monthKey].events.push(event)
    })
    
    return Object.values(groups).sort((a, b) => {
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