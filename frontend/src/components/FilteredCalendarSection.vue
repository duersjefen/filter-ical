<template>
  <div 
    v-if="shouldShowSection" 
    class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-4"
  >
    <div 
      class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:from-slate-200 hover:to-slate-100 dark:hover:from-gray-600 dark:hover:to-gray-700 transition-all duration-200"
      @click="toggleExpanded"
      :title="isExpanded ? $t('filteredCalendar.minimizeSection') : $t('filteredCalendar.expandSection')"
    >
      <div class="flex items-center gap-3">
        <!-- Chevron icon (moved to left, matching groups card) -->
        <svg 
          class="w-4 h-4 text-gray-600 dark:text-gray-300 transition-transform duration-300 flex-shrink-0" 
          :class="{ 'rotate-90': isExpanded }"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
        
        <div class="flex-1">
          <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            🔗 {{ $t('filteredCalendar.title') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
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
      <!-- Create/Update Form - Auto-show when events selected -->
      <div v-if="selectedRecurringEvents.length > 0 || isUpdateMode" class="mb-6 p-4 rounded-lg border" 
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
        
        <!-- Login Required Message for Anonymous Users -->
        <div v-if="!hasCustomUsername()" class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg p-3 mb-4">
          <div class="flex items-center gap-2">
            <div class="text-amber-600 dark:text-amber-400">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </div>
            <p class="text-amber-800 dark:text-amber-200 text-sm font-medium">
              Please set a username above to save filters
            </p>
          </div>
        </div>
        
        <form @submit.prevent="createFilteredCalendar" class="space-y-4" :class="{ 'opacity-50 pointer-events-none': !hasCustomUsername() }">
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
            <div class="space-y-3">
              <!-- Group Subscriptions Display -->
              <div v-if="hasGroups && groups && Object.keys(groups).length > 0" class="space-y-2">
                <!-- All Groups in a flex wrap layout -->
                <div class="flex flex-wrap gap-2 text-xs">
                  <span 
                    v-for="(group, groupId) in groups" 
                    :key="groupId"
                    class="inline-flex items-center gap-2 px-3 py-2 rounded-lg border-2 whitespace-nowrap font-medium transition-all duration-200"
                    :class="getGroupDisplayClass(groupId)"
                  >
                    <!-- Large, prominent subscription icon -->
                    <span class="text-sm font-bold">{{ getGroupSubscriptionIcon(groupId) }}</span>
                    <!-- Subscription status text -->
                    <span class="font-semibold text-xs uppercase tracking-wide">{{ getGroupSubscriptionStatus(groupId) }}</span>
                    <!-- Count display -->
                    <span class="px-2 py-1 rounded-md text-xs font-bold" :class="getCountDisplayClass(groupId)">
                      {{ getGroupSelectedCount(groupId) }}/{{ getGroupTotalCount(group) }}
                    </span>
                    <!-- Group name with icon -->
                    <span class="font-medium">{{ getGroupDisplayName(group) }}</span>
                  </span>
                </div>
              </div>
              <!-- Fallback for non-group calendars -->
              <div v-else class="text-sm text-gray-600 dark:text-gray-400">
                {{ reactiveGroupBreakdown || $t('preview.noEventsSelected') }}
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="!createForm.name.trim() || creating || !hasCustomUsername()"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="isUpdateMode 
                ? 'bg-amber-600 hover:bg-amber-700 disabled:bg-gray-400 text-white' 
                : 'bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white'"
            >
              <span v-if="isUpdateMode">
                {{ creating ? $t('filteredCalendar.updating') : $t('filteredCalendar.updateFilter') }}
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

      <!-- Existing Filtered Calendars (hidden during update mode) -->
      <div v-if="filteredCalendars.length > 0 && !isUpdateMode">
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
                    <span v-if="getFilterSummary(calendar.filter_config).hasFilter" 
                          :class="getFilterSummary(calendar.filter_config).badgeClass">
                      {{ getFilterSummary(calendar.filter_config).text }}
                    </span>
                    <span v-else
                          class="bg-gray-100 dark:bg-gray-900/30 text-gray-800 dark:text-gray-200 px-2 py-1 rounded font-medium">
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
                  
                  <!-- Filter details display -->
                  <div class="text-xs text-gray-600 dark:text-gray-300">
                    <div v-if="hasGroups && calendar.filter_config?.groups?.length > 0">
                      <!-- Group-based filter display -->
                      <div class="flex flex-wrap gap-2 mb-2">
                        <span 
                          v-for="groupId in calendar.filter_config.groups" 
                          :key="groupId"
                          v-if="groups[groupId]"
                          class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
                        >
                          <span>{{ getGroupDisplayName(groups[groupId]) }}</span>
                        </span>
                      </div>
                    </div>
                    <!-- Remove redundant individual events display since we show it in the badge above -->
                  </div>
                </div>

                <div class="flex flex-wrap gap-2 mt-2">
                  <button
                    @click="copyToClipboard(getFullExportUrl(calendar))"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium text-xs transition-all duration-200 hover:shadow-sm"
                    :class="copySuccess === getFullExportUrl(calendar) 
                      ? 'bg-green-600 dark:bg-green-700 text-white hover:bg-green-700 dark:hover:bg-green-800' 
                      : 'bg-blue-500 dark:bg-blue-600 text-white hover:bg-blue-600 dark:hover:bg-blue-700'"
                  >
                    <span v-if="copySuccess === getFullExportUrl(calendar)">✅</span>
                    <span v-else>📋</span>
                    <span>{{ copySuccess === getFullExportUrl(calendar) 
                      ? $t('filteredCalendar.copied') 
                      : $t('filteredCalendar.copyUrl') }}</span>
                  </button>
                  
                  <button
                    @click="loadFilterIntoPage(calendar)"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 dark:bg-amber-600 text-white hover:bg-amber-600 dark:hover:bg-amber-700 rounded-md font-medium text-xs transition-all duration-200 hover:shadow-sm"
                  >
                    <span>🔄</span>
                    <span>{{ $t('filteredCalendar.updateFilter') }}</span>
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

      <!-- Empty state - only show if no existing calendars and no events selected (and not in update mode) -->
      <div v-else-if="filteredCalendars.length === 0 && selectedRecurringEvents.length === 0 && !isUpdateMode" class="text-center py-6">
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
          <span class="text-sm font-medium">{{ $t('filteredCalendar.calendarNameUpdated') }}</span>
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
import { formatDateTime as formatDateTimeUtil, formatDateRange as formatDateRangeUtil } from '@/utils/dateFormatting'
import { useFilteredCalendarAPI } from '@/composables/useFilteredCalendarAPI'
import { useUsername } from '@/composables/useUsername'
import { API_ENDPOINTS } from '@/constants/api'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'

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
const { hasCustomUsername } = useUsername()
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
const hasEverHadRecurringEvents = ref(false) // Track if user has ever selected events
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

// Reactive computed property for group breakdown display
const reactiveGroupBreakdown = computed(() => {
  if (!props.hasGroups || !props.groups) {
    // For personal calendars, show basic event count display
    return getBasicRecurringEventDisplay(props.selectedRecurringEvents)
  }
  
  const groupBreakdowns = []
  
  // Process all groups and show detailed breakdown
  Object.entries(props.groups).forEach(([groupId, group]) => {
    const isSubscribed = props.subscribedGroups && props.subscribedGroups.has(groupId)
    const groupRecurringEvents = getGroupRecurringEvents(group)
    const selectedInGroup = groupRecurringEvents.filter(event => 
      props.selectedRecurringEvents && props.selectedRecurringEvents.includes(event)
    ).length
    const totalInGroup = groupRecurringEvents.length
    
    // Get group emoji/icon from name (first emoji) or use default
    const groupIcon = group.name.match(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u)?.[0] || '📋'
    const groupName = group.name.replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '').trim()
    
    const subscriptionIcon = isSubscribed ? '✅' : '☐'
    const effectiveSelected = selectedInGroup
    
    groupBreakdowns.push(`${subscriptionIcon} ${effectiveSelected}/${totalInGroup} ${groupIcon} ${groupName}`)
  })
  
  if (groupBreakdowns.length === 0) {
    return t('calendar.noGroupsAvailable')
  }
  
  // Show ALL groups - no truncation
  return groupBreakdowns.join(', ')
})

// Show section if there are existing filtered calendars OR if events are selected
// OR if user has ever interacted with events (to prevent disappearing during search/filter workflows)
const shouldShowSection = computed(() => {
  // Always show if there are existing filtered calendars
  if (filteredCalendars.value.length > 0) {
    return true
  }
  
  // Show if events are currently selected
  if (props.selectedRecurringEvents.length > 0) {
    return true
  }
  
  // Show if user has ever selected events in this session
  // This prevents the section from disappearing during search/filter operations
  if (hasEverHadRecurringEvents.value) {
    return true
  }
  
  return false
})

// Auto-populate form name when groups/events selected
const updateFormName = () => {
  if ((props.selectedRecurringEvents.length > 0 || (props.subscribedGroups && props.subscribedGroups.size > 0)) && !createForm.value.name.trim()) {
    const groupCount = props.subscribedGroups ? props.subscribedGroups.size : 0
    const suffix = groupCount > 0 ? t('filteredCalendar.groupSelection') : t('filteredCalendar.eventSelection')
    createForm.value.name = `${props.selectedCalendar.name} - ${suffix}`
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
    recurring_events: props.selectedRecurringEvents,
    groups: Array.from(props.subscribedGroups || [])
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
      filterConfig.groups,
      filterConfig.recurring_events
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
    // Create filter config based on current recurring events selection
    const filterConfig = {
      recurring_events: props.selectedRecurringEvents,
      groups: Array.from(props.subscribedGroups || [])
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
  
  // Get recurring events and groups to select
  const recurringEventsToSelect = filterConfig.recurring_events || []
  const groupsToSelect = filterConfig.groups || []
  
  // Enter update mode
  isUpdateMode.value = true
  updateModeCalendar.value = calendar
  createForm.value.name = calendar.name
  
  // Emit to parent component to load the filter with both events and groups
  emit('load-filter', {
    recurringEvents: recurringEventsToSelect,
    groups: groupsToSelect,
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

const getFilterRecurringEvents = (filterConfig) => {
  return filterConfig?.recurring_events || []
}

// Helper to check if filter has specific recurring events
const hasSpecificRecurringEvents = (filterConfig) => {
  return filterConfig?.recurring_events && filterConfig.recurring_events.length > 0
}

// Helper to build full export URL from calendar object
const getFullExportUrl = (calendar) => {
  if (!calendar || !calendar.export_url) {
    console.warn('Calendar object missing export_url:', calendar)
    return ''
  }
  
  // If we're in development, use localhost backend
  if (import.meta.env.MODE === 'development') {
    return `http://localhost:3000${calendar.export_url}`
  }
  
  // Production URL
  return `https://filter-ical.de${calendar.export_url}`
}

const getGroupRecurringEvents = (group) => {
  if (!group || !group.recurring_events) return []
  return group.recurring_events.filter(recurringEvent => {
    return recurringEvent.event_count > 0
  }).map(recurringEvent => recurringEvent.title)
}

const getDetailedGroupBreakdown = () => {
  if (!props.hasGroups || !props.groups) {
    return ''
  }
  
  const groupBreakdowns = []
  
  // Process all groups and show detailed breakdown
  Object.entries(props.groups).forEach(([groupId, group]) => {
    const isSubscribed = props.subscribedGroups && props.subscribedGroups.has(groupId)
    const groupRecurringEvents = getGroupRecurringEvents(group)
    const selectedInGroup = groupRecurringEvents.filter(event => 
      props.selectedRecurringEvents && props.selectedRecurringEvents.includes(event)
    ).length
    const totalInGroup = groupRecurringEvents.length
    
    // Get group emoji/icon from name (first emoji) or use default
    const groupIcon = group.name.match(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u)?.[0] || '📋'
    const groupName = group.name.replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '').trim()
    
    const subscriptionIcon = isSubscribed ? '✅' : '☐'
    const effectiveSelected = selectedInGroup
    
    groupBreakdowns.push(`${subscriptionIcon} ${effectiveSelected}/${totalInGroup} ${groupIcon} ${groupName}`)
  })
  
  if (groupBreakdowns.length === 0) {
    return t('calendar.noGroupsAvailable')
  }
  
  // Show ALL groups - no truncation
  return groupBreakdowns.join(', ')
}

const getGroupSubscriptionDisplay = (selectedRecurringEvents, selectedGroups) => {
  if (!props.hasGroups || !props.groups) {
    // Fallback for non-group calendars
    return getBasicRecurringEventDisplay(selectedRecurringEvents)
  }
  
  // Return the detailed group breakdown instead of the old simple display
  return getDetailedGroupBreakdown()
}

const getSmartRecurringEventDisplay = (selectedRecurringEvents) => {
  if (!selectedRecurringEvents || selectedRecurringEvents.length === 0) return ''
  
  // Enhanced display for group-aware filtering
  if (props.hasGroups && props.groups && Object.keys(props.groups).length > 0) {
    return getGroupAwareDisplay(selectedRecurringEvents)
  }
  
  // Fallback to original logic for non-group calendars
  return getBasicRecurringEventDisplay(selectedRecurringEvents)
}

const getGroupAwareDisplay = (selectedRecurringEvents) => {
  if (!props.groups || !props.subscribedGroups) {
    return getBasicRecurringEventDisplay(selectedRecurringEvents)
  }
  
  const totalGroups = Object.keys(props.groups).length
  const subscribedGroups = props.subscribedGroups.size || 0
  
  if (subscribedGroups === 0 && (!selectedRecurringEvents || selectedRecurringEvents.length === 0)) {
    return 'No groups or events selected'
  }
  
  // Create summary for compact display
  const parts = []
  
  if (subscribedGroups > 0) {
    parts.push(`${subscribedGroups}/${totalGroups} groups subscribed`)
  }
  
  const individualEvents = selectedRecurringEvents || []
  if (individualEvents.length > 0) {
    parts.push(`${individualEvents.length} individual events`)
  }
  
  return parts.join(' + ')
}

const getVirtualGroupSelection = (groupName, selectedRecurringEvents, selectedIndividualRecurringEvents) => {
  // This is a simplified version - in a real implementation, you'd check
  // against the actual virtual group event types from the store
  // For now, we'll just return null to avoid complexity
  return null
}

const getBasicRecurringEventDisplay = (selectedRecurringEvents) => {
  // Use proper recurring event data to distinguish main vs single recurring events
  const mainRecurringEventNames = props.mainRecurringEvents.map(event => event.name)
  const singleRecurringEventNames = props.singleRecurringEvents.map(event => event.name)
  
  // Separate selected recurring events by their actual type (not name length heuristic)
  const selectedMainEvents = selectedRecurringEvents.filter(event => mainRecurringEventNames.includes(event))
  const selectedSingleEvents = selectedRecurringEvents.filter(event => singleRecurringEventNames.includes(event))
  
  let display = ''
  
  // Show main recurring events first
  if (selectedMainEvents.length > 0) {
    if (selectedMainEvents.length <= 3) {
      display = selectedMainEvents.join(', ')
    } else {
      display = `${selectedMainEvents.slice(0, 2).join(', ')} and ${selectedMainEvents.length - 2} more events`
    }
  }
  
  // Add single events summary if any
  if (selectedSingleEvents.length > 0) {
    const eventSummary = selectedSingleEvents.length === 1 ? '1 unique event' : `${selectedSingleEvents.length} unique events`
    display = display ? `${display} + ${eventSummary}` : eventSummary
  }
  
  return display
}

// New helper functions for improved group display
const getGroupSubscriptionIcon = (groupId) => {
  const isSubscribed = props.subscribedGroups && props.subscribedGroups.has(groupId)
  return isSubscribed ? '✅' : '☐'
}

const getGroupSelectedCount = (groupId) => {
  const group = props.groups[groupId]
  if (!group) return 0
  
  const groupRecurringEvents = getGroupRecurringEvents(group)
  
  // Always count only the actually selected events from props.selectedRecurringEvents
  // This works for both subscribed groups and individual selections
  return groupRecurringEvents.filter(event => 
    props.selectedRecurringEvents && props.selectedRecurringEvents.includes(event)
  ).length
}

const getGroupTotalCount = (group) => {
  return getGroupRecurringEvents(group).length
}

const getGroupDisplayName = (group) => {
  // Extract emoji and clean name
  const groupIcon = group.name.match(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u)?.[0] || '📋'
  const groupName = group.name.replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '').trim()
  return `${groupIcon} ${groupName}`
}

const getGroupSubscriptionStatus = (groupId) => {
  const isSubscribed = props.subscribedGroups && props.subscribedGroups.has(groupId)
  const selectedCount = getGroupSelectedCount(groupId)
  const totalCount = getGroupTotalCount(props.groups[groupId])
  
  if (isSubscribed) {
    return 'SUBSCRIBED'
  } else if (selectedCount === totalCount && totalCount > 0) {
    return 'ALL SELECTED'
  } else if (selectedCount > 0) {
    return 'PARTIAL'
  } else {
    return 'NOT SELECTED'
  }
}

const getGroupDisplayClass = (groupId) => {
  const isSubscribed = props.subscribedGroups && props.subscribedGroups.has(groupId)
  const selectedCount = getGroupSelectedCount(groupId)
  const totalCount = getGroupTotalCount(props.groups[groupId])
  
  if (isSubscribed) {
    // SUBSCRIBED - Very prominent green with strong border
    return 'bg-green-100 dark:bg-green-800/50 border-green-500 dark:border-green-400 text-green-800 dark:text-green-100 shadow-lg shadow-green-200/50 dark:shadow-green-800/30'
  } else if (selectedCount === totalCount && totalCount > 0) {
    // ALL SELECTED manually - Strong blue
    return 'bg-blue-100 dark:bg-blue-800/50 border-blue-500 dark:border-blue-400 text-blue-800 dark:text-blue-100 shadow-md shadow-blue-200/50 dark:shadow-blue-800/30'
  } else if (selectedCount > 0) {
    // PARTIALLY selected - Light blue
    return 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-600 text-blue-700 dark:text-blue-300'
  } else {
    // NOT SELECTED - Muted gray
    return 'bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'
  }
}

const getCountDisplayClass = (groupId) => {
  const selectedCount = getGroupSelectedCount(groupId)
  const totalCount = getGroupTotalCount(props.groups[groupId])
  
  // Match the same color coding: 0 -> Grey; 1/7 -> Blue; 7/7 -> Green
  // Based on subscription ratios, regardless of subscription status
  if (selectedCount === totalCount && totalCount > 0) {
    // 7/7 (or any complete selection) -> Green
    return 'bg-green-600 dark:bg-green-500 text-white'
  } else if (selectedCount > 0 && selectedCount < totalCount) {
    // 1/7 (or any partial selection) -> Blue
    return 'bg-blue-600 dark:bg-blue-500 text-white'
  } else {
    // 0/7 (no selection) -> Grey
    return 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
  }
}

// Keep the old function for backward compatibility in existing calendars display
const getConciseRecurringEvents = (recurringEvents) => {
  if (!recurringEvents || recurringEvents.length === 0) return ''
  
  // For 1-2 items, show all
  if (recurringEvents.length <= 2) {
    return recurringEvents.join(', ')
  }
  
  // For 3+ items, be more aggressive with truncation to avoid UI clutter
  const firstEvent = recurringEvents[0]
  const remaining = recurringEvents.length - 1
  
  return `${firstEvent} and ${remaining} more...`
}

// New function to combine group and event counts into a single clear display
const getFilterSummary = (filterConfig) => {
  if (!filterConfig) {
    return { hasFilter: false, text: '', badgeClass: '' }
  }
  
  const groupCount = filterConfig.groups?.length || 0
  const eventCount = filterConfig.recurring_events?.length || 0
  
  if (groupCount === 0 && eventCount === 0) {
    return { hasFilter: false, text: '', badgeClass: '' }
  }
  
  // Build combined text
  const parts = []
  if (groupCount > 0) {
    parts.push(`📊 ${groupCount} ${groupCount === 1 ? 'group' : 'groups'}`)
  }
  if (eventCount > 0) {
    parts.push(`📂 ${eventCount} ${eventCount === 1 ? 'event' : 'events'}`)
  }
  
  // Choose badge color based on primary selection type
  let badgeClass
  if (groupCount > 0) {
    // Green for group-based filters (primary)
    badgeClass = 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-2 py-1 rounded font-medium'
  } else {
    // Blue for event-based filters
    badgeClass = 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 px-2 py-1 rounded font-medium'
  }
  
  return {
    hasFilter: true,
    text: parts.join(' + '),
    badgeClass
  }
}

// Watch for recurring event changes to auto-populate form name and track user interaction
watch([() => props.selectedRecurringEvents], () => {
  updateFormName()
  
  // Track if user has ever selected events to prevent section from disappearing
  if (props.selectedRecurringEvents.length > 0) {
    hasEverHadRecurringEvents.value = true
  }
  
  // Exit update mode if no events are selected (with delay to allow parent to update props)
  if (props.selectedRecurringEvents.length === 0 && isUpdateMode.value) {
    // Use nextTick to allow parent component to process the load-filter event first
    setTimeout(() => {
      // Only exit if still no events after allowing time for parent to update
      if (props.selectedRecurringEvents.length === 0 && isUpdateMode.value) {
        exitUpdateMode()
      }
    }, 100)
  }
}, { immediate: true })

// Lifecycle
onMounted(async () => {
  // Load filtered calendars for the selected calendar
  if (props.selectedCalendar?.id) {
    await loadFilteredCalendars(props.selectedCalendar.id)
    updateFormName()
  }
})
</script>