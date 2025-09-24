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
  const deleting = ref(false)
  
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

  const loadFilteredCalendars = async (calendarIdOrDomain) => {
    if (!calendarIdOrDomain) {
      console.warn('Cannot load filtered calendars without calendar ID or domain')
      return
    }
    
    // Determine if this is a domain calendar or regular calendar
    let endpoint
    if (typeof calendarIdOrDomain === 'string' && calendarIdOrDomain.startsWith('cal_domain_')) {
      // Domain calendar: extract domain from cal_domain_exter -> exter
      const domain = calendarIdOrDomain.replace('cal_domain_', '')
      endpoint = `/domains/${domain}/filters`
    } else {
      // Regular calendar
      endpoint = `/calendars/${calendarIdOrDomain}/filters`
    }
    
    const result = await get(endpoint)
    
    if (result.success && result.data) {
      // Backend returns array directly, not wrapped in filtered_calendars
      const filters = Array.isArray(result.data) ? result.data : []
      filteredCalendars.value = filters.map(filter => ({
        id: filter.id,
        name: filter.name,
        calendar_id: filter.calendar_id,
        domain_key: filter.domain_key,
        username: filter.username,
        subscribed_event_ids: filter.subscribed_event_ids || [],
        subscribed_group_ids: filter.subscribed_group_ids || [],
        link_uuid: filter.link_uuid,
        export_url: filter.export_url || `/ical/${filter.link_uuid}.ics`
      }))
    } else if (!result.success) {
      console.error('Error loading filtered calendars:', result.error)
    }
  }

  const createFilteredCalendar = async (sourceCalendarId, name, selectedGroups, selectedEvents) => {
    if (!name?.trim()) {
      setError('Name is required')
      return false
    }

    if (!sourceCalendarId) {
      setError('Calendar ID is required')
      return false
    }

    creating.value = true
    
    // Map to backend filter format
    const payload = {
      name: name.trim(),
      subscribed_group_ids: selectedGroups || [],
      subscribed_event_ids: selectedEvents || []
    }
    
    // Determine if this is a domain calendar or regular calendar
    let endpoint
    if (typeof sourceCalendarId === 'string' && sourceCalendarId.startsWith('cal_domain_')) {
      // Domain calendar: extract domain from cal_domain_exter -> exter
      const domain = sourceCalendarId.replace('cal_domain_', '')
      endpoint = `/domains/${domain}/filters`
    } else {
      // Regular calendar
      endpoint = `/calendars/${sourceCalendarId}/filters`
    }
    
    const result = await post(endpoint, payload)
    
    creating.value = false
    
    if (result.success && result.data) {
      const newFilter = {
        id: result.data.id,
        name: result.data.name,
        calendar_id: result.data.calendar_id,
        domain_key: result.data.domain_key,
        username: result.data.username,
        subscribed_event_ids: result.data.subscribed_event_ids || [],
        subscribed_group_ids: result.data.subscribed_group_ids || [],
        link_uuid: result.data.link_uuid,
        export_url: result.data.export_url || `/ical/${result.data.link_uuid}.ics`
      }
      filteredCalendars.value.push(newFilter)
      return true
    } else {
      console.error('Error creating filtered calendar:', result.error)
      return false
    }
  }

  const updateFilteredCalendar = async (filterId, updates) => {
    // TODO: Backend doesn't currently support updating individual filters
    // For now, this functionality is not available
    console.warn('Filter update functionality not yet implemented in backend')
    setError('Filter updates not yet supported')
    return false
  }

  const deleteFilteredCalendar = async (filterId) => {
    if (!filterId) {
      setError('Filter ID is required')
      return false
    }

    // Find the filter in the current list to determine the endpoint
    const filterToDelete = filteredCalendars.value.find(filter => filter.id === filterId)
    if (!filterToDelete) {
      setError('Filter not found')
      return false
    }

    deleting.value = true

    try {
      let endpoint
      if (filterToDelete.domain_key) {
        // Domain calendar filter
        endpoint = `/domains/${filterToDelete.domain_key}/filters/${filterId}`
      } else if (filterToDelete.calendar_id) {
        // User calendar filter
        endpoint = `/calendars/${filterToDelete.calendar_id}/filters/${filterId}`
      } else {
        setError('Invalid filter: missing calendar_id or domain_key')
        return false
      }

      const result = await del(endpoint)
      
      if (result.success) {
        // Remove from local list
        filteredCalendars.value = removeFilteredCalendarFromList(filteredCalendars.value, filterId)
        return true
      } else {
        console.error('Error deleting filtered calendar:', result.error)
        setError(result.error || 'Failed to delete filter')
        return false
      }
    } catch (error) {
      console.error('Error deleting filtered calendar:', error)
      setError('Failed to delete filter')
      return false
    } finally {
      deleting.value = false
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


  return {
    // State
    filteredCalendars,
    loading,
    creating,
    updating,
    deleting,
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