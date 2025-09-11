<template>
  <div class="container">
    <div class="page-header">
      <h1>🗓️ iCal Filter & Subscribe</h1>
      <p>Easily filter your iCal feeds and create custom subscriptions</p>
      
      <!-- User info in header -->
      <div style="margin-top: 20px; display: flex; justify-content: center; align-items: center; gap: 20px;">
        <span>Welcome, {{ appStore.user.username }}!</span>
        <button @click="appStore.logout()" class="btn btn-secondary">Logout</button>
      </div>
    </div>

    <!-- Add Calendar Form -->
    <div class="card">
      <h2 style="margin-bottom: 24px;">Add New Calendar</h2>
      
      <div v-if="appStore.error" class="error">
        {{ appStore.error }}
        <button @click="appStore.clearError()" style="float: right; background: none; border: none; color: inherit; cursor: pointer;">&times;</button>
      </div>

      <form @submit.prevent="handleAddCalendar" style="display: grid; grid-template-columns: 1fr 1fr auto; gap: 16px; align-items: end;">
        <div class="form-group" style="margin-bottom: 0;">
          <label for="calendar-name">Calendar Name</label>
          <input
            id="calendar-name"
            v-model="appStore.newCalendar.name"
            type="text"
            class="form-control"
            placeholder="e.g., Work Calendar"
            required
          />
        </div>

        <div class="form-group" style="margin-bottom: 0;">
          <label for="calendar-url">iCal URL</label>
          <input
            id="calendar-url"
            v-model="appStore.newCalendar.url"
            type="url"
            class="form-control"
            placeholder="https://calendar.google.com/calendar/ical/..."
            required
          />
        </div>

        <button type="submit" class="btn" :disabled="appStore.loading">
          {{ appStore.loading ? 'Adding...' : 'Add Calendar' }}
        </button>
      </form>
    </div>

    <!-- Calendar List -->
    <div class="card">
      <h2 style="margin-bottom: 24px;">Your Calendars</h2>
      
      <div v-if="appStore.loading && appStore.calendars.length === 0" class="loading">
        Loading calendars...
      </div>

      <div v-else-if="appStore.calendars.length === 0" style="text-align: center; color: #6c757d; padding: 40px;">
        <p>No calendars found. Add your first calendar above!</p>
      </div>

      <div v-else>
        <table class="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>URL</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="calendar in appStore.calendars" :key="calendar.id">
              <td>
                <strong>{{ calendar.name }}</strong>
              </td>
              <td>
                <a :href="calendar.url" target="_blank" style="color: #007bff; text-decoration: none;">
                  {{ calendar.url.length > 60 ? calendar.url.substring(0, 60) + '...' : calendar.url }}
                </a>
              </td>
              <td>
                <button @click="viewCalendar(calendar.id)" class="btn" style="margin-right: 8px;">
                  View Events
                </button>
                <button 
                  v-if="calendar.user_id !== 'default'"
                  @click="deleteCalendar(calendar.id)" 
                  class="btn btn-danger"
                  :disabled="appStore.loading"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import { useRouter } from 'vue-router'
import { onMounted, watch } from 'vue'

const appStore = useAppStore()
const router = useRouter()

onMounted(() => {
  if (!appStore.isLoggedIn) {
    router.push('/login')
    return
  }
  appStore.fetchCalendars()
})

// Watch for navigation changes
watch(() => appStore.currentView, (newView) => {
  if (newView === 'calendar') {
    router.push(`/calendar/${appStore.selectedCalendar?.id}`)
  } else if (newView === 'login') {
    router.push('/login')
  }
})

const handleAddCalendar = async () => {
  await appStore.addCalendar()
}

const viewCalendar = async (calendarId) => {
  await appStore.viewCalendar(calendarId)
}

const deleteCalendar = async (calendarId) => {
  if (confirm('Are you sure you want to delete this calendar?')) {
    await appStore.deleteCalendar(calendarId)
  }
}
</script>