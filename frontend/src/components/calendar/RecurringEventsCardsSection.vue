<template>
  <div v-if="hasAnyRecurringEvents" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden hover:shadow-2xl hover:shadow-purple-500/10 dark:hover:shadow-purple-400/20 transition-all duration-500 transform" :class="{ 'hover:scale-[1.02]': !props.showRecurringEventsSection }">
    <!-- Header with Switch Button -->
    <div 
      class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700"
      :class="props.showRecurringEventsSection ? 'rounded-t-xl' : 'rounded-xl'"
    >
      <!-- Mobile Layout -->
      <div class="block sm:hidden">
        <div class="flex items-center justify-between mb-3">
          <div class="flex-1">
            <h3 class="text-2xl font-black text-gray-900 dark:text-gray-100 tracking-tight">
              📂 <span class="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">{{ $t('calendar.recurringEvents') }}</span>
            </h3>
          </div>
          <!-- Mobile Switch Button - Enhanced Modern Design -->
          <button
            v-if="hasGroups"
            @click="$emit('switch-to-groups')"
            class="group relative px-4 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2 transform hover:scale-105 active:scale-95"
            :title="$t('ui.switchToGroupsView')"
          >
            <!-- Switch Icon -->
            <div class="flex items-center justify-center w-6 h-6 bg-white/20 rounded-lg group-hover:bg-white/30 transition-colors duration-200">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
              </svg>
            </div>
            
            <!-- Switch Text -->
            <div class="text-xs font-bold text-white">
              Groups
            </div>
          </button>
        </div>
        <!-- Enhanced status text on mobile -->
        <p class="text-sm font-medium text-gray-700 dark:text-gray-300 text-center leading-tight mt-2">
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
            <h3 class="text-2xl sm:text-3xl font-black text-gray-900 dark:text-gray-100 mb-2 tracking-tight">
              📂 <span class="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">{{ $t('calendar.recurringEvents') }}</span>
            </h3>
            <p class="text-base font-medium text-gray-700 dark:text-gray-300 leading-relaxed">
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
          class="group relative px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-3 ml-4 transform hover:scale-105 active:scale-95"
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
            <div class="text-xs text-blue-100">
              Browse by organized groups
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
      <!-- Enhanced Action Bar -->
      <div class="mb-6">
        <!-- Primary Actions Row -->
        <div class="flex flex-col gap-4 sm:flex-row sm:gap-4 mb-4">
          <!-- Quick Actions -->
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-3 flex-1">
            <!-- When NOT searching: Show All/Clear All -->
            <template v-if="!searchTerm.trim()">
              <button 
                v-if="!areAllRecurringEventsSelected && allRecurringEvents.length > 0"
                @click="$emit('select-all')" 
                class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                {{ $t('recurringEvents.selectAll') }}
              </button>
              
              <button 
                v-if="hasAnyRecurringEventsSelected"
                @click="$emit('clear-all')" 
                class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-lg bg-gray-600 hover:bg-gray-700 text-white shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                {{ $t('recurringEvents.deselectAll') }}
              </button>
            </template>
            
            <!-- When searching: Show contextual buttons -->
            <template v-else>
              <button 
                v-if="!areAllVisibleSelected && (filteredMainRecurringEvents.length + filteredSingleRecurringEvents.length) > 0"
                @click="selectAllVisible"
                class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                Select visible ({{ filteredMainRecurringEvents.length + filteredSingleRecurringEvents.length }})
              </button>
              
              <button 
                v-if="hasAnyVisibleSelected"
                @click="clearAllVisible"
                class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-lg bg-gray-600 hover:bg-gray-700 text-white shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                {{ $t('recurringEvents.deselectVisible') }}
              </button>
            </template>
          </div>
          
          <!-- View Controls -->
          <div class="flex justify-center sm:justify-end">
            <!-- Show Selected Only Toggle -->
            <button
              v-if="selectedRecurringEvents.length > 0 && !searchTerm.trim()"
              @click="$emit('toggle-selected-only')"
              class="inline-flex items-center gap-2 px-4 py-3 sm:py-2.5 text-sm font-medium rounded-lg border-2 transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] sm:min-h-auto w-full sm:w-auto justify-center touch-manipulation"
              :class="showSelectedOnly 
                ? 'bg-orange-50 hover:bg-orange-100 text-orange-700 border-orange-200 hover:border-orange-300 dark:bg-orange-900/20 dark:hover:bg-orange-900/30 dark:text-orange-300 dark:border-orange-700' 
                : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border-indigo-200 hover:border-indigo-300 dark:bg-indigo-900/20 dark:hover:bg-indigo-900/30 dark:text-indigo-300 dark:border-indigo-700'"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path v-if="showSelectedOnly" fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
                <path v-else fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
              </svg>
              <span class="hidden sm:inline">{{ showSelectedOnly ? $t('viewControls.showAll') : $t('viewControls.showSelectedOnly') }}</span>
              <span class="sm:hidden">{{ showSelectedOnly ? 'Show All' : 'Show Selected' }}</span>
            </button>
          </div>
        </div>
        
        <!-- Removed redundant selection summary as it's already in the header -->
      </div>

      <!-- Enhanced Search Interface -->
      <div class="mb-6">
        <div class="relative">
          <!-- Search Icon -->
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <!-- Search Input -->
          <input 
            :value="searchTerm"
            @input="$emit('update:search-term', $event.target.value)"
            type="text" 
            :placeholder="$t('recurringEvents.searchRecurringEvents')"
            class="w-full pl-12 pr-12 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 rounded-xl focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm text-base"
          >
          
          <!-- Clear Search Button -->
          <button
            v-if="searchTerm.trim()"
            @click="$emit('update:search-term', '')"
            class="absolute inset-y-0 right-0 pr-4 flex items-center group"
            :title="$t('recurringEvents.clearSearch')"
          >
            <div class="w-7 h-7 bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-600 dark:text-gray-300 hover:text-gray-700 dark:hover:text-gray-200 rounded-lg flex items-center justify-center transition-all duration-200 group-hover:scale-110">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </div>
          </button>
        </div>
        
        <!-- Search Results Summary -->
        <div v-if="searchTerm.trim()" class="mt-3 flex items-center justify-between text-sm">
          <span class="text-gray-600 dark:text-gray-400">
            <span class="font-medium">{{ filteredMainRecurringEvents.length + filteredSingleRecurringEvents.length }}</span> 
            events found for "<span class="font-medium text-gray-900 dark:text-gray-100">{{ searchTerm.trim() }}</span>"
          </span>
          <button 
            v-if="filteredMainRecurringEvents.length + filteredSingleRecurringEvents.length > 0"
            @click="selectAllVisible"
            class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium transition-colors"
          >
            Select all results
          </button>
        </div>
      </div>
      
      <!-- Concise Event Cards Grid - 4 columns for better space usage -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 mb-4 items-start">
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
          <!-- Two-Row Event Header -->
          <div class="p-3 transition-colors">
            <!-- Row 1: Checkbox and Title -->
            <div class="flex items-center gap-3 mb-2">
              <!-- Checkbox -->
              <div 
                class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs transition-all flex-shrink-0"
                :class="selectedRecurringEvents.includes(recurringEvent.name)
                  ? 'bg-blue-500 border-blue-500 text-white' 
                  : 'border-gray-300 dark:border-gray-400 bg-white dark:bg-gray-700 group-hover/item:border-blue-400'"
              >
                <span v-if="selectedRecurringEvents.includes(recurringEvent.name)">✓</span>
              </div>
              
              <!-- Event Title -->
              <div class="flex-1 min-w-0">
                <div class="font-semibold text-gray-900 dark:text-gray-100 truncate group-hover/item:text-blue-600 dark:group-hover/item:text-blue-400 transition-colors">
                  {{ recurringEvent.name.trim() }}
                </div>
              </div>
            </div>
            
            <!-- Row 2: Day Pattern, Count, and Expand Button -->
            <div class="flex items-center justify-between gap-2">
              <!-- Day Pattern -->
              <div class="flex-1 min-w-0">
                <div v-if="getRecurringEventDayPattern(recurringEvent)" class="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {{ getRecurringEventDayPattern(recurringEvent) }}
                </div>
              </div>
              
              <!-- Count Badge -->
              <div class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 group-hover/item:bg-blue-100 dark:group-hover/item:bg-blue-900/40 group-hover/item:text-blue-800 dark:group-hover/item:text-blue-200 transition-colors flex-shrink-0">
                {{ recurringEvent.count }}
              </div>
              
              <!-- Enhanced Expansion Button -->
              <button
                @click.stop="$emit('toggle-expansion', recurringEvent.name)"
                class="flex items-center gap-1 px-2 py-1 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-all duration-200 flex-shrink-0 group/expand"
                :class="expandedRecurringEvents.has(recurringEvent.name) 
                  ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' 
                  : 'text-gray-500 dark:text-gray-400'"
                :title="expandedRecurringEvents.has(recurringEvent.name) ? 'Hide individual events' : 'Show individual events'"
              >
                <span class="text-xs font-medium group-hover/expand:text-blue-600 dark:group-hover/expand:text-blue-400 transition-colors">
                  {{ expandedRecurringEvents.has(recurringEvent.name) ? 'Hide' : 'Show' }}
                </span>
                <svg 
                  class="w-3 h-3 transition-transform duration-300" 
                  :class="{ 'rotate-180': expandedRecurringEvents.has(recurringEvent.name) }"
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Concise Expandable Events List -->
          <div 
            v-if="expandedRecurringEvents.has(recurringEvent.name)"
            class="border-t border-gray-100 dark:border-gray-700 bg-gray-25 dark:bg-gray-900/20"
          >
            <!-- Ultra-Compact Events List -->
            <div class="max-h-48 overflow-y-auto">
              <div 
                v-for="event in recurringEvent.events" 
                :key="event.uid"
                class="px-3 py-1.5 border-b border-gray-100 dark:border-gray-700 last:border-b-0 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors"
              >
                <!-- Single Line Layout -->
                <div class="flex items-center justify-between gap-3 text-xs">
                  <!-- Left: Date and Title -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <!-- Concise Date with Pattern Awareness -->
                      <span class="font-mono text-gray-600 dark:text-gray-400 whitespace-nowrap">
                        {{ formatCompactEventDate(event, !!getRecurringEventDayPattern(recurringEvent)) }}
                      </span>
                      <!-- Recurring indicator -->
                      <span v-if="event.is_recurring" class="text-blue-500" title="Recurring event">🔄</span>
                      <!-- Title (only if different) -->
                      <span v-if="event.title !== recurringEvent.name" class="font-medium text-gray-800 dark:text-gray-200 truncate">
                        {{ event.title.trim() }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- Right: Location -->
                  <div v-if="event.location" class="text-gray-500 dark:text-gray-400 text-right truncate max-w-[40%]" :title="event.location.trim()">
                    {{ event.location.trim() }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced No Results Message -->
      <div 
        v-if="!hasAnyVisibleRecurringEvents && (searchTerm.trim() || showSelectedOnly)" 
        class="text-center py-12 px-6 mx-auto max-w-md"
      >
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
          <!-- Icon -->
          <div class="mb-6">
            <div class="w-16 h-16 mx-auto bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
              <svg v-if="searchTerm.trim()" class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <svg v-else class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
          </div>
          
          <!-- Message -->
          <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
            {{ searchTerm.trim() ? 'No events found' : 'No selected events visible' }}
          </h3>
          
          <p class="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
            <template v-if="searchTerm.trim()">
              No events match "<span class="font-semibold text-gray-900 dark:text-gray-100">{{ searchTerm.trim() }}</span>". 
              Try adjusting your search terms or browse all events.
            </template>
            <template v-else>
              You haven't selected any events yet. Select some events above to see them here.
            </template>
          </p>
          
          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-3 justify-center">
            <button 
              v-if="searchTerm.trim()"
              @click="$emit('update:search-term', '')"
              class="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
              </svg>
              Clear search
            </button>
            <button 
              v-else
              @click="$emit('toggle-selected-only')"
              class="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
              </svg>
              Show all events
            </button>
          </div>
        </div>
      </div>

      <!-- Enhanced Unique Events Section -->
      <div 
        v-if="filteredSingleRecurringEvents.length > 0" 
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden transition-all duration-300 hover:shadow-md"
      >
        <!-- Modern Header -->
        <div 
          class="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 px-6 py-4 border-b border-emerald-200 dark:border-emerald-700 cursor-pointer hover:from-emerald-100 hover:to-teal-100 dark:hover:from-emerald-900/30 dark:hover:to-teal-900/30 transition-all duration-200"
          @click="$emit('toggle-singles-visibility')"
          :title="showSingleEvents ? 'Click to collapse unique events' : 'Click to expand unique events'"
        >
          <div class="flex items-center justify-between">
            <!-- Left: Title and Info -->
            <div class="flex items-center gap-4">
              <!-- Expand/Collapse Icon -->
              <div class="flex-shrink-0">
                <div class="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center transition-transform duration-300"
                     :class="{ 'rotate-180': showSingleEvents }">
                  <svg class="w-4 h-4 text-emerald-600 dark:text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
              
              <!-- Title and Description -->
              <div>
                <h3 class="text-lg font-bold text-emerald-900 dark:text-emerald-100 mb-1 flex items-center gap-2">
                  <span class="text-xl">📄</span>
                  {{ $t('recurringEvents.uniqueEvents') }}
                </h3>
                <p class="text-sm text-emerald-700 dark:text-emerald-300">
                  One-time events • {{ selectedSinglesCount }}/{{ filteredSingleRecurringEvents.length }} selected
                </p>
              </div>
            </div>
            
            <!-- Right: Actions -->
            <div class="flex items-center gap-3">
              <!-- Selection Progress -->
              <div class="hidden sm:flex items-center gap-2">
                <div class="w-16 h-2 bg-emerald-200 dark:bg-emerald-800 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-emerald-500 dark:bg-emerald-400 transition-all duration-300"
                    :style="{ width: `${filteredSingleRecurringEvents.length > 0 ? (selectedSinglesCount / filteredSingleRecurringEvents.length) * 100 : 0}%` }"
                  ></div>
                </div>
                <span class="text-xs font-medium text-emerald-700 dark:text-emerald-300 min-w-[3rem]">
                  {{ Math.round(filteredSingleRecurringEvents.length > 0 ? (selectedSinglesCount / filteredSingleRecurringEvents.length) * 100 : 0) }}%
                </span>
              </div>
              
              <!-- Select/Deselect Button -->
              <button
                @click.stop="handleSinglesToggle"
                class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98]"
                :class="areAllSinglesSelected
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  : 'bg-white hover:bg-emerald-50 text-emerald-700 border border-emerald-300 hover:border-emerald-400 dark:bg-gray-700 dark:hover:bg-emerald-900/20 dark:text-emerald-300 dark:border-emerald-600'"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path v-if="areAllSinglesSelected" fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  <path v-else fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span>{{ areAllSinglesSelected ? 'Deselect All' : 'Select All' }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Expanded Unique Events List -->
        <div v-if="showSingleEvents" class="p-6">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div 
              v-for="recurringEvent in filteredSingleRecurringEvents"
              :key="recurringEvent.name"
              class="group/card relative bg-gray-50 dark:bg-gray-800/50 rounded-lg border transition-all duration-300 cursor-pointer overflow-hidden hover:shadow-md"
              :class="selectedRecurringEvents.includes(recurringEvent.name)
                ? 'border-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 dark:border-emerald-500 shadow-sm scale-[1.02]' 
                : 'border-gray-200 dark:border-gray-600 hover:border-emerald-300 dark:hover:border-emerald-500'"
              @click="$emit('toggle-recurring-event', recurringEvent.name)"
              :title="`${selectedRecurringEvents.includes(recurringEvent.name) ? 'Deselect' : 'Select'} ${recurringEvent.name}`"
            >
              <!-- Selection Indicator -->
              <div 
                class="absolute top-0 left-0 right-0 h-1 transition-all duration-300"
                :class="selectedRecurringEvents.includes(recurringEvent.name) ? 'bg-emerald-500' : 'bg-gray-200 dark:bg-gray-700'"
              ></div>
              
              <!-- Card Content -->
              <div class="p-4">
                <!-- Header -->
                <div class="flex items-start gap-3 mb-3">
                  <!-- Checkbox -->
                  <div 
                    class="flex-shrink-0 w-4 h-4 rounded border-2 flex items-center justify-center transition-all duration-200 mt-1"
                    :class="selectedRecurringEvents.includes(recurringEvent.name)
                      ? 'bg-emerald-500 border-emerald-500 text-white' 
                      : 'border-gray-300 dark:border-gray-500 bg-white dark:bg-gray-700 group-hover/card:border-emerald-400'"
                  >
                    <svg v-if="selectedRecurringEvents.includes(recurringEvent.name)" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  
                  <!-- Event Title -->
                  <div class="flex-1 min-w-0">
                    <h4 class="font-semibold text-gray-900 dark:text-gray-100 text-sm leading-tight truncate group-hover/card:text-emerald-600 dark:group-hover/card:text-emerald-400 transition-colors">
                      {{ recurringEvent.name.trim() }}
                    </h4>
                  </div>
                </div>
                
                <!-- Event Details -->
                <div class="space-y-2 text-xs">
                  <div class="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                    <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                    </svg>
                    <span class="font-medium truncate">{{ formatDateRange(recurringEvent.events[0]) }}</span>
                  </div>
                  
                  <div v-if="recurringEvent.events[0].location" class="flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
                    <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                    </svg>
                    <span class="truncate">{{ recurringEvent.events[0].location }}</span>
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

// Overall selection state (all events, not just visible)
const areAllRecurringEventsSelected = computed(() => {
  if (props.allRecurringEvents.length === 0) return false
  const allNames = props.allRecurringEvents.map(recurringEvent => recurringEvent.name)
  return allNames.every(name => props.selectedRecurringEvents.includes(name))
})

const hasAnyRecurringEventsSelected = computed(() => {
  return props.selectedRecurringEvents.length > 0
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

// Genius day pattern detection for recurring events
const getRecurringEventDayPattern = (recurringEvent) => {
  if (!recurringEvent.events || recurringEvent.events.length === 0) return null
  
  // Analyze the days of the week for this recurring event
  const dayPattern = analyzeDayPattern(recurringEvent.events)
  
  if (dayPattern.type === 'consistent') {
    // Always the same day - show the day (translatable)
    const day = dayPattern.days[0]
    // Use a simple English format for now, can be made translatable later
    return `Every ${day}`
  } else if (dayPattern.type === 'weekdays') {
    return 'Weekdays'
  } else if (dayPattern.type === 'weekends') {
    return 'Weekends'
  } else if (dayPattern.type === 'multiple' && dayPattern.days.length <= 3) {
    // Multiple but consistent days - use abbreviated form for space
    const shortDays = dayPattern.days.map(day => day.substring(0, 3))
    return shortDays.join('/')
  }
  
  return null // Too complex or irregular pattern
}

function analyzeDayPattern(events) {
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
  const weekends = ['Saturday', 'Sunday']
  
  // Get unique days of the week
  const uniqueDays = [...new Set(events.map(event => {
    const date = new Date(event.start || event.dtstart)
    return dayNames[date.getDay()]
  }))]
  
  if (uniqueDays.length === 1) {
    return { type: 'consistent', days: uniqueDays }
  }
  
  // Check if it's all weekdays
  if (uniqueDays.every(day => weekdays.includes(day)) && uniqueDays.length >= 3) {
    return { type: 'weekdays', days: uniqueDays }
  }
  
  // Check if it's weekends
  if (uniqueDays.every(day => weekends.includes(day))) {
    return { type: 'weekends', days: uniqueDays }
  }
  
  // Multiple specific days
  if (uniqueDays.length <= 3) {
    return { type: 'multiple', days: uniqueDays.sort((a, b) => dayNames.indexOf(a) - dayNames.indexOf(b)) }
  }
  
  return { type: 'complex', days: uniqueDays }
}

// Enhanced date formatting for individual events with pattern awareness
function formatCompactEventDate(event, hasConsistentDay = false) {
  const date = new Date(event.start || event.dtstart)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const eventDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  
  // Calculate days difference
  const diffTime = eventDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  // Format time part
  const timeStr = date.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: false 
  })
  
  // Smart date formatting based on proximity and pattern
  if (diffDays === 0) {
    return `Today ${timeStr}`
  } else if (diffDays === 1) {
    return `Tomorrow ${timeStr}`
  } else if (diffDays === -1) {
    return `Yesterday ${timeStr}`
  } else if (diffDays > 0 && diffDays <= 7) {
    // For this week, show day if no consistent pattern, otherwise skip day
    const dayName = date.toLocaleDateString(undefined, { weekday: 'short' })
    return hasConsistentDay ? timeStr : `${dayName} ${timeStr}`
  } else if (diffDays >= -7 && diffDays < 0) {
    // For last week, show day if no consistent pattern, otherwise skip day
    const dayName = date.toLocaleDateString(undefined, { weekday: 'short' })
    return hasConsistentDay ? timeStr : `${dayName} ${timeStr}`
  } else {
    // For dates further away, always show month/day (day pattern is shown in card header)
    const monthDay = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    const currentYear = now.getFullYear()
    const eventYear = date.getFullYear()
    
    if (eventYear !== currentYear) {
      return `${monthDay} ${eventYear} ${timeStr}`
    } else {
      return `${monthDay} ${timeStr}`
    }
  }
}

</script>

<style scoped>
.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.touch-manipulation {
  touch-action: manipulation;
}
</style>