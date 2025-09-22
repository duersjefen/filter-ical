/**
 * Composable for Filtered Calendar API operations
 * Following functional programming principles with pure functions
 */

import { ref, reactive } from 'vue'
import axios from 'axios'
import { useAPI } from './useAPI'
import { useAppStore } from '../stores/app'

export function useFilteredCalendarAPI() {
  // State
  const filteredCalendars = ref([])
  const loading = ref(false)
  const creating = ref(false)
  const updating = ref(false)
  const error = ref(null)
  
  // No authentication required for public access
  const appStore = useAppStore()

  // Use axios directly for HTTP calls

  /**
   * Pure function: Create filtered calendar data payload
   */
  const createFilteredCalendarPayload = (sourceCalendarId, name, selectedGroups, selectedEvents) => {
    return {
      source_calendar_id: sourceCalendarId,
      name: name.trim(),
      selected_groups: selectedGroups || [],
      selected_events: selectedEvents || []
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
      selected_groups: apiResponse.selected_groups || [],
      selected_events: apiResponse.selected_events || [],
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
      const response = await axios.get('/api/filtered-calendars', {
        headers: {}
      })
      
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

  const createFilteredCalendar = async (sourceCalendarId, name, selectedGroups, selectedEvents) => {
    if (!name?.trim()) {
      error.value = 'Name is required'
      return false
    }

    creating.value = true
    error.value = null

    try {
      const payload = createFilteredCalendarPayload(sourceCalendarId, name, selectedGroups, selectedEvents)
      const response = await axios.post('/api/filtered-calendars', payload, {
        headers: {}
      })
      
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
        selected_groups: updates.selected_groups,
        selected_events: updates.selected_events
      }

      // Remove undefined values
      Object.keys(payload).forEach(key => {
        if (payload[key] === undefined) {
          delete payload[key]
        }
      })

      const response = await axios.put(`/api/filtered-calendars/${calendarId}`, payload, {
        headers: {}
      })
      
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
      await axios.delete(`/api/filtered-calendars/${calendarId}`, {
        headers: {}
      })
      
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
      const response = await axios.get(`/cal/${token}`, {
        headers: {}
      })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load public calendar'
      console.error('Error loading public calendar:', err)
      return null
    }
  }

  // Note: Removed downloadFilteredCalendar function since we now provide
  // calendar subscription URLs instead of forcing file downloads

  /**
   * Pure helper functions for validation
   */
  const validateSelection = (selectedGroups, selectedEvents) => {
    const errors = []
    
    const hasGroups = selectedGroups?.length > 0
    const hasEvents = selectedEvents?.length > 0

    if (!hasGroups && !hasEvents) {
      errors.push('At least one group or event must be selected')
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
    
    // Utilities
    validateSelection,
    validateCalendarName,
    clearError,
    
    // Pure functions (exposed for testing)
    createFilteredCalendarPayload,
    transformFilteredCalendar,
    updateFilteredCalendarInList,
    removeFilteredCalendarFromList
  }
}