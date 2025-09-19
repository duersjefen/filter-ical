<template>
  <div v-if="hasGroups" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mb-4">
    <!-- Minimalistic Header -->
    <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">Event Groups</h3>
        <div class="flex items-center gap-3">
          <!-- Filter Mode Toggle - Compact -->
          <button
            @click="$emit('switch-filter-mode', filterMode === 'include' ? 'exclude' : 'include')"
            class="px-3 py-1 text-sm rounded-md transition-colors"
            :class="filterMode === 'include'
              ? 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-300'
              : 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-300'"
          >
            {{ filterMode === 'include' ? 'Include' : 'Exclude' }}
          </button>
          
          <!-- Selection count badge -->
          <span v-if="selectedEventTypesCount > 0" class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full dark:bg-blue-900/30 dark:text-blue-300">
            {{ selectedEventTypesCount }}
          </span>
        </div>
      </div>
    </div>

    <div class="p-4">
      <!-- Compact Actions -->
      <div class="flex justify-between items-center mb-4">
        <div class="flex space-x-2">
          <button
            @click="clearAll"
            class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700"
            :disabled="selectedEventTypesCount === 0"
            :class="selectedEventTypesCount === 0 ? 'opacity-50 cursor-not-allowed' : ''"
          >
            Clear
          </button>
          <button
            @click="selectAll"
            class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors dark:text-blue-400 dark:hover:text-blue-300 dark:hover:bg-blue-900/30"
          >
            Select All
          </button>
        </div>
        
        <span class="text-xs text-gray-500 dark:text-gray-400">
          {{ Object.keys(groups || {}).length + (otherActivitiesGroup ? 1 : 0) }} groups
        </span>
      </div>

      <!-- Group Cards Grid - Following existing EventTypeCardsSection pattern -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <GroupCard
          v-for="group in Object.values(groups || {})"
          :key="group.id"
          :group="group"
          :selected-event-types="selectedEventTypes"
          :expanded-groups="expandedGroups"
          :domain-id="domainId"
          @toggle-group="handleGroupToggle"
          @toggle-event-type="handleEventTypeToggle"
          @expand-group="handleGroupExpansion"
        />
        
        <!-- Other Activities Group for ungrouped event types -->
        <GroupCard
          v-if="otherActivitiesGroup"
          :key="otherActivitiesGroup.id"
          :group="otherActivitiesGroup"
          :selected-event-types="selectedEventTypes"
          :expanded-groups="expandedGroups"
          :domain-id="domainId"
          @toggle-group="handleGroupToggle"
          @toggle-event-type="handleEventTypeToggle"
          @expand-group="handleGroupExpansion"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import GroupCard from './GroupCard.vue'
import { useSimpleGroupSelection } from '../../composables/useSimpleGroupSelection'

const props = defineProps({
  hasGroups: { type: Boolean, default: false },
  groups: { type: Object, default: () => ({}) },
  filterMode: { type: String, default: 'include' },
  ungroupedEventTypes: { type: Array, default: () => [] },
  domainId: { type: String, required: true }
})

const emit = defineEmits([
  'switch-filter-mode',
  'selection-changed'
])

// Use the simplified selection composable
const {
  selectedEventTypes,
  expandedGroups,
  toggleEventType,
  toggleGroupExpansion,
  toggleGroupSelection,
  clearAllSelections,
  selectAllGroups,
  selectedCount
} = useSimpleGroupSelection()

// Computed
const selectedEventTypesCount = computed(() => selectedCount.value)

// Create virtual "Other Activities" group from ungrouped event types
const otherActivitiesGroup = computed(() => {
  if (!props.ungroupedEventTypes || props.ungroupedEventTypes.length === 0) {
    return null
  }
  
  // Transform ungrouped event types into event_types format
  const eventTypes = {}
  props.ungroupedEventTypes.forEach(eventType => {
    eventTypes[eventType.name] = {
      name: eventType.name,
      count: eventType.count,
      events: []
    }
  })
  
  return {
    id: 'group_other_activities',
    name: '📦 Other Activities',
    description: 'Events not assigned to specific groups',
    color: '#6B7280', // gray-500
    parent_group_id: null,
    event_types: eventTypes
  }
})

// Watch for selection changes and emit to parent
const emitSelectionChange = () => {
  emit('selection-changed', selectedEventTypes.value)
}

// Event handlers  
const handleGroupToggle = (groupId) => {
  const group = props.groups[groupId]
  if (group) {
    toggleGroupSelection(group)
    emitSelectionChange()
  }
}

const handleEventTypeToggle = (eventType) => {
  toggleEventType(eventType)
  emitSelectionChange()
}

const handleGroupExpansion = (groupId) => {
  toggleGroupExpansion(groupId)
}

const clearAll = () => {
  clearAllSelections()
  emitSelectionChange()
}

const selectAll = () => {
  selectAllGroups(props.groups)
  emitSelectionChange()
}
</script>