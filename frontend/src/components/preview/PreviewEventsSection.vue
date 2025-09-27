<template>
  <div 
    v-if="hasPreviewEvents" 
    class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden hover:shadow-2xl hover:shadow-amber-500/10 dark:hover:shadow-amber-400/20 transition-all duration-500 transform"
    :class="{ 'hover:scale-[1.02]': !isExpanded }"
  >
    <!-- Header -->
    <PreviewHeader
      :event-count="previewEventCount"
      :is-expanded="isExpanded"
      @toggle="isExpanded = !isExpanded"
    />
    
    <!-- Content -->
    <div v-if="isExpanded">
      <!-- Chronological View with Month Grouping - No Scroll, Show Everything -->
      <PreviewGroups
        :groups="monthGroupedEvents"
        view-mode="month"
        :format-date-range="formatDateRange"
        :get-recurring-event-key="getRecurringEventKey"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { formatDateRange } from '@/utils/dateFormatting'
import { usePreview } from '@/composables/usePreview'
import PreviewHeader from '@/components/preview/PreviewHeader.vue'
import PreviewGroups from '@/components/preview/PreviewGroups.vue'

const props = defineProps({
  getRecurringEventKey: { type: Function, required: true }
})

// Use the preview composable with centralized selection store
const {
  sortedPreviewEvents,
  hasPreviewEvents,
  previewEventCount,
  groupEventsByMonth
} = usePreview()

// Local state
const isExpanded = ref(false)

// Always show events grouped by month
const monthGroupedEvents = computed(() => {
  return groupEventsByMonth(sortedPreviewEvents.value)
})
</script>