<template>
  <div class="mb-6">
    <!-- Primary Actions Row - Match Events View Structure -->
    <div class="flex flex-col gap-4 sm:flex-row sm:gap-4 mb-4">
      <!-- Quick Actions - Match Events View Layout -->
      <div class="flex flex-col sm:flex-row gap-3 sm:gap-3 flex-1">
        <button
          v-if="!allSubscribed"
          @click="$emit('subscribe-to-all')"
          class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 border-2 border-blue-600 hover:border-blue-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-blue-500/50 min-h-[44px]"
          :aria-label="$t('status.subscribeToAllGroups')"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span>{{ $t('controls.selectAll') }}</span>
        </button>
        
        <button
          v-if="hasSelections"
          @click="$emit('unsubscribe-from-all')"
          class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 border-2 border-gray-600 hover:border-gray-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-gray-500/50 min-h-[44px]"
          :aria-label="$t('status.unsubscribeFromAllGroups')"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
          <span>{{ $t('controls.deselectAll') }}</span>
        </button>
      </div>
      
      <!-- View Controls - Match Events View Layout -->
      <div class="flex justify-center sm:justify-end gap-3">
        <!-- Expand/Collapse Controls -->
        <div class="flex gap-2">
          <button
            v-if="!allExpanded"
            @click="$emit('expand-all')"
            class="inline-flex items-center justify-center gap-2 px-2 py-1 text-xs font-medium text-blue-600 bg-gradient-to-r from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 border border-transparent hover:border-blue-200 rounded-md opacity-75 hover:opacity-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30 dark:from-blue-900/20 dark:to-blue-800/40 dark:text-blue-300 dark:hover:from-blue-800/40 dark:hover:to-blue-900/60 dark:hover:text-blue-200"
            :aria-label="$t('status.expandAllGroups')"
          >
            <svg class="w-3 h-3 transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <span>{{ $t('controls.expandAll') }}</span>
          </button>
          
          <button
            v-if="!allCollapsed"
            @click="$emit('collapse-all')"
            class="inline-flex items-center justify-center gap-2 px-2 py-1 text-xs font-medium text-slate-500 bg-gradient-to-r from-slate-50 to-slate-100 hover:from-slate-100 hover:to-slate-200 border border-transparent hover:border-slate-300 rounded-md opacity-75 hover:opacity-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-slate-400/30 dark:from-gray-700 dark:to-gray-600 dark:text-gray-400 dark:hover:from-gray-600 dark:hover:to-gray-500 dark:hover:text-gray-300"
            :aria-label="$t('status.collapseAllGroups')"
          >
            <svg class="w-3 h-3 transition-transform duration-200 rotate-90" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <span>{{ $t('controls.collapseAll') }}</span>
          </button>
        </div>
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