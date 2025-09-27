<template>
  <div class="preview-event-card border-b border-gray-100 dark:border-gray-600 pb-2 last:border-b-0 last:pb-0">
    <!-- Event Title -->
    <div class="font-semibold text-gray-900 dark:text-gray-100 text-sm leading-tight mb-1">
      {{ event.title.trim() }}
    </div>
    
    <!-- Event Details in single line -->
    <div class="text-xs text-gray-600 dark:text-gray-400 leading-tight">
      <span class="font-medium">{{ formatDateRange(event) }}</span><span v-if="event.location" class="text-gray-500 dark:text-gray-400 ml-1">• {{ event.location.trim() }}</span>
    </div>
    
    <!-- Event Category (if different from main title) -->
    <div 
      v-if="showCategory && getRecurringEventKey(event) !== event.title" 
      class="text-xs text-blue-600 dark:text-blue-400 font-medium mt-0.5"
    >
      <span class="truncate">📂 {{ getRecurringEventKey(event) }}</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  event: { type: Object, required: true },
  showCategory: { type: Boolean, default: true },
  formatDateRange: { type: Function, required: true },
  getRecurringEventKey: { type: Function, required: true }
})
</script>