<template>
  <div v-if="hasAnyRecurringEvents" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
    <!-- Collapsible Header -->
    <div 
      class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-slate-100 dark:hover:bg-gray-700 transition-colors duration-200"
      :class="showRecurringEventsSection ? 'rounded-t-xl' : 'rounded-xl'"
      @click="showRecurringEventsSection = !showRecurringEventsSection"
    >
      <!-- Mobile Layout -->
      <div class="block sm:hidden">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">🔄 {{ $t('calendar.recurringEvents') }}</h3>
          <button class="flex-shrink-0 p-2 rounded-full bg-white/50 dark:bg-gray-600/50 hover:bg-white dark:hover:bg-gray-600 transition-all duration-200">
            <svg 
              class="w-5 h-5 text-gray-600 dark:text-gray-300 transition-transform duration-200" 
              :class="{ 'rotate-180': showRecurringEventsSection }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <!-- Status text on mobile -->
        <p class="text-xs text-gray-600 dark:text-gray-400 text-center leading-tight">
          {{ selectedRecurringEvents.length > 0 
            ? $t('recurringEvents.selectedRecurringEvents', { count: selectedRecurringEvents.length, total: allRecurringEvents.length })
            : $t('recurringEvents.selectRecurringEventsBelow') }}
        </p>
      </div>

      <!-- Desktop Layout -->
      <div class="hidden sm:flex items-center justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-4 mb-2">
            <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">🔄 {{ $t('calendar.recurringEvents') }}</h3>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ selectedRecurringEvents.length > 0 
              ? $t('recurringEvents.selectedRecurringEvents', { count: selectedRecurringEvents.length, total: allRecurringEvents.length })
              : $t('recurringEvents.selectRecurringEventsBelow') }}
          </p>
        </div>
        <button class="flex-shrink-0 p-2 rounded-full bg-white/50 dark:bg-gray-600/50 hover:bg-white dark:hover:bg-gray-600 transition-all duration-200 ml-4">
          <svg 
            class="w-5 h-5 text-gray-600 dark:text-gray-300 transition-transform duration-200" 
            :class="{ 'rotate-180': showRecurringEventsSection }"
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Collapsible Content -->
    <div v-if="showRecurringEventsSection" class="p-3 sm:p-4">
      <!-- Action Buttons -->
      <div class="flex flex-wrap gap-2 justify-center mb-4 px-1">
        <!-- When NOT searching: Show All/Clear All -->
        <template v-if="!searchTerm.trim()">
          <button 
            @click="$emit('clear-all')" 
            class="px-4 py-2 bg-gray-500 dark:bg-gray-600 text-white dark:text-gray-200 rounded-lg font-semibold hover:bg-gray-600 dark:hover:bg-gray-700 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✗ {{ $t('recurringEvents.clearAll') }}
          </button>
          <button 
            @click="$emit('select-all')" 
            class="px-4 py-2 bg-blue-500 dark:bg-blue-600 text-white dark:text-gray-200 rounded-lg font-semibold hover:bg-blue-600 dark:hover:bg-blue-700 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✓ {{ $t('recurringEvents.selectAll') }}
          </button>
        </template>
        
        <!-- When searching: Show contextual buttons -->
        <template v-else>
          <button 
            v-if="hasAnyVisibleSelected"
            @click="clearAllVisible"
            class="px-4 py-2 bg-rose-500 dark:bg-rose-600 text-white dark:text-gray-200 rounded-lg font-semibold hover:bg-rose-600 dark:hover:bg-rose-700 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✗ {{ $t('recurringEvents.clearVisible') }}
          </button>
          <button 
            v-if="!areAllVisibleSelected"
            @click="selectAllVisible"
            class="px-4 py-2 bg-emerald-500 dark:bg-emerald-600 text-white dark:text-gray-200 rounded-lg font-semibold hover:bg-emerald-600 dark:hover:bg-emerald-700 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✓ {{ $t('recurringEvents.selectVisible', { count: filteredMainRecurringEvents.length }) }}
          </button>
        </template>
        
        <!-- Show Selected Only Toggle - responsive text -->
        <button
          v-if="selectedRecurringEvents.length > 0"
          @click="$emit('toggle-selected-only')"
          class="px-3 py-2 border-2 rounded-lg text-xs font-semibold transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap"
          :class="showSelectedOnly 
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/50' 
            : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'"
        >
          <span class="hidden sm:inline">{{ showSelectedOnly ? '👁️ ' + $t('recurringEvents.showAllRecurringEvents') : '🎯 ' + $t('recurringEvents.showSelectedOnly') }}</span>
          <span class="sm:hidden">{{ showSelectedOnly ? '👁️ ' + $t('common.all') : '🎯 ' + $t('common.select') }}</span>
        </button>
        
      </div>

      <!-- Event Type Search -->
      <div class="mb-4 relative">
        <input 
          :value="searchTerm"
          @input="$emit('update:search-term', $event.target.value)"
          type="text" 
          :placeholder="$t('recurringEvents.searchRecurringEvents')"
          class="w-full px-3 py-2.5 pr-10 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 rounded-lg focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/30 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm"
        >
        <!-- Clear search button -->
        <button
          v-if="searchTerm.trim()"
          @click="$emit('update:search-term', '')"
          class="absolute right-2 top-1/2 transform -translate-y-1/2 w-6 h-6 bg-gray-400 dark:bg-gray-500 hover:bg-gray-500 dark:hover:bg-gray-600 text-white dark:text-gray-200 rounded-full flex items-center justify-center text-xs transition-all duration-200"
          :title="$t('recurringEvents.clearSearch')"
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
      
      <!-- Multi-Event Types -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4 items-start">
        <div 
          v-for="recurringEvent in filteredMainRecurringEvents" 
          :key="recurringEvent.name"
          class="rounded-lg border-2 transition-all duration-200"
          :class="selectedRecurringEvents.includes(recurringEvent.name) 
            ? 'border-green-500 bg-green-50 dark:bg-green-900/30' 
            : 'border-gray-200 dark:border-gray-700'"
        >
          <!-- Event Type Header -->
          <div 
            class="flex items-center gap-3 p-2.5 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
            :class="expandedRecurringEvents.includes(recurringEvent.name) ? 'rounded-t-lg' : 'rounded-lg'"
            @click="$emit('toggle-recurring-event', recurringEvent.name)"
          >
            <!-- Checkbox -->
            <div class="flex-shrink-0">
              <div 
                class="w-5 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200"
                :class="selectedRecurringEvents.includes(recurringEvent.name) 
                  ? 'bg-green-500 border-green-500 text-white' 
                  : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700'"
              >
                <span v-if="selectedRecurringEvents.includes(recurringEvent.name)">✓</span>
              </div>
            </div>
            
            <!-- Event Type Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2">
                <span class="font-medium text-gray-800 dark:text-gray-200 text-xs leading-tight truncate">{{ recurringEvent.name }}</span>
                <span class="flex-shrink-0 px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 text-xs rounded-full font-medium">
                  {{ recurringEvent.count }}
                </span>
              </div>
            </div>
            
            <!-- Expand Button -->
            <button 
              @click.stop="$emit('toggle-expansion', recurringEvent.name)"
              class="flex-shrink-0 w-10 h-6 flex items-center justify-center rounded-full transition-all duration-200 hover:bg-white dark:hover:bg-gray-600"
              :class="expandedRecurringEvents.includes(recurringEvent.name) 
                ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400' 
                : 'bg-gray-100 dark:bg-gray-600 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              <svg 
                class="w-4 h-4 transition-transform duration-200" 
                :class="{ 'rotate-90': expandedRecurringEvents.includes(recurringEvent.name) }"
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          
          <!-- Expandable Events List -->
          <div 
            v-if="expandedRecurringEvents.includes(recurringEvent.name)"
            class="border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-6 py-3 rounded-b-lg"
          >
            <div class="space-y-3">
              <div 
                v-for="event in recurringEvent.events" 
                :key="event.uid"
                class="py-2 border-b border-gray-200 dark:border-gray-600 last:border-b-0"
              >
                <div v-if="event.title !== recurringEvent.name" class="font-medium text-gray-800 dark:text-gray-200 text-sm mb-1">{{ event.title }}</div>
                <div class="flex flex-col gap-1 text-xs text-gray-600 dark:text-gray-400">
                  <span>📅 {{ formatDateRange(event) }}</span>
                  <span v-if="event.location" class="break-words">📍 {{ event.location }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results Message -->
      <div 
        v-if="!hasAnyVisibleRecurringEvents && (searchTerm.trim() || showSelectedOnly)" 
        class="text-center py-8 px-4 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600"
      >
        <div class="text-4xl mb-3">🔍</div>
        <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
          {{ searchTerm.trim() ? $t('recurringEvents.noSearchResults') : $t('recurringEvents.noSelectedVisible') }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ searchTerm.trim() 
            ? $t('recurringEvents.tryDifferentSearch') 
            : $t('recurringEvents.selectRecurringEventsFirst') }}
        </p>
      </div>

      <!-- Unique Events Section -->
      <div 
        v-if="filteredSingleRecurringEvents.length > 0" 
        class="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl border-2 border-purple-200 dark:border-purple-700 overflow-hidden"
      >
        <!-- Singles Header - Fully Clickable -->
        <div 
          class="flex items-center justify-between p-4 cursor-pointer hover:bg-purple-100/50 dark:hover:bg-purple-800/30 transition-colors duration-200"
          :class="showSingleEvents ? '' : ''"
          @click="areAllSinglesSelected ? $emit('clear-all-singles') : $emit('select-all-singles')"
        >
          <div class="flex items-center gap-3">
            <div 
              class="w-5 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200"
              :class="areAllSinglesSelected
                ? 'bg-purple-500 border-purple-500 text-white' 
                : 'border-purple-300 dark:border-purple-600 bg-white dark:bg-gray-700'"
            >
              <span v-if="areAllSinglesSelected">✓</span>
            </div>
            <span class="font-semibold text-purple-800 dark:text-purple-300">📄 {{ $t('recurringEvents.uniqueEvents') }}</span>
            <span class="px-2 py-1 bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300 text-xs rounded-full font-medium">
              {{ selectedSinglesCount }}/{{ filteredSingleRecurringEvents.length }}
            </span>
          </div>
          <button 
            @click.stop="showSingleEvents = !showSingleEvents"
            class="px-3 py-1 bg-purple-100 dark:bg-purple-900/50 hover:bg-purple-200 dark:hover:bg-purple-800/50 text-purple-700 dark:text-purple-300 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-1"
          >
            {{ showSingleEvents ? $t('recurringEvents.hideSingleEvents') : $t('recurringEvents.showSingleEvents') }}
            <svg 
              class="w-3 h-3 transition-transform duration-200" 
              :class="{ 'rotate-90': showSingleEvents }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>

        <!-- Singles List (when expanded) -->
        <div v-if="showSingleEvents" class="border-t border-purple-200 dark:border-purple-700 p-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 items-start">
          <div 
            v-for="recurringEvent in filteredSingleRecurringEvents"
            :key="recurringEvent.name"
            class="flex items-center gap-2 p-2 rounded-lg border transition-all duration-200 cursor-pointer hover:bg-purple-50 dark:hover:bg-purple-900/30"
            :class="selectedRecurringEvents.includes(recurringEvent.name) 
              ? 'border-purple-500 bg-purple-100 dark:bg-purple-900/50' 
              : 'border-purple-200 dark:border-purple-700 bg-white dark:bg-gray-700'"
            @click="$emit('toggle-recurring-event', recurringEvent.name)"
          >
            <!-- Checkbox -->
            <div 
              class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200 flex-shrink-0"
              :class="selectedRecurringEvents.includes(recurringEvent.name) 
                ? 'bg-purple-500 border-purple-500 text-white' 
                : 'border-purple-300 dark:border-purple-600 bg-white dark:bg-gray-700'"
            >
              <span v-if="selectedRecurringEvents.includes(recurringEvent.name)">✓</span>
            </div>
            
            <!-- Event Info -->
            <div class="flex-1 min-w-0">
              <div class="font-medium text-purple-800 dark:text-purple-300 text-xs leading-tight mb-1 truncate">{{ recurringEvent.name }}</div>
              <div class="flex flex-col gap-1 text-xs text-purple-600 dark:text-purple-400">
                <span class="truncate">📅 {{ formatDateRange(recurringEvent.events[0]) }}</span>
                <span v-if="recurringEvent.events[0].location" class="truncate">📍 {{ recurringEvent.events[0].location }}</span>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  recurringEvents: { type: Array, default: () => [] },
  mainRecurringEvents: { type: Array, default: () => [] },
  singleRecurringEvents: { type: Array, default: () => [] },
  allRecurringEvents: { type: Array, default: () => [] }, // Unfiltered recurring events for visibility check
  selectedRecurringEvents: { type: Array, default: () => [] },
  expandedRecurringEvents: { type: Array, default: () => [] },
  showSingleEvents: { type: Boolean, default: false },
  showRecurringEventsSection: { type: Boolean, default: true },
  showSelectedOnly: { type: Boolean, default: false },
  searchTerm: { type: String, default: '' },
  formatDateTime: { type: Function, required: true },
  formatDateRange: { type: Function, required: true }
})

// Check if there are any recurring events at all (for section visibility)
// Use unfiltered recurring events to prevent section from disappearing during search
const hasAnyRecurringEvents = computed(() => {
  return props.allRecurringEvents.length > 0
})

// Filtered recurring events based on search and selection
const filteredMainRecurringEvents = computed(() => {
  let recurringEvents = props.mainRecurringEvents
  
  // Filter by selection if showSelectedOnly is true
  if (props.showSelectedOnly) {
    recurringEvents = recurringEvents.filter(recurringEvent => 
      props.selectedRecurringEvents.includes(recurringEvent.name)
    )
  }
  
  // Filter by search term
  if (props.searchTerm.trim()) {
    const searchTerm = props.searchTerm.toLowerCase()
    recurringEvents = recurringEvents.filter(recurringEvent => 
      recurringEvent.name.toLowerCase().includes(searchTerm)
    )
  }
  
  return recurringEvents
})

const filteredSingleRecurringEvents = computed(() => {
  let recurringEvents = props.singleRecurringEvents
  
  // Filter by selection if showSelectedOnly is true
  if (props.showSelectedOnly) {
    recurringEvents = recurringEvents.filter(recurringEvent => 
      props.selectedRecurringEvents.includes(recurringEvent.name)
    )
  }
  
  // Filter by search term
  if (props.searchTerm.trim()) {
    const searchTerm = props.searchTerm.toLowerCase()
    recurringEvents = recurringEvents.filter(recurringEvent => 
      recurringEvent.name.toLowerCase().includes(searchTerm)
    )
  }
  
  return recurringEvents
})

// Singles selection state
const areAllSinglesSelected = computed(() => {
  if (filteredSingleRecurringEvents.value.length === 0) return false
  const singleNames = filteredSingleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  return singleNames.every(name => props.selectedRecurringEvents.includes(name))
})

const selectedSinglesCount = computed(() => {
  const singleNames = filteredSingleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  return singleNames.filter(name => props.selectedRecurringEvents.includes(name)).length
})

// Visible selection state for main event types
const areAllVisibleSelected = computed(() => {
  if (filteredMainRecurringEvents.value.length === 0) return false
  const visibleNames = filteredMainRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  return visibleNames.every(name => props.selectedRecurringEvents.includes(name))
})

const hasAnyVisibleSelected = computed(() => {
  const visibleNames = filteredMainRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  return visibleNames.some(name => props.selectedRecurringEvents.includes(name))
})

// Check if filtering/search results in any visible event types
const hasAnyVisibleRecurringEvents = computed(() => {
  return filteredMainRecurringEvents.value.length > 0 || filteredSingleRecurringEvents.value.length > 0
})

// Methods for visible event type selection
function selectAllVisible() {
  const visibleNames = filteredMainRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  visibleNames.forEach(name => {
    if (!props.selectedRecurringEvents.includes(name)) {
      emit('toggle-recurring-event', name)
    }
  })
}

function clearAllVisible() {
  const visibleNames = filteredMainRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  visibleNames.forEach(name => {
    if (props.selectedRecurringEvents.includes(name)) {
      emit('toggle-recurring-event', name)
    }
  })
}

const emit = defineEmits([
  'clear-all',
  'select-all', 
  'update:search-term',
  'toggle-recurring-event',
  'toggle-expansion',
  'toggle-singles-visibility',
  'select-all-singles',
  'clear-all-singles',
  'toggle-selected-only',
  'switch-filter-mode'
])

// Make showSingleEvents and showRecurringEventsSection writable
const showSingleEvents = computed({
  get: () => props.showSingleEvents,
  set: (value) => emit('toggle-singles-visibility', value)
})

const showRecurringEventsSection = computed({
  get: () => props.showRecurringEventsSection,
  set: (value) => emit('toggle-recurring-events-section', value)
})
</script>