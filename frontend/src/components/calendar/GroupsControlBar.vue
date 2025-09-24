<template>
  <div class="flex flex-col gap-4 mb-6">
    <!-- Action Buttons - Organized in Groups -->
    <div class="flex flex-wrap gap-3 justify-center">
      <!-- Selection Actions Group -->
      <div v-if="!allSubscribed || !noSelections" class="flex gap-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
        <button
          v-if="hasSelections"
          @click="$emit('unsubscribe-from-all')"
          class="px-3 py-2 text-sm border border-red-300 dark:border-red-600 rounded-md hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors font-medium text-red-600 dark:text-red-400"
        >
          📤 Unsubscribe & Deselect All
        </button>
        
        <button
          v-if="!allSubscribed"
          @click="$emit('subscribe-to-all')"
          class="px-3 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
        >
          📥 Subscribe & Select All
        </button>
      </div>
      
      <!-- Expansion Actions Group -->
      <div class="flex gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600">
        <button
          v-if="!allExpanded"
          @click="$emit('expand-all')"
          class="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors font-medium text-gray-700 dark:text-gray-300"
        >
          📂 Expand All
        </button>
        
        <button
          v-if="!allCollapsed"
          @click="$emit('collapse-all')"
          class="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors font-medium text-gray-700 dark:text-gray-300"
        >
          📁 Collapse All
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
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
  allSubscribed: {
    type: Boolean,
    default: false
  },
  totalGroups: {
    type: Number,
    default: 0
  },
  subscribedCount: {
    type: Number,
    default: 0
  }
})

// Computed properties for contextual logic
const noSelections = computed(() => {
  return props.subscribedCount === 0 && !props.hasSelections
})

defineEmits([
  'unsubscribe-from-all',
  'subscribe-to-all',
  'expand-all',
  'collapse-all'
])
</script>