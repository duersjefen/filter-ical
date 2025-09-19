import { ref, computed } from 'vue'

export function useSimpleGroupSelection() {
  // Enhanced selection state - separate group vs individual tracking
  const selectedEventTypes = ref([]) // Individual event type selections
  const selectedGroups = ref(new Set()) // Group-level selections (includes future events)
  const expandedGroups = ref(new Set())
  
  // Enhanced selection management
  const isEventTypeSelected = (eventType) => {
    return selectedEventTypes.value.includes(eventType)
  }
  
  const isGroupSelected = (groupId) => {
    return selectedGroups.value.has(groupId)
  }
  
  const isEventTypeInSelectedGroup = (eventType, groups) => {
    // Check if this event type is in a selected group
    for (const groupId of selectedGroups.value) {
      const group = groups[groupId]
      if (group && group.event_types && group.event_types[eventType]) {
        return true
      }
    }
    return false
  }
  
  const isEventTypeEffectivelySelected = (eventType, groups = {}) => {
    // Event type is selected if:
    // 1. Explicitly selected as individual event type, OR
    // 2. Part of a selected group
    return isEventTypeSelected(eventType) || isEventTypeInSelectedGroup(eventType, groups)
  }
  
  const toggleEventType = (eventType) => {
    const index = selectedEventTypes.value.indexOf(eventType)
    if (index > -1) {
      selectedEventTypes.value.splice(index, 1)
    } else {
      selectedEventTypes.value.push(eventType)
    }
  }
  
  const setSelectedEventTypes = (eventTypes) => {
    selectedEventTypes.value = [...eventTypes]
  }
  
  // Group expansion management
  const isGroupExpanded = (groupId) => {
    return expandedGroups.value.has(groupId)
  }
  
  const toggleGroupExpansion = (groupId) => {
    const newExpanded = new Set(expandedGroups.value)
    if (newExpanded.has(groupId)) {
      newExpanded.delete(groupId)
    } else {
      newExpanded.add(groupId)
    }
    expandedGroups.value = newExpanded
  }
  
  // Group selection helpers
  const getGroupEventTypes = (group) => {
    return group.event_types ? Object.keys(group.event_types) : []
  }
  
  const isGroupFullySelected = (group) => {
    const groupEventTypes = getGroupEventTypes(group)
    return groupEventTypes.length > 0 && 
           groupEventTypes.every(eventType => isEventTypeSelected(eventType))
  }
  
  const isGroupPartiallySelected = (group) => {
    const groupEventTypes = getGroupEventTypes(group)
    const selectedCount = groupEventTypes.filter(eventType => 
      isEventTypeSelected(eventType)
    ).length
    return selectedCount > 0 && selectedCount < groupEventTypes.length
  }
  
  const toggleGroupSelection = (group) => {
    const groupId = group.id
    const groupEventTypes = getGroupEventTypes(group)
    
    if (groupEventTypes.length === 0) return
    
    if (selectedGroups.value.has(groupId)) {
      // Deselect the group
      selectedGroups.value.delete(groupId)
      
      // Remove individual selections for event types in this group
      // (since they were covered by the group selection)
      groupEventTypes.forEach(eventType => {
        const index = selectedEventTypes.value.indexOf(eventType)
        if (index > -1) {
          selectedEventTypes.value.splice(index, 1)
        }
      })
    } else {
      // Select the group - this will include all current AND future event types
      selectedGroups.value.add(groupId)
      
      // Remove individual event type selections for this group's events
      // since they're now covered by the group selection
      groupEventTypes.forEach(eventType => {
        const index = selectedEventTypes.value.indexOf(eventType)
        if (index > -1) {
          selectedEventTypes.value.splice(index, 1)
        }
      })
    }
  }
  
  const toggleIndividualEventType = (eventType, groups = {}) => {
    // Toggle individual event type selection
    // Individual selections work independently of group selections
    
    const index = selectedEventTypes.value.indexOf(eventType)
    if (index > -1) {
      // Remove individual selection
      selectedEventTypes.value.splice(index, 1)
    } else {
      // Add individual selection - no group interference
      selectedEventTypes.value.push(eventType)
    }
  }
  
  // Bulk operations
  const clearAllSelections = () => {
    selectedEventTypes.value = []
    selectedGroups.value = new Set()
  }
  
  const selectAllGroups = (groups) => {
    const allEventTypes = []
    Object.values(groups || {}).forEach(group => {
      const groupEventTypes = getGroupEventTypes(group)
      allEventTypes.push(...groupEventTypes)
    })
    selectedEventTypes.value = [...new Set(allEventTypes)]
  }
  
  // Computed values
  const selectedCount = computed(() => selectedEventTypes.value.length)
  
  const selectionSummary = computed(() => {
    return {
      eventTypes: selectedEventTypes.value,
      groups: Array.from(selectedGroups.value),
      count: selectedEventTypes.value.length,
      groupCount: selectedGroups.value.size
    }
  })
  
  return {
    // State
    selectedEventTypes: computed(() => selectedEventTypes.value),
    selectedGroups: computed(() => selectedGroups.value),
    expandedGroups: computed(() => expandedGroups.value),
    
    // Event type selection
    isEventTypeSelected,
    isEventTypeEffectivelySelected,
    toggleEventType,
    toggleIndividualEventType,
    setSelectedEventTypes,
    
    // Group selection
    isGroupSelected,
    isEventTypeInSelectedGroup,
    toggleGroupSelection,
    
    // Group expansion
    isGroupExpanded,
    toggleGroupExpansion,
    
    // Legacy group selection helpers (for compatibility)
    isGroupFullySelected,
    isGroupPartiallySelected,
    
    // Bulk operations
    clearAllSelections,
    selectAllGroups,
    
    // Computed values
    selectedCount,
    selectionSummary
  }
}