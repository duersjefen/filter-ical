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
              📂 <span class="bg-gradient-to-r from-gray-700 to-gray-600 dark:from-gray-300 dark:to-gray-200 bg-clip-text text-transparent">{{ $t('calendar.recurringEvents') }}</span>
            </h3>
          </div>
          <!-- Mobile Switch Button - Enhanced Modern Design -->
          <button
            v-if="hasGroups"
            @click="$emit('switch-to-groups')"
            class="group relative px-4 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2 transform hover:scale-105 active:scale-95"
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
              📂 <span class="bg-gradient-to-r from-gray-700 to-gray-600 dark:from-gray-300 dark:to-gray-200 bg-clip-text text-transparent">{{ $t('calendar.recurringEvents') }}</span>
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
          class="group relative px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-3 ml-4 transform hover:scale-105 active:scale-95"
          :title="$t('status.switchToGroupsView')"
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
              {{ $t('ui.switchToGroupsView') }}
            </div>
            <div class="text-xs text-blue-100">
              {{ $t('ui.browseByOrganizedGroups') }}
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
                class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 border-2 border-blue-600 hover:border-blue-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-blue-500/50 min-h-[44px]"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                {{ $t('controls.selectAll') }}
              </button>
              
              <button 
                v-if="hasAnyRecurringEventsSelected"
                @click="$emit('clear-all')" 
                class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 border-2 border-gray-600 hover:border-gray-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-gray-500/50 min-h-[44px]"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                {{ $t('controls.deselectAll') }}
              </button>
            </template>
            
            <!-- When searching: Show contextual buttons -->
            <template v-else>
              <button 
                v-if="!areAllVisibleSelected && filteredMainRecurringEvents.length > 0"
                @click="selectAllVisible"
                class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 border-2 border-blue-600 hover:border-blue-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-blue-500/50 min-h-[44px]"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                {{ $t('controls.selectVisible', { count: filteredMainRecurringEvents.length }) }}
              </button>
              
              <button 
                v-if="hasAnyVisibleSelected"
                @click="clearAllVisible"
                class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 border-2 border-gray-600 hover:border-gray-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-gray-500/50 min-h-[44px]"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                {{ $t('recurringEvents.deselectVisible') }}
              </button>
            </template>
            
            <!-- Show Selected Only Toggle - Moved to main actions -->
            <button
              v-if="selectedRecurringEvents.length > 0 && !searchTerm.trim()"
              @click="$emit('toggle-selected-only')"
              class="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] touch-manipulation"
              :class="showSelectedOnly 
                ? 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border-2 border-emerald-200 hover:border-emerald-300 shadow-sm dark:bg-emerald-900/20 dark:hover:bg-emerald-900/30 dark:text-emerald-300 dark:border-emerald-700' 
                : 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-2 border-blue-200 hover:border-blue-300 shadow-sm dark:bg-blue-900/20 dark:hover:bg-blue-900/30 dark:text-blue-300 dark:border-blue-700'"
            >
              <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-180': showSelectedOnly }" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
              </svg>
              <span class="hidden sm:inline">{{ showSelectedOnly ? $t('viewControls.showAll') : $t('viewControls.showSelectedOnly') }}</span>
              <span class="sm:hidden">{{ showSelectedOnly ? $t('status.showAll') : $t('status.showSelected') }}</span>
            </button>
          </div>
          
          <!-- View Controls -->
          <div class="flex justify-center sm:justify-end gap-3">
            <!-- Expand/Collapse Individual Events Controls -->
            <div v-if="hasAnyMainRecurringEvents && !searchTerm.trim()" class="flex gap-2">
              <button
                v-if="!allIndividualEventsExpanded"
                @click="expandAllIndividualEvents"
                class="inline-flex items-center justify-center gap-2 px-2 py-1 text-xs font-medium text-blue-600 bg-gradient-to-r from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 border border-transparent hover:border-blue-200 rounded-md opacity-75 hover:opacity-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30 dark:from-blue-900/20 dark:to-blue-800/40 dark:text-blue-300 dark:hover:from-blue-800/40 dark:hover:to-blue-900/60 dark:hover:text-blue-200"
                :title="$t('controls.expandAllIndividualEvents')"
              >
                <svg class="w-3 h-3 transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                {{ $t('controls.expandAll') }}
              </button>
              
              <button
                v-if="!allIndividualEventsCollapsed"
                @click="collapseAllIndividualEvents"
                class="inline-flex items-center justify-center gap-2 px-2 py-1 text-xs font-medium text-slate-500 bg-gradient-to-r from-slate-50 to-slate-100 hover:from-slate-100 hover:to-slate-200 border border-transparent hover:border-slate-300 rounded-md opacity-75 hover:opacity-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-slate-400/30 dark:from-gray-700 dark:to-gray-600 dark:text-gray-400 dark:hover:from-gray-600 dark:hover:to-gray-500 dark:hover:text-gray-300"
                :title="$t('controls.collapseAllIndividualEvents')"
              >
                <svg class="w-3 h-3 transition-transform duration-200 rotate-90" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                {{ $t('controls.collapseAll') }}
              </button>
            </div>
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
            <span class="font-medium">{{ filteredMainRecurringEvents.length }}</span> 
            events found for "<span class="font-medium text-gray-900 dark:text-gray-100">{{ searchTerm.trim() }}</span>"
          </span>
          <button 
            v-if="filteredMainRecurringEvents.length > 0"
            @click="selectAllVisible"
            class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium transition-colors"
          >
            {{ $t('controls.selectAllResults') }}
          </button>
        </div>
      </div>

      <!-- Enhanced Event Cards Grid with Drag Selection -->
      <div 
        class="relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3"
        @mousedown="startDragSelection"
        @mousemove="updateDragSelection"
        @mouseup="endDragSelection"
        @mouseleave="endDragSelection"
      >
        <!-- Drag Selection Overlay -->
        <div
          v-if="dragSelection.dragging"
          class="absolute pointer-events-none bg-gradient-to-br from-blue-300 to-blue-400 dark:from-blue-500 dark:to-blue-600 opacity-30 border-2 border-blue-500 dark:border-blue-400 rounded-lg shadow-lg backdrop-blur-sm"
          :style="{
            left: Math.min(dragSelection.startX, dragSelection.currentX) + 'px',
            top: Math.min(dragSelection.startY, dragSelection.currentY) + 'px',
            width: Math.abs(dragSelection.currentX - dragSelection.startX) + 'px',
            height: Math.abs(dragSelection.currentY - dragSelection.startY) + 'px',
            zIndex: 10
          }"
        >
          <div class="absolute inset-0 bg-white dark:bg-gray-900 opacity-10 rounded-lg"></div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 mb-4 items-start">
          <div 
            v-for="recurringEvent in filteredMainRecurringEvents" 
            :key="recurringEvent.name"
            :ref="el => { if (el) cardRefs[`main-${recurringEvent.name}`] = el }"
            class="relative border-2 rounded-lg transition-all duration-200 cursor-pointer group/item transform hover:scale-[1.01]"
            :class="selectedRecurringEvents.includes(recurringEvent.name)
              ? 'border-blue-400 bg-blue-50 dark:border-blue-500 dark:bg-blue-900/30 shadow-lg ring-2 ring-blue-200 dark:ring-blue-700/50 scale-[1.01]' 
              : 'border-gray-200 dark:border-gray-600 hover:border-blue-200 dark:hover:border-blue-600 bg-white dark:bg-gray-800 hover:bg-blue-25 dark:hover:bg-blue-950/10'"
            @click="handleCardClick(recurringEvent.name, $event)"
            :title="`Click to ${selectedRecurringEvents.includes(recurringEvent.name) ? 'deselect' : 'select'} ${recurringEvent.name} • Drag to select multiple`"
          >
            <!-- Selection Indicator Line -->
            <div 
              class="absolute top-0 left-0 right-0 h-1 transition-all duration-300"
              :class="selectedRecurringEvents.includes(recurringEvent.name) ? 'bg-blue-500' : 'bg-gray-200 dark:bg-gray-700'"
            ></div>
            
            <!-- Two-Row Event Header -->
            <div class="p-3 transition-colors relative">
              <!-- Selected Indicator Icon (top-right corner) -->
              <div 
                v-if="selectedRecurringEvents.includes(recurringEvent.name)"
                class="absolute top-2 right-2 w-5 h-5 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold shadow-sm z-10"
              >
                ✓
              </div>
              
              <!-- Row 1: Full-width Title -->
              <div class="mb-2 pr-6">
                <!-- Event Title with full space -->
                <div class="font-semibold text-gray-900 dark:text-gray-100 truncate transition-colors"
                     :class="selectedRecurringEvents.includes(recurringEvent.name)
                       ? 'text-blue-700 dark:text-blue-300' 
                       : 'group-hover/item:text-blue-600 dark:group-hover/item:text-blue-400'"
                >
                  {{ recurringEvent.name.trim() }}
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
                  :title="expandedRecurringEvents.has(recurringEvent.name) ? $t('messages.hideIndividualEvents') : $t('messages.showIndividualEvents')"
                >
                  <span class="text-xs font-medium group-hover/expand:text-blue-600 dark:group-hover/expand:text-blue-400 transition-colors">
                    {{ expandedRecurringEvents.has(recurringEvent.name) ? $t('domainAdmin.hide') : $t('domainAdmin.show') }}
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
                        <span v-if="event.is_recurring" class="text-blue-500" :title="$t('messages.recurringEvent')">🔄</span>
                        <!-- Title (only if different) -->
                        <span v-if="event.title && event.title !== recurringEvent.name" class="font-medium text-gray-800 dark:text-gray-200 truncate">
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
            {{ searchTerm.trim() ? $t('messages.noEventsFound') : $t('messages.noSelectedEventsVisible') }}
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
              class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 border-2 border-blue-600 hover:border-blue-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-blue-500/50 min-h-[44px]"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
              </svg>
              Clear search
            </button>
            <button 
              v-else
              @click="$emit('toggle-selected-only')"
              class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 border-2 border-blue-600 hover:border-blue-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-blue-500/50 min-h-[44px]"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
              </svg>
              Show all events
            </button>
          </div>
        </div>
      </div>

      <!-- Unique Events Section - Now a separate component -->
      <UniqueEventsSection
        :single-recurring-events="singleRecurringEvents"
        :selected-recurring-events="selectedRecurringEvents"
        :show-single-events="showSingleEvents"
        :show-selected-only="showSelectedOnly"
        :search-term="searchTerm"
        :format-date-range="formatDateRange"
        @toggle-recurring-event="$emit('toggle-recurring-event', $event)"
        @toggle-singles-visibility="$emit('toggle-singles-visibility')"
        @select-all-singles="$emit('select-all-singles')"
        @clear-all-singles="$emit('clear-all-singles')"
      />

      <!-- Bulk Groups Actions -->
      <div v-if="hasGroups" 
           class="border-t border-gray-200 dark:border-gray-600 pb-6 mt-6 pt-6">
        <div class="text-center">
          <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
            What to do with future Events?
          </h4>
          <div class="flex flex-col sm:flex-row gap-3 justify-center items-center">
            <!-- Enhanced Subscribe to All Groups -->
            <button
              @click="$emit('subscribe-all-groups')"
              class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 border-2 border-green-600 hover:border-green-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-green-500/50 min-h-[44px]"
            >
              <span>{{ $t('viewControls.subscribeToAllGroups') }}</span>
            </button>
            
            <!-- Enhanced Unsubscribe & Deselect All Groups -->
            <button
              @click="$emit('unsubscribe-all-groups')"
              class="inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 border-2 border-gray-600 hover:border-gray-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-gray-500/50 min-h-[44px]"
            >
              <span>{{ $t('viewControls.unsubscribeFromAllGroups') }}</span>
            </button>
          </div>
          
          <!-- Helper Text -->
          <p class="mt-4 text-xs text-gray-500 dark:text-gray-400 max-w-md mx-auto">
            💡 {{ $t('viewControls.fineGrainedControlText') }}
            <button 
              @click="$emit('switch-to-groups')"
              class="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 underline decoration-dotted underline-offset-2 hover:decoration-solid transition-all cursor-pointer"
            >
              {{ $t('viewControls.groupsView') }}
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { analyzeSmartRecurringPattern } from '@/utils/dateFormatting'
import UniqueEventsSection from './UniqueEventsSection.vue'

const { t } = useI18n()

// Drag selection state
const dragSelection = ref({
  dragging: false,
  startX: 0,
  startY: 0,
  currentX: 0,
  currentY: 0,
  initialSelection: [],
  containerRect: null
})

// Card refs for drag selection
const cardRefs = ref({})

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
  return filteredMainRecurringEvents.value.length > 0
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

// Individual events expansion state for main recurring events
const hasAnyMainRecurringEvents = computed(() => {
  return filteredMainRecurringEvents.value.length > 0
})

const allIndividualEventsExpanded = computed(() => {
  if (filteredMainRecurringEvents.value.length === 0) return false
  return filteredMainRecurringEvents.value.every(recurringEvent => 
    props.expandedRecurringEvents.has(recurringEvent.name)
  )
})

const allIndividualEventsCollapsed = computed(() => {
  if (filteredMainRecurringEvents.value.length === 0) return false
  return filteredMainRecurringEvents.value.every(recurringEvent => 
    !props.expandedRecurringEvents.has(recurringEvent.name)
  )
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
  
}

function clearAllVisible() {
  // Clear all visible main recurring events
  const visibleMainNames = filteredMainRecurringEvents.value.map(recurringEvent => recurringEvent.name)
  visibleMainNames.forEach(name => {
    if (props.selectedRecurringEvents.includes(name)) {
      emit('toggle-recurring-event', name)
    }
  })
  
}

// Methods for individual events expansion control
function expandAllIndividualEvents() {
  filteredMainRecurringEvents.value.forEach(recurringEvent => {
    if (!props.expandedRecurringEvents.has(recurringEvent.name)) {
      emit('toggle-expansion', recurringEvent.name)
    }
  })
}

function collapseAllIndividualEvents() {
  filteredMainRecurringEvents.value.forEach(recurringEvent => {
    if (props.expandedRecurringEvents.has(recurringEvent.name)) {
      emit('toggle-expansion', recurringEvent.name)
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
  'subscribe-all-groups',
  'unsubscribe-all-groups',
  'switch-to-groups',
  'toggle-recurring-events-section'
])


// Smart day pattern detection for recurring events with i18n support
const getRecurringEventDayPattern = (recurringEvent) => {
  if (!recurringEvent.events || recurringEvent.events.length === 0) return null
  
  // Use the new smart pattern analysis
  return analyzeSmartRecurringPattern(recurringEvent.events, t)
}


// Enhanced date formatting for individual events with pattern awareness and i18n support
function formatCompactEventDate(event, hasConsistentDay = false) {
  const date = new Date(event.start || event.dtstart)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const eventDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  
  // Calculate days difference
  const diffTime = eventDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  // Get current locale for proper formatting
  const locale = t('language.switch') === 'Sprache wechseln' ? 'de-DE' : 'en-US'
  
  // Format time part
  const timeStr = date.toLocaleTimeString(locale, { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: false 
  })
  
  // Smart date formatting based on proximity and pattern
  if (diffDays === 0) {
    return `${t('preview.today')} ${timeStr}`
  } else if (diffDays === 1) {
    return `${t('preview.tomorrow')} ${timeStr}`
  } else if (diffDays === -1) {
    return `${t('preview.yesterday')} ${timeStr}`
  } else if (diffDays > 0 && diffDays <= 14) {
    // For the next two weeks, show day name + date when needed for clarity
    const dayName = date.toLocaleDateString(locale, { weekday: 'short' })
    if (diffDays <= 7) {
      // This week - just show day name
      return `${dayName} ${timeStr}`
    } else {
      // Next week - show day name + date to distinguish from this week
      const monthDay = date.toLocaleDateString(locale, { month: 'short', day: 'numeric' })
      return `${dayName} ${monthDay} ${timeStr}`
    }
  } else if (diffDays >= -7 && diffDays < 0) {
    // For last week, show day name + date to distinguish from future events
    const dayName = date.toLocaleDateString(locale, { weekday: 'short' })
    const monthDay = date.toLocaleDateString(locale, { month: 'short', day: 'numeric' })
    return `${dayName} ${monthDay} ${timeStr}`
  } else {
    // For dates further away, always show month/day regardless of pattern
    const monthDay = date.toLocaleDateString(locale, { month: 'short', day: 'numeric' })
    const currentYear = now.getFullYear()
    const eventYear = date.getFullYear()
    
    if (eventYear !== currentYear) {
      return `${monthDay} ${eventYear} ${timeStr}`
    } else {
      return `${monthDay} ${timeStr}`
    }
  }
}

// Drag selection methods
const startDragSelection = (event) => {
  // Only start drag selection on left mouse button
  if (event.button !== 0) return
  
  const containerRect = event.currentTarget.getBoundingClientRect()
  dragSelection.value = {
    dragging: true,
    startX: event.clientX - containerRect.left,
    startY: event.clientY - containerRect.top,
    currentX: event.clientX - containerRect.left,
    currentY: event.clientY - containerRect.top,
    initialSelection: [...props.selectedRecurringEvents],
    containerRect: containerRect
  }
  
  event.preventDefault()
  event.stopPropagation()
}

const updateDragSelection = (event) => {
  if (!dragSelection.value.dragging) return
  
  // Use stored container rect for stable coordinates
  const containerRect = dragSelection.value.containerRect
  dragSelection.value.currentX = event.clientX - containerRect.left
  dragSelection.value.currentY = event.clientY - containerRect.top
  
  event.preventDefault()
  event.stopPropagation()
  
  // Calculate which cards intersect with selection rectangle
  const selectionRect = {
    left: Math.min(dragSelection.value.startX, dragSelection.value.currentX),
    top: Math.min(dragSelection.value.startY, dragSelection.value.currentY),
    right: Math.max(dragSelection.value.startX, dragSelection.value.currentX),
    bottom: Math.max(dragSelection.value.startY, dragSelection.value.currentY)
  }
  
  const newSelection = [...dragSelection.value.initialSelection]
  
  // Check main recurring events
  filteredMainRecurringEvents.value.forEach(recurringEvent => {
    const cardElement = cardRefs.value[`main-${recurringEvent.name}`]
    if (cardElement) {
      const cardRect = cardElement.getBoundingClientRect()
      const containerRect = cardElement.closest('.grid').getBoundingClientRect()
      
      const cardRelativeRect = {
        left: cardRect.left - containerRect.left,
        top: cardRect.top - containerRect.top,
        right: cardRect.right - containerRect.left,
        bottom: cardRect.bottom - containerRect.top
      }
      
      // Check if card intersects with selection rectangle
      const intersects = !(cardRelativeRect.right < selectionRect.left || 
                         cardRelativeRect.left > selectionRect.right || 
                         cardRelativeRect.bottom < selectionRect.top || 
                         cardRelativeRect.top > selectionRect.bottom)
      
      if (intersects) {
        if (!newSelection.includes(recurringEvent.name)) {
          newSelection.push(recurringEvent.name)
        }
      }
    }
  })
  
  
  // Emit selection updates
  const currentlySelected = props.selectedRecurringEvents
  const toDeselect = currentlySelected.filter(name => !newSelection.includes(name))
  const toSelect = newSelection.filter(name => !currentlySelected.includes(name))
  
  toDeselect.forEach(name => emit('toggle-recurring-event', name))
  toSelect.forEach(name => emit('toggle-recurring-event', name))
}

const endDragSelection = () => {
  if (!dragSelection.value.dragging) return
  
  // Check if this was just a click (minimal movement)
  const deltaX = Math.abs(dragSelection.value.currentX - dragSelection.value.startX)
  const deltaY = Math.abs(dragSelection.value.currentY - dragSelection.value.startY) 
  const wasClick = deltaX < 5 && deltaY < 5
  
  if (wasClick) {
    // Restore original selection for clicks - let normal click handler take over
    const currentlySelected = props.selectedRecurringEvents
    const originalSelection = dragSelection.value.initialSelection
    
    const toDeselect = currentlySelected.filter(name => !originalSelection.includes(name))
    const toSelect = originalSelection.filter(name => !currentlySelected.includes(name))
    
    toDeselect.forEach(name => emit('toggle-recurring-event', name))
    toSelect.forEach(name => emit('toggle-recurring-event', name))
  }
  
  // Reset drag state
  dragSelection.value.dragging = false
}

const handleCardClick = (recurringEventName, event) => {
  // If we're currently dragging, don't handle clicks
  if (dragSelection.value.dragging) {
    return
  }
  emit('toggle-recurring-event', recurringEventName)
}

// Global escape handler for drag selection cleanup
onMounted(() => {
  const handleEscape = (event) => {
    if (event.key === 'Escape' && dragSelection.value.dragging) {
      endDragSelection()
    }
  }
  
  // Global cleanup for drag state
  const handleBeforeUnload = () => {
    dragSelection.value.dragging = false
  }
  
  document.addEventListener('keydown', handleEscape)
  window.addEventListener('beforeunload', handleBeforeUnload)
  
  // Cleanup listeners on unmount
  onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
    window.removeEventListener('beforeunload', handleBeforeUnload)
    // Reset drag state if component unmounts during drag
    dragSelection.value.dragging = false
  })
})

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