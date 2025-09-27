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
    <div v-if="props.showGroupsSection" class="p-3 sm:p-4">
      <!-- Control Bar Component -->
      <GroupsControlBar
        :has-selections="hasSelections"
        :all-expanded="allGroupsExpanded"
        :all-collapsed="allGroupsCollapsed"
        :all-subscribed="allEventsSelected(allGroups, [])"
        :total-groups="Object.keys(props.groups || {}).length"
        :subscribed-count="subscribedGroups.size"
        :group-stats-text="getGroupBreakdownSummary()"
        @unsubscribe-from-all="unsubscribeAndDeselectAllGroups"
        @subscribe-to-all="subscribeAndSelectAllGroups"
        @expand-all="expandAllGroups"
        @collapse-all="collapseAllGroups"
      />

      <!-- Groups Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4 items-start">
        <!-- All Groups (sorted by event count, descending) -->
        <GroupCard
          v-for="group in sortedGroups"
          :key="group.id"
          :group="group"
          :selected-recurring-events="selectedRecurringEvents"
          :subscribed-groups="subscribedGroups"
          :expanded-groups="expandedGroups"
          :domain-id="domainId || 'default'"
          @toggle-group="toggleGroupSubscription"
          @toggle-recurring-event="toggleRecurringEvent"
          @expand-group="toggleExpansion"
          @subscribe-to-group="toggleGroupSubscription"
          @select-all-recurring-events="handleSelectAllRecurringEvents"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useSelection } from '../../composables/useSelection'
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
  selectedRecurringEvents,
  subscribeToGroup,
  unsubscribeFromGroup,
  toggleRecurringEvent,
  clearSelection,
  isRecurringEventEffectivelySelected,
  getSelectionSummary,
  expandedGroups,
  toggleGroupExpansion,
  expandAllGroups,
  collapseAllGroups,
  handleSelectAllRecurringEvents,
  allEventsSelected,
  getGroupBreakdownSummary,
  subscribeAndSelectAllGroups,
  unsubscribeAndDeselectAllGroups
} = useSelection()

// All groups are now real groups (including auto-created ones from backend)
// No virtual group logic needed - backend handles auto-grouping

// Computed properties for UI state  
const allGroups = computed(() => {
  return { ...(props.groups || {}) }
})

// Sort groups with auto-groups last, then by event count (descending)
const sortedGroups = computed(() => {
  const groupsArray = Object.values(allGroups.value)
  
  return groupsArray.sort((a, b) => {
    // Calculate total events for group a
    const totalEventsA = a.recurring_events ? 
      a.recurring_events.reduce((sum, recurringEvent) => sum + (recurringEvent.event_count || 0), 0) : 0
    
    // Calculate total events for group b  
    const totalEventsB = b.recurring_events ?
      b.recurring_events.reduce((sum, recurringEvent) => sum + (recurringEvent.event_count || 0), 0) : 0
    
    // Check if groups are auto-groups (high numeric IDs)
    const aIsAuto = a.id >= 9998
    const bIsAuto = b.id >= 9998
    
    // Auto-groups always come last
    if (aIsAuto && !bIsAuto) return 1   // a is auto, b is regular -> a comes after b
    if (!aIsAuto && bIsAuto) return -1  // a is regular, b is auto -> a comes before b
    
    // Within same type (both auto or both regular), sort by event count descending
    return totalEventsB - totalEventsA
  })
})

const effectiveSelectedRecurringEvents = computed(() => {
  // Combine individual selections with subscribed group selections
  const selected = [...selectedRecurringEvents.value]
  
  for (const groupId of subscribedGroups.value) {
    const group = allGroups.value[groupId]
    if (group && group.recurring_events) {
      for (const recurringEvent of group.recurring_events) {
        if (!selected.includes(recurringEvent.title)) {
          selected.push(recurringEvent.title)
        }
      }
    }
  }
  
  return selected
})

const hasSelections = computed(() => {
  return subscribedGroups.value.size > 0 || selectedRecurringEvents.value.length > 0
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

const getGroupRecurringEvents = (group) => {
  if (!group || !group.recurring_events) return []
  return group.recurring_events.filter(recurringEvent => {
    return recurringEvent.event_count > 0
  }).map(recurringEvent => recurringEvent.title)
}


// handleSelectAllRecurringEvents is now provided by unified selection system

// getGroupBreakdownSummary is now provided by unified selection system

const getDetailedGroupSummary = () => {
  // Create detailed group status display
  const groupSummaries = []
  
  Object.entries(allGroups.value).forEach(([groupId, group]) => {
    const isSubscribed = subscribedGroups.value.has(groupId)
    const groupRecurringEvents = getGroupRecurringEvents(group)
    const selectedInGroup = groupRecurringEvents.filter(recurringEvent => 
      selectedRecurringEvents.value.includes(recurringEvent)
    ).length
    
    const checkbox = isSubscribed ? '☑' : '☐'
    const name = group.name || 'Unnamed Group'
    const summary = `${checkbox} ${selectedInGroup}/${groupRecurringEvents.length} ${name}`
    
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
watch([subscribedGroups, selectedRecurringEvents], () => {
  emit('selection-changed', {
    subscribedGroups: Array.from(subscribedGroups.value),
    groups: Array.from(subscribedGroups.value), // Legacy compatibility
    recurringEvents: selectedRecurringEvents.value,
    events: effectiveSelectedRecurringEvents.value
  })
}, { deep: true })
</script>