/**
 * Unified App Store
 * Combines all functionality from appStore, calendars, events, filters, and compatibility stores
 * Eliminates cross-store dependencies and simplifies the architecture
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useHTTP } from '../composables/useHTTP'
import { useUsername } from '../composables/useUsername'

export const useAppStore = defineStore('app', () => {
  // ===============================================
  // USERNAME & API INTEGRATION
  // ===============================================
  
  const { getUserId, onUsernameChange } = useUsername()
  const { get, post, put, del, loading, error, clearError, setError } = useHTTP()

  // ===============================================
  // PUBLIC ACCESS - NO AUTHENTICATION REQUIRED
  // ===============================================
  
  const initializeApp = () => {
    // Set up username change detection for data source switching
    onUsernameChange((newUsername, oldUsername) => {
      console.log('🔄 App store detected username change - triggering data reload')
      
      // Clear current calendars to prevent confusion
      calendars.value = []
      
      // Reload calendars with new authentication state
      fetchCalendars()
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
    console.log('🔄 fetchCalendars called with username:', getUserId())
    
    const currentUserId = getUserId()
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')
    
    console.log('🔍 Authentication state:', {
      currentUserId,
      hasCustomUsername,
      isLoggedIn: hasCustomUsername
    })
    
    if (hasCustomUsername) {
      // LOGGED IN: Load from server only
      console.log('🔐 User is logged in - loading from server only')
      
      try {
        console.log('🌐 Making API call to /calendars?username=' + currentUserId)
        const result = await get(`/calendars?username=${currentUserId}`)
        console.log('🌐 Server API result:', { 
          success: result.success, 
          calendarsLength: result.data?.length || 0
        })
        
        if (result.success) {
          // New API returns direct array, not wrapped in object
          calendars.value = result.data || []
          
          console.log('✅ Server calendars loaded:', { 
            length: calendars.value.length,
            firstCalendarName: calendars.value[0]?.name
          })
          
          return { success: true, data: calendars.value }
        } else {
          console.error('❌ Server load failed for logged in user:', result.error)
          calendars.value = []
          return { success: false, error: result.error }
        }
      } catch (error) {
        console.error('❌ Server connection failed for logged in user:', error)
        calendars.value = []
        return { success: false, error: 'Failed to connect to server' }
      }
      
    } else {
      // LOGGED OUT: Read-only mode - no calendar management
      console.log('👤 User is anonymous - read-only mode (login required for calendar management)')
      
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

    console.log('📅 Adding calendar:', { calendarData, hasCustomUsername })

    if (hasCustomUsername) {
      // LOGGED IN: Create on server immediately, wait for response
      console.log('🔐 User logged in - creating calendar on server')
      
      try {
        const result = await post(`/calendars?username=${currentUserId}`, calendarData)
        
        if (result.success) {
          console.log('✅ Calendar created on server:', result.data)
          
          // Add to local calendars list
          calendars.value.push(result.data)
          
          // Reset form
          newCalendar.value = { name: '', url: '' }
          
          // Check for warnings and modify result to include them
          if (result.data.warnings && result.data.warnings.length > 0) {
            console.warn('⚠️ Calendar created with warnings:', result.data.warnings)
            return {
              success: true,
              data: result.data,
              warnings: result.data.warnings
            }
          }
          
          return result
        } else {
          console.error('❌ Server calendar creation failed:', result.error)
          return { 
            success: false, 
            error: result.error || 'Failed to create calendar on server'
          }
        }
      } catch (error) {
        console.error('❌ Server request failed:', error)
        return { 
          success: false, 
          error: 'Failed to connect to server. Please check your connection.'
        }
      }
      
    } else {
      // LOGGED OUT: Create locally only
      console.log('👤 User anonymous - creating calendar locally')
      
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
      const availableIds = calendars.value.map(c => c.id).join(', ')
      console.error(`Calendar ${calendarId} not found. Available: ${availableIds}`)
      return { success: false, error: 'Calendar not found. It may have already been deleted.' }
    }
    
    const calendarToDelete = calendars.value[calendarIndex]
    console.log('🗑️ Deleting calendar:', { calendarId, hasCustomUsername, source: calendarToDelete.source })

    if (hasCustomUsername) {
      // LOGGED IN: Delete from server first, then update local list
      console.log('🔐 User logged in - deleting from server first')
      
      try {
        const result = await del(`/calendars/${numericCalendarId}?username=${currentUserId}`)
        
        if (result.success) {
          // Server deletion succeeded - remove from local list
          calendars.value.splice(calendarIndex, 1)
          console.log('✅ Calendar deleted from server and local list')
          return { success: true }
        } else {
          console.error('❌ Server deletion failed:', result.error)
          // Check if it's a 404 (calendar already deleted)
          if (result.status === 404 || result.error?.includes('not found') || result.error?.includes('404')) {
            // Calendar doesn't exist on server anymore - remove from local list anyway
            calendars.value.splice(calendarIndex, 1)
            console.log('✅ Calendar was already deleted from server - removed from local list')
            return { success: true }
          } else {
            return { 
              success: false, 
              error: result.error || 'Failed to delete calendar from server'
            }
          }
        }
      } catch (error) {
        console.error('❌ Server request failed:', error)
        return { 
          success: false, 
          error: 'Failed to connect to server. Please try again.'
        }
      }
      
    } else {
      // LOGGED OUT: Read-only mode
      console.log('👤 User anonymous - read-only mode')
      
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
      console.log('🔄 Syncing calendar from server')
      
      try {
        const result = await post(`/calendars/${numericCalendarId}/sync?username=${currentUserId}`)
        
        if (result.success) {
          console.log('✅ Calendar sync succeeded:', result.data)
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
        console.error('❌ Server sync request failed:', error)
        return { 
          success: false, 
          error: 'Failed to connect to server. Please try again.'
        }
      }
      
    } else {
      // LOGGED OUT: Read-only mode
      console.log('👤 User anonymous - cannot sync calendars')
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
    
    return extractedEvents
  })


  const loadCalendarEvents = async (calendarId) => {
    const result = await get(`/calendars/${calendarId}/events`)

    if (result.success) {
      events.value = result.data.events || []
    }

    return result
  }

  const loadCalendarRecurringEvents = async (calendarId) => {
    const result = await get(`/calendars/${calendarId}/events`)

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
    const result = await get(`/calendars/${calendarId}/events`)

    if (result.success) {
      // User calendars don't have groups in the new API, they have flat event structure
      hasGroups.value = false
      groups.value = {}

      // Process events from the new API response format
      if (result.data.events && result.data.events.length > 0) {
        // Events is an array of individual events, we need to group them by title
        const recurringEventMap = {}
        result.data.events.forEach(event => {
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
        events.value = result.data.events || []
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
    const result = await get(`/domains/${domainName}/events`)

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
      

      
      console.log('📊 Domain groups data loaded (simplified):', {
        domainName,
        hasGroups: hasGroups.value,
        groupsCount: Object.keys(groups.value).length,
        groupNames: Object.values(groups.value).map(g => g.name)
      })
    }

    return result
  }


  // Individual event selection removed - groups now work with event types

  // Note: Manual event assignment removed - groups now contain event types, not individual events

  // ===============================================
  // SAVED FILTERS SECTION
  // ===============================================
  
  const savedFilters = ref([])

  const fetchFilters = async () => {
    // Note: Saved filters functionality not implemented in new backend yet
    return { success: true, data: { filters: [] } }
  }

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
      const filterResult = await post(`/calendars/${calendarId}/filters?username=${getUserId()}`, filterData)
      
      if (filterResult.success && filterResult.data.link_uuid) {
        // Get the iCal content using the filter's UUID
        const icalResult = await get(`/ical/${filterResult.data.link_uuid}.ics`)
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
    fetchFilters,
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