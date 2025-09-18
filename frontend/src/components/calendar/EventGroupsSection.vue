<template>
  <div v-if="hasGroups" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4">
    <!-- Header -->
    <div class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-6 py-4 border-b">
      <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">🏷️ Event Groups</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        {{ selectedGroups.size > 0
          ? `${selectedGroups.size} groups selected`
          : 'Select groups to filter by event types' }}
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

      <!-- Groups Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div
          v-for="group in Object.values(groups || {})"
          :key="group.id"
          class="border-2 rounded-lg transition-all duration-200 cursor-pointer"
          :class="selectedGroups.has(group.id)
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'"
          @click="$emit('toggle-group', group.id)"
        >
          <div class="p-4">
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-semibold text-gray-900 dark:text-gray-100">{{ group.name }}</h4>
              <div
                class="w-4 h-4 rounded-full"
                :style="{ backgroundColor: group.color }"
              ></div>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                {{ getTotalEventCount(group) }} events
              </span>
              <div
                class="w-5 h-5 rounded border-2 flex items-center justify-center"
                :class="selectedGroups.has(group.id)
                  ? 'bg-blue-500 border-blue-500 text-white'
                  : 'border-gray-300 dark:border-gray-600'"
              >
                <span v-if="selectedGroups.has(group.id)">✓</span>
              </div>
            </div>
          </div>

          <!-- Event Types List (expandable) -->
          <div v-if="expandedGroups.has(group.id)" class="border-t border-gray-200 dark:border-gray-600 p-4">
            <div
              v-for="eventType in getGroupEventTypes(group)"
              :key="eventType"
              class="flex items-center justify-between p-2 rounded bg-gray-50 dark:bg-gray-700 mb-1"
            >
              <span class="text-sm text-gray-700 dark:text-gray-300 font-medium">{{ eventType }}</span>
              <div class="w-4 h-4 rounded bg-blue-100 dark:bg-blue-800 flex items-center justify-center">
                <span class="text-xs text-blue-600 dark:text-blue-300">📅</span>
              </div>
            </div>
          </div>

          <!-- Expand/Collapse Button -->
          <div v-if="getGroupEventTypes(group).length > 0" class="border-t border-gray-200 dark:border-gray-600 p-2">
            <button
              @click.stop="toggleGroupExpansion(group.id)"
              class="w-full text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
            >
              {{ expandedGroups.has(group.id) ? '▲ Hide Event Types' : '▼ Show Event Types' }}
            </button>
          </div>
        </div>
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
              class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
            >
              <div class="flex-1">
                <div class="font-medium text-gray-900 dark:text-gray-100">{{ eventType }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">
                  Event type not assigned to any group
                </div>
              </div>
              
              <div class="ml-4">
                <span class="px-3 py-2 bg-orange-100 dark:bg-orange-800 text-orange-700 dark:text-orange-200 rounded-lg text-sm">
                  Unassigned
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  hasGroups: { type: Boolean, default: false },
  groups: { type: Object, default: () => ({}) },
  selectedGroups: { type: Set, default: () => new Set() },
  filterMode: { type: String, default: 'include' },
  ungroupedEventTypes: { type: Array, default: () => [] }
})

const emit = defineEmits([
  'toggle-group',
  'switch-filter-mode'
])

// Local state for group expansion
const expandedGroups = ref(new Set())

const toggleGroupExpansion = (groupId) => {
  const newExpanded = new Set(expandedGroups.value)
  if (newExpanded.has(groupId)) {
    newExpanded.delete(groupId)
  } else {
    newExpanded.add(groupId)
  }
  expandedGroups.value = newExpanded
}

// Calculate total event count for a group (including children)
const getTotalEventCount = (group) => {
  if (!group) return 0
  
  // Count events in this group
  let totalEvents = (group.events || []).length
  
  // Count events in all children recursively
  if (group.children && Array.isArray(group.children)) {
    totalEvents += group.children.reduce((sum, child) => {
      return sum + getTotalEventCount(child)
    }, 0)
  }
  
  return totalEvents
}

// Extract unique event types from a group and its children
const getGroupEventTypes = (group) => {
  if (!group) return []
  
  const eventTypes = new Set()
  
  // Add event types from this group's events
  if (group.events && Array.isArray(group.events)) {
    group.events.forEach(event => {
      if (event.event_type) {
        eventTypes.add(event.event_type)
      }
    })
  }
  
  // Add event types from children recursively
  if (group.children && Array.isArray(group.children)) {
    group.children.forEach(child => {
      const childEventTypes = getGroupEventTypes(child)
      childEventTypes.forEach(type => eventTypes.add(type))
    })
  }
  
  return Array.from(eventTypes)
}

// Note: Manual event assignment removed - groups now contain event types, not individual events
</script>