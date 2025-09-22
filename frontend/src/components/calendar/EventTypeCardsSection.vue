<template>
  <div v-if="hasAnyEventTypes" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
    <!-- Header with Switch Button -->
    <div 
      class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700"
      :class="props.showEventTypesSection ? 'rounded-t-xl' : 'rounded-xl'"
    >
      <!-- Mobile Layout -->
      <div class="block sm:hidden">
        <div class="flex items-center justify-between mb-3">
          <div class="flex-1">
            <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">
              📂 {{ $t('calendar.eventTypes') }}
            </h3>
          </div>
          <!-- Mobile Switch Button -->
          <button
            @click="$emit('switch-to-groups')"
            class="px-3 py-2 rounded-md border border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200 flex items-center gap-1 group"
            title="Switch to Groups view"
          >
            <span class="text-xs font-medium text-gray-600 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400">🏷️ Groups</span>
            <svg class="w-4 h-4 text-gray-400 group-hover:text-blue-500 transition-colors" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <!-- Status text on mobile -->
        <p class="text-xs text-gray-600 dark:text-gray-400 text-center leading-tight">
          {{ selectedEventTypes.length > 0 
            ? $t('eventTypes.selectedEventTypes', { count: selectedEventTypes.length, total: allEventTypes.length })
            : $t('eventTypes.selectEventTypesBelow') }}
        </p>
      </div>

      <!-- Desktop Layout -->
      <div class="hidden sm:flex items-center justify-between">
        <!-- Left: Header Info with collapse button -->
        <div class="flex items-center gap-3 flex-1 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg p-2 -m-2 transition-colors duration-200" @click="$emit('toggle-event-types-section')">
          <!-- Dropdown Icon -->
          <svg 
            class="w-5 h-5 text-gray-400 transition-transform duration-200"
            :class="{ 'rotate-180': !props.showEventTypesSection }"
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
          
          <div class="flex-1">
            <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              📂 {{ $t('calendar.eventTypes') }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ selectedEventTypes.length > 0 
                ? $t('eventTypes.selectedEventTypes', { count: selectedEventTypes.length, total: allEventTypes.length })
                : $t('eventTypes.selectEventTypesBelow') }}
            </p>
          </div>
        </div>
        
        <!-- Desktop Switch Button -->
        <button
          @click="$emit('switch-to-groups')"
          class="px-4 py-3 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200 flex items-center gap-2 group ml-4"
          title="Switch to Groups view"
        >
          <div class="text-right">
            <div class="text-sm font-semibold text-gray-700 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400">
              Switch to
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 group-hover:text-blue-500 dark:group-hover:text-blue-300">
              🏷️ Groups
            </div>
          </div>
          <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Collapsible Content -->
    <div v-if="props.showEventTypesSection" class="p-3 sm:p-4">
      <!-- Action Buttons -->
      <div class="flex flex-wrap gap-2 justify-center mb-4 px-1">
        <!-- When NOT searching: Show All/Clear All -->
        <template v-if="!searchTerm.trim()">
          <button 
            @click="$emit('clear-all')" 
            class="px-4 py-2 bg-gray-500 dark:bg-gray-600 text-white dark:text-gray-200 rounded-lg font-semibold hover:bg-gray-600 dark:hover:bg-gray-700 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✗ {{ $t('eventTypes.clearAll') }}
          </button>
          <button 
            @click="$emit('select-all')" 
            class="px-4 py-2 bg-blue-500 dark:bg-blue-600 text-white dark:text-gray-200 rounded-lg font-semibold hover:bg-blue-600 dark:hover:bg-blue-700 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✓ {{ $t('eventTypes.selectAll') }}
          </button>
        </template>
        
        <!-- When searching: Show contextual buttons -->
        <template v-else>
          <button 
            v-if="hasAnyVisibleSelected"
            @click="clearAllVisible"
            class="px-4 py-2 bg-rose-500 dark:bg-rose-600 text-white dark:text-gray-200 rounded-lg font-semibold hover:bg-rose-600 dark:hover:bg-rose-700 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✗ {{ $t('eventTypes.clearVisible') }}
          </button>
          <button 
            v-if="!areAllVisibleSelected"
            @click="selectAllVisible"
            class="px-4 py-2 bg-emerald-500 dark:bg-emerald-600 text-white dark:text-gray-200 rounded-lg font-semibold hover:bg-emerald-600 dark:hover:bg-emerald-700 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✓ {{ $t('eventTypes.selectVisible', { count: filteredMainEventTypes.length }) }}
          </button>
        </template>
        
        <!-- Show Selected Only Toggle - responsive text -->
        <button
          v-if="selectedEventTypes.length > 0"
          @click="$emit('toggle-selected-only')"
          class="px-3 py-2 border-2 rounded-lg text-xs font-semibold transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap"
          :class="showSelectedOnly 
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/50' 
            : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'"
        >
          <span class="hidden sm:inline">{{ showSelectedOnly ? '👁️ ' + $t('eventTypes.showAllEventTypes') : '🎯 ' + $t('eventTypes.showSelectedOnly') }}</span>
          <span class="sm:hidden">{{ showSelectedOnly ? '👁️ ' + $t('common.all') : '🎯 ' + $t('common.select') }}</span>
        </button>
        
      </div>

      <!-- Event Type Search -->
      <div class="mb-4 relative">
        <input 
          :value="searchTerm"
          @input="$emit('update:search-term', $event.target.value)"
          type="text" 
          :placeholder="$t('eventTypes.searchEventTypes')"
          class="w-full px-3 py-2.5 pr-10 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 rounded-lg focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/30 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm"
        >
        <!-- Clear search button -->
        <button
          v-if="searchTerm.trim()"
          @click="$emit('update:search-term', '')"
          class="absolute right-2 top-1/2 transform -translate-y-1/2 w-6 h-6 bg-gray-400 dark:bg-gray-500 hover:bg-gray-500 dark:hover:bg-gray-600 text-white dark:text-gray-200 rounded-full flex items-center justify-center text-xs transition-all duration-200"
          :title="$t('eventTypes.clearSearch')"
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
      
      <!-- Multi-Event Types -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4 items-start">
        <div 
          v-for="eventType in filteredMainEventTypes" 
          :key="eventType.name"
          class="rounded-lg border-2 transition-all duration-200"
          :class="selectedEventTypes.includes(eventType.name) 
            ? 'border-green-500 bg-green-50 dark:bg-green-900/30' 
            : 'border-gray-200 dark:border-gray-700'"
        >
          <!-- Event Type Header -->
          <div 
            class="flex items-center gap-3 p-2.5 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
            :class="expandedEventTypes.includes(eventType.name) ? 'rounded-t-lg' : 'rounded-lg'"
            @click="$emit('toggle-event-type', eventType.name)"
          >
            <!-- Checkbox -->
            <div class="flex-shrink-0">
              <div 
                class="w-5 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200"
                :class="selectedEventTypes.includes(eventType.name) 
                  ? 'bg-green-500 border-green-500 text-white' 
                  : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700'"
              >
                <span v-if="selectedEventTypes.includes(eventType.name)">✓</span>
              </div>
            </div>
            
            <!-- Event Type Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2">
                <span class="font-medium text-gray-800 dark:text-gray-200 text-xs leading-tight truncate">{{ eventType.name }}</span>
                <span class="flex-shrink-0 px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 text-xs rounded-full font-medium">
                  {{ eventType.count }}
                </span>
              </div>
            </div>
            
            <!-- Expand Button -->
            <button 
              @click.stop="$emit('toggle-expansion', eventType.name)"
              class="flex-shrink-0 w-10 h-6 flex items-center justify-center rounded-full transition-all duration-200 hover:bg-white dark:hover:bg-gray-600"
              :class="expandedEventTypes.includes(eventType.name) 
                ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400' 
                : 'bg-gray-100 dark:bg-gray-600 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              <svg 
                class="w-4 h-4 transition-transform duration-200" 
                :class="{ 'rotate-90': expandedEventTypes.includes(eventType.name) }"
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          
          <!-- Expandable Events List -->
          <div 
            v-if="expandedEventTypes.includes(eventType.name)"
            class="border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-6 py-3 rounded-b-lg"
          >
            <div class="space-y-3">
              <div 
                v-for="event in eventType.events" 
                :key="event.uid"
                class="py-2 border-b border-gray-200 dark:border-gray-600 last:border-b-0"
              >
                <div v-if="event.title !== eventType.name" class="font-medium text-gray-800 dark:text-gray-200 text-sm mb-1">{{ event.title }}</div>
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
        v-if="!hasAnyVisibleEventTypes && (searchTerm.trim() || showSelectedOnly)" 
        class="text-center py-8 px-4 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600"
      >
        <div class="text-4xl mb-3">🔍</div>
        <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
          {{ searchTerm.trim() ? $t('eventTypes.noSearchResults') : $t('eventTypes.noSelectedVisible') }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ searchTerm.trim() 
            ? $t('eventTypes.tryDifferentSearch') 
            : $t('eventTypes.selectEventTypesFirst') }}
        </p>
      </div>

      <!-- Unique Events Section -->
      <div 
        v-if="filteredSingleEventTypes.length > 0" 
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
            <span class="font-semibold text-purple-800 dark:text-purple-300">📄 {{ $t('eventTypes.uniqueEvents') }}</span>
            <span class="px-2 py-1 bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300 text-xs rounded-full font-medium">
              {{ selectedSinglesCount }}/{{ filteredSingleEventTypes.length }}
            </span>
          </div>
          <button 
            @click.stop="showSingleEvents = !showSingleEvents"
            class="px-3 py-1 bg-purple-100 dark:bg-purple-900/50 hover:bg-purple-200 dark:hover:bg-purple-800/50 text-purple-700 dark:text-purple-300 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-1"
          >
            {{ showSingleEvents ? $t('eventTypes.hideSingleEvents') : $t('eventTypes.showSingleEvents') }}
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
            v-for="eventType in filteredSingleEventTypes"
            :key="eventType.name"
            class="flex items-center gap-2 p-2 rounded-lg border transition-all duration-200 cursor-pointer hover:bg-purple-50 dark:hover:bg-purple-900/30"
            :class="selectedEventTypes.includes(eventType.name) 
              ? 'border-purple-500 bg-purple-100 dark:bg-purple-900/50' 
              : 'border-purple-200 dark:border-purple-700 bg-white dark:bg-gray-700'"
            @click="$emit('toggle-event-type', eventType.name)"
          >
            <!-- Checkbox -->
            <div 
              class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200 flex-shrink-0"
              :class="selectedEventTypes.includes(eventType.name) 
                ? 'bg-purple-500 border-purple-500 text-white' 
                : 'border-purple-300 dark:border-purple-600 bg-white dark:bg-gray-700'"
            >
              <span v-if="selectedEventTypes.includes(eventType.name)">✓</span>
            </div>
            
            <!-- Event Info -->
            <div class="flex-1 min-w-0">
              <div class="font-medium text-purple-800 dark:text-purple-300 text-xs leading-tight mb-1 truncate">{{ eventType.name }}</div>
              <div class="flex flex-col gap-1 text-xs text-purple-600 dark:text-purple-400">
                <span class="truncate">📅 {{ formatDateRange(eventType.events[0]) }}</span>
                <span v-if="eventType.events[0].location" class="truncate">📍 {{ eventType.events[0].location }}</span>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
      
      <!-- Bulk Groups Actions -->
      <div v-if="hasGroups" class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
        <div class="text-center">
          <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            What to do with future Events?
          </h4>
          <div class="flex flex-col sm:flex-row gap-3 justify-center items-center">
            <!-- Subscribe to All Groups -->
            <button
              @click="$emit('subscribe-all-groups')"
              class="px-6 py-2.5 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg transition-all duration-200 hover:shadow-md hover:scale-105 active:scale-95 flex items-center gap-2"
            >
              <span>📥</span>
              <span>Subscribe to All Groups</span>
            </button>
            
            <!-- Unsubscribe from All Groups -->
            <button
              @click="$emit('unsubscribe-all-groups')"
              class="px-6 py-2.5 bg-gray-500 hover:bg-gray-600 text-white font-semibold rounded-lg transition-all duration-200 hover:shadow-md hover:scale-105 active:scale-95 flex items-center gap-2"
            >
              <span>📤</span>
              <span>Unsubscribe from All</span>
            </button>
          </div>
          
          <!-- Helper Text -->
          <p class="mt-3 text-xs text-gray-500 dark:text-gray-400 max-w-md mx-auto">
            💡 For fine-grained control and customization, switch to 
            <span class="font-medium text-blue-600 dark:text-blue-400">Groups view</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  eventTypes: { type: Array, default: () => [] },
  mainEventTypes: { type: Array, default: () => [] },
  singleEventTypes: { type: Array, default: () => [] },
  allEventTypes: { type: Array, default: () => [] }, // Unfiltered event types for visibility check
  selectedEventTypes: { type: Array, default: () => [] },
  expandedEventTypes: { type: Array, default: () => [] },
  showSingleEvents: { type: Boolean, default: false },
  showEventTypesSection: { type: Boolean, default: true },
  showSelectedOnly: { type: Boolean, default: false },
  searchTerm: { type: String, default: '' },
  hasGroups: { type: Boolean, default: false },
  formatDateTime: { type: Function, required: true },
  formatDateRange: { type: Function, required: true }
})

// Check if there are any event types at all (for section visibility)
// Use unfiltered event types to prevent section from disappearing during search
const hasAnyEventTypes = computed(() => {
  return props.allEventTypes.length > 0
})

// Filtered event types based on search and selection
const filteredMainEventTypes = computed(() => {
  let eventTypes = props.mainEventTypes
  
  // Filter by selection if showSelectedOnly is true
  if (props.showSelectedOnly) {
    eventTypes = eventTypes.filter(eventType => 
      props.selectedEventTypes.includes(eventType.name)
    )
  }
  
  // Filter by search term
  if (props.searchTerm.trim()) {
    const searchTerm = props.searchTerm.toLowerCase()
    eventTypes = eventTypes.filter(eventType => 
      eventType.name.toLowerCase().includes(searchTerm)
    )
  }
  
  return eventTypes
})

const filteredSingleEventTypes = computed(() => {
  let eventTypes = props.singleEventTypes
  
  // Filter by selection if showSelectedOnly is true
  if (props.showSelectedOnly) {
    eventTypes = eventTypes.filter(eventType => 
      props.selectedEventTypes.includes(eventType.name)
    )
  }
  
  // Filter by search term
  if (props.searchTerm.trim()) {
    const searchTerm = props.searchTerm.toLowerCase()
    eventTypes = eventTypes.filter(eventType => 
      eventType.name.toLowerCase().includes(searchTerm)
    )
  }
  
  return eventTypes
})

// Singles selection state
const areAllSinglesSelected = computed(() => {
  if (filteredSingleEventTypes.value.length === 0) return false
  const singleNames = filteredSingleEventTypes.value.map(eventType => eventType.name)
  return singleNames.every(name => props.selectedEventTypes.includes(name))
})

const selectedSinglesCount = computed(() => {
  const singleNames = filteredSingleEventTypes.value.map(eventType => eventType.name)
  return singleNames.filter(name => props.selectedEventTypes.includes(name)).length
})

// Visible selection state for main event types
const areAllVisibleSelected = computed(() => {
  if (filteredMainEventTypes.value.length === 0) return false
  const visibleNames = filteredMainEventTypes.value.map(eventType => eventType.name)
  return visibleNames.every(name => props.selectedEventTypes.includes(name))
})

const hasAnyVisibleSelected = computed(() => {
  const visibleNames = filteredMainEventTypes.value.map(eventType => eventType.name)
  return visibleNames.some(name => props.selectedEventTypes.includes(name))
})

// Check if filtering/search results in any visible event types
const hasAnyVisibleEventTypes = computed(() => {
  return filteredMainEventTypes.value.length > 0 || filteredSingleEventTypes.value.length > 0
})

// Methods for visible event type selection
function selectAllVisible() {
  const visibleNames = filteredMainEventTypes.value.map(eventType => eventType.name)
  visibleNames.forEach(name => {
    if (!props.selectedEventTypes.includes(name)) {
      emit('toggle-event-type', name)
    }
  })
}

function clearAllVisible() {
  const visibleNames = filteredMainEventTypes.value.map(eventType => eventType.name)
  visibleNames.forEach(name => {
    if (props.selectedEventTypes.includes(name)) {
      emit('toggle-event-type', name)
    }
  })
}

const emit = defineEmits([
  'clear-all',
  'select-all', 
  'update:search-term',
  'toggle-event-type',
  'toggle-expansion',
  'toggle-singles-visibility',
  'select-all-singles',
  'clear-all-singles',
  'toggle-selected-only',
  'subscribe-all-groups',
  'unsubscribe-all-groups',
  'switch-to-groups',
  'toggle-event-types-section'
])

// Make showSingleEvents and showCategoriesSection writable
const showSingleEvents = computed({
  get: () => props.showSingleEvents,
  set: (value) => emit('toggle-singles-visibility', value)
})

</script>