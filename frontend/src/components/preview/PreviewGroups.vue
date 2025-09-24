<template>
  <div class="p-4">
    <div class="flex flex-col gap-6">
      <div 
        v-for="group in groups" 
        :key="group.name"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
      >
        <!-- Group Header -->
        <div 
          @click="toggleGroupExpansion(group.name)"
          class="px-4 py-3 flex justify-between items-center cursor-pointer transition-all"
          :class="getGroupHeaderClass(viewMode)"
        >
          <div class="flex items-center gap-3">
            <svg 
              class="w-4 h-4 transition-transform duration-300" 
              :class="{ 'rotate-90': expandedGroups.has(group.name) }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <h4 class="font-semibold text-base m-0">{{ group.name }}</h4>
          </div>
          <span class="bg-white/20 px-2 py-1 rounded-full text-xs font-medium">
            {{ group.events.length }}
          </span>
        </div>
        
        <!-- Group Content -->
        <div v-if="expandedGroups.has(group.name)" class="p-4">
          <div class="flex flex-col gap-3">
            <PreviewEventCard
              v-for="event in group.events.slice(0, maxEventsPerGroup)" 
              :key="event.uid"
              :event="event"
              :show-category="showCategoryInGroups"
              :format-date-range="formatDateRange"
              :get-recurring-event-key="getRecurringEventKey"
            />
            
            <!-- Show more indicator -->
            <div 
              v-if="group.events.length > maxEventsPerGroup" 
              class="text-center text-gray-500 dark:text-gray-400 italic p-3 bg-gray-100 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 text-sm font-medium mt-3"
            >
              {{ $t('preview.andMoreEvents', { count: group.events.length - maxEventsPerGroup }) }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="groups.length === 0" class="text-center py-8 px-4 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
        <div class="text-4xl mb-3">📂</div>
        <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
          {{ $t('preview.noGroupsToShow') }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ $t('preview.selectEventsToSeeGroupedPreview') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import PreviewEventCard from './PreviewEventCard.vue'

const props = defineProps({
  groups: { type: Array, default: () => [] },
  viewMode: { type: String, default: 'category' },
  maxEventsPerGroup: { type: Number, default: 10 },
  formatDateRange: { type: Function, required: true },
  getRecurringEventKey: { type: Function, required: true }
})

// State for tracking which groups are expanded
const expandedGroups = ref(new Set())

// Category vs Month view should show category differently
const showCategoryInGroups = computed(() => props.viewMode === 'month')

// Watch for view mode changes and reset expanded state
watch(() => props.viewMode, () => {
  expandedGroups.value.clear()
})

// Toggle group expansion
const toggleGroupExpansion = (groupName) => {
  if (expandedGroups.value.has(groupName)) {
    expandedGroups.value.delete(groupName)
  } else {
    expandedGroups.value.add(groupName)
  }
}

// Get appropriate styling for group headers based on view mode
const getGroupHeaderClass = (viewMode) => {
  const baseClass = "text-white hover:shadow-md transition-all"
  
  if (viewMode === 'category') {
    return `${baseClass} bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 hover:from-blue-600 hover:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800`
  } else if (viewMode === 'month') {
    return `${baseClass} bg-gradient-to-r from-green-500 to-green-600 dark:from-green-600 dark:to-green-700 hover:from-green-600 hover:to-green-700 dark:hover:from-green-700 dark:hover:to-green-800`
  }
  
  return `${baseClass} bg-gradient-to-r from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 hover:from-purple-600 hover:to-purple-700 dark:hover:from-purple-700 dark:hover:to-purple-800`
}
</script>