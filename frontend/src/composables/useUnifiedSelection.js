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
    selectedRecurringEvents,
    subscribedGroups,
    expandedGroups,
    expandedRecurringEvents
  } = storeToRefs(selectionStore)
  
  // ===============================================
  // COMPUTED PROPERTIES WITH APP STORE INTEGRATION
  // ===============================================
  
  /**
   * Get all effectively selected recurring events
   * Integrates with app store's groups data
   */
  const effectiveSelectedRecurringEvents = computed(() => {
    const selected = [...selectedRecurringEvents.value]
    
    // Add recurring events from subscribed groups
    for (const groupId of subscribedGroups.value) {
      const group = appStore.groups[groupId]
      if (group && group.recurring_events) {
        for (const recurringEvent of group.recurring_events) {
          if (recurringEvent.event_count > 0 && !selected.includes(recurringEvent.title)) {
            selected.push(recurringEvent.title)
          }
        }
      }
    }
    
    return selected
  })
  
  /**
   * Check if all events are selected (simplified - no ungrouped events)
   */
  const allEventsSelected = (groups) => {
    return selectionStore.allEventsSelected(groups || appStore.groups || {})
  }
  
  /**
   * Check if recurring event is effectively selected (with app store groups)
   */
  const isRecurringEventEffectivelySelected = (recurringEventTitle, groups) => {
    return selectionStore.isRecurringEventEffectivelySelected(recurringEventTitle, groups || appStore.groups || {})
  }
  
  /**
   * Get selection summary with app store data (simplified - no ungrouped events)
   */
  const selectionSummary = computed(() => {
    // With simplified backend, everything is auto-grouped
    const summary = selectionStore.getSelectionSummary(appStore.groups || {}, [])
    
    return {
      ...summary,
      compactText: getGroupBreakdownSummary()
    }
  })
  
  /**
   * Get group breakdown summary for display - Fixed to prevent double counting
   */
  const getGroupBreakdownSummary = () => {
    const groups = appStore.groups || {}
    const totalGroups = Object.keys(groups).length
    const subscribedGroupsCount = subscribedGroups.value.size
    
    // Get all unique recurring events across all groups (prevents double counting)
    const allUniqueRecurringEvents = new Set()
    const effectivelySelectedRecurringEvents = new Set()
    
    // First pass: collect all unique recurring events
    Object.entries(groups).forEach(([groupId, group]) => {
      if (group && group.recurring_events) {
        group.recurring_events.forEach((recurringEvent) => {
          if (recurringEvent.event_count > 0) {
            allUniqueRecurringEvents.add(recurringEvent.title)
            
            // Check if this recurring event is effectively selected
            // (either through group subscription OR individual selection)
            if (subscribedGroups.value.has(groupId) || selectedRecurringEvents.value.includes(recurringEvent.title)) {
              effectivelySelectedRecurringEvents.add(recurringEvent.title)
            }
          }
        })
      }
    })
    
    const totalAvailableEvents = allUniqueRecurringEvents.size
    const effectiveSelectedEvents = effectivelySelectedRecurringEvents.size
    
    if (effectiveSelectedEvents === 0 && subscribedGroupsCount === 0) {
      return 'No events or groups selected'
    }
    
    const parts = []
    
    // Events part - now shows unique event types
    if (effectiveSelectedEvents > 0) {
      parts.push(`${effectiveSelectedEvents}/${totalAvailableEvents} Events`)
    } else if (totalAvailableEvents > 0) {
      parts.push(`0/${totalAvailableEvents} Events`)
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
   * Get recurring events from a group (only those with count > 0)
   */
  const getGroupRecurringEvents = (group) => {
    if (!group || !group.recurring_events) return []
    return group.recurring_events.filter(recurringEvent => {
      return recurringEvent.event_count > 0
    }).map(recurringEvent => recurringEvent.title)
  }
  
  /**
   * Get group selection state for UI display
   */
  const getGroupSelectionState = (group, groupId) => {
    const isSubscribed = selectionStore.isGroupSubscribed(groupId)
    const recurringEvents = getGroupRecurringEvents(group)
    const individuallySelected = recurringEvents.filter(title => 
      selectionStore.isRecurringEventSelected(title)
    ).length
    
    if (isSubscribed) {
      return { type: 'subscribed', count: recurringEvents.length }
    } else if (individuallySelected === recurringEvents.length && recurringEvents.length > 0) {
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
   * Handle "Select All Recurring Events" action for a group
   */
  const handleSelectAllRecurringEvents = ({ groupId, recurringEvents, selectAll }) => {
    if (selectAll) {
      // Select all recurring events in this group
      recurringEvents.forEach(recurringEvent => {
        if (!selectedRecurringEvents.value.includes(recurringEvent)) {
          selectionStore.toggleRecurringEvent(recurringEvent)
        }
      })
    } else {
      // Deselect all recurring events in this group
      recurringEvents.forEach(recurringEvent => {
        if (selectedRecurringEvents.value.includes(recurringEvent)) {
          selectionStore.toggleRecurringEvent(recurringEvent)
        }
      })
    }
  }

  // ===============================================
  // RETURN UNIFIED API
  // ===============================================
  
  return {
    // Properly reactive refs from storeToRefs
    selectedRecurringEvents,
    subscribedGroups,
    expandedGroups,
    expandedRecurringEvents,
    
    // Computed properties with app store integration
    effectiveSelectedRecurringEvents,
    selectionSummary,
    
    // Individual recurring event operations
    isRecurringEventSelected: selectionStore.isRecurringEventSelected,
    isRecurringEventEffectivelySelected,
    toggleRecurringEvent: selectionStore.toggleRecurringEvent,
    selectRecurringEvents: selectionStore.selectRecurringEvents,
    deselectRecurringEvents: selectionStore.deselectRecurringEvents,
    
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
    getGroupRecurringEvents,
    getGroupSelectionState,
    getGroupBreakdownSummary,
    handleSelectAllRecurringEvents,
    
    // Selection checking methods
    allEventsSelected,
    
    // Legacy compatibility functions (simplified - no ungrouped events)
    getSelectionSummary: () => selectionStore.getSelectionSummary(
      appStore.groups || {}, 
      [] // No ungrouped events with auto-grouping backend
    ),
    
    // Legacy compatibility exports (maintain old names for gradual migration)
    selectedRecurringEvents: selectedRecurringEvents,
    expandedRecurringEvents: expandedRecurringEvents,
    effectiveSelectedRecurringEvents: effectiveSelectedRecurringEvents,
    isRecurringEventSelected: selectionStore.isRecurringEventSelected,
    isRecurringEventEffectivelySelected,
    toggleRecurringEvent: selectionStore.toggleRecurringEvent,
    selectRecurringEvents: selectionStore.selectRecurringEvents,
    deselectRecurringEvents: selectionStore.deselectRecurringEvents
  }
}