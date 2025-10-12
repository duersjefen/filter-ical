<template>
  <div v-if="filteredCalendars.length > 0 && !isUpdateMode" class="space-y-4">
    <div class="flex items-center justify-between">
      <h4 class="text-lg font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
        📋 {{ $t('filteredCalendar.yourFiltered') }}
        <span class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-sm font-semibold rounded-lg">
          {{ filteredCalendars.length }}
        </span>
      </h4>
    </div>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
      <FilteredCalendarCard
        v-for="calendar in filteredCalendars"
        :key="calendar.id"
        :calendar="calendar"
        :copy-success="copySuccessId === String(calendar.id)"
        :updating="updatingId === calendar.id"
        @copy-url="$emit('copy-url', calendar)"
        @update-filter="$emit('update-filter', calendar)"
        @delete="$emit('delete', calendar.id)"
        @save-name="(name) => $emit('save-name', { id: calendar.id, name })"
      />
    </div>
  </div>

  <!-- Empty State -->
  <div v-else-if="filteredCalendars.length === 0 && showEmptyState" class="text-center py-8">
    <div class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-600">
      <div class="text-6xl mb-4">📅</div>
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
        {{ $t('filteredCalendar.noFiltered') }}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 max-w-md mx-auto leading-relaxed">
        {{ $t('filteredCalendar.getStarted') }}
      </p>
      <div class="mt-6 flex items-center justify-center gap-2 text-xs text-gray-500 dark:text-gray-400">
        <span class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-md font-medium">
          Select events above
        </span>
        <span>→</span>
        <span class="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-md font-medium">
          Create filter
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import FilteredCalendarCard from './FilteredCalendarCard.vue'

defineProps({
  filteredCalendars: {
    type: Array,
    required: true
  },
  isUpdateMode: {
    type: Boolean,
    default: false
  },
  showEmptyState: {
    type: Boolean,
    default: false
  },
  copySuccessId: {
    type: String,
    default: null
  },
  updatingId: {
    type: String,
    default: null
  }
})

defineEmits(['copy-url', 'update-filter', 'delete', 'save-name'])
</script>
