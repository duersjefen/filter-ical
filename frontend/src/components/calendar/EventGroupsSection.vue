<template>
  <div v-if="hasGroups" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
    <!-- Header Component -->
    <GroupsHeader 
      :selection-summary="selectionSummary" 
      :is-collapsed="!props.showGroupsSection"
      @toggle-collapse="$emit('toggle-groups-section')"
      @switch-to-types="$emit('switch-to-types')"
    />

    <!-- Collapsible Content -->
    <div v-if="props.showGroupsSection" class="p-3 sm:p-4 lg:p-6">
      <!-- Control Bar Component -->
      <GroupsControlBar
        :has-selections="hasSelections"
        :all-expanded="allGroupsExpanded"
        :all-collapsed="allGroupsCollapsed"
        :all-subscribed="allEventsSelected"
        :total-groups="Object.keys(allGroups).length"
        :subscribed-count="subscribedGroups.size"
        :group-stats-text="getGroupBreakdownSummary()"
        @unsubscribe-all="unsubscribeFromAllGroups"
        @subscribe-and-select-all="subscribeAndSelectAllGroups"
        @expand-all="expandAllGroups"
        @collapse-all="collapseAllGroups"
      />

      <!-- Groups Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <!-- Regular Groups -->
        <GroupCard
          v-for="group in Object.values(groups || {})"
          :key="group.id"
          :group="group"
          :selected-event-types="selectedEventTypes"
          :subscribed-groups="subscribedGroups"
          :expanded-groups="expandedGroups"
          :domain-id="domainId || 'default'"
          @toggle-group="toggleGroupSubscription"
          @toggle-event-type="toggleEventType"
          @expand-group="toggleExpansion"
          @subscribe-to-group="toggleGroupSubscription"
          @select-all-event-types="handleSelectAllEventTypes"
        />

        <!-- Virtual Groups (Recurring and Unique Activities) -->
        <GroupCard
          v-if="recurringActivitiesGroup"
          :key="recurringActivitiesGroup.id"
          :group="recurringActivitiesGroup"
          :selected-event-types="selectedEventTypes"
          :subscribed-groups="subscribedGroups"
          :expanded-groups="expandedGroups"
          :domain-id="domainId || 'default'"
          @toggle-group="toggleGroupSubscription"
          @toggle-event-type="toggleEventType"
          @expand-group="toggleExpansion"
          @subscribe-to-group="toggleGroupSubscription"
          @select-all-event-types="handleSelectAllEventTypes"
        />

        <GroupCard
          v-if="uniqueActivitiesGroup"
          :key="uniqueActivitiesGroup.id"
          :group="uniqueActivitiesGroup"
          :selected-event-types="selectedEventTypes"
          :subscribed-groups="subscribedGroups"
          :expanded-groups="expandedGroups"
          :domain-id="domainId || 'default'"
          @toggle-group="toggleGroupSubscription"
          @toggle-event-type="toggleEventType"
          @expand-group="toggleExpansion"
          @subscribe-to-group="toggleGroupSubscription"
          @select-all-event-types="handleSelectAllEventTypes"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useEventSelection } from '../../composables/useEventSelection'
import GroupsHeader from './GroupsHeader.vue'
import GroupsControlBar from './GroupsControlBar.vue'
import GroupCard from './GroupCard.vue'

const props = defineProps({
  hasGroups: { type: Boolean, default: false },
  groups: { type: Object, default: () => ({}) },
  ungroupedEventTypes: { type: Array, default: () => [] },
  ungroupedRecurringEventTypes: { type: Array, default: () => [] },
  ungroupedUniqueEventTypes: { type: Array, default: () => [] },
  domainId: { type: String, default: null },
  showGroupsSection: { type: Boolean, default: true }
})

const emit = defineEmits([
  'selection-changed',
  'switch-to-types',
  'toggle-groups-section'
])

// Use simplified event selection system
const {
  subscribedGroups,
  selectedEventTypes,
  subscribeToGroup,
  unsubscribeFromGroup,
  toggleEventType,
  clearSelection,
  isEventTypeEffectivelySelected,
  getSelectionSummary
} = useEventSelection()

// Local state for UI interactions
const expandedGroups = ref(new Set())

// Virtual groups for ungrouped event types
const recurringActivitiesGroup = computed(() => {
  if (!props.ungroupedRecurringEventTypes || props.ungroupedRecurringEventTypes.length === 0) {
    return null
  }
  
  const eventTypes = {}
  props.ungroupedRecurringEventTypes.forEach(eventType => {
    eventTypes[eventType.name] = {
      count: eventType.count || 0,
      is_recurring: true
    }
  })
  
  return {
    id: 'virtual-recurring',
    name: '🔄 Recurring Activities',
    description: 'Regular weekly/monthly events and recurring activities',
    event_types: eventTypes,
    color: '#f97316' // orange-500
  }
})

const uniqueActivitiesGroup = computed(() => {
  if (!props.ungroupedUniqueEventTypes || props.ungroupedUniqueEventTypes.length === 0) {
    return null
  }
  
  const eventTypes = {}
  props.ungroupedUniqueEventTypes.forEach(eventType => {
    eventTypes[eventType.name] = {
      count: eventType.count || 0,
      is_recurring: false
    }
  })
  
  return {
    id: 'virtual-unique',
    name: '📅 Unique Activities',
    description: 'One-time events and special occasions',
    event_types: eventTypes,
    color: '#3b82f6' // blue-500
  }
})

// Computed properties for UI state
const allGroups = computed(() => {
  const groups = { ...(props.groups || {}) }
  if (recurringActivitiesGroup.value) {
    groups[recurringActivitiesGroup.value.id] = recurringActivitiesGroup.value
  }
  if (uniqueActivitiesGroup.value) {
    groups[uniqueActivitiesGroup.value.id] = uniqueActivitiesGroup.value
  }
  return groups
})

const effectiveSelectedEventTypes = computed(() => {
  // Combine individual selections with subscribed group selections
  const selected = [...selectedEventTypes.value]
  
  for (const groupId of subscribedGroups.value) {
    const group = allGroups.value[groupId]
    if (group && group.event_types) {
      for (const eventType of Object.keys(group.event_types)) {
        if (!selected.includes(eventType)) {
          selected.push(eventType)
        }
      }
    }
  }
  
  return selected
})

const hasSelections = computed(() => {
  return subscribedGroups.value.size > 0 || selectedEventTypes.value.length > 0
})

const allGroupsExpanded = computed(() => {
  const totalGroups = Object.keys(allGroups.value).length
  return totalGroups > 0 && expandedGroups.value.size === totalGroups
})

const allGroupsCollapsed = computed(() => {
  return expandedGroups.value.size === 0
})

const allGroupsSubscribed = computed(() => {
  const totalGroups = Object.keys(allGroups.value).length
  return totalGroups > 0 && subscribedGroups.value.size === totalGroups
})

const allEventsSelected = computed(() => {
  // Get all available event types from all sources
  const allAvailableEventTypes = new Set()
  
  // Add event types from all groups
  Object.values(allGroups.value).forEach(group => {
    if (group.event_types) {
      Object.keys(group.event_types).forEach(eventType => {
        allAvailableEventTypes.add(eventType)
      })
    }
  })
  
  // Add ungrouped event types
  props.ungroupedEventTypes.forEach(eventType => {
    allAvailableEventTypes.add(eventType.name || eventType)
  })
  props.ungroupedRecurringEventTypes.forEach(eventType => {
    allAvailableEventTypes.add(eventType.name || eventType)
  })
  props.ungroupedUniqueEventTypes.forEach(eventType => {
    allAvailableEventTypes.add(eventType.name || eventType)
  })
  
  // Check if all available event types are effectively selected
  // (either through group subscription or individual selection)
  for (const eventType of allAvailableEventTypes) {
    if (!isEventTypeEffectivelySelected(eventType)) {
      return false
    }
  }
  
  return allAvailableEventTypes.size > 0
})

const selectionSummary = computed(() => {
  // Combine all ungrouped event types for comprehensive summary
  const allUngroupedTypes = [
    ...props.ungroupedEventTypes,
    ...props.ungroupedRecurringEventTypes,
    ...props.ungroupedUniqueEventTypes
  ]
  const summary = getSelectionSummary(allGroups.value, allUngroupedTypes)
  
  // Add compact text using our enhanced format
  const compactText = getGroupBreakdownSummary()
  
  return {
    ...summary,
    compactText
  }
})

// Methods
const toggleGroupSubscription = (groupId) => {
  const group = allGroups.value[groupId]
  if (subscribedGroups.value.has(groupId)) {
    unsubscribeFromGroup(groupId, group)
  } else {
    subscribeToGroup(groupId, group)
  }
}

const subscribeToAllGroups = () => {
  Object.entries(allGroups.value).forEach(([groupId, group]) => {
    subscribeToGroup(groupId, group)
  })
}

const unsubscribeFromAllGroups = () => {
  // Unsubscribe from all groups but keep individual event selections
  Object.entries(allGroups.value).forEach(([groupId, group]) => {
    unsubscribeFromGroup(groupId, group)
  })
}

const subscribeAndSelectAllGroups = () => {
  // Subscribe to all groups AND select all their event types (like Subscribe & Select)
  Object.entries(allGroups.value).forEach(([groupId, group]) => {
    subscribeToGroup(groupId, group)
    
    // Also select all event types in this group
    if (group && group.event_types) {
      const groupEventTypes = Object.keys(group.event_types).filter(eventType => {
        return group.event_types[eventType].count > 0
      })
      groupEventTypes.forEach(eventType => {
        if (!selectedEventTypes.value.includes(eventType)) {
          toggleEventType(eventType)
        }
      })
    }
  })
}

const toggleExpansion = (groupId) => {
  if (expandedGroups.value.has(groupId)) {
    expandedGroups.value.delete(groupId)
  } else {
    expandedGroups.value.add(groupId)
  }
}

const expandAllGroups = () => {
  Object.keys(allGroups.value).forEach(groupId => {
    expandedGroups.value.add(groupId)
  })
}

const collapseAllGroups = () => {
  expandedGroups.value.clear()
}

const getGroupEventTypes = (group) => {
  if (!group || !group.event_types) return []
  return Object.keys(group.event_types).filter(eventType => {
    return group.event_types[eventType].count > 0
  })
}


const handleSelectAllEventTypes = ({ groupId, eventTypes, selectAll }) => {
  if (selectAll) {
    // Select all event types in this group
    eventTypes.forEach(eventType => {
      if (!selectedEventTypes.value.includes(eventType)) {
        toggleEventType(eventType)
      }
    })
  } else {
    // Deselect all event types in this group
    eventTypes.forEach(eventType => {
      if (selectedEventTypes.value.includes(eventType)) {
        toggleEventType(eventType)
      }
    })
  }
}

const getGroupBreakdownSummary = () => {
  const totalGroups = Object.keys(allGroups.value).length
  const subscribedGroupsCount = subscribedGroups.value.size
  const selectedEventsCount = selectedEventTypes.value.length
  
  // Calculate total available events across all groups
  let totalAvailableEvents = 0
  Object.values(allGroups.value).forEach(group => {
    const groupEventTypes = getGroupEventTypes(group)
    totalAvailableEvents += groupEventTypes.length
  })
  
  // Calculate effective selected events (subscribed groups + individual selections)
  let effectiveSelectedEvents = selectedEventsCount
  subscribedGroups.value.forEach(groupId => {
    const group = allGroups.value[groupId]
    if (group) {
      const groupEventTypes = getGroupEventTypes(group)
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

const getDetailedGroupSummary = () => {
  // Create detailed group status display
  const groupSummaries = []
  
  Object.entries(allGroups.value).forEach(([groupId, group]) => {
    const isSubscribed = subscribedGroups.value.has(groupId)
    const groupEventTypes = getGroupEventTypes(group)
    const selectedInGroup = groupEventTypes.filter(eventType => 
      selectedEventTypes.value.includes(eventType)
    ).length
    
    const checkbox = isSubscribed ? '☑' : '☐'
    const name = group.name || 'Unnamed Group'
    const summary = `${checkbox} ${selectedInGroup}/${groupEventTypes.length} ${name}`
    
    groupSummaries.push(summary)
  })
  
  // Limit display to avoid overwhelming UI - show first 3-4 groups with "and X more"
  if (groupSummaries.length <= 4) {
    return groupSummaries.join(', ')
  } else {
    const displayed = groupSummaries.slice(0, 3)
    const remaining = groupSummaries.length - 3
    return displayed.join(', ') + `, and ${remaining} more groups`
  }
}

// Watch for changes and emit to parent
watch([subscribedGroups, selectedEventTypes], () => {
  emit('selection-changed', {
    subscribedGroups: Array.from(subscribedGroups.value),
    groups: Array.from(subscribedGroups.value), // Legacy compatibility
    eventTypes: selectedEventTypes.value,
    events: effectiveSelectedEventTypes.value
  })
}, { deep: true })
</script>