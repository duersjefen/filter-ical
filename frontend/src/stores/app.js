/**
 * Unified App Store
 * Combines all functionality from appStore, calendars, events, filters, and compatibility stores
 * Eliminates cross-store dependencies and simplifies the architecture
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useHTTP } from '../composables/useHTTP'
import { useUsername } from '../composables/useUsername'
import { API_ENDPOINTS } from '../constants/api'

export const useAppStore = defineStore('app', () => {
  // ===============================================
  // USERNAME & API INTEGRATION
  // ===============================================
  
  const { getUserId, onUsernameChange } = useUsername()
  const { get, post, put, del, loading, error, clearError, setError } = useHTTP()

  // ===============================================
  // PUBLIC ACCESS - NO AUTHENTICATION REQUIRED
  // ===============================================

  // Available domains (all configured domains in system)
  const availableDomains = ref([])

  const fetchAvailableDomains = async () => {
    try {
      const result = await get(API_ENDPOINTS.DOMAINS)

      if (result.success) {
        availableDomains.value = result.data || []
        return { success: true, data: availableDomains.value }
      } else {
        availableDomains.value = []
        return { success: false, error: result.error }
      }
    } catch (error) {
      availableDomains.value = []
      return { success: false, error: 'Failed to load domains' }
    }
  }

  const initializeApp = () => {
    // Force username initialization from localStorage
    getUserId() // This triggers the username composable initialization

    // Load available domains (public data, no auth required)
    fetchAvailableDomains()

    // Set up username change detection for data source switching
    onUsernameChange((newUsername, oldUsername) => {
      // Clear current calendars to prevent confusion
      calendars.value = []

      // Clear filtered calendars to prevent showing stale data
      filteredCalendars.value = []

      // Reload calendars with new authentication state
      fetchCalendars()

      // Reload filters with new username
      fetchUserFilters()
    })
  }

  // ===============================================
  // CALENDARS SECTION
  // ===============================================
  
  const calendars = ref([])
  const selectedCalendar = ref(null)
  const newCalendar = ref({
    name: '',
    url: ''
  })


  const generateLocalCalendarId = () => {
    // Generate a local calendar ID with 'local_' prefix
    return 'local_' + Math.random().toString(36).substring(2, 11)
  }


  const fetchCalendars = async () => {
    const currentUserId = getUserId()
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')

    if (hasCustomUsername) {
      // LOGGED IN: Load from server only
      try {
        const result = await get(`${API_ENDPOINTS.CALENDARS}`)

        if (result.success) {
          // New API returns direct array, not wrapped in object
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
      // LOGGED OUT: Create locally only
      const localCalendar = {
        id: generateLocalCalendarId(),
        name: calendarData.name,
        url: calendarData.url,
        user_id: currentUserId,
        created_at: new Date().toISOString(),
        source: 'local'
      }

      // Prevent calendar creation for anonymous users
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

    const calendarToDelete = calendars.value[calendarIndex]

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
      // Prevent calendar deletion for anonymous users
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

  const selectCalendar = (calendar) => {
    selectedCalendar.value = calendar
  }

  const clearSelection = () => {
    selectedCalendar.value = null
  }

  // ===============================================
  // EVENTS SECTION
  // ===============================================
  
  const events = ref([])
  const recurringEvents = ref({})
  
  // Event filtering state
  const keywordFilter = ref('')
  const dateRange = ref({
    start: null,
    end: null
  })
  const sortBy = ref('date')
  const sortDirection = ref('asc')

  // ===============================================
  // GROUPS SECTION
  // ===============================================
  
  const groups = ref({})
  const hasGroups = ref(false)

  // ===============================================
  // EVENTS EXTRACTION FROM GROUPS - REACTIVE
  // ===============================================
  
  /**
   * Extract all events from groups data for preview consumption
   * This computed property ensures reactivity when groups data changes
   * Deduplicates events that appear in multiple groups
   */
  const allEventsFromGroups = computed(() => {
    const extractedEvents = []
    
    // Extract from current events array (for user calendars)
    if (events.value && events.value.length > 0) {
      extractedEvents.push(...events.value)
    }
    
    // Extract from groups structure (for domain calendars)
    if (groups.value && Object.keys(groups.value).length > 0) {
      Object.values(groups.value).forEach(group => {
        if (group.recurring_events && Array.isArray(group.recurring_events)) {
          group.recurring_events.forEach(recurringEvent => {
            if (recurringEvent.events && Array.isArray(recurringEvent.events)) {
              extractedEvents.push(...recurringEvent.events)
            }
          })
        }
      })
    }
    
    // Deduplicate events using robust identifier strategy
    const uniqueEvents = new Map()
    extractedEvents.forEach(event => {
      // Generate stable identifier using event content
      let identifier
      if (event.uid) {
        identifier = event.uid
      } else {
        // Create content-based identifier
        const title = event.title || event.summary || 'untitled'
        const start = event.start || event.dtstart || ''
        const end = event.end || event.dtend || ''
        
        if (start && end) {
          identifier = `${title}-${start}-${end}`
        } else if (start) {
          const description = event.description || ''
          const descHash = description ? description.length.toString() : '0'
          identifier = `${title}-${start}-${descHash}`
        } else {
          const description = event.description || ''
          const descHash = description ? description.length.toString() : '0'
          identifier = `${title}-${descHash}`
        }
      }
      
      // Only keep the first occurrence of each unique event
      if (!uniqueEvents.has(identifier)) {
        uniqueEvents.set(identifier, event)
      }
    })
    
    return Array.from(uniqueEvents.values())
  })


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

  // Event filtering methods

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
    keywordFilter.value = ''
    dateRange.value = { start: null, end: null }
    sortBy.value = 'date'
    sortDirection.value = 'asc'
  }

  // Groups methods
  const loadCalendarGroups = async (calendarId) => {
    // For user calendars, use the events endpoint which provides flat structure
    const result = await get(API_ENDPOINTS.CALENDAR_EVENTS(calendarId))

    if (result.success) {
      // User calendars don't have groups in the new API, they have flat event structure
      hasGroups.value = false
      groups.value = {}

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

  const loadDomainGroups = async (domainName) => {
    // Use the domain events endpoint which provides the full hierarchical structure
    const result = await get(API_ENDPOINTS.DOMAIN_EVENTS(domainName))

    if (result.success) {
      // Use backend format directly - no complex conversion needed
      const domainData = result.data
      
      hasGroups.value = domainData.groups && domainData.groups.length > 0
      
      // Simple direct mapping - keep backend structure
      groups.value = {}
      if (domainData.groups) {
        domainData.groups.forEach(group => {
          const groupId = String(group.id)
          groups.value[groupId] = {
            id: groupId,
            name: group.name,
            description: group.description,
            recurring_events: group.recurring_events || []
          }
        })
      }
      

    }

    return result
  }


  // Individual event selection removed - groups now work with event types

  // Note: Manual event assignment removed - groups now contain event types, not individual events

  // ===============================================
  // SAVED FILTERS SECTION
  // ===============================================

  const savedFilters = ref([])
  const userDomainFilters = ref([])

  const fetchFilters = async () => {
    // Note: Saved filters functionality not implemented in new backend yet
    return { success: true, data: { filters: [] } }
  }

  const fetchUserFilters = async () => {
    const currentUserId = getUserId()

    // Always fetch filters if we have any user ID (including anon)
    // But only store/display domain filters for logged-in users
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')

    // Still fetch even for anonymous users in case they log in later
    try {
      const result = await get(`${API_ENDPOINTS.USER_FILTERS}`)

      if (result.success) {
        // useHTTP wraps response in { success: true, data: [...] }
        const filters = result.data || []

        // Store filters only if user is logged in
        if (hasCustomUsername) {
          userDomainFilters.value = filters
        } else {
          userDomainFilters.value = []
        }

        return { success: true, data: filters }
      } else {
        userDomainFilters.value = []
        return { success: false, error: result.error || 'Failed to fetch filters' }
      }
    } catch (error) {
      userDomainFilters.value = []
      return { success: false, error: 'Failed to connect to server' }
    }
  }

  // Computed property to extract unique domains where user has filters
  const domainsWithFilters = computed(() => {
    // Ensure we have an array to work with
    const filters = Array.isArray(userDomainFilters.value) ? userDomainFilters.value : []
    const domainMap = new Map()

    filters.forEach(filter => {
      if (filter.domain_key && !domainMap.has(filter.domain_key)) {
        domainMap.set(filter.domain_key, {
          domain_key: filter.domain_key,
          filter_count: 0
        })
      }

      if (filter.domain_key) {
        domainMap.get(filter.domain_key).filter_count++
      }
    })

    return Array.from(domainMap.values())
  })

  const saveFilter = async (name, config) => {
    const filterName = name || `Filter ${config.selectedRecurringEvents?.length || 0} types`
    
    const newFilter = {
      id: 'filter_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9),
      name: filterName,
      config: config,
      created_at: new Date().toISOString()
    }

    // Add to filters list
    savedFilters.value.push(newFilter)

    return { success: true, data: newFilter }
  }

  const deleteFilter = async (filterId) => {
    const filterIndex = savedFilters.value.findIndex(filter => filter.id === filterId)
    
    if (filterIndex === -1) {
      return { success: false, error: 'Filter not found' }
    }

    // Remove from filters list
    savedFilters.value.splice(filterIndex, 1)

    return { success: true }
  }


  // ===============================================
  // FILTERED CALENDARS SECTION
  // ===============================================
  
  const filteredCalendars = ref([])

  const loadFilteredCalendars = async () => {
    // Note: This functionality may need to be implemented in the new backend
    // For now, return empty list to prevent errors
    filteredCalendars.value = []
    return { success: true, data: [] }
  }

  const createFilteredCalendar = async (sourceCalendarId, name, filterConfig) => {
    if (!name?.trim()) {
      return { success: false, error: 'Name is required' }
    }

    // Note: This functionality may need to be implemented in the new backend
    // The new API uses filters at calendar or domain level instead
    return { success: false, error: 'Filtered calendars not yet implemented in new backend' }
  }

  const updateFilteredCalendar = async (calendarId, updates) => {
    if (!calendarId) {
      return { success: false, error: 'Calendar ID is required' }
    }

    // Note: This functionality may need to be implemented in the new backend
    return { success: false, error: 'Filtered calendars not yet implemented in new backend' }
  }

  const deleteFilteredCalendar = async (calendarId) => {
    if (!calendarId) {
      return { success: false, error: 'Calendar ID is required' }
    }

    // Note: This functionality may need to be implemented in the new backend
    return { success: false, error: 'Filtered calendars not yet implemented in new backend' }
  }

  // ===============================================
  // USER PREFERENCES SECTION
  // ===============================================
  
  const getUserPreferences = async () => {
    // Note: User preferences not implemented in new backend yet
    return { success: true, data: { preferences: {} } }
  }

  const saveUserPreferences = async (preferences) => {
    // Note: User preferences not implemented in new backend yet
    return { success: true }
  }

  const getCalendarPreferences = async (calendarId) => {
    // Note: Calendar preferences not implemented in new backend yet
    return { success: true, data: { preferences: {} } }
  }

  const saveCalendarPreferences = async (calendarId, preferences) => {
    // Note: Calendar preferences not implemented in new backend yet
    return { success: true }
  }

  // ===============================================
  // ICAL GENERATION SECTION
  // ===============================================
  
  const generateIcal = async ({ calendarId, selectedRecurringEvents }) => {
    // Use the new filter creation + iCal export workflow
    // First create a filter, then use its UUID to get the iCal
    
    const filterData = {
      name: `Generated Filter ${new Date().toISOString()}`,
      subscribed_event_ids: [],
      subscribed_group_ids: []
    }
    
    try {
      // Create filter for this calendar
      const filterResult = await post(`${API_ENDPOINTS.CALENDAR_FILTERS(calendarId)}`, filterData)

      if (filterResult.success && filterResult.data.link_uuid) {
        // Get the iCal content using the filter's UUID
        const icalResult = await get(API_ENDPOINTS.ICAL_EXPORT(filterResult.data.link_uuid))
        return icalResult
      } else {
        return { success: false, error: 'Failed to create filter for iCal generation' }
      }
    } catch (error) {
      return { success: false, error: 'Failed to generate iCal: ' + error.message }
    }
  }


  return {
    // ===============================================
    // APP INITIALIZATION
    // ===============================================
    initializeApp,

    // ===============================================
    // DOMAINS
    // ===============================================
    availableDomains,
    fetchAvailableDomains,

    // ===============================================
    // CALENDARS
    // ===============================================
    calendars,
    selectedCalendar,
    newCalendar,
    fetchCalendars,
    addCalendar,
    deleteCalendar,
    syncCalendar,
    selectCalendar,
    clearSelection,

    // ===============================================
    // EVENTS & FILTERING
    // ===============================================
    events,
    allEventsFromGroups,
    recurringEvents,
    keywordFilter,
    dateRange,
    sortBy,
    sortDirection,
    loadCalendarEvents,
    loadCalendarRecurringEvents,
    setKeywordFilter,
    setDateRange,
    setSorting,
    clearAllFilters,

    // ===============================================
    // GROUPS
    // ===============================================
    groups,
    hasGroups,
    loadCalendarGroups,
    loadDomainGroups,

    // ===============================================
    // SAVED FILTERS
    // ===============================================
    savedFilters,
    userDomainFilters,
    domainsWithFilters,
    fetchFilters,
    fetchUserFilters,
    saveFilter,
    deleteFilter,

    // ===============================================
    // FILTERED CALENDARS
    // ===============================================
    filteredCalendars,
    loadFilteredCalendars,
    createFilteredCalendar,
    updateFilteredCalendar,
    deleteFilteredCalendar,

    // ===============================================
    // USER PREFERENCES
    // ===============================================
    getUserPreferences,
    saveUserPreferences,
    getCalendarPreferences,
    saveCalendarPreferences,

    // ===============================================
    // ICAL GENERATION
    // ===============================================
    generateIcal,

    // ===============================================
    // SHARED STATE & UTILITIES
    // ===============================================
    loading,
    error,
    clearError,
    setError
  }
})