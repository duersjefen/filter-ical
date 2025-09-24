/**
 * Unified Selection Store - Single Source of Truth
 * 
 * This store replaces the dual selection systems that were causing sync issues:
 * - useCalendar's selectedRecurringEvents (Events view)
 * - useEventSelection's state (Groups view)
 * 
 * Now both views share identical selection state through this centralized store.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSelectionStore = defineStore('selection', () => {
  // ===============================================
  // CORE SELECTION STATE - SINGLE SOURCE OF TRUTH
  // ===============================================
  
  // Individual recurring events selected (across all views)
  const selectedRecurringEvents = ref([])
  
  // Groups that user subscribed to (includes future events)
  const subscribedGroups = ref(new Set())
  
  // UI expansion state for groups and recurring events
  const expandedGroups = ref(new Set())
  const expandedRecurringEvents = ref(new Set())

  // ===============================================
  // COMPUTED PROPERTIES - UNIFIED LOGIC
  // ===============================================
  
  /**
   * Get all effectively selected recurring events
   * Combines individual selections + subscribed group events
   */
  const effectiveSelectedRecurringEvents = computed(() => {
    const selected = [...selectedRecurringEvents.value]
    
    // Add recurring events from subscribed groups
    // Note: groups data comes from app store
    return selected
  })
  
  /**
   * Check if a specific recurring event is effectively selected
   * (either individually or through group subscription)
   */
  const isRecurringEventEffectivelySelected = (recurringEventTitle, groups = {}) => {
    // Direct individual selection
    if (selectedRecurringEvents.value.includes(recurringEventTitle)) return true
    
    // Check if recurring event is in any subscribed group
    for (const groupId of subscribedGroups.value) {
      const group = groups[groupId]
      if (group && group.recurring_events && group.recurring_events.some(event => event.title === recurringEventTitle)) {
        return true
      }
    }
    return false
  }
  
  /**
   * Check if all available events are selected
   */
  const allEventsSelected = (groups = {}) => {
    // Get all available recurring events from all sources
    const allAvailableRecurringEvents = new Set()
    
    // Add recurring events from all groups
    Object.values(groups).forEach(group => {
      if (group.recurring_events) {
        group.recurring_events.forEach(recurringEvent => {
          if (recurringEvent.event_count > 0) {
            allAvailableRecurringEvents.add(recurringEvent.title)
          }
        })
      }
    })
    
    
    // Check if all available recurring events are effectively selected
    for (const recurringEventTitle of allAvailableRecurringEvents) {
      if (!isRecurringEventEffectivelySelected(recurringEventTitle, groups)) {
        return false
      }
    }
    
    return allAvailableRecurringEvents.size > 0
  }

  // ===============================================
  // INDIVIDUAL RECURRING EVENT OPERATIONS
  // ===============================================
  
  const isRecurringEventSelected = (recurringEventTitle) => {
    return selectedRecurringEvents.value.includes(recurringEventTitle)
  }
  
  const toggleRecurringEvent = (recurringEventTitle) => {
    const index = selectedRecurringEvents.value.indexOf(recurringEventTitle)
    if (index > -1) {
      selectedRecurringEvents.value.splice(index, 1)
    } else {
      selectedRecurringEvents.value.push(recurringEventTitle)
    }
  }
  
  const selectRecurringEvents = (recurringEventTitles) => {
    // Add recurring events that aren't already selected
    const newTitles = recurringEventTitles.filter(title => !selectedRecurringEvents.value.includes(title))
    selectedRecurringEvents.value.push(...newTitles)
  }
  
  const deselectRecurringEvents = (recurringEventTitles) => {
    selectedRecurringEvents.value = selectedRecurringEvents.value.filter(
      title => !recurringEventTitles.includes(title)
    )
  }

  // ===============================================
  // GROUP SUBSCRIPTION OPERATIONS
  // ===============================================
  
  const isGroupSubscribed = (groupId) => {
    return subscribedGroups.value.has(groupId)
  }
  
  const subscribeToGroup = (groupId, group = null) => {
    subscribedGroups.value.add(groupId)
  }
  
  const unsubscribeFromGroup = (groupId, group = null) => {
    subscribedGroups.value.delete(groupId)
  }
  
  const toggleGroupSubscription = (groupId, group = null) => {
    if (subscribedGroups.value.has(groupId)) {
      unsubscribeFromGroup(groupId, group)
    } else {
      subscribeToGroup(groupId, group)
    }
  }

  // ===============================================
  // COMBINED OPERATIONS (Subscribe & Select)
  // ===============================================
  
  /**
   * Subscribe to group AND select all its event types
   * This is the "Subscribe & Select" button functionality
   */
  const subscribeAndSelectGroup = (groupId, group) => {
    // Subscribe to group
    subscribeToGroup(groupId, group)
    
    // Also select all recurring events in this group
    if (group?.recurring_events) {
      const groupRecurringEvents = group.recurring_events.filter(recurringEvent => {
        return recurringEvent.event_count > 0
      }).map(recurringEvent => recurringEvent.title)
      selectRecurringEvents(groupRecurringEvents)
    }
  }
  
  /**
   * Unsubscribe from group AND deselect all its event types
   * This is the "Unsubscribe & Deselect" button functionality
   */
  const unsubscribeAndDeselectGroup = (groupId, group) => {
    // Unsubscribe from group
    unsubscribeFromGroup(groupId, group)
    
    // Also deselect all recurring events in this group
    if (group?.recurring_events) {
      const groupRecurringEvents = group.recurring_events.filter(recurringEvent => {
        return recurringEvent.event_count > 0
      }).map(recurringEvent => recurringEvent.title)
      deselectRecurringEvents(groupRecurringEvents)
    }
  }

  // ===============================================
  // BULK OPERATIONS
  // ===============================================
  
  const selectAllGroups = (groups) => {
    const groupIds = Object.keys(groups || {})
    subscribedGroups.value = new Set(groupIds)
  }
  
  const unsubscribeFromAllGroups = () => {
    subscribedGroups.value.clear()
  }
  
  const subscribeAndSelectAllGroups = (groups) => {
    // Subscribe to all groups AND select all their event types
    Object.entries(groups || {}).forEach(([groupId, group]) => {
      subscribeAndSelectGroup(groupId, group)
    })
  }
  
  const clearSelection = () => {
    selectedRecurringEvents.value = []
    subscribedGroups.value.clear()
  }

  // ===============================================
  // EXPANSION STATE OPERATIONS
  // ===============================================
  
  const isGroupExpanded = (groupId) => {
    return expandedGroups.value.has(groupId)
  }
  
  const toggleGroupExpansion = (groupId) => {
    if (expandedGroups.value.has(groupId)) {
      expandedGroups.value.delete(groupId)
    } else {
      expandedGroups.value.add(groupId)
    }
  }
  
  const expandAllGroups = (groups) => {
    const groupIds = Object.keys(groups || {})
    expandedGroups.value = new Set(groupIds)
  }
  
  const collapseAllGroups = () => {
    expandedGroups.value.clear()
  }

  // ===============================================
  // SELECTION SUMMARY & ANALYSIS
  // ===============================================
  
  /**
   * Get comprehensive selection summary for display - Fixed double counting
   */
  const getSelectionSummary = (groups = {}) => {
    const totalRecurringEvents = new Set()
    const effectivelySelectedEvents = new Set()
    
    // Count unique recurring events from groups (only those with events)
    Object.values(groups).forEach(group => {
      if (group.recurring_events) {
        group.recurring_events.forEach(recurringEvent => {
          if (recurringEvent.event_count > 0) {
            totalRecurringEvents.add(recurringEvent.title)
          }
        })
      }
    })
    
    
    // Count effectively selected recurring events (no double counting)
    totalRecurringEvents.forEach(recurringEventTitle => {
      if (isRecurringEventEffectivelySelected(recurringEventTitle, groups)) {
        effectivelySelectedEvents.add(recurringEventTitle)
      }
    })
    
    return {
      selected: effectivelySelectedEvents.size,
      total: totalRecurringEvents.size,
      subscribed: subscribedGroups.value.size,
      individual: selectedRecurringEvents.value.length,
      text: `${effectivelySelectedEvents.size} of ${totalRecurringEvents.size} recurring events selected`
    }
  }

  // ===============================================
  // RETURN PUBLIC API
  // ===============================================
  
  return {
    // Direct reactive refs (not wrapped in computed)
    selectedRecurringEvents,
    subscribedGroups,
    expandedGroups,
    expandedRecurringEvents,
    
    // Computed properties for derived values
    effectiveSelectedRecurringEvents,
    
    // Individual recurring event operations
    isRecurringEventSelected,
    toggleRecurringEvent,
    selectRecurringEvents,
    deselectRecurringEvents,
    
    // Group subscription operations
    isGroupSubscribed,
    subscribeToGroup,
    unsubscribeFromGroup,
    toggleGroupSubscription,
    
    // Combined operations
    subscribeAndSelectGroup,
    unsubscribeAndDeselectGroup,
    
    // Bulk operations
    selectAllGroups,
    unsubscribeFromAllGroups,
    subscribeAndSelectAllGroups,
    clearSelection,
    
    // Expansion operations
    isGroupExpanded,
    toggleGroupExpansion,
    expandAllGroups,
    collapseAllGroups,
    
    // Methods for checking selection state
    isRecurringEventEffectivelySelected,
    allEventsSelected,
    
    // Summary and analysis
    getSelectionSummary,
    
    // Legacy compatibility (temporarily maintain old names for gradual migration)
    selectedRecurringEvents: selectedRecurringEvents,
    expandedRecurringEvents: expandedRecurringEvents,
    effectiveSelectedRecurringEvents: effectiveSelectedRecurringEvents,
    isRecurringEventSelected: isRecurringEventSelected,
    toggleRecurringEvent: toggleRecurringEvent,
    selectRecurringEvents: selectRecurringEvents,
    deselectRecurringEvents: deselectRecurringEvents,
    isRecurringEventEffectivelySelected: isRecurringEventEffectivelySelected
  }
})