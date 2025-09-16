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
  // USER AUTHENTICATION SECTION
  // ===============================================
  
  const user = ref({
    username: null,
    loggedIn: false,
    loginTime: null,
    lastActivity: null
  })

  const isLoggedIn = computed(() => user.value.loggedIn)

  const getUserHeaders = () => {
    // Optional authentication - provide user ID if available
    if (user.value.loggedIn && user.value.username) {
      return { 'x-user-id': user.value.username }
    }
    return {}
  }

  const login = async (username) => {
    if (!username || username.trim() === '' || username.trim().toLowerCase() === 'anonymous') {
      throw new Error('Please enter a valid username')
    }
    
    const userData = {
      username: username.trim(),
      loggedIn: true,
      loginTime: new Date().getTime(),
      lastActivity: new Date().getTime()
    }
    
    user.value = userData
    localStorage.setItem('icalViewer_user', JSON.stringify(userData))
    
    return { success: true, data: userData }
  }

  const logout = () => {
    user.value = {
      username: null,
      loggedIn: false,
      loginTime: null,
      lastActivity: null
    }
    localStorage.removeItem('icalViewer_user')
  }

  const initializeApp = () => {
    try {
      const savedUser = localStorage.getItem('icalViewer_user')
      if (savedUser) {
        const parsed = JSON.parse(savedUser)
        
        if (parsed && parsed.username && parsed.loggedIn) {
          const now = new Date().getTime()
          const sessionAge = now - (parsed.loginTime || now)
          const maxSessionAge = 7 * 24 * 60 * 60 * 1000 // 7 days
          
          if (sessionAge < maxSessionAge) {
            parsed.lastActivity = now
            user.value = parsed
            localStorage.setItem('icalViewer_user', JSON.stringify(parsed))
            return true
          } else {
            logout()
            return false
          }
        }
      }
    } catch (error) {
      console.warn('Error loading saved user:', error)
      logout()
    }
    return false
  }

  const updateActivity = () => {
    if (user.value.loggedIn) {
      user.value.lastActivity = new Date().getTime()
      localStorage.setItem('icalViewer_user', JSON.stringify(user.value))
    }
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

  const fetchCalendars = async () => {
    const result = await get('/api/calendars', getUserHeaders())
    
    if (result.success) {
      calendars.value = result.data.calendars
    }
    
    return result
  }

  const addCalendar = async () => {
    if (!newCalendar.value.name.trim() || !newCalendar.value.url.trim()) {
      return { success: false, error: 'Please provide both calendar name and URL' }
    }

    const result = await post('/api/calendars', {
      name: newCalendar.value.name,
      url: newCalendar.value.url
    }, getUserHeaders())

    if (result.success) {
      // Reset form
      newCalendar.value = {
        name: '',
        url: ''
      }
      
      // Refresh calendars list
      await fetchCalendars()
    }

    return result
  }

  const deleteCalendar = async (calendarId) => {
    const result = await del(`/api/calendars/${calendarId}`, getUserHeaders())

    if (result.success) {
      // Refresh calendars list
      await fetchCalendars()
    }

    return result
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
    const result = await get(`/api/calendar/${calendarId}/events`, getUserHeaders())

    if (result.success) {
      events.value = result.data.events
    }

    return result
  }

  const loadCalendarCategories = async (calendarId) => {
    const result = await get(`/api/calendar/${calendarId}/categories`, getUserHeaders())

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
    const result = await get('/api/filters', getUserHeaders())

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
    }, getUserHeaders())

    if (result.success) {
      // Refresh filters list
      await fetchFilters()
    }

    return result
  }

  const deleteFilter = async (filterId) => {
    const result = await del(`/api/filters/${filterId}`, getUserHeaders())

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
    const result = await get('/api/filtered-calendars', getUserHeaders())
    
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
    }, getUserHeaders())
    
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

    const result = await put(`/api/filtered-calendars/${calendarId}`, updates, getUserHeaders())
    
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

    const result = await del(`/api/filtered-calendars/${calendarId}`, getUserHeaders())
    
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
    return await get('/api/user/preferences', getUserHeaders())
  }

  const saveUserPreferences = async (preferences) => {
    return await put('/api/user/preferences', preferences, getUserHeaders())
  }

  const getCalendarPreferences = async (calendarId) => {
    return await get(`/api/calendars/${calendarId}/preferences`, getUserHeaders())
  }

  const saveCalendarPreferences = async (calendarId, preferences) => {
    return await put(`/api/calendars/${calendarId}/preferences`, preferences, getUserHeaders())
  }

  // ===============================================
  // ICAL GENERATION SECTION
  // ===============================================
  
  const generateIcal = async (calendarId, selectedCategories, filterMode) => {
    return await post(`/api/calendar/${calendarId}/generate`, {
      selected_categories: selectedCategories,
      filter_mode: filterMode
    }, getUserHeaders())
  }

  // ===============================================
  // COMPATIBILITY LAYER METHODS
  // ===============================================
  
  // Login form state for compatibility
  const loginForm = ref({
    username: ''
  })

  // Compatibility login method that uses form state
  const loginWithForm = async () => {
    const username = loginForm.value.username?.trim()
    if (!username) {
      return { success: false, error: 'Please enter a username' }
    }
    const result = await login(username)
    if (result.success) {
      loginForm.value.username = ''
    }
    return result
  }

  // Utility method compatibility
  const setError = (errorMessage) => {
    // The error is automatically set by the useApiCall composable
    // This method exists for compatibility with components
  }

  return {
    // ===============================================
    // USER AUTHENTICATION
    // ===============================================
    user,
    isLoggedIn,
    login: loginWithForm, // Form-aware login method
    logout,
    initializeApp,
    updateActivity,
    loginForm,

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
    clearError,
    setError
  }
})