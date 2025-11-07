<template>
  <div
    v-if="shouldShowSection"
    class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-4 hover:shadow-2xl hover:shadow-emerald-500/10 dark:hover:shadow-emerald-400/20 transition-all duration-500 transform"
    :class="{ 'hover:scale-[1.02]': !isExpanded }"
  >
    <!-- Section Header -->
    <div
      class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-4 sm:px-5 lg:px-6 py-4 sm:py-5 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:from-slate-200 hover:to-slate-100 dark:hover:from-gray-600 dark:hover:to-gray-700 transition-all duration-300 group"
      @click="toggleExpanded"
      :title="isExpanded ? $t('filteredCalendar.minimizeSection') : $t('filteredCalendar.expandSection')"
    >
      <div class="flex items-center gap-4">
        <svg
          class="w-5 h-5 text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200 transition-all duration-300 flex-shrink-0"
          :class="{ 'rotate-90 text-blue-600 dark:text-blue-400': isExpanded }"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>

        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 mb-2">
            <h3 class="text-2xl sm:text-3xl font-black text-gray-900 dark:text-gray-100 leading-tight tracking-tight">
              🔗 <span class="bg-gradient-to-r from-gray-700 to-gray-600 dark:from-gray-300 dark:to-gray-200 bg-clip-text text-transparent">{{ $t('filteredCalendar.title') }}</span>
            </h3>
            <div v-if="enrichedFilteredCalendars.length > 0"
                 class="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-sm font-semibold rounded-full border border-blue-200 dark:border-blue-700">
              {{ enrichedFilteredCalendars.length }}
            </div>
          </div>
          <p class="text-base font-medium text-gray-700 dark:text-gray-300 leading-relaxed">
            {{ $t('filteredCalendar.description') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Collapsible content section -->
    <div
      v-show="isExpanded"
      class="transition-all duration-300 ease-in-out"
      :class="{
        'opacity-100': isExpanded,
        'opacity-0 max-h-0 overflow-hidden': !isExpanded
      }"
    >
      <div class="p-3 sm:p-4">
        <!-- Filter Form -->
        <FilterForm
          :selected-recurring-events="selectedRecurringEvents"
          :subscribed-groups="subscribedGroups"
          :is-update-mode="isUpdateMode"
          :update-mode-calendar="updateModeCalendar"
          :is-logged-in="isLoggedIn"
          :form-name="createForm.name"
          :include-new-events="createForm.includeNewEvents"
          :creating="creating"
          :is-domain-calendar="isDomainCalendar"
          :groups="groups"
          :has-groups="hasGroups"
          :main-recurring-events="mainRecurringEvents"
          :single-recurring-events="singleRecurringEvents"
          @submit="createFilteredCalendar"
          @exit-update-mode="exitUpdateMode"
          @update:formName="createForm.name = $event"
          @update:includeNewEvents="createForm.includeNewEvents = $event"
        />

        <!-- Filtered Calendars List -->
        <FilteredCalendarList
          :filtered-calendars="enrichedFilteredCalendars"
          :is-update-mode="isUpdateMode"
          :show-empty-state="selectedRecurringEvents.length === 0 && !isUpdateMode"
          :copy-success-id="copySuccess"
          :updating-id="updatingCalendarId"
          @copy-url="copyToClipboard($event)"
          @update-filter="loadFilterIntoPage"
          @delete="deleteFilteredCalendar"
          @save-name="handleSaveName"
        />

        <!-- Loading State -->
        <div v-if="loading && !creating && !updating" class="text-center py-6">
          <div class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-700">
            <div class="inline-flex items-center justify-center w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-4">
              <div class="animate-spin rounded-full h-6 w-6 border-2 border-blue-600 border-t-transparent"></div>
            </div>
            <h3 class="text-base font-semibold text-blue-900 dark:text-blue-100 mb-1">
              {{ $t('filteredCalendar.loadingCalendars') }}
            </h3>
            <p class="text-sm text-blue-700 dark:text-blue-300">
              Fetching your saved calendar filters...
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirm Dialog -->
  <ConfirmDialog
    ref="confirmDialog"
    :title="$t('home.deleteCalendar')"
    :message="$t('filteredCalendar.confirmDelete')"
    :confirm-text="$t('common.delete')"
    :cancel-text="$t('common.cancel')"
    @confirm="handleDeleteConfirm"
    @cancel="handleDeleteCancel"
  />
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFilteredCalendarAPI } from '@/composables/useFilteredCalendarAPI'
import { useUsername } from '@/composables/useUsername'
import { useAuth } from '@/composables/useAuth'
import { useNotification } from '@/composables/useNotification'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import FilterForm from '@/components/filtered-calendar/FilterForm.vue'
import FilteredCalendarList from '@/components/filtered-calendar/FilteredCalendarList.vue'

// Props
const props = defineProps({
  selectedCalendar: {
    type: Object,
    required: true
  },
  selectedRecurringEvents: {
    type: Array,
    required: true
  },
  selectedGroups: {
    type: Array,
    default: () => []
  },
  subscribedGroups: {
    type: Set,
    default: () => new Set()
  },
  mainRecurringEvents: {
    type: Array,
    default: () => []
  },
  singleRecurringEvents: {
    type: Array,
    default: () => []
  },
  groups: {
    type: Object,
    default: () => ({})
  },
  hasGroups: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['navigate-to-calendar', 'load-filter'])

// Composables
const { t } = useI18n()
const { getUserId } = useUsername()
const { isLoggedIn, user } = useAuth()
const notify = useNotification()
const {
  filteredCalendars,
  loading,
  creating,
  updating,
  createFilteredCalendar: apiCreateFiltered,
  updateFilteredCalendar: apiUpdateFiltered,
  deleteFilteredCalendar: apiDeleteFiltered,
  loadFilteredCalendars
} = useFilteredCalendarAPI()

// Reactive state
const isExpanded = ref(true)
const hasEverHadRecurringEvents = ref(false)
const isUpdateMode = ref(false)
const updateModeCalendar = ref(null)
const updateModeOriginalFilter = ref(null)  // Store original filter to detect changes
const createForm = ref({
  name: '',
  includeNewEvents: true
})
const confirmDialog = ref(null)
const deleteCalendarId = ref(null)
const copySuccess = ref(null)
const updatingCalendarId = ref(null)

// Computed
const isDomainCalendar = computed(() => {
  return props.selectedCalendar?.domain_key ||
         String(props.selectedCalendar?.id).startsWith('cal_domain_')
})

const shouldShowSection = computed(() => {
  if (filteredCalendars.value.length > 0) return true
  if (props.selectedRecurringEvents.length > 0) return true
  if (hasEverHadRecurringEvents.value) return true
  if (props.selectedCalendar?.id) return true
  return false
})

// Enrich filtered calendars with actual event counts
const enrichedFilteredCalendars = computed(() => {
  return filteredCalendars.value.map(calendar => {
    const filterConfig = calendar.filter_config
    if (!filterConfig) {
      return { ...calendar, totalEventCount: 0 }
    }

    let totalCount = 0

    // Count events from subscribed groups
    if (filterConfig.groups && Array.isArray(filterConfig.groups)) {
      filterConfig.groups.forEach(groupId => {
        const group = props.groups[String(groupId)]
        if (group && group.recurring_events) {
          totalCount += group.recurring_events.length
        }
      })
    }

    // Add individually selected events (that aren't already in groups)
    if (filterConfig.recurring_events && Array.isArray(filterConfig.recurring_events)) {
      totalCount += filterConfig.recurring_events.length
    }

    // Subtract unselected events
    if (filterConfig.unselected_events && Array.isArray(filterConfig.unselected_events)) {
      totalCount -= filterConfig.unselected_events.length
    }

    return { ...calendar, totalEventCount: Math.max(0, totalCount) }
  })
})

// Methods
const updateFormName = () => {
  if (isUpdateMode.value) return

  const hasSelection = props.selectedRecurringEvents.length > 0 || (props.subscribedGroups && props.subscribedGroups.size > 0)

  if (hasSelection) {
    // Use actual username from authenticated user, fallback to getUserId for anonymous users
    const displayName = user.value?.username || getUserId()
    const filterNumbers = filteredCalendars.value
      .map(cal => {
        const match = cal.name.match(/Filter (\d+)$/i)
        return match ? parseInt(match[1], 10) : 0
      })
      .filter(num => num > 0)

    const nextNumber = filterNumbers.length > 0 ? Math.max(...filterNumbers) + 1 : 1
    createForm.value.name = `${displayName} - Filter ${nextNumber}`
  } else {
    createForm.value.name = ''
  }
}

const clearCreateForm = () => {
  createForm.value.name = ''
}

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const createFilteredCalendar = async () => {
  if (!props.selectedCalendar?.id) {
    console.error('Cannot create filtered calendar: No calendar selected')
    return false
  }

  if (props.selectedRecurringEvents.length === 0 && props.subscribedGroups.size === 0) {
    console.error('Cannot create filtered calendar: No events or groups selected')
    return false
  }

  const filterConfig = {
    recurring_events: props.selectedRecurringEvents,
    groups: Array.from(props.subscribedGroups || []),
    include_future_events: !isDomainCalendar.value ? createForm.value.includeNewEvents : undefined
  }

  let success = false

  if (isUpdateMode.value && updateModeCalendar.value) {
    success = await apiUpdateFiltered(
      updateModeCalendar.value.id,
      {
        name: createForm.value.name,
        filter_config: filterConfig
      },
      props.groups || {}
    )
  } else {
    success = await apiCreateFiltered(
      props.selectedCalendar.id,
      createForm.value.name,
      filterConfig.groups,
      filterConfig.recurring_events,
      filterConfig.include_future_events,
      props.groups || {}
    )
  }

  if (success) {
    if (isUpdateMode.value) {
      notify.success(t('filteredCalendar.filterUpdatedSuccessfully') || 'Filter updated successfully!')
    } else {
      notify.success(t('filteredCalendar.filterCreatedSuccessfully') || 'Filter created successfully!')
    }

    clearCreateForm()
    if (isUpdateMode.value) {
      exitUpdateMode()
    }
  } else {
    notify.error(t('filteredCalendar.failedToSaveFilter') || 'Failed to save filter. Please try again.')
  }
}

const handleSaveName = async ({ id, name }) => {
  if (!name.trim() || updating.value) return

  updatingCalendarId.value = id

  try {
    // CRITICAL FIX: Only send name if that's all that changed
    // This prevents losing event selections when user only updates name
    const updates = { name }

    // Only include filter_config if not updating, or if no original filter stored
    // (which means selection UI is active and user might have changed things)
    if (!updateModeOriginalFilter.value) {
      const filterConfig = {
        recurring_events: props.selectedRecurringEvents,
        groups: Array.from(props.subscribedGroups || [])
      }
      updates.filter_config = filterConfig
    }

    const success = await apiUpdateFiltered(
      id,
      updates,
      props.groups || {}
    )

    if (success) {
      notify.success(t('filteredCalendar.filterNameUpdated') || 'Filter name updated successfully!')
      emit('navigate-to-calendar')
    } else {
      notify.error(t('filteredCalendar.failedToUpdateFilterName') || 'Failed to update filter name')
    }
  } catch (error) {
    notify.error(t('filteredCalendar.failedToUpdateFilterName') || 'Failed to update filter name')
    console.error('Error updating calendar:', error)
  } finally {
    updatingCalendarId.value = null
  }
}

const deleteFilteredCalendar = async (id) => {
  deleteCalendarId.value = id
  confirmDialog.value.open()
}

const handleDeleteConfirm = async () => {
  if (deleteCalendarId.value) {
    const success = await apiDeleteFiltered(deleteCalendarId.value)
    if (success) {
      notify.success(t('filteredCalendar.filterDeletedSuccessfully') || 'Filter deleted successfully!')
    } else {
      notify.error(t('filteredCalendar.failedToDeleteFilter') || 'Failed to delete filter')
    }
    deleteCalendarId.value = null
  }
}

const handleDeleteCancel = () => {
  deleteCalendarId.value = null
}

const loadFilterIntoPage = (calendar) => {
  const filterConfig = calendar.filter_config
  if (!filterConfig) return

  isUpdateMode.value = true
  updateModeCalendar.value = calendar
  updateModeOriginalFilter.value = calendar  // Store original filter data
  createForm.value.name = calendar.name

  // Pass COMPLETE three-list model to CalendarView
  emit('load-filter', {
    groups: filterConfig.groups || [],
    recurringEvents: filterConfig.recurring_events || [],
    unselectedEvents: filterConfig.unselected_events || [],
    calendarName: calendar.name
  })

  nextTick(() => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  })
}

const exitUpdateMode = () => {
  isUpdateMode.value = false
  updateModeCalendar.value = null
  updateModeOriginalFilter.value = null  // Clear original filter
  createForm.value.name = ''
}

const copyToClipboard = async (calendar) => {
  const url = getFullExportUrl(calendar)
  if (!url) {
    console.error('Cannot copy: no URL available')
    return
  }

  try {
    await navigator.clipboard.writeText(url)
    copySuccess.value = String(calendar.id)
    setTimeout(() => {
      copySuccess.value = null
    }, 2000)
  } catch (err) {
    console.error('Failed to copy URL:', err)
    const textArea = document.createElement('textarea')
    textArea.value = url
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    copySuccess.value = String(calendar.id)
    setTimeout(() => {
      copySuccess.value = null
    }, 2000)
  }
}

const getFullExportUrl = (calendar) => {
  if (!calendar || !calendar.export_url) {
    console.warn('Calendar object missing export_url:', calendar)
    return ''
  }
  // If export_url is already an absolute URL, return it as-is
  if (calendar.export_url.startsWith('http://') || calendar.export_url.startsWith('https://')) {
    return calendar.export_url
  }
  // Otherwise, prepend the current origin (for backward compatibility with relative URLs)
  return `${window.location.origin}${calendar.export_url}`
}

// Watchers
watch(() => props.selectedCalendar, async (newCalendar) => {
  if (newCalendar?.id) {
    await loadFilteredCalendars(newCalendar.id)
  } else {
    filteredCalendars.value = []
  }
}, { immediate: false })

watch(() => getUserId(), async (newUserId, oldUserId) => {
  if (newUserId !== oldUserId) {
    if (props.selectedCalendar?.id) {
      await loadFilteredCalendars(props.selectedCalendar.id)
    }
  }
}, { immediate: false })

watch(
  [
    () => props.selectedRecurringEvents.length,
    () => props.subscribedGroups?.size || 0,
    () => props.selectedCalendar?.id
  ],
  () => {
    updateFormName()

    if (props.selectedRecurringEvents.length > 0) {
      hasEverHadRecurringEvents.value = true
    }

    if (props.selectedRecurringEvents.length === 0 && isUpdateMode.value) {
      setTimeout(() => {
        if (props.selectedRecurringEvents.length === 0 && isUpdateMode.value) {
          exitUpdateMode()
        }
      }, 100)
    }
  },
  { immediate: true }
)

// Lifecycle
onMounted(async () => {
  if (props.selectedCalendar?.id) {
    await loadFilteredCalendars(props.selectedCalendar.id)
    updateFormName()
  } else {
    filteredCalendars.value = []
  }
})
</script>
