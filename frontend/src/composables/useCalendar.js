import { ref, computed, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { useSelectionStore } from '../stores/selectionStore'
import { useUsername } from './useUsername'
import { FILTER_MODES, PREVIEW_GROUPS, SORT_ORDERS, EVENT_LIMITS } from '../constants/ui'

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
  const getFilterStorageKey = (calId) => {
    const userId = getUserId()
    return calId ? `icalViewer_filters_${calId}_${userId}` : `icalViewer_filters_default_${userId}`
  }

  const saveFiltersToLocalStorage = () => {
    try {
      const storageKey = getFilterStorageKey(calendarId.value)
      const filtersData = {
        selectedRecurringEvents: selectedRecurringEvents.value,
        recurringEventSearch: recurringEventSearch.value,
        showSingleEvents: showSingleEvents.value,
        showSelectedOnly: showSelectedOnly.value,
        // expandedRecurringEvents now managed centrally in selectionStore
        savedAt: new Date().toISOString()
      }
      localStorage.setItem(storageKey, JSON.stringify(filtersData))
      console.log(`💾 Filters saved for calendar: ${calendarId.value || 'default'} (user: ${getUserId()})`)
    } catch (error) {
      console.warn('Failed to save filters to localStorage:', error)
    }
  }

  const loadFiltersFromLocalStorage = () => {
    try {
      const storageKey = getFilterStorageKey(calendarId.value)
      const saved = localStorage.getItem(storageKey)
      if (saved) {
        const filtersData = JSON.parse(saved)
        
        // Validate data structure
        if (filtersData && typeof filtersData === 'object') {
          // Apply saved filters with validation
          if (Array.isArray(filtersData.selectedRecurringEvents)) {
            selectedRecurringEvents.value = filtersData.selectedRecurringEvents
          }
          if (typeof filtersData.recurringEventSearch === 'string') {
            recurringEventSearch.value = filtersData.recurringEventSearch
          }
          if (typeof filtersData.showSingleEvents === 'boolean') {
            showSingleEvents.value = filtersData.showSingleEvents
          }
          if (typeof filtersData.showSelectedOnly === 'boolean') {
            showSelectedOnly.value = filtersData.showSelectedOnly
          }
          // expandedRecurringEvents now managed centrally in selectionStore
          
          console.log(`📂 Filters loaded for calendar: ${calendarId.value || 'default'} (user: ${getUserId()})`)
          return true
        }
      }
    } catch (error) {
      console.warn('Failed to load filters from localStorage:', error)
    }
    return false
  }

  // Watch for calendar changes - save current filters and load new calendar's filters
  watch(calendarId, (newCalendarId, oldCalendarId) => {
    if (oldCalendarId !== null && oldCalendarId !== newCalendarId) {
      console.log(`🔄 Calendar changed from ${oldCalendarId} to ${newCalendarId} (user: ${getUserId()})`)
      
      // Save current filters for the old calendar
      if (oldCalendarId) {
        const oldStorageKey = getFilterStorageKey(oldCalendarId)
        const currentFilters = {
          selectedRecurringEvents: selectedRecurringEvents.value,
          recurringEventSearch: recurringEventSearch.value,
          showSingleEvents: showSingleEvents.value,
          showSelectedOnly: showSelectedOnly.value,
          // expandedRecurringEvents now managed centrally in selectionStore
          savedAt: new Date().toISOString()
        }
        try {
          localStorage.setItem(oldStorageKey, JSON.stringify(currentFilters))
          console.log(`💾 Saved filters for old calendar: ${oldCalendarId} (user: ${getUserId()})`)
        } catch (error) {
          console.warn('Failed to save filters for old calendar:', error)
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
    if (!recurringEvents.value) return []
    if (Array.isArray(recurringEvents.value)) return recurringEvents.value
    
    // Convert object to array format - recurringEvents.value now contains event types from /events endpoint
    return Object.entries(recurringEvents.value).map(([name, recurringEventData]) => {
      // recurringEventData has structure: { count: number, events: [event objects] }
      const count = recurringEventData.count || 0
      const typeEvents = recurringEventData.events || []
      
      return {
        name,
        count,
        events: typeEvents
      }
    }).sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
  })

  // Computed properties
  const filteredRecurringEvents = computed(() => {
    if (!recurringEventSearch.value.trim()) {
      return recurringEventsSortedByCount.value
    }
    
    const searchTerm = recurringEventSearch.value.toLowerCase()
    return recurringEventsSortedByCount.value.filter(recurringEvent => 
      recurringEvent.name.toLowerCase().includes(searchTerm)
    )
  })

  // Recurring events: event types that occur multiple times (count > 1)
  const mainRecurringEvents = computed(() => {
    return filteredRecurringEvents.value.filter(recurringEvent => recurringEvent.count > 1)
  })

  // Alias for backwards compatibility and clearer naming
  const recurringRecurringEvents = computed(() => mainRecurringEvents.value)

  // Unique events: event types that occur only once (count === 1)
  const singleRecurringEvents = computed(() => {
    return filteredRecurringEvents.value.filter(recurringEvent => recurringEvent.count === 1)
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
    return recurringEventsSortedByCount.value
      .filter(recurringEvent => selectedRecurringEvents.value.includes(recurringEvent.name))
      .reduce((sum, recurringEvent) => sum + recurringEvent.count, 0)
  })

  const selectedEventsCount = computed(() => {
    if (selectedRecurringEvents.value.length === 0) return 0

    const selectedRecurringEventNames = new Set(selectedRecurringEvents.value)
    return events.value.filter(event => {
      const recurringEvent = getRecurringEventKey(event)
      const isInSelectedRecurringEvent = selectedRecurringEventNames.has(recurringEvent)
      
      // With groups, we only show selected event types (simple inclusion)
      return isInSelectedRecurringEvent
    }).length
  })

  const previewEvents = computed(() => {
    if (selectedRecurringEvents.value.length === 0) return []

    const selectedRecurringEventNames = new Set(selectedRecurringEvents.value)
    const now = new Date()
    
    return events.value.filter(event => {
      const recurringEvent = getRecurringEventKey(event)
      const isInSelectedRecurringEvent = selectedRecurringEventNames.has(recurringEvent)
      
      // Check if event is in future (filter out past events)
      const eventStart = event.start || event.dtstart
      const isFutureEvent = !eventStart || new Date(eventStart) >= now
      
      // Apply both event type filter and future events filter
      // With groups, we only show selected event types (simple inclusion)
      const passesRecurringEventFilter = isInSelectedRecurringEvent
        
      return passesRecurringEventFilter && isFutureEvent
    })
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
    const stats = {
      totalRecurringEvents: recurringEventsSortedByCount.value.length,
      recurringRecurringEvents: recurringRecurringEvents.value.length,
      uniqueRecurringEvents: uniqueRecurringEvents.value.length,
      totalEvents: recurringEventsSortedByCount.value.reduce((sum, recurringEvent) => sum + recurringEvent.count, 0),
      recurringEvents: recurringRecurringEvents.value.reduce((sum, recurringEvent) => sum + recurringEvent.count, 0),
      uniqueEvents: uniqueRecurringEvents.value.length // Each unique type has exactly 1 event
    }
    return stats
  })

  // Event type classification helper
  function classifyRecurringEvent(recurringEventName) {
    const recurringEvent = recurringEventsSortedByCount.value.find(et => et.name === recurringEventName)
    if (!recurringEvent) return 'unknown'
    
    return recurringEvent.count === 1 ? 'unique' : 'recurring'
  }

  // Methods
  function getRecurringEventKey(event) {
    // Get the key used for filtering events (by title - what users select)
    return event.title || event.summary || 'Untitled Event'
  }

  function getEventGroupKey(event) {
    // Get the key used for grouping events by type in preview
    // Use event title for proper grouping (same as filtering key)
    return event.title || event.summary || 'Unknown Event Type'
  }

  function parseIcalDate(dateString) {
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

  function formatDateTime(dateString) {
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

  function formatDateRange(event) {
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
    classifyRecurringEvent,
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