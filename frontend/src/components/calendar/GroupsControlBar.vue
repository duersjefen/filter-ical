<template>
  <div class="flex flex-col gap-4 mb-6">
    <!-- Action Buttons - Left/Right Aligned Groups -->
    <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
      <!-- Left: Subscription Actions -->
      <div class="flex flex-wrap gap-3 justify-center sm:justify-start">
        <button
          v-if="!allSubscribed"
          @click="$emit('subscribe-to-all')"
          class="flex items-center justify-center gap-2 px-4 py-3 text-sm bg-green-500 hover:bg-green-600 text-white rounded-xl transition-all duration-300 font-semibold shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] border-2 border-green-400 hover:border-green-500"
          aria-label="Subscribe to all groups and select them"
        >
          <span class="hidden xs:inline">Subscribe &</span>
          <span>Select All</span>
        </button>
        
        <button
          v-if="hasSelections"
          @click="$emit('unsubscribe-from-all')"
          class="flex items-center justify-center gap-2 px-4 py-3 text-sm bg-red-500 hover:bg-red-600 text-white rounded-xl transition-all duration-300 font-semibold shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] border-2 border-red-400 hover:border-red-500"
          aria-label="Unsubscribe from all groups and deselect them"
        >
          <span class="hidden xs:inline">Unsubscribe &</span>
          <span>Deselect All</span>
        </button>
      </div>

      <!-- Right: Expansion Actions -->
      <div class="flex flex-wrap gap-3 justify-center sm:justify-end">
        <button
          v-if="!allExpanded"
          @click="$emit('expand-all')"
          class="flex items-center justify-center gap-2 px-4 py-3 text-sm bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl transition-all duration-300 font-semibold shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] border-2 border-indigo-400 hover:border-indigo-500"
          aria-label="Expand all group sections to show content"
        >
          <span>Expand All</span>
        </button>
        
        <button
          v-if="!allCollapsed"
          @click="$emit('collapse-all')"
          class="flex items-center justify-center gap-2 px-4 py-3 text-sm bg-gray-500 hover:bg-gray-400 text-white rounded-xl transition-all duration-300 font-semibold shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] border-2 border-gray-400 hover:border-gray-300"
          aria-label="Collapse all group sections to hide content"
        >
          <span>Collapse All</span>
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