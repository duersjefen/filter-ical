<template>
  <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 overflow-x-hidden dark:bg-gray-900 min-h-screen">
    <HeaderSection 
      :selected-calendar="selectedCalendar"
      :error="error"
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
      <EventTypeCardsSection
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
        :filter-mode="filterMode"
        :main-event-types="mainEventTypes"
        :single-event-types="singleEventTypes"
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
import { ref, computed, onMounted } from 'vue'
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

// Define props first
const props = defineProps(['id'])

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
    
    // Load calendar info
    if (appStore.calendars.length === 0) {
      await appStore.fetchCalendars()
    }
    
    const calendar = appStore.calendars.find(c => c.id === calendarId)
    if (calendar) {
      selectedCalendar.value = calendar
    }
    
    // Load events and event types from single endpoint
    const eventsResult = await api.safeExecute(async () => {
      const response = await axios.get(`/api/calendar/${calendarId}/events`)
      return response.data.events
    })
    
    if (eventsResult.success) {
      // Backend returns {events: {eventTypeName: {count: N, events: [...]}, ...}}
      console.log('✅ API response received. Raw data structure:', {
        hasData: !!eventsResult.data,
        dataKeys: eventsResult.data ? Object.keys(eventsResult.data) : 'null',
        firstEventType: eventsResult.data ? Object.keys(eventsResult.data)[0] : 'null'
      })
      
      // Extract event types object
      eventTypes.value = eventsResult.data
      console.log('✅ EventTypes assigned:', {
        eventTypesKeys: Object.keys(eventTypes.value).length,
        eventTypeNames: Object.keys(eventTypes.value)
      })
      
      // Extract unique events from all event types
      const allEvents = []
      Object.values(eventTypes.value).forEach(eventType => {
        if (eventType.events && Array.isArray(eventType.events)) {
          allEvents.push(...eventType.events)
        }
      })
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
    } else {
      console.error('❌ API call failed:', eventsResult)
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

onMounted(async () => {
  console.log('CalendarView mounted with public-first access')
  
  // Initialize app state (loads calendars from localStorage)
  appStore.initializeApp()

  const calendarId = props.id || route.params.id
  console.log('Calendar ID from route:', calendarId)
  
  if (calendarId) {
    await loadCalendarData(calendarId)
    // Using default filter state - no persistence needed
  }
})

// No watchers needed - direct navigation only
</script>