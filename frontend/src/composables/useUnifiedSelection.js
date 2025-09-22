/**
 * Universal Selection Composable
 * 
 * This composable provides a unified interface to the selection store.
 * It replaces both:
 * - useCalendar's selection logic (Events view)
 * - useEventSelection (Groups view)
 * 
 * Now both views use this same composable for perfect synchronization.
 */
import { useSelectionStore } from '../stores/selectionStore'
import { useAppStore } from '../stores/app'
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

export function useUnifiedSelection() {
  const selectionStore = useSelectionStore()
  const appStore = useAppStore()
  
  // Extract reactive refs properly from stores
  const {
    selectedEventTypes,
    subscribedGroups,
    expandedGroups,
    expandedEventTypes
  } = storeToRefs(selectionStore)
  
  // ===============================================
  // COMPUTED PROPERTIES WITH APP STORE INTEGRATION
  // ===============================================
  
  /**
   * Get all effectively selected event types
   * Integrates with app store's groups data
   */
  const effectiveSelectedEventTypes = computed(() => {
    const selected = [...selectedEventTypes.value]
    
    // Add event types from subscribed groups
    for (const groupId of subscribedGroups.value) {
      const group = appStore.groups[groupId]
      if (group && group.event_types) {
        for (const eventType of Object.keys(group.event_types)) {
          if (group.event_types[eventType].count > 0 && !selected.includes(eventType)) {
            selected.push(eventType)
          }
        }
      }
    }
    
    return selected
  })
  
  /**
   * Check if all events are selected (integrates with app store data)
   */
  const allEventsSelected = (groups, ungroupedEventTypes) => {
    return selectionStore.allEventsSelected(
      groups || appStore.groups || {}, 
      ungroupedEventTypes || [
        ...(appStore.ungroupedEventTypes || []),
        ...(appStore.ungroupedRecurringEventTypes || []),
        ...(appStore.ungroupedUniqueEventTypes || [])
      ]
    )
  }
  
  /**
   * Check if event type is effectively selected (with app store groups)
   */
  const isEventTypeEffectivelySelected = (eventType, groups) => {
    return selectionStore.isEventTypeEffectivelySelected(eventType, groups || appStore.groups || {})
  }
  
  /**
   * Get selection summary with app store data
   */
  const selectionSummary = computed(() => {
    const allUngroupedTypes = [
      ...(appStore.ungroupedEventTypes || []),
      ...(appStore.ungroupedRecurringEventTypes || []),
      ...(appStore.ungroupedUniqueEventTypes || [])
    ]
    
    const summary = selectionStore.getSelectionSummary(appStore.groups || {}, allUngroupedTypes)
    
    return {
      ...summary,
      compactText: getGroupBreakdownSummary()
    }
  })
  
  /**
   * Get group breakdown summary for display
   */
  const getGroupBreakdownSummary = () => {
    const groups = appStore.groups || {}
    const totalGroups = Object.keys(groups).length
    const subscribedGroupsCount = subscribedGroups.value.size
    const selectedEventsCount = selectedEventTypes.value.length
    
    // Calculate total available events across all groups
    let totalAvailableEvents = 0
    Object.values(groups).forEach(group => {
      if (group.event_types) {
        const groupEventTypes = Object.keys(group.event_types).filter(eventType => 
          group.event_types[eventType].count > 0
        )
        totalAvailableEvents += groupEventTypes.length
      }
    })
    
    // Calculate effective selected events (subscribed groups + individual selections)
    let effectiveSelectedEvents = selectedEventsCount
    subscribedGroups.value.forEach(groupId => {
      const group = groups[groupId]
      if (group && group.event_types) {
        const groupEventTypes = Object.keys(group.event_types).filter(eventType => 
          group.event_types[eventType].count > 0
        )
        // Add group events that aren't already counted as individual selections
        groupEventTypes.forEach(eventType => {
          if (!selectedEventTypes.value.includes(eventType)) {
            effectiveSelectedEvents++
          }
        })
      }
    })
    
    if (effectiveSelectedEvents === 0 && subscribedGroupsCount === 0) {
      return 'No events or groups selected'
    }
    
    const parts = []
    
    // Events part
    if (effectiveSelectedEvents > 0) {
      parts.push(`${effectiveSelectedEvents}/${totalAvailableEvents} Events`)
    }
    
    // Groups part with special cases
    if (subscribedGroupsCount === 0) {
      parts.push('No groups')
    } else if (subscribedGroupsCount === totalGroups && totalGroups > 0) {
      parts.push('All groups')
    } else {
      parts.push(`${subscribedGroupsCount}/${totalGroups} Groups`)
    }
    
    return parts.join(' & ')
  }

  // ===============================================
  // GROUP HELPER FUNCTIONS
  // ===============================================
  
  /**
   * Get event types from a group (only those with count > 0)
   */
  const getGroupEventTypes = (group) => {
    if (!group || !group.event_types) return []
    return Object.keys(group.event_types).filter(eventType => {
      return group.event_types[eventType].count > 0
    })
  }
  
  /**
   * Get group selection state for UI display
   */
  const getGroupSelectionState = (group, groupId) => {
    const isSubscribed = selectionStore.isGroupSubscribed(groupId)
    const eventTypes = getGroupEventTypes(group)
    const individuallySelected = eventTypes.filter(type => 
      selectionStore.isEventTypeSelected(type)
    ).length
    
    if (isSubscribed) {
      return { type: 'subscribed', count: eventTypes.length }
    } else if (individuallySelected === eventTypes.length && eventTypes.length > 0) {
      return { type: 'fully_selected', count: individuallySelected }
    } else if (individuallySelected > 0) {
      return { type: 'partially_selected', count: individuallySelected }
    } else {
      return { type: 'none_selected', count: 0 }
    }
  }

  // ===============================================
  // BULK OPERATIONS WITH APP STORE INTEGRATION
  // ===============================================
  
  /**
   * Subscribe and select all groups (uses app store groups)
   */
  const subscribeAndSelectAllGroups = () => {
    selectionStore.subscribeAndSelectAllGroups(appStore.groups || {})
  }
  
  /**
   * Expand all groups (uses app store groups)
   */
  const expandAllGroups = () => {
    selectionStore.expandAllGroups(appStore.groups || {})
  }
  
  /**
   * Handle "Select All Event Types" action for a group
   */
  const handleSelectAllEventTypes = ({ groupId, eventTypes, selectAll }) => {
    if (selectAll) {
      // Select all event types in this group
      eventTypes.forEach(eventType => {
        if (!selectedEventTypes.value.includes(eventType)) {
          selectionStore.toggleEventType(eventType)
        }
      })
    } else {
      // Deselect all event types in this group
      eventTypes.forEach(eventType => {
        if (selectedEventTypes.value.includes(eventType)) {
          selectionStore.toggleEventType(eventType)
        }
      })
    }
  }

  // ===============================================
  // RETURN UNIFIED API
  // ===============================================
  
  return {
    // Properly reactive refs from storeToRefs
    selectedEventTypes,
    subscribedGroups,
    expandedGroups,
    expandedEventTypes,
    
    // Computed properties with app store integration
    effectiveSelectedEventTypes,
    selectionSummary,
    
    // Individual event type operations
    isEventTypeSelected: selectionStore.isEventTypeSelected,
    isEventTypeEffectivelySelected,
    toggleEventType: selectionStore.toggleEventType,
    selectEventTypes: selectionStore.selectEventTypes,
    deselectEventTypes: selectionStore.deselectEventTypes,
    
    // Group subscription operations
    isGroupSubscribed: selectionStore.isGroupSubscribed,
    subscribeToGroup: selectionStore.subscribeToGroup,
    unsubscribeFromGroup: selectionStore.unsubscribeFromGroup,
    toggleGroupSubscription: selectionStore.toggleGroupSubscription,
    
    // Combined operations
    subscribeAndSelectGroup: selectionStore.subscribeAndSelectGroup,
    unsubscribeAndDeselectGroup: selectionStore.unsubscribeAndDeselectGroup,
    
    // Bulk operations
    selectAllGroups: selectionStore.selectAllGroups,
    unsubscribeFromAllGroups: selectionStore.unsubscribeFromAllGroups,
    subscribeAndSelectAllGroups,
    clearSelection: selectionStore.clearSelection,
    
    // Expansion operations
    isGroupExpanded: selectionStore.isGroupExpanded,
    toggleGroupExpansion: selectionStore.toggleGroupExpansion,
    expandAllGroups,
    collapseAllGroups: selectionStore.collapseAllGroups,
    
    // Helper functions
    getGroupEventTypes,
    getGroupSelectionState,
    getGroupBreakdownSummary,
    handleSelectAllEventTypes,
    
    // Selection checking methods
    allEventsSelected,
    
    // Legacy compatibility functions (for gradual migration)
    getSelectionSummary: () => selectionStore.getSelectionSummary(
      appStore.groups || {}, 
      [
        ...(appStore.ungroupedEventTypes || []),
        ...(appStore.ungroupedRecurringEventTypes || []),
        ...(appStore.ungroupedUniqueEventTypes || [])
      ]
    )
  }
}