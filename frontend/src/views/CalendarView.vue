<template>
  <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 overflow-x-hidden dark:bg-gray-900 min-h-screen">
    <HeaderSection 
      :user="appStore.user"
      :selected-calendar="selectedCalendar"
      :error="error"
      @logout="appStore.logout()"
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
    <template v-else-if="events.length > 0 && categories && Object.keys(categories).length > 0">
      <CategoryCardsSection
        :categories="mainCategories"
        :main-categories="mainCategories"
        :single-categories="singleEventCategories"
        :all-categories="categoriesSortedByCount"
        :selected-categories="selectedCategories"
        :expanded-categories="expandedCategories"
        :show-single-events="showSingleEvents"
        :show-categories-section="showCategoriesSection"
        :show-selected-only="showSelectedOnly"
        :search-term="categorySearch"
        :filter-mode="filterMode"
        :formatDateTime="formatDateTime"
        :formatDateRange="formatDateRange"
        @clear-all="clearAllCategories"
        @select-all="selectAllCategories"
        @update:search-term="categorySearch = $event"
        @toggle-category="toggleCategory"
        @toggle-expansion="toggleCategoryExpansion"
        @toggle-singles-visibility="showSingleEvents = !showSingleEvents"
        @select-all-singles="selectAllSingleEvents"
        @clear-all-singles="clearAllSingleEvents"
        @toggle-categories-section="showCategoriesSection = !showCategoriesSection"
        @toggle-selected-only="showSelectedOnly = !showSelectedOnly"
        @switch-filter-mode="switchFilterMode"
      />


      <!-- Filtered Calendar Section -->
      <!-- Always show if categories selected OR if existing filtered calendars exist -->
      <FilteredCalendarSection
        :selected-calendar="selectedCalendar"
        :selected-categories="selectedCategories"
        :filter-mode="filterMode"
        :main-categories="mainCategories"
        :single-event-categories="singleEventCategories"
        @navigate-to-calendar="navigateToCalendar"
        @load-filter="loadFilterIntoPage"
      />

      <PreviewEventsSection
        :selected-categories="selectedCategories"
        :sorted-preview-events="sortedPreviewEvents"
        :preview-group="previewGroup"
        :grouped-preview-events="groupedPreviewEvents"
        :filter-mode="filterMode"
        :all-events="events"
        :formatDateTime="formatDateTime"
        :formatDateRange="formatDateRange"
        :getCategoryForEvent="getCategoryForEvent"
        @update:preview-group="previewGroup = $event"
      />

      <!-- Categories not loaded fallback -->
      <div v-if="Object.keys(categories).length === 0" class="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-xl shadow-lg border-2 border-amber-200 dark:border-amber-700 text-center p-8">
        <div class="text-6xl mb-4">📂</div>
        <p class="text-amber-800 dark:text-amber-200 mb-3 font-semibold text-lg">
          {{ $t('calendar.loadingCategoriesOrNotFound') }}
        </p>
        <p class="text-amber-700 dark:text-amber-300 text-sm font-medium">
          {{ $t('calendar.loadingCategoriesDescription') }}
        </p>
      </div>
    </template>

    <!-- No Events Found -->
    <div v-else-if="!loading" class="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-xl shadow-lg border-2 border-red-200 dark:border-red-700 text-center py-12 px-8">
      <div class="text-6xl mb-4">📅</div>
      <h3 class="text-2xl font-bold text-red-800 dark:text-red-200 mb-4">{{ $t('calendar.noEventsFound') }}</h3>
      <p class="text-red-700 dark:text-red-300 mb-6 font-medium">{{ $t('calendar.noEventsFoundDescription') }}</p>
      <button @click="navigateHome" class="px-8 py-3.5 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white rounded-lg font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-lg hover:shadow-xl">
        {{ $t('navigation.backToCalendars') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCompatibilityStore as useAppStore } from '../stores/compatibility'
import { useAPI } from '../composables/useAPI'
import { useCalendar } from '../composables/useCalendar'
import axios from 'axios'
import {
  HeaderSection,
  CategoryCardsSection,
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
const categories = ref({})
const selectedCalendar = ref(null)

// Define props first
const props = defineProps(['id'])

// Use calendar composable with local data and calendar ID for persistence
const {
  selectedCategories,
  expandedCategories,
  showSingleEvents,
  showCategoriesSection,
  showSelectedOnly,
  categorySearch,
  filterMode,
  previewGroup,
  categoriesSortedByCount,
  mainCategories,
  singleEventCategories,
  selectedCategoriesCount,
  sortedPreviewEvents,
  groupedPreviewEvents,
  getCategoryForEvent,
  formatDateTime,
  formatDateRange,
  toggleCategory,
  toggleCategoryExpansion,
  selectAllCategories,
  clearAllCategories,
  selectAllSingleEvents,
  clearAllSingleEvents,
  switchFilterMode,
  loadFilterState,
  preferencesLoaded
} = useCalendar(events, categories, props.id)

// Simple, direct data loading
const loadCalendarData = async (calendarId) => {
  console.log('Loading calendar data for:', calendarId)
  loading.value = true
  error.value = null
  
  try {
    const userHeaders = appStore.getUserHeaders()
    
    // Load calendar info
    if (appStore.calendars.length === 0) {
      await appStore.fetchCalendars()
    }
    
    const calendar = appStore.calendars.find(c => c.id === calendarId)
    if (calendar) {
      selectedCalendar.value = calendar
    }
    
    // Load events and categories directly
    const [eventsResult, categoriesResult] = await Promise.all([
      api.safeExecute(async () => {
        const response = await axios.get(`/api/calendar/${calendarId}/events`, { headers: userHeaders })
        return response.data.events
      }),
      api.safeExecute(async () => {
        const response = await axios.get(`/api/calendar/${calendarId}/categories`, { headers: userHeaders })
        return response.data.categories
      })
    ])
    
    if (eventsResult.success) {
      // Backend returns {events: [...]} - extract the events array
      events.value = eventsResult.data.events || eventsResult.data
      console.log('Loaded events:', events.value.length)
    }
    
    if (categoriesResult.success) {
      // Backend returns {categories: {...}} - extract the categories object
      categories.value = categoriesResult.data.categories || categoriesResult.data
      console.log('Loaded categories:', Object.keys(categories.value).length)
    }
    
  } catch (err) {
    console.error('Error loading calendar data:', err)
    error.value = 'Failed to load calendar data'
  } finally {
    loading.value = false
  }
}

const clearError = () => {
  error.value = null
}

const navigateHome = () => {
  router.push('/')
}

const navigateToCalendar = () => {
  // Stay on current calendar view - this is the calendar view, so no navigation needed
  // The function exists to fulfill the event handler requirement from FilteredCalendarSection
}

const loadFilterIntoPage = (filterData) => {
  // Clear current selection
  clearAllCategories()
  
  // Set the filter mode
  if (filterData.mode !== filterMode.value) {
    switchFilterMode(filterData.mode)
  }
  
  // Select the categories from the filter
  filterData.categories.forEach(categoryName => {
    toggleCategory(categoryName)
  })
  
  console.log(`Loaded filter "${filterData.calendarName}" with ${filterData.categories.length} categories in ${filterData.mode} mode`)
}

onMounted(async () => {
  console.log('Simple CalendarView mounted')
  console.log('User state:', appStore.user)
  console.log('Is logged in:', appStore.isLoggedIn)
  
  // Initialize app state first (handles saved login)
  await appStore.initializeApp()
  console.log('After init - User state:', appStore.user)
  console.log('After init - Is logged in:', appStore.isLoggedIn)
  
  if (!appStore.isLoggedIn) {
    console.log('Not logged in, redirecting to login')
    router.push('/login')
    return
  }

  const calendarId = props.id || route.params.id
  console.log('Calendar ID from route:', calendarId)
  
  if (calendarId) {
    await loadCalendarData(calendarId)
    // Load saved filter state after calendar data is loaded
    await loadFilterState()
  }
})

// No watchers needed - direct navigation only
</script>