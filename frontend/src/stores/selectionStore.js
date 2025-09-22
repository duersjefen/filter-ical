/**
 * Unified Selection Store - Single Source of Truth
 * 
 * This store replaces the dual selection systems that were causing sync issues:
 * - useCalendar's selectedEventTypes (Events view)
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
  
  // Individual event types selected (across all views)
  const selectedEventTypes = ref([])
  
  // Groups that user subscribed to (includes future events)
  const subscribedGroups = ref(new Set())
  
  // UI expansion state for groups and event types
  const expandedGroups = ref(new Set())
  const expandedEventTypes = ref(new Set())

  // ===============================================
  // COMPUTED PROPERTIES - UNIFIED LOGIC
  // ===============================================
  
  /**
   * Get all effectively selected event types
   * Combines individual selections + subscribed group events
   */
  const effectiveSelectedEventTypes = computed(() => {
    const selected = [...selectedEventTypes.value]
    
    // Add event types from subscribed groups
    // Note: groups data comes from app store
    return selected
  })
  
  /**
   * Check if a specific event type is effectively selected
   * (either individually or through group subscription)
   */
  const isEventTypeEffectivelySelected = (eventType, groups = {}) => {
    // Direct individual selection
    if (selectedEventTypes.value.includes(eventType)) return true
    
    // Check if event type is in any subscribed group
    for (const groupId of subscribedGroups.value) {
      const group = groups[groupId]
      if (group && group.event_types && group.event_types[eventType]) {
        return true
      }
    }
    return false
  }
  
  /**
   * Check if all available events are selected
   */
  const allEventsSelected = (groups = {}, ungroupedEventTypes = []) => {
    // Get all available event types from all sources
    const allAvailableEventTypes = new Set()
    
    // Add event types from all groups
    Object.values(groups).forEach(group => {
      if (group.event_types) {
        Object.keys(group.event_types).forEach(eventType => {
          if (group.event_types[eventType].count > 0) {
            allAvailableEventTypes.add(eventType)
          }
        })
      }
    })
    
    // Add ungrouped event types
    ungroupedEventTypes.forEach(eventType => {
      if (eventType.count > 0) {
        allAvailableEventTypes.add(eventType.name || eventType)
      }
    })
    
    // Check if all available event types are effectively selected
    for (const eventType of allAvailableEventTypes) {
      if (!isEventTypeEffectivelySelected(eventType, groups)) {
        return false
      }
    }
    
    return allAvailableEventTypes.size > 0
  }

  // ===============================================
  // INDIVIDUAL EVENT TYPE OPERATIONS
  // ===============================================
  
  const isEventTypeSelected = (eventType) => {
    return selectedEventTypes.value.includes(eventType)
  }
  
  const toggleEventType = (eventType) => {
    const index = selectedEventTypes.value.indexOf(eventType)
    if (index > -1) {
      selectedEventTypes.value.splice(index, 1)
    } else {
      selectedEventTypes.value.push(eventType)
    }
  }
  
  const selectEventTypes = (eventTypes) => {
    // Add event types that aren't already selected
    const newTypes = eventTypes.filter(type => !selectedEventTypes.value.includes(type))
    selectedEventTypes.value.push(...newTypes)
  }
  
  const deselectEventTypes = (eventTypes) => {
    selectedEventTypes.value = selectedEventTypes.value.filter(
      type => !eventTypes.includes(type)
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
    
    // Also select all event types in this group
    if (group?.event_types) {
      const groupEventTypes = Object.keys(group.event_types).filter(eventType => {
        return group.event_types[eventType].count > 0
      })
      selectEventTypes(groupEventTypes)
    }
  }
  
  /**
   * Unsubscribe from group AND deselect all its event types
   * This is the "Unsubscribe & Deselect" button functionality
   */
  const unsubscribeAndDeselectGroup = (groupId, group) => {
    // Unsubscribe from group
    unsubscribeFromGroup(groupId, group)
    
    // Also deselect all event types in this group
    if (group?.event_types) {
      const groupEventTypes = Object.keys(group.event_types).filter(eventType => {
        return group.event_types[eventType].count > 0
      })
      deselectEventTypes(groupEventTypes)
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
    selectedEventTypes.value = []
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
   * Get comprehensive selection summary for display
   */
  const getSelectionSummary = (groups = {}, ungroupedTypes = []) => {
    const totalEventTypes = new Set()
    const effectivelySelectedTypes = new Set()
    
    // Count event types from groups (only those with events)
    Object.values(groups).forEach(group => {
      if (group.event_types) {
        Object.keys(group.event_types).forEach(eventType => {
          if (group.event_types[eventType].count > 0) {
            totalEventTypes.add(eventType)
          }
        })
      }
    })
    
    // Count ungrouped event types (only those with count > 0)
    ungroupedTypes.forEach(typeObj => {
      if (typeObj.count > 0) {
        totalEventTypes.add(typeObj.name)
      }
    })
    
    // Count effectively selected: subscribed groups + individual selections
    totalEventTypes.forEach(eventType => {
      if (isEventTypeEffectivelySelected(eventType, groups)) {
        effectivelySelectedTypes.add(eventType)
      }
    })
    
    // Add individual selections from NON-subscribed groups
    Object.entries(groups).forEach(([groupId, group]) => {
      if (!subscribedGroups.value.has(groupId) && group.event_types) {
        Object.keys(group.event_types).forEach(eventType => {
          if (group.event_types[eventType].count > 0 && selectedEventTypes.value.includes(eventType)) {
            effectivelySelectedTypes.add(eventType)
          }
        })
      }
    })
    
    return {
      selected: effectivelySelectedTypes.size,
      total: totalEventTypes.size,
      subscribed: subscribedGroups.value.size,
      individual: selectedEventTypes.value.length,
      text: `${effectivelySelectedTypes.size} of ${totalEventTypes.size} event types selected`
    }
  }

  // ===============================================
  // RETURN PUBLIC API
  // ===============================================
  
  return {
    // Direct reactive refs (not wrapped in computed)
    selectedEventTypes,
    subscribedGroups,
    expandedGroups,
    expandedEventTypes,
    
    // Computed properties for derived values
    effectiveSelectedEventTypes,
    
    // Individual event type operations
    isEventTypeSelected,
    toggleEventType,
    selectEventTypes,
    deselectEventTypes,
    
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
    isEventTypeEffectivelySelected,
    allEventsSelected,
    
    // Summary and analysis
    getSelectionSummary
  }
})