/**
 * Unified App Store
 * Combines all functionality from appStore, calendars, events, filters, and compatibility stores
 * Eliminates cross-store dependencies and simplifies the architecture
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApiCall } from '../composables/useApiCall'
import { useEventFiltering } from '../composables/useEventFiltering'

export const useAppStore = defineStore('app', () => {
  // ===============================================
  // API Helper - Reusable across all sections
  // ===============================================
  
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

  // localStorage persistence for calendars
  const CALENDARS_STORAGE_KEY = 'icalViewer_calendars'

  const generateLocalCalendarId = () => {
    // Generate a local calendar ID with 'local_' prefix
    return 'local_' + Math.random().toString(36).substring(2, 11)
  }

  const saveCalendarsToLocalStorage = () => {
    try {
      localStorage.setItem(CALENDARS_STORAGE_KEY, JSON.stringify(calendars.value))
    } catch (error) {
      console.warn('Failed to save calendars to localStorage:', error)
    }
  }

  const loadCalendarsFromLocalStorage = () => {
    try {
      const saved = localStorage.getItem(CALENDARS_STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed)) {
          calendars.value = parsed
          return true
        }
      }
    } catch (error) {
      console.warn('Failed to load calendars from localStorage:', error)
    }
    return false
  }

  const fetchCalendars = async () => {
    // Load from localStorage first for immediate display
    const hasLocalData = loadCalendarsFromLocalStorage()
    
    // Try to sync with API in background
    try {
      const result = await get('/api/calendars')
      
      if (result.success) {
        // Merge local and server data, preferring server data for conflicts
        const serverCalendars = result.data.calendars
        const localCalendars = calendars.value
        
        // For now, just use server data if available, fall back to local
        calendars.value = serverCalendars.length > 0 ? serverCalendars : localCalendars
        
        // Save updated calendars to localStorage
        saveCalendarsToLocalStorage()
        
        return result
      }
    } catch (error) {
      console.warn('API sync failed, using localStorage data:', error)
    }
    
    // Return success if we have local data, even if API failed
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
      user_id: 'public', // Always public in no-auth system
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
      const result = await post('/api/calendars', {
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
      await del(`/api/calendars/${calendarId}`)
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
  const categories = ref({})
  
  // Event filtering state
  const selectedEventTypes = ref(new Set())
  const keywordFilter = ref('')
  const dateRange = ref({
    start: null,
    end: null
  })
  const sortBy = ref('date')
  const sortDirection = ref('asc')

  // Create filtering composable with current state
  const eventFiltering = useEventFiltering(events, {
    selectedEventTypes,
    keywordFilter,
    dateRange,
    sortBy,
    sortDirection,
    categories
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

  const loadCalendarCategories = async (calendarId) => {
    const result = await get(`/api/calendar/${calendarId}/categories`)

    if (result.success) {
      categories.value = result.data.categories
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
    selectedEventTypes.value = new Set(Object.keys(categories.value))
  }

  // ===============================================
  // SAVED FILTERS SECTION
  // ===============================================
  
  const savedFilters = ref([])

  const fetchFilters = async () => {
    const result = await get('/api/filters', )

    if (result.success) {
      savedFilters.value = result.data.filters
    }

    return result
  }

  const saveFilter = async (name, config) => {
    const filterName = name || `Filter ${config.selectedEventTypes?.length || 0} types`
    
    const result = await post('/api/filters', {
      name: filterName,
      config: config
    }, )

    if (result.success) {
      // Refresh filters list
      await fetchFilters()
    }

    return result
  }

  const deleteFilter = async (filterId) => {
    const result = await del(`/api/filters/${filterId}`, )

    if (result.success) {
      // Refresh filters list
      await fetchFilters()
    }

    return result
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
    const result = await get('/api/filtered-calendars', )
    
    if (result.success) {
      filteredCalendars.value = result.data.filtered_calendars
    }
    
    return result
  }

  const createFilteredCalendar = async (sourceCalendarId, name, filterConfig) => {
    if (!name?.trim()) {
      return { success: false, error: 'Name is required' }
    }

    const result = await post('/api/filtered-calendars', {
      source_calendar_id: sourceCalendarId,
      name: name.trim(),
      filter_config: filterConfig
    }, )
    
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

    const result = await put(`/api/filtered-calendars/${calendarId}`, updates, )
    
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

    const result = await del(`/api/filtered-calendars/${calendarId}`, )
    
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
  
  const generateIcal = async (calendarId, selectedCategories, filterMode) => {
    return await post(`/api/calendar/${calendarId}/generate`, {
      selected_categories: selectedCategories,
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
    categories,
    filteredEvents,
    statistics,
    selectedEventTypes,
    keywordFilter,
    dateRange,
    sortBy,
    sortDirection,
    loadCalendarEvents,
    loadCalendarCategories,
    toggleEventType,
    setKeywordFilter,
    setDateRange,
    setSorting,
    clearAllFilters,
    selectAllEventTypes,

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