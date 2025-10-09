/**
 * Filtered Calendar API operations
 * Business logic for creating and managing filtered calendars
 */

import { ref } from 'vue'
import { useHTTP } from './useHTTP'
import { useAppStore } from '../stores/app'
import { useUsername } from './useUsername'
import { API_ENDPOINTS } from '../constants/api'

export function useFilteredCalendarAPI() {
  // HTTP client
  const { get, post, put, del, loading, error, clearError, setError } = useHTTP()
  const { getUserId } = useUsername()
  
  // State
  const filteredCalendars = ref([])
  const creating = ref(false)
  const updating = ref(false)
  const deleting = ref(false)
  
  const appStore = useAppStore()

  /**
   * Pure function: Build endpoint for filtered calendars
   *
   * NOTE: Authentication now handled via JWT tokens in Authorization header,
   * not via username query parameters.
   */
  const buildFilterEndpoint = (calendarIdOrDomain, filterId = null) => {
    if (typeof calendarIdOrDomain === 'string' && calendarIdOrDomain.startsWith('cal_domain_')) {
      // Domain calendar: extract domain from cal_domain_exter -> exter
      const domain = calendarIdOrDomain.replace('cal_domain_', '')
      const base = API_ENDPOINTS.DOMAIN_FILTERS(domain)
      return filterId ? `${base}/${filterId}` : base
    } else {
      // Regular calendar
      const base = API_ENDPOINTS.CALENDAR_FILTERS(calendarIdOrDomain)
      return filterId ? `${base}/${filterId}` : base
    }
  }

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
    
    // Check authentication state - only load filtered calendars for logged-in users
    const currentUserId = getUserId()
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')
    
    if (!hasCustomUsername) {
      console.log('👤 User is anonymous - clearing filtered calendars')
      filteredCalendars.value = []
      return
    }
    
    // Build authenticated endpoint
    const endpoint = buildFilterEndpoint(calendarIdOrDomain)
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
        unselected_event_ids: filter.unselected_event_ids || [],
        link_uuid: filter.link_uuid,
        export_url: filter.export_url || API_ENDPOINTS.ICAL_EXPORT(filter.link_uuid),
        filter_config: filter.filter_config || {
          recurring_events: filter.subscribed_event_ids || [],
          groups: filter.subscribed_group_ids || []
        },
        created_at: filter.created_at,
        updated_at: filter.updated_at
      }))
    } else if (!result.success) {
      console.error('Error loading filtered calendars:', result.error)
    }
  }

  const createFilteredCalendar = async (sourceCalendarId, name, selectedGroups, selectedEvents, includeFutureEvents, groups = {}) => {
    if (!name?.trim()) {
      setError('Name is required')
      return false
    }

    if (!sourceCalendarId) {
      setError('Calendar ID is required')
      return false
    }

    // Check authentication state - only logged-in users can create filtered calendars
    const currentUserId = getUserId()
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')

    if (!hasCustomUsername) {
      setError('Login required to create filtered calendars')
      return false
    }

    creating.value = true

    // Compute the three lists for domain filters
    const subscribedGroupIds = selectedGroups || []
    let subscribedEventIds = selectedEvents || []
    const unselectedEventIds = []

    // For domain calendars: compute whitelist and blacklist
    if (subscribedGroupIds.length > 0 && Object.keys(groups).length > 0) {
      // Get all event titles from subscribed groups
      const eventTitlesInSubscribedGroups = new Set()
      subscribedGroupIds.forEach(groupId => {
        const group = groups[groupId]
        if (group?.recurring_events) {
          group.recurring_events.forEach(event => {
            if (event.event_count > 0) {
              eventTitlesInSubscribedGroups.add(event.title)
            }
          })
        }
      })

      // Whitelist: events selected but NOT in any subscribed group
      subscribedEventIds = selectedEvents.filter(title => !eventTitlesInSubscribedGroups.has(title))

      // Blacklist: events in subscribed groups but NOT selected
      eventTitlesInSubscribedGroups.forEach(title => {
        if (!selectedEvents.includes(title)) {
          unselectedEventIds.push(title)
        }
      })
    }

    // Map to backend filter format
    const payload = {
      name: name.trim(),
      subscribed_group_ids: subscribedGroupIds,
      subscribed_event_ids: subscribedEventIds,
      unselected_event_ids: unselectedEventIds
    }

    // Only add include_future_events for personal calendars when explicitly set to true
    // Don't send it at all for domain calendars or when false/undefined
    if (includeFutureEvents === true) {
      payload.include_future_events = true
    }
    
    // Build authenticated endpoint
    const endpoint = buildFilterEndpoint(sourceCalendarId)
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
        unselected_event_ids: result.data.unselected_event_ids || [],
        link_uuid: result.data.link_uuid,
        export_url: result.data.export_url || API_ENDPOINTS.ICAL_EXPORT(result.data.link_uuid),
        filter_config: result.data.filter_config || {
          recurring_events: result.data.subscribed_event_ids || [],
          groups: result.data.subscribed_group_ids || []
        },
        created_at: result.data.created_at,
        updated_at: result.data.updated_at
      }
      filteredCalendars.value.push(newFilter)
      return true
    } else {
      console.error('Error creating filtered calendar:', result.error)
      return false
    }
  }

  const updateFilteredCalendar = async (filterId, updates, groups = {}) => {
    if (!filterId) {
      setError('Filter ID is required')
      return false
    }

    updating.value = true

    try {
      // Find the filter to determine the correct endpoint
      const filterToUpdate = filteredCalendars.value.find(filter => filter.id === filterId)
      if (!filterToUpdate) {
        setError('Filter not found')
        return false
      }

      let payload = { ...updates }

      // If filter_config is provided, map it to backend format with three-list computation
      if (updates.filter_config) {
        const selectedGroups = updates.filter_config.groups || []
        const selectedEvents = updates.filter_config.recurring_events || []

        // Compute the three lists for domain filters
        const subscribedGroupIds = selectedGroups
        let subscribedEventIds = selectedEvents
        const unselectedEventIds = []

        // For domain calendars: compute whitelist and blacklist
        if (subscribedGroupIds.length > 0 && Object.keys(groups).length > 0) {
          // Get all event titles from subscribed groups
          const eventTitlesInSubscribedGroups = new Set()
          subscribedGroupIds.forEach(groupId => {
            const group = groups[groupId]
            if (group?.recurring_events) {
              group.recurring_events.forEach(event => {
                if (event.event_count > 0) {
                  eventTitlesInSubscribedGroups.add(event.title)
                }
              })
            }
          })

          // Whitelist: events selected but NOT in any subscribed group
          subscribedEventIds = selectedEvents.filter(title => !eventTitlesInSubscribedGroups.has(title))

          // Blacklist: events in subscribed groups but NOT selected
          eventTitlesInSubscribedGroups.forEach(title => {
            if (!selectedEvents.includes(title)) {
              unselectedEventIds.push(title)
            }
          })
        }

        payload.subscribed_event_ids = subscribedEventIds
        payload.subscribed_group_ids = subscribedGroupIds
        payload.unselected_event_ids = unselectedEventIds
        // Remove filter_config from payload as backend doesn't expect it
        delete payload.filter_config
      }

      // Build authenticated endpoint with filter ID
      const calendarIdOrDomain = filterToUpdate.domain_key 
        ? `cal_domain_${filterToUpdate.domain_key}` 
        : filterToUpdate.calendar_id
      
      if (!calendarIdOrDomain) {
        setError('Invalid filter: missing calendar_id or domain_key')
        return false
      }
      
      const endpoint = buildFilterEndpoint(calendarIdOrDomain, filterId)

      const result = await put(endpoint, payload)
      
      if (result.success && result.data) {
        // Update the filter in local list
        const updatedFilter = {
          ...filterToUpdate,
          ...result.data,
          filter_config: result.data.filter_config || {
            recurring_events: result.data.subscribed_event_ids || [],
            groups: result.data.subscribed_group_ids || []
          }
        }
        filteredCalendars.value = updateFilteredCalendarInList(filteredCalendars.value, updatedFilter)
        return true
      } else {
        console.error('Error updating filtered calendar:', result.error)
        setError(result.error || 'Failed to update filter')
        return false
      }
    } catch (error) {
      console.error('Error updating filtered calendar:', error)
      setError('Failed to update filter')
      return false
    } finally {
      updating.value = false
    }
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
      // Build authenticated endpoint with filter ID
      const calendarIdOrDomain = filterToDelete.domain_key 
        ? `cal_domain_${filterToDelete.domain_key}` 
        : filterToDelete.calendar_id
      
      if (!calendarIdOrDomain) {
        setError('Invalid filter: missing calendar_id or domain_key')
        return false
      }
      
      const endpoint = buildFilterEndpoint(calendarIdOrDomain, filterId)

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
    const result = await get(API_ENDPOINTS.PUBLIC_CALENDAR(token))

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