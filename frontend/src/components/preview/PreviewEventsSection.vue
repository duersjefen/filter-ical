<template>
  <div 
    v-if="hasPreviewEvents" 
    class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden hover:shadow-2xl hover:shadow-amber-500/10 dark:hover:shadow-amber-400/20 transition-all duration-500 transform"
    :class="{ 'hover:scale-[1.02]': !isExpanded }"
  >
    <!-- Clean Header -->
    <PreviewHeader
      :event-count="previewEventCount"
      :is-expanded="isExpanded"
      @toggle="isExpanded = !isExpanded"
    />
    
    <!-- Content -->
    <div v-if="isExpanded">
      <!-- Smart Adaptive Grouping -->
      <PreviewGroups
        :groups="smartGroupedEvents.groups"
        :view-mode="smartGroupedEvents.viewMode"
        :format-date-range="formatDateRange"
        :get-recurring-event-key="getRecurringEventKey"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
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
  groupEventsByMonth,
  groupEventsByYear
} = usePreview()

// Local state
const isExpanded = ref(false)

// Smart auto-detection - automatically choose best grouping
const hasMultipleYears = computed(() => {
  const events = sortedPreviewEvents.value
  if (events.length === 0) return false
  
  const years = new Set(events.map(event => {
    const date = new Date(event.start || event.dtstart)
    return date.getFullYear()
  }))
  
  return years.size > 1
})

// Automatic smart grouping - one perfect solution
const smartGroupedEvents = computed(() => {
  if (hasMultipleYears.value) {
    // Multi-year: Use flattened year grouping
    return {
      viewMode: 'year',
      groups: groupEventsByYear(sortedPreviewEvents.value)
    }
  } else {
    // Single year: Simple month grouping
    return {
      viewMode: 'month', 
      groups: groupEventsByMonth(sortedPreviewEvents.value)
    }
  }
})
</script>