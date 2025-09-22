<template>
  <div class="border-t border-gray-200 dark:border-gray-600 bg-gray-25 dark:bg-gray-800">
    <div class="p-3 space-y-1">
      <div
        v-for="event in events"
        :key="event.id"
        class="flex items-center justify-between p-2 text-sm bg-white dark:bg-gray-700 rounded border border-gray-100 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-650 transition-colors"
      >
        <div class="flex-1">
          <div class="font-medium text-gray-900 dark:text-gray-100">{{ event.title }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>{{ formatEventTime(event.start, event.end) }}</span>
            <span v-if="event.location" class="ml-2">📍 {{ event.location }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  events: {
    type: Array,
    default: () => []
  }
})

// Simple event time formatting
const formatEventTime = (start, end) => {
  try {
    const startDate = new Date(start)
    const endDate = new Date(end)
    
    const formatOptions = {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }
    
    const startFormatted = startDate.toLocaleDateString('en-US', formatOptions)
    const endTime = endDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    
    return `${startFormatted} - ${endTime}`
  } catch (error) {
    return 'Invalid date'
  }
}
</script>