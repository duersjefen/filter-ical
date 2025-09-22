import { ref, computed, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { useUsername } from './useUsername'
import { FILTER_MODES, PREVIEW_GROUPS, SORT_ORDERS, EVENT_LIMITS } from '../constants/ui'

export function useCalendar(eventsData = null, eventTypesData = null, initialCalendarId = null) {
  const appStore = useAppStore()
  const { getUserId } = useUsername()
  
  // Use provided data or fall back to store
  const events = eventsData || computed(() => appStore.events)
  const eventTypes = eventTypesData || computed(() => appStore.eventTypes)
  
  // Make calendar ID reactive to handle navigation between calendars
  const calendarId = ref(initialCalendarId)
  
  // Reactive state - these will be loaded from backend preferences
  const selectedEventTypes = ref([])
  const expandedEventTypes = ref([])
  const showSingleEvents = ref(false)
  const showEventTypesSection = ref(true)
  const showGroupsSection = ref(true)
  const showSelectedOnly = ref(false)
  const eventTypeSearch = ref('')
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
        selectedEventTypes: selectedEventTypes.value,
        eventTypeSearch: eventTypeSearch.value,
        showSingleEvents: showSingleEvents.value,
        showSelectedOnly: showSelectedOnly.value,
        expandedEventTypes: expandedEventTypes.value,
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
          if (Array.isArray(filtersData.selectedEventTypes)) {
            selectedEventTypes.value = filtersData.selectedEventTypes
          }
          if (typeof filtersData.eventTypeSearch === 'string') {
            eventTypeSearch.value = filtersData.eventTypeSearch
          }
          if (typeof filtersData.showSingleEvents === 'boolean') {
            showSingleEvents.value = filtersData.showSingleEvents
          }
          if (typeof filtersData.showSelectedOnly === 'boolean') {
            showSelectedOnly.value = filtersData.showSelectedOnly
          }
          if (Array.isArray(filtersData.expandedEventTypes)) {
            expandedEventTypes.value = filtersData.expandedEventTypes
          }
          
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
          selectedEventTypes: selectedEventTypes.value,
          eventTypeSearch: eventTypeSearch.value,
          showSingleEvents: showSingleEvents.value,
          showSelectedOnly: showSelectedOnly.value,
          expandedEventTypes: expandedEventTypes.value,
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

  // Watch for when selectedEventTypes becomes empty and auto-turn off showSelectedOnly
  watch(selectedEventTypes, (newEventTypes) => {
    if (newEventTypes.length === 0 && showSelectedOnly.value) {
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
  watch(selectedEventTypes, debouncedSave, { deep: true })
  watch(showSingleEvents, debouncedSave)
  watch(showSelectedOnly, debouncedSave)
  watch(expandedEventTypes, debouncedSave, { deep: true })
  
  // Debounce search term more aggressively to avoid excessive saves
  watch(eventTypeSearch, () => {
    if (saveTimeout) clearTimeout(saveTimeout)
    saveTimeout = setTimeout(() => {
      saveFiltersToLocalStorage()
    }, 1000) // 1 second debounce for search
  })

  // Convert event types object to sorted array with events
  const eventTypesSortedByCount = computed(() => {
    if (!eventTypes.value) return []
    if (Array.isArray(eventTypes.value)) return eventTypes.value
    
    // Convert object to array format - eventTypes.value now contains event types from /events endpoint
    return Object.entries(eventTypes.value).map(([name, eventTypeData]) => {
      // eventTypeData has structure: { count: number, events: [event objects] }
      const count = eventTypeData.count || 0
      const typeEvents = eventTypeData.events || []
      
      return {
        name,
        count,
        events: typeEvents
      }
    }).sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
  })

  // Computed properties
  const filteredEventTypes = computed(() => {
    if (!eventTypeSearch.value.trim()) {
      return eventTypesSortedByCount.value
    }
    
    const searchTerm = eventTypeSearch.value.toLowerCase()
    return eventTypesSortedByCount.value.filter(eventType => 
      eventType.name.toLowerCase().includes(searchTerm)
    )
  })

  // Recurring events: event types that occur multiple times (count > 1)
  const mainEventTypes = computed(() => {
    return filteredEventTypes.value.filter(eventType => eventType.count > 1)
  })

  // Alias for backwards compatibility and clearer naming
  const recurringEventTypes = computed(() => mainEventTypes.value)

  // Unique events: event types that occur only once (count === 1)
  const singleEventTypes = computed(() => {
    return filteredEventTypes.value.filter(eventType => eventType.count === 1)
  })

  // Alias for more accurate naming
  const uniqueEventTypes = computed(() => singleEventTypes.value)

  const unifiedEventTypes = computed(() => {
    // Combine and sort all event types by count (highest first), then alphabetically
    return filteredEventTypes.value.sort((a, b) => {
      if (a.count !== b.count) {
        return b.count - a.count // Higher count first
      }
      return a.name.localeCompare(b.name) // Alphabetical if same count
    })
  })

  const selectedEventTypesCount = computed(() => {
    return eventTypesSortedByCount.value
      .filter(eventType => selectedEventTypes.value.includes(eventType.name))
      .reduce((sum, eventType) => sum + eventType.count, 0)
  })

  const selectedEventsCount = computed(() => {
    if (selectedEventTypes.value.length === 0) return 0

    const selectedEventTypeNames = new Set(selectedEventTypes.value)
    return events.value.filter(event => {
      const eventType = getEventTypeKey(event)
      const isInSelectedEventType = selectedEventTypeNames.has(eventType)
      
      // With groups, we only show selected event types (simple inclusion)
      return isInSelectedEventType
    }).length
  })

  const previewEvents = computed(() => {
    if (selectedEventTypes.value.length === 0) return []

    const selectedEventTypeNames = new Set(selectedEventTypes.value)
    const now = new Date()
    
    return events.value.filter(event => {
      const eventType = getEventTypeKey(event)
      const isInSelectedEventType = selectedEventTypeNames.has(eventType)
      
      // Check if event is in future (filter out past events)
      const eventStart = event.start || event.dtstart
      const isFutureEvent = !eventStart || new Date(eventStart) >= now
      
      // Apply both event type filter and future events filter
      // With groups, we only show selected event types (simple inclusion)
      const passesEventTypeFilter = isInSelectedEventType
        
      return passesEventTypeFilter && isFutureEvent
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
  const eventTypeStats = computed(() => {
    const stats = {
      totalEventTypes: eventTypesSortedByCount.value.length,
      recurringEventTypes: recurringEventTypes.value.length,
      uniqueEventTypes: uniqueEventTypes.value.length,
      totalEvents: eventTypesSortedByCount.value.reduce((sum, eventType) => sum + eventType.count, 0),
      recurringEvents: recurringEventTypes.value.reduce((sum, eventType) => sum + eventType.count, 0),
      uniqueEvents: uniqueEventTypes.value.length // Each unique type has exactly 1 event
    }
    return stats
  })

  // Event type classification helper
  function classifyEventType(eventTypeName) {
    const eventType = eventTypesSortedByCount.value.find(et => et.name === eventTypeName)
    if (!eventType) return 'unknown'
    
    return eventType.count === 1 ? 'unique' : 'recurring'
  }

  // Methods
  function getEventTypeKey(event) {
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

  function toggleEventType(eventTypeName) {
    const index = selectedEventTypes.value.indexOf(eventTypeName)
    if (index === -1) {
      selectedEventTypes.value.push(eventTypeName)
    } else {
      selectedEventTypes.value.splice(index, 1)
    }
  }

  function toggleEventTypeExpansion(eventTypeName) {
    const index = expandedEventTypes.value.indexOf(eventTypeName)
    if (index === -1) {
      expandedEventTypes.value.push(eventTypeName)
    } else {
      expandedEventTypes.value.splice(index, 1)
    }
  }

  function selectAllEventTypes() {
    selectedEventTypes.value = filteredEventTypes.value.map(eventType => eventType.name)
  }

  function clearAllEventTypes() {
    selectedEventTypes.value = []
    showPreview.value = false
  }

  function selectAllSingleEvents() {
    const singleEventNames = singleEventTypes.value.map(eventType => eventType.name)
    singleEventNames.forEach(name => {
      if (!selectedEventTypes.value.includes(name)) {
        selectedEventTypes.value.push(name)
      }
    })
  }

  function clearAllSingleEvents() {
    const singleEventNames = singleEventTypes.value.map(eventType => eventType.name)
    selectedEventTypes.value = selectedEventTypes.value.filter(name => !singleEventNames.includes(name))
  }


  function togglePreviewOrder() {
    previewOrder.value = previewOrder.value === SORT_ORDERS.ASC ? SORT_ORDERS.DESC : SORT_ORDERS.ASC
  }

  async function generateIcalFile() {
    try {
      const result = await appStore.generateIcal({
        calendarId: appStore.selectedCalendar.id,
        selectedEventTypes: selectedEventTypes.value
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
    selectedEventTypes,
    expandedEventTypes,
    showSingleEvents,
    showEventTypesSection,
    showGroupsSection,
    showSelectedOnly,
    eventTypeSearch,
    showPreview,
    previewGroup,
    previewOrder,
    previewLimit,
    
    // Computed
    eventTypesSortedByCount,
    filteredEventTypes,
    mainEventTypes,
    singleEventTypes,
    recurringEventTypes,
    uniqueEventTypes,
    unifiedEventTypes,
    eventTypeStats,
    selectedEventTypesCount,
    selectedEventsCount,
    previewEvents,
    sortedPreviewEvents,
    groupedPreviewEvents,
    
    // Methods
    getEventTypeKey,
    getEventGroupKey,
    classifyEventType,
    formatDateTime,
    formatDateRange,
    toggleEventType,
    toggleEventTypeExpansion,
    selectAllEventTypes,
    clearAllEventTypes,
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