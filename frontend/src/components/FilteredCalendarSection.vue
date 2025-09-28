<template>
  <div 
    v-if="shouldShowSection" 
    class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-4 hover:shadow-2xl hover:shadow-emerald-500/10 dark:hover:shadow-emerald-400/20 transition-all duration-500 transform"
    :class="{ 'hover:scale-[1.02]': !isExpanded }"
  >
    <div 
      class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-4 sm:px-5 lg:px-6 py-4 sm:py-5 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:from-slate-200 hover:to-slate-100 dark:hover:from-gray-600 dark:hover:to-gray-700 transition-all duration-300 group"
      @click="toggleExpanded"
      :title="isExpanded ? $t('filteredCalendar.minimizeSection') : $t('filteredCalendar.expandSection')"
    >
      <div class="flex items-center gap-4">
        <!-- Enhanced chevron icon with better animation -->
        <svg 
          class="w-5 h-5 text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200 transition-all duration-300 flex-shrink-0" 
          :class="{ 'rotate-90 text-blue-600 dark:text-blue-400': isExpanded }"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
        
        <!-- Enhanced header content with better visual hierarchy -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 mb-2">
            <h3 class="text-2xl sm:text-3xl font-black text-gray-900 dark:text-gray-100 leading-tight tracking-tight">
              🔗 <span class="bg-gradient-to-r from-gray-700 to-gray-600 dark:from-gray-300 dark:to-gray-200 bg-clip-text text-transparent">{{ $t('filteredCalendar.title') }}</span>
            </h3>
            <!-- Status badge showing count of filtered calendars -->
            <div v-if="filteredCalendars.length > 0" 
                 class="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-sm font-semibold rounded-full border border-blue-200 dark:border-blue-700">
              {{ filteredCalendars.length }}
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

          <!-- Enhanced Groups Overview with improved visual design -->
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-600 shadow-sm">
            <!-- Groups Display for Group-enabled Calendars -->
            <div v-if="hasGroups && groups && Object.keys(groups).length > 0">
              <!-- Enhanced Groups Grid with better spacing -->
              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
                <div 
                  v-for="(group, groupId) in groups" 
                  :key="groupId"
                  class="relative bg-white dark:bg-gray-800 rounded-xl p-3 border shadow-sm hover:shadow-md transition-all duration-200 hover:scale-105"
                  :class="getGroupDisplayClass(groupId)"
                >
                  <!-- Enhanced status indicator with gradient -->
                  <div 
                    class="absolute top-0 left-0 right-0 h-1.5 rounded-t-xl transition-all duration-300"
                    :class="getProgressBarClass(groupId)"
                  ></div>
                  
                  <!-- Group Content with improved layout -->
                  <div class="pt-1">
                    <!-- Group Name with better typography -->
                    <div class="flex items-start gap-2 mb-2">
                      <span class="text-lg leading-none">{{ getGroupDisplayName(group).split(' ')[0] || '📋' }}</span>
                      <span class="text-sm font-bold text-gray-900 dark:text-gray-100 leading-tight line-clamp-2 flex-1">
                        {{ getGroupDisplayName(group).substring(getGroupDisplayName(group).indexOf(' ') + 1) || group.name }}
                      </span>
                    </div>
                    
                    <!-- Enhanced Count and Status display -->
                    <div class="flex items-center justify-between mt-2">
                      <!-- Improved Count Badge -->
                      <div class="flex items-center gap-1">
                        <span 
                          class="px-2.5 py-1 rounded-lg text-xs font-bold shadow-sm border" 
                          :class="getCountDisplayClass(groupId)"
                        >
                          {{ getGroupSelectedCount(groupId) }}/{{ getGroupTotalCount(group) }}
                        </span>
                      </div>
                      
                      <!-- Enhanced Status Indicator -->
                      <div class="flex items-center gap-1">
                        <div 
                          class="w-3 h-3 rounded-full border-2 border-white dark:border-gray-700 shadow-sm" 
                          :class="getGroupSubscriptionDotClass(groupId)"
                          :title="getGroupSubscriptionStatus(groupId)"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Summary stats below grid -->
              <div class="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-600 dark:text-gray-400">
                    {{ Object.keys(groups).length }} total groups
                  </span>
                  <span class="text-gray-600 dark:text-gray-400">
                    {{ reactiveGroupBreakdown }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Enhanced fallback for Non-Group Calendars -->
            <div v-else class="text-center py-4">
              <div class="text-gray-500 dark:text-gray-400 text-lg mb-2">📂</div>
              <div class="text-sm text-gray-600 dark:text-gray-400 font-medium">
                {{ reactiveGroupBreakdown || $t('preview.noEventsSelected') }}
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="!createForm.name.trim() || creating || !hasCustomUsername()"
              class="px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] border-2 flex items-center justify-center gap-2"
              :class="isUpdateMode 
                ? 'bg-amber-500 hover:bg-amber-600 disabled:bg-gray-400 text-white border-amber-400 hover:border-amber-500 disabled:border-gray-300' 
                : 'bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white border-green-400 hover:border-green-500 disabled:border-gray-300'"
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
              class="px-4 py-3 bg-gray-500 hover:bg-gray-400 text-white rounded-xl text-sm font-semibold transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] border-2 border-gray-400 hover:border-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>

      <!-- Enhanced Existing Filtered Calendars Section -->
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
          <div
            v-for="calendar in filteredCalendars"
            :key="calendar.id"
            class="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden"
          >
            <!-- Calendar Header with Inline Editing -->
            <div class="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
              <div class="flex items-center gap-3">
                <div class="flex-shrink-0">
                  <div class="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                </div>
                
                <!-- Inline Edit Name -->
                <div class="flex-1 min-w-0">
                  <div v-if="editingCalendarId === calendar.id" class="flex items-center gap-2">
                    <input
                      v-model="editForm.name"
                      @keyup.enter="updateFilteredCalendar"
                      @keyup.escape="cancelInlineEdit"
                      @blur="updateFilteredCalendar"
                      ref="inlineEditInput"
                      class="flex-1 bg-white dark:bg-gray-800 border border-blue-300 dark:border-blue-600 rounded-lg px-3 py-1.5 text-lg font-bold text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                      :disabled="updating"
                    />
                    <button
                      @click="updateFilteredCalendar"
                      :disabled="updating || !editForm.name.trim()"
                      class="p-1.5 text-green-600 hover:text-green-700 hover:bg-green-50 dark:text-green-400 dark:hover:text-green-300 dark:hover:bg-green-900/20 rounded-lg transition-all duration-200 disabled:opacity-50"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </button>
                    <button
                      @click="cancelInlineEdit"
                      class="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                  
                  <div v-else class="flex items-center gap-2 group/name cursor-pointer" @click="startInlineEdit(calendar)">
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
                
                <!-- Enhanced Filter Summary with better visual hierarchy -->
                <div class="space-y-3 mb-4">
                  <!-- Filter Badge - Primary Visual Element -->
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <span v-if="getFilterSummary(calendar.filter_config).hasFilter" 
                            :class="getFilterSummary(calendar.filter_config).badgeClass + ' text-sm font-semibold px-3 py-1.5 rounded-lg border shadow-sm'">
                        {{ getFilterSummary(calendar.filter_config).text }}
                      </span>
                      <span v-else
                            class="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-1.5 rounded-lg font-semibold text-sm border border-gray-200 dark:border-gray-600 shadow-sm">
                        📋 All events
                      </span>
                    </div>
                    
                    <!-- Date info with improved styling -->
                    <div class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                      <span v-if="calendar.updated_at && calendar.updated_at !== calendar.created_at">
                        Updated {{ formatCreatedDate(calendar.updated_at) }}
                      </span>
                      <span v-else>
                        Created {{ formatCreatedDate(calendar.created_at) }}
                      </span>
                    </div>
                  </div>
                  
                </div>

                <!-- Enhanced Action Buttons with better visual hierarchy -->
                <div class="flex flex-col sm:flex-row gap-2 mt-3">
                  <!-- Primary Actions (first row on mobile) -->
                  <div class="flex gap-2 flex-1">
                    <button
                      @click="copyToClipboard(getFullExportUrl(calendar))"
                      class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg font-semibold text-xs transition-all duration-200 shadow-sm hover:shadow-md border"
                      :class="copySuccess === getFullExportUrl(calendar) 
                        ? 'bg-green-500 text-white hover:bg-green-600 border-green-400 hover:border-green-500' 
                        : 'bg-blue-500 text-white hover:bg-blue-600 border-blue-400 hover:border-blue-500'"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                      </svg>
                      <span>{{ copySuccess === getFullExportUrl(calendar) 
                        ? $t('filteredCalendar.copied') 
                        : $t('filteredCalendar.copyUrl') }}</span>
                    </button>
                    
                    <button
                      @click="loadFilterIntoPage(calendar)"
                      class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2.5 bg-amber-500 text-white hover:bg-amber-600 rounded-lg font-semibold text-xs transition-all duration-200 shadow-sm hover:shadow-md border border-amber-400 hover:border-amber-500"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                      <span>{{ $t('filteredCalendar.updateFilter') }}</span>
                    </button>
                  </div>
                  
                  <!-- Destructive Action (separate for emphasis) -->
                  <button
                    @click="deleteFilteredCalendar(calendar.id)"
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
        </div>
      </div>

      <!-- Enhanced Empty State -->
      <div v-else-if="filteredCalendars.length === 0 && selectedRecurringEvents.length === 0 && !isUpdateMode" class="text-center py-8">
        <div class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-600">
          <div class="text-6xl mb-4">📅</div>
          <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
            {{ $t('filteredCalendar.noFiltered') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 max-w-md mx-auto leading-relaxed">
            {{ $t('filteredCalendar.getStarted') }}
          </p>
          <!-- Visual guide -->
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

      <!-- Enhanced Loading State -->
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
const editingCalendarId = ref(null) // Track which calendar is being edited inline
const inlineEditInput = ref(null) // Reference to inline edit input for focus

// Computed
const formatDateTime = computed(() => formatDateTimeUtil)
const formatDateRange = computed(() => formatDateRangeUtil)

// Reactive computed property for group breakdown display
const reactiveGroupBreakdown = computed(() => {
  if (!props.hasGroups || !props.groups) {
    // For personal calendars, show basic event count display
    return getBasicRecurringEventDisplay(props.selectedRecurringEvents)
  }
  
  // For group calendars, show concise summary
  const totalGroups = Object.keys(props.groups).length
  const subscribedGroups = props.subscribedGroups ? props.subscribedGroups.size : 0
  const selectedEvents = props.selectedRecurringEvents ? props.selectedRecurringEvents.length : 0
  
  const parts = []
  if (subscribedGroups > 0) {
    parts.push(`${subscribedGroups}/${totalGroups} groups subscribed`)
  }
  if (selectedEvents > 0) {
    parts.push(`${selectedEvents} events selected`)
  }
  
  return parts.length > 0 ? parts.join(' • ') : t('preview.noEventsSelected')
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

const startInlineEdit = (calendar) => {
  editingCalendarId.value = calendar.id
  editForm.value = {
    id: calendar.id,
    name: calendar.name
  }
  
  // Focus input after DOM update
  nextTick(() => {
    if (inlineEditInput.value) {
      inlineEditInput.value.focus()
      inlineEditInput.value.select()
    }
  })
}

const cancelInlineEdit = () => {
  editingCalendarId.value = null
  editForm.value = { id: '', name: '' }
}

const updateFilteredCalendar = async () => {
  if (!editForm.value.name.trim() || updating.value) return
  
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
      // Close inline editor immediately
      cancelInlineEdit()
      emit('navigate-to-calendar')
    } else {
      console.error('Failed to update calendar name - API returned false')
      // Keep inline editor open for retry
    }
  } catch (error) {
    console.error('Error updating calendar:', error)
    // Keep inline editor open for retry
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


const getGroupSubscriptionDisplay = (selectedRecurringEvents, selectedGroups) => {
  if (!props.hasGroups || !props.groups) {
    // Fallback for non-group calendars
    return getBasicRecurringEventDisplay(selectedRecurringEvents)
  }
  
  // Use the concise reactive breakdown
  return reactiveGroupBreakdown.value
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

// New helper methods for enhanced group display
const getGroupSelectionPercentage = (groupId) => {
  const selectedCount = getGroupSelectedCount(groupId)
  const totalCount = getGroupTotalCount(props.groups[groupId])
  return totalCount > 0 ? (selectedCount / totalCount) * 100 : 0
}

const getGroupSubscriptionBadgeClass = (groupId) => {
  const isSubscribed = props.subscribedGroups && props.subscribedGroups.has(groupId)
  const selectedCount = getGroupSelectedCount(groupId)
  const totalCount = getGroupTotalCount(props.groups[groupId])
  
  if (isSubscribed) {
    return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
  } else if (selectedCount === totalCount && totalCount > 0) {
    return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
  } else if (selectedCount > 0) {
    return 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
  } else {
    return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
  }
}

const getGroupSubscriptionDotClass = (groupId) => {
  const isSubscribed = props.subscribedGroups && props.subscribedGroups.has(groupId)
  const selectedCount = getGroupSelectedCount(groupId)
  const totalCount = getGroupTotalCount(props.groups[groupId])
  
  if (isSubscribed) {
    return 'bg-green-600 dark:bg-green-400'
  } else if (selectedCount === totalCount && totalCount > 0) {
    return 'bg-blue-600 dark:bg-blue-400'
  } else if (selectedCount > 0) {
    return 'bg-blue-500 dark:bg-blue-400'
  } else {
    return 'bg-gray-400 dark:bg-gray-500'
  }
}

const getProgressBarClass = (groupId) => {
  const selectedCount = getGroupSelectedCount(groupId)
  const totalCount = getGroupTotalCount(props.groups[groupId])
  
  if (selectedCount === totalCount && totalCount > 0) {
    return 'bg-gradient-to-r from-green-400 to-green-500'
  } else if (selectedCount > 0) {
    return 'bg-gradient-to-r from-blue-400 to-blue-500'
  } else {
    return 'bg-gray-300 dark:bg-gray-600'
  }
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
  
  // Build combined text with clearer language
  let text = ''
  if (groupCount > 0 && eventCount > 0) {
    // Both groups and recurring events
    text = `📊 ${groupCount} ${groupCount === 1 ? 'group' : 'groups'} & ${eventCount} recurring ${eventCount === 1 ? 'event' : 'events'}`
  } else if (groupCount > 0) {
    // Only groups
    text = `📊 ${groupCount} ${groupCount === 1 ? 'group' : 'groups'}`
  } else if (eventCount > 0) {
    // Only recurring events
    text = `📂 ${eventCount} recurring ${eventCount === 1 ? 'event' : 'events'}`
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
    text: text,
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