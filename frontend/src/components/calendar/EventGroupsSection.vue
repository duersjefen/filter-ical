<template>
  <div v-if="hasGroups" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4">
    <!-- Header -->
    <div class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-6 py-4 border-b">
      <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">🏷️ Event Groups</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        {{ selectedCount > 0
          ? getSelectedEventTypesText()
          : 'Subscribe to groups or select specific event types' }}
      </p>
    </div>

    <div class="p-6">
      <!-- Enhanced Control Bar -->
      <div class="flex justify-between items-center mb-6">
        <!-- Left Side: Action Buttons -->
        <div class="flex space-x-3">
          <button
            @click="clearSelections"
            class="px-4 py-2 text-sm border border-blue-300 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors font-medium text-blue-600 dark:text-blue-400"
            :disabled="selectedCount === 0"
            :class="selectedCount === 0 ? 'opacity-50 cursor-not-allowed' : ''"
          >
            Clear All
          </button>
          <button
            @click="subscribeToAllGroups"
            class="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            📁 Subscribe to All Groups
          </button>
          <button
            v-if="!allGroupsExpanded"
            @click="expandAllGroups"
            class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium text-gray-700 dark:text-gray-300"
          >
            📂 Expand All Groups
          </button>
          <button
            v-if="!allGroupsCollapsed"
            @click="collapseAllGroups"
            class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium text-gray-700 dark:text-gray-300"
          >
            📁 Collapse All Groups
          </button>
        </div>
        
        <!-- Right Side: Stats and Filter Toggle -->
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            {{ getTotalGroupsText() }}
          </div>
          
          <!-- Filter Mode Toggle -->
          <button
            @click="$emit('switch-filter-mode', filterMode === 'include' ? 'exclude' : 'include')"
            class="px-3 py-1 text-sm rounded-md transition-colors hover:scale-105 active:scale-95"
            :class="filterMode === 'include'
              ? 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-300'
              : 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-300'"
          >
            {{ filterMode === 'include' ? '✅ Include' : '❌ Exclude' }}
          </button>
        </div>
      </div>

      <!-- Groups Grid - Including Virtual Groups -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <!-- Regular Groups -->
        <div
          v-for="group in Object.values(groups || {})"
          :key="group.id"
          class="border rounded-lg transition-all duration-200 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700"
        >
          <!-- Group Header (Clickable to expand/collapse) -->
          <div class="p-4 cursor-pointer" @click="toggleExpansion(group.id)">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ group.name }}</h4>
                <div
                  class="w-3 h-3 rounded-full opacity-60"
                  :style="{ backgroundColor: group.color }"
                ></div>
                <!-- Expand/Collapse indicator -->
                <div class="text-gray-400 dark:text-gray-500">
                  <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-180': isExpanded(group.id) }" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ getTotalEventCount(group) }} events • {{ getGroupEventTypeCount(group) }} types
              </span>
            </div>
            
            <!-- Description -->
            <p v-if="group.description" class="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {{ group.description }}
            </p>
          </div>

          <!-- Dual Action Buttons -->
          <div class="px-4 pb-4">
            <div class="flex space-x-2">
              <!-- Subscribe to Group Button -->
              <button
                @click.stop="toggleGroupSubscription(group.id)"
                class="flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2"
                :class="isGroupSubscribed(group.id)
                  ? 'bg-green-500 hover:bg-green-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
              >
                <span>📁</span>
                <span>{{ isGroupSubscribed(group.id) ? 'Subscribed' : 'Subscribe' }}</span>
              </button>
              
              <!-- Select All Current Button -->
              <button
                @click.stop="selectAllCurrentInGroup(group.id)"
                class="flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2"
                :class="areAllEventTypesSelected(group.id)
                  ? 'bg-blue-500 hover:bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
              >
                <span>📋</span>
                <span>{{ areAllEventTypesSelected(group.id) ? 'All Selected' : 'Select All' }}</span>
              </button>
            </div>
          </div>

          <!-- Expandable Event Types Section -->
          <div v-if="isExpanded(group.id)" class="border-t border-gray-200 dark:border-gray-600 bg-gray-50/30 dark:bg-gray-800/30">
            <!-- Event Types List -->
            <div v-if="group.event_types && Object.keys(group.event_types).length > 0" class="p-4 space-y-2">
              <h5 class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3 uppercase tracking-wide">Event Types</h5>
              <div class="space-y-2">
                <div
                  v-for="(eventTypeData, eventTypeName) in group.event_types"
                  :key="eventTypeName"
                  class="bg-white dark:bg-gray-700 rounded-lg border transition-colors"
                  :class="isEventTypeSelected(eventTypeName)
                    ? 'bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-600'
                    : 'border-gray-200 dark:border-gray-600'"
                >
                  <!-- Event Type Header -->
                  <div 
                    class="flex items-center justify-between p-3 cursor-pointer transition-colors"
                    :class="isEventTypeSelected(eventTypeName)
                      ? 'text-green-800 dark:text-green-200'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'"
                    @click="handleEventTypeToggle(eventTypeName)"
                  >
                    <div class="flex-1 flex items-center">
                      <div class="mr-3">
                        <div class="font-medium">{{ eventTypeName }}</div>
                        <div class="text-sm opacity-75">{{ eventTypeData.count || 0 }} events</div>
                      </div>
                      
                      <!-- Expand Individual Events Button -->
                      <button
                        v-if="eventTypeData.events && eventTypeData.events.length > 0"
                        @click.stop="toggleEventTypeExpansion(eventTypeName)"
                        class="ml-auto mr-3 p-1 rounded hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
                        :title="isEventTypeExpanded(eventTypeName) ? 'Hide events' : 'Show individual events'"
                      >
                        <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-180': isEventTypeExpanded(eventTypeName) }" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                    
                    <!-- Event Type Selection Checkbox -->
                    <div
                      class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0"
                      :class="isEventTypeSelected(eventTypeName)
                        ? 'bg-green-500 border-green-500 text-white'
                        : 'border-gray-300 dark:border-gray-600'"
                    >
                      <span v-if="isEventTypeSelected(eventTypeName)" class="text-xs">✓</span>
                    </div>
                  </div>
                  
                  <!-- Individual Events List -->
                  <div v-if="isEventTypeExpanded(eventTypeName) && eventTypeData.events && eventTypeData.events.length > 0" class="border-t border-gray-200 dark:border-gray-600 bg-gray-25 dark:bg-gray-800">
                    <div class="p-3 space-y-1">
                      <div
                        v-for="event in eventTypeData.events"
                        :key="event.id"
                        class="flex items-center justify-between p-2 text-sm bg-white dark:bg-gray-700 rounded border border-gray-100 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-650 transition-colors"
                      >
                        <div class="flex-1">
                          <div class="font-medium text-gray-900 dark:text-gray-100">{{ event.title }}</div>
                          <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <span>{{ formatEventTime(event.start, event.end) }}</span>
                            <span v-if="event.location" class="ml-2">📍 {{ event.location }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Virtual Groups integrated into main grid -->
        <!-- Recurring Events Group for ungrouped recurring event types -->
        <div
          v-if="recurringActivitiesGroup"
          :key="recurringActivitiesGroup.id"
          class="border rounded-lg transition-all duration-200 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700"
        >
          <!-- Group Header -->
          <div class="p-4 cursor-pointer" @click="toggleExpansion(recurringActivitiesGroup.id)">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <h4 class="text-lg font-semibold text-orange-900 dark:text-orange-100">{{ recurringActivitiesGroup.name }}</h4>
                <div class="w-3 h-3 rounded-full bg-orange-500 opacity-60"></div>
                <!-- Expand/Collapse indicator -->
                <div class="text-gray-400 dark:text-gray-500">
                  <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-180': isExpanded(recurringActivitiesGroup.id) }" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ getTotalEventCount(recurringActivitiesGroup) }} events • {{ getGroupEventTypeCount(recurringActivitiesGroup) }} types
              </span>
            </div>
            
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {{ recurringActivitiesGroup.description }}
            </p>
          </div>

          <!-- Dual Action Buttons -->
          <div class="px-4 pb-4">
            <div class="flex space-x-2">
              <!-- Subscribe to Group Button -->
              <button
                @click.stop="toggleGroupSubscription(recurringActivitiesGroup.id)"
                class="flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2"
                :class="isGroupSubscribed(recurringActivitiesGroup.id)
                  ? 'bg-green-500 hover:bg-green-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
              >
                <span>📁</span>
                <span>{{ isGroupSubscribed(recurringActivitiesGroup.id) ? 'Subscribed' : 'Subscribe' }}</span>
              </button>
              
              <!-- Select All Current Button -->
              <button
                @click.stop="selectAllCurrentInGroup(recurringActivitiesGroup.id)"
                class="flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2"
                :class="areAllEventTypesSelected(recurringActivitiesGroup.id)
                  ? 'bg-blue-500 hover:bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
              >
                <span>📋</span>
                <span>{{ areAllEventTypesSelected(recurringActivitiesGroup.id) ? 'All Selected' : 'Select All' }}</span>
              </button>
            </div>
          </div>

          <!-- Expandable Event Types Section -->
          <div v-if="isExpanded(recurringActivitiesGroup.id)" class="border-t border-gray-200 dark:border-gray-600 bg-gray-50/30 dark:bg-gray-800/30">
            <div v-if="recurringActivitiesGroup.event_types && Object.keys(recurringActivitiesGroup.event_types).length > 0" class="p-4 space-y-2">
              <h5 class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3 uppercase tracking-wide">Recurring Event Types</h5>
              <div class="space-y-2">
                <div
                  v-for="(eventTypeData, eventTypeName) in recurringActivitiesGroup.event_types"
                  :key="eventTypeName"
                  class="bg-white dark:bg-gray-700 rounded-lg border transition-colors"
                  :class="isEventTypeSelected(eventTypeName)
                    ? 'bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-600'
                    : 'border-gray-200 dark:border-gray-600'"
                >
                  <!-- Event Type Header -->
                  <div 
                    class="flex items-center justify-between p-3 cursor-pointer transition-colors"
                    :class="isEventTypeSelected(eventTypeName)
                      ? 'text-green-800 dark:text-green-200'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'"
                    @click="handleEventTypeToggle(eventTypeName)"
                  >
                    <div class="flex-1 flex items-center">
                      <div class="mr-3">
                        <div class="font-medium">{{ eventTypeName }}</div>
                        <div class="text-sm opacity-75">{{ eventTypeData.count || 0 }} events</div>
                      </div>
                      
                      <!-- Expand Individual Events Button -->
                      <button
                        v-if="eventTypeData.events && eventTypeData.events.length > 0"
                        @click.stop="toggleEventTypeExpansion(eventTypeName)"
                        class="ml-auto mr-3 p-1 rounded hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
                        :title="isEventTypeExpanded(eventTypeName) ? 'Hide events' : 'Show individual events'"
                      >
                        <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-180': isEventTypeExpanded(eventTypeName) }" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                    
                    <!-- Event Type Selection Checkbox -->
                    <div
                      class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0"
                      :class="isEventTypeSelected(eventTypeName)
                        ? 'bg-green-500 border-green-500 text-white'
                        : 'border-gray-300 dark:border-gray-600'"
                    >
                      <span v-if="isEventTypeSelected(eventTypeName)" class="text-xs">✓</span>
                    </div>
                  </div>
                  
                  <!-- Individual Events List -->
                  <div v-if="isEventTypeExpanded(eventTypeName) && eventTypeData.events && eventTypeData.events.length > 0" class="border-t border-gray-200 dark:border-gray-600 bg-gray-25 dark:bg-gray-800">
                    <div class="p-3 space-y-1">
                      <div
                        v-for="event in eventTypeData.events"
                        :key="event.id"
                        class="flex items-center justify-between p-2 text-sm bg-white dark:bg-gray-700 rounded border border-gray-100 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-650 transition-colors"
                      >
                        <div class="flex-1">
                          <div class="font-medium text-gray-900 dark:text-gray-100">{{ event.title }}</div>
                          <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <span>{{ formatEventTime(event.start, event.end) }}</span>
                            <span v-if="event.location" class="ml-2">📍 {{ event.location }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Unique Events Group for ungrouped unique event types -->
        <div
          v-if="uniqueActivitiesGroup"
          :key="uniqueActivitiesGroup.id"
          class="border rounded-lg transition-all duration-200 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700"
        >
          <!-- Group Header -->
          <div class="p-4 cursor-pointer" @click="toggleExpansion(uniqueActivitiesGroup.id)">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <h4 class="text-lg font-semibold text-blue-900 dark:text-blue-100">{{ uniqueActivitiesGroup.name }}</h4>
                <div class="w-3 h-3 rounded-full bg-blue-500 opacity-60"></div>
                <!-- Expand/Collapse indicator -->
                <div class="text-gray-400 dark:text-gray-500">
                  <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-180': isExpanded(uniqueActivitiesGroup.id) }" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ getTotalEventCount(uniqueActivitiesGroup) }} events • {{ getGroupEventTypeCount(uniqueActivitiesGroup) }} types
              </span>
            </div>
            
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {{ uniqueActivitiesGroup.description }}
            </p>
          </div>

          <!-- Dual Action Buttons -->
          <div class="px-4 pb-4">
            <div class="flex space-x-2">
              <!-- Subscribe to Group Button -->
              <button
                @click.stop="toggleGroupSubscription(uniqueActivitiesGroup.id)"
                class="flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2"
                :class="isGroupSubscribed(uniqueActivitiesGroup.id)
                  ? 'bg-green-500 hover:bg-green-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
              >
                <span>📁</span>
                <span>{{ isGroupSubscribed(uniqueActivitiesGroup.id) ? 'Subscribed' : 'Subscribe' }}</span>
              </button>
              
              <!-- Select All Current Button -->
              <button
                @click.stop="selectAllCurrentInGroup(uniqueActivitiesGroup.id)"
                class="flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2"
                :class="areAllEventTypesSelected(uniqueActivitiesGroup.id)
                  ? 'bg-blue-500 hover:bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
              >
                <span>📋</span>
                <span>{{ areAllEventTypesSelected(uniqueActivitiesGroup.id) ? 'All Selected' : 'Select All' }}</span>
              </button>
            </div>
          </div>

          <!-- Expandable Event Types Section -->
          <div v-if="isExpanded(uniqueActivitiesGroup.id)" class="border-t border-gray-200 dark:border-gray-600 bg-gray-50/30 dark:bg-gray-800/30">
            <div v-if="uniqueActivitiesGroup.event_types && Object.keys(uniqueActivitiesGroup.event_types).length > 0" class="p-4 space-y-2">
              <h5 class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3 uppercase tracking-wide">Unique Event Types</h5>
              <div class="space-y-2">
                <div
                  v-for="(eventTypeData, eventTypeName) in uniqueActivitiesGroup.event_types"
                  :key="eventTypeName"
                  class="bg-white dark:bg-gray-700 rounded-lg border transition-colors"
                  :class="isEventTypeSelected(eventTypeName)
                    ? 'bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-600'
                    : 'border-gray-200 dark:border-gray-600'"
                >
                  <!-- Event Type Header -->
                  <div 
                    class="flex items-center justify-between p-3 cursor-pointer transition-colors"
                    :class="isEventTypeSelected(eventTypeName)
                      ? 'text-green-800 dark:text-green-200'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'"
                    @click="handleEventTypeToggle(eventTypeName)"
                  >
                    <div class="flex-1 flex items-center">
                      <div class="mr-3">
                        <div class="font-medium">{{ eventTypeName }}</div>
                        <div class="text-sm opacity-75">{{ eventTypeData.count || 0 }} events</div>
                      </div>
                      
                      <!-- Expand Individual Events Button -->
                      <button
                        v-if="eventTypeData.events && eventTypeData.events.length > 0"
                        @click.stop="toggleEventTypeExpansion(eventTypeName)"
                        class="ml-auto mr-3 p-1 rounded hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
                        :title="isEventTypeExpanded(eventTypeName) ? 'Hide events' : 'Show individual events'"
                      >
                        <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-180': isEventTypeExpanded(eventTypeName) }" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                    
                    <!-- Event Type Selection Checkbox -->
                    <div
                      class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0"
                      :class="isEventTypeSelected(eventTypeName)
                        ? 'bg-green-500 border-green-500 text-white'
                        : 'border-gray-300 dark:border-gray-600'"
                    >
                      <span v-if="isEventTypeSelected(eventTypeName)" class="text-xs">✓</span>
                    </div>
                  </div>
                  
                  <!-- Individual Events List -->
                  <div v-if="isEventTypeExpanded(eventTypeName) && eventTypeData.events && eventTypeData.events.length > 0" class="border-t border-gray-200 dark:border-gray-600 bg-gray-25 dark:bg-gray-800">
                    <div class="p-3 space-y-1">
                      <div
                        v-for="event in eventTypeData.events"
                        :key="event.id"
                        class="flex items-center justify-between p-2 text-sm bg-white dark:bg-gray-700 rounded border border-gray-100 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-650 transition-colors"
                      >
                        <div class="flex-1">
                          <div class="font-medium text-gray-900 dark:text-gray-100">{{ event.title }}</div>
                          <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <span>{{ formatEventTime(event.start, event.end) }}</span>
                            <span v-if="event.location" class="ml-2">📍 {{ event.location }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
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
import { ref, computed, watch } from 'vue'
import { useGlobalEventTypeSelection } from '../../composables/useGlobalEventTypeSelection'

const props = defineProps({
  hasGroups: { type: Boolean, default: false },
  groups: { type: Object, default: () => ({}) },
  filterMode: { type: String, default: 'include' },
  ungroupedEventTypes: { type: Array, default: () => [] },
  ungroupedRecurringEventTypes: { type: Array, default: () => [] },
  ungroupedUniqueEventTypes: { type: Array, default: () => [] }
})

const emit = defineEmits([
  'selection-changed',
  'switch-filter-mode'
])

// Use global event type selection system
const {
  selectedEventTypes,
  selectedCount: eventTypeSelectedCount,
  totalCount,
  isEventTypeSelected,
  toggleEventType,
  clearAllSelections: clearEventTypeSelections,
  selectAllEventTypes,
  updateRegistry,
  getSelectionSummaryText,
  isGroupPartiallySelected,
  isGroupFullySelected,
  toggleGroupSelection
} = useGlobalEventTypeSelection()

// Local state for group expansion and subscriptions
const expandedGroups = ref(new Set())

// Local state for event type expansion (3rd level)
const expandedEventTypes = ref(new Set())

// Group expansion methods
const isExpanded = (groupId) => {
  return expandedGroups.value.has(groupId)
}

const toggleExpansion = (groupId) => {
  toggleGroupExpansion(groupId)
}

const toggleGroupExpansion = (groupId) => {
  const newExpanded = new Set(expandedGroups.value)
  if (newExpanded.has(groupId)) {
    newExpanded.delete(groupId)
  } else {
    newExpanded.add(groupId)
  }
  expandedGroups.value = newExpanded
}

// Local state for group subscriptions (separate from event type selection)
const subscribedGroups = ref(new Set())

// Create virtual groups for recurring and unique ungrouped event types
const recurringActivitiesGroup = computed(() => {
  if (!props.ungroupedRecurringEventTypes || props.ungroupedRecurringEventTypes.length === 0) {
    return null
  }
  
  // Transform ungrouped recurring event types into event_types format
  const eventTypes = {}
  props.ungroupedRecurringEventTypes.forEach(eventType => {
    eventTypes[eventType.name || eventType] = {
      name: eventType.name || eventType,
      count: eventType.count || 0,
      events: eventType.events || []
    }
  })
  
  return {
    id: 'virtual_recurring',
    name: '🔄 Recurring Events',
    description: 'Events that repeat on a schedule (unassigned to groups)',
    color: '#f97316', // orange-500
    event_types: eventTypes
  }
})

const uniqueActivitiesGroup = computed(() => {
  if (!props.ungroupedUniqueEventTypes || props.ungroupedUniqueEventTypes.length === 0) {
    return null
  }
  
  // Transform ungrouped unique event types into event_types format
  const eventTypes = {}
  props.ungroupedUniqueEventTypes.forEach(eventType => {
    eventTypes[eventType.name || eventType] = {
      name: eventType.name || eventType,
      count: eventType.count || 0,
      events: eventType.events || []
    }
  })
  
  return {
    id: 'virtual_unique',
    name: '📅 Unique Events', 
    description: 'One-time events (unassigned to groups)',
    color: '#3b82f6', // blue-500
    event_types: eventTypes
  }
})

// Initialize global registry when groups data changes
watch([
  () => props.groups,
  () => props.ungroupedRecurringEventTypes,
  () => props.ungroupedUniqueEventTypes
], () => {
  // Build virtual groups first
  const virtualGroups = {}
  if (recurringActivitiesGroup.value) {
    virtualGroups[recurringActivitiesGroup.value.id] = recurringActivitiesGroup.value
  }
  if (uniqueActivitiesGroup.value) {
    virtualGroups[uniqueActivitiesGroup.value.id] = uniqueActivitiesGroup.value
  }
  
  // Update the global registry with both regular and virtual groups
  updateRegistry(props.groups || {}, virtualGroups)
}, { immediate: true })

// Computed properties
const selectedCount = computed(() => {
  return eventTypeSelectedCount.value + subscribedGroups.value.size
})

// Group subscription methods
const isGroupSubscribed = (groupId) => {
  return subscribedGroups.value.has(groupId)
}

const toggleGroupSubscription = (groupId) => {
  const newSubscribed = new Set(subscribedGroups.value)
  const isCurrentlySubscribed = newSubscribed.has(groupId)
  
  if (isCurrentlySubscribed) {
    // Unsubscribing from group
    newSubscribed.delete(groupId)
    
    // Smart logic: If all events are currently selected, unselect all events
    const totalEventTypes = totalCount.value // Use global count (accurate unique count)
    const selectedEventTypes = eventTypeSelectedCount.value
    if (selectedEventTypes > 0 && selectedEventTypes === totalEventTypes) {
      // All events are selected, so unselect all
      clearEventTypeSelections()
    }
  } else {
    // Subscribing to group
    newSubscribed.add(groupId)
    
    // Smart logic: If no events are currently selected, clear any existing selections
    const selectedEventTypes = eventTypeSelectedCount.value
    if (selectedEventTypes === 0) {
      // No events selected, ensure clean state by clearing any existing selections
      clearEventTypeSelections()
    }
  }
  
  subscribedGroups.value = newSubscribed
  emitSelectionChange()
}

// Event type selection methods
// Event type selection check now uses global system
const isEventTypeSelectedLocal = (eventTypeName) => {
  return isEventTypeSelected(eventTypeName) // Uses global system
}

// Event type selection now uses global system for cross-group synchronization
const handleEventTypeToggle = (eventTypeName) => {
  toggleEventType(eventTypeName) // This uses the global system
  emitSelectionChange()
}

// Enhanced group selection functions to handle virtual groups
const areAllEventTypesSelected = (groupId) => {
  let group
  if (groupId === 'virtual_recurring') {
    group = recurringActivitiesGroup.value
  } else if (groupId === 'virtual_unique') {
    group = uniqueActivitiesGroup.value
  } else {
    group = props.groups[groupId]
  }
  
  if (!group?.event_types) return false
  
  const eventTypes = Object.keys(group.event_types)
  return eventTypes.length > 0 && eventTypes.every(eventType => 
    isEventTypeSelected(eventType)
  )
}

const selectAllCurrentInGroup = (groupId) => {
  let group
  if (groupId === 'virtual_recurring') {
    group = recurringActivitiesGroup.value
  } else if (groupId === 'virtual_unique') {
    group = uniqueActivitiesGroup.value
  } else {
    group = props.groups[groupId]
  }
  
  if (!group?.event_types) return
  
  const eventTypes = Object.keys(group.event_types)
  const allSelected = isGroupFullySelected(groupId, { [groupId]: group })
  
  eventTypes.forEach(eventTypeName => {
    const isCurrentlySelected = isEventTypeSelected(eventTypeName)
    if (allSelected && isCurrentlySelected) {
      // Deselect this event type
      toggleEventType(eventTypeName)
    } else if (!allSelected && !isCurrentlySelected) {
      // Select this event type
      toggleEventType(eventTypeName)
    }
  })
  
  emitSelectionChange()
}

// Enhanced subscribeToAllGroups to include virtual groups
const subscribeToAllGroups = () => {
  const allGroupIds = Object.keys(props.groups || {})
  if (recurringActivitiesGroup.value) allGroupIds.push(recurringActivitiesGroup.value.id)
  if (uniqueActivitiesGroup.value) allGroupIds.push(uniqueActivitiesGroup.value.id)
  subscribedGroups.value = new Set(allGroupIds)
  emitSelectionChange()
}

// Clear all selections
const clearSelections = () => {
  clearEventTypeSelections()
  subscribedGroups.value = new Set()
  emitSelectionChange()
}

// Helper methods
const getTotalEventCount = (group) => {
  if (!group?.event_types) return 0
  
  return Object.values(group.event_types).reduce((sum, eventType) => 
    sum + (eventType.count || 0), 0
  )
}

const getGroupEventTypeCount = (group) => {
  if (!group?.event_types) return 0
  return Object.keys(group.event_types).length
}

// Header text functions
const getTotalGroupsText = () => {
  const totalGroups = Object.keys(props.groups || {}).length + 
    (recurringActivitiesGroup.value ? 1 : 0) + 
    (uniqueActivitiesGroup.value ? 1 : 0)
  const selectedGroups = subscribedGroups.value.size
  return `${totalGroups} groups • ${selectedGroups} selected`
}

const getSelectedEventTypesText = () => {
  // Use global counting system for accurate unique event type counts
  return getSelectionSummaryText()
}

const getTotalEventTypesCount = () => {
  let count = 0
  
  // Count from regular groups
  Object.values(props.groups || {}).forEach(group => {
    if (group.event_types) {
      count += Object.keys(group.event_types).length
    }
  })
  
  // Count from virtual groups
  if (recurringActivitiesGroup.value?.event_types) {
    count += Object.keys(recurringActivitiesGroup.value.event_types).length
  }
  if (uniqueActivitiesGroup.value?.event_types) {
    count += Object.keys(uniqueActivitiesGroup.value.event_types).length
  }
  
  return count
}

// Event type expansion functions (3rd level)
const isEventTypeExpanded = (eventTypeName) => {
  return expandedEventTypes.value.has(eventTypeName)
}

const toggleEventTypeExpansion = (eventTypeName) => {
  const newExpanded = new Set(expandedEventTypes.value)
  if (newExpanded.has(eventTypeName)) {
    newExpanded.delete(eventTypeName)
  } else {
    newExpanded.add(eventTypeName)
  }
  expandedEventTypes.value = newExpanded
}

// Event time formatting
const formatEventTime = (start, end) => {
  if (!start) return ''
  
  try {
    const startDate = new Date(start)
    const endDate = end ? new Date(end) : null
    
    const startTime = startDate.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    })
    
    if (endDate) {
      const endTime = endDate.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      })
      return `${startTime} - ${endTime}`
    }
    
    return startTime
  } catch (error) {
    return start
  }
}

// Expand All Groups functionality
const getAllGroupIds = () => {
  const ids = Object.keys(props.groups || {})
  if (recurringActivitiesGroup.value) ids.push(recurringActivitiesGroup.value.id)
  if (uniqueActivitiesGroup.value) ids.push(uniqueActivitiesGroup.value.id)
  return ids
}

const allGroupsExpanded = computed(() => {
  const allIds = getAllGroupIds()
  if (allIds.length === 0) return true
  return allIds.every(groupId => expandedGroups.value.has(groupId))
})

const expandAllGroups = () => {
  const allIds = getAllGroupIds()
  const newExpanded = new Set(expandedGroups.value)
  allIds.forEach(groupId => newExpanded.add(groupId))
  // We need to update the expandedGroups from useGroupSelection
  allIds.forEach(groupId => {
    if (!expandedGroups.value.has(groupId)) {
      toggleGroupExpansion(groupId)
    }
  })
}

const allGroupsCollapsed = computed(() => {
  const allIds = getAllGroupIds()
  if (allIds.length === 0) return true
  return allIds.every(groupId => !expandedGroups.value.has(groupId))
})

const collapseAllGroups = () => {
  const allIds = getAllGroupIds()
  // We need to update the expandedGroups from useGroupSelection
  allIds.forEach(groupId => {
    if (expandedGroups.value.has(groupId)) {
      toggleGroupExpansion(groupId)
    }
  })
}

// Emit selection changes to parent
const emitSelectionChange = () => {
  const selectionData = {
    selectedEventTypes: selectedEventTypes.value,
    subscribedGroups: Array.from(subscribedGroups.value),
    selectionCount: eventTypeSelectedCount.value,
    totalCount: totalCount.value
  }
  emit('selection-changed', selectionData)
}

// Watch for selection changes to emit to parent
watch([selectedEventTypes, subscribedGroups], () => {
  emitSelectionChange()
}, { deep: true })
</script>