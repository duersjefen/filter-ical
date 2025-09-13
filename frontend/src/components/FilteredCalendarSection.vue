<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
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
        <button
          v-if="!showCreateForm"
          @click="startCreateForm"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :disabled="selectedCategories.length === 0"
        >
          ➕ {{ $t('filteredCalendar.createNew') }}
        </button>
      </div>
    </div>

    <div class="p-4 sm:p-6">
      <!-- Create Form -->
      <div v-if="showCreateForm" class="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
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
                {{ selectedCategories.join(', ') || $t('filteredCalendar.allCategories') }}
              </div>
              <div v-else class="mb-1">
                ❌ <strong>{{ $t('filteredCalendar.excludeMode') }}</strong>: 
                {{ selectedCategories.join(', ') || $t('filteredCalendar.noExclusions') }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-500">
                {{ $t('filteredCalendar.filterInfo') }}
              </div>
            </div>
          </div>

          <div class="flex gap-2">
            <button
              type="submit"
              :disabled="!createForm.name.trim() || creating"
              class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              {{ creating ? $t('filteredCalendar.creating') : $t('filteredCalendar.create') }}
            </button>
            <button
              type="button"
              @click="cancelCreateForm"
              class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              {{ $t('common.cancel') }}
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
                <h5 class="font-medium text-gray-800 dark:text-gray-200 mb-1">
                  {{ calendar.name }}
                </h5>
                
                <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <div class="mb-1">
                    📅 {{ $t('filteredCalendar.created') }}: {{ formatDateTime(calendar.created_at) }}
                  </div>
                  <div v-if="calendar.filter_config" class="flex flex-wrap gap-1">
                    <span
                      v-for="category in getFilterCategories(calendar.filter_config)"
                      :key="category"
                      class="inline-flex items-center px-2 py-1 rounded-md text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
                    >
                      {{ category }}
                    </span>
                  </div>
                </div>

                <div class="flex flex-wrap gap-2 text-xs">
                  <button
                    @click="copyToClipboard(calendar.calendar_url)"
                    class="inline-flex items-center px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                  >
                    📋 {{ $t('filteredCalendar.copyUrl') }}
                  </button>
                  
                  <a
                    :href="calendar.preview_url"
                    target="_blank"
                    class="inline-flex items-center px-2 py-1 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                  >
                    👁️ {{ $t('filteredCalendar.preview') }}
                  </a>
                  
                  <button
                    @click="startEditForm(calendar)"
                    class="inline-flex items-center px-2 py-1 bg-yellow-600 hover:bg-yellow-700 text-white rounded transition-colors"
                  >
                    ✏️ {{ $t('common.edit') }}
                  </button>
                  
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

      <!-- Empty state -->
      <div v-else-if="!showCreateForm" class="text-center py-6">
        <div class="text-6xl mb-4">📅</div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          {{ $t('filteredCalendar.noFiltered') }}
        </p>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {{ $t('filteredCalendar.getStarted') }}
        </p>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-4">
        <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
        <p class="text-sm text-gray-600 dark:text-gray-300 mt-2">{{ $t('common.loading') }}</p>
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatDateTime as formatDateTimeUtil, formatDateRange as formatDateRangeUtil } from '@/utils/dates'
import { useFilteredCalendarAPI } from '@/composables/useFilteredCalendarAPI'

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
const showCreateForm = ref(false)
const showEditModal = ref(false)
const createForm = ref({
  name: ''
})
const editForm = ref({
  id: '',
  name: ''
})

// Computed
const formatDateTime = computed(() => formatDateTimeUtil)
const formatDateRange = computed(() => formatDateRangeUtil)

// Methods
const startCreateForm = () => {
  createForm.value.name = `${props.selectedCalendar.name} - ${props.filterMode === 'include' ? t('filteredCalendar.includeMode') : t('filteredCalendar.excludeMode')}`
  showCreateForm.value = true
}

const cancelCreateForm = () => {
  showCreateForm.value = false
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
    cancelCreateForm()
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
  if (confirm(t('filteredCalendar.confirmDelete'))) {
    await apiDeleteFiltered(id)
  }
}

const copyToClipboard = async (url) => {
  try {
    await navigator.clipboard.writeText(url)
    // TODO: Add toast notification
    alert(t('filteredCalendar.urlCopied'))
  } catch (err) {
    console.error('Failed to copy URL:', err)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = url
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    alert(t('filteredCalendar.urlCopied'))
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

// Lifecycle
onMounted(() => {
  if (props.selectedCalendar?.id) {
    loadFilteredCalendars()
  }
})
</script>