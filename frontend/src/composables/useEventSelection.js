import { ref, computed } from 'vue'

/**
 * Simplified Event Selection Composable
 * Replaces the complex multi-composable system with a single, focused solution
 * 
 * Core Philosophy: Simple array of selected event types + direct filtering
 * No complex registries, cross-group sync, or over-abstraction
 */
export function useEventSelection() {
  // Dual selection model: subscriptions + individual selections
  const subscribedGroups = ref(new Set())      // Groups user subscribed to (includes future events)
  const selectedRecurringEvents = ref([])          // Individual event types selected
  
  // Simple expansion state for groups
  const expandedGroups = ref(new Set())
  // Using expandedRecurringEvents from selectionStore instead of local state
  
  // === Basic Selection Operations ===
  
  const isRecurringEventSelected = (recurringEvent) => {
    return selectedRecurringEvents.value.includes(recurringEvent)
  }
  
  const isRecurringEventEffectivelySelected = (recurringEvent, groups = {}) => {
    // Event type is selected if:
    // 1. Explicitly selected as individual event type, OR
    // 2. Part of a subscribed group
    if (selectedRecurringEvents.value.includes(recurringEvent)) return true
    
    // Check if recurring event is in any subscribed group
    for (const groupId of subscribedGroups.value) {
      const group = groups[groupId]
      if (group && group.recurring_events && group.recurring_events.some(event => event.title === recurringEvent)) {
        return true
      }
    }
    return false
  }
  
  const toggleRecurringEvent = (recurringEvent) => {
    const index = selectedRecurringEvents.value.indexOf(recurringEvent)
    if (index > -1) {
      selectedRecurringEvents.value.splice(index, 1)
    } else {
      selectedRecurringEvents.value.push(recurringEvent)
    }
  }
  
  const selectRecurringEvents = (recurringEvents) => {
    // Add event types that aren't already selected
    const newTypes = recurringEvents.filter(type => !selectedRecurringEvents.value.includes(type))
    selectedRecurringEvents.value.push(...newTypes)
  }
  
  const deselectRecurringEvents = (recurringEvents) => {
    selectedRecurringEvents.value = selectedRecurringEvents.value.filter(
      type => !recurringEvents.includes(type)
    )
  }
  
  const clearSelection = () => {
    selectedRecurringEvents.value = []
    subscribedGroups.value = new Set()
  }
  
  // === Group Subscription Operations ===
  
  const isGroupSubscribed = (groupId) => {
    return subscribedGroups.value.has(groupId)
  }
  
  const toggleGroupSubscription = (groupId, group = null) => {
    if (subscribedGroups.value.has(groupId)) {
      unsubscribeFromGroup(groupId, group)
    } else {
      subscribeToGroup(groupId, group)
    }
  }
  
  const subscribeToGroup = (groupId, group = null) => {
    subscribedGroups.value.add(groupId)
    // Subscribe only - no automatic selection of event types
    // Use the combined "Subscribe & Select" button for automatic selection
  }
  
  const unsubscribeFromGroup = (groupId, group = null) => {
    subscribedGroups.value.delete(groupId)
    // Unsubscribe only - no automatic deselection of event types
    // Use the combined "Subscribe & Select" button for automatic deselection
  }
  
  const subscribeToAllGroups = (groups) => {
    const groupIds = Object.keys(groups || {})
    subscribedGroups.value = new Set(groupIds)
  }

  // === Combined Operations for Three-Button System ===
  
  const subscribeAndSelectGroup = (groupId, group) => {
    // Combined action: Subscribe to group AND select all its recurring events
    subscribeToGroup(groupId, group)
    
    if (group?.recurring_events) {
      const groupRecurringEvents = group.recurring_events.filter(recurringEvent => {
        // Only include recurring events that have events (count > 0)
        return recurringEvent.event_count > 0
      }).map(recurringEvent => recurringEvent.title)
      selectRecurringEvents(groupRecurringEvents)
    }
  }
  
  const unsubscribeAndDeselectGroup = (groupId, group) => {
    // Combined action: Unsubscribe from group AND deselect all its recurring events
    unsubscribeFromGroup(groupId, group)
    
    if (group?.recurring_events) {
      const groupRecurringEvents = group.recurring_events.filter(recurringEvent => {
        // Only include recurring events that have events (count > 0)
        return recurringEvent.event_count > 0
      }).map(recurringEvent => recurringEvent.title)
      deselectRecurringEvents(groupRecurringEvents)
    }
  }
  
  // === Group Operations (Legacy - for individual event type selection within groups) ===
  
  const getGroupRecurringEvents = (group) => {
    if (!group || !group.recurring_events) return []
    return group.recurring_events.filter(recurringEvent => {
      // Only include recurring events that have events (count > 0)
      return recurringEvent.event_count > 0
    }).map(recurringEvent => recurringEvent.title)
  }
  
  const isGroupFullySelected = (group) => {
    const recurringEvents = getGroupRecurringEvents(group)
    return recurringEvents.length > 0 && 
           recurringEvents.every(eventTitle => isRecurringEventSelected(eventTitle))
  }
  
  const isGroupPartiallySelected = (group) => {
    const recurringEvents = getGroupRecurringEvents(group)
    const selectedCount = recurringEvents.filter(eventTitle => isRecurringEventSelected(eventTitle)).length
    return selectedCount > 0 && selectedCount < recurringEvents.length
  }
  
  const getGroupSelectionState = (group, groupId) => {
    const isSubscribed = isGroupSubscribed(groupId)
    const recurringEvents = getGroupRecurringEvents(group)
    const individuallySelected = recurringEvents.filter(eventTitle => isRecurringEventSelected(eventTitle)).length
    
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
  
  const toggleGroupSelection = (group) => {
    const recurringEvents = getGroupRecurringEvents(group)
    if (recurringEvents.length === 0) return
    
    if (isGroupFullySelected(group)) {
      // Deselect all event types in group
      deselectRecurringEvents(recurringEvents)
    } else {
      // Select all event types in group
      selectRecurringEvents(recurringEvents)
    }
  }
  
  // === Expansion State ===
  
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
  
  // Event type expansion state managed centrally in selectionStore
  const isRecurringEventExpanded = (recurringEvent) => {
    // Note: This function exists for compatibility but expandedRecurringEvents 
    // state is now managed centrally in selectionStore
    return false // Placeholder - real implementation should use selectionStore
  }
  
  const toggleRecurringEventExpansion = (recurringEvent) => {
    // Note: This function exists for compatibility but expandedRecurringEvents 
    // state is now managed centrally in selectionStore
    // Real implementation should use selectionStore.toggleRecurringEventExpansion
  }
  
  // === Bulk Operations ===
  
  const expandAllGroups = (groups) => {
    const groupIds = Object.keys(groups || {})
    expandedGroups.value = new Set(groupIds)
  }
  
  const collapseAllGroups = () => {
    expandedGroups.value = new Set()
  }
  
  const selectAllGroups = (groups) => {
    // Subscribe to all groups instead of selecting individual event types
    subscribeToAllGroups(groups)
  }
  
  // === Computed Properties ===
  
  const selectedCount = computed(() => selectedRecurringEvents.value.length)
  
  const allGroupsExpanded = computed(() => {
    return (groups) => {
      const groupIds = Object.keys(groups || {})
      return groupIds.length > 0 && 
             groupIds.every(id => expandedGroups.value.has(id))
    }
  })
  
  const allGroupsCollapsed = computed(() => {
    return expandedGroups.value.size === 0
  })
  
  // === Summary Information ===
  
  const getSelectionSummary = (groups = {}) => {
    const totalRecurringEvents = new Set()
    const effectivelySelectedTypes = new Set()
    
    // Count event types from groups (only those with events)
    Object.values(groups).forEach(group => {
      getGroupRecurringEvents(group).forEach(type => totalRecurringEvents.add(type))
    })
    
    
    // Count effectively selected: subscribed groups + individual selections
    totalRecurringEvents.forEach(recurringEvent => {
      if (isRecurringEventEffectivelySelected(recurringEvent, groups)) {
        effectivelySelectedTypes.add(recurringEvent)
      }
    })
    
    
    // ENHANCEMENT: Add individual selections from NON-subscribed groups
    // This addresses the requirement: "+ 30 recurring events should include selected events from groups the user is not subscribed to"
    Object.entries(groups).forEach(([groupId, group]) => {
      if (!subscribedGroups.value.has(groupId) && group.recurring_events) {
        group.recurring_events.forEach(recurringEvent => {
          if (recurringEvent.event_count > 0 && selectedRecurringEvents.value.includes(recurringEvent.title)) {
            effectivelySelectedTypes.add(recurringEvent.title)
          }
        })
      }
    })
    
    return {
      selected: effectivelySelectedTypes.size,
      total: totalRecurringEvents.size,
      subscribed: subscribedGroups.value.size,
      individual: selectedRecurringEvents.value.length,
      text: `${effectivelySelectedTypes.size} of ${totalRecurringEvents.size} recurring events selected`
    }
  }
  
  return {
    // State
    selectedRecurringEvents: computed(() => selectedRecurringEvents.value),
    subscribedGroups: computed(() => subscribedGroups.value),
    expandedGroups: computed(() => expandedGroups.value),
    
    // Individual event type selection
    isRecurringEventSelected,
    isRecurringEventEffectivelySelected,
    toggleRecurringEvent,
    selectRecurringEvents,
    deselectRecurringEvents,
    
    // Group subscription operations
    isGroupSubscribed,
    toggleGroupSubscription,
    subscribeToGroup,
    unsubscribeFromGroup,
    subscribeToAllGroups,
    
    // Combined operations (for three-button system)
    subscribeAndSelectGroup,
    unsubscribeAndDeselectGroup,
    
    // Group operations (legacy individual selection)
    getGroupRecurringEvents,
    isGroupFullySelected,
    isGroupPartiallySelected,
    toggleGroupSelection,
    getGroupSelectionState,
    
    // Expansion operations
    isGroupExpanded,
    toggleGroupExpansion,
    isRecurringEventExpanded,
    toggleRecurringEventExpansion,
    
    // Bulk operations
    expandAllGroups,
    collapseAllGroups,
    selectAllGroups,
    clearSelection,
    
    // Computed properties
    selectedCount,
    allGroupsExpanded,
    allGroupsCollapsed,
    
    // Summary
    getSelectionSummary
  }
}