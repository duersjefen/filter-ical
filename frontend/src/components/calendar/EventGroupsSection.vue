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
        :all-subscribed="allEventsSelected(allGroups, [])"
        :total-groups="Object.keys(props.groups || {}).length"
        :subscribed-count="subscribedGroups.size"
        :group-stats-text="getGroupBreakdownSummary()"
        @unsubscribe-all="unsubscribeFromAllGroups"
        @subscribe-and-select-all="subscribeAndSelectAllGroups"
        @expand-all="expandAllGroups"
        @collapse-all="collapseAllGroups"
      />

      <!-- Groups Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <!-- All Groups (including auto-created groups from backend) -->
        <GroupCard
          v-for="group in Object.values(props.groups || {})"
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useUnifiedSelection } from '../../composables/useUnifiedSelection'
import GroupsHeader from './GroupsHeader.vue'
import GroupsControlBar from './GroupsControlBar.vue'
import GroupCard from './GroupCard.vue'

const props = defineProps({
  hasGroups: { type: Boolean, default: false },
  groups: { type: Object, default: () => ({}) },
  domainId: { type: String, default: null },
  showGroupsSection: { type: Boolean, default: true }
})

const emit = defineEmits([
  'selection-changed',
  'switch-to-types',
  'toggle-groups-section'
])

// Use unified selection system (single source of truth)
const {
  subscribedGroups,
  selectedEventTypes,
  subscribeToGroup,
  unsubscribeFromGroup,
  toggleEventType,
  clearSelection,
  isEventTypeEffectivelySelected,
  getSelectionSummary,
  expandedGroups,
  toggleGroupExpansion,
  expandAllGroups,
  collapseAllGroups,
  subscribeAndSelectAllGroups,
  unsubscribeFromAllGroups,
  handleSelectAllEventTypes,
  allEventsSelected,
  getGroupBreakdownSummary
} = useUnifiedSelection()

// All groups are now real groups (including auto-created ones from backend)
// No virtual group logic needed - backend handles auto-grouping

// Computed properties for UI state  
const allGroups = computed(() => {
  return { ...(props.groups || {}) }
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

// allEventsSelected is now provided by unified selection system

const selectionSummary = computed(() => {
  // All event types are now in groups (no ungrouped types)
  const summary = getSelectionSummary(allGroups.value, [])
  
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

// unsubscribeFromAllGroups and subscribeAndSelectAllGroups are now provided by unified selection system

// Use unified expansion functions (toggleGroupExpansion, expandAllGroups, collapseAllGroups)
const toggleExpansion = toggleGroupExpansion

const getGroupEventTypes = (group) => {
  if (!group || !group.event_types) return []
  return Object.keys(group.event_types).filter(eventType => {
    return group.event_types[eventType].count > 0
  })
}


// handleSelectAllEventTypes is now provided by unified selection system

// getGroupBreakdownSummary is now provided by unified selection system

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