/**
 * Unified App Store
 * Combines all functionality from appStore, calendars, events, filters, and compatibility stores
 * Eliminates cross-store dependencies and simplifies the architecture
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApiCall } from '../composables/useApiCall'
import { useEventFiltering } from '../composables/useEventFiltering'
import { useUsername } from '../composables/useUsername'

export const useAppStore = defineStore('app', () => {
  // ===============================================
  // USERNAME & API INTEGRATION
  // ===============================================
  
  const { getUserId, onUsernameChange } = useUsername()
  const { get, post, put, del, loading, error, clearError, setError } = useApiCall()

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
        console.log('🌐 Making API call to /api/calendars?username=' + currentUserId)
        const result = await get(`/api/calendars?username=${currentUserId}`)
        console.log('🌐 Server API result:', { 
          success: result.success, 
          calendarsLength: result.data?.calendars?.length || 0
        })
        
        if (result.success) {
          calendars.value = result.data.calendars || []
          
          console.log('✅ Server calendars loaded:', { 
            length: calendars.value.length,
            firstCalendarName: calendars.value[0]?.name
          })
          
          // Clear any anonymous localStorage data to prevent confusion
          clearAnonymousLocalStorage()
          
          return result
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
        data: { calendars: calendars.value }
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
      url: newCalendar.value.url.trim()
    }

    console.log('📅 Adding calendar:', { calendarData, hasCustomUsername })

    if (hasCustomUsername) {
      // LOGGED IN: Create on server immediately, wait for response
      console.log('🔐 User logged in - creating calendar on server')
      
      try {
        const result = await post(`/api/calendars?username=${currentUserId}`, calendarData)
        
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
        const result = await del(`/api/calendars/${calendarId}?username=${currentUserId}`)
        
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
  const eventTypes = ref({})
  
  // Event filtering state
  const selectedEventTypes = ref(new Set())
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
  const ungroupedEventTypes = ref([])
  const selectedGroups = ref(new Set())
  const selectedEvents = ref(new Set()) // Individual event selections

  // Create filtering composable with current state
  const eventFiltering = useEventFiltering(events, {
    selectedEventTypes,
    keywordFilter,
    dateRange,
    sortBy,
    sortDirection,
    eventTypes
  })

  // Use filtered events and statistics from the composable
  const filteredEvents = eventFiltering.filteredEvents
  const statistics = eventFiltering.statistics

  const loadCalendarEvents = async (calendarId) => {
    const result = await get(`/api/calendar/${calendarId}/events`)

    if (result.success) {
      events.value = result.data.events
    }

    return result
  }

  const loadCalendarEventTypes = async (calendarId) => {
    const result = await get(`/api/calendar/${calendarId}/event_types`)

    if (result.success) {
      eventTypes.value = result.data.event_types
    }

    return result
  }

  // Event filtering methods
  const toggleEventType = (eventType) => {
    const types = new Set(selectedEventTypes.value)
    if (types.has(eventType)) {
      types.delete(eventType)
    } else {
      types.add(eventType)
    }
    selectedEventTypes.value = types
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
    selectedEventTypes.value = new Set()
    keywordFilter.value = ''
    dateRange.value = { start: null, end: null }
    sortBy.value = 'date'
    sortDirection.value = 'asc'
  }

  const selectAllEventTypes = () => {
    selectedEventTypes.value = new Set(Object.keys(eventTypes.value))
  }

  // Groups methods
  const loadCalendarGroups = async (calendarId) => {
    const result = await get(`/api/calendar/${calendarId}/groups`)

    if (result.success) {
      hasGroups.value = result.data.has_groups
      groups.value = result.data.groups || {}
      ungroupedEventTypes.value = result.data.ungrouped_event_types || []

      // Reset selections when loading new calendar
      selectedGroups.value = new Set()
      
      console.log('📊 Groups data loaded:', {
        hasGroups: hasGroups.value,
        groupsCount: Object.keys(groups.value).length,
        ungroupedEventTypesCount: ungroupedEventTypes.value.length
      })
    }

    return result
  }

  const toggleGroup = (groupId) => {
    const newGroups = new Set(selectedGroups.value)

    if (newGroups.has(groupId)) {
      newGroups.delete(groupId)
    } else {
      newGroups.add(groupId)
    }

    selectedGroups.value = newGroups
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
    const filterName = name || `Filter ${config.selectedEventTypes?.length || 0} types`
    
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
      selectedEventTypes,
      keywordFilter,
      dateRange,
      sortBy,
      sortDirection
    })
  }

  const loadFilter = (filter) => {
    eventFiltering.applyFilterConfig(filter.config, {
      selectedEventTypes,
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
    const result = await get(`/api/filtered-calendars?username=${getUserId()}`)
    
    if (result.success) {
      filteredCalendars.value = result.data.filtered_calendars
    }
    
    return result
  }

  const createFilteredCalendar = async (sourceCalendarId, name, filterConfig) => {
    if (!name?.trim()) {
      return { success: false, error: 'Name is required' }
    }

    const result = await post(`/api/filtered-calendars?username=${getUserId()}`, {
      source_calendar_id: sourceCalendarId,
      name: name.trim(),
      filter_config: filterConfig
    })
    
    if (result.success) {
      // Refresh filtered calendars list
      await loadFilteredCalendars()
    }
    
    return result
  }

  const updateFilteredCalendar = async (calendarId, updates) => {
    if (!calendarId) {
      return { success: false, error: 'Calendar ID is required' }
    }

    const result = await put(`/api/filtered-calendars/${calendarId}?username=${getUserId()}`, updates)
    
    if (result.success) {
      // Refresh filtered calendars list
      await loadFilteredCalendars()
    }
    
    return result
  }

  const deleteFilteredCalendar = async (calendarId) => {
    if (!calendarId) {
      return { success: false, error: 'Calendar ID is required' }
    }

    const result = await del(`/api/filtered-calendars/${calendarId}?username=${getUserId()}`)
    
    if (result.success) {
      // Refresh filtered calendars list
      await loadFilteredCalendars()
    }
    
    return result
  }

  // ===============================================
  // USER PREFERENCES SECTION
  // ===============================================
  
  const getUserPreferences = async () => {
    return await get('/api/user/preferences')
  }

  const saveUserPreferences = async (preferences) => {
    return await put('/api/user/preferences', preferences)
  }

  const getCalendarPreferences = async (calendarId) => {
    return await get(`/api/calendars/${calendarId}/preferences`)
  }

  const saveCalendarPreferences = async (calendarId, preferences) => {
    return await put(`/api/calendars/${calendarId}/preferences`, preferences)
  }

  // ===============================================
  // ICAL GENERATION SECTION
  // ===============================================
  
  const generateIcal = async ({ calendarId, selectedEventTypes, filterMode }) => {
    return await post(`/api/calendar/${calendarId}/generate`, {
      selected_groups: Array.from(selectedGroups.value),
      selected_events: Array.from(selectedEvents.value),
      selected_event_types: selectedEventTypes || [], // Backward compatibility
      filter_mode: filterMode
    })
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
    eventTypes,
    filteredEvents,
    statistics,
    selectedEventTypes,
    keywordFilter,
    dateRange,
    sortBy,
    sortDirection,
    loadCalendarEvents,
    loadCalendarEventTypes,
    toggleEventType,
    setKeywordFilter,
    setDateRange,
    setSorting,
    clearAllFilters,
    selectAllEventTypes,

    // ===============================================
    // GROUPS
    // ===============================================
    groups,
    hasGroups,
    ungroupedEventTypes,
    selectedGroups,
    loadCalendarGroups,
    toggleGroup,

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