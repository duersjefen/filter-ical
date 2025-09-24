/**
 * Unified App Store
 * Combines all functionality from appStore, calendars, events, filters, and compatibility stores
 * Eliminates cross-store dependencies and simplifies the architecture
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useHTTP } from '../composables/useHTTP'
import { useEventFiltering } from '../composables/useEventFiltering'
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
    // Load calendars from localStorage immediately
    loadCalendarsFromLocalStorage()
    
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

  // localStorage persistence for calendars - dynamic based on username
  const getCalendarsStorageKey = () => `icalViewer_calendars_${getUserId()}`
  
  // Clear anonymous localStorage data when user logs in
  const clearAnonymousLocalStorage = () => {
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith('icalViewer_calendars_anon_') || key === 'icalViewer_calendars_public') {
          localStorage.removeItem(key)
          console.log('🧹 Cleared anonymous localStorage key:', key)
        }
      })
    } catch (error) {
      console.warn('Failed to clear anonymous localStorage:', error)
    }
  }

  const generateLocalCalendarId = () => {
    // Generate a local calendar ID with 'local_' prefix
    return 'local_' + Math.random().toString(36).substring(2, 11)
  }

  const saveCalendarsToLocalStorage = () => {
    try {
      const storageKey = getCalendarsStorageKey()
      localStorage.setItem(storageKey, JSON.stringify(calendars.value))
      console.log(`Calendars saved to ${storageKey}`)
    } catch (error) {
      console.warn('Failed to save calendars to localStorage:', error)
    }
  }

  const loadCalendarsFromLocalStorage = () => {
    try {
      const storageKey = getCalendarsStorageKey()
      const saved = localStorage.getItem(storageKey)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed)) {
          calendars.value = parsed
          console.log(`Calendars loaded from ${storageKey}: ${parsed.length} calendars`)
          return true
        }
      }
      console.log(`No calendars found in ${storageKey}`)
    } catch (error) {
      console.warn('Failed to load calendars from localStorage:', error)
    }
    return false
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
      // LOGGED IN: Load from server only, clear localStorage from any anonymous data
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
          
          // Clear any anonymous localStorage data to prevent confusion
          clearAnonymousLocalStorage()
          
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
      // LOGGED OUT: Use localStorage only, no server sync
      console.log('👤 User is anonymous - using localStorage only')
      
      const hasLocalData = loadCalendarsFromLocalStorage()
      console.log('📦 localStorage data loaded:', { hasLocalData, count: calendars.value.length })
      
      return { 
        success: hasLocalData || calendars.value.length >= 0, 
        data: calendars.value
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

      // Add to calendars and save to localStorage
      calendars.value.push(localCalendar)
      saveCalendarsToLocalStorage()

      // Reset form
      newCalendar.value = { name: '', url: '' }

      console.log('✅ Calendar created locally:', localCalendar)
      return { success: true, data: localCalendar }
    }
  }

  const deleteCalendar = async (calendarId) => {
    // Prevent deletion of domain calendars
    if (calendarId.startsWith('cal_domain_')) {
      return { 
        success: false, 
        error: 'Domain calendars cannot be deleted by users. Please contact your administrator.' 
      }
    }
    
    const currentUserId = getUserId()
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')
    
    const calendarIndex = calendars.value.findIndex(cal => cal.id === calendarId)
    if (calendarIndex === -1) {
      return { success: false, error: 'Calendar not found in local list' }
    }
    
    const calendarToDelete = calendars.value[calendarIndex]
    console.log('🗑️ Deleting calendar:', { calendarId, hasCustomUsername, source: calendarToDelete.source })

    if (hasCustomUsername) {
      // LOGGED IN: Delete from server first, then update local list
      console.log('🔐 User logged in - deleting from server first')
      
      try {
        const result = await del(`/calendars/${calendarId}?username=${currentUserId}`)
        
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
      // LOGGED OUT: Delete from localStorage only
      console.log('👤 User anonymous - deleting locally only')
      
      calendars.value.splice(calendarIndex, 1)
      saveCalendarsToLocalStorage()
      
      console.log('✅ Calendar deleted locally')
      return { success: true }
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
  const selectedRecurringEvents = ref(new Set())
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

  // Create filtering composable with current state
  const eventFiltering = useEventFiltering(events, {
    selectedRecurringEvents,
    keywordFilter,
    dateRange,
    sortBy,
    sortDirection,
    recurringEvents
  })

  // Use filtered events and statistics from the composable
  const filteredEvents = eventFiltering.filteredEvents
  const statistics = eventFiltering.statistics

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
  const toggleRecurringEvent = (recurringEvent) => {
    const types = new Set(selectedRecurringEvents.value)
    if (types.has(recurringEvent)) {
      types.delete(recurringEvent)
    } else {
      types.add(recurringEvent)
    }
    selectedRecurringEvents.value = types
  }

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
    selectedRecurringEvents.value = new Set()
    keywordFilter.value = ''
    dateRange.value = { start: null, end: null }
    sortBy.value = 'date'
    sortDirection.value = 'asc'
  }

  const selectAllRecurringEvents = () => {
    selectedRecurringEvents.value = new Set(Object.keys(recurringEvents.value))
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
      if (result.data.events) {
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
        
      }

      
      console.log('📊 Calendar data loaded:', {
        hasGroups: hasGroups.value,
        groupsCount: Object.keys(groups.value).length
      })
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

  // localStorage key for saved filters
  const getSavedFiltersKey = () => `icalViewer_savedFilters_${getUserId()}`

  const fetchFilters = async () => {
    try {
      const storageKey = getSavedFiltersKey()
      const saved = localStorage.getItem(storageKey)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed)) {
          savedFilters.value = parsed
          console.log(`Loaded ${parsed.length} saved filters from localStorage`)
          return { success: true, data: { filters: parsed } }
        }
      }
      console.log('No saved filters found in localStorage')
      savedFilters.value = []
      return { success: true, data: { filters: [] } }
    } catch (error) {
      console.warn('Failed to load filters from localStorage:', error)
      savedFilters.value = []
      return { success: false, error: 'Failed to load saved filters' }
    }
  }

  const saveFiltersToStorage = () => {
    try {
      const storageKey = getSavedFiltersKey()
      localStorage.setItem(storageKey, JSON.stringify(savedFilters.value))
      console.log(`Saved ${savedFilters.value.length} filters to localStorage`)
    } catch (error) {
      console.warn('Failed to save filters to localStorage:', error)
    }
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
    
    // Save to localStorage
    saveFiltersToStorage()

    return { success: true, data: newFilter }
  }

  const deleteFilter = async (filterId) => {
    const filterIndex = savedFilters.value.findIndex(filter => filter.id === filterId)
    
    if (filterIndex === -1) {
      return { success: false, error: 'Filter not found' }
    }

    // Remove from filters list
    savedFilters.value.splice(filterIndex, 1)
    
    // Save to localStorage
    saveFiltersToStorage()

    return { success: true }
  }

  const createFilterConfig = () => {
    return eventFiltering.createFilterConfig({
      selectedRecurringEvents,
      keywordFilter,
      dateRange,
      sortBy,
      sortDirection
    })
  }

  const loadFilter = (filter) => {
    eventFiltering.applyFilterConfig(filter.config, {
      selectedRecurringEvents,
      keywordFilter,
      dateRange,
      sortBy,
      sortDirection
    })
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
    selectCalendar,
    clearSelection,

    // ===============================================
    // EVENTS & FILTERING
    // ===============================================
    events,
    recurringEvents,
    filteredEvents,
    statistics,
    selectedRecurringEvents,
    keywordFilter,
    dateRange,
    sortBy,
    sortDirection,
    loadCalendarEvents,
    loadCalendarRecurringEvents,
    toggleRecurringEvent,
    setKeywordFilter,
    setDateRange,
    setSorting,
    clearAllFilters,
    selectAllRecurringEvents,

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
    createFilterConfig,
    loadFilter,

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