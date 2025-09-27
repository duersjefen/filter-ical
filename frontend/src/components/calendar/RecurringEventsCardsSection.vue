<template>
  <div v-if="hasAnyRecurringEvents" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
    <!-- Header with Switch Button -->
    <div 
      class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700"
      :class="props.showRecurringEventsSection ? 'rounded-t-xl' : 'rounded-xl'"
    >
      <!-- Mobile Layout -->
      <div class="block sm:hidden">
        <div class="flex items-center justify-between mb-3">
          <div class="flex-1">
            <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">
              📂 {{ $t('calendar.recurringEvents') }}
            </h3>
          </div>
          <!-- Mobile Switch Button - Compact Modern Design -->
          <button
            v-if="hasGroups"
            @click="$emit('switch-to-groups')"
            class="group px-4 py-2.5 rounded-lg bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white shadow-md hover:shadow-lg transition-all duration-200 flex items-center gap-2 transform hover:scale-105 active:scale-95"
            :title="$t('ui.switchToGroupsView')"
          >
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
            <span class="text-sm font-semibold text-white">Groups</span>
            <svg class="w-4 h-4 text-white group-hover:translate-x-0.5 transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <!-- Status text on mobile -->
        <p class="text-xs text-gray-600 dark:text-gray-400 text-center leading-tight">
          {{ summaryText || (selectedRecurringEvents.length > 0 
            ? $t('recurringEvents.selectedRecurringEvents', { count: selectedRecurringEvents.length, total: allRecurringEvents.length })
            : $t('recurringEvents.selectRecurringEventsBelow')) }}
        </p>
      </div>

      <!-- Desktop Layout -->
      <div class="hidden sm:flex items-center justify-between">
        <!-- Left: Header Info with collapse button -->
        <div class="flex items-center gap-3 flex-1 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg p-2 -m-2 transition-colors duration-200" @click="$emit('toggle-recurring-events-section')">
          <!-- Dropdown Icon (standardized design) -->
          <svg 
            class="w-4 h-4 text-gray-400 transition-transform duration-300"
            :class="{ 'rotate-90': props.showRecurringEventsSection }"
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
          
          <div class="flex-1">
            <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              📂 {{ $t('calendar.recurringEvents') }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ summaryText || (selectedRecurringEvents.length > 0 
                ? $t('recurringEvents.selectedRecurringEvents', { count: selectedRecurringEvents.length, total: allRecurringEvents.length })
                : $t('recurringEvents.selectRecurringEventsBelow')) }}
            </p>
          </div>
        </div>
        
        <!-- Desktop Switch Button - Enhanced Modern Design -->
        <button
          v-if="hasGroups"
          @click="$emit('switch-to-groups')"
          class="group relative px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-3 ml-4 transform hover:scale-105 active:scale-95"
          title="Switch to Groups view"
        >
          <!-- Switch Icon -->
          <div class="flex items-center justify-center w-8 h-8 bg-white/20 rounded-lg group-hover:bg-white/30 transition-colors duration-200">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
          </div>
          
          <!-- Switch Text -->
          <div class="text-left">
            <div class="text-sm font-bold text-white mb-0.5">
              Switch to Groups View
            </div>
            <div class="text-xs text-emerald-100">
              Browse by calendar groups
            </div>
          </div>
          
          <!-- Arrow Icon -->
          <svg class="w-5 h-5 text-white group-hover:translate-x-1 transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Collapsible Content -->
    <div v-if="props.showRecurringEventsSection" class="p-3 sm:p-4">
      <!-- Enhanced Action Buttons -->
      <div class="flex flex-wrap gap-3 justify-center mb-6 px-1">
        <!-- When NOT searching: Show All/Clear All -->
        <template v-if="!searchTerm.trim()">
          <button 
            @click="$emit('clear-all')" 
            class="px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] bg-gray-500 hover:bg-gray-400 text-white border-2 border-gray-400 hover:border-gray-300"
          >
            {{ $t('recurringEvents.clearAll') }}
          </button>
          <button 
            @click="$emit('select-all')" 
            class="px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] bg-blue-500 hover:bg-blue-600 text-white border-2 border-blue-400 hover:border-blue-500"
          >
            {{ $t('recurringEvents.selectAll') }}
          </button>
        </template>
        
        <!-- When searching: Show contextual buttons -->
        <template v-else>
          <button 
            v-if="hasAnyVisibleSelected"
            @click="clearAllVisible"
            class="px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] bg-red-500 hover:bg-red-600 text-white border-2 border-red-400 hover:border-red-500"
          >
            {{ $t('recurringEvents.clearVisible') }}
          </button>
          <button 
            v-if="!areAllVisibleSelected"
            @click="selectAllVisible"
            class="px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] bg-green-500 hover:bg-green-600 text-white border-2 border-green-400 hover:border-green-500"
          >
            {{ $t('recurringEvents.selectVisible', { count: filteredMainRecurringEvents.length + filteredSingleRecurringEvents.length }) }}
          </button>
        </template>
        
        <!-- Enhanced Show Selected Only / Show All Toggle -->
        <button
          v-if="selectedRecurringEvents.length > 0 && !searchTerm.trim()"
          @click="$emit('toggle-selected-only')"
          :class="showSelectedOnly 
            ? 'bg-orange-500 hover:bg-orange-600 text-white border-orange-400 hover:border-orange-500' 
            : 'bg-indigo-500 hover:bg-indigo-600 text-white border-indigo-400 hover:border-indigo-500'"
          class="px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] border-2"
        >
          <span class="hidden sm:inline">{{ showSelectedOnly ? $t('viewControls.showAll') : $t('viewControls.showSelectedOnly') }}</span>
          <span class="sm:hidden">{{ showSelectedOnly ? $t('viewControls.showAllShort') : $t('viewControls.showSelectedShort') }}</span>
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
      
      <!-- Multi-Events -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4 items-start">
        <div 
          v-for="recurringEvent in filteredMainRecurringEvents" 
          :key="recurringEvent.name"
          class="border rounded-lg transition-all duration-200 cursor-pointer group/item"
          :class="selectedRecurringEvents.includes(recurringEvent.name)
            ? 'border-blue-400 bg-blue-50/50 dark:bg-blue-900/20 dark:border-blue-500 shadow-sm' 
            : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-sm'"
          @click="$emit('toggle-recurring-event', recurringEvent.name)"
          :title="`Click to ${selectedRecurringEvents.includes(recurringEvent.name) ? 'deselect' : 'select'} ${recurringEvent.name}`"
        >
          <!-- Recurring Event Header - Entire row clickable -->
          <div class="flex items-center gap-3 p-3 transition-colors">
            <!-- Recurring Event Checkbox -->
            <div 
              class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs transition-all flex-shrink-0"
              :class="selectedRecurringEvents.includes(recurringEvent.name)
                ? 'bg-blue-500 border-blue-500 text-white' 
                : 'border-gray-300 dark:border-gray-400 bg-white dark:bg-gray-700 group-hover/item:border-blue-400'"
            >
              <span v-if="selectedRecurringEvents.includes(recurringEvent.name)">✓</span>
            </div>
            
            <!-- Recurring Event Info - Enhanced Layout -->
            <div class="flex-1 min-w-0">
              <div class="font-semibold text-gray-900 dark:text-gray-100 truncate group-hover/item:text-blue-600 dark:group-hover/item:text-blue-400 transition-colors">
                {{ recurringEvent.name.trim() }}
              </div>
            </div>
            
            <!-- Count badge and expansion arrow -->
            <div class="flex items-center gap-2">
              <!-- Event count badge beside dropdown arrow -->
              <div class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 group-hover/item:bg-blue-100 dark:group-hover/item:bg-blue-900/40 group-hover/item:text-blue-800 dark:group-hover/item:text-blue-200 transition-colors">
                {{ recurringEvent.count }}
              </div>
              
              <!-- Expansion Arrow (larger and standardized) -->
              <button
                @click.stop="$emit('toggle-expansion', recurringEvent.name)"
                class="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors flex-shrink-0"
                title="Click to view individual events"
              >
                <svg 
                  class="w-5 h-5 text-gray-400 group-hover/item:text-blue-500 dark:group-hover/item:text-blue-400 transition-transform duration-300" 
                  :class="{ 'rotate-90': expandedRecurringEvents.has(recurringEvent.name) }"
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Expandable Events List -->
          <div 
            v-if="expandedRecurringEvents.has(recurringEvent.name)"
            class="border-t border-gray-100 dark:border-gray-700 bg-gray-25 dark:bg-gray-900/20"
          >
            <!-- Events List (Compact Display) -->
            <div class="space-y-1">
              <div 
                v-for="event in recurringEvent.events" 
                :key="event.uid"
                class="px-2 py-1.5 bg-gray-50 dark:bg-gray-800/30 rounded text-xs"
              >
                <!-- Event Title (if different from recurring event name) -->
                <div v-if="event.title !== recurringEvent.name" class="font-medium text-gray-800 dark:text-gray-200 text-sm mb-1">{{ event.title.trim() }}</div>
                
                <!-- Compact Event Details -->
                <div class="text-gray-700 dark:text-gray-300">
                  {{ formatDateRange(event) }}
                  <span v-if="event.is_recurring" class="ml-1">🔄</span>
                </div>
                <div v-if="event.location" class="text-gray-600 dark:text-gray-400 mt-0.5">
                  📍 {{ event.location.trim() }}
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
        class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
      >
        <!-- Singles Header - Entire area clickable for expand/collapse -->
        <div 
          class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-4 py-4 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-slate-100 dark:hover:bg-gray-700 transition-colors duration-200"
          @click="$emit('toggle-singles-visibility')"
          :title="showSingleEvents ? 'Click to collapse unique events list' : 'Click to expand and see all unique events'"
        >
          <div class="flex items-center gap-3">
            <!-- Chevron icon -->
            <svg 
              class="w-4 h-4 text-gray-600 dark:text-gray-300 transition-transform duration-300 flex-shrink-0" 
              :class="{ 'rotate-90': showSingleEvents }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            
            <div class="flex-1">
              <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-1">
                📄 {{ $t('recurringEvents.uniqueEvents') }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ selectedSinglesCount }}/{{ filteredSingleRecurringEvents.length }} events selected
              </p>
            </div>
            
            <!-- Selection count badge -->
            <div class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium transition-colors bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 mr-3">
              {{ selectedSinglesCount }}/{{ filteredSingleRecurringEvents.length }}
            </div>
            
            <!-- Enhanced Select/Deselect All Button -->
            <button
              @click.stop="handleSinglesToggle"
              class="px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 shadow-sm hover:shadow-md flex items-center justify-center gap-2 z-10 relative min-w-[120px] border-2 transform hover:scale-[1.02] active:scale-[0.98] min-h-[40px]"
              :class="areAllSinglesSelected
                ? 'bg-gray-500 hover:bg-gray-400 text-white border-gray-400 hover:border-gray-300'
                : 'bg-blue-500 hover:bg-blue-600 text-white border-blue-400 hover:border-blue-500'"
            >
              <span v-if="areAllSinglesSelected">{{ $t('viewControls.deselectAllSingles') }}</span>
              <span v-else>{{ $t('viewControls.selectAllSingles') }}</span>
            </button>
          </div>
        </div>

        <!-- Singles List (when expanded) -->
        <div v-if="showSingleEvents" class="p-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 items-start">
            <div 
              v-for="recurringEvent in filteredSingleRecurringEvents"
              :key="recurringEvent.name"
              class="border rounded-lg transition-all duration-200 cursor-pointer group/item"
              :class="selectedRecurringEvents.includes(recurringEvent.name)
                ? 'border-blue-400 bg-blue-50/50 dark:bg-blue-900/20 dark:border-blue-500 shadow-sm' 
                : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-sm'"
              @click="$emit('toggle-recurring-event', recurringEvent.name)"
              :title="`Click to ${selectedRecurringEvents.includes(recurringEvent.name) ? 'deselect' : 'select'} ${recurringEvent.name}`"
            >
              <!-- Event Header - Entire row clickable -->
              <div class="flex items-center gap-3 p-3 transition-colors">
                <!-- Event Checkbox -->
                <div 
                  class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs transition-all flex-shrink-0"
                  :class="selectedRecurringEvents.includes(recurringEvent.name)
                    ? 'bg-blue-500 border-blue-500 text-white' 
                    : 'border-gray-300 dark:border-gray-400 bg-white dark:bg-gray-700 group-hover/item:border-blue-400'"
                >
                  <span v-if="selectedRecurringEvents.includes(recurringEvent.name)">✓</span>
                </div>
                
                <!-- Event Info - Enhanced Layout -->
                <div class="flex-1 min-w-0">
                  <div class="font-semibold text-gray-900 dark:text-gray-100 truncate group-hover/item:text-blue-600 dark:group-hover/item:text-blue-400 transition-colors mb-1">
                    {{ recurringEvent.name.trim() }}
                  </div>
                  <!-- Event Details -->
                  <div class="space-y-0.5 h-8 flex flex-col justify-start">
                    <div class="text-xs text-gray-600 dark:text-gray-400 font-medium">
                      {{ formatDateRange(recurringEvent.events[0]) }}
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400 min-h-[1rem]">
                      <template v-if="recurringEvent.events[0].location">
                        <span class="truncate">{{ recurringEvent.events[0].location }}</span>
                      </template>
                      <template v-else>
                        <!-- Reserve space for consistency -->
                        <span class="opacity-0">No location</span>
                      </template>
                    </div>
                  </div>
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
            <!-- Enhanced Subscribe to All Groups -->
            <button
              @click="$emit('subscribe-all-groups')"
              class="px-4 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-xl transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 border-2 border-green-400 hover:border-green-500 min-h-[44px]"
            >
              <span>{{ $t('viewControls.subscribeToAllGroups') }}</span>
            </button>
            
            <!-- Enhanced Unsubscribe & Deselect All Groups -->
            <button
              @click="$emit('unsubscribe-all-groups')"
              class="px-4 py-3 bg-gray-500 hover:bg-gray-400 text-white font-semibold rounded-xl transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 border-2 border-gray-400 hover:border-gray-300 min-h-[44px]"
            >
              <span>{{ $t('viewControls.unsubscribeFromAllGroups') }}</span>
            </button>
          </div>
          
          <!-- Helper Text -->
          <p class="mt-3 text-xs text-gray-500 dark:text-gray-400 max-w-md mx-auto">
            💡 For fine-grained control and customization, switch to 
            <span class="font-medium text-blue-600 dark:text-blue-400">{{ $t('viewControls.groupsView') }}</span>
          </p>
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
  allRecurringEvents: { type: Array, default: () => [] }, // Unfiltered events for visibility check
  selectedRecurringEvents: { type: Array, default: () => [] },
  expandedRecurringEvents: { type: Set, default: () => new Set() },
  showSingleEvents: { type: Boolean, default: false },
  showRecurringEventsSection: { type: Boolean, default: true },
  showSelectedOnly: { type: Boolean, default: false },
  searchTerm: { type: String, default: '' },
  hasGroups: { type: Boolean, default: false },
  summaryText: { type: String, default: '' },
  formatDateTime: { type: Function, required: true },
  formatDateRange: { type: Function, required: true }
})

// Check if there are any events at all (for section visibility)
// Use unfiltered events to prevent section from disappearing during search
const hasAnyRecurringEvents = computed(() => {
  return props.allRecurringEvents.length > 0
})

// Filtered events based on search and selection
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

// Visible selection state for main events
const areAllVisibleSelected = computed(() => {
  if (filteredMainRecurringEvents.value.length === 0) return false
  const visibleNames = filteredMainRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  return visibleNames.every(name => props.selectedRecurringEvents.includes(name))
})

const hasAnyVisibleSelected = computed(() => {
  const visibleNames = filteredMainRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  return visibleNames.some(name => props.selectedRecurringEvents.includes(name))
})

// Check if filtering/search results in any visible events
const hasAnyVisibleRecurringEvents = computed(() => {
  return filteredMainRecurringEvents.value.length > 0 || filteredSingleRecurringEvents.value.length > 0
})

// Methods for visible event type selection
function selectAllVisible() {
  // Select all visible main recurring events
  const visibleMainNames = filteredMainRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  visibleMainNames.forEach(name => {
    if (!props.selectedRecurringEvents.includes(name)) {
      emit('toggle-recurring-event', name)
    }
  })
  
  // Also select all visible single recurring events
  const visibleSingleNames = filteredSingleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  visibleSingleNames.forEach(name => {
    if (!props.selectedRecurringEvents.includes(name)) {
      emit('toggle-recurring-event', name)
    }
  })
}

function clearAllVisible() {
  // Clear all visible main recurring events
  const visibleMainNames = filteredMainRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  visibleMainNames.forEach(name => {
    if (props.selectedRecurringEvents.includes(name)) {
      emit('toggle-recurring-event', name)
    }
  })
  
  // Also clear all visible single recurring events
  const visibleSingleNames = filteredSingleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  visibleSingleNames.forEach(name => {
    if (props.selectedRecurringEvents.includes(name)) {
      emit('toggle-recurring-event', name)
    }
  })
}

function handleSinglesCardClick() {
  // During filtering: select/deselect only visible filtered unique events
  if (props.searchTerm.trim()) {
    const visibleSingleNames = filteredSingleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
    const allVisibleSelected = visibleSingleNames.every(name => props.selectedRecurringEvents.includes(name))
    
    if (allVisibleSelected) {
      // Deselect visible unique events
      visibleSingleNames.forEach(name => {
        if (props.selectedRecurringEvents.includes(name)) {
          emit('toggle-recurring-event', name)
        }
      })
    } else {
      // Select visible unique events
      visibleSingleNames.forEach(name => {
        if (!props.selectedRecurringEvents.includes(name)) {
          emit('toggle-recurring-event', name)
        }
      })
    }
  } else {
    // No filtering: select/deselect ALL unique events using unified system
    const allSingleNames = filteredSingleRecurringEvents.value.map(recurringEvent => recurringEvent.name)
    const allSelected = allSingleNames.every(name => props.selectedRecurringEvents.includes(name))
    
    if (allSelected) {
      // Deselect all unique events
      allSingleNames.forEach(name => {
        if (props.selectedRecurringEvents.includes(name)) {
          emit('toggle-recurring-event', name)
        }
      })
    } else {
      // Select all unique events
      allSingleNames.forEach(name => {
        if (!props.selectedRecurringEvents.includes(name)) {
          emit('toggle-recurring-event', name)
        }
      })
    }
  }
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
  'subscribe-all-groups',
  'unsubscribe-all-groups',
  'switch-to-groups',
  'toggle-recurring-events-section'
])

// Make showSingleEvents and showCategoriesSection writable
const showSingleEvents = computed({
  get: () => props.showSingleEvents,
  set: (value) => emit('toggle-singles-visibility', value)
})

// Handle singles toggle button explicitly
function handleSinglesToggle() {
  if (areAllSinglesSelected.value) {
    emit('clear-all-singles')
  } else {
    emit('select-all-singles')
  }
}

</script>