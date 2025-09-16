import { ref, computed, watch } from 'vue'
import { useCompatibilityStore as useAppStore } from '../stores/compatibility'
import { FILTER_MODES, PREVIEW_GROUPS, SORT_ORDERS, EVENT_LIMITS } from '../constants/ui'
import { useUserPreferences } from './useUserPreferences'

export function useCalendar(eventsData = null, categoriesData = null, calendarId = null) {
  const appStore = useAppStore()
  const { saveCalendarFilterState, loadCalendarFilterState } = useUserPreferences()
  
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
  
  // Track if preferences have been loaded
  const preferencesLoaded = ref(false)

  // Watch for when selectedCategories becomes empty and auto-turn off showSelectedOnly
  watch(selectedCategories, (newCategories) => {
    if (newCategories.length === 0 && showSelectedOnly.value) {
      showSelectedOnly.value = false
    }
  }, { deep: true })

  // Convert categories object to sorted array with events
  const categoriesSortedByCount = computed(() => {
    if (!categories.value) return []
    if (Array.isArray(categories.value)) return categories.value
    
    // Convert object to array format and attach events to each category
    return Object.entries(categories.value).map(([name, count]) => {
      // Find events for this category
      const categoryEvents = events.value.filter(event => {
        const eventCategory = getCategoryForEvent(event)
        return eventCategory === name
      })
      
      return {
        name,
        count,
        events: categoryEvents
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

  const mainCategories = computed(() => {
    return filteredCategories.value.filter(category => category.count > 1)
  })

  const singleEventCategories = computed(() => {
    return filteredCategories.value.filter(category => category.count === 1)
  })

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
      const dateA = new Date(a.dtstart)
      const dateB = new Date(b.dtstart)
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
        // Handle iCal date format properly
        let date
        if (typeof event.dtstart === 'string') {
          if (event.dtstart.match(/^\d{8}T\d{6}Z?$/)) {
            // Format: 20231215T140000Z
            const year = event.dtstart.substring(0, 4)
            const month = event.dtstart.substring(4, 6)
            const day = event.dtstart.substring(6, 8)
            date = new Date(`${year}-${month}-${day}`)
          } else if (event.dtstart.match(/^\d{8}$/)) {
            // Format: 20231215 (date only)
            const year = event.dtstart.substring(0, 4)
            const month = event.dtstart.substring(4, 6)
            const day = event.dtstart.substring(6, 8)
            date = new Date(`${year}-${month}-${day}`)
          } else {
            date = new Date(event.dtstart)
          }
        } else {
          date = new Date(event.dtstart)
        }
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
          const dateA = new Date(a.dtstart)
          const dateB = new Date(b.dtstart)
          return (dateA - dateB) * multiplier
        })
      })
    }

    return groupedArray
  })

  // Methods
  function getCategoryForEvent(event) {
    return event.categories?.[0] || event.summary || 'Uncategorized'
  }

  function parseIcalDate(dateString) {
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

  // Persistence functions for filter state
  const loadFilterState = async () => {
    if (!calendarId) return
    
    try {
      const savedState = await loadCalendarFilterState(calendarId)
      
      // Apply saved state to reactive refs
      selectedCategories.value = savedState.selectedCategories || []
      expandedCategories.value = savedState.expandedCategories || []
      showSingleEvents.value = savedState.showSingleEvents || false
      showCategoriesSection.value = savedState.showCategoriesSection !== undefined ? savedState.showCategoriesSection : true
      showSelectedOnly.value = savedState.showSelectedOnly || false
      categorySearch.value = savedState.categorySearch || ''
      filterMode.value = savedState.filterMode || FILTER_MODES.INCLUDE
      previewGroup.value = savedState.previewGroup || PREVIEW_GROUPS.NONE
      
      preferencesLoaded.value = true
      console.log('Loaded filter state for calendar:', calendarId, savedState)
    } catch (error) {
      console.error('Failed to load filter state:', error)
      preferencesLoaded.value = true // Still mark as loaded to prevent infinite attempts
    }
  }

  const saveFilterState = async () => {
    if (!calendarId || !preferencesLoaded.value) return
    
    const currentState = {
      selectedCategories: selectedCategories.value,
      expandedCategories: expandedCategories.value,
      showSingleEvents: showSingleEvents.value,
      showCategoriesSection: showCategoriesSection.value,
      showSelectedOnly: showSelectedOnly.value,
      categorySearch: categorySearch.value,
      filterMode: filterMode.value,
      previewGroup: previewGroup.value
    }
    
    try {
      await saveCalendarFilterState(calendarId, currentState)
      console.log('Saved filter state for calendar:', calendarId, currentState)
    } catch (error) {
      console.error('Failed to save filter state:', error)
    }
  }

  // Auto-save filter state when it changes (debounced to avoid excessive API calls)
  let saveTimeout
  const debouncedSave = () => {
    clearTimeout(saveTimeout)
    saveTimeout = setTimeout(saveFilterState, 1000) // Save after 1 second of inactivity
  }

  // Watch for changes and auto-save
  watch([selectedCategories, expandedCategories, showSingleEvents, showCategoriesSection, 
         showSelectedOnly, categorySearch, filterMode, previewGroup], 
         debouncedSave, { deep: true })

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
    preferencesLoaded,
    
    // Computed
    categoriesSortedByCount,
    filteredCategories,
    mainCategories,
    singleEventCategories,
    unifiedCategories,
    selectedCategoriesCount,
    selectedEventsCount,
    previewEvents,
    sortedPreviewEvents,
    groupedPreviewEvents,
    
    // Methods
    getCategoryForEvent,
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
    generateIcalFile,
    loadFilterState,
    saveFilterState
  }
}