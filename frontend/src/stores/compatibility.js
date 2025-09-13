/**
 * Compatibility Bridge Store
 * Provides the old store interface while delegating to new modular stores
 * This allows gradual migration of components
 */
import { defineStore } from 'pinia'
import { computed } from 'vue'
import { useAppStore } from './app'
import { useCalendarStore } from './calendars'
import { useEventsStore } from './events'
import { useFiltersStore } from './filters'

export const useCompatibilityStore = defineStore('compatibility', () => {
  // Get all the new modular stores
  const appStore = useAppStore()
  const calendarStore = useCalendarStore()
  const eventsStore = useEventsStore()
  const filtersStore = useFiltersStore()

  // Bridge the old interface to new stores
  return {
    // App state (direct delegation)
    get currentView() { return appStore.currentView },
    set currentView(value) { appStore.currentView = value },
    
    get user() { return appStore.user },
    set user(value) { appStore.user = value },

    // Calendar state (direct delegation)
    get calendars() { return calendarStore.calendars },
    set calendars(value) { calendarStore.calendars = value },

    get selectedCalendar() { return calendarStore.selectedCalendar },
    set selectedCalendar(value) { calendarStore.selectedCalendar = value },

    get newCalendar() { return calendarStore.newCalendar },
    set newCalendar(value) { calendarStore.newCalendar = value },

    // Events state (direct delegation)
    get events() { return eventsStore.events },
    set events(value) { eventsStore.events = value },

    get categories() { return eventsStore.categories },
    set categories(value) { eventsStore.categories = value },

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
    async login() { return await appStore.login() },
    logout() { appStore.logout() },

    async viewCalendar(calendarId) {
      const calendar = calendarStore.calendars.find(c => c.id === calendarId)
      if (!calendar) return

      calendarStore.selectCalendar(calendar)
      appStore.setView('calendar')
      
      await eventsStore.loadCalendarEvents(calendarId)
      await eventsStore.loadCalendarCategories(calendarId)
    },

    async fetchCalendars() { return await calendarStore.fetchCalendars() },
    async addCalendar() { return await calendarStore.addCalendar() },
    async deleteCalendar(calendarId) { return await calendarStore.deleteCalendar(calendarId) },

    async loadCalendarEvents(calendarId) { return await eventsStore.loadCalendarEvents(calendarId) },
    async loadCalendarCategories(calendarId) { return await eventsStore.loadCalendarCategories(calendarId) },

    async fetchFilters() { return await filtersStore.fetchFilters() },
    async saveFilter(name = null) {
      const config = filtersStore.createFilterConfig(eventsStore)
      return await filtersStore.saveFilter(name, config)
    },
    async deleteFilter(filterId) { return await filtersStore.deleteFilter(filterId) },

    async loadFilter(filter) {
      filtersStore.applyFilter(filter, eventsStore)
    },

    // Helper methods
    getUserHeaders() {
      return { 'x-user-id': appStore.getUserId() }
    },

    toggleEventType(eventType) { eventsStore.toggleEventType(eventType) },
    updateStatistics() { /* Now computed automatically */ },
    clearAllFilters() { eventsStore.clearAllFilters() },
    selectAllEventTypes() { eventsStore.selectAllEventTypes() }
  }
})