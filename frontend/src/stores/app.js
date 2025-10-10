/**
 * App Store - Orchestration Layer
 * Coordinates initialization between specialized stores
 * Delegates to: calendar, domain, filter, user stores
 */
import { defineStore } from 'pinia'
import { computed } from 'vue'
import { useUsername } from '../composables/useUsername'
import { useHTTP } from '../composables/useHTTP'
import { useCalendarStore } from './calendar'
import { useDomainStore } from './domain'
import { useFilterStore } from './filter'
import { useUserStore } from './user'

export const useAppStore = defineStore('app', () => {
  // ===============================================
  // DEPENDENCIES - SPECIALIZED STORES
  // ===============================================
  const calendarStore = useCalendarStore()
  const domainStore = useDomainStore()
  const filterStore = useFilterStore()
  const userStore = useUserStore()

  // ===============================================
  // SHARED UTILITIES
  // ===============================================
  const { getUserId, onUsernameChange } = useUsername()
  const { loading, error, clearError, setError } = useHTTP()

  // ===============================================
  // APP INITIALIZATION
  // ===============================================
  const initializeApp = () => {
    // Force username initialization from localStorage
    getUserId() // This triggers the username composable initialization

    // Load available domains (public data, no auth required)
    domainStore.fetchAvailableDomains()

    // Set up username change detection for data source switching
    onUsernameChange((newUsername, oldUsername) => {
      // Clear current calendars to prevent confusion
      calendarStore.calendars = []

      // Clear filtered calendars to prevent showing stale data
      filterStore.filteredCalendars = []

      // Reload calendars with new authentication state
      calendarStore.fetchCalendars()

      // Reload filters with new username
      filterStore.fetchUserFilters()
    })
  }

  // ===============================================
  // DELEGATED STATE (READ-ONLY COMPUTED)
  // ===============================================

  // Calendar state
  const calendars = computed({
    get() { return calendarStore.calendars },
    set(value) { calendarStore.calendars = value }
  })
  const selectedCalendar = computed({
    get() { return calendarStore.selectedCalendar },
    set(value) { calendarStore.selectedCalendar = value }
  })
  const newCalendar = computed({
    get() { return calendarStore.newCalendar },
    set(value) { calendarStore.newCalendar = value }
  })
  const events = computed({
    get() { return calendarStore.events },
    set(value) { calendarStore.events = value }
  })
  const recurringEvents = computed({
    get() { return calendarStore.recurringEvents },
    set(value) { calendarStore.recurringEvents = value }
  })

  // Domain state
  const availableDomains = computed({
    get() { return domainStore.availableDomains },
    set(value) { domainStore.availableDomains = value }
  })
  const groups = computed({
    get() { return domainStore.groups },
    set(value) { domainStore.groups = value }
  })
  const isDomainCalendar = computed(() => domainStore.isDomainCalendar)
  const hasCustomGroups = computed(() => domainStore.hasCustomGroups)
  const allEventsFromGroups = computed(() => domainStore.allEventsFromGroups)

  // Filter state
  const savedFilters = computed(() => filterStore.savedFilters)
  const userDomainFilters = computed(() => filterStore.userDomainFilters)
  const domainsWithFilters = computed(() => filterStore.domainsWithFilters)
  const filteredCalendars = computed({
    get() { return filterStore.filteredCalendars },
    set(value) { filterStore.filteredCalendars = value }
  })

  // ===============================================
  // DELEGATED ACTIONS
  // ===============================================

  // Calendar actions
  const fetchCalendars = calendarStore.fetchCalendars
  const addCalendar = calendarStore.addCalendar
  const deleteCalendar = calendarStore.deleteCalendar
  const syncCalendar = calendarStore.syncCalendar
  const selectCalendar = calendarStore.selectCalendar
  const clearSelection = calendarStore.clearSelection
  const loadCalendarEvents = calendarStore.loadCalendarEvents
  const loadCalendarRecurringEvents = calendarStore.loadCalendarRecurringEvents
  const loadCalendarGroups = calendarStore.loadCalendarGroups

  // Domain actions
  const fetchAvailableDomains = domainStore.fetchAvailableDomains
  const loadDomainGroups = domainStore.loadDomainGroups

  // Filter actions
  const fetchFilters = filterStore.fetchFilters
  const fetchUserFilters = filterStore.fetchUserFilters
  const saveFilter = filterStore.saveFilter
  const deleteFilter = filterStore.deleteFilter
  const loadFilteredCalendars = filterStore.loadFilteredCalendars
  const createFilteredCalendar = filterStore.createFilteredCalendar
  const updateFilteredCalendar = filterStore.updateFilteredCalendar
  const deleteFilteredCalendar = filterStore.deleteFilteredCalendar
  const generateIcal = filterStore.generateIcal

  // User actions
  const getUserPreferences = userStore.getUserPreferences
  const saveUserPreferences = userStore.saveUserPreferences
  const getCalendarPreferences = userStore.getCalendarPreferences
  const saveCalendarPreferences = userStore.saveCalendarPreferences

  // ===============================================
  // EXPORTS - UNIFIED API
  // ===============================================
  return {
    // App initialization
    initializeApp,

    // Shared utilities
    loading,
    error,
    clearError,
    setError,

    // Calendar state
    calendars,
    selectedCalendar,
    newCalendar,
    events,
    recurringEvents,

    // Calendar actions
    fetchCalendars,
    addCalendar,
    deleteCalendar,
    syncCalendar,
    selectCalendar,
    clearSelection,
    loadCalendarEvents,
    loadCalendarRecurringEvents,
    loadCalendarGroups,

    // Domain state
    availableDomains,
    groups,
    isDomainCalendar,
    hasCustomGroups,
    allEventsFromGroups,

    // Domain actions
    fetchAvailableDomains,
    loadDomainGroups,

    // Filter state
    savedFilters,
    userDomainFilters,
    domainsWithFilters,
    filteredCalendars,

    // Filter actions
    fetchFilters,
    fetchUserFilters,
    saveFilter,
    deleteFilter,
    loadFilteredCalendars,
    createFilteredCalendar,
    updateFilteredCalendar,
    deleteFilteredCalendar,
    generateIcal,

    // User actions
    getUserPreferences,
    saveUserPreferences,
    getCalendarPreferences,
    saveCalendarPreferences
  }
})
