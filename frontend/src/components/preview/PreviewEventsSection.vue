<template>
  <div 
    v-if="hasPreviewEvents" 
    class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden"
  >
    <!-- Header -->
    <PreviewHeader
      :event-count="previewEventCount"
      :is-expanded="isExpanded"
      @toggle="isExpanded = !isExpanded"
    />
    
    <!-- Content -->
    <div v-if="isExpanded">
      <!-- Controls -->
      <PreviewControls
        :view-mode="viewMode"
        @update:view-mode="viewMode = $event"
      />
      
      <!-- Content Container with scroll -->
      <div class="max-h-[600px] overflow-y-auto">
        <!-- List View -->
        <PreviewList
          v-if="viewMode === 'list'"
          :events="sortedPreviewEvents"
          :show-category="true"
          :format-date-range="formatDateRange"
          :get-recurring-event-key="getRecurringEventKey"
        />
        
        <!-- Grouped Views -->
        <PreviewGroups
          v-else
          :groups="groupedEvents"
          :view-mode="viewMode"
          :format-date-range="formatDateRange"
          :get-recurring-event-key="getRecurringEventKey"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { formatDateRange } from '@/utils/dateFormatting'
import { usePreview } from '@/composables/usePreview'
import PreviewHeader from '@/components/preview/PreviewHeader.vue'
import PreviewControls from '@/components/preview/PreviewControls.vue'
import PreviewList from '@/components/preview/PreviewList.vue'
import PreviewGroups from '@/components/preview/PreviewGroups.vue'

const props = defineProps({
  getRecurringEventKey: { type: Function, required: true }
})

// Use the preview composable with centralized selection store
const {
  sortedPreviewEvents,
  hasPreviewEvents,
  previewEventCount,
  groupEventsByCategory,
  groupEventsByMonth
} = usePreview()


// Local state
const isExpanded = ref(false)
const viewMode = ref('list')

// Computed properties for grouped data
const groupedEvents = computed(() => {
  if (viewMode.value === 'category') {
    return groupEventsByCategory(sortedPreviewEvents.value, props.getRecurringEventKey)
  } else if (viewMode.value === 'month') {
    return groupEventsByMonth(sortedPreviewEvents.value)
  }
  return []
})
</script>