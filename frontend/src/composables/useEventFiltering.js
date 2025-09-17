/**
 * Event Filtering Composable
 * Pure functions for event filtering, sorting, and statistics
 * Extracted from the complex computed property in events store
 */
import { computed } from 'vue'

export function useEventFiltering(events, filters) {
  /**
   * Filter events by selected types/categories
   */
  const filterByTypes = (eventList, selectedTypes) => {
    if (!selectedTypes || selectedTypes.size === 0) return eventList
    return eventList.filter(event => selectedTypes.has(event.summary))
  }

  /**
   * Filter events by keyword search
   */
  const filterByKeyword = (eventList, keyword) => {
    if (!keyword || !keyword.trim()) return eventList
    
    const searchTerm = keyword.toLowerCase()
    return eventList.filter(event => {
      const searchText = `${event.summary} ${event.description || ''} ${event.location || ''}`.toLowerCase()
      return searchText.includes(searchTerm)
    })
  }

  /**
   * Filter events by date range
   */
  const filterByDateRange = (eventList, dateRange) => {
    if (!dateRange || (!dateRange.start && !dateRange.end)) return eventList
    
    return eventList.filter(event => {
      // Handle both API field names (start/end) and iCal field names (dtstart/dtend)
      const startField = event.start || event.dtstart
      const eventDate = new Date(startField)
      if (dateRange.start && eventDate < dateRange.start) return false
      if (dateRange.end && eventDate > dateRange.end) return false
      return true
    })
  }

  /**
   * Sort events by specified criteria
   */
  const sortEvents = (eventList, sortBy, sortDirection = 'asc') => {
    const sorted = [...eventList]
    
    if (sortBy === 'date') {
      sorted.sort((a, b) => {
        // Handle both API field names (start/end) and iCal field names (dtstart/dtend)
        const startFieldA = a.start || a.dtstart
        const startFieldB = b.start || b.dtstart
        const dateA = new Date(startFieldA)
        const dateB = new Date(startFieldB)
        return sortDirection === 'asc' ? dateA - dateB : dateB - dateA
      })
    } else if (sortBy === 'title') {
      sorted.sort((a, b) => {
        const titleA = a.summary.toLowerCase()
        const titleB = b.summary.toLowerCase()
        const comparison = titleA.localeCompare(titleB)
        return sortDirection === 'asc' ? comparison : -comparison
      })
    }
    
    return sorted
  }

  /**
   * Apply all filters and sorting in sequence
   */
  const filteredEvents = computed(() => {
    if (!events.value || events.value.length === 0) return []
    
    let result = [...events.value]
    
    // Apply filters in sequence
    result = filterByTypes(result, filters.selectedEventTypes)
    result = filterByKeyword(result, filters.keywordFilter)
    result = filterByDateRange(result, filters.dateRange)
    
    // Apply sorting
    result = sortEvents(result, filters.sortBy, filters.sortDirection)
    
    return result
  })

  /**
   * Generate statistics about events
   */
  const statistics = computed(() => {
    const totalEvents = events.value?.length || 0
    const filteredCount = filteredEvents.value?.length || 0
    const upcomingEvents = events.value?.filter(event => {
      // Handle both API field names (start/end) and iCal field names (dtstart/dtend)
      const startField = event.start || event.dtstart
      return new Date(startField) > new Date()
    }).length || 0
    
    return {
      total: totalEvents,
      filtered: filteredCount,
      upcoming: upcomingEvents,
      categories: filters.categories ? Object.keys(filters.categories).length : 0
    }
  })

  /**
   * Helper function to create filter configuration objects
   */
  const createFilterConfig = (filters) => {
    return {
      selectedEventTypes: Array.from(filters.selectedEventTypes || []),
      keywordFilter: filters.keywordFilter || '',
      dateRange: filters.dateRange || { start: null, end: null },
      sortBy: filters.sortBy || 'date',
      sortDirection: filters.sortDirection || 'asc'
    }
  }

  /**
   * Helper function to apply filter configuration to filters object
   */
  const applyFilterConfig = (config, filtersRef) => {
    filtersRef.selectedEventTypes = new Set(config.selectedEventTypes || [])
    filtersRef.keywordFilter = config.keywordFilter || ''
    filtersRef.dateRange = config.dateRange || { start: null, end: null }
    filtersRef.sortBy = config.sortBy || 'date'
    filtersRef.sortDirection = config.sortDirection || 'asc'
  }

  return {
    // Pure filtering functions
    filterByTypes,
    filterByKeyword,
    filterByDateRange,
    sortEvents,
    
    // Computed results
    filteredEvents,
    statistics,
    
    // Helper functions
    createFilterConfig,
    applyFilterConfig
  }
}