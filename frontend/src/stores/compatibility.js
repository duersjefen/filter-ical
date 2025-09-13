/**
 * Compatibility Bridge Store
 * Provides the old store interface while delegating to new modular stores
 * This allows gradual migration of components
 */
import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import axios from 'axios'
import { useAppStore } from './appStore'
import { useCalendarStore } from './calendars'
import { useEventsStore } from './events'
import { useFiltersStore } from './filters'
import { useAPI } from '../composables/useAPI'

export const useCompatibilityStore = defineStore('compatibility', () => {
  // Get all the new modular stores
  const appStore = useAppStore()
  const calendarStore = useCalendarStore()
  const eventsStore = useEventsStore()
  const filtersStore = useFiltersStore()

  // API composable for error handling
  const api = useAPI()

  // Local state for form data (compatibility layer)
  const loginForm = reactive({
    username: ''
  })

  // Bridge the old interface to new stores using computed for reactivity
  const user = computed({
    get() { return appStore.user },
    set(value) { appStore.user = value }
  })

  return {
    // App state (reactive delegation) - use computed for reactivity
    // currentView removed - navigation now handled directly by Vue Router
    
    user,

    // Form state (compatibility layer)
    loginForm,

    // Calendar state (reactive delegation) 
    calendars: computed({
      get() { return calendarStore.calendars },
      set(value) { calendarStore.calendars = value }
    }),

    selectedCalendar: computed({
      get() { return calendarStore.selectedCalendar },
      set(value) { calendarStore.selectedCalendar = value }
    }),

    get newCalendar() { return calendarStore.newCalendar },
    set newCalendar(value) { calendarStore.newCalendar = value },

    // Events state (reactive delegation)
    events: computed({
      get() { return eventsStore.events },
      set(value) { eventsStore.events = value }
    }),

    categories: computed({
      get() { return eventsStore.categories },
      set(value) { eventsStore.categories = value }
    }),

    get selectedEventTypes() { return eventsStore.selectedEventTypes },
    set selectedEventTypes(value) { eventsStore.selectedEventTypes = value },

    get keywordFilter() { return eventsStore.keywordFilter },
    set keywordFilter(value) { eventsStore.keywordFilter = value },

    get dateRange() { return eventsStore.dateRange },
    set dateRange(value) { eventsStore.dateRange = value },

    get sortBy() { return eventsStore.sortBy },
    set sortBy(value) { eventsStore.sortBy = value },

    get sortDirection() { return eventsStore.sortDirection },
    set sortDirection(value) { eventsStore.sortDirection = value },

    // Filter state
    get savedFilters() { return filtersStore.savedFilters },
    set savedFilters(value) { filtersStore.savedFilters = value },

    // Combined loading and error states
    get loading() { 
      return calendarStore.loading || eventsStore.loading || filtersStore.loading 
    },
    
    get error() {
      return calendarStore.error || eventsStore.error || filtersStore.error || null
    },

    // Computed properties (delegate to events store)
    isLoggedIn: computed(() => appStore.isLoggedIn),
    filteredEvents: computed(() => eventsStore.filteredEvents),
    statistics: computed(() => eventsStore.statistics),

    // Actions (delegate to appropriate stores)
    async login() { 
      const username = loginForm.username?.trim()
      if (!username) {
        return { success: false, error: 'Please enter a username' }
      }
      const result = await appStore.login(username)
      // Clear the form after successful login
      if (result) {
        loginForm.username = ''
      }
      return result
    },
    logout() { appStore.logout() },

    // viewCalendar method removed - navigation handled directly by components using router

    async fetchCalendars() { 
      // Override calendar store to use proper user headers
      const result = await api.safeExecute(async () => {
        const response = await axios.get('/api/calendars', {
          headers: this.getUserHeaders()
        })
        return response.data.calendars
      })

      if (result.success) {
        calendarStore.calendars = result.data
      }
      
      return result
    },
    async addCalendar() { 
      // Override calendar store to use proper user headers  
      if (!calendarStore.newCalendar.name.trim() || !calendarStore.newCalendar.url.trim()) {
        return { success: false, error: 'Please provide both calendar name and URL' }
      }

      const result = await api.safeExecute(async () => {
        const response = await axios.post('/api/calendars', {
          name: calendarStore.newCalendar.name,
          url: calendarStore.newCalendar.url
        }, {
          headers: this.getUserHeaders()
        })
        return response.data
      })

      if (result.success) {
        // Reset form
        calendarStore.newCalendar.name = ''
        calendarStore.newCalendar.url = ''
        
        // Refresh calendars list
        await this.fetchCalendars()
      }

      return result
    },
    async deleteCalendar(calendarId) { 
      console.log('deleteCalendar called for ID:', calendarId)
      const result = await api.safeExecute(async () => {
        await axios.delete(`/api/calendars/${calendarId}`, {
          headers: this.getUserHeaders()
        })
      })

      console.log('Delete API result:', result)
      if (result.success) {
        console.log('Delete successful, refreshing calendars...')
        // Refresh calendars list
        await this.fetchCalendars()
        console.log('Calendars refreshed, current count:', this.calendars.length)
      }

      return result
    },

    async loadCalendarEvents(calendarId) { return await eventsStore.loadCalendarEvents(calendarId, this.getUserHeaders()) },
    async loadCalendarCategories(calendarId) { return await eventsStore.loadCalendarCategories(calendarId, this.getUserHeaders()) },

    async fetchFilters() { return await filtersStore.fetchFilters() },
    async saveFilter(name = null) {
      const config = filtersStore.createFilterConfig(eventsStore)
      return await filtersStore.saveFilter(name, config)
    },
    async deleteFilter(filterId) { return await filtersStore.deleteFilter(filterId) },

    async loadFilter(filter) {
      filtersStore.applyFilter(filter, eventsStore)
    },

    // App initialization
    initializeApp() {
      return appStore.initializeApp()
    },

    // navigateHome removed - components should use router.push('/home') directly

    // Helper methods
    getUserHeaders() {
      try {
        return { 'x-user-id': appStore.getUserId() }
      } catch (error) {
        // If user not logged in, throw error to force login
        throw new Error('Authentication required - please log in')
      }
    },

    toggleEventType(eventType) { eventsStore.toggleEventType(eventType) },
    updateStatistics() { /* Now computed automatically */ },
    clearAllFilters() { eventsStore.clearAllFilters() },
    selectAllEventTypes() { eventsStore.selectAllEventTypes() },
    clearError() { calendarStore.clearError() },

    // iCal generation - use correct backend endpoint
    async generateIcal(config) {
      const result = await api.safeExecute(async () => {
        const response = await axios.post(`/api/calendar/${config.calendarId}/generate`, {
          selected_categories: config.selectedCategories,
          filter_mode: config.filterMode
        }, {
          headers: this.getUserHeaders(),
          responseType: 'text' // For iCal file content
        })
        return response.data
      })

      return result
    }
  }
})