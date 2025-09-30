<template>
  <div class="p-4">
    <!-- Ultra-Minimal Toggle Buttons -->
    <div v-if="(viewMode === 'month' || viewMode === 'year') && groups.length > 1" class="flex justify-start mb-4">
      <div class="flex gap-2 text-xs">
        <button
          v-if="!allExpanded"
          @click="expandAll"
          class="inline-flex items-center justify-center gap-2 px-2 py-1 text-xs font-medium text-blue-600 bg-gradient-to-r from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 border border-transparent hover:border-blue-200 rounded-md opacity-75 hover:opacity-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30 dark:from-blue-900/20 dark:to-blue-800/40 dark:text-blue-300 dark:hover:from-blue-800/40 dark:hover:to-blue-900/60 dark:hover:text-blue-200"
        >
          <svg class="w-3 h-3 transition-all duration-300 rotate-180" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
          {{ $t('controls.expandAll') }}
        </button>
        <button
          v-if="!allCollapsed"
          @click="collapseAll"
          class="inline-flex items-center justify-center gap-2 px-2 py-1 text-xs font-medium text-slate-500 bg-gradient-to-r from-slate-50 to-slate-100 hover:from-slate-100 hover:to-slate-200 border border-transparent hover:border-slate-300 rounded-md opacity-75 hover:opacity-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-slate-400/30 dark:from-gray-700 dark:to-gray-600 dark:text-gray-400 dark:hover:from-gray-600 dark:hover:to-gray-500 dark:hover:text-gray-300"
        >
          <svg class="w-3 h-3 transition-all duration-300" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
          {{ $t('controls.collapseAll') }}
        </button>
      </div>
    </div>

    <div class="flex flex-col gap-3">
      <div 
        v-for="group in groups" 
        :key="viewMode === 'year' ? group.year : group.name"
      >
        <!-- Year View with Smart Flattened Hierarchy -->
        <template v-if="viewMode === 'year'">
          <!-- Current Year: Show months directly (no year wrapper) -->
          <template v-if="group.year === new Date().getFullYear()">
            <div
              v-for="month in group.months"
              :key="month.name"
              class="mb-2"
            >
              <!-- Current Year Month Header (direct, no nesting) -->
              <div
                @click="toggleGroupExpansion(month.name)"
                class="flex items-center gap-3 py-3 px-3 cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-all duration-200 group"
                :class="{
                  'bg-blue-50 dark:bg-blue-900/10 border-l-4 border-blue-500': isCurrentMonth(month.name),
                  'ml-1': !isCurrentMonth(month.name)
                }"
              >
                <svg
                  class="w-4 h-4 transition-all duration-300 text-blue-500 dark:text-blue-400 flex-shrink-0"
                  :class="{ 'rotate-180': expandedGroups.has(month.name) }"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>

                <div class="flex-1 flex items-baseline gap-2">
                  <span class="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-700 dark:group-hover:text-blue-300 transition-colors">
                    {{ month.name }}
                  </span>
                  <span class="text-sm text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {{ month.events.length }} {{ month.events.length === 1 ? 'event' : 'events' }}
                  </span>
                </div>
              </div>
              
              <!-- Current Year Events -->
              <div v-if="expandedGroups.has(month.name)" class="mb-3">
                <PreviewEventCard
                  v-for="event in month.events" 
                  :key="event.uid"
                  :event="event"
                  :show-category="showCategoryInGroups"
                  :format-date-range="formatDateRange"
                  :get-recurring-event-key="getRecurringEventKey"
                />
              </div>
            </div>
          </template>
          
          <!-- Other Years: Simple collapsed groups -->
          <template v-else>
            <div class="mb-2">
              <!-- Year Header (collapsed by default) -->
              <div
                @click="toggleGroupExpansion(group.year)"
                class="flex items-center gap-3 py-3 px-3 cursor-pointer hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg transition-all duration-200 group"
              >
                <svg
                  class="w-4 h-4 transition-all duration-300 text-purple-500 dark:text-purple-400 flex-shrink-0"
                  :class="{ 'rotate-180': expandedGroups.has(group.year) }"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>

                <div class="flex-1 flex items-baseline gap-2">
                  <span class="font-semibold text-gray-700 dark:text-gray-300 group-hover:text-purple-700 dark:group-hover:text-purple-300 transition-colors">
                    📅 {{ group.year }}
                  </span>
                  <span class="text-sm text-gray-500 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                    {{ group.totalEvents }} {{ group.totalEvents === 1 ? 'event' : 'events' }}
                  </span>
                </div>
              </div>
              
              <!-- Other Year Months (when expanded) -->
              <div v-if="expandedGroups.has(group.year)" class="space-y-1">
                <div
                  v-for="month in group.months"
                  :key="month.name"
                >
                  <!-- Month Header -->
                  <div
                    @click="toggleGroupExpansion(month.name)"
                    class="flex items-center gap-2 py-2 px-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-all duration-200 group ml-2"
                  >
                    <svg
                      class="w-3 h-3 transition-all duration-300 text-gray-500 dark:text-gray-400 flex-shrink-0"
                      :class="{ 'rotate-180': expandedGroups.has(month.name) }"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>

                    <div class="flex-1 flex items-baseline gap-2">
                      <span class="font-medium text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-gray-100 transition-colors">
                        {{ month.name.split(' ')[0] }}
                      </span>
                      <span class="text-sm text-gray-500 dark:text-gray-400">
                        {{ month.events.length }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- Events for this month -->
                  <div v-if="expandedGroups.has(month.name)" class="mb-2">
                    <PreviewEventCard
                      v-for="event in month.events" 
                      :key="event.uid"
                      :event="event"
                      :show-category="showCategoryInGroups"
                      :format-date-range="formatDateRange"
                      :get-recurring-event-key="getRecurringEventKey"
                    />
                  </div>
                </div>
              </div>
            </div>
          </template>
        </template>

        <!-- Natural Month Header -->
        <template v-else-if="viewMode === 'month'">
          <div
            @click="toggleGroupExpansion(group.name)"
            class="flex items-center gap-3 py-3 px-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-all duration-200 group"
            :class="{
              'bg-blue-50 dark:bg-blue-900/10 border-l-4 border-blue-500': isCurrentMonth(group.name),
              'ml-1': !isCurrentMonth(group.name)
            }"
          >
            <!-- Minimal expansion icon -->
            <svg
              class="w-4 h-4 transition-all duration-300 text-gray-400 dark:text-gray-500 flex-shrink-0"
              :class="{ 'rotate-180': expandedGroups.has(group.name) }"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>

            <!-- Clean month title -->
            <div class="flex-1 flex items-baseline gap-2">
              <span class="font-semibold text-gray-900 dark:text-gray-100">
                {{ group.name }}
              </span>
              <span class="text-sm text-gray-500 dark:text-gray-400">
                {{ group.events.length }} {{ group.events.length === 1 ? 'event' : 'events' }}
              </span>
            </div>
          </div>
          
          <!-- Natural Events List -->
          <div v-if="expandedGroups.has(group.name)" class="mb-4 space-y-0">
            <PreviewEventCard
              v-for="event in group.events" 
              :key="event.uid"
              :event="event"
              :show-category="showCategoryInGroups"
              :format-date-range="formatDateRange"
              :get-recurring-event-key="getRecurringEventKey"
            />
          </div>
        </template>

        <!-- Full Card for Category View -->
        <template v-else>
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
            <!-- Group Header -->
            <div 
              @click="toggleGroupExpansion(group.name)"
              class="px-4 py-3 flex justify-between items-center cursor-pointer transition-all"
              :class="getGroupHeaderClass(viewMode)"
            >
              <div class="flex items-center gap-3">
                <svg
                  class="w-4 h-4 transition-all duration-300 flex-shrink-0"
                  :class="{ 'rotate-180': expandedGroups.has(group.name) }"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <h4 class="font-semibold text-base m-0">{{ group.name }}</h4>
              </div>
              <span class="bg-white/20 px-2 py-1 rounded-full text-xs font-medium">
                {{ group.events.length }}
              </span>
            </div>
            
            <!-- Group Content -->
            <div v-if="expandedGroups.has(group.name)" class="p-3 sm:p-4">
              <div class="flex flex-col gap-2">
                <PreviewEventCard
                  v-for="event in group.events" 
                  :key="event.uid"
                  :event="event"
                  :show-category="showCategoryInGroups"
                  :format-date-range="formatDateRange"
                  :get-recurring-event-key="getRecurringEventKey"
                />
              </div>
            </div>
          </div>
        </template>
      </div>
      
      <!-- Ultra-Minimal Empty State -->
      <div v-if="groups.length === 0" class="text-center py-8 opacity-60">
        <div class="text-3xl mb-3 opacity-50">📂</div>
        <p class="text-sm text-gray-600 dark:text-gray-400 font-medium">
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
  formatDateRange: { type: Function, required: true },
  getRecurringEventKey: { type: Function, required: true }
})

// State for tracking which groups are expanded - default all to expanded
const expandedGroups = ref(new Set())

// Category vs Month view should show category differently
const showCategoryInGroups = computed(() => props.viewMode === 'month')

// Watch for groups changes and use smart defaults
watch(() => props.groups, (newGroups) => {
  // Clear existing expanded groups
  expandedGroups.value.clear()
  
  const currentYear = new Date().getFullYear()
  
  // Smart expansion based on relevance
  newGroups.forEach(group => {
    if (props.viewMode === 'year') {
      // For year view: expand current year only, collapse others
      if (group.year === currentYear) {
        expandedGroups.value.add(group.year)
        // Expand current year's months
        group.months?.forEach(month => {
          expandedGroups.value.add(month.name)
        })
      }
      // Other years stay collapsed by default
    } else {
      // For month/category view, expand all by name (simpler case)
      expandedGroups.value.add(group.name)
    }
  })
}, { immediate: true })

// Toggle group expansion
const toggleGroupExpansion = (groupName) => {
  if (expandedGroups.value.has(groupName)) {
    expandedGroups.value.delete(groupName)
  } else {
    expandedGroups.value.add(groupName)
  }
}

// Computed properties for conditional buttons
const allExpanded = computed(() => {
  if (props.groups.length === 0) return false
  
  if (props.viewMode === 'year') {
    return props.groups.every(group => {
      const yearExpanded = expandedGroups.value.has(group.year)
      const monthsExpanded = group.months?.every(month => expandedGroups.value.has(month.name)) ?? true
      return yearExpanded && monthsExpanded
    })
  } else {
    return props.groups.every(group => expandedGroups.value.has(group.name))
  }
})

const allCollapsed = computed(() => {
  if (props.groups.length === 0) return false
  
  if (props.viewMode === 'year') {
    return props.groups.every(group => !expandedGroups.value.has(group.year))
  } else {
    return props.groups.every(group => !expandedGroups.value.has(group.name))
  }
})

// Expand/Collapse all methods
const expandAll = () => {
  props.groups.forEach(group => {
    if (props.viewMode === 'year') {
      expandedGroups.value.add(group.year)
      group.months?.forEach(month => {
        expandedGroups.value.add(month.name)
      })
    } else {
      expandedGroups.value.add(group.name)
    }
  })
}

const collapseAll = () => {
  expandedGroups.value.clear()
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

// Extract month name from "Month Year" format
const getMonthName = (monthString) => {
  return monthString.split(' ')[0]
}

// Extract year from "Month Year" format
const getYearFromMonth = (monthString) => {
  return monthString.split(' ')[1]
}

// Check if a month string represents the current month
const isCurrentMonth = (monthString) => {
  const now = new Date()
  const currentMonthName = now.toLocaleDateString('en-US', { month: 'long' })
  const currentYear = now.getFullYear()
  return monthString === `${currentMonthName} ${currentYear}`
}
</script>