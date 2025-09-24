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
    <div v-if="loading" class="text-center py-12 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl border-2 border-blue-200 dark:border-blue-700 shadow-lg">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-6"></div>
      <div class="text-blue-800 dark:text-blue-200 font-semibold text-lg">{{ $t('common.loadingEvents') }}</div>
      <div class="text-blue-600 dark:text-blue-300 text-sm mt-2">{{ $t('common.pleaseWait') }}</div>
    </div>

    <!-- Main Content -->
    <template v-if="!loading && events.length > 0 && recurringEvents && Object.keys(recurringEvents).length > 0">
      <!-- Show Groups Interface Based on User Choice -->
      <EventGroupsSection
        v-if="shouldShowGroups"
        :has-groups="appStore.hasGroups"
        :groups="appStore.groups"
        :domain-id="props.domainContext?.id || 'default'"
        :show-groups-section="showGroupsSection"
        @selection-changed="handleGroupSelectionChanged"
        @switch-to-types="handleSwitchToTypes"
        @toggle-groups-section="showGroupsSection = !showGroupsSection"
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
        :has-groups="appStore.hasGroups"
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
        :has-groups="appStore.hasGroups"
        @navigate-to-calendar="navigateToCalendar"
        @load-filter="loadFilterIntoPage"
      />

      <PreviewEventsSection
        :selected-recurring-events="unifiedSelectedRecurringEvents"
        :sorted-preview-events="sortedPreviewEvents"
        :preview-group="previewGroup"
        :grouped-preview-events="groupedPreviewEvents"
        :all-events="events"
        :formatDateTime="formatDateTime"
        :formatDateRange="formatDateRange"
        :getRecurringEventKey="getRecurringEventKey"
        @update:preview-group="previewGroup = $event"
      />
    </template>

    <!-- Event types not loaded fallback -->
    <template v-else-if="!loading && events.length > 0 && recurringEvents && Object.keys(recurringEvents).length === 0">
      <div class="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-xl shadow-lg border-2 border-amber-200 dark:border-amber-700 text-center p-8">
        <div class="text-6xl mb-4">📂</div>
        <p class="text-amber-800 dark:text-amber-200 mb-3 font-semibold text-lg">
          {{ $t('calendar.loadingRecurringEventsOrNotFound') }}
        </p>
        <p class="text-amber-700 dark:text-amber-300 text-sm font-medium">
          {{ $t('calendar.loadingRecurringEventsDescription') }}
        </p>
      </div>
    </template>

    <!-- No Events Found -->
    <template v-else-if="!loading && events.length === 0">
      <div class="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-xl shadow-lg border-2 border-red-200 dark:border-red-700 text-center py-12 px-8">
        <div class="text-6xl mb-4">📅</div>
        <h3 class="text-2xl font-bold text-red-800 dark:text-red-200 mb-4">{{ $t('calendar.noEventsFound') }}</h3>
        <p class="text-red-700 dark:text-red-300 mb-6 font-medium">{{ $t('calendar.noEventsFoundDescription') }}</p>
        <button @click="navigateHome" class="px-8 py-3.5 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white rounded-lg font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-lg hover:shadow-xl">
          {{ $t('navigation.backToCalendars') }}
        </button>
      </div>
    </template>

    <!-- Event Types not loaded fallback -->
    <template v-else-if="!loading && !recurringEvents">
      <div class="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-xl shadow-lg border-2 border-red-200 dark:border-red-700 text-center py-12 px-8">
        <div class="text-6xl mb-4">📅</div>
        <h3 class="text-2xl font-bold text-red-800 dark:text-red-200 mb-4">{{ $t('calendar.noEventsFound') }}</h3>
        <p class="text-red-700 dark:text-red-300 mb-6 font-medium">{{ $t('calendar.noEventsFoundDescription') }}</p>
        <button @click="navigateHome" class="px-8 py-3.5 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white rounded-lg font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-lg hover:shadow-xl">
          {{ $t('navigation.backToCalendars') }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import { useHTTP } from '../composables/useHTTP'
import { useCalendar } from '../composables/useCalendar'
import { useSelection } from '../composables/useSelection'
import { API_ENDPOINTS } from '../constants/api'
import axios from 'axios'
import {
  HeaderSection,
  RecurringEventsCardsSection,
  PreviewEventsSection
} from '../components/calendar'
import EventGroupsSection from '../components/calendar/EventGroupsSection.vue'
import FilteredCalendarSection from '../components/FilteredCalendarSection.vue'

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
  previewGroup,
  recurringEventsSortedByCount,
  mainRecurringEvents,
  singleRecurringEvents,
  selectedRecurringEventsCount,
  sortedPreviewEvents,
  groupedPreviewEvents,
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
  
  // If user chose groups but no groups available, fallback to types
  if (viewMode.value === 'groups' && !appStore.hasGroups) return false
  
  // Show groups if available and user chose groups
  return appStore.hasGroups
})

const shouldShowTypes = computed(() => {
  return !shouldShowGroups.value
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
    if (props.domainContext && calendarId.startsWith('cal_')) {
      // Domain calendars are system-managed - create reference without API dependency
      selectedCalendar.value = {
        id: calendarId,
        name: props.domainContext.name || `Domain Calendar (${calendarId})`,
        url: props.domainContext.ical_url || '',
        user_id: 'system', // Mark as system-managed, not domain user
        source: 'domain',
        system_managed: true // Explicit flag for domain calendars
      }
    } else {
      // For user calendars, load from API/localStorage as normal
      if (appStore.calendars.length === 0) {
        await appStore.fetchCalendars()
      }
      
      const calendar = appStore.calendars.find(c => c.id === calendarId)
      if (calendar) {
        selectedCalendar.value = calendar
      } else {
        console.error(`❌ User calendar ${calendarId} not found in available calendars`)
        setError(`Calendar ${calendarId} not found`)
        return
      }
    }
    
    // Simplified: Load groups data directly - no conversion needed
    console.log('🔄 Loading groups data...')
    const isDomainCalendar = props.domainContext || calendarId.startsWith('cal_domain_')
    let domainName = null
    
    if (isDomainCalendar && props.domainContext?.domain_key) {
      domainName = props.domainContext.domain_key
    } else if (isDomainCalendar && calendarId.startsWith('cal_domain_')) {
      domainName = calendarId.replace('cal_domain_', '')
    }

    // Load groups data first - this contains all events
    if (isDomainCalendar && domainName) {
      await appStore.loadDomainGroups(domainName)
    } else {
      await appStore.loadCalendarGroups(calendarId)
    }
    
    console.log('✅ Groups loaded:', {
      hasGroups: appStore.hasGroups,
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
        console.warn('⚠️ No groups data available')
        recurringEvents.value = {}
        events.value = []
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
      console.log('🐛 DEBUG: hasGroups reactivity check:', {
        hasGroupsValue: appStore.hasGroups,
        hasGroupsType: typeof appStore.hasGroups
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
  // Clear current selection
  clearAllRecurringEvents()
  
  
  // Select the event types from the filter
  filterData.recurringEvents.forEach(recurringEventName => {
    toggleRecurringEvent(recurringEventName)
  })
  
  console.log(`Loaded filter "${filterData.calendarName}" with ${filterData.recurringEvents.length} recurring events`)
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
  console.log('🚀 CalendarView mounted with public-first access - DEBUG MODE ACTIVE')
  
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
})
</script>