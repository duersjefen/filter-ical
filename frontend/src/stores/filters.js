/**
 * Filters Store - Focused on saved filter management
 * Uses composable for clean error handling
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { useAPI } from '../composables/useAPI'

export const useFiltersStore = defineStore('filters', () => {
  // State
  const savedFilters = ref([])

  // API composable
  const api = useAPI()

  // User authentication helpers - removed anonymous fallback
  // This store should not be used independently - only through compatibility store
  const getUserHeaders = () => {
    throw new Error('Filters store should not be used directly - use compatibility store with proper user context')
  }

  // Actions
  const fetchFilters = async () => {
    const result = await api.safeExecute(async () => {
      const response = await axios.get('/api/filters', {
        headers: getUserHeaders()
      })
      return response.data.filters
    })

    if (result.success) {
      savedFilters.value = result.data
    }

    return result
  }

  const saveFilter = async (name, config) => {
    const filterName = name || `Filter ${config.selectedEventTypes?.length || 0} types`
    
    const result = await api.safeExecute(async () => {
      const response = await axios.post('/api/filters', {
        name: filterName,
        config: config
      }, {
        headers: getUserHeaders()
      })
      return response.data
    })

    if (result.success) {
      // Refresh filters list
      await fetchFilters()
    }

    return result
  }

  const deleteFilter = async (filterId) => {
    const result = await api.safeExecute(async () => {
      await axios.delete(`/api/filters/${filterId}`, {
        headers: getUserHeaders()
      })
    })

    if (result.success) {
      // Refresh filters list
      await fetchFilters()
    }

    return result
  }

  const createFilterConfig = (eventsStore) => {
    return {
      selectedEventTypes: Array.from(eventsStore.selectedEventTypes),
      keywordFilter: eventsStore.keywordFilter,
      dateRange: eventsStore.dateRange,
      sortBy: eventsStore.sortBy,
      sortDirection: eventsStore.sortDirection
    }
  }

  const applyFilter = (filter, eventsStore) => {
    const config = filter.config
    
    // Apply the filter configuration to the events store
    eventsStore.selectedEventTypes = new Set(config.selectedEventTypes || [])
    eventsStore.keywordFilter = config.keywordFilter || ''
    eventsStore.dateRange = config.dateRange || { start: null, end: null }
    eventsStore.sortBy = config.sortBy || 'date'
    eventsStore.sortDirection = config.sortDirection || 'asc'
  }

  return {
    // State
    savedFilters,

    // Loading and error from composable
    loading: api.loading,
    error: api.error,

    // Actions
    fetchFilters,
    saveFilter,
    deleteFilter,
    createFilterConfig,
    applyFilter
  }
})