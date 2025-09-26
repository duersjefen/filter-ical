<template>
  <div class="flex flex-col gap-4 mb-6">
    <!-- Action Buttons - Left/Right Aligned Groups -->
    <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
      <!-- Left: Subscription Actions -->
      <div class="flex flex-wrap gap-2 justify-center sm:justify-start">
        <button
          v-if="!allSubscribed"
          @click="$emit('subscribe-to-all')"
          class="flex items-center gap-2 px-4 py-2.5 text-sm bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all duration-200 font-medium shadow-md hover:shadow-lg active:scale-95"
          aria-label="Subscribe to all groups and select them"
        >
          <span class="text-base">📥</span>
          <span class="hidden xs:inline">Subscribe &</span>
          <span>Select All</span>
        </button>
        
        <button
          v-if="hasSelections"
          @click="$emit('unsubscribe-from-all')"
          class="flex items-center gap-2 px-4 py-2.5 text-sm border-2 border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 hover:border-red-400 dark:hover:border-red-500 transition-all duration-200 font-medium text-red-600 dark:text-red-400 hover:shadow-md active:scale-95"
          aria-label="Unsubscribe from all groups and deselect them"
        >
          <span class="text-base">📤</span>
          <span class="hidden xs:inline">Unsubscribe &</span>
          <span>Deselect All</span>
        </button>
      </div>

      <!-- Right: Expansion Actions -->
      <div class="flex flex-wrap gap-2 justify-center sm:justify-end">
        <button
          v-if="!allExpanded"
          @click="$emit('expand-all')"
          class="flex items-center gap-2 px-4 py-2.5 text-sm border-2 border-amber-300 dark:border-amber-600 bg-amber-50 dark:bg-amber-900/20 rounded-lg hover:bg-amber-100 dark:hover:bg-amber-900/30 hover:border-amber-400 dark:hover:border-amber-500 transition-all duration-200 font-medium text-amber-700 dark:text-amber-300 hover:shadow-md active:scale-95"
          aria-label="Expand all group sections to show content"
        >
          <span class="text-base">📂</span>
          <span>Expand All</span>
        </button>
        
        <button
          v-if="!allCollapsed"
          @click="$emit('collapse-all')"
          class="flex items-center gap-2 px-4 py-2.5 text-sm border-2 border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-900/20 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700/50 hover:border-slate-400 dark:hover:border-slate-500 transition-all duration-200 font-medium text-slate-700 dark:text-slate-300 hover:shadow-md active:scale-95"
          aria-label="Collapse all group sections to hide content"
        >
          <span class="text-base">📁</span>
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