<template>
  <div v-if="hasGroups" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4">
    <!-- Header Component -->
    <GroupsHeader :selection-summary="selectionSummary" />

    <div class="p-6">
      <!-- Control Bar Component -->
      <GroupsControlBar
        :has-selections="hasSelections"
        :all-expanded="allGroupsExpanded"
        :all-collapsed="allGroupsCollapsed"
        :group-stats-text="getTotalGroupsText()"
        :filter-mode="filterMode"
        @clear-all="clearSelections"
        @subscribe-all="subscribeToAllGroups"
        @expand-all="expandAllGroups"
        @collapse-all="collapseAllGroups"
        @toggle-filter-mode="handleFilterModeToggle"
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
  filterMode: { type: String, default: 'include' },
  ungroupedEventTypes: { type: Array, default: () => [] },
  ungroupedRecurringEventTypes: { type: Array, default: () => [] },
  ungroupedUniqueEventTypes: { type: Array, default: () => [] },
  domainId: { type: String, default: null }
})

const emit = defineEmits([
  'selection-changed',
  'switch-filter-mode'
])

// Use simplified event selection system
const {
  subscribedGroups,
  selectedEventTypes,
  subscribeToGroup,
  unsubscribeFromGroup,
  toggleEventType,
  clearSelections,
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

const selectionSummary = computed(() => {
  // Combine all ungrouped event types for comprehensive summary
  const allUngroupedTypes = [
    ...props.ungroupedEventTypes,
    ...props.ungroupedRecurringEventTypes,
    ...props.ungroupedUniqueEventTypes
  ]
  return getSelectionSummary(allGroups.value, allUngroupedTypes)
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

const handleFilterModeToggle = () => {
  const newMode = props.filterMode === 'include' ? 'exclude' : 'include'
  emit('switch-filter-mode', newMode)
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

const getTotalGroupsText = () => {
  const totalGroups = Object.keys(allGroups.value).length
  const selectedGroups = subscribedGroups.value.size
  const selectedTypes = selectedEventTypes.value.length
  
  if (selectedGroups > 0 || selectedTypes > 0) {
    return `${selectedGroups} groups subscribed, ${selectedTypes} types selected`
  }
  
  return `${totalGroups} ${totalGroups === 1 ? 'group' : 'groups'}`
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