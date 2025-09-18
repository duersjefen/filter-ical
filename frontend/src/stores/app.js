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
  
  const { getUserId } = useUsername()
  const { get, post, put, del, loading, error, clearError } = useApiCall()

  // ===============================================
  // PUBLIC ACCESS - NO AUTHENTICATION REQUIRED
  // ===============================================
  
  const initializeApp = () => {
    // Load calendars from localStorage immediately
    loadCalendarsFromLocalStorage()
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
    console.log('🔄 fetchCalendars called')
    
    // Load from localStorage first for immediate display
    const hasLocalData = loadCalendarsFromLocalStorage()
    console.log('📦 localStorage data loaded:', { hasLocalData, count: calendars.value.length })
    
    // Try to sync with API in background
    try {
      console.log('🌐 Making API call to /api/calendars?username=' + getUserId())
      const result = await get(`/api/calendars?username=${getUserId()}`)
      console.log('🌐 API result received:', { 
        success: result.success, 
        dataType: typeof result.data,
        dataKeys: result.data ? Object.keys(result.data) : 'null',
        calendarsProperty: result.data?.calendars,
        calendarsLength: result.data?.calendars?.length
      })
      
      if (result.success) {
        // Merge local and server data, preferring server data for conflicts
        const serverCalendars = result.data.calendars
        const localCalendars = calendars.value
        
        console.log('📊 Data comparison:', {
          serverCalendarsLength: serverCalendars?.length || 0,
          localCalendarsLength: localCalendars.length,
          serverCalendarsType: typeof serverCalendars,
          serverCalendarsArray: Array.isArray(serverCalendars)
        })
        
        // For now, just use server data if available, fall back to local
        calendars.value = serverCalendars.length > 0 ? serverCalendars : localCalendars
        
        console.log('✅ Final calendars.value set:', { 
          length: calendars.value.length,
          firstCalendarId: calendars.value[0]?.id,
          firstCalendarName: calendars.value[0]?.name
        })
        
        // Save updated calendars to localStorage
        saveCalendarsToLocalStorage()
        
        return result
      }
    } catch (error) {
      console.warn('API sync failed, using localStorage data:', error)
    }
    
    // Return success if we have local data, even if API failed
    console.log('📤 Returning fallback result:', { hasLocalData, calendarsLength: calendars.value.length })
    return { 
      success: hasLocalData || calendars.value.length > 0, 
      data: { calendars: calendars.value }
    }
  }

  const addCalendar = async () => {
    if (!newCalendar.value.name.trim() || !newCalendar.value.url.trim()) {
      return { success: false, error: 'Please provide both calendar name and URL' }
    }

    // Create calendar object for localStorage
    const localCalendar = {
      id: generateLocalCalendarId(),
      name: newCalendar.value.name.trim(),
      url: newCalendar.value.url.trim(),
      user_id: getUserId(), // Use current username
      created_at: new Date().toISOString(),
      source: 'local' // Mark as locally created
    }

    // Add to local storage immediately for instant feedback
    calendars.value.push(localCalendar)
    saveCalendarsToLocalStorage()

    // Reset form immediately
    newCalendar.value = {
      name: '',
      url: ''
    }

    // Try to sync with API in background
    try {
      const result = await post(`/api/calendars?username=${getUserId()}`, {
        name: localCalendar.name,
        url: localCalendar.url
      })

      if (result.success) {
        // Replace local calendar with server calendar
        const serverCalendar = result.data
        const localIndex = calendars.value.findIndex(cal => cal.id === localCalendar.id)
        if (localIndex !== -1) {
          calendars.value[localIndex] = {
            ...serverCalendar,
            source: 'server' // Mark as server synced
          }
          saveCalendarsToLocalStorage()
        }
      }
    } catch (error) {
      console.warn('Failed to sync calendar with server, keeping local copy:', error)
    }

    return { success: true, data: localCalendar }
  }

  const deleteCalendar = async (calendarId) => {
    // Remove from localStorage immediately for instant feedback
    const calendarIndex = calendars.value.findIndex(cal => cal.id === calendarId)
    let deletedCalendar = null
    
    if (calendarIndex !== -1) {
      deletedCalendar = calendars.value[calendarIndex]
      calendars.value.splice(calendarIndex, 1)
      saveCalendarsToLocalStorage()
    }

    // Try to delete from server in background
    try {
      await del(`/api/calendars/${calendarId}?username=${getUserId()}`)
      // If server deletion succeeds, return success
      return { success: true }
    } catch (error) {
      // If server deletion fails but it was a local calendar, that's OK
      if (deletedCalendar?.source === 'local') {
        console.log('Local calendar deleted successfully (no server sync needed)')
        return { success: true }
      } else {
        // If server deletion failed for a server calendar, restore it
        console.warn('Failed to delete calendar from server, restoring locally:', error)
        if (deletedCalendar && calendarIndex !== -1) {
          calendars.value.splice(calendarIndex, 0, deletedCalendar)
          saveCalendarsToLocalStorage()
        }
        return { success: false, error: 'Failed to delete calendar from server' }
      }
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
      groups.value = result.data.groups

      // Reset selections when loading new calendar
      selectedGroups.value = new Set()
      selectedEvents.value = new Set()
    }

    return result
  }

  const toggleGroup = (groupId) => {
    const newGroups = new Set(selectedGroups.value)

    if (newGroups.has(groupId)) {
      newGroups.delete(groupId)
      // Remove all events from this group from individual selections
      const groupEvents = groups.value[groupId]?.events || []
      const newEvents = new Set(selectedEvents.value)
      groupEvents.forEach(event => newEvents.delete(event.id))
      selectedEvents.value = newEvents
    } else {
      newGroups.add(groupId)
      // Auto-add all events from this group
      const groupEvents = groups.value[groupId]?.events || []
      const newEvents = new Set(selectedEvents.value)
      groupEvents.forEach(event => newEvents.add(event.id))
      selectedEvents.value = newEvents
    }

    selectedGroups.value = newGroups
  }

  const toggleEvent = (eventId) => {
    const newEvents = new Set(selectedEvents.value)

    if (newEvents.has(eventId)) {
      newEvents.delete(eventId)
    } else {
      newEvents.add(eventId)
    }

    selectedEvents.value = newEvents
  }

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
    selectedGroups,
    selectedEvents,
    loadCalendarGroups,
    toggleGroup,
    toggleEvent,

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
    clearError
  }
})