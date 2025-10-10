/**
 * Calendar Store
 * Manages calendar operations: CRUD, sync, events, and groups
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useHTTP } from '../composables/useHTTP'
import { useUsername } from '../composables/useUsername'
import { API_ENDPOINTS } from '../constants/api'

export const useCalendarStore = defineStore('calendar', () => {
  // ===============================================
  // DEPENDENCIES
  // ===============================================
  const { getUserId } = useUsername()
  const { get, post, del } = useHTTP()

  // ===============================================
  // STATE
  // ===============================================
  const calendars = ref([])
  const selectedCalendar = ref(null)
  const newCalendar = ref({
    name: '',
    url: ''
  })
  const events = ref([])
  const recurringEvents = ref({})

  // ===============================================
  // CALENDAR CRUD OPERATIONS
  // ===============================================

  const fetchCalendars = async () => {
    const currentUserId = getUserId()
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')

    if (hasCustomUsername) {
      // LOGGED IN: Load from server only
      try {
        const result = await get(`${API_ENDPOINTS.CALENDARS}`)

        if (result.success) {
          calendars.value = result.data || []
          return { success: true, data: calendars.value }
        } else {
          calendars.value = []
          return { success: false, error: result.error }
        }
      } catch (error) {
        calendars.value = []
        return { success: false, error: 'Failed to connect to server' }
      }
    } else {
      // LOGGED OUT: Read-only mode - no calendar management
      calendars.value = []
      return {
        success: true,
        data: [],
        message: 'Login required for calendar management'
      }
    }
  }

  const addCalendar = async () => {
    if (!newCalendar.value.name.trim() || !newCalendar.value.url.trim()) {
      return { success: false, error: 'Please provide both calendar name and URL' }
    }

    const currentUserId = getUserId()
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')

    const calendarData = {
      name: newCalendar.value.name.trim(),
      source_url: newCalendar.value.url.trim()
    }

    if (hasCustomUsername) {
      // LOGGED IN: Create on server immediately, wait for response
      try {
        const result = await post(`${API_ENDPOINTS.CALENDARS}`, calendarData)

        if (result.success) {
          // Add to local calendars list
          calendars.value.push(result.data)

          // Reset form
          newCalendar.value = { name: '', url: '' }

          // Check for warnings and modify result to include them
          if (result.data.warnings && result.data.warnings.length > 0) {
            return {
              success: true,
              data: result.data,
              warnings: result.data.warnings
            }
          }

          return result
        } else {
          return {
            success: false,
            error: result.error || 'Failed to create calendar on server'
          }
        }
      } catch (error) {
        return {
          success: false,
          error: 'Failed to connect to server. Please check your connection.'
        }
      }
    } else {
      // LOGGED OUT: Prevent calendar creation for anonymous users
      return { success: false, error: 'Login required to create calendars' }
    }
  }

  const deleteCalendar = async (calendarId) => {
    // Prevent deletion of domain calendars
    if (String(calendarId).startsWith('cal_domain_')) {
      return {
        success: false,
        error: 'Domain calendars cannot be deleted by users. Please contact your administrator.'
      }
    }

    const currentUserId = getUserId()
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')

    // Convert calendarId to number for consistent comparison
    const numericCalendarId = typeof calendarId === 'string' ? parseInt(calendarId, 10) : calendarId

    const calendarIndex = calendars.value.findIndex(cal => cal.id === numericCalendarId)
    if (calendarIndex === -1) {
      return { success: false, error: 'Calendar not found. It may have already been deleted.' }
    }

    if (hasCustomUsername) {
      // LOGGED IN: Delete from server first, then update local list
      try {
        const result = await del(`${API_ENDPOINTS.CALENDAR_DELETE(numericCalendarId)}`)

        if (result.success) {
          // Server deletion succeeded - remove from local list
          calendars.value.splice(calendarIndex, 1)
          return { success: true }
        } else {
          // Check if it's a 404 (calendar already deleted)
          if (result.status === 404 || result.error?.includes('not found') || result.error?.includes('404')) {
            // Calendar doesn't exist on server anymore - remove from local list anyway
            calendars.value.splice(calendarIndex, 1)
            return { success: true }
          } else {
            return {
              success: false,
              error: result.error || 'Failed to delete calendar from server'
            }
          }
        }
      } catch (error) {
        return {
          success: false,
          error: 'Failed to connect to server. Please try again.'
        }
      }
    } else {
      // LOGGED OUT: Read-only mode
      return { success: false, error: 'Login required to delete calendars' }
    }
  }

  const syncCalendar = async (calendarId) => {
    // Convert calendarId to number for consistent comparison
    const numericCalendarId = typeof calendarId === 'string' ? parseInt(calendarId, 10) : calendarId

    const currentUserId = getUserId()
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')

    if (hasCustomUsername) {
      // LOGGED IN: Call server sync endpoint
      try {
        const result = await post(`${API_ENDPOINTS.CALENDAR_SYNC(numericCalendarId)}`)

        if (result.success) {
          return {
            success: true,
            data: result.data
          }
        } else {
          return {
            success: false,
            error: result.error || 'Failed to sync calendar'
          }
        }
      } catch (error) {
        return {
          success: false,
          error: 'Failed to connect to server. Please try again.'
        }
      }
    } else {
      // LOGGED OUT: Read-only mode
      return { success: false, error: 'Login required to sync calendars' }
    }
  }

  // ===============================================
  // CALENDAR SELECTION
  // ===============================================

  const selectCalendar = (calendar) => {
    selectedCalendar.value = calendar
  }

  const clearSelection = () => {
    selectedCalendar.value = null
  }

  // ===============================================
  // EVENT LOADING
  // ===============================================

  const loadCalendarEvents = async (calendarId) => {
    const result = await get(API_ENDPOINTS.CALENDAR_EVENTS(calendarId))

    if (result.success) {
      events.value = result.data.events || []
    }

    return result
  }

  const loadCalendarRecurringEvents = async (calendarId) => {
    const result = await get(API_ENDPOINTS.CALENDAR_EVENTS(calendarId))

    if (result.success) {
      // Process events into event types format
      const recurringEventMap = {}
      if (result.data.events) {
        result.data.events.forEach(event => {
          const recurringEvent = event.title
          if (!recurringEventMap[recurringEvent]) {
            recurringEventMap[recurringEvent] = {
              count: 0,
              events: []
            }
          }
          recurringEventMap[recurringEvent].count++
          recurringEventMap[recurringEvent].events.push(event)
        })
      }
      recurringEvents.value = recurringEventMap
    }

    return result
  }

  // ===============================================
  // GROUP LOADING
  // ===============================================

  const loadCalendarGroups = async (calendarId) => {
    // For user calendars, use the events endpoint which provides flat structure
    const result = await get(API_ENDPOINTS.CALENDAR_EVENTS(calendarId))

    if (result.success) {
      // Process events from the new API response format
      if (result.data.events && result.data.events.length > 0) {
        // Normalize field names: API returns start_time/end_time, but frontend expects start/end
        const normalizedEvents = result.data.events.map(event => ({
          ...event,
          // Map start_time -> start (keep original as fallback)
          start: event.start_time || event.start,
          dtstart: event.start_time || event.dtstart,
          // Map end_time -> end (keep original as fallback)
          end: event.end_time || event.end,
          dtend: event.end_time || event.dtend,
          // Keep original fields for compatibility
          start_time: event.start_time,
          end_time: event.end_time
        }))

        // Events is an array of individual events, we need to group them by title
        const recurringEventMap = {}
        normalizedEvents.forEach(event => {
          const recurringEvent = event.title
          if (!recurringEventMap[recurringEvent]) {
            recurringEventMap[recurringEvent] = {
              name: recurringEvent,
              count: 0,
              events: []
            }
          }
          recurringEventMap[recurringEvent].count++
          recurringEventMap[recurringEvent].events.push(event)
        })

        // Store the processed data in reactive variables for CalendarView
        recurringEvents.value = recurringEventMap
        events.value = normalizedEvents
      } else {
        // No events data - clear reactive variables
        recurringEvents.value = {}
        events.value = []
      }
    }

    return result
  }

  // ===============================================
  // EXPORTS
  // ===============================================

  return {
    // State
    calendars,
    selectedCalendar,
    newCalendar,
    events,
    recurringEvents,

    // Calendar CRUD
    fetchCalendars,
    addCalendar,
    deleteCalendar,
    syncCalendar,

    // Selection
    selectCalendar,
    clearSelection,

    // Event Loading
    loadCalendarEvents,
    loadCalendarRecurringEvents,
    loadCalendarGroups
  }
})
