import { ref, computed, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { FILTER_MODES, PREVIEW_GROUPS, SORT_ORDERS, EVENT_LIMITS } from '../constants/ui'

export function useCalendar(eventsData = null, categoriesData = null, calendarId = null) {
  const appStore = useAppStore()
  
  // Use provided data or fall back to store
  const events = eventsData || computed(() => appStore.events)
  const categories = categoriesData || computed(() => appStore.categories)
  
  // Reactive state - these will be loaded from backend preferences
  const selectedCategories = ref([])
  const expandedCategories = ref([])
  const showSingleEvents = ref(false)
  const showCategoriesSection = ref(true)
  const showSelectedOnly = ref(false)
  const categorySearch = ref('')
  const filterMode = ref(FILTER_MODES.INCLUDE)
  const showPreview = ref(false)
  const previewGroup = ref(PREVIEW_GROUPS.NONE)
  const previewOrder = ref(SORT_ORDERS.ASC)
  const previewLimit = ref(EVENT_LIMITS.PREVIEW_DEFAULT)
  
  // No preferences loading needed - using default state only

  // Watch for when selectedCategories becomes empty and auto-turn off showSelectedOnly
  watch(selectedCategories, (newCategories) => {
    if (newCategories.length === 0 && showSelectedOnly.value) {
      showSelectedOnly.value = false
    }
  }, { deep: true })

  // Convert event types object to sorted array with events
  const categoriesSortedByCount = computed(() => {
    if (!categories.value) return []
    if (Array.isArray(categories.value)) return categories.value
    
    // Convert object to array format - categories.value now contains event types from /events endpoint
    return Object.entries(categories.value).map(([name, eventTypeData]) => {
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
  const filteredCategories = computed(() => {
    if (!categorySearch.value.trim()) {
      return categoriesSortedByCount.value
    }
    
    const searchTerm = categorySearch.value.toLowerCase()
    return categoriesSortedByCount.value.filter(category => 
      category.name.toLowerCase().includes(searchTerm)
    )
  })

  // Recurring events: event types that occur multiple times (count > 1)
  const mainCategories = computed(() => {
    return filteredCategories.value.filter(category => category.count > 1)
  })

  // Alias for backwards compatibility and clearer naming
  const recurringEventTypes = computed(() => mainCategories.value)

  // Unique events: event types that occur only once (count === 1)
  const singleEventCategories = computed(() => {
    return filteredCategories.value.filter(category => category.count === 1)
  })

  // Alias for more accurate naming
  const uniqueEventTypes = computed(() => singleEventCategories.value)

  const unifiedCategories = computed(() => {
    // Combine and sort all categories by count (highest first), then alphabetically
    return filteredCategories.value.sort((a, b) => {
      if (a.count !== b.count) {
        return b.count - a.count // Higher count first
      }
      return a.name.localeCompare(b.name) // Alphabetical if same count
    })
  })

  const selectedCategoriesCount = computed(() => {
    return categoriesSortedByCount.value
      .filter(cat => selectedCategories.value.includes(cat.name))
      .reduce((sum, cat) => sum + cat.count, 0)
  })

  const selectedEventsCount = computed(() => {
    if (selectedCategories.value.length === 0) return 0

    const selectedCategoryNames = new Set(selectedCategories.value)
    return events.value.filter(event => {
      const eventCategory = getCategoryForEvent(event)
      const isInSelectedCategory = selectedCategoryNames.has(eventCategory)
      
      return filterMode.value === FILTER_MODES.INCLUDE 
        ? isInSelectedCategory 
        : !isInSelectedCategory
    }).length
  })

  const previewEvents = computed(() => {
    if (selectedCategories.value.length === 0) return []

    const selectedCategoryNames = new Set(selectedCategories.value)
    return events.value.filter(event => {
      const eventCategory = getCategoryForEvent(event)
      const isInSelectedCategory = selectedCategoryNames.has(eventCategory)
      
      return filterMode.value === FILTER_MODES.INCLUDE 
        ? isInSelectedCategory 
        : !isInSelectedCategory
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
      
      if (previewGroup.value === PREVIEW_GROUPS.CATEGORY) {
        groupKey = getCategoryForEvent(event)
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

    if (previewGroup.value === PREVIEW_GROUPS.CATEGORY) {
      // Sort category groups by event count (descending)
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
      totalEventTypes: categoriesSortedByCount.value.length,
      recurringEventTypes: recurringEventTypes.value.length,
      uniqueEventTypes: uniqueEventTypes.value.length,
      totalEvents: categoriesSortedByCount.value.reduce((sum, cat) => sum + cat.count, 0),
      recurringEvents: recurringEventTypes.value.reduce((sum, cat) => sum + cat.count, 0),
      uniqueEvents: uniqueEventTypes.value.length // Each unique type has exactly 1 event
    }
    return stats
  })

  // Event type classification helper
  function classifyEventType(eventTypeName) {
    const eventType = categoriesSortedByCount.value.find(cat => cat.name === eventTypeName)
    if (!eventType) return 'unknown'
    
    return eventType.count === 1 ? 'unique' : 'recurring'
  }

  // Methods
  function getCategoryForEvent(event) {
    // In the new system, the "category" is the event title (for event type grouping)
    return event.title || event.summary || 'Untitled Event'
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

  function toggleCategory(categoryName) {
    const index = selectedCategories.value.indexOf(categoryName)
    if (index === -1) {
      selectedCategories.value.push(categoryName)
    } else {
      selectedCategories.value.splice(index, 1)
    }
  }

  function toggleCategoryExpansion(categoryName) {
    const index = expandedCategories.value.indexOf(categoryName)
    if (index === -1) {
      expandedCategories.value.push(categoryName)
    } else {
      expandedCategories.value.splice(index, 1)
    }
  }

  function selectAllCategories() {
    selectedCategories.value = filteredCategories.value.map(cat => cat.name)
  }

  function clearAllCategories() {
    selectedCategories.value = []
    showPreview.value = false
  }

  function selectAllSingleEvents() {
    const singleEventNames = singleEventCategories.value.map(cat => cat.name)
    singleEventNames.forEach(name => {
      if (!selectedCategories.value.includes(name)) {
        selectedCategories.value.push(name)
      }
    })
  }

  function clearAllSingleEvents() {
    const singleEventNames = singleEventCategories.value.map(cat => cat.name)
    selectedCategories.value = selectedCategories.value.filter(name => !singleEventNames.includes(name))
  }

  function switchFilterMode(newMode) {
    if (filterMode.value !== newMode) {
      // Just switch the mode, keep the same categories selected
      filterMode.value = newMode
      previewLimit.value = EVENT_LIMITS.PREVIEW_DEFAULT
    }
  }

  function togglePreviewOrder() {
    previewOrder.value = previewOrder.value === SORT_ORDERS.ASC ? SORT_ORDERS.DESC : SORT_ORDERS.ASC
  }

  async function generateIcalFile() {
    try {
      const result = await appStore.generateIcal({
        calendarId: appStore.selectedCalendar.id,
        selectedCategories: selectedCategories.value,
        filterMode: filterMode.value
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

  // No persistence functions needed - using default state only

  return {
    // State
    selectedCategories,
    expandedCategories,
    showSingleEvents,
    showCategoriesSection,
    showSelectedOnly,
    categorySearch,
    filterMode,
    showPreview,
    previewGroup,
    previewOrder,
    previewLimit,
    
    // Computed
    categoriesSortedByCount,
    filteredCategories,
    mainCategories,
    singleEventCategories,
    recurringEventTypes,
    uniqueEventTypes,
    unifiedCategories,
    eventTypeStats,
    selectedCategoriesCount,
    selectedEventsCount,
    previewEvents,
    sortedPreviewEvents,
    groupedPreviewEvents,
    
    // Methods
    getCategoryForEvent,
    classifyEventType,
    formatDateTime,
    formatDateRange,
    toggleCategory,
    toggleCategoryExpansion,
    selectAllCategories,
    clearAllCategories,
    selectAllSingleEvents,
    clearAllSingleEvents,
    switchFilterMode,
    togglePreviewOrder,
    generateIcalFile
  }
}