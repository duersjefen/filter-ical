import { defineStore } from 'pinia'
import axios from 'axios'

export const useAppStore = defineStore('app', {
  state: () => ({
    // User state
    user: {
      username: null,
      loggedIn: false
    },
    
    // Navigation
    currentView: 'login',
    
    // Data
    calendars: [],
    events: [],
    filters: [],
    
    // Selected state
    selectedCalendar: null,
    selectedEventTypes: new Set(),
    
    // UI state
    loading: false,
    error: null,
    
    // Form state
    loginForm: {
      username: ''
    },
    newCalendar: {
      name: '',
      url: ''
    },
    
    // Statistics
    statistics: {
      totalEvents: 0,
      eventTypes: 0,
      yearsCovered: 0
    }
  }),

  getters: {
    isLoggedIn: (state) => state.user.loggedIn,
    filteredEvents: (state) => {
      if (state.selectedEventTypes.size === 0) {
        return state.events
      }
      return state.events.filter(event => 
        state.selectedEventTypes.has(event.summary)
      )
    },
    groupedEvents: (state) => {
      const grouped = {}
      state.events.forEach(event => {
        if (!grouped[event.summary]) {
          grouped[event.summary] = []
        }
        grouped[event.summary].push(event)
      })
      return grouped
    },
    eventTypes: (state) => {
      return [...new Set(state.events.map(event => event.summary))].sort()
    }
  },

  actions: {
    // Initialize app
    initializeApp() {
      const storedUser = this.loadUserFromStorage()
      if (storedUser && storedUser.loggedIn) {
        this.user = storedUser
        this.currentView = 'home'
      }
    },

    // Local storage helpers
    loadUserFromStorage() {
      try {
        const stored = localStorage.getItem('ical-viewer-user')
        return stored ? JSON.parse(stored) : null
      } catch (e) {
        console.error('Error loading user from storage:', e)
        localStorage.removeItem('ical-viewer-user')
        return null
      }
    },

    saveUserToStorage() {
      if (this.user.loggedIn) {
        localStorage.setItem('ical-viewer-user', JSON.stringify(this.user))
      }
    },

    clearUserFromStorage() {
      localStorage.removeItem('ical-viewer-user')
    },

    // API helpers
    getUserHeaders() {
      return {
        'X-User-ID': this.user.username || 'anonymous'
      }
    },

    // Auth actions
    async login() {
      const username = this.loginForm.username.trim()
      if (!username) {
        this.error = 'Please enter a username'
        return
      }

      this.user = {
        username,
        loggedIn: true
      }
      
      this.saveUserToStorage()
      this.currentView = 'home'
      this.loginForm.username = ''
      this.error = null
      
      await this.fetchCalendars()
    },

    logout() {
      this.clearUserFromStorage()
      this.user = { username: null, loggedIn: false }
      this.currentView = 'login'
      this.calendars = []
      this.events = []
      this.filters = []
      this.selectedCalendar = null
      this.selectedEventTypes.clear()
      this.loginForm.username = ''
    },

    // Navigation
    navigateHome() {
      this.currentView = 'home'
      this.selectedCalendar = null
      this.events = []
      this.selectedEventTypes.clear()
      this.fetchCalendars()
    },

    async viewCalendar(calendarId) {
      const calendar = this.calendars.find(c => c.id === calendarId)
      if (!calendar) return

      this.selectedCalendar = calendar
      this.currentView = 'calendar'
      this.loading = true
      
      await this.loadCalendarEvents(calendarId)
    },

    // API calls
    async fetchCalendars() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/calendars', {
          headers: this.getUserHeaders()
        })
        this.calendars = response.data.calendars
      } catch (error) {
        this.error = error.response?.data?.message || 'Error loading calendars'
      } finally {
        this.loading = false
      }
    },

    async addCalendar() {
      if (!this.newCalendar.name.trim() || !this.newCalendar.url.trim()) {
        this.error = 'Please provide both calendar name and URL'
        return
      }

      this.loading = true
      this.error = null

      try {
        await axios.post('/api/calendars', {
          name: this.newCalendar.name,
          url: this.newCalendar.url
        }, {
          headers: this.getUserHeaders()
        })
        
        this.newCalendar = { name: '', url: '' }
        await this.fetchCalendars()
      } catch (error) {
        this.error = error.response?.data?.message || 'Error adding calendar'
      } finally {
        this.loading = false
      }
    },

    async deleteCalendar(calendarId) {
      this.loading = true
      this.error = null

      try {
        await axios.delete(`/api/calendars/${calendarId}`, {
          headers: this.getUserHeaders()
        })
        
        await this.fetchCalendars()
      } catch (error) {
        this.error = error.response?.data?.message || 'Error deleting calendar'
      } finally {
        this.loading = false
      }
    },

    async loadCalendarEvents(calendarId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`/api/calendar/${calendarId}/events`, {
          headers: this.getUserHeaders()
        })
        
        this.events = response.data.events
        this.updateStatistics()
      } catch (error) {
        this.error = error.response?.data?.message || 'Error loading events'
      } finally {
        this.loading = false
      }
    },

    // Statistics
    updateStatistics() {
      const events = this.events
      const groupedEvents = this.groupedEvents
      const years = new Set()
      
      events.forEach(event => {
        if (event.dtstart && event.dtstart.length >= 4) {
          years.add(event.dtstart.substring(0, 4))
        }
      })

      this.statistics = {
        totalEvents: events.length,
        eventTypes: Object.keys(groupedEvents).length,
        yearsCovered: years.size
      }
    },

    // Event filtering
    toggleEventType(eventType) {
      if (this.selectedEventTypes.has(eventType)) {
        this.selectedEventTypes.delete(eventType)
      } else {
        this.selectedEventTypes.add(eventType)
      }
    },

    clearFilters() {
      this.selectedEventTypes.clear()
    },

    setQuickFilter(eventTypes) {
      this.selectedEventTypes = new Set(eventTypes)
    },

    // Filters API (basic implementation)
    async fetchFilters() {
      try {
        const response = await axios.get('/api/filters', {
          headers: this.getUserHeaders()
        })
        this.filters = response.data.filters
      } catch (error) {
        console.error('Error loading filters:', error)
      }
    },

    async saveFilter() {
      if (this.selectedEventTypes.size === 0) return

      try {
        await axios.post('/api/filters', {
          calendar_id: this.selectedCalendar?.id,
          name: `Filter ${this.selectedEventTypes.size} types`,
          types: Array.from(this.selectedEventTypes)
        }, {
          headers: this.getUserHeaders()
        })
        
        await this.fetchFilters()
      } catch (error) {
        this.error = error.response?.data?.message || 'Error saving filter'
      }
    },

    // UI helpers
    setLoading(loading) {
      this.loading = loading
    },

    setError(error) {
      this.error = error
    },

    clearError() {
      this.error = null
    }
  }
})