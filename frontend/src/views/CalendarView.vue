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
    <template v-if="!loading && events.length > 0 && eventTypes && Object.keys(eventTypes).length > 0">
      <!-- Show Improved Groups Interface if Domain has Groups -->
      <EventGroupsSection
        v-if="appStore.hasGroups"
        :has-groups="appStore.hasGroups"
        :groups="appStore.groups"
        :ungrouped-event-types="appStore.ungroupedEventTypes"
        :ungrouped-recurring-event-types="appStore.ungroupedRecurringEventTypes"
        :ungrouped-unique-event-types="appStore.ungroupedUniqueEventTypes"
        :filter-mode="filterMode"
        :domain-id="props.domainContext?.id || 'default'"
        @selection-changed="handleGroupSelectionChanged"
        @switch-filter-mode="switchFilterMode"
      />
      
      <!-- Fallback to Event Types Interface if No Groups -->
      <EventTypeCardsSection
        v-else
        :event-types="mainEventTypes"
        :main-event-types="mainEventTypes"
        :single-event-types="singleEventTypes"
        :all-event-types="eventTypesSortedByCount"
        :selected-event-types="selectedEventTypes"
        :expanded-event-types="expandedEventTypes"
        :show-single-events="showSingleEvents"
        :show-event-types-section="showEventTypesSection"
        :show-selected-only="showSelectedOnly"
        :search-term="eventTypeSearch"
        :filter-mode="filterMode"
        :formatDateTime="formatDateTime"
        :formatDateRange="formatDateRange"
        @clear-all="clearAllEventTypes"
        @select-all="selectAllEventTypes"
        @update:search-term="eventTypeSearch = $event"
        @toggle-event-type="toggleEventType"
        @toggle-expansion="toggleEventTypeExpansion"
        @toggle-singles-visibility="showSingleEvents = !showSingleEvents"
        @select-all-singles="selectAllSingleEvents"
        @clear-all-singles="clearAllSingleEvents"
        @toggle-event-types-section="showEventTypesSection = !showEventTypesSection"
        @toggle-selected-only="showSelectedOnly = !showSelectedOnly"
        @switch-filter-mode="switchFilterMode"
      />

      <!-- Filtered Calendar Section -->
      <!-- Always show filtered calendars section - independent of current calendar's events/event types -->
      <!-- This manages global filtered calendars that may exist from any source calendar -->
      <FilteredCalendarSection
        :selected-calendar="selectedCalendar"
        :selected-event-types="selectedEventTypes"
        :selected-groups="selectedGroups"
        :filter-mode="filterMode"
        :main-event-types="mainEventTypes"
        :single-event-types="singleEventTypes"
        :groups="appStore.groups"
        :has-groups="appStore.hasGroups"
        @navigate-to-calendar="navigateToCalendar"
        @load-filter="loadFilterIntoPage"
      />

      <PreviewEventsSection
        :selected-event-types="selectedEventTypes"
        :sorted-preview-events="sortedPreviewEvents"
        :preview-group="previewGroup"
        :grouped-preview-events="groupedPreviewEvents"
        :filter-mode="filterMode"
        :all-events="events"
        :formatDateTime="formatDateTime"
        :formatDateRange="formatDateRange"
        :getEventTypeKey="getEventTypeKey"
        @update:preview-group="previewGroup = $event"
      />
    </template>

    <!-- Event types not loaded fallback -->
    <template v-else-if="!loading && events.length > 0 && eventTypes && Object.keys(eventTypes).length === 0">
      <div class="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-xl shadow-lg border-2 border-amber-200 dark:border-amber-700 text-center p-8">
        <div class="text-6xl mb-4">📂</div>
        <p class="text-amber-800 dark:text-amber-200 mb-3 font-semibold text-lg">
          {{ $t('calendar.loadingEventTypesOrNotFound') }}
        </p>
        <p class="text-amber-700 dark:text-amber-300 text-sm font-medium">
          {{ $t('calendar.loadingEventTypesDescription') }}
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
    <template v-else-if="!loading && !eventTypes">
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
import { useAPI } from '../composables/useAPI'
import { useCalendar } from '../composables/useCalendar'
import axios from 'axios'
import {
  HeaderSection,
  EventTypeCardsSection,
  PreviewEventsSection
} from '../components/calendar'
import EventGroupsSection from '../components/calendar/EventGroupsSection.vue'
import FilteredCalendarSection from '../components/FilteredCalendarSection.vue'

const appStore = useAppStore()
const router = useRouter()
const route = useRoute()
const api = useAPI()

// Local reactive data - much simpler than store delegation
const loading = ref(false)
const error = ref(null)
const events = ref([])
const eventTypes = ref({})
const selectedCalendar = ref(null)
const selectedGroups = ref([])

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
  selectedEventTypes,
  expandedEventTypes,
  showSingleEvents,
  showEventTypesSection,
  showSelectedOnly,
  eventTypeSearch,
  filterMode,
  previewGroup,
  eventTypesSortedByCount,
  mainEventTypes,
  singleEventTypes,
  selectedEventTypesCount,
  sortedPreviewEvents,
  groupedPreviewEvents,
  getEventTypeKey,
  formatDateTime,
  formatDateRange,
  toggleEventType,
  toggleEventTypeExpansion,
  selectAllEventTypes,
  clearAllEventTypes,
  selectAllSingleEvents,
  clearAllSingleEvents,
  switchFilterMode,
  updateCalendarId,
  // No preferences loading needed
} = useCalendar(events, eventTypes, props.id)

// Simple, direct data loading
const loadCalendarData = async (calendarId) => {
  console.log('🔄 Loading calendar data for:', calendarId)
  loading.value = true
  error.value = null
  
  console.log('🔄 Initial state:', {
    loading: loading.value,
    eventsLength: events.value.length,
    eventTypesKeys: eventTypes.value ? Object.keys(eventTypes.value).length : 'null'
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
        error.value = `Calendar ${calendarId} not found`
        return
      }
    }
    
    // Detect if this is a domain calendar and choose appropriate endpoint
    const isDomainCalendar = props.domainContext || calendarId.startsWith('cal_domain_')
    let domainName = null
    
    if (isDomainCalendar && props.domainContext) {
      domainName = props.domainContext.id
    } else if (isDomainCalendar && calendarId.startsWith('cal_domain_')) {
      domainName = calendarId.replace('cal_domain_', '')
    }
    
    let apiEndpoint, apiPath
    if (isDomainCalendar && domainName) {
      apiEndpoint = `/api/domains/${domainName}/events`
      apiPath = 'domain events'
    } else {
      apiEndpoint = `/api/calendar/${calendarId}/events`
      apiPath = 'calendar events'
    }
    
    console.log('🔍 About to make API call to:', apiEndpoint, `(${apiPath})`)
    const eventsResult = await api.safeExecute(async () => {
      console.log('🔍 Inside API call, making axios request...')
      const response = await axios.get(apiEndpoint)
      console.log('🔍 Raw axios response:', response)
      console.log('🔍 Response data:', response.data)
      
      // Domain endpoints return {events: {eventType: {...}}} structure
      // Calendar endpoints return {events: {eventType: {...}}} structure
      // Both have the same structure!
      if (isDomainCalendar) {
        console.log('🔍 Domain response data.events:', response.data.events)
        return response.data.events
      } else {
        console.log('🔍 Calendar response data.events:', response.data.events)
        return response.data.events
      }
    })
    console.log('🔍 safeExecute result:', eventsResult)
    
    if (eventsResult.success) {
      // Backend returns {events: {eventTypeName: {count: N, events: [...]}, ...}}
      console.log('✅ API response received. Raw data structure:', {
        hasData: !!eventsResult.data,
        dataKeys: eventsResult.data ? Object.keys(eventsResult.data) : 'null',
        firstEventType: eventsResult.data ? Object.keys(eventsResult.data)[0] : 'null'
      })
      
      // Extract event types object
      console.log('🔍 Raw API response:', eventsResult.data)
      console.log('🔍 Data type:', typeof eventsResult.data)
      console.log('🔍 Data keys:', Object.keys(eventsResult.data || {}))
      
      eventTypes.value = eventsResult.data
      console.log('✅ EventTypes assigned:', {
        eventTypesKeys: eventTypes.value ? Object.keys(eventTypes.value).length : 'eventTypes is null',
        eventTypeNames: eventTypes.value ? Object.keys(eventTypes.value) : 'eventTypes is null'
      })
      
      // Extract unique events from all event types
      const allEvents = []
      console.log('🔍 About to process eventTypes.value:', eventTypes.value)
      try {
        if (eventTypes.value) {
          Object.values(eventTypes.value).forEach(eventType => {
            console.log('🔍 Processing eventType:', eventType)
            if (eventType && eventType.events && Array.isArray(eventType.events)) {
              console.log(`🔍 Adding ${eventType.events.length} events from eventType`)
              allEvents.push(...eventType.events)
            }
          })
        } else {
          console.warn('⚠️ eventTypes.value is null or undefined')
        }
      } catch (extractError) {
        console.error('❌ Error extracting events:', extractError)
        throw extractError
      }
      events.value = allEvents
      console.log('✅ Events extracted:', {
        eventsLength: events.value.length,
        sampleEventTitle: events.value[0]?.title
      })
      
      // Debug the conditional rendering requirements
      console.log('🎯 Conditional rendering check:', {
        loading: loading.value,
        eventsLength: events.value.length,
        eventTypesExists: !!eventTypes.value,
        eventTypesKeysLength: Object.keys(eventTypes.value).length,
        shouldShow: !loading.value && events.value.length > 0 && eventTypes.value && Object.keys(eventTypes.value).length > 0
      })

      // Load groups data - use domain endpoint for domain calendars
      console.log('🔄 Loading groups data...')
      if (isDomainCalendar && domainName) {
        console.log('🔍 Loading domain groups for:', domainName)
        await appStore.loadDomainGroups(domainName)
      } else {
        await appStore.loadCalendarGroups(calendarId)
      }
      console.log('✅ Groups loaded:', {
        hasGroups: appStore.hasGroups,
        groupsCount: appStore.groups ? Object.keys(appStore.groups).length : 0
      })
      
      // Debug: Force re-render check
      console.log('🐛 DEBUG: hasGroups reactivity check:', {
        hasGroupsValue: appStore.hasGroups,
        hasGroupsType: typeof appStore.hasGroups
      })
    } else {
      console.error('❌ API call failed:', eventsResult)
      console.error('❌ Error details:', {
        success: eventsResult.success,
        error: eventsResult.error,
        data: eventsResult.data
      })
    }
    
  } catch (err) {
    console.error('Error loading calendar data:', err)
    error.value = 'Failed to load calendar data'
  } finally {
    loading.value = false
    console.log('🏁 Loading complete. Final state:', {
      loading: loading.value,
      eventsLength: events.value.length,
      eventTypesKeys: eventTypes.value ? Object.keys(eventTypes.value).length : 'null',
      shouldShow: !loading.value && events.value.length > 0 && eventTypes.value && Object.keys(eventTypes.value).length > 0
    })
  }
}

const clearError = () => {
  error.value = null
}

const navigateHome = () => {
  router.push('/home')
}

const navigateToCalendar = () => {
  // Stay on current calendar view - this is the calendar view, so no navigation needed
  // The function exists to fulfill the event handler requirement from FilteredCalendarSection
}

// Handle assigning ungrouped events to groups
const handleAssignEventToGroup = async ({ eventId, groupId }) => {
  console.log(`🔄 Assigning event ${eventId} to group ${groupId}`)
  
  const result = await appStore.assignEventToGroup(eventId, groupId)
  
  if (result.success) {
    console.log('✅ Event successfully assigned to group')
    // The store will handle updating the UI state automatically
  } else {
    console.error('❌ Failed to assign event to group:', result.error)
    // Could show user notification here
  }
}

const loadFilterIntoPage = (filterData) => {
  // Clear current selection
  clearAllEventTypes()
  
  // Set the filter mode
  if (filterData.mode !== filterMode.value) {
    switchFilterMode(filterData.mode)
  }
  
  // Select the event types from the filter
  filterData.eventTypes.forEach(eventTypeName => {
    toggleEventType(eventTypeName)
  })
  
  console.log(`Loaded filter "${filterData.calendarName}" with ${filterData.eventTypes.length} event types in ${filterData.mode} mode`)
}

// Handle selection changes from the new multi-level selection system (old complex)
const handleSelectionChanged = (selection) => {
  console.log('📊 Selection changed:', selection)
  
  // Resolve hierarchical group selections into a flat list of event types
  const resolvedEventTypes = resolveGroupSelectionsToEventTypes(selection)
  console.log('📋 Resolved event types:', resolvedEventTypes)
  
  // Update the selectedEventTypes to integrate with existing filter system
  selectedEventTypes.value = resolvedEventTypes
}

// Handle selection changes from the dual selection system
const handleGroupSelectionChanged = (selectionData) => {
  console.log('🎯 Dual selection changed:', selectionData)
  
  // Extract data from the dual selection format
  const { groups, eventTypes, events, subscribedGroups } = selectionData
  
  console.log('🔧 Processing dual selection:', {
    subscribedGroups: subscribedGroups,
    groups: groups,
    eventTypes: eventTypes,
    events: events
  })
  
  // Store selected groups and event types for filtering (legacy support)
  selectedGroups.value = groups || []
  
  // Handle subscribed groups separately (for future-proof filtering)
  if (subscribedGroups) {
    console.log('📁 Group subscriptions:', subscribedGroups)
    // Store subscribed groups for filtered calendar creation
    // This data will be used when creating filtered calendars that auto-include new events
  }
  
  // Update selectedEventTypes to include both direct event types and resolved group event types
  let resolvedEventTypes = [...(eventTypes || [])]
  
  // Add event types from selected groups (current manual selection)
  if (groups && groups.length > 0 && appStore.groups) {
    groups.forEach(groupId => {
      const group = appStore.groups[groupId]
      if (group && group.event_types) {
        resolvedEventTypes.push(...Object.keys(group.event_types))
      }
    })
  }
  
  // Add event types from subscribed groups (future-proof selection)
  if (subscribedGroups && subscribedGroups.length > 0 && appStore.groups) {
    subscribedGroups.forEach(groupId => {
      const group = appStore.groups[groupId]
      if (group && group.event_types) {
        resolvedEventTypes.push(...Object.keys(group.event_types))
      }
    })
  }
  
  // Remove duplicates
  resolvedEventTypes = [...new Set(resolvedEventTypes)]
  
  // Update the selectedEventTypes to integrate with existing filter system
  selectedEventTypes.value = resolvedEventTypes
  
  console.log('✅ Final selectedEventTypes:', selectedEventTypes.value)
  console.log('📁 Subscribed groups will auto-include future events:', subscribedGroups || [])
}

// Handle selection changes from the enhanced selection system  
const handleSimpleSelectionChanged = (selectionData) => {
  console.log('📊 Enhanced selection changed:', selectionData)
  
  if (selectionData.mode === 'enhanced') {
    // Handle enhanced selection data with both groups and individual event types
    console.log('🔧 Processing enhanced selection:', {
      eventTypes: selectionData.selectedEventTypes,
      groups: selectionData.selectedGroups
    })
    
    // Store both selected groups and individual event types
    selectedEventTypes.value = selectionData.selectedEventTypes
    selectedGroups.value = selectionData.selectedGroups
  } else {
    // Legacy support: direct array of event types
    selectedEventTypes.value = selectionData
    selectedGroups.value = []
  }
}

// Helper function to resolve hierarchical group selections into event types
const resolveGroupSelectionsToEventTypes = (selection) => {
  const eventTypes = new Set()
  
  // Get all event types from explicit event type selections
  selection.eventTypes.forEach(eventType => {
    eventTypes.add(eventType)
  })
  
  // Get all event types from selected groups (including nested groups)
  if (appStore.groups) {
    selection.groups.forEach(groupId => {
      const eventTypesFromGroup = getEventTypesFromGroup(groupId, appStore.groups)
      eventTypesFromGroup.forEach(eventType => {
        eventTypes.add(eventType)
      })
    })
  }
  
  // Add individual events (these are already event-specific, not type-specific)
  // Individual events will be handled differently by the filter system
  
  return Array.from(eventTypes)
}

// Recursive helper to extract all event types from a group and its children
const getEventTypesFromGroup = (groupId, groups) => {
  const eventTypes = new Set()
  
  // Find the group
  const group = findGroupById(groupId, groups)
  if (!group) return eventTypes
  
  // Add direct event types from this group
  if (group.event_types) {
    Object.keys(group.event_types).forEach(eventType => {
      eventTypes.add(eventType)
    })
  }
  
  // Recursively add event types from children
  if (group.children) {
    group.children.forEach(child => {
      const childEventTypes = getEventTypesFromGroup(child.id, groups)
      childEventTypes.forEach(eventType => {
        eventTypes.add(eventType)
      })
    })
  }
  
  return eventTypes
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
</script>