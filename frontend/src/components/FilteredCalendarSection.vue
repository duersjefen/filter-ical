<template>
  <div 
    v-if="shouldShowSection" 
    class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6"
  >
    <div 
      class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:from-green-100 hover:to-emerald-100 dark:hover:from-green-900/30 dark:hover:to-emerald-900/30 transition-all duration-200"
      @click="toggleExpanded"
      :title="isExpanded ? 'Minimize section' : 'Expand section'"
    >
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
            🔗 {{ $t('filteredCalendar.title') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-300">
            {{ $t('filteredCalendar.description') }}
          </p>
        </div>
        <!-- Chevron icon with background circle (consistent with EventTypeCardsSection) -->
        <button class="flex-shrink-0 p-2 rounded-full bg-white/50 dark:bg-gray-600/50 hover:bg-white dark:hover:bg-gray-600 transition-all duration-200 pointer-events-none">
          <svg 
            class="w-5 h-5 text-gray-600 dark:text-gray-300 transition-transform duration-200" 
            :class="{ 'rotate-180': isExpanded }"
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
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
      <div class="p-4 sm:p-6">
      <!-- Create/Update Form - Auto-show when event types selected -->
      <div v-if="selectedEventTypes.length > 0 || isUpdateMode" class="mb-6 p-4 rounded-lg border" 
           :class="isUpdateMode 
             ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-300 dark:border-amber-700' 
             : 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600'">
        
        <!-- Update Mode Header -->
        <div v-if="isUpdateMode" class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🔄</span>
            <div>
              <h4 class="text-md font-medium text-amber-800 dark:text-amber-200">
                Update Filter: "{{ updateModeCalendar?.name }}"
              </h4>
              <p class="text-xs text-amber-700 dark:text-amber-300">
                You're modifying an existing filtered calendar
              </p>
            </div>
          </div>
          <button 
            @click="exitUpdateMode"
            class="text-amber-700 dark:text-amber-300 hover:text-amber-900 dark:hover:text-amber-100 font-medium text-sm"
          >
            ✕ Cancel Update
          </button>
        </div>
        
        <!-- Create Mode Header -->
        <h4 v-else class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">
          {{ $t('filteredCalendar.createTitle') }}
        </h4>
        
        <form @submit.prevent="createFilteredCalendar" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ $t('filteredCalendar.name') }}
            </label>
            <input
              v-model="createForm.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              :placeholder="$t('filteredCalendar.namePlaceholder')"
            />
          </div>

          <div class="bg-white dark:bg-gray-800 p-3 rounded border border-gray-200 dark:border-gray-600">
            <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('filteredCalendar.currentFilter') }}:
            </h5>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              <div v-if="filterMode === 'include'" class="mb-1">
                ✅ <strong>{{ $t('filteredCalendar.includeMode') }}</strong>: 
                {{ getSmartEventTypeDisplay(selectedEventTypes) || $t('filteredCalendar.allEventTypes') }}
              </div>
              <div v-else class="mb-1">
                ❌ <strong>{{ $t('filteredCalendar.excludeMode') }}</strong>: 
                {{ getSmartEventTypeDisplay(selectedEventTypes) || $t('filteredCalendar.noExclusions') }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-500">
                {{ $t('filteredCalendar.filterInfo') }}
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="!createForm.name.trim() || creating"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="isUpdateMode 
                ? 'bg-amber-600 hover:bg-amber-700 disabled:bg-gray-400 text-white' 
                : 'bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white'"
            >
              <span v-if="isUpdateMode">
                {{ creating ? 'Updating...' : '🔄 Update Filter' }}
              </span>
              <span v-else>
                {{ creating ? $t('filteredCalendar.creating') : $t('filteredCalendar.create') }}
              </span>
            </button>
            
            <button
              v-if="isUpdateMode"
              type="button"
              @click="exitUpdateMode"
              class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>

      <!-- Existing Filtered Calendars -->
      <div v-if="filteredCalendars.length > 0">
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">
          {{ $t('filteredCalendar.yourFiltered') }} ({{ filteredCalendars.length }})
        </h4>
        
        <div class="space-y-2">
          <div
            v-for="calendar in filteredCalendars"
            :key="calendar.id"
            class="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <h5 class="font-medium text-gray-800 dark:text-gray-200">
                    {{ calendar.name }}
                  </h5>
                  <button
                    @click="startEditForm(calendar)"
                    class="inline-flex items-center p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 dark:text-gray-500 dark:hover:text-blue-400 dark:hover:bg-blue-900/20 rounded-md transition-all duration-200 group"
                    :title="$t('common.edit')"
                  >
                    <svg class="w-4 h-4 transition-transform duration-200 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                </div>
                
                <!-- Compact Filter Summary -->
                <div class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  <!-- Single line with filter info and date -->
                  <div class="flex items-center gap-3 text-xs mb-2">
                    <!-- Filter badge -->
                    <span v-if="calendar.filter_config?.include_event_types?.length > 0" 
                          class="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-2 py-1 rounded font-medium">
                      ✅ {{ calendar.filter_config.include_event_types.length }} included
                    </span>
                    <span v-else-if="calendar.filter_config?.exclude_event_types?.length > 0" 
                          class="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-2 py-1 rounded font-medium">
                      ❌ {{ calendar.filter_config.exclude_event_types.length }} excluded
                    </span>
                    <span v-else-if="calendar.filter_config?.filter_mode" 
                          class="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 px-2 py-1 rounded font-medium">
                      📋 All events
                    </span>
                    
                    <!-- Date info -->
                    <span class="text-gray-500 dark:text-gray-400">
                      <span v-if="calendar.updated_at && calendar.updated_at !== calendar.created_at">
                        Updated {{ formatCreatedDate(calendar.updated_at) }}
                      </span>
                      <span v-else>
                        Created {{ formatCreatedDate(calendar.created_at) }}
                      </span>
                    </span>
                  </div>
                  
                  <!-- Event types list (only if specific types selected) -->
                  <div v-if="calendar.filter_config?.include_event_types?.length > 0 || calendar.filter_config?.exclude_event_types?.length > 0" 
                       class="text-xs text-gray-600 dark:text-gray-300">
                    {{ getSmartEventTypeDisplay(
                      calendar.filter_config?.include_event_types?.length > 0 
                        ? calendar.filter_config.include_event_types 
                        : calendar.filter_config.exclude_event_types || []
                    ) }}
                  </div>
                </div>

                <div class="flex flex-wrap gap-2 mt-2">
                  <button
                    @click="copyToClipboard(calendar.calendar_url)"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium text-xs transition-all duration-200 hover:shadow-sm"
                    :class="copySuccess === calendar.calendar_url 
                      ? 'bg-green-600 dark:bg-green-700 text-white hover:bg-green-700 dark:hover:bg-green-800' 
                      : 'bg-blue-500 dark:bg-blue-600 text-white hover:bg-blue-600 dark:hover:bg-blue-700'"
                  >
                    <span v-if="copySuccess === calendar.calendar_url">✅</span>
                    <span v-else>📋</span>
                    <span>{{ copySuccess === calendar.calendar_url 
                      ? $t('filteredCalendar.copied') 
                      : $t('filteredCalendar.copyUrl') }}</span>
                  </button>
                  
                  <button
                    @click="loadFilterIntoPage(calendar)"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 dark:bg-amber-600 text-white hover:bg-amber-600 dark:hover:bg-amber-700 rounded-md font-medium text-xs transition-all duration-200 hover:shadow-sm"
                  >
                    <span>🔄</span>
                    <span>Update Filter</span>
                  </button>
                  
                  <button
                    @click="deleteFilteredCalendar(calendar.id)"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-500 dark:bg-rose-600 text-white hover:bg-rose-600 dark:hover:bg-rose-700 rounded-md font-medium text-xs transition-all duration-200 hover:shadow-sm"
                    @click.stop
                  >
                    <span>🗑️</span>
                    <span>{{ $t('common.delete') }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state - only show if no existing calendars and no event types selected -->
      <div v-else-if="!showCreateForm && filteredCalendars.length === 0 && selectedEventTypes.length === 0" class="text-center py-6">
        <div class="text-6xl mb-4">📅</div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          {{ $t('filteredCalendar.noFiltered') }}
        </p>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {{ $t('filteredCalendar.getStarted') }}
        </p>
      </div>

      <!-- Loading state - only show if not creating/updating (avoid double loading indicators) -->
      <div v-if="loading && !creating && !updating" class="text-center py-4">
        <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
        <p class="text-sm text-gray-600 dark:text-gray-300 mt-2">{{ $t('filteredCalendar.loadingCalendars') }}</p>
      </div>
      </div>
    </div>
  </div>

  <!-- Edit Modal -->
  <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="cancelEditForm">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-md mx-4 transform transition-all duration-300" @click.stop>
      <div class="flex items-center gap-3 mb-4">
        <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
          <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">
          {{ $t('filteredCalendar.editTitle') }}
        </h3>
      </div>
      
      <!-- Success feedback -->
      <div v-if="editSuccess" class="mb-4 p-3 bg-green-100 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg">
        <div class="flex items-center gap-2 text-green-800 dark:text-green-200">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
          </svg>
          <span class="text-sm font-medium">Calendar name updated successfully!</span>
        </div>
      </div>
      
      <form @submit.prevent="updateFilteredCalendar" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('filteredCalendar.name') }}
          </label>
          <input
            v-model="editForm.name"
            type="text"
            required
            class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all duration-200"
            :disabled="updating"
            ref="editNameInput"
          />
        </div>

        <div class="flex gap-3 pt-2">
          <button
            type="submit"
            :disabled="updating || !editForm.name.trim() || editSuccess"
            :class="{
              'flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 text-white': true,
              'bg-green-600 cursor-not-allowed': editSuccess,
              'bg-gray-400 cursor-not-allowed': updating,
              'bg-blue-600 hover:bg-blue-700': !editSuccess && !updating,
              'disabled:bg-gray-400 disabled:cursor-not-allowed': !editSuccess && !updating
            }"
          >
            <svg v-if="updating" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else-if="editSuccess" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            {{ editSuccess ? $t('common.saved') : (updating ? $t('filteredCalendar.saving') : $t('common.save')) }}
          </button>
          <button
            type="button"
            @click="cancelEditForm"
            :disabled="updating"
            class="px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg text-sm font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('common.cancel') }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Confirm Dialog -->
  <ConfirmDialog
    ref="confirmDialog"
    title="Delete Calendar"
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
import { formatDateTime as formatDateTimeUtil, formatDateRange as formatDateRangeUtil } from '@/utils/dates'
import { useFilteredCalendarAPI } from '@/composables/useFilteredCalendarAPI'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'

// Props
const props = defineProps({
  selectedCalendar: {
    type: Object,
    required: true
  },
  selectedEventTypes: {
    type: Array,
    required: true
  },
  selectedGroups: {
    type: Array,
    default: () => []
  },
  filterMode: {
    type: String,
    required: true
  },
  mainEventTypes: {
    type: Array,
    default: () => []
  },
  singleEventTypes: {
    type: Array,
    default: () => []
  },
  // Group data for enhanced filter display
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
const isExpanded = ref(true) // Start expanded by default
const showEditModal = ref(false)
const hasEverHadEventTypes = ref(false) // Track if user has ever selected event types
const isUpdateMode = ref(false) // Track if user is updating an existing filter
const updateModeCalendar = ref(null) // Store the calendar being updated
const createForm = ref({
  name: ''
})
const editForm = ref({
  id: '',
  name: ''
})
const confirmDialog = ref(null)
const deleteCalendarId = ref(null)
const copySuccess = ref(null) // Track which URL was successfully copied
const editSuccess = ref(false) // Track edit success feedback
const editNameInput = ref(null) // Reference to edit input for focus

// Computed
const formatDateTime = computed(() => formatDateTimeUtil)
const formatDateRange = computed(() => formatDateRangeUtil)

// Show section if there are existing filtered calendars OR if event types are selected
// OR if user has ever interacted with event types (to prevent disappearing during search/filter workflows)
const shouldShowSection = computed(() => {
  // Always show if there are existing filtered calendars
  if (filteredCalendars.value.length > 0) {
    return true
  }
  
  // Show if event types are currently selected
  if (props.selectedEventTypes.length > 0) {
    return true
  }
  
  // Show if user has ever selected event types in this session
  // This prevents the section from disappearing during search/filter operations
  if (hasEverHadEventTypes.value) {
    return true
  }
  
  return false
})

// Auto-populate form name when event types selected
const updateFormName = () => {
  if (props.selectedEventTypes.length > 0 && !createForm.value.name.trim()) {
    createForm.value.name = `${props.selectedCalendar.name} - ${props.filterMode === 'include' ? t('filteredCalendar.includeMode') : t('filteredCalendar.excludeMode')}`
  }
}

const clearCreateForm = () => {
  createForm.value.name = ''
}

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const createFilteredCalendar = async () => {
  // Guard clause: Ensure we have a selected calendar
  if (!props.selectedCalendar?.id) {
    console.error('Cannot create filtered calendar: No calendar selected')
    return false
  }

  const filterConfig = {
    include_event_types: props.filterMode === 'include' ? props.selectedEventTypes : [],
    exclude_event_types: props.filterMode === 'exclude' ? props.selectedEventTypes : [],
    include_groups: props.filterMode === 'include' ? props.selectedGroups : [],
    exclude_groups: props.filterMode === 'exclude' ? props.selectedGroups : [],
    filter_mode: props.filterMode
  }

  let success = false

  if (isUpdateMode.value && updateModeCalendar.value) {
    // Update existing calendar
    success = await apiUpdateFiltered(
      updateModeCalendar.value.id,
      { 
        name: createForm.value.name,
        filter_config: filterConfig
      }
    )
  } else {
    // Create new calendar
    success = await apiCreateFiltered(
      props.selectedCalendar.id,
      createForm.value.name,
      filterConfig
    )
  }

  if (success) {
    clearCreateForm()
    if (isUpdateMode.value) {
      exitUpdateMode()
    }
  }
}

const startEditForm = (calendar) => {
  editForm.value = {
    id: calendar.id,
    name: calendar.name
  }
  editSuccess.value = false
  showEditModal.value = true
  
  // Focus input after modal renders
  nextTick(() => {
    if (editNameInput.value) {
      editNameInput.value.focus()
      editNameInput.value.select()
    }
  })
}

const cancelEditForm = () => {
  showEditModal.value = false
  editForm.value = { id: '', name: '' }
  editSuccess.value = false
}

const updateFilteredCalendar = async () => {
  try {
    // Create filter config based on current event type selection
    const filterConfig = {
      include_event_types: props.filterMode === 'include' ? props.selectedEventTypes : [],
      exclude_event_types: props.filterMode === 'exclude' ? props.selectedEventTypes : [],
      filter_mode: props.filterMode
    }
    
    const success = await apiUpdateFiltered(
      editForm.value.id,
      { 
        name: editForm.value.name,
        filter_config: filterConfig
      }
    )

    if (success) {
      // Set success state briefly to show green button
      editSuccess.value = true
      
      // Close modal immediately after brief success feedback (250ms)
      setTimeout(() => {
        showEditModal.value = false
        editForm.value = { id: '', name: '' }
        editSuccess.value = false
        emit('navigate-to-calendar')
      }, 250)
    } else {
      // Show error and close modal
      console.error('Failed to update calendar name - API returned false')
      setTimeout(() => {
        showEditModal.value = false
        editForm.value = { id: '', name: '' }
        editSuccess.value = false
      }, 1000)
    }
  } catch (error) {
    console.error('Error updating calendar:', error)
    // Always close modal even on exception
    setTimeout(() => {
      showEditModal.value = false
      editForm.value = { id: '', name: '' }
      editSuccess.value = false
    }, 1000)
  }
}

const deleteFilteredCalendar = async (id) => {
  deleteCalendarId.value = id
  confirmDialog.value.open()
}

const handleDeleteConfirm = async () => {
  if (deleteCalendarId.value) {
    await apiDeleteFiltered(deleteCalendarId.value)
    deleteCalendarId.value = null
  }
}

const handleDeleteCancel = () => {
  deleteCalendarId.value = null
}

const loadFilterIntoPage = (calendar) => {
  // Extract the filter configuration
  const filterConfig = calendar.filter_config
  if (!filterConfig) return
  
  // Determine the event types to select and the filter mode
  const eventTypesToSelect = filterConfig.filter_mode === 'include' 
    ? filterConfig.include_event_types || []
    : filterConfig.exclude_event_types || []
  
  const filterMode = filterConfig.filter_mode || 'include'
  
  // Enter update mode
  isUpdateMode.value = true
  updateModeCalendar.value = calendar
  createForm.value.name = calendar.name
  
  // Emit to parent component to load the filter
  emit('load-filter', {
    eventTypes: eventTypesToSelect,
    mode: filterMode,
    calendarName: calendar.name
  })
}

const exitUpdateMode = () => {
  isUpdateMode.value = false
  updateModeCalendar.value = null
  createForm.value.name = ''
}

const formatCreatedDate = (dateString) => {
  if (!dateString) {
    return new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }
  
  try {
    // Handle different date formats from backend
    let date
    
    // Try parsing as ISO string first
    if (typeof dateString === 'string') {
      date = new Date(dateString)
    } else {
      // Handle if it's already a Date object or timestamp
      date = new Date(dateString)
    }
    
    // Validate the date
    if (isNaN(date.getTime())) {
      // Fallback to current date if invalid
      console.warn('Invalid date format, using current date:', dateString)
      date = new Date()
    }
    
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric'
    })
  } catch (error) {
    console.error('Date formatting error:', error, 'for date:', dateString)
    return new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }
}

const copyToClipboard = async (url) => {
  try {
    await navigator.clipboard.writeText(url)
    // Show success feedback
    copySuccess.value = url
    setTimeout(() => {
      copySuccess.value = null
    }, 2000)
  } catch (err) {
    console.error('Failed to copy URL:', err)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = url
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    // Show success feedback
    copySuccess.value = url
    setTimeout(() => {
      copySuccess.value = null
    }, 2000)
  }
}

const getFilterEventTypes = (filterConfig) => {
  const include = filterConfig?.include_event_types || []
  const exclude = filterConfig?.exclude_event_types || []
  
  if (include.length > 0) {
    return include
  } else if (exclude.length > 0) {
    return exclude.map(cat => `❌${cat}`)
  }
  
  return []
}

// New helper functions for improved UX
const hasIncludeEventTypes = (filterConfig) => {
  return filterConfig?.include_event_types && filterConfig.include_event_types.length > 0
}

const hasExcludeEventTypes = (filterConfig) => {
  return filterConfig?.exclude_event_types && filterConfig.exclude_event_types.length > 0
}

const getIncludeEventTypes = (filterConfig) => {
  return filterConfig?.include_event_types || []
}

const getExcludeEventTypes = (filterConfig) => {
  return filterConfig?.exclude_event_types || []
}

const getIncludeEventTypesCount = (filterConfig) => {
  return filterConfig?.include_event_types?.length || 0
}

const getExcludeEventTypesCount = (filterConfig) => {
  return filterConfig?.exclude_event_types?.length || 0
}

const getSmartEventTypeDisplay = (selectedEventTypes) => {
  if (!selectedEventTypes || selectedEventTypes.length === 0) return ''
  
  // Enhanced display for group-aware filtering
  if (props.hasGroups && props.groups && Object.keys(props.groups).length > 0) {
    return getGroupAwareDisplay(selectedEventTypes)
  }
  
  // Fallback to original logic for non-group calendars
  return getBasicEventTypeDisplay(selectedEventTypes)
}

const getGroupAwareDisplay = (selectedEventTypes) => {
  const selectedGroups = []
  const selectedIndividualEventTypes = [...selectedEventTypes]
  
  // Find which groups are fully or partially selected
  Object.values(props.groups).forEach(group => {
    if (!group.event_types) return
    
    const groupEventTypes = Object.keys(group.event_types)
    const selectedInGroup = groupEventTypes.filter(eventType => 
      selectedEventTypes.includes(eventType)
    )
    
    if (selectedInGroup.length === groupEventTypes.length && groupEventTypes.length > 0) {
      // Fully selected group
      selectedGroups.push({ name: group.name, type: 'full', count: groupEventTypes.length })
      // Remove these event types from individual list
      selectedInGroup.forEach(eventType => {
        const index = selectedIndividualEventTypes.indexOf(eventType)
        if (index > -1) selectedIndividualEventTypes.splice(index, 1)
      })
    } else if (selectedInGroup.length > 0) {
      // Partially selected group
      selectedGroups.push({ 
        name: group.name, 
        type: 'partial', 
        count: selectedInGroup.length,
        total: groupEventTypes.length
      })
      // Remove these event types from individual list
      selectedInGroup.forEach(eventType => {
        const index = selectedIndividualEventTypes.indexOf(eventType)
        if (index > -1) selectedIndividualEventTypes.splice(index, 1)
      })
    }
  })
  
  // Check virtual groups (Recurring and Unique)
  const recurringGroup = getVirtualGroupSelection('🔄 Recurring Events', selectedEventTypes, selectedIndividualEventTypes)
  const uniqueGroup = getVirtualGroupSelection('📅 Unique Events', selectedEventTypes, selectedIndividualEventTypes)
  
  if (recurringGroup) selectedGroups.push(recurringGroup)
  if (uniqueGroup) selectedGroups.push(uniqueGroup)
  
  // Build display string
  let parts = []
  
  // Add groups
  if (selectedGroups.length > 0) {
    const groupDescriptions = selectedGroups.map(group => {
      if (group.type === 'full') {
        return group.name
      } else {
        return `${group.name} (${group.count}/${group.total})`
      }
    })
    
    if (groupDescriptions.length <= 2) {
      parts.push(groupDescriptions.join(', '))
    } else {
      parts.push(`${groupDescriptions[0]} and ${groupDescriptions.length - 1} more groups`)
    }
  }
  
  // Add remaining individual event types
  if (selectedIndividualEventTypes.length > 0) {
    const individualSummary = selectedIndividualEventTypes.length === 1 
      ? '1 event type' 
      : `${selectedIndividualEventTypes.length} event types`
    parts.push(individualSummary)
  }
  
  return parts.join(' + ')
}

const getVirtualGroupSelection = (groupName, selectedEventTypes, selectedIndividualEventTypes) => {
  // This is a simplified version - in a real implementation, you'd check
  // against the actual virtual group event types from the store
  // For now, we'll just return null to avoid complexity
  return null
}

const getBasicEventTypeDisplay = (selectedEventTypes) => {
  // Use proper event type data to distinguish main vs single event types
  const mainEventTypeNames = props.mainEventTypes.map(eventType => eventType.name)
  const singleEventTypeNames = props.singleEventTypes.map(eventType => eventType.name)
  
  // Separate selected event types by their actual type (not name length heuristic)
  const selectedMainTypes = selectedEventTypes.filter(cat => mainEventTypeNames.includes(cat))
  const selectedSingleEvents = selectedEventTypes.filter(cat => singleEventTypeNames.includes(cat))
  
  let display = ''
  
  // Show main event types first
  if (selectedMainTypes.length > 0) {
    if (selectedMainTypes.length <= 3) {
      display = selectedMainTypes.join(', ')
    } else {
      display = `${selectedMainTypes.slice(0, 2).join(', ')} and ${selectedMainTypes.length - 2} more event types`
    }
  }
  
  // Add single events summary if any
  if (selectedSingleEvents.length > 0) {
    const eventSummary = selectedSingleEvents.length === 1 ? '1 unique event' : `${selectedSingleEvents.length} unique events`
    display = display ? `${display} + ${eventSummary}` : eventSummary
  }
  
  return display
}

// Keep the old function for backward compatibility in existing calendars display
const getConciseEventTypes = (eventTypes) => {
  if (!eventTypes || eventTypes.length === 0) return ''
  
  // For 1-2 items, show all
  if (eventTypes.length <= 2) {
    return eventTypes.join(', ')
  }
  
  // For 3+ items, be more aggressive with truncation to avoid UI clutter
  const firstEventType = eventTypes[0]
  const remaining = eventTypes.length - 1
  
  return `${firstEventType} and ${remaining} more...`
}

// Watch for event type changes to auto-populate form name and track user interaction
watch([() => props.selectedEventTypes, () => props.filterMode], () => {
  updateFormName()
  
  // Track if user has ever selected event types to prevent section from disappearing
  if (props.selectedEventTypes.length > 0) {
    hasEverHadEventTypes.value = true
  }
  
  // Exit update mode if no event types are selected (with delay to allow parent to update props)
  if (props.selectedEventTypes.length === 0 && isUpdateMode.value) {
    // Use nextTick to allow parent component to process the load-filter event first
    setTimeout(() => {
      // Only exit if still no event types after allowing time for parent to update
      if (props.selectedEventTypes.length === 0 && isUpdateMode.value) {
        exitUpdateMode()
      }
    }, 100)
  }
}, { immediate: true })

// Lifecycle
onMounted(async () => {
  // Always load filtered calendars since they are global, not specific to one source calendar
  await loadFilteredCalendars()
  
  // Only auto-populate form name if we have a selected calendar
  if (props.selectedCalendar?.id) {
    updateFormName()
  }
})
</script>