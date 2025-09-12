<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <AppHeader 
      title="🗓️ iCal Filter & Subscribe"
      subtitle="Easily filter your iCal feeds and create custom subscriptions"
      :user="appStore.user"
      :show-user-info="true"
      @logout="appStore.logout()"
    />

    <!-- Add Calendar Form -->
    <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8 mb-8">
      <h2 class="mb-8 text-2xl font-bold text-gray-900">Add New Calendar</h2>
      
      <div v-if="appStore.error" class="bg-gradient-to-r from-red-100 to-red-50 text-red-800 px-6 py-4 rounded-xl mb-6 border-2 border-red-300 relative shadow-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="text-2xl">⚠️</div>
            <span class="font-semibold">{{ appStore.error }}</span>
          </div>
          <button @click="appStore.clearError()" class="bg-transparent border-none text-red-800 cursor-pointer text-xl font-bold hover:text-red-900 transition-all duration-300 hover:scale-110 p-2 rounded-full hover:bg-red-200">&times;</button>
        </div>
      </div>

      <form @submit.prevent="handleAddCalendar" class="flex flex-col sm:grid sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-[1fr_1fr_auto] gap-4 sm:gap-6 lg:items-end">
        <div class="mb-0">
          <label for="calendar-name" class="block mb-2 font-medium text-gray-700">Calendar Name</label>
          <input
            id="calendar-name"
            v-model="appStore.newCalendar.name"
            type="text"
            class="w-full px-4 py-3.5 border-2 border-gray-300 rounded-lg text-sm transition-all duration-300 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 hover:border-gray-400 shadow-sm font-medium"
            placeholder="e.g., Work Calendar"
            required
          />
        </div>

        <div class="mb-0">
          <label for="calendar-url" class="block mb-2 font-medium text-gray-700">iCal URL</label>
          <input
            id="calendar-url"
            v-model="appStore.newCalendar.url"
            type="url"
            class="w-full px-4 py-3.5 border-2 border-gray-300 rounded-lg text-sm transition-all duration-300 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 hover:border-gray-400 shadow-sm font-medium"
            placeholder="https://calendar.google.com/calendar/ical/..."
            required
          />
        </div>

        <button type="submit" class="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white border-none px-6 sm:px-8 py-3 sm:py-3.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-1 shadow-lg hover:shadow-xl w-full lg:w-auto mt-4 lg:mt-0" :disabled="appStore.loading">
          {{ appStore.loading ? 'Adding...' : 'Add Calendar' }}
        </button>
      </form>
    </div>

    <!-- Calendar List -->
    <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8 mb-8">
      <h2 class="mb-8 text-2xl font-bold text-gray-900">Your Calendars</h2>
      
      <div v-if="appStore.loading && appStore.calendars.length === 0" class="text-center py-12 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200 shadow-lg">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-6"></div>
        <div class="text-blue-800 font-semibold text-lg">Loading calendars...</div>
        <div class="text-blue-600 text-sm mt-2">Please wait while we fetch your calendars</div>
      </div>

      <div v-else-if="appStore.calendars.length === 0" class="text-center bg-gradient-to-br from-yellow-50 to-amber-50 border-2 border-yellow-300 rounded-xl py-12 px-8 shadow-lg">
        <div class="text-6xl mb-4">📅</div>
        <p class="text-yellow-800 font-semibold text-lg">No calendars found. Add your first calendar above!</p>
      </div>

      <div v-else>
        <!-- Mobile: Card Layout -->
        <div class="sm:hidden space-y-4">
          <div v-for="calendar in appStore.calendars" :key="calendar.id" class="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
            <div class="flex flex-col space-y-3">
              <div>
                <h3 class="font-semibold text-gray-900 text-base">{{ calendar.name }}</h3>
                <a :href="calendar.url" target="_blank" class="text-blue-600 hover:text-blue-800 no-underline font-medium transition-colors duration-200 hover:underline text-xs truncate block">
                  {{ calendar.url.length > 35 ? calendar.url.substring(0, 35) + '...' : calendar.url }}
                </a>
              </div>
              <div class="flex flex-col gap-2">
                <button @click="viewCalendar(calendar.id)" class="bg-blue-500 hover:bg-blue-600 text-white border-none px-4 py-2.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg">
                  View Events
                </button>
                <button 
                  v-if="calendar.user_id !== 'default'"
                  @click="deleteCalendar(calendar.id)" 
                  class="bg-red-500 hover:bg-red-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white border-none px-4 py-2.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg"
                  :disabled="appStore.loading"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop: Table Layout -->
        <div class="hidden sm:block overflow-x-auto">
          <table class="w-full border-collapse mt-6 bg-white rounded-lg overflow-hidden shadow-sm">
            <thead>
              <tr>
                <th class="px-6 py-4 text-left border-b-2 border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100 font-bold text-gray-800 tracking-wide uppercase text-sm">Name</th>
                <th class="px-6 py-4 text-left border-b-2 border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100 font-bold text-gray-800 tracking-wide uppercase text-sm">URL</th>
                <th class="px-6 py-4 text-left border-b-2 border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100 font-bold text-gray-800 tracking-wide uppercase text-sm">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="calendar in appStore.calendars" :key="calendar.id" class="hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 transition-all duration-200 border-b border-gray-100">
                <td class="px-6 py-4">
                  <strong class="text-gray-900 font-semibold text-base">{{ calendar.name }}</strong>
                </td>
                <td class="px-6 py-4">
                  <a :href="calendar.url" target="_blank" class="text-blue-600 hover:text-blue-800 no-underline break-all font-medium transition-colors duration-200 hover:underline">
                    {{ calendar.url.length > 60 ? calendar.url.substring(0, 60) + '...' : calendar.url }}
                  </a>
                </td>
                <td class="px-6 py-4">
                  <div class="flex gap-3">
                    <button @click="viewCalendar(calendar.id)" class="bg-blue-500 hover:bg-blue-600 text-white border-none px-6 py-2.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg whitespace-nowrap">
                      View Events
                    </button>
                    <button 
                      v-if="calendar.user_id !== 'default'"
                      @click="deleteCalendar(calendar.id)" 
                      class="bg-red-500 hover:bg-red-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white border-none px-6 py-2.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg whitespace-nowrap"
                      :disabled="appStore.loading"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import { useRouter } from 'vue-router'
import { onMounted, watch } from 'vue'
import AppHeader from '../components/shared/AppHeader.vue'

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