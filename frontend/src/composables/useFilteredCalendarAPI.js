/**
 * Filtered Calendar API operations
 * Business logic for creating and managing filtered calendars
 */

import { ref } from 'vue'
import { useHTTP } from './useHTTP'
import { useAppStore } from '../stores/app'

export function useFilteredCalendarAPI() {
  // HTTP client
  const { get, post, put, del, loading, error, clearError, setError } = useHTTP()
  
  // State
  const filteredCalendars = ref([])
  const creating = ref(false)
  const updating = ref(false)
  
  const appStore = useAppStore()

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
    const result = await get('/api/filtered-calendars')
    
    if (result.success && result.data && result.data.filtered_calendars) {
      filteredCalendars.value = result.data.filtered_calendars.map(transformFilteredCalendar)
    } else if (!result.success) {
      console.error('Error loading filtered calendars:', result.error)
    }
  }

  const createFilteredCalendar = async (sourceCalendarId, name, selectedGroups, selectedEvents) => {
    if (!name?.trim()) {
      setError('Name is required')
      return false
    }

    creating.value = true
    
    const payload = createFilteredCalendarPayload(sourceCalendarId, name, selectedGroups, selectedEvents)
    const result = await post('/api/filtered-calendars', payload)
    
    creating.value = false
    
    if (result.success && result.data) {
      const newCalendar = transformFilteredCalendar(result.data)
      filteredCalendars.value.push(newCalendar)
      return true
    } else {
      console.error('Error creating filtered calendar:', result.error)
      return false
    }
  }

  const updateFilteredCalendar = async (calendarId, updates) => {
    if (!calendarId) {
      setError('Calendar ID is required')
      return false
    }

    updating.value = true

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

    const result = await put(`/api/filtered-calendars/${calendarId}`, payload)
    
    updating.value = false
    
    if (result.success && result.data) {
      const updatedCalendar = transformFilteredCalendar(result.data)
      filteredCalendars.value = updateFilteredCalendarInList(
        filteredCalendars.value, 
        updatedCalendar
      )
      return true
    } else {
      console.error('Error updating filtered calendar:', result.error)
      return false
    }
  }

  const deleteFilteredCalendar = async (calendarId) => {
    if (!calendarId) {
      setError('Calendar ID is required')
      return false
    }

    const result = await del(`/api/filtered-calendars/${calendarId}`)
    
    if (result.success) {
      filteredCalendars.value = removeFilteredCalendarFromList(
        filteredCalendars.value, 
        calendarId
      )
      return true
    } else {
      console.error('Error deleting filtered calendar:', result.error)
      return false
    }
  }

  const getPublicCalendar = async (token) => {
    const result = await get(`/cal/${token}`)
    
    if (result.success) {
      return result.data
    } else {
      console.error('Error loading public calendar:', result.error)
      return null
    }
  }


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