<template>
  <div v-if="hasGroups" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4">
    <!-- Header -->
    <div class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-6 py-4 border-b">
      <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">🏷️ Event Groups</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        {{ selectedCount > 0
          ? `${selectedCount} items selected`
          : 'Select groups, event types, or individual events to filter' }}
      </p>
    </div>

    <div class="p-6">
      <!-- Filter Mode Toggle -->
      <div class="flex justify-center mb-6">
        <button
          @click="$emit('switch-filter-mode', filterMode === 'include' ? 'exclude' : 'include')"
          class="px-4 py-2 border-2 rounded-lg font-semibold transition-all duration-200"
          :class="filterMode === 'include'
            ? 'border-green-400 bg-green-50 text-green-700'
            : 'border-red-400 bg-red-50 text-red-700'"
        >
          {{ filterMode === 'include' ? '✅ Include Selected' : '❌ Exclude Selected' }}
        </button>
      </div>

      <!-- Selection Actions -->
      <div class="flex justify-between items-center mb-6">
        <div class="flex space-x-3">
          <button
            @click="clearSelections"
            class="px-4 py-2 text-sm border border-blue-300 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors font-medium text-blue-600 dark:text-blue-400"
            :disabled="selectedCount === 0"
            :class="selectedCount === 0 ? 'opacity-50 cursor-not-allowed' : ''"
          >
            Clear All
          </button>
          <button
            @click="selectAllGroups"
            class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Select All Groups
          </button>
        </div>
        
        <div class="text-sm">
          <span class="text-gray-600 dark:text-gray-400">{{ Object.keys(groups || {}).length }} groups</span>
          <span v-if="selectedCount > 0" class="ml-2 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full font-medium">
            {{ selectedCount }} selected
          </span>
        </div>
      </div>

      <!-- Groups List with Recursive Components -->
      <div class="space-y-3 mb-6">
        <GroupItem
          v-for="group in Object.values(groups || {})"
          :key="group.id"
          :group="group"
          :is-selected="isSelected(`group:${group.id}`)"
          :is-partially-selected="isPartiallySelected(groups, group.id)"
          :selected-items="selectedItems"
          :expanded-groups="expandedGroups"
          :expanded-event-types="expandedEventTypes"
          @toggle-selection="handleSelection"
          @toggle-expansion="handleExpansion"
        />
      </div>
      
      <!-- Ungrouped Event Types Section -->
      <div v-if="ungroupedEventTypes && ungroupedEventTypes.length > 0" class="mt-8">
        <div class="bg-gradient-to-r from-orange-100 to-yellow-50 dark:from-orange-900/30 dark:to-yellow-800/30 px-6 py-4 border-b border-orange-200 dark:border-orange-700 rounded-t-xl">
          <h3 class="text-xl font-bold text-orange-900 dark:text-orange-100">📝 Unassigned Event Types</h3>
          <p class="text-sm text-orange-700 dark:text-orange-300">
            {{ ungroupedEventTypes.length }} event types not assigned to groups
          </p>
        </div>
        
        <div class="bg-white dark:bg-gray-800 px-6 py-4 rounded-b-xl shadow-lg border border-gray-200 dark:border-gray-700 border-t-0">
          <div class="space-y-3">
            <div
              v-for="eventType in ungroupedEventTypes"
              :key="eventType"
              class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer transition-colors"
              :class="isSelected(`event_type:${eventType}`)
                ? 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-300'
                : 'hover:bg-gray-100 dark:hover:bg-gray-600'"
              @click="handleSelection(`event_type:${eventType}`)"
            >
              <div class="flex-1">
                <div class="font-medium text-gray-900 dark:text-gray-100">{{ eventType }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">
                  Unassigned event type
                </div>
              </div>
              
              <div class="ml-4">
                <div
                  class="w-4 h-4 rounded border-2 flex items-center justify-center"
                  :class="isSelected(`event_type:${eventType}`)
                    ? 'bg-yellow-500 border-yellow-500 text-white'
                    : 'border-gray-300 dark:border-gray-600'"
                >
                  <span v-if="isSelected(`event_type:${eventType}`)" class="text-xs">✓</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Selection Summary -->
      <div v-if="selectedCount > 0" class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
        <h4 class="font-medium text-blue-900 dark:text-blue-100 mb-2">Selection Summary</h4>
        <div class="text-sm text-blue-700 dark:text-blue-300">
          <div v-if="selectedGroupsForFilter.groups.length > 0">
            <strong>Groups:</strong> {{ selectedGroupsForFilter.groups.join(', ') }}
          </div>
          <div v-if="selectedGroupsForFilter.eventTypes.length > 0">
            <strong>Event Types:</strong> {{ selectedGroupsForFilter.eventTypes.join(', ') }}
          </div>
          <div v-if="selectedGroupsForFilter.events.length > 0">
            <strong>Individual Events:</strong> {{ selectedGroupsForFilter.events.length }} selected
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import GroupItem from './GroupItem.vue'
import { useGroupSelection } from '../../composables/useGroupSelection'

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

// Use our selection composable
const {
  selectedItems,
  expandedGroups,
  expandedEventTypes,
  toggleSelection,
  isSelected,
  isPartiallySelected,
  toggleExpansion,
  clearSelections,
  selectAll,
  selectedCount,
  selectedGroupsForFilter,
  setGroupsData
} = useGroupSelection()

// Initialize with groups data when it changes
watch(() => props.groups, (newGroups) => {
  if (newGroups) {
    setGroupsData(newGroups)
  }
}, { immediate: true })

// Handle selection changes
const handleSelection = (itemId) => {
  toggleSelection(itemId, props.groups)
  // Emit the current selection to parent
  emit('selection-changed', selectedGroupsForFilter.value)
}

// Handle expansion changes
const handleExpansion = (itemId) => {
  toggleExpansion(itemId)
}

// Select all groups helper
const selectAllGroups = () => {
  selectAll(props.groups)
  emit('selection-changed', selectedGroupsForFilter.value)
}

// Watch for selection changes to emit to parent
const currentSelection = computed(() => selectedGroupsForFilter.value)
</script>