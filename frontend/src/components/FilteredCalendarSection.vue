<template>
  <div 
    v-if="shouldShowSection" 
    class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6"
  >
    <div class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
            🔗 {{ $t('filteredCalendar.title') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-300">
            {{ $t('filteredCalendar.description') }}
          </p>
        </div>
        <!-- Auto-show form when categories selected, no button needed -->
      </div>
    </div>

    <div class="p-4 sm:p-6">
      <!-- Create Form - Auto-show when categories selected -->
      <div v-if="selectedCategories.length > 0" class="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">
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
                {{ getSmartCategoryDisplay(selectedCategories) || $t('filteredCalendar.allCategories') }}
              </div>
              <div v-else class="mb-1">
                ❌ <strong>{{ $t('filteredCalendar.excludeMode') }}</strong>: 
                {{ getSmartCategoryDisplay(selectedCategories) || $t('filteredCalendar.noExclusions') }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-500">
                {{ $t('filteredCalendar.filterInfo') }}
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="!createForm.name.trim() || creating"
              class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              {{ creating ? $t('filteredCalendar.creating') : $t('filteredCalendar.create') }}
            </button>
          </div>
        </form>
      </div>

      <!-- Existing Filtered Calendars -->
      <div v-if="filteredCalendars.length > 0">
        <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">
          {{ $t('filteredCalendar.yourFiltered') }} ({{ filteredCalendars.length }})
        </h4>
        
        <div class="space-y-3">
          <div
            v-for="calendar in filteredCalendars"
            :key="calendar.id"
            class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <h5 class="font-medium text-gray-800 dark:text-gray-200">
                    {{ calendar.name }}
                  </h5>
                  <button
                    @click="startEditForm(calendar)"
                    class="inline-flex items-center p-1 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 rounded transition-colors"
                    :title="t('common.edit')"
                  >
                    ✏️
                  </button>
                </div>
                
                <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <div class="mb-1">
                    📅 {{ $t('filteredCalendar.created') }}: {{ formatDateTime(calendar.created_at) }}
                  </div>
                  
                  <!-- Filter Logic Summary -->
                  <div v-if="calendar.filter_config" class="bg-gray-100 dark:bg-gray-600 rounded-lg p-3 mb-2">
                    <div class="font-medium text-gray-800 dark:text-gray-200 mb-2">
                      🔍 {{ $t('filteredCalendar.filterLogic') }}:
                    </div>
                    
                    <!-- Include Mode Display -->
                    <div v-if="hasIncludeCategories(calendar.filter_config)" class="mb-2">
                      <div class="flex items-center gap-2 mb-1">
                        <span class="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-2 py-1 rounded text-xs font-medium">
                          ✅ {{ $t('filteredCalendar.includeOnly') }}
                        </span>
                        <span class="text-xs text-gray-600 dark:text-gray-400">
                          {{ getIncludeCategoriesCount(calendar.filter_config) }} {{ $t('filteredCalendar.categories') }}
                        </span>
                      </div>
                      <div class="text-xs text-gray-700 dark:text-gray-300">
                        {{ getSmartCategoryDisplay(getIncludeCategories(calendar.filter_config)) }}
                      </div>
                    </div>
                    
                    <!-- Exclude Mode Display -->
                    <div v-else-if="hasExcludeCategories(calendar.filter_config)" class="mb-2">
                      <div class="flex items-center gap-2 mb-1">
                        <span class="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-2 py-1 rounded text-xs font-medium">
                          ❌ {{ $t('filteredCalendar.excludeOnly') }}
                        </span>
                        <span class="text-xs text-gray-600 dark:text-gray-400">
                          {{ getExcludeCategoriesCount(calendar.filter_config) }} {{ $t('filteredCalendar.categories') }}
                        </span>
                      </div>
                      <div class="text-xs text-gray-700 dark:text-gray-300">
                        {{ getSmartCategoryDisplay(getExcludeCategories(calendar.filter_config)) }}
                      </div>
                    </div>
                    
                    <!-- No Category Filter Display -->
                    <div v-else class="mb-2">
                      <span class="bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200 px-2 py-1 rounded text-xs font-medium">
                        📋 No category filter applied
                      </span>
                      <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        This calendar contains the original events
                      </div>
                    </div>
                    
                    <!-- Additional Filter Info -->
                    <div v-if="calendar.filter_config.filter_mode" class="text-xs text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-500 pt-2 mt-2">
                      {{ $t('filteredCalendar.mode') }}: {{ calendar.filter_config.filter_mode === 'include' ? $t('filteredCalendar.includeMode') : $t('filteredCalendar.excludeMode') }}
                    </div>
                  </div>
                </div>

                <div class="flex flex-wrap gap-2 text-xs">
                  <button
                    @click="copyToClipboard(calendar.calendar_url)"
                    class="inline-flex items-center px-2 py-1 rounded transition-colors"
                    :class="copySuccess === calendar.calendar_url 
                      ? 'bg-green-600 text-white' 
                      : 'bg-blue-600 hover:bg-blue-700 text-white'"
                  >
                    <span v-if="copySuccess === calendar.calendar_url">✅</span>
                    <span v-else>📋</span>
                    {{ copySuccess === calendar.calendar_url 
                      ? $t('filteredCalendar.copied') 
                      : $t('filteredCalendar.copyUrl') }}
                  </button>
                  
                  <a
                    :href="calendar.preview_url"
                    target="_blank"
                    class="inline-flex items-center px-2 py-1 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                  >
                    👁️ {{ $t('filteredCalendar.preview') }}
                  </a>
                  
                  <button
                    @click="deleteFilteredCalendar(calendar.id)"
                    class="inline-flex items-center px-2 py-1 bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                    @click.stop
                  >
                    🗑️ {{ $t('common.delete') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state - only show if no existing calendars and no categories selected -->
      <div v-else-if="!showCreateForm && filteredCalendars.length === 0 && selectedCategories.length === 0" class="text-center py-6">
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

  <!-- Edit Modal -->
  <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
      <h3 class="text-lg font-medium text-gray-800 dark:text-gray-200 mb-4">
        {{ $t('filteredCalendar.editTitle') }}
      </h3>
      
      <form @submit.prevent="updateFilteredCalendar" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ $t('filteredCalendar.name') }}
          </label>
          <input
            v-model="editForm.name"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          />
        </div>

        <div class="flex gap-2">
          <button
            type="submit"
            :disabled="updating"
            class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            {{ updating ? $t('common.saving') : $t('common.save') }}
          </button>
          <button
            type="button"
            @click="cancelEditForm"
            class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
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
import { ref, computed, watch, onMounted } from 'vue'
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
  selectedCategories: {
    type: Array,
    required: true
  },
  filterMode: {
    type: String,
    required: true
  },
  mainCategories: {
    type: Array,
    default: () => []
  },
  singleEventCategories: {
    type: Array,
    default: () => []
  }
})

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
const showEditModal = ref(false)
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

// Computed
const formatDateTime = computed(() => formatDateTimeUtil)
const formatDateRange = computed(() => formatDateRangeUtil)

// Show section if there are existing filtered calendars OR if categories are selected
const shouldShowSection = computed(() => {
  return filteredCalendars.value.length > 0 || props.selectedCategories.length > 0
})

// Auto-populate form name when categories selected
const updateFormName = () => {
  if (props.selectedCategories.length > 0 && !createForm.value.name.trim()) {
    createForm.value.name = `${props.selectedCalendar.name} - ${props.filterMode === 'include' ? t('filteredCalendar.includeMode') : t('filteredCalendar.excludeMode')}`
  }
}

const clearCreateForm = () => {
  createForm.value.name = ''
}

const createFilteredCalendar = async () => {
  const filterConfig = {
    include_categories: props.filterMode === 'include' ? props.selectedCategories : [],
    exclude_categories: props.filterMode === 'exclude' ? props.selectedCategories : [],
    filter_mode: props.filterMode
  }

  const success = await apiCreateFiltered(
    props.selectedCalendar.id,
    createForm.value.name,
    filterConfig
  )

  if (success) {
    clearCreateForm()
  }
}

const startEditForm = (calendar) => {
  editForm.value = {
    id: calendar.id,
    name: calendar.name
  }
  showEditModal.value = true
}

const cancelEditForm = () => {
  showEditModal.value = false
  editForm.value = { id: '', name: '' }
}

const updateFilteredCalendar = async () => {
  const success = await apiUpdateFiltered(
    editForm.value.id,
    { name: editForm.value.name }
  )

  if (success) {
    cancelEditForm()
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

const getFilterCategories = (filterConfig) => {
  const include = filterConfig?.include_categories || []
  const exclude = filterConfig?.exclude_categories || []
  
  if (include.length > 0) {
    return include
  } else if (exclude.length > 0) {
    return exclude.map(cat => `❌${cat}`)
  }
  
  return []
}

// New helper functions for improved UX
const hasIncludeCategories = (filterConfig) => {
  return filterConfig?.include_categories && filterConfig.include_categories.length > 0
}

const hasExcludeCategories = (filterConfig) => {
  return filterConfig?.exclude_categories && filterConfig.exclude_categories.length > 0
}

const getIncludeCategories = (filterConfig) => {
  return filterConfig?.include_categories || []
}

const getExcludeCategories = (filterConfig) => {
  return filterConfig?.exclude_categories || []
}

const getIncludeCategoriesCount = (filterConfig) => {
  return filterConfig?.include_categories?.length || 0
}

const getExcludeCategoriesCount = (filterConfig) => {
  return filterConfig?.exclude_categories?.length || 0
}

const getSmartCategoryDisplay = (selectedCategories) => {
  if (!selectedCategories || selectedCategories.length === 0) return ''
  
  // Use proper category data to distinguish main vs single categories
  const mainCategoryNames = props.mainCategories.map(cat => cat.name)
  const singleEventCategoryNames = props.singleEventCategories.map(cat => cat.name)
  
  // Separate selected categories by their actual type (not name length heuristic)
  const selectedMainCats = selectedCategories.filter(cat => mainCategoryNames.includes(cat))
  const selectedSingleEvents = selectedCategories.filter(cat => singleEventCategoryNames.includes(cat))
  
  let display = ''
  
  // Show main categories first
  if (selectedMainCats.length > 0) {
    if (selectedMainCats.length <= 3) {
      display = selectedMainCats.join(', ')
    } else {
      display = `${selectedMainCats.slice(0, 2).join(', ')} and ${selectedMainCats.length - 2} more categories`
    }
  }
  
  // Add single events summary if any
  if (selectedSingleEvents.length > 0) {
    const eventSummary = selectedSingleEvents.length === 1 ? '1 individual event' : `${selectedSingleEvents.length} individual events`
    display = display ? `${display} + ${eventSummary}` : eventSummary
  }
  
  return display
}

// Keep the old function for backward compatibility in existing calendars display
const getConciseCategories = (categories) => {
  if (!categories || categories.length === 0) return ''
  
  // For 1-2 items, show all
  if (categories.length <= 2) {
    return categories.join(', ')
  }
  
  // For 3+ items, be more aggressive with truncation to avoid UI clutter
  const firstCategory = categories[0]
  const remaining = categories.length - 1
  
  return `${firstCategory} and ${remaining} more...`
}

// Watch for category changes to auto-populate form name
watch([() => props.selectedCategories, () => props.filterMode], () => {
  updateFormName()
}, { immediate: true })

// Lifecycle
onMounted(async () => {
  if (props.selectedCalendar?.id) {
    await loadFilteredCalendars()
    updateFormName() // Auto-populate form name on mount
  }
})
</script>