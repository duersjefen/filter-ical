<template>
  <div v-if="hasGroups" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4">
    <!-- Header -->
    <div class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-6 py-4 border-b">
      <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">🏷️ Event Groups</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        {{ selectedGroups.size > 0
          ? `${selectedGroups.size} groups selected (${selectedEvents.size} events)`
          : 'Select groups to filter events' }}
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
          v-for="group in groups"
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
                {{ group.events.length }} events
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

          <!-- Individual Events List (expandable) -->
          <div v-if="expandedGroups.has(group.id)" class="border-t border-gray-200 dark:border-gray-600 p-4">
            <div
              v-for="event in group.events"
              :key="event.id"
              class="flex items-center justify-between p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
              @click.stop="$emit('toggle-event', event.id)"
            >
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ event.title }}</span>
              <div
                class="w-4 h-4 rounded border flex items-center justify-center text-xs"
                :class="selectedEvents.has(event.id)
                  ? 'bg-green-500 border-green-500 text-white'
                  : 'border-gray-300 dark:border-gray-600'"
              >
                <span v-if="selectedEvents.has(event.id)">✓</span>
              </div>
            </div>
          </div>

          <!-- Expand/Collapse Button -->
          <div v-if="group.events.length > 0" class="border-t border-gray-200 dark:border-gray-600 p-2">
            <button
              @click.stop="toggleGroupExpansion(group.id)"
              class="w-full text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
            >
              {{ expandedGroups.has(group.id) ? '▲ Hide Events' : '▼ Show Events' }}
            </button>
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
  selectedEvents: { type: Set, default: () => new Set() },
  filterMode: { type: String, default: 'include' }
})

const emit = defineEmits([
  'toggle-group',
  'toggle-event',
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
</script>