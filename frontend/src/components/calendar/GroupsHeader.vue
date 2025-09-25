<template>
  <div 
    class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700"
    :class="isCollapsed ? 'rounded-xl' : 'rounded-t-xl'"
  >
    <!-- Mobile Layout -->
    <div class="block sm:hidden">
      <div class="flex items-center justify-between mb-3">
        <div class="flex-1">
          <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">
            🏷️ Groups
          </h3>
        </div>
        <!-- Mobile Switch Button -->
        <button
          @click="$emit('switch-to-types')"
          class="px-3 py-2 rounded-md border border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200 flex items-center gap-1 group"
          :title="$t('ui.switchToEventsView')"
        >
          <span class="text-xs font-medium text-gray-600 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400">📂 Types</span>
          <svg class="w-4 h-4 text-gray-400 group-hover:text-blue-500 transition-colors" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
      <!-- Status text on mobile -->
      <p class="text-xs text-gray-600 dark:text-gray-400 text-center leading-tight">
        {{ selectionSummary.selected > 0
          ? selectionSummary.compactText || selectionSummary.text
          : 'Subscribe to groups or select specific event types' }}
      </p>
    </div>

    <!-- Desktop Layout -->
    <div class="hidden sm:flex items-center justify-between">
      <!-- Left: Header Info with collapse button -->
      <div class="flex items-center gap-3 flex-1 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg p-2 -m-2 transition-colors duration-200" @click="$emit('toggle-collapse')">
        <!-- Dropdown Icon -->
        <svg 
          class="w-5 h-5 text-gray-400 transition-transform duration-200"
          :class="{ 'rotate-180': !isCollapsed }"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
        
        <div class="flex-1">
          <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            🏷️ Groups
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ selectionSummary.selected > 0
              ? selectionSummary.compactText || selectionSummary.text
              : 'Subscribe to groups or select specific event types' }}
          </p>
        </div>
      </div>
      
      <!-- Desktop Switch Button -->
      <button
        @click="$emit('switch-to-types')"
        class="px-4 py-3 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200 flex items-center gap-2 group ml-4"
        :title="$t('ui.switchToEventsView')"
      >
        <div class="text-right">
          <div class="text-sm font-semibold text-gray-700 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400">
            Switch to
          </div>
          <div class="text-xs text-gray-500 dark:text-gray-400 group-hover:text-blue-500 dark:group-hover:text-blue-300">
            📂 Events
          </div>
        </div>
        <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  selectionSummary: {
    type: Object,
    required: true,
    default: () => ({ selected: 0, total: 0, text: '0 of 0 events selected' })
  },
  isCollapsed: {
    type: Boolean,
    default: false
  }
})

defineEmits([
  'switch-to-types',
  'toggle-collapse'
])
</script>