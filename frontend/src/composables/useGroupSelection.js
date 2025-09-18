import { ref, computed } from 'vue'

export function useGroupSelection() {
  // Core selection state
  const selectedItems = ref(new Set())
  const expandedGroups = ref(new Set())
  const expandedEventTypes = ref(new Set())
  
  // Store reference to groups data for cascading logic
  let groupsData = null
  
  // Initialize with groups data
  const setGroupsData = (groups) => {
    groupsData = groups
  }
  
  // Selection helper functions
  const isSelected = (itemId) => selectedItems.value.has(itemId)
  
  const toggleSelection = (itemId, groups = null) => {
    if (groups) setGroupsData(groups)
    
    const newSelection = new Set(selectedItems.value)
    
    if (newSelection.has(itemId)) {
      // Deselecting - remove this item and all its children
      removeItemAndChildren(newSelection, itemId)
    } else {
      // Selecting - add this item and all its children automatically
      addItemAndChildren(newSelection, itemId)
    }
    
    selectedItems.value = newSelection
  }
  
  const removeItemAndChildren = (selection, itemId) => {
    selection.delete(itemId)
    
    if (!groupsData) return
    
    // If it's a group, remove all its children recursively
    if (itemId.startsWith('group:')) {
      const groupId = itemId.replace('group:', '')
      const group = findGroupById(groupId)
      if (group) {
        // Remove all subgroups
        if (group.children) {
          group.children.forEach(child => {
            removeItemAndChildren(selection, `group:${child.id}`)
          })
        }
        // Remove all event types in this group
        if (group.event_types) {
          Object.keys(group.event_types).forEach(eventTypeName => {
            selection.delete(`event_type:${eventTypeName}`)
          })
        }
      }
    }
    
    // If it's an event type, remove all its individual events
    if (itemId.startsWith('event_type:')) {
      const eventTypeName = itemId.replace('event_type:', '')
      for (const selectedItem of Array.from(selection)) {
        if (selectedItem.startsWith('event:') && isEventOfType(selectedItem, eventTypeName)) {
          selection.delete(selectedItem)
        }
      }
    }
  }
  
  const addItemAndChildren = (selection, itemId) => {
    selection.add(itemId)
    
    if (!groupsData) return
    
    // If selecting a group, automatically select all its children
    if (itemId.startsWith('group:')) {
      const groupId = itemId.replace('group:', '')
      const group = findGroupById(groupId)
      if (group) {
        // Select all subgroups
        if (group.children) {
          group.children.forEach(child => {
            addItemAndChildren(selection, `group:${child.id}`)
          })
        }
        // Select all event types in this group
        if (group.event_types) {
          Object.keys(group.event_types).forEach(eventTypeName => {
            selection.add(`event_type:${eventTypeName}`)
          })
        }
      }
    }
  }
  
  const findGroupById = (groupId) => {
    if (!groupsData) return null
    
    // Search in top-level groups
    for (const group of Object.values(groupsData)) {
      if (group.id === groupId) return group
      
      // Search in children recursively
      const found = findGroupInChildren(group.children || [], groupId)
      if (found) return found
    }
    
    return null
  }
  
  const findGroupInChildren = (children, groupId) => {
    for (const child of children) {
      if (child.id === groupId) return child
      
      if (child.children) {
        const found = findGroupInChildren(child.children, groupId)
        if (found) return found
      }
    }
    
    return null
  }
  
  // Helper functions to determine relationships
  const isChildOfGroup = (itemId, groupId) => {
    // This would need group hierarchy data to determine properly
    // For now, we'll use a simple approach
    return false // Will be enhanced with actual group data
  }
  
  const isEventOfType = (eventId, eventTypeName) => {
    // This would need event data to determine properly
    // For now, we'll use a simple approach
    return false // Will be enhanced with actual event data
  }
  
  // Partial selection detection
  const isPartiallySelected = (groups, groupId) => {
    if (isSelected(`group:${groupId}`)) return false
    
    // Find the group in the provided groups data
    const group = findGroupInProvidedData(groups, groupId)
    if (!group) return false
    
    // Check if any children are selected
    return hasAnyChildrenSelected(group)
  }
  
  // Helper to find group in provided groups data (not the global groupsData)
  const findGroupInProvidedData = (groups, groupId) => {
    if (!groups || typeof groups !== 'object') return null
    
    for (const group of Object.values(groups)) {
      if (group.id === groupId) return group
      
      if (group.children) {
        const found = findGroupInChildren(group.children, groupId)
        if (found) return found
      }
    }
    
    return null
  }
  
  const hasAnyChildrenSelected = (group) => {
    // Check subgroups
    if (group.children) {
      for (const child of group.children) {
        if (isSelected(`group:${child.id}`) || hasAnyChildrenSelected(child)) {
          return true
        }
      }
    }
    
    // Check event types
    if (group.event_types) {
      for (const eventTypeName of Object.keys(group.event_types)) {
        if (isSelected(`event_type:${eventTypeName}`)) {
          return true
        }
        
        // Check individual events of this type
        const eventType = group.event_types[eventTypeName]
        if (eventType.events) {
          for (const event of eventType.events) {
            if (isSelected(`event:${event.id}`)) {
              return true
            }
          }
        }
      }
    }
    
    return false
  }
  
  
  // Expansion management
  const toggleExpansion = (itemId) => {
    const newExpanded = new Set(expandedGroups.value)
    
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId)
    } else {
      newExpanded.add(itemId)
    }
    
    expandedGroups.value = newExpanded
  }
  
  const toggleEventTypeExpansion = (eventTypeName) => {
    const newExpanded = new Set(expandedEventTypes.value)
    
    if (newExpanded.has(eventTypeName)) {
      newExpanded.delete(eventTypeName)
    } else {
      newExpanded.add(eventTypeName)
    }
    
    expandedEventTypes.value = newExpanded
  }
  
  // Computed properties for UI
  const selectedCount = computed(() => selectedItems.value.size)
  
  const selectedGroupsForFilter = computed(() => {
    const groups = []
    const eventTypes = []
    const events = []
    
    for (const item of selectedItems.value) {
      if (item.startsWith('group:')) {
        groups.push(item.replace('group:', ''))
      } else if (item.startsWith('event_type:')) {
        eventTypes.push(item.replace('event_type:', ''))
      } else if (item.startsWith('event:')) {
        events.push(item.replace('event:', ''))
      }
    }
    
    return { groups, eventTypes, events }
  })
  
  // Clear all selections
  const clearSelections = () => {
    selectedItems.value = new Set()
  }
  
  // Bulk selection operations
  const selectAll = (groups) => {
    const newSelection = new Set()
    
    if (groups && typeof groups === 'object') {
      for (const group of Object.values(groups)) {
        newSelection.add(`group:${group.id}`)
      }
    }
    
    selectedItems.value = newSelection
  }
  
  const selectEventType = (eventTypeName) => {
    toggleSelection(`event_type:${eventTypeName}`)
  }
  
  const selectIndividualEvent = (eventId) => {
    toggleSelection(`event:${eventId}`)
  }
  
  return {
    // State
    selectedItems: computed(() => selectedItems.value),
    expandedGroups: computed(() => expandedGroups.value),
    expandedEventTypes: computed(() => expandedEventTypes.value),
    
    // Selection actions
    toggleSelection,
    isSelected,
    isPartiallySelected,
    selectEventType,
    selectIndividualEvent,
    
    // Expansion actions
    toggleExpansion,
    toggleEventTypeExpansion,
    
    // Bulk operations
    clearSelections,
    selectAll,
    
    // Computed values
    selectedCount,
    selectedGroupsForFilter,
    
    // Data initialization
    setGroupsData
  }
}