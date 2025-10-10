/**
 * Filter Store
 * Manages filters, filtered calendars, and iCal generation
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useHTTP } from '../composables/useHTTP'
import { useUsername } from '../composables/useUsername'
import { API_ENDPOINTS } from '../constants/api'

export const useFilterStore = defineStore('filter', () => {
  // ===============================================
  // DEPENDENCIES
  // ===============================================
  const { getUserId } = useUsername()
  const { get, post, del } = useHTTP()

  // ===============================================
  // STATE
  // ===============================================
  const savedFilters = ref([])
  const userDomainFilters = ref([])
  const filteredCalendars = ref([])

  // ===============================================
  // SAVED FILTERS OPERATIONS
  // ===============================================

  const fetchFilters = async () => {
    // Note: Saved filters functionality not implemented in new backend yet
    return { success: true, data: { filters: [] } }
  }

  const fetchUserFilters = async () => {
    const currentUserId = getUserId()

    // Always fetch filters if we have any user ID (including anon)
    // But only store/display domain filters for logged-in users
    const hasCustomUsername = currentUserId !== 'public' && !currentUserId.startsWith('anon_')

    // Still fetch even for anonymous users in case they log in later
    try {
      const result = await get(`${API_ENDPOINTS.USER_FILTERS}`)

      if (result.success) {
        // useHTTP wraps response in { success: true, data: [...] }
        const filters = result.data || []

        // Store filters only if user is logged in
        if (hasCustomUsername) {
          userDomainFilters.value = filters
        } else {
          userDomainFilters.value = []
        }

        return { success: true, data: filters }
      } else {
        userDomainFilters.value = []
        return { success: false, error: `Failed to fetch filters${result.error ? ': ' + result.error : ''}` }
      }
    } catch (error) {
      userDomainFilters.value = []
      return { success: false, error: 'Failed to connect to server' }
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

    return { success: true, data: newFilter }
  }

  const deleteFilter = async (filterId) => {
    const filterIndex = savedFilters.value.findIndex(filter => filter.id === filterId)

    if (filterIndex === -1) {
      return { success: false, error: 'Filter not found' }
    }

    // Remove from filters list
    savedFilters.value.splice(filterIndex, 1)

    return { success: true }
  }

  // ===============================================
  // COMPUTED PROPERTIES
  // ===============================================

  // Computed property to extract unique domains where user has filters
  const domainsWithFilters = computed(() => {
    // Ensure we have an array to work with
    const filters = Array.isArray(userDomainFilters.value) ? userDomainFilters.value : []
    const domainMap = new Map()

    filters.forEach(filter => {
      if (filter.domain_key && !domainMap.has(filter.domain_key)) {
        domainMap.set(filter.domain_key, {
          domain_key: filter.domain_key,
          filter_count: 0
        })
      }

      if (filter.domain_key) {
        domainMap.get(filter.domain_key).filter_count++
      }
    })

    return Array.from(domainMap.values())
  })

  // ===============================================
  // FILTERED CALENDARS OPERATIONS
  // ===============================================

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
  // ICAL GENERATION
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
      const filterResult = await post(`${API_ENDPOINTS.CALENDAR_FILTERS(calendarId)}`, filterData)

      if (filterResult.success && filterResult.data.link_uuid) {
        // Get the iCal content using the filter's UUID
        const icalResult = await get(API_ENDPOINTS.ICAL_EXPORT(filterResult.data.link_uuid))
        return icalResult
      } else {
        return { success: false, error: 'Failed to create filter for iCal generation' }
      }
    } catch (error) {
      return { success: false, error: 'Failed to generate iCal: ' + error.message }
    }
  }

  // ===============================================
  // EXPORTS
  // ===============================================

  return {
    // State
    savedFilters,
    userDomainFilters,
    filteredCalendars,

    // Computed
    domainsWithFilters,

    // Saved Filters
    fetchFilters,
    fetchUserFilters,
    saveFilter,
    deleteFilter,

    // Filtered Calendars
    loadFilteredCalendars,
    createFilteredCalendar,
    updateFilteredCalendar,
    deleteFilteredCalendar,

    // iCal Generation
    generateIcal
  }
})
