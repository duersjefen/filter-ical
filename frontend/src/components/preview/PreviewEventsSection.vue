<template>
  <div 
    v-if="hasPreviewEvents" 
    class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden hover:shadow-2xl hover:shadow-amber-500/10 dark:hover:shadow-amber-400/20 transition-all duration-500 transform"
    :class="{ 'hover:scale-[1.02]': !isExpanded }"
  >
    <!-- Header with Year Toggle -->
    <div class="relative">
      <PreviewHeader
        :event-count="previewEventCount"
        :is-expanded="isExpanded"
        @toggle="isExpanded = !isExpanded"
      />
      
      <!-- Year Grouping Toggle (only show when expanded and multiple years exist) -->
      <div v-if="isExpanded && hasMultipleYears" class="absolute top-2 right-16 z-10">
        <button
          @click="toggleYearGrouping"
          class="px-2 py-1 text-xs font-medium rounded transition-colors"
          :class="useYearGrouping 
            ? 'bg-purple-100 hover:bg-purple-200 text-purple-700 dark:bg-purple-900/40 dark:hover:bg-purple-800/60 dark:text-purple-300'
            : 'bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300'
          "
          :title="useYearGrouping ? 'Switch to Month view' : 'Switch to Year view'"
        >
          {{ useYearGrouping ? '📅 Years' : '📅 Months' }}
        </button>
      </div>
    </div>
    
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
const useYearGrouping = ref(false)

// Smart year detection - auto-enable year grouping for multi-year events
const hasMultipleYears = computed(() => {
  const events = sortedPreviewEvents.value
  if (events.length === 0) return false
  
  const years = new Set(events.map(event => {
    const date = new Date(event.start || event.dtstart)
    return date.getFullYear()
  }))
  
  return years.size > 1
})

// Auto-set year grouping based on data
watch(hasMultipleYears, (multiYear) => {
  useYearGrouping.value = multiYear
}, { immediate: true })

// Smart grouping - adapt based on year span
const smartGroupedEvents = computed(() => {
  if (useYearGrouping.value) {
    return {
      viewMode: 'year',
      groups: groupEventsByYear(sortedPreviewEvents.value)
    }
  } else {
    return {
      viewMode: 'month', 
      groups: groupEventsByMonth(sortedPreviewEvents.value)
    }
  }
})

// Toggle between year and month grouping
const toggleYearGrouping = () => {
  useYearGrouping.value = !useYearGrouping.value
}
</script>