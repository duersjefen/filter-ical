<template>
  <div class="preview-event-card border-b border-gray-100 dark:border-gray-600 pb-3 last:border-b-0 last:pb-0">
    <!-- Event Title -->
    <div class="font-semibold text-gray-800 dark:text-gray-200 text-sm leading-tight mb-1">
      {{ event.title }}
    </div>
    
    <!-- Event Date -->
    <div class="text-xs text-gray-600 dark:text-gray-400 font-medium mb-1 flex items-center gap-1">
      <span>📅</span>
      <span>{{ formatDateRange(event) }}</span>
    </div>
    
    <!-- Event Location -->
    <div 
      v-if="event.location" 
      class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1 mb-1"
    >
      <span>📍</span>
      <span class="truncate">{{ event.location }}</span>
    </div>
    
    <!-- Event Title (if different from main title) -->
    <div 
      v-if="showCategory && getRecurringEventKey(event) !== event.title" 
      class="text-xs text-blue-600 dark:text-blue-400 font-medium flex items-center gap-1"
    >
      <span>📂</span>
      <span class="truncate">{{ getRecurringEventKey(event) }}</span>
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