<template>
  <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 overflow-x-hidden dark:bg-gray-900 min-h-screen">
    <HeaderSection 
      :user="appStore.user"
      :selected-calendar="appStore.selectedCalendar"
      :error="appStore.error"
      :loading="appStore.loading"
      @logout="appStore.logout()"
      @navigate-home="navigateHome"
      @clear-error="appStore.clearError()"
    />

    <template v-if="appStore.events.length > 0">
      <CategoryCardsSection
        :categories="appStore.categories"
        :main-categories="mainCategories"
        :single-categories="singleEventCategories"
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

      <!-- Download Action Section -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
        <div class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">📥 {{ $t('calendar.downloadYourSelection') }}</h3>
            
            <!-- When no categories selected -->
            <div v-if="selectedCategories.length === 0" class="py-4 text-center">
              <div class="text-4xl mb-3">👆</div>
              <p class="text-gray-600 dark:text-gray-300 mb-4">{{ $t('calendar.selectSomeCategoriesAbove') }}</p>
              <button 
                class="px-8 py-3.5 bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 rounded-xl font-semibold cursor-not-allowed"
                disabled
              >
                💾 {{ $t('calendar.selectCategoriesFirst') }}
              </button>
            </div>

            <!-- When categories are selected -->
            <div v-else class="py-2">
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
                {{ $t('calendar.readyToDownload', { 
                  eventText: $t('calendar.eventCount', { count: selectedCategoriesCount }, selectedCategoriesCount),
                  categoryText: $t('calendar.categoryCount', { count: selectedCategories.length }, selectedCategories.length)
                }) }}
              </p>
              <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
                <button 
                  @click="generateIcalFile"
                  class="w-full sm:w-auto px-8 py-3 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg min-w-[200px]"
                >
                  💾 {{ $t('calendar.downloadIcalFile') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <PreviewEventsSection
        :selected-categories="selectedCategories"
        :sorted-preview-events="sortedPreviewEvents"
        :preview-group="previewGroup"
        :grouped-preview-events="groupedPreviewEvents"
        :formatDateTime="formatDateTime"
        :formatDateRange="formatDateRange"
        :getCategoryForEvent="getCategoryForEvent"
        @update:preview-group="previewGroup = $event"
      />

      <!-- Categories not loaded fallback -->
      <div v-if="appStore.categories.length === 0" class="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-xl shadow-lg border-2 border-amber-200 dark:border-amber-700 text-center p-8">
        <div class="text-6xl mb-4">📂</div>
        <p class="text-amber-800 dark:text-amber-200 mb-3 font-semibold text-lg">
          {{ $t('calendar.loadingCategoriesOrNotFound') }}
        </p>
        <p class="text-amber-700 dark:text-amber-300 text-sm font-medium">
          {{ $t('calendar.loadingCategoriesDescription') }}
        </p>
      </div>
    </template>

    <div v-else-if="!appStore.loading" class="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-xl shadow-lg border-2 border-red-200 dark:border-red-700 text-center py-12 px-8">
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
import { useAppStore } from '../stores/app'
import { useRouter, useRoute } from 'vue-router'
import { onMounted, watch } from 'vue'
import { useCalendar } from '../composables/useCalendar'
import {
  HeaderSection,
  CategoryCardsSection,
  PreviewEventsSection
} from '../components/calendar'

const appStore = useAppStore()
const router = useRouter()
const route = useRoute()

// Use calendar composable for all calendar-related functionality
const {
  // State
  selectedCategories,
  expandedCategories,
  showSingleEvents,
  showCategoriesSection,
  showSelectedOnly,
  categorySearch,
  filterMode,
  previewGroup,
  previewOrder,
  previewLimit,
  
  // Computed
  mainCategories,
  singleEventCategories,
  unifiedCategories,
  selectedCategoriesCount,
  selectedEventsCount,
  sortedPreviewEvents,
  groupedPreviewEvents,
  
  // Methods
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
  togglePreviewOrder,
  generateIcalFile
} = useCalendar()

const props = defineProps(['id'])

onMounted(async () => {
  if (!appStore.isLoggedIn) {
    router.push('/login')
    return
  }

  const calendarId = props.id || route.params.id
  if (calendarId) {
    // If we don't have calendars loaded, load them first
    if (appStore.calendars.length === 0) {
      await appStore.fetchCalendars()
    }
    await appStore.viewCalendar(calendarId)
    // Load saved filters for this user
    await appStore.fetchFilters()
  }
})

// Watch for navigation
watch(() => appStore.currentView, (newView) => {
  if (newView === 'home') {
    router.push('/home')
  } else if (newView === 'login') {
    router.push('/login')
  }
})

// Navigation helper
const navigateHome = () => {
  appStore.navigateHome()
}
</script>

