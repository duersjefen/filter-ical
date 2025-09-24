<template>
  <div class="p-4">
    <div class="flex flex-col gap-3">
      <PreviewEventCard
        v-for="event in events" 
        :key="event.uid"
        :event="event"
        :show-category="showCategory"
        :format-date-range="formatDateRange"
        :get-recurring-event-key="getRecurringEventKey"
      />
      
      <!-- Empty State -->
      <div v-if="events.length === 0" class="text-center py-8 px-4 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
        <div class="text-4xl mb-3">📝</div>
        <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
          {{ $t('preview.noEventsToPreview') }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ $t('preview.selectEventsToSeePreview') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import PreviewEventCard from './PreviewEventCard.vue'

const props = defineProps({
  events: { type: Array, default: () => [] },
  showCategory: { type: Boolean, default: true },
  formatDateRange: { type: Function, required: true },
  getRecurringEventKey: { type: Function, required: true }
})
</script>