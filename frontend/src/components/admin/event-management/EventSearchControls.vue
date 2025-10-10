<template>
  <div class="space-y-4">
    <!-- Selected-Only Mode Indicator -->
    <div
      v-if="showSelectedOnly"
      class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3 flex items-center justify-between"
    >
      <div class="flex items-center gap-3">
        <div class="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
          <span class="text-blue-600 dark:text-blue-400 text-xs font-bold">👁</span>
        </div>
        <div>
          <p class="text-sm font-medium text-blue-800 dark:text-blue-200">
            Showing only {{ selectedEvents.length }} selected event{{ selectedEvents.length > 1 ? 's' : '' }}
          </p>
          <p class="text-xs text-blue-600 dark:text-blue-400">
            Use filters above to return to normal view
          </p>
        </div>
      </div>
      <button
        @click="$emit('update:showSelectedOnly', false)"
        class="px-3 py-1 bg-blue-100 hover:bg-blue-200 dark:bg-blue-800 dark:hover:bg-blue-700 text-blue-800 dark:text-blue-200 rounded-md text-xs font-medium transition-colors"
      >
        {{ t('domainAdmin.showAllEvents') }}
      </button>
    </div>

    <!-- Desktop: Horizontal Layout | Mobile: Vertical Stacked Layout -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
      <!-- Search Bar -->
      <div class="flex-1 relative">
        <input
          :value="eventSearch"
          @input="$emit('update:eventSearch', $event.target.value)"
          type="text"
          :placeholder="activeGroupFilters.length > 0 ? $t('placeholders.searchInFilteredGroups') : $t('placeholders.searchEvents')"
          class="w-full px-4 py-3 sm:py-2 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 text-base sm:text-sm"
        />

        <!-- Search Clear Button -->
        <button
          v-if="eventSearch.trim()"
          @click="$emit('update:eventSearch', ''); $emit('update:showSelectedOnly', false)"
          class="absolute right-3 top-1/2 transform -translate-y-1/2 w-6 h-6 sm:w-5 sm:h-5 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          :title="t('domainAdmin.clearSearch')"
        >
          <span class="text-base sm:text-sm font-bold">×</span>
        </button>
      </div>

      <!-- Selection and Action Controls -->
      <div class="flex flex-col sm:flex-row gap-2 sm:gap-3">
        <!-- Main Selection Button with Event Counter -->
        <button
          @click="$emit('toggle-select-all')"
          class="flex items-center justify-center gap-2 px-4 py-3 sm:px-4 sm:py-2 text-base sm:text-sm font-medium rounded-lg transition-all duration-200 border min-h-[44px] sm:min-h-0"
          :class="[
            isAllEventsSelected
              ? 'bg-green-100 text-green-800 border-green-300 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-200 dark:border-green-700 dark:hover:bg-green-800/30'
              : isSomeEventsSelected
              ? 'bg-blue-100 text-blue-800 border-blue-300 hover:bg-blue-200 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-700 dark:hover:bg-blue-800/30'
              : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
          ]"
          :title="isAllEventsSelected ? `Deselect all ${filteredEvents.length} visible events` : `Select all ${filteredEvents.length} visible events`"
        >
          <div
            class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs transition-all flex-shrink-0"
            :class="isAllEventsSelected
              ? 'bg-green-500 border-green-500 text-white'
              : isSomeEventsSelected
              ? 'bg-blue-500 border-blue-500 text-white'
              : 'border-gray-400 bg-white dark:bg-gray-700 dark:border-gray-500'"
          >
            <span v-if="isAllEventsSelected">✓</span>
            <span v-else-if="isSomeEventsSelected">−</span>
          </div>
          <!-- Desktop: Include count in button -->
          <span v-if="isAllEventsSelected" class="hidden sm:inline">All {{ filteredEvents.length }} Selected</span>
          <span v-else-if="isSomeEventsSelected" class="hidden sm:inline">{{ selectedEvents.length }}/{{ filteredEvents.length }} Selected</span>
          <span v-else class="hidden sm:inline">Select {{ filteredEvents.length }} Visible</span>
          <!-- Mobile: Also include count -->
          <span v-if="isAllEventsSelected" class="sm:hidden">All {{ filteredEvents.length }} Selected</span>
          <span v-else-if="isSomeEventsSelected" class="sm:hidden">{{ selectedEvents.length }}/{{ filteredEvents.length }} Selected</span>
          <span v-else class="sm:hidden">Select {{ filteredEvents.length }} Visible</span>
        </button>

        <!-- Action Buttons -->
        <button
          @click="$emit('clear-selection')"
          :disabled="selectedEvents.length === 0"
          class="px-4 py-3 sm:px-3 sm:py-2 text-base sm:text-xs font-medium rounded-lg sm:rounded-md transition-all duration-200 border border-gray-300 text-gray-600 hover:bg-gray-100 hover:text-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] sm:min-h-0"
          :title="selectedEvents.length === 0 ? $t('domainAdmin.noEventsSelected') : $t('domainAdmin.clearSelection', { count: selectedEvents.length })"
        >
          {{ $t('domainAdmin.clearSelectionButton') }}
        </button>
        <button
          v-if="hasHiddenSelectedEvents || showSelectedOnly"
          @click="$emit('show-selected')"
          :disabled="selectedEvents.length === 0"
          :class="[
            'px-4 py-3 sm:px-3 sm:py-2 text-base sm:text-xs font-medium rounded-lg sm:rounded-md transition-all duration-200 border min-h-[44px] sm:min-h-0',
            hasHiddenSelectedEvents
              ? 'bg-amber-100 hover:bg-amber-200 border-amber-300 text-amber-800 dark:bg-amber-900/30 dark:hover:bg-amber-800/50 dark:border-amber-600 dark:text-amber-200'
              : 'bg-blue-100 hover:bg-blue-200 border-blue-300 text-blue-800 dark:bg-blue-900/30 dark:hover:bg-blue-800/50 dark:border-blue-600 dark:text-blue-200'
          ]"
          :title="hasHiddenSelectedEvents ? 'Some selected events are hidden by filters' : 'View only your selected events'"
        >
          <span class="mr-2 sm:mr-1">{{ hasHiddenSelectedEvents ? '⚠️' : '👁' }}</span>
          Show Only Selected
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'

export default {
  name: 'EventSearchControls',
  props: {
    eventSearch: { type: String, required: true },
    showSelectedOnly: { type: Boolean, required: true },
    selectedEvents: { type: Array, required: true },
    filteredEvents: { type: Array, required: true },
    activeGroupFilters: { type: Array, required: true },
    isAllEventsSelected: { type: Boolean, required: true },
    isSomeEventsSelected: { type: Boolean, required: true },
    hasHiddenSelectedEvents: { type: Boolean, required: true }
  },
  emits: [
    'update:eventSearch',
    'update:showSelectedOnly',
    'toggle-select-all',
    'clear-selection',
    'show-selected'
  ],
  setup() {
    const { t } = useI18n()
    return { t }
  }
}
</script>
