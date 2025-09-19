import { ref, computed, watch } from 'vue'

export function useGlobalEventTypeSelection() {
  // Global state - unique event types across all groups
  const selectedEventTypes = ref([])
  const globalEventTypeRegistry = ref(new Map()) // eventType -> Set of groupIds that contain it
  
  // Build global registry of all unique event types and which groups contain them
  const buildGlobalRegistry = (groups = {}, virtualGroups = {}) => {
    const registry = new Map()
    
    // Process regular groups
    Object.entries(groups).forEach(([groupId, group]) => {
      if (group.event_types) {
        Object.keys(group.event_types).forEach(eventTypeName => {
          if (!registry.has(eventTypeName)) {
            registry.set(eventTypeName, new Set())
          }
          registry.get(eventTypeName).add(groupId)
        })
      }
    })
    
    // Process virtual groups
    Object.entries(virtualGroups).forEach(([groupId, group]) => {
      if (group && group.event_types) {
        Object.keys(group.event_types).forEach(eventTypeName => {
          if (!registry.has(eventTypeName)) {
            registry.set(eventTypeName, new Set())
          }
          registry.get(eventTypeName).add(groupId)
        })
      }
    })
    
    globalEventTypeRegistry.value = registry
    return registry
  }
  
  // Update the registry when groups data changes
  const updateRegistry = (groups, virtualGroups) => {
    buildGlobalRegistry(groups, virtualGroups)
  }
  
  // Get total count of unique event types (no duplicates)
  const getTotalUniqueEventTypesCount = () => {
    return globalEventTypeRegistry.value.size
  }
  
  // Get count of selected event types
  const getSelectedEventTypesCount = () => {
    return selectedEventTypes.value.length
  }
  
  // Check if event type is selected globally
  const isEventTypeSelected = (eventTypeName) => {
    return selectedEventTypes.value.includes(eventTypeName)
  }
  
  // Toggle event type selection globally (affects all groups that contain it)
  const toggleEventType = (eventTypeName) => {
    const index = selectedEventTypes.value.indexOf(eventTypeName)
    if (index > -1) {
      // Remove from selection
      selectedEventTypes.value.splice(index, 1)
    } else {
      // Add to selection
      selectedEventTypes.value.push(eventTypeName)
    }
  }
  
  // Set selected event types (replace entire selection)
  const setSelectedEventTypes = (eventTypes) => {
    selectedEventTypes.value = [...eventTypes]
  }
  
  // Clear all selections
  const clearAllSelections = () => {
    selectedEventTypes.value = []
  }
  
  // Get all unique event type names
  const getAllUniqueEventTypes = () => {
    return Array.from(globalEventTypeRegistry.value.keys())
  }
  
  // Select all unique event types
  const selectAllEventTypes = () => {
    selectedEventTypes.value = getAllUniqueEventTypes()
  }
  
  // Check if a group has any selected event types
  const isGroupPartiallySelected = (groupId, groups) => {
    const group = groups[groupId]
    if (!group || !group.event_types) return false
    
    const groupEventTypes = Object.keys(group.event_types)
    return groupEventTypes.some(eventType => isEventTypeSelected(eventType)) &&
           !groupEventTypes.every(eventType => isEventTypeSelected(eventType))
  }
  
  // Check if all event types in a group are selected
  const isGroupFullySelected = (groupId, groups) => {
    const group = groups[groupId]
    if (!group || !group.event_types) return false
    
    const groupEventTypes = Object.keys(group.event_types)
    return groupEventTypes.length > 0 && 
           groupEventTypes.every(eventType => isEventTypeSelected(eventType))
  }
  
  // Select/deselect all event types in a specific group
  const toggleGroupSelection = (groupId, groups) => {
    const group = groups[groupId]
    if (!group || !group.event_types) return
    
    const groupEventTypes = Object.keys(group.event_types)
    const allSelected = groupEventTypes.every(eventType => isEventTypeSelected(eventType))
    
    if (allSelected) {
      // Deselect all event types in this group
      groupEventTypes.forEach(eventType => {
        const index = selectedEventTypes.value.indexOf(eventType)
        if (index > -1) {
          selectedEventTypes.value.splice(index, 1)
        }
      })
    } else {
      // Select all event types in this group
      groupEventTypes.forEach(eventType => {
        if (!isEventTypeSelected(eventType)) {
          selectedEventTypes.value.push(eventType)
        }
      })
    }
  }
  
  // Get which groups contain a specific event type
  const getGroupsContainingEventType = (eventTypeName) => {
    const groupSet = globalEventTypeRegistry.value.get(eventTypeName)
    return groupSet ? Array.from(groupSet) : []
  }
  
  // Computed properties for reactive UI updates
  const selectedCount = computed(() => getSelectedEventTypesCount())
  const totalCount = computed(() => getTotalUniqueEventTypesCount())
  
  // Selection summary text
  const getSelectionSummaryText = () => {
    return `${selectedCount.value} of ${totalCount.value} events selected`
  }
  
  return {
    // State
    selectedEventTypes: computed(() => selectedEventTypes.value),
    globalEventTypeRegistry: computed(() => globalEventTypeRegistry.value),
    
    // Registry management
    updateRegistry,
    buildGlobalRegistry,
    
    // Counting
    getTotalUniqueEventTypesCount,
    getSelectedEventTypesCount,
    selectedCount,
    totalCount,
    getSelectionSummaryText,
    
    // Individual event type selection
    isEventTypeSelected,
    toggleEventType,
    setSelectedEventTypes,
    clearAllSelections,
    selectAllEventTypes,
    getAllUniqueEventTypes,
    
    // Group-level selection
    isGroupPartiallySelected,
    isGroupFullySelected,
    toggleGroupSelection,
    
    // Registry queries
    getGroupsContainingEventType
  }
}