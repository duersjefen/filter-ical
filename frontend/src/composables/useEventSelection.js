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
  const selectedEventTypes = ref([])          // Individual event types selected
  
  // Simple expansion state for groups
  const expandedGroups = ref(new Set())
  const expandedEventTypes = ref(new Set())
  
  // === Basic Selection Operations ===
  
  const isEventTypeSelected = (eventType) => {
    return selectedEventTypes.value.includes(eventType)
  }
  
  const isEventTypeEffectivelySelected = (eventType, groups = {}) => {
    // Event type is selected if:
    // 1. Explicitly selected as individual event type, OR
    // 2. Part of a subscribed group
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
  
  const clearSelection = () => {
    selectedEventTypes.value = []
    subscribedGroups.value = new Set()
  }
  
  // === Group Subscription Operations ===
  
  const isGroupSubscribed = (groupId) => {
    return subscribedGroups.value.has(groupId)
  }
  
  const toggleGroupSubscription = (groupId) => {
    if (subscribedGroups.value.has(groupId)) {
      subscribedGroups.value.delete(groupId)
    } else {
      subscribedGroups.value.add(groupId)
    }
  }
  
  const subscribeToGroup = (groupId) => {
    subscribedGroups.value.add(groupId)
  }
  
  const unsubscribeFromGroup = (groupId) => {
    subscribedGroups.value.delete(groupId)
  }
  
  const subscribeToAllGroups = (groups) => {
    const groupIds = Object.keys(groups || {})
    subscribedGroups.value = new Set(groupIds)
  }
  
  // === Group Operations (Legacy - for individual event type selection within groups) ===
  
  const getGroupEventTypes = (group) => {
    if (!group || !group.event_types) return []
    return Object.keys(group.event_types).filter(eventType => {
      // Only include event types that have events (count > 0)
      return group.event_types[eventType].count > 0
    })
  }
  
  const isGroupFullySelected = (group) => {
    const eventTypes = getGroupEventTypes(group)
    return eventTypes.length > 0 && 
           eventTypes.every(type => isEventTypeSelected(type))
  }
  
  const isGroupPartiallySelected = (group) => {
    const eventTypes = getGroupEventTypes(group)
    const selectedCount = eventTypes.filter(type => isEventTypeSelected(type)).length
    return selectedCount > 0 && selectedCount < eventTypes.length
  }
  
  const getGroupSelectionState = (group, groupId) => {
    const isSubscribed = isGroupSubscribed(groupId)
    const eventTypes = getGroupEventTypes(group)
    const individuallySelected = eventTypes.filter(type => isEventTypeSelected(type)).length
    
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
  
  const toggleGroupSelection = (group) => {
    const eventTypes = getGroupEventTypes(group)
    if (eventTypes.length === 0) return
    
    if (isGroupFullySelected(group)) {
      // Deselect all event types in group
      deselectEventTypes(eventTypes)
    } else {
      // Select all event types in group
      selectEventTypes(eventTypes)
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
  
  const isEventTypeExpanded = (eventType) => {
    return expandedEventTypes.value.has(eventType)
  }
  
  const toggleEventTypeExpansion = (eventType) => {
    if (expandedEventTypes.value.has(eventType)) {
      expandedEventTypes.value.delete(eventType)
    } else {
      expandedEventTypes.value.add(eventType)
    }
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
  
  const selectedCount = computed(() => selectedEventTypes.value.length)
  
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
  
  const getSelectionSummary = (groups = {}, ungroupedTypes = []) => {
    const totalEventTypes = new Set()
    const effectivelySelectedTypes = new Set()
    
    // Count event types from groups (only those with events)
    Object.values(groups).forEach(group => {
      getGroupEventTypes(group).forEach(type => totalEventTypes.add(type))
    })
    
    // Count ungrouped event types (only those with count > 0)
    ungroupedTypes.forEach(typeObj => {
      if (typeObj.count > 0) {
        totalEventTypes.add(typeObj.name)
      }
    })
    
    // Count effectively selected (subscribed groups + individual selections)
    totalEventTypes.forEach(eventType => {
      if (isEventTypeEffectivelySelected(eventType, groups)) {
        effectivelySelectedTypes.add(eventType)
      }
    })
    
    // Add ungrouped individual selections
    ungroupedTypes.forEach(typeObj => {
      if (typeObj.count > 0 && selectedEventTypes.value.includes(typeObj.name)) {
        effectivelySelectedTypes.add(typeObj.name)
      }
    })
    
    return {
      selected: effectivelySelectedTypes.size,
      total: totalEventTypes.size,
      subscribed: subscribedGroups.value.size,
      individual: selectedEventTypes.value.length,
      text: `${effectivelySelectedTypes.size} of ${totalEventTypes.size} events selected`
    }
  }
  
  return {
    // State
    selectedEventTypes: computed(() => selectedEventTypes.value),
    subscribedGroups: computed(() => subscribedGroups.value),
    expandedGroups: computed(() => expandedGroups.value),
    expandedEventTypes: computed(() => expandedEventTypes.value),
    
    // Individual event type selection
    isEventTypeSelected,
    isEventTypeEffectivelySelected,
    toggleEventType,
    selectEventTypes,
    deselectEventTypes,
    
    // Group subscription operations
    isGroupSubscribed,
    toggleGroupSubscription,
    subscribeToGroup,
    unsubscribeFromGroup,
    subscribeToAllGroups,
    
    // Group operations (legacy individual selection)
    getGroupEventTypes,
    isGroupFullySelected,
    isGroupPartiallySelected,
    toggleGroupSelection,
    getGroupSelectionState,
    
    // Expansion operations
    isGroupExpanded,
    toggleGroupExpansion,
    isEventTypeExpanded,
    toggleEventTypeExpansion,
    
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