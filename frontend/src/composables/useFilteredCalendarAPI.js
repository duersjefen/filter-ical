/**
 * Composable for Filtered Calendar API operations
 * Following functional programming principles with pure functions
 */

import { ref, reactive } from 'vue'
import { useAPI } from './useAPI'

export function useFilteredCalendarAPI() {
  // State
  const filteredCalendars = ref([])
  const loading = ref(false)
  const creating = ref(false)
  const updating = ref(false)
  const error = ref(null)

  // Get API instance
  const { api } = useAPI()

  /**
   * Pure function: Create filtered calendar data payload
   */
  const createFilteredCalendarPayload = (sourceCalendarId, name, filterConfig) => {
    return {
      source_calendar_id: sourceCalendarId,
      name: name.trim(),
      filter_config: {
        include_categories: filterConfig.include_categories || [],
        exclude_categories: filterConfig.exclude_categories || [],
        include_keywords: filterConfig.include_keywords || [],
        exclude_keywords: filterConfig.exclude_keywords || [],
        filter_mode: filterConfig.filter_mode || 'include',
        match_all: filterConfig.match_all || false,
        date_range_start: filterConfig.date_range_start || null,
        date_range_end: filterConfig.date_range_end || null,
        date_range_type: filterConfig.date_range_type || 'absolute'
      }
    }
  }

  /**
   * Pure function: Transform API response to filtered calendar
   */
  const transformFilteredCalendar = (apiResponse) => {
    return {
      id: apiResponse.id,
      name: apiResponse.name,
      public_token: apiResponse.public_token,
      calendar_url: apiResponse.calendar_url,
      preview_url: apiResponse.preview_url,
      source_calendar_id: apiResponse.source_calendar_id,
      filter_config: apiResponse.filter_config,
      created_at: apiResponse.created_at,
      updated_at: apiResponse.updated_at || apiResponse.created_at
    }
  }

  /**
   * Pure function: Update filtered calendar in list
   */
  const updateFilteredCalendarInList = (calendars, updatedCalendar) => {
    return calendars.map(cal => 
      cal.id === updatedCalendar.id ? updatedCalendar : cal
    )
  }

  /**
   * Pure function: Remove filtered calendar from list
   */
  const removeFilteredCalendarFromList = (calendars, calendarId) => {
    return calendars.filter(cal => cal.id !== calendarId)
  }

  /**
   * API Operations (Imperative Shell)
   */

  const loadFilteredCalendars = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/api/filtered-calendars')
      
      if (response.data && response.data.filtered_calendars) {
        filteredCalendars.value = response.data.filtered_calendars.map(transformFilteredCalendar)
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load filtered calendars'
      console.error('Error loading filtered calendars:', err)
    } finally {
      loading.value = false
    }
  }

  const createFilteredCalendar = async (sourceCalendarId, name, filterConfig) => {
    if (!name?.trim()) {
      error.value = 'Name is required'
      return false
    }

    creating.value = true
    error.value = null

    try {
      const payload = createFilteredCalendarPayload(sourceCalendarId, name, filterConfig)
      const response = await api.post('/api/filtered-calendars', payload)
      
      if (response.data) {
        const newCalendar = transformFilteredCalendar(response.data)
        filteredCalendars.value.push(newCalendar)
        return true
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create filtered calendar'
      console.error('Error creating filtered calendar:', err)
      return false
    } finally {
      creating.value = false
    }
  }

  const updateFilteredCalendar = async (calendarId, updates) => {
    if (!calendarId) {
      error.value = 'Calendar ID is required'
      return false
    }

    updating.value = true
    error.value = null

    try {
      const payload = {
        name: updates.name?.trim(),
        filter_config: updates.filter_config
      }

      // Remove undefined values
      Object.keys(payload).forEach(key => {
        if (payload[key] === undefined) {
          delete payload[key]
        }
      })

      const response = await api.put(`/api/filtered-calendars/${calendarId}`, payload)
      
      if (response.data) {
        const updatedCalendar = transformFilteredCalendar(response.data)
        filteredCalendars.value = updateFilteredCalendarInList(
          filteredCalendars.value, 
          updatedCalendar
        )
        return true
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update filtered calendar'
      console.error('Error updating filtered calendar:', err)
      return false
    } finally {
      updating.value = false
    }
  }

  const deleteFilteredCalendar = async (calendarId) => {
    if (!calendarId) {
      error.value = 'Calendar ID is required'
      return false
    }

    loading.value = true
    error.value = null

    try {
      await api.delete(`/api/filtered-calendars/${calendarId}`)
      
      filteredCalendars.value = removeFilteredCalendarFromList(
        filteredCalendars.value, 
        calendarId
      )
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete filtered calendar'
      console.error('Error deleting filtered calendar:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const getPublicCalendar = async (token) => {
    try {
      const response = await api.get(`/cal/${token}`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load public calendar'
      console.error('Error loading public calendar:', err)
      return null
    }
  }

  const downloadFilteredCalendar = async (token) => {
    try {
      const response = await api.get(`/cal/${token}.ics`, {
        responseType: 'blob'
      })
      
      // Create download link
      const blob = new Blob([response.data], { type: 'text/calendar' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `filtered-calendar-${token}.ics`
      document.body.appendChild(link)
      link.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(link)
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to download calendar'
      console.error('Error downloading calendar:', err)
      return false
    }
  }

  /**
   * Pure helper functions for validation
   */
  const validateFilterConfig = (filterConfig) => {
    const errors = []
    
    if (!filterConfig) {
      errors.push('Filter configuration is required')
      return { isValid: false, errors }
    }

    if (!filterConfig.filter_mode || !['include', 'exclude'].includes(filterConfig.filter_mode)) {
      errors.push('Valid filter mode (include/exclude) is required')
    }

    const hasIncludeCategories = filterConfig.include_categories?.length > 0
    const hasExcludeCategories = filterConfig.exclude_categories?.length > 0
    const hasKeywords = filterConfig.include_keywords?.length > 0 || filterConfig.exclude_keywords?.length > 0

    if (!hasIncludeCategories && !hasExcludeCategories && !hasKeywords) {
      errors.push('At least one filter criteria is required (categories or keywords)')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  const validateCalendarName = (name) => {
    const errors = []
    
    if (!name || !name.trim()) {
      errors.push('Calendar name is required')
    } else if (name.trim().length < 3) {
      errors.push('Calendar name must be at least 3 characters')
    } else if (name.trim().length > 100) {
      errors.push('Calendar name must be less than 100 characters')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  // Clear error helper
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    filteredCalendars,
    loading,
    creating,
    updating,
    error,
    
    // API Operations
    loadFilteredCalendars,
    createFilteredCalendar,
    updateFilteredCalendar,
    deleteFilteredCalendar,
    getPublicCalendar,
    downloadFilteredCalendar,
    
    // Utilities
    validateFilterConfig,
    validateCalendarName,
    clearError,
    
    // Pure functions (exposed for testing)
    createFilteredCalendarPayload,
    transformFilteredCalendar,
    updateFilteredCalendarInList,
    removeFilteredCalendarFromList
  }
}