<template>
  <div class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-600 shadow-sm">
    <!-- Header label -->
    <div v-if="selectedRecurringEvents.length > 0" class="mb-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span>{{ $t('filteredCalendar.currentFilter') }}</span>
    </div>

    <div v-if="selectedRecurringEvents.length > 0" class="space-y-3">
      <!-- Recurring Events - Show all names as chips -->
      <div v-if="selectedMainRecurringEventNames.length > 0" class="flex flex-wrap gap-2">
        <div
          v-for="eventName in selectedMainRecurringEventNames"
          :key="eventName"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-lg text-xs font-medium border border-blue-200 dark:border-blue-700 shadow-sm"
        >
          <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span class="truncate max-w-[200px]">{{ eventName }}</span>
        </div>
      </div>

      <!-- Unique Events - Just show count -->
      <div v-if="selectedSingleRecurringEventNames.length > 0">
        <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-200 rounded-lg text-xs font-medium border border-emerald-200 dark:border-emerald-700 shadow-sm">
          <span>+ {{ selectedSingleRecurringEventNames.length }} unique {{ selectedSingleRecurringEventNames.length === 1 ? 'event' : 'events' }}</span>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-4">
      <div class="text-gray-500 dark:text-gray-400 text-lg mb-2">📂</div>
      <div class="text-sm text-gray-600 dark:text-gray-400 font-medium">
        {{ $t('preview.noEventsSelected') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  selectedRecurringEvents: {
    type: Array,
    required: true
  },
  mainRecurringEvents: {
    type: Array,
    default: () => []
  },
  singleRecurringEvents: {
    type: Array,
    default: () => []
  }
})

const selectedMainRecurringEventNames = computed(() => {
  const mainEventNames = props.mainRecurringEvents.map(event => event.name)
  return props.selectedRecurringEvents.filter(name => mainEventNames.includes(name))
})

const selectedSingleRecurringEventNames = computed(() => {
  const singleEventNames = props.singleRecurringEvents.map(event => event.name)
  return props.selectedRecurringEvents.filter(name => singleEventNames.includes(name))
})
</script>
