<template>
  <div class="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden">
    <!-- Calendar Header -->
    <div class="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center gap-3">
        <div class="flex-shrink-0">
          <div class="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
        </div>

        <!-- Inline Edit Name -->
        <div class="flex-1 min-w-0">
          <div v-if="isEditing" class="flex items-center gap-2">
            <input
              v-model="editedName"
              @keyup.enter="$emit('save-name', editedName)"
              @keyup.escape="cancelEdit"
              @blur="$emit('save-name', editedName)"
              ref="nameInput"
              class="flex-1 bg-white dark:bg-gray-800 border border-blue-300 dark:border-blue-600 rounded-lg px-3 py-1.5 text-lg font-bold text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              :disabled="updating"
            />
            <button
              @click="$emit('save-name', editedName)"
              :disabled="updating || !editedName.trim()"
              class="p-1.5 text-green-600 hover:text-green-700 hover:bg-green-50 dark:text-green-400 dark:hover:text-green-300 dark:hover:bg-green-900/20 rounded-lg transition-all duration-200 disabled:opacity-50"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </button>
            <button
              @click="cancelEdit"
              class="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div v-else class="flex items-center gap-2 group/name cursor-pointer" @click="startEdit">
            <h5 class="font-bold text-gray-900 dark:text-gray-100 text-lg leading-tight">
              {{ calendar.name }}
            </h5>
            <div class="opacity-0 group-hover/name:opacity-100 transition-opacity duration-200">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar Content -->
    <div class="p-4">
      <div class="flex-1">
        <!-- Filter Summary -->
        <div class="space-y-3 mb-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span v-if="filterSummary.hasFilter"
                    :class="filterSummary.badgeClass + ' text-sm font-semibold px-3 py-1.5 rounded-lg border shadow-sm'">
                {{ filterSummary.text }}
              </span>
              <span v-else
                    class="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-1.5 rounded-lg font-semibold text-sm border border-gray-200 dark:border-gray-600 shadow-sm">
                📋 All events
              </span>
            </div>

            <!-- Date info -->
            <div class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span v-if="calendar.updated_at && calendar.updated_at !== calendar.created_at">
                {{ t('common.updated') }} {{ formatCreatedDate(calendar.updated_at) }}
              </span>
              <span v-else>
                {{ t('common.created') }} {{ formatCreatedDate(calendar.created_at) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-2 mt-3">
          <div class="flex gap-2 flex-1">
            <button
              @click="$emit('copy-url', calendar)"
              class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg font-semibold text-xs transition-all duration-200 shadow-sm hover:shadow-md border"
              :class="copySuccess
                ? 'bg-green-500 text-white hover:bg-green-600 border-green-400 hover:border-green-500'
                : 'bg-blue-500 text-white hover:bg-blue-600 border-blue-400 hover:border-blue-500'"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
              <span>{{ copySuccess ? $t('filteredCalendar.copied') : $t('filteredCalendar.copyUrl') }}</span>
            </button>

            <button
              @click="$emit('update-filter')"
              class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-amber-500 text-white hover:bg-amber-600 rounded-lg font-semibold text-xs transition-all duration-200 shadow-sm hover:shadow-md border border-amber-400 hover:border-amber-500"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
              <span>{{ $t('filteredCalendar.updateFilter') }}</span>
            </button>
          </div>

          <button
            @click="$emit('delete')"
            class="inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-red-500 text-white hover:bg-red-600 rounded-lg font-semibold text-xs transition-all duration-200 shadow-sm hover:shadow-md border border-red-400 hover:border-red-500 sm:w-auto w-full"
            @click.stop
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            <span>{{ $t('common.delete') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  calendar: {
    type: Object,
    required: true
  },
  copySuccess: {
    type: Boolean,
    default: false
  },
  updating: {
    type: Boolean,
    default: false
  }
})

defineEmits(['copy-url', 'update-filter', 'delete', 'save-name'])

const { t, locale } = useI18n()
const isEditing = ref(false)
const editedName = ref('')
const nameInput = ref(null)

const filterSummary = computed(() => {
  const filterConfig = props.calendar.filter_config
  if (!filterConfig) {
    return { hasFilter: false, text: '', badgeClass: '' }
  }

  const groupCount = filterConfig.groups?.length || 0
  const eventCount = filterConfig.recurring_events?.length || 0

  if (groupCount === 0 && eventCount === 0) {
    return { hasFilter: false, text: '', badgeClass: '' }
  }

  let text = ''
  if (groupCount > 0 && eventCount > 0) {
    text = `📊 ${groupCount} ${groupCount === 1 ? t('common.group') : t('common.groups')} & ${eventCount} ${t('common.recurringEvents')}`
  } else if (groupCount > 0) {
    text = `📊 ${groupCount} ${groupCount === 1 ? 'group' : 'groups'}`
  } else if (eventCount > 0) {
    text = `📂 ${eventCount} recurring ${eventCount === 1 ? 'event' : 'events'}`
  }

  let badgeClass
  if (groupCount > 0) {
    badgeClass = 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-2 py-1 rounded font-medium'
  } else {
    badgeClass = 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 px-2 py-1 rounded font-medium'
  }

  return {
    hasFilter: true,
    text: text,
    badgeClass
  }
})

const startEdit = () => {
  isEditing.value = true
  editedName.value = props.calendar.name

  nextTick(() => {
    if (nameInput.value) {
      nameInput.value.focus()
      nameInput.value.select()
    }
  })
}

const cancelEdit = () => {
  isEditing.value = false
  editedName.value = ''
}

const formatCreatedDate = (dateString) => {
  if (!dateString) {
    return new Date().toLocaleDateString(locale.value, { year: 'numeric', month: 'short', day: 'numeric' })
  }

  try {
    let date
    if (typeof dateString === 'string') {
      date = new Date(dateString)
    } else {
      date = new Date(dateString)
    }

    if (isNaN(date.getTime())) {
      console.warn('Invalid date format, using current date:', dateString)
      date = new Date()
    }

    return date.toLocaleDateString(locale.value, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch (error) {
    console.error('Date formatting error:', error, 'for date:', dateString)
    return new Date().toLocaleDateString(locale.value, { year: 'numeric', month: 'short', day: 'numeric' })
  }
}
</script>
