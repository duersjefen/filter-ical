<template>
  <div class="p-3 sm:p-4">
    <!-- Minimal Expand/Collapse All Buttons -->
    <div v-if="(viewMode === 'month' || viewMode === 'year') && groups.length > 1" class="flex justify-start mb-3">
      <div class="flex gap-1">
        <button 
          v-if="!allExpanded"
          @click="expandAll"
          class="px-2 py-1 text-xs font-medium rounded transition-colors bg-blue-100 hover:bg-blue-200 text-blue-700 dark:bg-blue-900/40 dark:hover:bg-blue-800/60 dark:text-blue-300"
        >
          Expand All {{ viewMode === 'year' ? 'Years' : 'Months' }}
        </button>
        <button 
          v-if="!allCollapsed"
          @click="collapseAll"
          class="px-2 py-1 text-xs font-medium rounded transition-colors bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300"
        >
          Collapse All {{ viewMode === 'year' ? 'Years' : 'Months' }}
        </button>
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <div 
        v-for="group in groups" 
        :key="viewMode === 'year' ? group.year : group.name"
      >
        <!-- Year View with Nested Months -->
        <template v-if="viewMode === 'year'">
          <!-- Year Header -->
          <div 
            @click="toggleGroupExpansion(group.year)"
            class="flex items-center gap-2 py-2 px-3 cursor-pointer hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg text-sm transition-colors border border-transparent hover:border-purple-200 dark:hover:border-purple-700 group"
          >
            <!-- Year expansion icon -->
            <svg 
              class="w-4 h-4 transition-transform duration-200 text-purple-500 dark:text-purple-400" 
              :class="{ 'rotate-90': expandedGroups.has(group.year) }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            
            <!-- Year title -->
            <div class="flex-1">
              <span class="font-bold text-gray-900 dark:text-gray-100 group-hover:text-purple-700 dark:group-hover:text-purple-300 transition-colors">
                📅 {{ group.year }}
              </span>
            </div>
            
            <!-- Year event count -->
            <span class="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 rounded-full font-medium">
              {{ group.totalEvents }}
            </span>
          </div>
          
          <!-- Nested Months for this Year -->
          <div v-if="expandedGroups.has(group.year)" class="ml-6 mb-3">
            <div class="space-y-1">
              <div
                v-for="month in group.months"
                :key="month.name"
              >
                <!-- Month Header (nested under year) -->
                <div 
                  @click="toggleGroupExpansion(month.name)"
                  class="flex items-center gap-2 py-1.5 px-2 cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded text-sm transition-colors border border-transparent hover:border-blue-200 dark:hover:border-blue-700 group"
                >
                  <svg 
                    class="w-3 h-3 transition-transform duration-200 text-blue-500 dark:text-blue-400" 
                    :class="{ 'rotate-90': expandedGroups.has(month.name) }"
                    fill="currentColor" 
                    viewBox="0 0 20 20"
                  >
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                  
                  <div class="flex-1">
                    <span class="font-medium text-gray-800 dark:text-gray-200 group-hover:text-blue-700 dark:group-hover:text-blue-300 transition-colors">
                      {{ month.name.split(' ')[0] }} <!-- Just month name, not year -->
                    </span>
                  </div>
                  
                  <span class="text-xs px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 rounded-full font-medium">
                    {{ month.events.length }}
                  </span>
                </div>
                
                <!-- Events for this month -->
                <div v-if="expandedGroups.has(month.name)" class="ml-6 mb-2">
                  <div class="bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700 overflow-hidden">
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
          </div>
        </template>

        <!-- Enhanced Month Header -->
        <template v-else-if="viewMode === 'month'">
          <div 
            @click="toggleGroupExpansion(group.name)"
            class="flex items-center gap-3 py-1.5 px-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group"
          >
            <!-- Compact expansion icon -->
            <svg 
              class="w-3 h-3 transition-transform duration-200 text-gray-400 dark:text-gray-500" 
              :class="{ 'rotate-90': expandedGroups.has(group.name) }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            
            <!-- Month title with improved typography -->
            <div class="flex-1 flex items-baseline gap-2">
              <span class="font-bold text-gray-900 dark:text-gray-100 tracking-tight">
                {{ getMonthName(group.name) }}
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400 font-mono">
                {{ getYearFromMonth(group.name) }}
              </span>
            </div>
            
            <!-- Enhanced event count with context -->
            <div class="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
              <span class="font-medium tabular-nums">{{ group.events.length }}</span>
              <span class="hidden sm:inline">{{ group.events.length === 1 ? 'event' : 'events' }}</span>
            </div>
          </div>
          
          <!-- Minimal Events List -->
          <div v-if="expandedGroups.has(group.name)" class="ml-6 mb-3">
            <div class="bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700 overflow-hidden">
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
      
      <!-- Minimal Empty State -->
      <div v-if="groups.length === 0" class="text-center py-6 px-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-dashed border-gray-300 dark:border-gray-600">
        <div class="text-2xl mb-2">📂</div>
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
          {{ $t('preview.noGroupsToShow') }}
        </h3>
        <p class="text-xs text-gray-600 dark:text-gray-400">
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

// Watch for groups changes and default all to expanded
watch(() => props.groups, (newGroups) => {
  // Clear existing expanded groups
  expandedGroups.value.clear()
  
  // Default all groups to expanded
  newGroups.forEach(group => {
    if (props.viewMode === 'year') {
      // For year view, expand years and their months
      expandedGroups.value.add(group.year)
      group.months?.forEach(month => {
        expandedGroups.value.add(month.name)
      })
    } else {
      // For month/category view, expand by name
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
</script>