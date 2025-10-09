<template>
  <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 overflow-x-hidden dark:bg-gray-900 min-h-screen">
    <HeaderSection 
      :selected-calendar="selectedCalendar"
      :error="error"
      :domain-context="props.domainContext"
      @navigate-home="navigateHome"
      @clear-error="clearError"
    />

    <!-- Loading State -->
    <div v-if="loading" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-4">
      <!-- Header with gradient background matching admin cards -->
      <div class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center gap-3">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-3 border-blue-600 border-t-transparent"></div>
          <div class="flex-1">
            <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-gray-100 mb-1">
              📊 {{ $t('common.loadingEvents') }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ $t('common.pleaseWait') }}
            </p>
          </div>
        </div>
      </div>
      
      <!-- Content area -->
      <div class="p-6 text-center">
        <div class="text-6xl mb-4">📅</div>
        <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
          Organizing your calendar events...
        </p>
      </div>
    </div>

    <!-- Main Content -->
    <template v-if="!loading && events.length > 0 && recurringEvents && Object.keys(recurringEvents).length > 0">
      <!-- Show Groups Interface Based on User Choice -->
      <EventGroupsSection
        v-if="shouldShowGroups"
        :has-groups="appStore.hasCustomGroups"
        :groups="appStore.groups"
        :domain-id="props.domainContext?.id || 'default'"
        :show-groups-section="showGroupsSection"
        @selection-changed="handleGroupSelectionChanged"
        @switch-to-types="handleSwitchToTypes"
        @toggle-groups-section="showGroupsSection = !showGroupsSection"
      />

      <!-- Admin Setup Card - shown when no custom groups exist and user has admin access -->
      <AdminSetupCard
        :domain-context="props.domainContext"
        :has-custom-groups="hasRealCustomGroups"
      />

      <!-- Show Event Types Interface Based on User Choice -->
      <RecurringEventsCardsSection
        v-if="shouldShowTypes"
        :recurring-events="mainRecurringEvents"
        :main-recurring-events="mainRecurringEvents"
        :single-recurring-events="singleRecurringEvents"
        :all-recurring-events="recurringEventsSortedByCount"
        :selected-recurring-events="unifiedSelectedRecurringEvents"
        :expanded-recurring-events="expandedRecurringEvents"
        :show-single-events="showSingleEvents"
        :show-recurring-events-section="showRecurringEventsSection"
        :show-selected-only="showSelectedOnly"
        :search-term="recurringEventSearch"
        :has-groups="appStore.hasCustomGroups"
        :summary-text="getGroupBreakdownSummary()"
        :formatDateTime="formatDateTime"
        :formatDateRange="formatDateRange"
        @clear-all="handleClearAllEvents"
        @select-all="handleSelectAllEvents"
        @update:search-term="recurringEventSearch = $event"
        @toggle-recurring-event="unifiedToggleRecurringEvent"
        @toggle-expansion="toggleRecurringEventExpansion"
        @toggle-singles-visibility="showSingleEvents = !showSingleEvents"
        @select-all-singles="selectAllSingleEvents"
        @clear-all-singles="clearAllSingleEvents"
        @toggle-recurring-events-section="showRecurringEventsSection = !showRecurringEventsSection"
        @toggle-selected-only="showSelectedOnly = !showSelectedOnly"
        @subscribe-all-groups="handleSubscribeAllGroups"
        @unsubscribe-all-groups="handleUnsubscribeAllGroups"
        @switch-to-groups="handleSwitchToGroups"
      />

      <!-- Filtered Calendar Section -->
      <!-- Always show filtered calendars section - independent of current calendar's events/event types -->
      <!-- This manages global filtered calendars that may exist from any source calendar -->
      <FilteredCalendarSection
        :selected-calendar="selectedCalendar"
        :selected-recurring-events="unifiedSelectedRecurringEvents"
        :selected-groups="selectedGroups"
        :subscribed-groups="subscribedGroups"
        :main-recurring-events="mainRecurringEvents"
        :single-recurring-events="singleRecurringEvents"
        :groups="appStore.groups"
        :has-groups="appStore.hasCustomGroups"
        @navigate-to-calendar="navigateToCalendar"
        @load-filter="loadFilterIntoPage"
      />

      <PreviewEventsSection
        :get-recurring-event-key="getRecurringEventKey"
      />
    </template>

    <!-- Event types not loaded fallback -->
    <template v-else-if="!loading && events.length > 0 && recurringEvents && Object.keys(recurringEvents).length === 0">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-4">
        <!-- Header with gradient background matching admin cards -->
        <div class="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-amber-200 dark:border-amber-700">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
              <span class="text-amber-600 dark:text-amber-400 text-xl">📂</span>
            </div>
            <div class="flex-1">
              <h3 class="text-lg sm:text-xl font-bold text-amber-800 dark:text-amber-200 mb-1">
                📊 {{ $t('calendar.loadingRecurringEventsOrNotFound') }}
              </h3>
              <p class="text-sm text-amber-600 dark:text-amber-300">
                Processing event categories
              </p>
            </div>
          </div>
        </div>
        
        <!-- Content area -->
        <div class="p-6 text-center">
          <div class="text-6xl mb-4">📅</div>
          <p class="text-amber-700 dark:text-amber-300 leading-relaxed">
            {{ $t('calendar.loadingRecurringEventsDescription') }}
          </p>
        </div>
      </div>
    </template>

    <!-- No Events Found -->
    <template v-else-if="!loading && events.length === 0">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-4">
        <!-- Header with gradient background matching admin cards -->
        <div class="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-red-200 dark:border-red-700">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
              <span class="text-red-600 dark:text-red-400 text-xl">📅</span>
            </div>
            <div class="flex-1">
              <h3 class="text-lg sm:text-xl font-bold text-red-800 dark:text-red-200 mb-1">
                📊 {{ $t('calendar.noEventsFound') }}
              </h3>
              <p class="text-sm text-red-600 dark:text-red-300">
                Calendar appears to be empty
              </p>
            </div>
          </div>
        </div>
        
        <!-- Content area -->
        <div class="p-6 text-center">
          <div class="text-6xl mb-6">🗂️</div>
          <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800 mb-6">
            <p class="text-red-700 dark:text-red-300 leading-relaxed">{{ $t('calendar.noEventsFoundDescription') }}</p>
          </div>
          
          <!-- Action Button -->
          <button @click="navigateHome" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-sm hover:shadow-md">
            <span class="text-lg">🏠</span>
            {{ $t('navigation.backToCalendars') }}
          </button>
        </div>
      </div>
    </template>

    <!-- Event Types not loaded fallback -->
    <template v-else-if="!loading && !recurringEvents">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-4">
        <!-- Header with gradient background matching admin cards -->
        <div class="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-red-200 dark:border-red-700">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
              <span class="text-red-600 dark:text-red-400 text-xl">📅</span>
            </div>
            <div class="flex-1">
              <h3 class="text-lg sm:text-xl font-bold text-red-800 dark:text-red-200 mb-1">
                📊 {{ $t('calendar.noEventsFound') }}
              </h3>
              <p class="text-sm text-red-600 dark:text-red-300">
                Unable to load event data
              </p>
            </div>
          </div>
        </div>
        
        <!-- Content area -->
        <div class="p-6 text-center">
          <div class="text-6xl mb-6">🗂️</div>
          <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800 mb-6">
            <p class="text-red-700 dark:text-red-300 leading-relaxed">{{ $t('calendar.noEventsFoundDescription') }}</p>
          </div>
          
          <!-- Action Button -->
          <button @click="navigateHome" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-sm hover:shadow-md">
            <span class="text-lg">🏠</span>
            {{ $t('navigation.backToCalendars') }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, defineAsyncComponent } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useHTTP } from '../composables/useHTTP'
import { useCalendar } from '../composables/useCalendar'
import { useSelection } from '../composables/useSelection'
import { API_ENDPOINTS } from '../constants/api'
import axios from 'axios'
import {
  HeaderSection,
  RecurringEventsCardsSection
} from '../components/calendar'
import EventGroupsSection from '../components/calendar/EventGroupsSection.vue'
import AdminSetupCard from '../components/calendar/AdminSetupCard.vue'

// Lazy load heavy components for better initial page load
const PreviewEventsSection = defineAsyncComponent(() =>
  import('../components/preview/PreviewEventsSection.vue')
)
const FilteredCalendarSection = defineAsyncComponent(() =>
  import('../components/FilteredCalendarSection.vue')
)

const appStore = useAppStore()
const router = useRouter()
const route = useRoute()
const { loading, error, clearError, setError } = useHTTP()

// Local reactive data 
const events = ref([])
const recurringEvents = ref({})
const selectedCalendar = ref(null)
const selectedGroups = ref([])

// View mode state with localStorage persistence
const viewMode = ref('groups') // 'groups' | 'types'

// Groups data - from store (keep reactive by not destructuring)
// Note: Vue 3 + Pinia - destructuring breaks reactivity, use store.property instead

// Define props first
const props = defineProps({
  id: String,
  domainContext: {
    type: Object,
    default: null
  }
})

// Use calendar composable with local data and calendar ID for persistence
const {
  selectedRecurringEvents,
  expandedRecurringEvents,
  showSingleEvents,
  showRecurringEventsSection,
  showGroupsSection,
  showSelectedOnly,
  recurringEventSearch,
  recurringEventsSortedByCount,
  mainRecurringEvents,
  singleRecurringEvents,
  selectedRecurringEventsCount,
  getRecurringEventKey,
  formatDateTime,
  formatDateRange,
  toggleRecurringEvent,
  toggleRecurringEventExpansion,
  selectAllRecurringEvents,
  clearAllRecurringEvents,
  selectAllSingleEvents,
  clearAllSingleEvents,
  updateCalendarId,
  // No preferences loading needed
} = useCalendar(events, recurringEvents, props.id)

// Get unified event selection system (SINGLE SOURCE OF TRUTH)
const { 
  subscribeToGroup, 
  unsubscribeFromGroup, 
  subscribedGroups,
  selectedRecurringEvents: unifiedSelectedRecurringEvents,
  toggleRecurringEvent: unifiedToggleRecurringEvent,
  selectRecurringEvents,
  clearSelection,
  subscribeAndSelectAllGroups,
  selectAllGroups,
  unsubscribeFromAllGroups,
  getGroupBreakdownSummary
} = useSelection()

// View mode localStorage persistence functions
const VIEW_MODE_STORAGE_KEY = 'ical-viewer-view-mode'

const loadViewModePreference = () => {
  try {
    const saved = localStorage.getItem(VIEW_MODE_STORAGE_KEY)
    return saved && ['groups', 'types'].includes(saved) ? saved : 'groups'
  } catch (error) {
    console.warn('Failed to load view mode preference:', error)
    return 'groups'
  }
}

const saveViewModePreference = (mode) => {
  try {
    localStorage.setItem(VIEW_MODE_STORAGE_KEY, mode)
  } catch (error) {
    console.warn('Failed to save view mode preference:', error)
  }
}

// Initialize view mode from localStorage
viewMode.value = loadViewModePreference()

// Computed properties for view mode logic
const shouldShowGroups = computed(() => {
  // If user explicitly chose types, show types
  if (viewMode.value === 'types') return false

  // If user chose groups but no CUSTOM groups available, fallback to types
  if (viewMode.value === 'groups' && !appStore.hasCustomGroups) return false

  // Show groups if CUSTOM groups available and user chose groups
  return appStore.hasCustomGroups
})

const shouldShowTypes = computed(() => {
  return !shouldShowGroups.value
})

// Check if there are custom (non-auto) groups
// (use store's computed property instead of calling utility directly)
const hasRealCustomGroups = computed(() => {
  return appStore.hasCustomGroups
})



// Handle view mode changes
const handleViewModeChange = (newMode) => {
  console.log('🔄 ViewMode change requested:', newMode, 'current:', viewMode.value)
  viewMode.value = newMode
  saveViewModePreference(newMode)
  console.log('✅ ViewMode updated to:', viewMode.value)
}

// Specific switch handlers with debugging
const handleSwitchToTypes = () => {
  console.log('🔄 switch-to-types event fired')
  handleViewModeChange('types')
}

const handleSwitchToGroups = () => {
  console.log('🔄 switch-to-groups event fired') 
  handleViewModeChange('groups')
}

// Simple, direct data loading with proper error handling
const loadCalendarData = async (calendarId) => {
  console.log('🔄 Loading calendar data for:', calendarId)
  clearError() // Use API composable's error clearing
  
  console.log('🔄 Initial state:', {
    loading: loading.value,
    eventsLength: events.value.length,
    recurringEventsKeys: recurringEvents.value ? Object.keys(recurringEvents.value).length : 'null'
  })
  
  try {
    
    // For domain calendars, create a system-managed calendar reference
    // Domain calendars are NOT user calendars and should not be mixed with user calendar lists
    if (String(calendarId).startsWith('cal_domain_') || (props.domainContext && String(calendarId).startsWith('cal_'))) {
      // Domain calendars are system-managed - create reference without API dependency
      selectedCalendar.value = {
        id: calendarId,
        name: props.domainContext?.name || `Domain Calendar (${calendarId})`,
        url: props.domainContext?.ical_url || '',
        user_id: 'system', // Mark as system-managed, not domain user
        source: 'domain',
        system_managed: true // Explicit flag for domain calendars
      }
    } else {
      // For user calendars, load from API/localStorage as normal
      if (appStore.calendars.length === 0) {
        await appStore.fetchCalendars()
      }
      
      // Convert calendarId to number for database lookup since IDs are numeric
      const numericCalendarId = typeof calendarId === 'string' ? parseInt(calendarId, 10) : calendarId
      
      // Validate that we have a valid numeric ID
      if (isNaN(numericCalendarId)) {
        console.error(`❌ Invalid calendar ID: ${calendarId}`)
        setError(`Invalid calendar ID: ${calendarId}`)
        return
      }
      
      const calendar = appStore.calendars.find(c => c.id === numericCalendarId)
      if (calendar) {
        selectedCalendar.value = calendar
      } else {
        // More helpful error message
        const availableIds = appStore.calendars.map(c => c.id).join(', ')
        console.error(`❌ Calendar ${numericCalendarId} not found. Available calendars: ${availableIds}`)
        setError(`Calendar not found. The calendar may have been deleted or you may not have access to it.`)
        return
      }
    }
    
    // Simplified: Load groups data directly - no conversion needed
    console.log('🔄 Loading groups data...')
    const isDomainCalendar = props.domainContext || String(calendarId).startsWith('cal_domain_')
    let domainName = null
    
    if (isDomainCalendar && props.domainContext?.domain_key) {
      domainName = props.domainContext.domain_key
    } else if (isDomainCalendar && String(calendarId).startsWith('cal_domain_')) {
      domainName = String(calendarId).replace('cal_domain_', '')
    }

    // Load groups data first - this contains all events
    if (isDomainCalendar && domainName) {
      await appStore.loadDomainGroups(domainName)
    } else {
      // Use numeric calendar ID for API calls
      const numericCalendarId = typeof calendarId === 'string' ? parseInt(calendarId, 10) : calendarId
      await appStore.loadCalendarGroups(numericCalendarId)
    }
    
    console.log('✅ Groups loaded:', {
      isDomainCalendar: appStore.isDomainCalendar,
      hasCustomGroups: appStore.hasCustomGroups,
      groupsCount: appStore.groups ? Object.keys(appStore.groups).length : 0
    })

    // Extract events and recurringEvents from loaded groups - no API conversion needed
    const extractedRecurringEvents = {}
    const allEvents = []
    
    try {
      // Extract from groups loaded into appStore
      if (appStore.groups && Object.keys(appStore.groups).length > 0) {
        Object.values(appStore.groups).forEach(group => {
          if (group.recurring_events) {
            group.recurring_events.forEach(recurringEvent => {
              // Extract events from this recurring event
              const actualEvents = recurringEvent.events?.events || recurringEvent.events || []
              if (Array.isArray(actualEvents)) {
                allEvents.push(...actualEvents)
                
                // Create recurringEvent structure for compatibility
                extractedRecurringEvents[recurringEvent.title] = {
                  count: recurringEvent.event_count || actualEvents.length,
                  events: actualEvents
                }
              }
            })
          }
        })
        
        recurringEvents.value = extractedRecurringEvents
        events.value = allEvents
        
        console.log('✅ Data extracted from groups:', {
          recurringEventsCount: Object.keys(extractedRecurringEvents).length,
          eventsCount: allEvents.length,
          recurringEventNames: Object.keys(extractedRecurringEvents)
        })
      } else {
        // No groups - this is a personal calendar, extract from appStore directly
        console.log('📊 Personal calendar - checking appStore data:', {
          hasEvents: !!appStore.events,
          eventsLength: appStore.events?.length || 0,
          hasRecurringEvents: !!appStore.recurringEvents,
          recurringEventsKeys: appStore.recurringEvents ? Object.keys(appStore.recurringEvents).length : 0,
          eventsType: Array.isArray(appStore.events) ? 'array' : typeof appStore.events,
          recurringEventsType: typeof appStore.recurringEvents
        })

        // Validate and extract personal calendar data with proper checks
        const hasValidEvents = appStore.events && Array.isArray(appStore.events) && appStore.events.length > 0
        const hasValidRecurringEvents = appStore.recurringEvents &&
                                        typeof appStore.recurringEvents === 'object' &&
                                        Object.keys(appStore.recurringEvents).length > 0

        if (hasValidEvents && hasValidRecurringEvents) {
          // Create COPIES of the data to avoid reference issues
          events.value = [...appStore.events]
          recurringEvents.value = { ...appStore.recurringEvents }

          console.log('✅ Personal calendar data extracted:', {
            eventsCount: events.value.length,
            recurringEventsCount: Object.keys(recurringEvents.value).length,
            recurringEventNames: Object.keys(recurringEvents.value).slice(0, 5),
            firstEvent: events.value[0]?.title,
            firstEventStructure: events.value[0] ? Object.keys(events.value[0]) : [],
            firstEventDates: events.value[0] ? {
              start: events.value[0].start,
              dtstart: events.value[0].dtstart,
              end: events.value[0].end,
              dtend: events.value[0].dtend
            } : null
          })
        } else {
          // No valid data - clear and log warning
          recurringEvents.value = {}
          events.value = []

          console.warn('⚠️ Personal calendar: No valid events data:', {
            hasValidEvents,
            hasValidRecurringEvents,
            rawEventsLength: appStore.events?.length || 0,
            rawRecurringEventsKeys: appStore.recurringEvents ? Object.keys(appStore.recurringEvents).length : 0
          })
        }
      }
    } catch (extractError) {
      console.error('❌ Error extracting data from groups:', extractError)
      throw extractError
    }
      
      // Debug the conditional rendering requirements
      console.log('🎯 Conditional rendering check:', {
        loading: loading.value,
        eventsLength: events.value.length,
        recurringEventsExists: !!recurringEvents.value,
        recurringEventsKeysLength: Object.keys(recurringEvents.value).length,
        shouldShow: !loading.value && events.value.length > 0 && recurringEvents.value && Object.keys(recurringEvents.value).length > 0
      })

      // Groups already loaded above
      
      // Debug: Force re-render check
      console.log('🐛 DEBUG: Calendar type reactivity check:', {
        isDomainCalendar: appStore.isDomainCalendar,
        hasCustomGroups: appStore.hasCustomGroups,
        groupsCount: Object.keys(appStore.groups || {}).length
      })
      
    console.log('✅ Calendar data loaded successfully')
  } catch (error) {
    console.error('❌ Failed to load calendar data:', error)
    setError(error.message || 'Failed to load calendar data')
  }
  
  console.log('🏁 Loading complete. Final state:', {
    loading: loading.value,
    eventsLength: events.value.length,
    recurringEventsKeys: recurringEvents.value ? Object.keys(recurringEvents.value).length : 'null',
    shouldShow: !loading.value && events.value.length > 0 && recurringEvents.value && Object.keys(recurringEvents.value).length > 0
  })
}

// clearError is now provided by API composable

const navigateHome = () => {
  router.push('/home')
}

const navigateToCalendar = () => {
  // Stay on current calendar view - this is the calendar view, so no navigation needed
  // The function exists to fulfill the event handler requirement from FilteredCalendarSection
}

// Event assignment is now handled automatically by backend auto-grouping
// No manual assignment needed - all events are automatically grouped

const loadFilterIntoPage = (filterData) => {
  // Clear current selection using unified system
  clearSelection()
  
  // Handle group subscriptions first
  if (filterData.groups && filterData.groups.length > 0) {
    filterData.groups.forEach(groupId => {
      // Convert string groupId to ensure compatibility
      const groupIdStr = groupId.toString()
      subscribeToGroup(groupIdStr)
    })
    console.log(`Loaded filter "${filterData.calendarName}" with ${filterData.groups.length} subscribed groups`)
  }
  
  // Handle individual recurring event selections
  if (filterData.recurringEvents && filterData.recurringEvents.length > 0) {
    filterData.recurringEvents.forEach(recurringEventName => {
      unifiedToggleRecurringEvent(recurringEventName)
    })
    console.log(`Loaded filter "${filterData.calendarName}" with ${filterData.recurringEvents.length} individual recurring events`)
  }
  
  console.log(`Loaded filter "${filterData.calendarName}" - Groups: ${filterData.groups?.length || 0}, Events: ${filterData.recurringEvents?.length || 0}`)
}

// Handle selection changes from the new multi-level selection system (old complex)
const handleSelectionChanged = (selection) => {
  console.log('📊 Selection changed:', selection)
  
  // Resolve hierarchical group selections into a flat list of event types
  const resolvedRecurringEvents = resolveGroupSelectionsToRecurringEvents(selection)
  console.log('📋 Resolved recurring events:', resolvedRecurringEvents)
  
  // Update the selectedRecurringEvents to integrate with existing filter system
  selectedRecurringEvents.value = resolvedRecurringEvents
}

// Handle selection changes from the dual selection system
const handleGroupSelectionChanged = (selectionData) => {
  console.log('🎯 Unified selection changed:', selectionData)
  
  // Extract data from the unified selection format
  const { groups, recurringEvents, events, subscribedGroups } = selectionData
  
  console.log('🔧 Processing unified selection:', {
    subscribedGroups: subscribedGroups,
    groups: groups,
    recurringEvents: recurringEvents,
    events: events
  })
  
  // Store legacy selectedGroups for compatibility (will be removed later)
  selectedGroups.value = groups || []
  
  // Note: No need to manually update selectedRecurringEvents here anymore
  // The unified system handles this automatically through useEventSelection
  // The Events and Groups views now share the same selection state
  
  console.log('✅ Unified selection system updated')
}

// Handle selection changes from the enhanced selection system  
const handleSimpleSelectionChanged = (selectionData) => {
  console.log('📊 Enhanced selection changed:', selectionData)
  
  if (selectionData.mode === 'enhanced') {
    // Handle enhanced selection data with both groups and individual event types
    console.log('🔧 Processing enhanced selection:', {
      recurringEvents: selectionData.selectedRecurringEvents,
      groups: selectionData.selectedGroups
    })
    
    // Store both selected groups and individual event types
    selectedRecurringEvents.value = selectionData.selectedRecurringEvents
    selectedGroups.value = selectionData.selectedGroups
  } else {
    // Legacy support: direct array of event types
    selectedRecurringEvents.value = selectionData
    selectedGroups.value = []
  }
}

// Helper function to resolve hierarchical group selections into event types
const resolveGroupSelectionsToRecurringEvents = (selection) => {
  const recurringEvents = new Set()
  
  // Get all event types from explicit event type selections
  selection.recurringEvents.forEach(recurringEvent => {
    recurringEvents.add(recurringEvent)
  })
  
  // Get all event types from selected groups (including nested groups)
  if (appStore.groups) {
    selection.groups.forEach(groupId => {
      const recurringEventsFromGroup = getRecurringEventsFromGroup(groupId, appStore.groups)
      recurringEventsFromGroup.forEach(recurringEvent => {
        recurringEvents.add(recurringEvent)
      })
    })
  }
  
  // Add individual events (these are already event-specific, not type-specific)
  // Individual events will be handled differently by the filter system
  
  return Array.from(recurringEvents)
}

// Recursive helper to extract all event types from a group and its children
const getRecurringEventsFromGroup = (groupId, groups) => {
  const recurringEvents = new Set()
  
  // Find the group
  const group = findGroupById(groupId, groups)
  if (!group) return recurringEvents
  
  // Add direct recurring events from this group
  if (group.recurring_events) {
    group.recurring_events.forEach(recurringEvent => {
      recurringEvents.add(recurringEvent.title)
    })
  }
  
  // Recursively add recurring events from children
  if (group.children) {
    group.children.forEach(child => {
      const childRecurringEvents = getRecurringEventsFromGroup(child.id, groups)
      childRecurringEvents.forEach(recurringEvent => {
        recurringEvents.add(recurringEvent)
      })
    })
  }
  
  return recurringEvents
}

// Helper to find a group by ID in the hierarchical structure
const findGroupById = (groupId, groups) => {
  // Search in top-level groups
  for (const group of Object.values(groups)) {
    if (group.id === groupId) return group
    
    // Search in children recursively
    const found = findGroupInChildren(group.children || [], groupId)
    if (found) return found
  }
  
  return null
}

// Recursive helper for finding groups in children
const findGroupInChildren = (children, groupId) => {
  for (const child of children) {
    if (child.id === groupId) return child
    
    if (child.children) {
      const found = findGroupInChildren(child.children, groupId)
      if (found) return found
    }
  }
  
  return null
}

// Unified event selection handlers
const handleSelectAllEvents = () => {
  // Get ALL event types (both recurring and unique) for unified selection
  const allEventTitles = [
    ...(mainRecurringEvents.value?.map(event => event.name) || []),
    ...(singleRecurringEvents.value?.map(event => event.name) || [])
  ]
  
  // Use unified selection system for all events consistently
  if (allEventTitles.length > 0) {
    selectRecurringEvents(allEventTitles)
  }
}

const handleClearAllEvents = () => {
  // Clear all selections using the unified system
  clearSelection()
  
  // Auto-deactivate "Show Selected Only" when no events are selected
  if (showSelectedOnly.value) {
    showSelectedOnly.value = false
  }
}

// Event View group action handlers - subscription-only (no selection changes)
const handleSubscribeAllGroups = () => {
  // Event View: Subscribe to all groups only, don't change selections
  selectAllGroups()
}

const handleUnsubscribeAllGroups = () => {
  // Event View: Unsubscribe from all groups only, don't change selections
  unsubscribeFromAllGroups()
}

onMounted(async () => {
  if (import.meta.env.DEV) {
    console.log('🚀 CalendarView mounted with public-first access - DEBUG MODE')
  }
  
  // Initialize app state (loads calendars from localStorage)
  appStore.initializeApp()

  const calendarId = props.id || route.params.id
  console.log('Calendar ID from route:', calendarId)
  
  if (calendarId) {
    await loadCalendarData(calendarId)
    // Update the calendar ID in the composable for proper filter persistence
    updateCalendarId(calendarId)
  }
})

// Watch for route changes to update calendar ID for filter persistence
watch(() => props.id || route.params.id, (newCalendarId, oldCalendarId) => {
  if (newCalendarId && newCalendarId !== oldCalendarId) {
    console.log('🔄 Route changed, updating calendar ID:', newCalendarId)
    updateCalendarId(newCalendarId)
    loadCalendarData(newCalendarId)
  }
})

// Watch for selection changes and auto-deactivate "Show Selected Only" when no events are selected
watch(() => unifiedSelectedRecurringEvents.value.length, (newLength) => {
  if (newLength === 0 && showSelectedOnly.value) {
    console.log('🔄 Auto-deactivating "Show Selected Only" - no events selected')
    showSelectedOnly.value = false
  }
}, { immediate: true }) // Run immediately to handle page load state

// Additional safety check on component mount for any timing issues
watch([() => unifiedSelectedRecurringEvents.value, () => showSelectedOnly.value], ([selection, showSelected]) => {
  // If showSelectedOnly is active but no events are selected, deactivate it
  if (showSelected && selection.length === 0) {
    console.log('🔄 Safety check: Auto-deactivating "Show Selected Only" - no events selected on mount')
    showSelectedOnly.value = false
  }
}, { immediate: true })

// Auto-expand unique events section when searching and matches are found
watch(() => recurringEventSearch.value, (newSearchTerm) => {
  // Only auto-expand if search term is not empty
  if (newSearchTerm && newSearchTerm.trim()) {
    const searchLower = newSearchTerm.toLowerCase()

    // Check if any single/unique events match the search
    const hasUniqueMatches = singleRecurringEvents.value.some(event =>
      event && event.name && event.name.toLowerCase().includes(searchLower)
    )

    // Auto-expand if there are unique event matches and section is currently collapsed
    if (hasUniqueMatches && !showSingleEvents.value) {
      showSingleEvents.value = true
    }
  }
  // Note: We intentionally don't auto-collapse when search is cleared
  // to avoid jarring UX - let users manually collapse if desired
}, { immediate: false })
</script>