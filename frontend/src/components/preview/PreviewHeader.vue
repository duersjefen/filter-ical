<template>
  <div 
    class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-slate-100 dark:hover:bg-gray-700 transition-colors duration-200"
    :class="isExpanded ? 'rounded-t-xl' : 'rounded-xl'"
    @click="$emit('toggle')"
  >
    <!-- Mobile Layout -->
    <div class="block sm:hidden">
      <div class="flex items-center gap-3">
        <!-- Chevron icon (moved to left, matching groups card) -->
        <svg 
          class="w-4 h-4 text-gray-600 dark:text-gray-300 transition-transform duration-300 flex-shrink-0" 
          :class="{ 'rotate-90': isExpanded }"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
        
        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 flex-1">
          🔍 {{ $t('preview.eventPreview') }}
        </h3>
      </div>
      <p class="text-xs text-gray-600 dark:text-gray-400 text-center mt-2">
        {{ $t(`preview.${eventCountInfo.mobileMessage}`, { count: eventCountInfo.count }) }}
      </p>
    </div>

    <!-- Desktop Layout -->
    <div class="hidden sm:flex items-center gap-3">
      <!-- Chevron icon (moved to left, matching groups card) -->
      <svg 
        class="w-4 h-4 text-gray-600 dark:text-gray-300 transition-transform duration-300 flex-shrink-0" 
        :class="{ 'rotate-90': isExpanded }"
        fill="currentColor" 
        viewBox="0 0 20 20"
      >
        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
      </svg>
      
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-1">
          🔍 {{ $t('preview.eventPreview') }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ $t(`preview.${eventCountInfo.desktopMessage}`, { count: eventCountInfo.count }) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  eventCount: { type: Number, required: true },
  isExpanded: { type: Boolean, default: false }
})

const emit = defineEmits(['toggle'])

// Compute event count and message for selected recurring events
const eventCountInfo = computed(() => {
  return {
    count: props.eventCount,
    mobileMessage: 'eventsSelected',
    desktopMessage: 'eventsFromSelection'
  }
})
</script>