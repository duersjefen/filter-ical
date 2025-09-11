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
      <!-- Statistics -->
      <div class="statistics">
        <div class="stat-card">
          <h3>{{ appStore.statistics.totalEvents }}</h3>
          <p>Total Events</p>
        </div>
        <div class="stat-card">
          <h3>{{ appStore.statistics.eventTypes }}</h3>
          <p>Event Types</p>
        </div>
        <div class="stat-card">
          <h3>{{ appStore.statistics.yearsCovered }}</h3>
          <p>Years Covered</p>
        </div>
      </div>

      <!-- Event Filtering -->
      <div class="card">
        <div class="filter-section">
          <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 16px;">
            <h3 style="margin: 0;">Filter Events</h3>
            <div style="display: flex; gap: 12px;">
              <button @click="appStore.clearFilters()" class="btn btn-secondary">Clear All</button>
              <button @click="selectAll" class="btn">Select All</button>
            </div>
          </div>
          
          <div class="filter-grid">
            <div v-for="eventType in appStore.eventTypes" :key="eventType" class="filter-item">
              <input
                type="checkbox"
                :id="'filter-' + eventType"
                :checked="appStore.selectedEventTypes.has(eventType)"
                @change="appStore.toggleEventType(eventType)"
              />
              <label :for="'filter-' + eventType" style="cursor: pointer;">
                {{ eventType }} ({{ appStore.groupedEvents[eventType]?.length || 0 }})
              </label>
            </div>
          </div>

          <div v-if="appStore.selectedEventTypes.size > 0" style="margin-top: 20px;">
            <button @click="appStore.saveFilter()" class="btn">Save Current Filter</button>
          </div>
        </div>
      </div>

      <!-- Events Table -->
      <div class="card">
        <h3 style="margin-bottom: 20px;">
          Events 
          <span v-if="appStore.selectedEventTypes.size > 0">
            ({{ filteredEvents.length }} of {{ appStore.events.length }} shown)
          </span>
        </h3>

        <div v-if="filteredEvents.length === 0" style="text-align: center; color: #6c757d; padding: 40px;">
          <p v-if="appStore.selectedEventTypes.size > 0">
            No events match the selected filters.
          </p>
          <p v-else>
            No events found.
          </p>
        </div>

        <table v-else class="table">
          <thead>
            <tr>
              <th>Event</th>
              <th>Date</th>
              <th>Location</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="event in paginatedEvents" :key="event.uid">
              <td>
                <strong>{{ event.summary }}</strong>
              </td>
              <td>
                {{ formatDate(event.dtstart) }}
                <span v-if="event.dtend && event.dtend !== event.dtstart">
                  - {{ formatDate(event.dtend) }}
                </span>
              </td>
              <td>
                {{ event.location || '-' }}
              </td>
              <td>
                <div v-if="event.description" style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  {{ event.description.substring(0, 100) }}{{ event.description.length > 100 ? '...' : '' }}
                </div>
                <span v-else>-</span>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Simple pagination if needed -->
        <div v-if="filteredEvents.length > eventsPerPage" style="text-align: center; margin-top: 20px;">
          <button 
            @click="currentPage--" 
            :disabled="currentPage <= 1"
            class="btn btn-secondary"
            style="margin-right: 8px;"
          >
            Previous
          </button>
          <span style="margin: 0 16px;">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          <button 
            @click="currentPage++" 
            :disabled="currentPage >= totalPages"
            class="btn btn-secondary"
          >
            Next
          </button>
        </div>
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

const selectAll = () => {
  appStore.eventTypes.forEach(eventType => {
    appStore.selectedEventTypes.add(eventType)
  })
}

const formatDate = (dateStr) => {
  if (!dateStr || dateStr.length < 8) return dateStr
  
  // Handle YYYYMMDD format
  if (dateStr.length === 8) {
    const year = dateStr.substring(0, 4)
    const month = dateStr.substring(4, 6)
    const day = dateStr.substring(6, 8)
    return `${year}-${month}-${day}`
  }
  
  return dateStr
}

// Reset pagination when filters change
watch(() => appStore.selectedEventTypes.size, () => {
  currentPage.value = 1
})
</script>