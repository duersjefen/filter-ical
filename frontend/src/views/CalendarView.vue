<template>
  <div class="container">
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
      <StatisticsSection
        :statistics="appStore.statistics"
        :categories="appStore.categories"
        :main-categories-count="mainCategories.length"
        :single-categories-count="singleEventCategories.length"
      />

      <CategoryCardsSection
        :categories="appStore.categories"
        :main-categories="mainCategories"
        :single-categories="singleEventCategories"
        :selected-categories="selectedCategories"
        :expanded-categories="expandedCategories"
        :show-single-events="showSingleEvents"
        :search-term="categorySearch"
        :filter-mode="filterMode"
        :selected-categories-count="selectedCategoriesCount"
        :show-preview="showPreview"
        :formatDateTime="formatDateTime"
        @clear-all="clearAllCategories"
        @select-all="selectAllCategories"
        @update:search-term="categorySearch = $event"
        @toggle-category="toggleCategory"
        @toggle-expansion="toggleCategoryExpansion"
        @toggle-singles-visibility="showSingleEvents = !showSingleEvents"
        @select-all-singles="selectAllSingleEvents"
        @clear-all-singles="clearAllSingleEvents"
        @switch-filter-mode="switchFilterMode"
        @generate-ical="generateIcalFile"
        @toggle-preview="showPreview = !showPreview"
      />

      <PreviewEventsSection
        :selected-categories="selectedCategories"
        :show-preview="showPreview"
        :sorted-preview-events="sortedPreviewEvents"
        :preview-group="previewGroup"
        :preview-order="previewOrder"
        :preview-limit="previewLimit"
        :grouped-preview-events="groupedPreviewEvents"
        :formatDateTime="formatDateTime"
        :getCategoryForEvent="getCategoryForEvent"
        @hide-preview="showPreview = false"
        @update:preview-group="previewGroup = $event"
        @toggle-preview-order="togglePreviewOrder"
        @increase-preview-limit="previewLimit += 10"
      />

      <!-- Categories not loaded fallback -->
      <div v-if="appStore.categories.length === 0" class="card" style="text-align: center; padding: 20px;">
        <p style="color: #6c757d;">
          📂 Loading categories or no categories found...
        </p>
        <p style="color: #6c757d; font-size: 14px;">
          This may happen if the calendar doesn't have CATEGORIES fields.
        </p>
      </div>
    </template>

    <div v-else-if="!appStore.loading" class="card" style="text-align: center; padding: 40px;">
      <h3>No events found</h3>
      <p>This calendar doesn't contain any events or there was an error loading them.</p>
      <button @click="navigateHome" class="btn">Back to Calendars</button>
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
  StatisticsSection, 
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
  categorySearch,
  filterMode,
  showPreview,
  previewGroup,
  previewOrder,
  previewLimit,
  
  // Computed
  mainCategories,
  singleEventCategories,
  selectedCategoriesCount,
  sortedPreviewEvents,
  groupedPreviewEvents,
  
  // Methods
  getCategoryForEvent,
  formatDateTime,
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

<style>
@import '../styles/calendar-view.css';
</style>
