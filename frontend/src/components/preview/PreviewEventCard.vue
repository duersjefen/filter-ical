<template>
  <div class="preview-event-item py-1 px-3 border-b border-gray-100 dark:border-gray-700 last:border-b-0">
    <!-- Optimized Single Line Layout -->
    <div class="flex items-center gap-2 min-h-[20px]">
      <!-- Event Title -->
      <div class="font-semibold text-gray-900 dark:text-gray-100 text-sm truncate flex-1 leading-tight">
        {{ event.title.trim() }}
      </div>
      
      <!-- Compact Date -->
      <div class="text-xs text-gray-600 dark:text-gray-400 font-mono whitespace-nowrap tabular-nums">
        {{ formatCompactDate(event) }}
      </div>
    </div>
    
    <!-- Secondary Info (only if present and space allows) -->
    <div v-if="hasSecondaryInfo" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate leading-tight">
      <span v-if="event.location" class="mr-4">📍 {{ event.location.trim() }}</span>
      <span v-if="showCategory && getRecurringEventKey(event) !== event.title" class="text-blue-600 dark:text-blue-400 font-medium">📂 {{ getRecurringEventKey(event) }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  event: { type: Object, required: true },
  showCategory: { type: Boolean, default: true },
  formatDateRange: { type: Function, required: true },
  getRecurringEventKey: { type: Function, required: true }
})

// Check if we have secondary info to show
const hasSecondaryInfo = computed(() => {
  return props.event.location || (props.showCategory && props.getRecurringEventKey(props.event) !== props.event.title)
})

// Format date in a more compact way with better readability
const formatCompactDate = (event) => {
  const date = new Date(event.start || event.dtstart)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const eventDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  
  // Calculate days difference
  const diffTime = eventDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  // Format time part with better spacing
  const timeStr = date.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: false 
  })
  
  // Smart date formatting based on proximity with consistent spacing
  if (diffDays === 0) {
    return `Today·${timeStr}`
  } else if (diffDays === 1) {
    return `Tomorrow·${timeStr}`
  } else if (diffDays === -1) {
    return `Yesterday·${timeStr}`
  } else if (diffDays > 0 && diffDays <= 7) {
    return `${date.toLocaleDateString('en-US', { weekday: 'short' })}·${timeStr}`
  } else if (diffDays >= -7 && diffDays < 0) {
    return `${date.toLocaleDateString('en-US', { weekday: 'short' })}·${timeStr}`
  } else {
    // For dates further away, show month/day with year if needed
    const monthDay = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    const currentYear = now.getFullYear()
    const eventYear = date.getFullYear()
    
    if (eventYear !== currentYear) {
      return `${monthDay}·${eventYear}·${timeStr}`
    } else {
      return `${monthDay}·${timeStr}`
    }
  }
}
</script>