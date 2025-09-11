<template>
  <div class="container">
    <!-- Header with user info -->
    <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
      <div style="display: flex; align-items: center; gap: 16px;">
        <span>{{ appStore.user.username }}</span>
        <button @click="appStore.logout()" class="btn btn-secondary">Logout</button>
      </div>
    </div>

    <div class="page-header">
      <h1>Filter: {{ appStore.selectedCalendar?.name || 'Loading...' }}</h1>
      <p>Select event types to filter and create custom subscriptions</p>
      
      <div style="margin-top: 20px;">
        <button @click="navigateHome" class="btn btn-secondary">
          ← Back to Calendars
        </button>
      </div>
    </div>

    <div v-if="appStore.error" class="error">
      {{ appStore.error }}
      <button @click="appStore.clearError()" style="float: right; background: none; border: none; color: inherit; cursor: pointer;">&times;</button>
    </div>

    <div v-if="appStore.loading" class="loading">
      Loading events...
    </div>

    <template v-else-if="appStore.events.length > 0">
      <!-- Enhanced Statistics -->
      <div class="statistics">
        <div class="stat-card">
          <h3>{{ appStore.statistics.totalEvents }}</h3>
          <p>Total Events</p>
        </div>
        <div class="stat-card">
          <h3>{{ appStore.categories.length }}</h3>
          <p>Categories</p>
        </div>
        <div class="stat-card">
          <h3>{{ mainCategories.length }}</h3>
          <p>Multi-Event</p>
        </div>
        <div class="stat-card">
          <h3>{{ singleEventCategories.length }}</h3>
          <p>Unique Events</p>
        </div>
      </div>

      <!-- Category Cards Selection -->
      <div v-if="appStore.categories.length > 0" class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
          <h3 style="margin: 0;">📂 Select Event Categories</h3>
          <div class="category-actions">
            <div class="basic-actions">
              <button @click="clearAllCategories" class="btn btn-secondary">Clear All</button>
              <button @click="selectAllCategories" class="btn">Select All</button>
            </div>
          </div>
        </div>

        <!-- Category Search -->
        <div style="margin-bottom: 20px;">
          <input 
            v-model="categorySearch"
            type="text" 
            placeholder="🔍 Search categories..."
            class="form-control"
            style="width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px;"
          />
        </div>
        
        <!-- Main Categories (2+ events) -->
        <div class="category-cards">
          <div 
            v-for="category in mainCategories" 
            :key="category.name" 
            class="category-card"
            :class="{ 'selected': selectedCategories.includes(category.name), 'expanded': expandedCategories.includes(category.name) }"
            @click="toggleCategory(category.name)"
          >
            <div class="category-card-header">
              <div class="category-info">
                <strong>{{ category.name }}</strong>
                <span class="event-count">{{ category.count }} events</span>
              </div>
              <div class="category-actions">
                <div class="selected-check">
                  <span v-if="selectedCategories.includes(category.name)">✓</span>
                </div>
                <button 
                  @click.stop="toggleCategoryExpansion(category.name)"
                  class="expand-btn"
                  :class="{ 'expanded': expandedCategories.includes(category.name) }"
                >
                  {{ expandedCategories.includes(category.name) ? '▼' : '▶' }}
                </button>
              </div>
            </div>
            
            <!-- Expandable Events List -->
            <div v-if="expandedCategories.includes(category.name)" class="category-events">
              <div class="events-list">
                <div 
                  v-for="event in category.events.slice(0, 5)" 
                  :key="event.uid"
                  class="event-item"
                >
                  <div class="event-summary">{{ event.summary }}</div>
                  <div class="event-date">📅 {{ formatDateTime(event.dtstart) }}</div>
                  <div v-if="event.location" class="event-location">📍 {{ event.location }}</div>
                </div>
                <div v-if="category.events.length > 5" class="more-events">
                  ... and {{ category.events.length - 5 }} more events
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Single Event Categories (Collapsible) -->
        <div v-if="singleEventCategories.length > 0" class="single-events-section">
          <div class="single-events-header">
            <div class="section-left" @click="showSingleEvents = !showSingleEvents">
              <div class="section-info">
                <strong>📄 Individual Events</strong>
                <span class="section-count">{{ singleEventCategories.length }} unique events</span>
              </div>
              <button class="section-toggle" :class="{ 'expanded': showSingleEvents }">
                {{ showSingleEvents ? '▼' : '▶' }}
              </button>
            </div>
            <div class="singles-actions">
              <button @click.stop="selectAllSingleEvents" class="btn-small" title="Select all individual events">
                ✓ All
              </button>
              <button @click.stop="clearAllSingleEvents" class="btn-small btn-secondary" title="Deselect all individual events">
                ✗ None
              </button>
            </div>
          </div>
          
          <div v-if="showSingleEvents" class="single-events-grid">
            <div 
              v-for="category in singleEventCategories" 
              :key="category.name"
              class="single-event-item"
              :class="{ 'selected': selectedCategories.includes(category.name) }"
              @click="toggleCategory(category.name)"
            >
              <div class="single-event-content">
                <div class="single-event-title">{{ category.name }}</div>
                <div class="single-event-datetime">{{ formatDateTime(category.events[0].dtstart) }}</div>
                <div v-if="category.events[0].location" class="single-event-location">📍 {{ category.events[0].location }}</div>
              </div>
              <div class="selected-check">
                <span v-if="selectedCategories.includes(category.name)">✓</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Generate iCal -->
        <div v-if="selectedCategories.length > 0" class="ical-generator">
          <div class="ical-header">
            <h4>📥 Create Filtered Calendar</h4>
            <div class="filter-type-toggle">
              <label class="toggle-label">Filter Mode:</label>
              <div class="toggle-buttons">
                <button 
                  class="toggle-btn" 
                  :class="{ active: filterMode === 'include' }" 
                  @click="switchFilterMode('include')"
                >
                  ✅ Include Only
                </button>
                <button 
                  class="toggle-btn" 
                  :class="{ active: filterMode === 'exclude' }" 
                  @click="switchFilterMode('exclude')"
                >
                  ❌ Exclude These
                </button>
              </div>
            </div>
          </div>
          
          <div class="filter-summary">
            <div class="summary-info">
              <span class="summary-text">
                {{ filterMode === 'include' 
                  ? `Including ${selectedCategories.length} categories with ${selectedCategoriesCount} events` 
                  : `Excluding ${selectedCategories.length} categories (removing ${selectedCategoriesCount} events)` 
                }}
              </span>
            </div>
            <div class="category-tags">
              <span 
                v-for="category in selectedCategories.slice(0, 3)" 
                :key="category" 
                class="category-tag"
                :class="filterMode"
              >
                {{ category }}
              </span>
              <span v-if="selectedCategories.length > 3" class="more-tag">
                +{{ selectedCategories.length - 3 }} more
              </span>
            </div>
          </div>
          
          <div class="ical-actions">
            <button @click="generateIcalFile" class="btn-download">
              📥 Download Filtered Calendar
            </button>
            <button @click="showPreview = !showPreview" class="btn-preview">
              {{ showPreview ? 'Hide Preview' : '👀 Preview Events' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Enhanced Preview Events -->
      <div v-if="selectedCategories.length > 0 && showPreview" class="preview-events">
        <div class="preview-header">
          <h3>Preview Filtered Events ({{ sortedPreviewEvents.length }})</h3>
          <button @click="showPreview = false" class="close-preview-btn">Hide Preview</button>
        </div>
        
        <!-- Simplified Preview Controls -->
        <div class="preview-controls">
          <div class="control-group">
            <label>View:</label>
            <select v-model="previewGroup" class="preview-select">
              <option value="none">📋 Simple List</option>
              <option value="category">📂 By Category</option>
              <option value="month">📅 By Month</option>
            </select>
          </div>
          <div class="control-group">
            <label>Sort:</label>
            <button 
              @click="togglePreviewOrder"
              class="order-btn"
              :class="previewOrder"
            >
              {{ previewOrder === 'asc' ? '📅 Oldest First' : '📅 Newest First' }}
            </button>
          </div>
        </div>
        
        <!-- Preview Content -->
        <div class="preview-content">
          <!-- No Grouping -->
          <div v-if="previewGroup === 'none'" class="events-list-preview">
            <div 
              v-for="event in sortedPreviewEvents.slice(0, previewLimit)" 
              :key="event.uid"
              class="preview-event-item"
            >
              <div class="event-main">
                <div class="event-title">{{ event.summary }}</div>
                <div class="event-meta">
                  <span class="event-date">📅 {{ formatDateTime(event.dtstart) }}</span>
                  <span class="event-category">📂 {{ getCategoryForEvent(event) }}</span>
                  <span v-if="event.location" class="event-location">📍 {{ event.location }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Grouped Display -->
          <div v-else class="grouped-events">
            <div 
              v-for="group in groupedPreviewEvents" 
              :key="group.name"
              class="event-group"
            >
              <div class="group-header">
                <h4>{{ group.name }}</h4>
                <span class="group-count">{{ group.events.length }} events</span>
              </div>
              <div class="group-events">
                <div 
                  v-for="event in group.events.slice(0, 5)" 
                  :key="event.uid"
                  class="preview-event-item"
                >
                  <div class="event-main">
                    <div class="event-title">{{ event.summary }}</div>
                    <div class="event-meta">
                      <span class="event-date">📅 {{ formatDateTime(event.dtstart) }}</span>
                      <span v-if="previewGroup !== 'category'" class="event-category">📂 {{ getCategoryForEvent(event) }}</span>
                      <span v-if="event.location" class="event-location">📍 {{ event.location }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="group.events.length > 5" class="more-events" style="margin-top: 12px;">
                  ... and {{ group.events.length - 5 }} more events
                </div>
              </div>
            </div>
          </div>
          
          <!-- Show More Button -->
          <div v-if="sortedPreviewEvents.length > previewLimit" class="show-more">
            <button @click="previewLimit += 10" class="show-more-btn">
              Show {{ Math.min(10, sortedPreviewEvents.length - previewLimit) }} more events
              ({{ sortedPreviewEvents.length - previewLimit }} remaining)
            </button>
          </div>
        </div>
      </div>

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
import { onMounted, computed, ref, watch } from 'vue'

const appStore = useAppStore()
const router = useRouter()
const route = useRoute()

const currentPage = ref(1)
const eventsPerPage = 50
const selectedCategories = ref([])
const showPreview = ref(false)
const categorySearch = ref('')
const expandedCategories = ref([])
const filterMode = ref('include')
const previewSort = ref('date')
const previewOrder = ref('asc')
const previewGroup = ref('none')
const previewLimit = ref(10)
const maxCategoriesShown = ref(50) // Performance: limit initial category display
const showSingleEvents = ref(false)
const isGeneratingIcal = ref(false)

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

const filteredEvents = computed(() => appStore.filteredEvents)

const totalPages = computed(() => 
  Math.ceil(filteredEvents.value.length / eventsPerPage)
)

const paginatedEvents = computed(() => {
  const start = (currentPage.value - 1) * eventsPerPage
  const end = start + eventsPerPage
  return filteredEvents.value.slice(start, end)
})

const navigateHome = () => {
  appStore.navigateHome()
}

// Filtered categories based on search
const filteredCategories = computed(() => {
  if (!categorySearch.value.trim()) {
    return appStore.categoriesSortedByCount
  }
  
  const searchTerm = categorySearch.value.toLowerCase()
  return appStore.categoriesSortedByCount.filter(category => 
    category.name.toLowerCase().includes(searchTerm)
  )
})

// Separate main categories (2+ events) from single-event categories
const mainCategories = computed(() => {
  return filteredCategories.value.filter(category => category.count > 1)
})

const singleEventCategories = computed(() => {
  return filteredCategories.value.filter(category => category.count === 1)
})

// Category selection functions
const selectAllCategories = () => {
  selectedCategories.value = filteredCategories.value.map(cat => cat.name)
}

const clearAllCategories = () => {
  selectedCategories.value = []
  showPreview.value = false
}

// Singles selection functions
const selectAllSingleEvents = () => {
  const singleEventNames = singleEventCategories.value.map(cat => cat.name)
  singleEventNames.forEach(name => {
    if (!selectedCategories.value.includes(name)) {
      selectedCategories.value.push(name)
    }
  })
}

const clearAllSingleEvents = () => {
  const singleEventNames = singleEventCategories.value.map(cat => cat.name)
  selectedCategories.value = selectedCategories.value.filter(name => !singleEventNames.includes(name))
}

// Card interaction methods
const toggleCategory = (categoryName) => {
  const index = selectedCategories.value.indexOf(categoryName)
  if (index === -1) {
    selectedCategories.value.push(categoryName)
  } else {
    selectedCategories.value.splice(index, 1)
  }
}

const toggleCategoryExpansion = (categoryName) => {
  const index = expandedCategories.value.indexOf(categoryName)
  if (index === -1) {
    expandedCategories.value.push(categoryName)
  } else {
    expandedCategories.value.splice(index, 1)
  }
}

// Smart filter mode switching
const switchFilterMode = (newMode) => {
  if (filterMode.value !== newMode) {
    // Flip the selection when switching modes
    const allCategories = filteredCategories.value.map(cat => cat.name)
    const currentlyUnselected = allCategories.filter(cat => !selectedCategories.value.includes(cat))
    
    // Set the new selection to what was previously unselected
    selectedCategories.value = [...currentlyUnselected]
    filterMode.value = newMode
    
    // Reset preview limit when mode changes
    previewLimit.value = 10
  }
}

// Simplified preview toggle
const togglePreviewOrder = () => {
  previewOrder.value = previewOrder.value === 'asc' ? 'desc' : 'asc'
}

// Computed values for selected categories
const selectedCategoriesCount = computed(() => {
  return appStore.categoriesSortedByCount
    .filter(cat => selectedCategories.value.includes(cat.name))
    .reduce((sum, cat) => sum + cat.count, 0)
})

const previewEvents = computed(() => {
  if (selectedCategories.value.length === 0) return []
  
  const selectedCategoryEvents = []
  appStore.categoriesSortedByCount.forEach(category => {
    if (selectedCategories.value.includes(category.name)) {
      selectedCategoryEvents.push(...category.events)
    }
  })
  
  return selectedCategoryEvents
})

const sortedPreviewEvents = computed(() => {
  const events = [...previewEvents.value]
  
  // Always sort by date for simplicity - fix the date parsing
  events.sort((a, b) => {
    const parseDate = (dateStr) => {
      if (!dateStr) return new Date(0)
      
      // Handle YYYYMMDD format
      if (dateStr.length >= 8) {
        const year = parseInt(dateStr.substring(0, 4))
        const month = parseInt(dateStr.substring(4, 6)) - 1 // Month is 0-indexed
        const day = parseInt(dateStr.substring(6, 8))
        
        // Handle time if present (YYYYMMDDTHHMMSS)
        if (dateStr.length >= 15 && dateStr.includes('T')) {
          const hour = parseInt(dateStr.substring(9, 11))
          const minute = parseInt(dateStr.substring(11, 13))
          return new Date(year, month, day, hour, minute)
        }
        
        return new Date(year, month, day)
      }
      
      return new Date(dateStr)
    }
    
    const dateA = parseDate(a.dtstart)
    const dateB = parseDate(b.dtstart)
    
    return previewOrder.value === 'asc' ? dateA - dateB : dateB - dateA
  })
  
  return events
})

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