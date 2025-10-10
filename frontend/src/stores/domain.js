/**
 * Domain Store
 * Manages domain operations and groups
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useHTTP } from '../composables/useHTTP'
import { API_ENDPOINTS } from '../constants/api'
import { hasCustomGroups as checkHasCustomGroups } from '../utils/groups'

export const useDomainStore = defineStore('domain', () => {
  // ===============================================
  // DEPENDENCIES
  // ===============================================
  const { get } = useHTTP()

  // ===============================================
  // STATE
  // ===============================================
  const availableDomains = ref([])
  const groups = ref({})

  // ===============================================
  // DOMAIN OPERATIONS
  // ===============================================

  const fetchAvailableDomains = async () => {
    try {
      const result = await get(API_ENDPOINTS.DOMAINS)

      if (result.success) {
        availableDomains.value = result.data || []
        return { success: true, data: availableDomains.value }
      } else {
        availableDomains.value = []
        return { success: false, error: result.error }
      }
    } catch (error) {
      availableDomains.value = []
      return { success: false, error: 'Failed to load domains' }
    }
  }

  const loadDomainGroups = async (domainName) => {
    // Use the domain events endpoint which provides the full hierarchical structure
    const result = await get(API_ENDPOINTS.DOMAIN_EVENTS(domainName))

    if (result.success) {
      // Use backend format directly - no complex conversion needed
      const domainData = result.data

      // Simple direct mapping - keep backend structure
      groups.value = {}
      if (domainData.groups) {
        domainData.groups.forEach(group => {
          const groupId = String(group.id)
          groups.value[groupId] = {
            id: groupId,
            name: group.name,
            description: group.description,
            recurring_events: group.recurring_events || []
          }
        })
      }
    }

    return result
  }

  // ===============================================
  // COMPUTED PROPERTIES
  // ===============================================

  // Check if this is a domain calendar (has ANY groups including auto-groups)
  // Domain calendars always have groups (backend creates auto-groups)
  // Personal calendars never have groups
  // This is effectively a calendar type indicator
  const isDomainCalendar = computed(() => {
    return groups.value && Object.keys(groups.value).length > 0
  })

  // Check if CUSTOM (non-auto) groups exist
  // Used to decide whether to show group-related UI features
  // Auto-groups have IDs >= 9998
  const hasCustomGroups = computed(() => {
    return checkHasCustomGroups(groups.value)
  })

  /**
   * Extract all events from groups data for preview consumption
   * This computed property ensures reactivity when groups data changes
   * Deduplicates events that appear in multiple groups
   */
  const allEventsFromGroups = computed(() => {
    const extractedEvents = []

    // Extract from groups structure (for domain calendars)
    if (groups.value && Object.keys(groups.value).length > 0) {
      Object.values(groups.value).forEach(group => {
        if (group.recurring_events && Array.isArray(group.recurring_events)) {
          group.recurring_events.forEach(recurringEvent => {
            if (recurringEvent.events && Array.isArray(recurringEvent.events)) {
              extractedEvents.push(...recurringEvent.events)
            }
          })
        }
      })
    }

    // Deduplicate events using robust identifier strategy
    const uniqueEvents = new Map()
    extractedEvents.forEach(event => {
      // Generate stable identifier using event content
      let identifier
      if (event.uid) {
        identifier = event.uid
      } else {
        // Create content-based identifier
        const title = event.title || event.summary || 'untitled'
        const start = event.start || event.dtstart || ''
        const end = event.end || event.dtend || ''

        if (start && end) {
          identifier = `${title}-${start}-${end}`
        } else if (start) {
          const description = event.description || ''
          const descHash = description ? description.length.toString() : '0'
          identifier = `${title}-${start}-${descHash}`
        } else {
          const description = event.description || ''
          const descHash = description ? description.length.toString() : '0'
          identifier = `${title}-${descHash}`
        }
      }

      // Only keep the first occurrence of each unique event
      if (!uniqueEvents.has(identifier)) {
        uniqueEvents.set(identifier, event)
      }
    })

    return Array.from(uniqueEvents.values())
  })

  // ===============================================
  // EXPORTS
  // ===============================================

  return {
    // State
    availableDomains,
    groups,

    // Computed
    isDomainCalendar,
    hasCustomGroups,
    allEventsFromGroups,

    // Actions
    fetchAvailableDomains,
    loadDomainGroups
  }
})
