/**
 * Events Store - Focused on event loading, filtering, and display
 * Uses composable for clean error handling
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAPI } from '../composables/useAPI'

export const useEventsStore = defineStore('events', () => {
  // State
  const events = ref([])
  const categories = ref({})
  const selectedEventTypes = ref(new Set())
  const keywordFilter = ref('')
  const dateRange = ref({
    start: null,
    end: null
  })
  const sortBy = ref('date')
  const sortDirection = ref('asc')

  // API composable
  const api = useAPI()

  // User authentication helpers  
  const getUserHeaders = () => {
    return {
      'x-user-id': 'anonymous' // TODO: Implement proper user management
    }
  }

  // Computed - Filtered Events
  const filteredEvents = computed(() => {
    let filtered = [...events.value]

    // Filter by selected event types
    if (selectedEventTypes.value.size > 0) {
      filtered = filtered.filter(event => 
        selectedEventTypes.value.has(event.summary)
      )
    }

    // Filter by keyword
    if (keywordFilter.value.trim()) {
      const keyword = keywordFilter.value.toLowerCase()
      filtered = filtered.filter(event => {
        const searchText = `${event.summary} ${event.description || ''} ${event.location || ''}`.toLowerCase()
        return searchText.includes(keyword)
      })
    }

    // Filter by date range
    if (dateRange.value.start || dateRange.value.end) {
      filtered = filtered.filter(event => {
        const eventDate = new Date(event.dtstart)
        if (dateRange.value.start && eventDate < dateRange.value.start) return false
        if (dateRange.value.end && eventDate > dateRange.value.end) return false
        return true
      })
    }

    // Sort events
    if (sortBy.value === 'date') {
      filtered.sort((a, b) => {
        const dateA = new Date(a.dtstart)
        const dateB = new Date(b.dtstart)
        return sortDirection.value === 'asc' ? dateA - dateB : dateB - dateA
      })
    } else if (sortBy.value === 'title') {
      filtered.sort((a, b) => {
        const titleA = a.summary.toLowerCase()
        const titleB = b.summary.toLowerCase()
        const comparison = titleA.localeCompare(titleB)
        return sortDirection.value === 'asc' ? comparison : -comparison
      })
    }

    return filtered
  })

  // Computed - Statistics
  const statistics = computed(() => {
    const totalEvents = events.value.length
    const filteredCount = filteredEvents.value.length
    const upcomingEvents = events.value.filter(event => 
      new Date(event.dtstart) > new Date()
    ).length
    
    return {
      total: totalEvents,
      filtered: filteredCount,
      upcoming: upcomingEvents,
      categories: Object.keys(categories.value).length
    }
  })

  // Actions
  const loadCalendarEvents = async (calendarId) => {
    const result = await api.safeExecute(async () => {
      const response = await axios.get(`/api/calendar/${calendarId}/events`, {
        headers: getUserHeaders()
      })
      return response.data.events
    })

    if (result.success) {
      events.value = result.data
    }

    return result
  }

  const loadCalendarCategories = async (calendarId) => {
    const result = await api.safeExecute(async () => {
      const response = await axios.get(`/api/calendar/${calendarId}/categories`, {
        headers: getUserHeaders()
      })
      return response.data.categories
    })

    if (result.success) {
      categories.value = result.data
    }

    return result
  }

  // Filter Management
  const toggleEventType = (eventType) => {
    const types = new Set(selectedEventTypes.value)
    if (types.has(eventType)) {
      types.delete(eventType)
    } else {
      types.add(eventType)
    }
    selectedEventTypes.value = types
  }

  const setKeywordFilter = (keyword) => {
    keywordFilter.value = keyword
  }

  const setDateRange = (start, end) => {
    dateRange.value = { start, end }
  }

  const setSorting = (field, direction = 'asc') => {
    sortBy.value = field
    sortDirection.value = direction
  }

  const clearAllFilters = () => {
    selectedEventTypes.value = new Set()
    keywordFilter.value = ''
    dateRange.value = { start: null, end: null }
    sortBy.value = 'date'
    sortDirection.value = 'asc'
  }

  const selectAllEventTypes = () => {
    selectedEventTypes.value = new Set(Object.keys(categories.value))
  }

  const clearEventSelection = () => {
    selectedEventTypes.value = new Set()
  }

  return {
    // State
    events,
    categories,
    selectedEventTypes,
    keywordFilter,
    dateRange,
    sortBy,
    sortDirection,

    // Computed
    filteredEvents,
    statistics,

    // Loading and error from composable
    loading: api.loading,
    error: api.error,

    // Actions
    loadCalendarEvents,
    loadCalendarCategories,
    toggleEventType,
    setKeywordFilter,
    setDateRange,
    setSorting,
    clearAllFilters,
    selectAllEventTypes,
    clearEventSelection
  }
})