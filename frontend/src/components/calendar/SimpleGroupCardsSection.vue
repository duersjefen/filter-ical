<template>
  <div v-if="hasGroups" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
    <!-- Header -->
    <div class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">🏷️ Event Groups</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
        {{ selectedEventTypesCount > 0
          ? `${selectedEventTypesCount} event types selected`
          : 'Click groups to expand and select event types' }}
      </p>
    </div>

    <div class="p-6">
      <!-- Filter Mode Toggle -->
      <div class="flex justify-center mb-6">
        <button
          @click="$emit('switch-filter-mode', filterMode === 'include' ? 'exclude' : 'include')"
          class="px-4 py-2 border-2 rounded-lg font-semibold transition-all duration-200 hover:shadow-md"
          :class="filterMode === 'include'
            ? 'border-green-400 bg-green-50 text-green-700 hover:bg-green-100'
            : 'border-red-400 bg-red-50 text-red-700 hover:bg-red-100'"
        >
          {{ filterMode === 'include' ? '✅ Include Selected' : '❌ Exclude Selected' }}
        </button>
      </div>

      <!-- Selection Actions -->
      <div class="flex justify-between items-center mb-6">
        <div class="flex space-x-3">
          <button
            @click="clearAll"
            class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium text-gray-600"
            :disabled="selectedEventTypesCount === 0"
            :class="selectedEventTypesCount === 0 ? 'opacity-50 cursor-not-allowed' : ''"
          >
            Clear All
          </button>
          <button
            @click="selectAll"
            class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Select All Groups
          </button>
        </div>
        
        <div class="text-sm">
          <span class="text-gray-600 dark:text-gray-400">{{ Object.keys(groups || {}).length + (otherActivitiesGroup ? 1 : 0) }} groups</span>
          <span v-if="selectedEventTypesCount > 0" class="ml-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">
            {{ selectedEventTypesCount }} selected
          </span>
        </div>
      </div>

      <!-- Group Cards Grid - Following existing EventTypeCardsSection pattern -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <GroupCard
          v-for="group in Object.values(groups || {})"
          :key="group.id"
          :group="group"
          :selected-event-types="selectedEventTypes"
          :expanded-groups="expandedGroups"
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
          @toggle-group="handleGroupToggle"
          @toggle-event-type="handleEventTypeToggle"
          @expand-group="handleGroupExpansion"
        />
      </div>
      
      <!-- Selection Summary -->
      <div v-if="selectedEventTypesCount > 0" class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
        <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">Selection Summary</h4>
        <div class="text-sm text-blue-700 dark:text-blue-300">
          <div>
            <strong>{{ filterMode === 'include' ? 'Including' : 'Excluding' }}:</strong> 
            {{ selectedEventTypes.slice(0, 3).join(', ') }}
            <span v-if="selectedEventTypes.length > 3">
              and {{ selectedEventTypes.length - 3 }} more event types
            </span>
          </div>
        </div>
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
  ungroupedEventTypes: { type: Array, default: () => [] }
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