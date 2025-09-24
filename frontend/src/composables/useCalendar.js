import { ref, computed, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { useSelectionStore } from '../stores/selectionStore'
import { useUsername } from './useUsername'
import { FILTER_MODES, PREVIEW_GROUPS, SORT_ORDERS, EVENT_LIMITS } from '../constants/ui'
import { parseIcalDate, formatDateTime, formatDateRange } from '../utils/dateFormatting'
import {
  getRecurringEventKey,
  getEventGroupKey, 
  transformRecurringEventsToArray,
  filterRecurringEventsBySearch,
  categorizeRecurringEvents,
  calculateSelectedRecurringEventsCount,
  filterEventsBySelection,
  filterFutureEvents,
  calculateRecurringEventStats,
  classifyRecurringEvent
} from '../utils/eventHelpers'

export function useCalendar(eventsData = null, recurringEventsData = null, initialCalendarId = null) {
  const appStore = useAppStore()
  const selectionStore = useSelectionStore()
  const { getUserId } = useUsername()
  
  // Use provided data or fall back to store
  const events = eventsData || computed(() => appStore.events)
  const recurringEvents = recurringEventsData || computed(() => appStore.recurringEvents)
  
  // Make calendar ID reactive to handle navigation between calendars
  const calendarId = ref(initialCalendarId)
  
  // Selection state - delegated to selectionStore as single source of truth
  const selectedRecurringEvents = computed({
    get: () => selectionStore.selectedRecurringEvents,
    set: (value) => { selectionStore.selectedRecurringEvents = value }
  })
  // expandedRecurringEvents now managed centrally in selectionStore
  const showSingleEvents = ref(false)
  const showRecurringEventsSection = ref(true)
  const showGroupsSection = ref(true)
  const showSelectedOnly = ref(false)
  const recurringEventSearch = ref('')
  
  // Watch for calendar changes - reset filter state
  watch(calendarId, (newCalendarId, oldCalendarId) => {
    if (oldCalendarId !== null && oldCalendarId !== newCalendarId) {
      console.log(`🔄 Calendar changed from ${oldCalendarId} to ${newCalendarId} - resetting filters`)
      
      // Reset filters when switching calendars
      selectedRecurringEvents.value = new Set()
      recurringEventSearch.value = ''
      showSingleEvents.value = false
      showSelectedOnly.value = false
    }
  })

  // Convert event types object to sorted array with events
  const recurringEventsSortedByCount = computed(() => {
    return transformRecurringEventsToArray(recurringEvents.value)
  })

  // Computed properties
  const filteredRecurringEvents = computed(() => {
    return filterRecurringEventsBySearch(recurringEventsSortedByCount.value, recurringEventSearch.value)
  })

  // Recurring events: event types that occur multiple times (count > 1)
  const mainRecurringEvents = computed(() => {
    return categorizeRecurringEvents(filteredRecurringEvents.value).main
  })

  // Alias for backwards compatibility and clearer naming
  const recurringRecurringEvents = computed(() => mainRecurringEvents.value)

  // Unique events: event types that occur only once (count === 1)
  const singleRecurringEvents = computed(() => {
    return categorizeRecurringEvents(filteredRecurringEvents.value).single
  })

  // Alias for more accurate naming
  const uniqueRecurringEvents = computed(() => singleRecurringEvents.value)

  const unifiedRecurringEvents = computed(() => {
    // Combine and sort all event types by count (highest first), then alphabetically
    return filteredRecurringEvents.value.sort((a, b) => {
      if (a.count !== b.count) {
        return b.count - a.count // Higher count first
      }
      return a.name.localeCompare(b.name) // Alphabetical if same count
    })
  })

  const selectedRecurringEventsCount = computed(() => {
    return calculateSelectedRecurringEventsCount(recurringEventsSortedByCount.value, selectedRecurringEvents.value)
  })

  const selectedEventsCount = computed(() => {
    return filterEventsBySelection(events.value, selectedRecurringEvents.value).length
  })


  // Three-tier event system analytics
  const recurringEventStats = computed(() => {
    return calculateRecurringEventStats(recurringEventsSortedByCount.value)
  })

  // Event type classification helper
  function classifyRecurringEventLocal(recurringEventName) {
    return classifyRecurringEvent(recurringEventsSortedByCount.value, recurringEventName)
  }

  // Methods

  function toggleRecurringEvent(recurringEventName) {
    selectionStore.toggleRecurringEvent(recurringEventName)
  }

  function toggleRecurringEventExpansion(recurringEventName) {
    // Delegate to centralized selectionStore
    if (selectionStore.expandedRecurringEvents.has(recurringEventName)) {
      selectionStore.expandedRecurringEvents.delete(recurringEventName)
    } else {
      selectionStore.expandedRecurringEvents.add(recurringEventName)
    }
  }

  function selectAllRecurringEvents() {
    const eventNames = filteredRecurringEvents.value.map(recurringEvent => recurringEvent.name)
    selectionStore.selectRecurringEvents(eventNames)
  }

  function clearAllRecurringEvents() {
    selectionStore.clearSelection()
  }

  function selectAllSingleEvents() {
    const singleRecurringEventNames = singleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
    const toAdd = singleRecurringEventNames.filter(name => !selectedRecurringEvents.value.includes(name))
    if (toAdd.length > 0) {
      selectionStore.selectRecurringEvents([...selectedRecurringEvents.value, ...toAdd])
    }
  }

  function clearAllSingleEvents() {
    const singleRecurringEventNames = singleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
    const remaining = selectedRecurringEvents.value.filter(name => !singleRecurringEventNames.includes(name))
    selectionStore.selectRecurringEvents(remaining)
  }



  async function generateIcalFile() {
    try {
      const result = await appStore.generateIcal({
        calendarId: appStore.selectedCalendar.id,
        selectedRecurringEvents: selectedRecurringEvents.value
      })
      
      if (result.success) {
        // Create and trigger download
        const blob = new Blob([result.data], { type: 'text/calendar' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${appStore.selectedCalendar.name}_filtered.ics`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } else {
        console.error('Error generating iCal:', result.error)
      }
    } catch (error) {
      console.error('Error generating iCal:', error)
    }
  }

  // Method to update calendar ID - triggers the watcher for calendar change detection
  const updateCalendarId = (newCalendarId) => {
    if (calendarId.value !== newCalendarId) {
      calendarId.value = newCalendarId
    }
  }

  // No filter initialization needed - filters start clean each session

  return {
    // State
    selectedRecurringEvents,
    expandedRecurringEvents: selectionStore.expandedRecurringEvents,
    showSingleEvents,
    showRecurringEventsSection,
    showGroupsSection,
    showSelectedOnly,
    recurringEventSearch,
    
    // Computed
    recurringEventsSortedByCount,
    filteredRecurringEvents,
    mainRecurringEvents,
    singleRecurringEvents,
    recurringRecurringEvents,
    uniqueRecurringEvents,
    unifiedRecurringEvents,
    recurringEventStats,
    selectedRecurringEventsCount,
    selectedEventsCount,
    
    // Methods
    getRecurringEventKey,
    getEventGroupKey,
    classifyRecurringEvent: classifyRecurringEventLocal,
    formatDateTime,
    formatDateRange,
    toggleRecurringEvent,
    toggleRecurringEventExpansion,
    selectAllRecurringEvents,
    clearAllRecurringEvents,
    selectAllSingleEvents,
    clearAllSingleEvents,
    generateIcalFile,
    updateCalendarId
  }
}