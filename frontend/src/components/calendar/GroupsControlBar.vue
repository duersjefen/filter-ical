<template>
  <div class="flex justify-between items-center mb-6">
    <!-- Left Side: Action Buttons -->
    <div class="flex space-x-3">
      <button
        @click="$emit('clear-all')"
        class="px-4 py-2 text-sm border border-blue-300 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors font-medium text-blue-600 dark:text-blue-400"
        :disabled="!hasSelections"
        :class="!hasSelections ? 'opacity-50 cursor-not-allowed' : ''"
      >
        Clear All
      </button>
      
      <button
        @click="$emit('subscribe-all')"
        class="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
      >
        📁 Subscribe to All Groups
      </button>
      
      <button
        v-if="!allExpanded"
        @click="$emit('expand-all')"
        class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium text-gray-700 dark:text-gray-300"
      >
        📂 Expand All Groups
      </button>
      
      <button
        v-if="!allCollapsed"
        @click="$emit('collapse-all')"
        class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium text-gray-700 dark:text-gray-300"
      >
        📁 Collapse All Groups
      </button>
    </div>
    
    <!-- Right Side: Stats and Filter Toggle -->
    <div class="flex items-center space-x-4">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        {{ groupStatsText }}
      </div>
      
      <!-- Filter Mode Toggle -->
      <button
        @click="$emit('toggle-filter-mode')"
        class="px-3 py-1 text-sm rounded-md transition-colors hover:scale-105 active:scale-95"
        :class="filterMode === 'include'
          ? 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-300'
          : 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-300'"
      >
        {{ filterMode === 'include' ? '✅ Include' : '❌ Exclude' }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  hasSelections: {
    type: Boolean,
    default: false
  },
  allExpanded: {
    type: Boolean,
    default: false
  },
  allCollapsed: {
    type: Boolean,
    default: true
  },
  groupStatsText: {
    type: String,
    default: '0 groups'
  },
  filterMode: {
    type: String,
    default: 'include'
  }
})

defineEmits([
  'clear-all',
  'subscribe-all', 
  'expand-all',
  'collapse-all',
  'toggle-filter-mode'
])
</script>