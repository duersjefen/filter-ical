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
    
    // Enhanced filtering state
    keywordFilter: '',
    dateRange: { start: null, end: null },
    sortBy: 'date', // 'date', 'title', 'matches'
    sortDirection: 'asc',
    
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
      let filtered = state.events
      
      // Event type filtering (if any types selected)
      if (state.selectedEventTypes.size > 0) {
        filtered = filtered.filter(event => 
          state.selectedEventTypes.has(event.summary)
        )
      }
      
      // Keyword filtering
      if (state.keywordFilter.trim()) {
        const keyword = state.keywordFilter.toLowerCase()
        filtered = filtered.filter(event => {
          const searchText = `${event.summary} ${event.description || ''} ${event.location || ''}`.toLowerCase()
          return searchText.includes(keyword)
        })
      }
      
      // Date range filtering
      if (state.dateRange.start || state.dateRange.end) {
        filtered = filtered.filter(event => {
          const eventDate = new Date(event.dtstart)
          if (state.dateRange.start && eventDate < state.dateRange.start) return false
          if (state.dateRange.end && eventDate > state.dateRange.end) return false
          return true
        })
      }
      
      // Sorting
      if (state.sortBy === 'date') {
        filtered.sort((a, b) => {
          const dateA = new Date(a.dtstart)
          const dateB = new Date(b.dtstart)
          return state.sortDirection === 'asc' ? dateA - dateB : dateB - dateA
        })
      } else if (state.sortBy === 'title') {
        filtered.sort((a, b) => {
          const comparison = a.summary.localeCompare(b.summary)
          return state.sortDirection === 'asc' ? comparison : -comparison
        })
      }
      
      return filtered
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
      this.keywordFilter = ''
      this.dateRange = { start: null, end: null }
    },

    setQuickFilter(eventTypes) {
      this.selectedEventTypes = new Set(eventTypes)
    },

    // Timeframe filtering helpers
    setTimeframe(period) {
      const now = new Date()
      const start = new Date(now)
      const end = new Date(now)
      
      switch (period) {
        case 'week':
          start.setDate(now.getDate() - now.getDay()) // Start of week
          end.setDate(start.getDate() + 6) // End of week
          break
        case 'month':
          start.setDate(1) // Start of month
          end.setMonth(now.getMonth() + 1, 0) // End of month
          break
        case 'year':
          start.setMonth(0, 1) // Start of year
          end.setMonth(11, 31) // End of year
          break
      }
      
      this.dateRange = { start, end }
    },

    clearTimeframe() {
      this.dateRange = { start: null, end: null }
    },

    toggleSortDirection() {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
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

    async saveFilter(name = null) {
      try {
        this.loading = true
        const filterName = name || `Filter ${this.selectedEventTypes.size} types`
        const config = {
          selectedEventTypes: Array.from(this.selectedEventTypes),
          keywordFilter: this.keywordFilter,
          dateRange: this.dateRange,
          sortBy: this.sortBy,
          sortDirection: this.sortDirection
        }
        
        await axios.post('/api/filters', {
          name: filterName,
          config: config
        }, {
          headers: this.getUserHeaders()
        })
        await this.fetchFilters()
      } catch (error) {
        this.error = error.response?.data?.message || 'Error saving filter'
      } finally {
        this.loading = false
      }
    },

    async deleteFilter(filterId) {
      try {
        this.loading = true
        await axios.delete(`/api/filters/${filterId}`, {
          headers: this.getUserHeaders()
        })
        await this.fetchFilters()
      } catch (error) {
        this.error = error.response?.data?.message || 'Error deleting filter'
      } finally {
        this.loading = false
      }
    },

    async loadFilter(filter) {
      const config = filter.config
      this.selectedEventTypes = new Set(config.selectedEventTypes || [])
      this.keywordFilter = config.keywordFilter || ''
      this.dateRange = config.dateRange || { start: null, end: null }
      this.sortBy = config.sortBy || 'date'
      this.sortDirection = config.sortDirection || 'asc'
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