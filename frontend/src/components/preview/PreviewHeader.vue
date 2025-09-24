<template>
  <div 
    class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-slate-100 dark:hover:bg-gray-700 transition-colors duration-200"
    :class="isExpanded ? 'rounded-t-xl' : 'rounded-xl'"
    @click="$emit('toggle')"
  >
    <!-- Mobile Layout -->
    <div class="block sm:hidden">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
          🔍 {{ $t('preview.eventPreview') }}
        </h3>
        <button class="flex-shrink-0 p-2 rounded-full bg-white/50 dark:bg-gray-600/50 hover:bg-white dark:hover:bg-gray-600 transition-all duration-200">
          <svg 
            class="w-5 h-5 text-gray-600 dark:text-gray-300 transition-transform duration-200" 
            :class="{ 'rotate-180': isExpanded }"
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
      <p class="text-xs text-gray-600 dark:text-gray-400 text-center mt-2">
        {{ $t(`preview.${eventCountInfo.mobileMessage}`, { count: eventCountInfo.count }) }}
      </p>
    </div>

    <!-- Desktop Layout -->
    <div class="hidden sm:flex items-center justify-between">
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-1">
          🔍 {{ $t('preview.eventPreview') }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ $t(`preview.${eventCountInfo.desktopMessage}`, { count: eventCountInfo.count }) }}
        </p>
      </div>
      <button class="flex-shrink-0 p-2 rounded-full bg-white/50 dark:bg-gray-600/50 hover:bg-white dark:hover:bg-gray-600 transition-all duration-200 ml-4">
        <svg 
          class="w-5 h-5 text-gray-600 dark:text-gray-300 transition-transform duration-200" 
          :class="{ 'rotate-180': isExpanded }"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
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