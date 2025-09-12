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

    <template v-else-if="appStore.events.length > 0">
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


const groupedPreviewEvents = computed(() => {
  if (previewGroup.value === 'none') return []
  
  const groups = {}
  
  sortedPreviewEvents.value.forEach(event => {
    let groupKey = ''
    
    switch (previewGroup.value) {
      case 'category':
        groupKey = getCategoryForEvent(event)
        break
      case 'date':
        groupKey = formatDate(event.dtstart).split(' ')[0] // Just the date part
        break
      case 'month':
        const eventDate = new Date(event.dtstart.substring(0, 4), 
                                 parseInt(event.dtstart.substring(4, 6)) - 1)
        groupKey = eventDate.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
        break
    }
    
    if (!groups[groupKey]) {
      groups[groupKey] = []
    }
    groups[groupKey].push(event)
  })
  
  // Convert to array and sort groups
  const groupArray = Object.entries(groups).map(([name, events]) => ({
    name,
    events
  }))
  
  groupArray.sort((a, b) => {
    if (previewGroup.value === 'category') {
      return previewOrder.value === 'asc' 
        ? a.name.localeCompare(b.name)
        : b.name.localeCompare(a.name)
    } else {
      // For date-based grouping, sort by the first event's date
      const dateA = new Date(a.events[0].dtstart)
      const dateB = new Date(b.events[0].dtstart)
      return previewOrder.value === 'asc' ? dateA - dateB : dateB - dateA
    }
  })
  
  return groupArray
})

const getCategoryForEvent = (event) => {
  // Find which category this event belongs to
  for (const category of appStore.categoriesSortedByCount) {
    if (category.events.some(e => e.uid === event.uid)) {
      return category.name
    }
  }
  return 'Unknown'
}

const generateIcalFile = async () => {
  // Validation
  if (selectedCategories.value.length === 0) {
    appStore.setError('Please select at least one category to generate the calendar file.')
    return
  }
  
  // Set loading state
  appStore.setLoading(true)
  appStore.clearError()
  
  try {
    // First, validate that the download URL will work by testing it
    const categories = selectedCategories.value.join(',')
    const downloadUrl = `/api/calendar/${appStore.selectedCalendar.id}/filtered.ical?categories=${encodeURIComponent(categories)}&mode=${filterMode.value}`
    
    // Test the URL with a HEAD request to ensure it's valid
    const testResponse = await fetch(downloadUrl, { method: 'HEAD', headers: appStore.getUserHeaders() })
    if (!testResponse.ok) {
      throw new Error(`Server returned ${testResponse.status}: ${testResponse.statusText}`)
    }
    
    // Create download link
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `${filterMode.value}_filtered_${appStore.selectedCalendar.name}.ical`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // Show appropriate success message based on mode
    const modeText = filterMode.value === 'include' ? 'including only' : 'excluding'
    const categoryText = selectedCategories.value.length === 1 ? 'category' : 'categories'
    const successMessage = `✅ Downloaded filtered calendar (${modeText} ${selectedCategories.value.length} ${categoryText})!\n\n${selectedCategoriesCount.value} events total. You can now import this .ical file into your calendar app.`
    
    // Use a toast-like notification instead of alert for better UX
    const notification = document.createElement('div')
    notification.innerHTML = successMessage.replace('\n\n', '<br><br>')
    notification.style.cssText = `
      position: fixed; top: 20px; right: 20px; z-index: 10000;
      background: linear-gradient(135deg, #10b981, #059669);
      color: white; padding: 16px 20px; border-radius: 12px;
      box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
      max-width: 350px; font-size: 14px; line-height: 1.4;
      animation: slideIn 0.3s ease-out;
    `
    document.body.appendChild(notification)
    
    // Auto-remove notification after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = 'slideOut 0.3s ease-in'
        setTimeout(() => notification.remove(), 300)
      }
    }, 5000)
    
  } catch (error) {
    console.error('Error generating iCal:', error)
    
    // Provide more specific error messages
    let errorMessage = 'Error generating calendar file. Please try again.'
    
    if (error.message.includes('404')) {
      errorMessage = 'Calendar not found. Please refresh the page and try again.'
    } else if (error.message.includes('500')) {
      errorMessage = 'Server error while generating calendar. Please try again in a moment.'
    } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
      errorMessage = 'Network connection error. Please check your internet connection and try again.'
    }
    
    appStore.setError(errorMessage)
  } finally {
    appStore.setLoading(false)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr || dateStr.length < 8) return dateStr
  
  // Handle YYYYMMDD format (date only)
  if (dateStr.length === 8) {
    const year = dateStr.substring(0, 4)
    const month = dateStr.substring(4, 6)
    const day = dateStr.substring(6, 8)
    return `${day}/${month}/${year}`
  }
  
  // Handle YYYYMMDDTHHMMSSZ format (with time)
  if (dateStr.length >= 15 && dateStr.includes('T')) {
    const year = dateStr.substring(0, 4)
    const month = dateStr.substring(4, 6)
    const day = dateStr.substring(6, 8)
    const hour = dateStr.substring(9, 11)
    const minute = dateStr.substring(11, 13)
    return `${day}/${month}/${year} ${hour}:${minute}`
  }
  
  return dateStr
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return dateStr
  
  // Convert to string if it's not already
  const str = String(dateStr).trim()
  
  if (str.length < 8) return str
  
  try {
    // Handle iCal YYYYMMDDTHHMMSSZ format (with time)
    if (str.match(/^\d{8}T\d{6}Z?$/)) {
      const year = str.substring(0, 4)
      const month = str.substring(4, 6)
      const day = str.substring(6, 8)
      const hour = str.substring(9, 11)
      const minute = str.substring(11, 13)
      return `${day}/${month}/${year} at ${hour}:${minute}`
    }
    
    // Handle iCal YYYYMMDD format (date only) - most common case
    if (str.match(/^\d{8}$/) && !str.includes('T')) {
      const year = str.substring(0, 4)
      const month = str.substring(4, 6)
      const day = str.substring(6, 8)
      return `${day}/${month}/${year}`
    }
    
    // Handle other time formats that might exist
    if (str.includes('T') && str.length > 8) {
      const datePart = str.split('T')[0]
      const timePart = str.split('T')[1].replace('Z', '')
      
      if (datePart.length === 8 && timePart.length >= 6) {
        const year = datePart.substring(0, 4)
        const month = datePart.substring(4, 6)
        const day = datePart.substring(6, 8)
        const hour = timePart.substring(0, 2)
        const minute = timePart.substring(2, 4)
        return `${day}/${month}/${year} at ${hour}:${minute}`
      }
    }
    
    // Try standard JavaScript date parsing as fallback
    const dateObj = new Date(str)
    if (!isNaN(dateObj.getTime())) {
      const hasTime = str.includes('T') || str.includes(':') || str.includes(' ')
      const day = String(dateObj.getDate()).padStart(2, '0')
      const month = String(dateObj.getMonth() + 1).padStart(2, '0')
      const year = dateObj.getFullYear()
      
      if (hasTime) {
        const hour = String(dateObj.getHours()).padStart(2, '0')
        const minute = String(dateObj.getMinutes()).padStart(2, '0')
        return `${day}/${month}/${year} at ${hour}:${minute}`
      } else {
        return `${day}/${month}/${year}`
      }
    }
  } catch (e) {
    // Silent fallback
  }
  
  // Fallback: return original string
  return str
}

// Reset pagination when filters change
watch(() => appStore.selectedEventTypes.size, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.category-cards {
  display: grid;
  gap: 16px;
  margin: 20px 0;
}

/* Responsive grid: 1 on mobile, 2 on tablet, 3 on desktop, max 4 on large screens */
@media (max-width: 767px) {
  .category-cards {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .category-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) and (max-width: 1439px) {
  .category-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1440px) {
  .category-cards {
    grid-template-columns: repeat(4, 1fr);
  }
}

.category-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.category-card:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
  transform: translateY(-1px);
}

.category-card.selected {
  border-color: #28a745;
  background: #f8fff8;
}

.category-card.expanded {
  border-color: #007bff;
}

.category-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.category-info strong {
  display: block;
  font-size: 16px;
  color: #333;
  margin-bottom: 4px;
}

.event-count {
  font-size: 14px;
  color: #666;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 12px;
}

.category-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expand-btn {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border: 1px solid #dee2e6;
  font-size: 12px;
  color: #495057;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 20px;
  transition: all 0.2s ease;
  font-weight: 500;
  min-width: 32px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.expand-btn:hover {
  background: linear-gradient(135deg, #e9ecef, #dee2e6);
  border-color: #adb5bd;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.expand-btn.expanded {
  background: linear-gradient(135deg, #007bff, #0056b3);
  border-color: #0056b3;
  color: white;
}

.expand-btn.expanded:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
}

/* Removed old round selection-indicator - now using selected-check */

.category-events {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
  max-height: 350px;
  overflow-y: auto;
  background: linear-gradient(to bottom, rgba(248, 249, 250, 0.3), rgba(255, 255, 255, 0.1));
  border-radius: 8px;
  padding: 16px;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-item {
  padding: 12px 16px;
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border-radius: 8px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.event-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  border-radius: 0 2px 2px 0;
}

.event-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #007bff;
}

.event-summary {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 6px;
  font-size: 14px;
  line-height: 1.3;
}

.event-date {
  font-size: 13px;
  color: #6c757d;
  margin-bottom: 4px;
  font-weight: 500;
}

.event-location {
  font-size: 12px;
  color: #868e96;
  display: flex;
  align-items: center;
  gap: 2px;
}

.more-events {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 12px;
  background: linear-gradient(135deg, #e9ecef, #f8f9fa);
  border-radius: 8px;
  margin-top: 12px;
  border: 1px solid #dee2e6;
  font-size: 13px;
  font-weight: 500;
}

/* iCal Generator Styles */
.ical-generator {
  margin-top: 24px;
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  border-radius: 12px;
  border: 2px solid #e9ecef;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.ical-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.ical-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.filter-type-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-label {
  font-weight: 500;
  color: #6c757d;
  margin: 0;
}

.toggle-buttons {
  display: flex;
  background: #e9ecef;
  border-radius: 20px;
  padding: 2px;
}

.toggle-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  border-radius: 18px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
  color: #6c757d;
}

.toggle-btn.active {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.3);
}

.filter-summary {
  background: #ffffff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e9ecef;
  margin-bottom: 20px;
}

.summary-info {
  margin-bottom: 12px;
}

.summary-text {
  font-weight: 500;
  color: #495057;
  font-size: 14px;
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-tag {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
}

.category-tag.include {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  border-color: #28a745;
  color: #155724;
}

.category-tag.exclude {
  background: linear-gradient(135deg, #f8d7da, #f1b0b7);
  border-color: #dc3545;
  color: #721c24;
}

.more-tag {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #6c757d;
}

.ical-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-download {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 3px 8px rgba(40, 167, 69, 0.3);
}

.btn-download:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
  background: linear-gradient(135deg, #20c997, #28a745);
}

.btn-preview {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 3px 8px rgba(108, 117, 125, 0.3);
}

.btn-preview:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(108, 117, 125, 0.4);
}

@media (max-width: 767px) {
  .ical-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-type-toggle {
    justify-content: center;
  }
  
  .ical-actions {
    justify-content: center;
  }
  
  .btn-download, .btn-preview {
    flex: 1;
    min-width: 150px;
  }
}

/* Category Actions Styles */
.category-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.basic-actions {
  display: flex;
  gap: 8px;
}

.btn-info {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(23, 162, 184, 0.2);
}

.btn-info:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(23, 162, 184, 0.3);
  background: linear-gradient(135deg, #138496, #117a8b);
}

@media (max-width: 767px) {
  .category-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .quick-actions, .basic-actions {
    justify-content: center;
  }
}

/* Single Events Section Styles */
.single-events-section {
  margin-top: 20px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.single-events-header {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.2s;
  gap: 16px;
}

.section-left {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  flex: 1;
}

.section-left:hover {
  background: linear-gradient(135deg, #e9ecef, #dee2e6);
  border-radius: 6px;
  margin: -4px;
  padding: 4px;
}

.section-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-info strong {
  color: #495057;
  font-size: 16px;
}

.section-count {
  font-size: 14px;
  color: #6c757d;
  background: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
  width: fit-content;
}

.section-toggle {
  background: none;
  border: none;
  font-size: 16px;
  color: #007bff;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
}

.section-toggle:hover {
  background: rgba(0, 123, 255, 0.1);
}

.section-toggle.expanded {
  transform: rotate(90deg);
}

.singles-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  min-width: 120px;
  justify-content: flex-end;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
  border: 1px solid #007bff;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.btn-small:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.3);
}

.btn-small.btn-secondary {
  border-color: #6c757d;
  background: linear-gradient(135deg, #6c757d, #545b62);
}

.btn-small.btn-secondary:hover {
  background: linear-gradient(135deg, #545b62, #464c54);
}

.single-events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 16px;
  padding: 24px;
  background: #ffffff;
  max-height: 500px;
  overflow-y: auto;
}

.single-event-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
}

.single-event-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.1);
  transform: translateY(-1px);
}

.single-event-item.selected {
  border-color: #28a745;
  background: linear-gradient(135deg, #f8fff8, #e6ffed);
}

.single-event-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.single-event-title {
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
  line-height: 1.3;
}

.single-event-datetime, .single-event-location {
  font-size: 12px;
  color: #6c757d;
}

.single-event-datetime {
  font-weight: 500;
}

.selected-check {
  font-size: 16px;
  font-weight: bold;
  color: #28a745;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  animation: checkIn 0.2s ease-out;
}

@keyframes checkIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@media (max-width: 767px) {
  .single-events-grid {
    grid-template-columns: 1fr;
  }
  
  .section-info {
    align-items: flex-start;
  }
}

/* Enhanced Preview Events Styles */
.preview-events {
  margin-top: 20px;
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border-radius: 12px;
  border: 2px solid #e9ecef;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.preview-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.close-preview-btn {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-preview-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(108, 117, 125, 0.3);
}

.preview-controls {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 8px;
  border: 1px solid #dee2e6;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-group label {
  font-weight: 500;
  color: #495057;
  margin: 0;
  min-width: 60px;
}

.preview-select {
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.preview-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.order-btn {
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.order-btn:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.order-btn.asc {
  color: #28a745;
}

.order-btn.desc {
  color: #dc3545;
}

.preview-content {
  max-height: 600px;
  overflow-y: auto;
}

.events-list-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-event-item {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border-radius: 8px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.preview-event-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #007bff;
}

.event-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-title {
  font-weight: 600;
  color: #2c3e50;
  font-size: 16px;
  line-height: 1.3;
}

.event-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.event-date, .event-category, .event-location {
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.event-date {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  color: #1976d2;
  border: 1px solid #2196f3;
}

.event-category {
  background: linear-gradient(135deg, #f3e5f5, #e1bee7);
  color: #7b1fa2;
  border: 1px solid #9c27b0;
}

.event-location {
  background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
  color: #388e3c;
  border: 1px solid #4caf50;
}

.grouped-events {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.event-group {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.group-header {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.group-count {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.group-events {
  padding: 16px;
  background: white;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.show-more {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dee2e6;
}

.show-more-btn {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 3px 8px rgba(23, 162, 184, 0.3);
}

.show-more-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(23, 162, 184, 0.4);
  background: linear-gradient(135deg, #138496, #117a8b);
}

@media (max-width: 767px) {
  .preview-controls {
    flex-direction: column;
    gap: 12px;
  }
  
  .control-group {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }
  
  .control-group label {
    min-width: auto;
  }
  
  .event-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .preview-header {
    flex-direction: column;
    align-items: stretch;
  }
}

/* Toast notification animations */
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}
</style>