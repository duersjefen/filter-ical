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
        <!-- Mobile Switch Button - Compact Modern Design -->
        <button
          @click="$emit('switch-to-types')"
          class="group px-4 py-2.5 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-md hover:shadow-lg transition-all duration-200 flex items-center gap-2 transform hover:scale-105 active:scale-95"
          :title="$t('ui.switchToEventsView')"
        >
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
          </svg>
          <span class="text-sm font-semibold text-white">Events</span>
          <svg class="w-4 h-4 text-white group-hover:translate-x-0.5 transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20">
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
      <div class="flex items-center gap-3 flex-1 cursor-pointer" @click="$emit('toggle-collapse')">
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
      
      <!-- Desktop Switch Button - Enhanced Modern Design -->
      <button
        @click="$emit('switch-to-types')"
        class="group relative px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-3 ml-4 transform hover:scale-105 active:scale-95"
        :title="$t('ui.switchToEventsView')"
      >
        <!-- Switch Icon -->
        <div class="flex items-center justify-center w-8 h-8 bg-white/20 rounded-lg group-hover:bg-white/30 transition-colors duration-200">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
          </svg>
        </div>
        
        <!-- Switch Text -->
        <div class="text-left">
          <div class="text-sm font-bold text-white mb-0.5">
            Switch to Events View
          </div>
          <div class="text-xs text-blue-100">
            Browse by event types
          </div>
        </div>
        
        <!-- Arrow Icon -->
        <svg class="w-5 h-5 text-white group-hover:translate-x-1 transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20">
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