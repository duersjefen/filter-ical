import { ref, computed, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { useSelectionStore } from '../stores/selectionStore'
import { useUsername } from './useUsername'
import { FILTER_MODES, PREVIEW_GROUPS, SORT_ORDERS, EVENT_LIMITS } from '../constants/ui'
import { parseIcalDate, formatDateTime, formatDateRange } from '../utils/dateFormatting'
import { getFilterStorageKey, saveFiltersData, loadFiltersData } from '../utils/localStorage'
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
  
  // Reactive state - these will be loaded from backend preferences
  const selectedRecurringEvents = ref([])
  // expandedRecurringEvents now managed centrally in selectionStore
  const showSingleEvents = ref(false)
  const showRecurringEventsSection = ref(true)
  const showGroupsSection = ref(true)
  const showSelectedOnly = ref(false)
  const recurringEventSearch = ref('')
  const showPreview = ref(false)
  const previewGroup = ref(PREVIEW_GROUPS.NONE)
  const previewOrder = ref(SORT_ORDERS.ASC)
  const previewLimit = ref(EVENT_LIMITS.PREVIEW_DEFAULT)
  
  // Filter persistence functions - now includes user ID for proper isolation

  const saveFiltersToLocalStorage = () => {
    const storageKey = getFilterStorageKey(calendarId.value, getUserId())
    const filtersData = {
      selectedRecurringEvents: selectedRecurringEvents.value,
      recurringEventSearch: recurringEventSearch.value,
      showSingleEvents: showSingleEvents.value,
      showSelectedOnly: showSelectedOnly.value
      // expandedRecurringEvents now managed centrally in selectionStore
    }
    
    const result = saveFiltersData(storageKey, filtersData)
    if (result.success) {
      console.log(`💾 Filters saved for calendar: ${calendarId.value || 'default'} (user: ${getUserId()})`)
    } else {
      console.warn('Failed to save filters to localStorage:', result.error)
    }
  }

  const loadFiltersFromLocalStorage = () => {
    const storageKey = getFilterStorageKey(calendarId.value, getUserId())
    const result = loadFiltersData(storageKey)
    
    if (result.success && result.data) {
      const filtersData = result.data
      
      selectedRecurringEvents.value = filtersData.selectedRecurringEvents
      recurringEventSearch.value = filtersData.recurringEventSearch
      showSingleEvents.value = filtersData.showSingleEvents
      showSelectedOnly.value = filtersData.showSelectedOnly
      // expandedRecurringEvents now managed centrally in selectionStore
      
      console.log(`📂 Filters loaded for calendar: ${calendarId.value || 'default'} (user: ${getUserId()})`)
      return true
    } else if (result.error) {
      console.warn('Failed to load filters from localStorage:', result.error)
    }
    return false
  }

  // Watch for calendar changes - save current filters and load new calendar's filters
  watch(calendarId, (newCalendarId, oldCalendarId) => {
    if (oldCalendarId !== null && oldCalendarId !== newCalendarId) {
      console.log(`🔄 Calendar changed from ${oldCalendarId} to ${newCalendarId} (user: ${getUserId()})`)
      
      // Save current filters for the old calendar
      if (oldCalendarId) {
        const oldStorageKey = getFilterStorageKey(oldCalendarId, getUserId())
        const currentFilters = {
          selectedRecurringEvents: selectedRecurringEvents.value,
          recurringEventSearch: recurringEventSearch.value,
          showSingleEvents: showSingleEvents.value,
          showSelectedOnly: showSelectedOnly.value
          // expandedRecurringEvents now managed centrally in selectionStore
        }
        const result = saveFiltersData(oldStorageKey, currentFilters)
        if (result.success) {
          console.log(`💾 Saved filters for old calendar: ${oldCalendarId} (user: ${getUserId()})`)
        } else {
          console.warn('Failed to save filters for old calendar:', result.error)
        }
      }
      
      // Load filters for the new calendar
      loadFiltersFromLocalStorage()
    }
  })

  // Watch for when selectedRecurringEvents becomes empty and auto-turn off showSelectedOnly
  watch(selectedRecurringEvents, (newRecurringEvents) => {
    if (newRecurringEvents.length === 0 && showSelectedOnly.value) {
      showSelectedOnly.value = false
    }
  }, { deep: true })

  // Auto-save filter state changes to localStorage
  let saveTimeout = null
  const debouncedSave = () => {
    if (saveTimeout) clearTimeout(saveTimeout)
    saveTimeout = setTimeout(() => {
      saveFiltersToLocalStorage()
    }, 500) // 500ms debounce
  }

  // Watch filter state changes and auto-save
  watch(selectedRecurringEvents, debouncedSave, { deep: true })
  watch(showSingleEvents, debouncedSave)
  watch(showSelectedOnly, debouncedSave)
  // expandedRecurringEvents now managed centrally in selectionStore
  
  // Debounce search term more aggressively to avoid excessive saves
  watch(recurringEventSearch, () => {
    if (saveTimeout) clearTimeout(saveTimeout)
    saveTimeout = setTimeout(() => {
      saveFiltersToLocalStorage()
    }, 1000) // 1 second debounce for search
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

  const previewEvents = computed(() => {
    const selectedEvents = filterEventsBySelection(events.value, selectedRecurringEvents.value)
    return filterFutureEvents(selectedEvents)
  })

  const sortedPreviewEvents = computed(() => {
    const events = [...previewEvents.value]
    const multiplier = previewOrder.value === SORT_ORDERS.ASC ? 1 : -1
    
    return events.sort((a, b) => {
      // Handle both API field names (start/end) and iCal field names (dtstart/dtend)
      const startFieldA = a.start || a.dtstart
      const startFieldB = b.start || b.dtstart
      const dateA = parseIcalDate(startFieldA)
      const dateB = parseIcalDate(startFieldB)
      return (dateA - dateB) * multiplier
    })
  })

  const groupedPreviewEvents = computed(() => {
    if (previewGroup.value === PREVIEW_GROUPS.NONE) return []

    const groups = {}
    
    // First, group events and collect month date info for sorting
    previewEvents.value.forEach(event => {
      let groupKey
      let sortKey
      
      if (previewGroup.value === PREVIEW_GROUPS.EVENT_TYPE) {
        groupKey = getEventGroupKey(event)
        sortKey = groupKey
      } else if (previewGroup.value === PREVIEW_GROUPS.MONTH) {
        // Handle both API field names (start/end) and iCal field names (dtstart/dtend)
        const startField = event.start || event.dtstart
        // Use the improved parseIcalDate function instead of inline parsing
        const date = parseIcalDate(startField)
        groupKey = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
        sortKey = date.getTime() // Use timestamp for chronological sorting
      }
      
      if (!groups[groupKey]) {
        groups[groupKey] = { name: groupKey, events: [], sortKey }
      }
      groups[groupKey].events.push(event)
    })

    // Sort groups and events within groups
    const groupedArray = Object.values(groups)

    if (previewGroup.value === PREVIEW_GROUPS.EVENT_TYPE) {
      // Sort event type groups by event count (descending)
      groupedArray.sort((a, b) => b.events.length - a.events.length)
    } else if (previewGroup.value === PREVIEW_GROUPS.MONTH) {
      // Sort month groups chronologically
      groupedArray.sort((a, b) => a.sortKey - b.sortKey)
      
      // Sort events within each month group according to previewOrder
      const multiplier = previewOrder.value === SORT_ORDERS.ASC ? 1 : -1
      groupedArray.forEach(group => {
        group.events.sort((a, b) => {
          // Handle both API field names (start/end) and iCal field names (dtstart/dtend)
          const startFieldA = a.start || a.dtstart
          const startFieldB = b.start || b.dtstart
          const dateA = parseIcalDate(startFieldA)
          const dateB = parseIcalDate(startFieldB)
          return (dateA - dateB) * multiplier
        })
      })
    }

    return groupedArray
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
    const index = selectedRecurringEvents.value.indexOf(recurringEventName)
    if (index === -1) {
      selectedRecurringEvents.value.push(recurringEventName)
    } else {
      selectedRecurringEvents.value.splice(index, 1)
    }
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
    selectedRecurringEvents.value = filteredRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  }

  function clearAllRecurringEvents() {
    selectedRecurringEvents.value = []
    showPreview.value = false
  }

  function selectAllSingleEvents() {
    const singleRecurringEventNames = singleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
    singleRecurringEventNames.forEach(name => {
      if (!selectedRecurringEvents.value.includes(name)) {
        selectedRecurringEvents.value.push(name)
      }
    })
  }

  function clearAllSingleEvents() {
    const singleRecurringEventNames = singleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
    selectedRecurringEvents.value = selectedRecurringEvents.value.filter(name => !singleRecurringEventNames.includes(name))
  }


  function togglePreviewOrder() {
    previewOrder.value = previewOrder.value === SORT_ORDERS.ASC ? SORT_ORDERS.DESC : SORT_ORDERS.ASC
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

  // Load saved filter state when composable is initialized
  const initializeFilters = () => {
    loadFiltersFromLocalStorage()
  }

  // Call initialization immediately
  initializeFilters()

  return {
    // State
    selectedRecurringEvents,
    expandedRecurringEvents: selectionStore.expandedRecurringEvents,
    showSingleEvents,
    showRecurringEventsSection,
    showGroupsSection,
    showSelectedOnly,
    recurringEventSearch,
    showPreview,
    previewGroup,
    previewOrder,
    previewLimit,
    
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
    previewEvents,
    sortedPreviewEvents,
    groupedPreviewEvents,
    
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
    togglePreviewOrder,
    generateIcalFile,
    updateCalendarId,
    
    // Filter persistence functions
    saveFiltersToLocalStorage,
    loadFiltersFromLocalStorage
  }
}