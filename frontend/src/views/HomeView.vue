<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <AppHeader 
      title="🗓️ iCal Filter & Subscribe"
      subtitle="Easily filter your iCal feeds and create custom subscriptions"
    />

    <!-- Add Calendar Form -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-8 mb-8">
      <h2 class="mb-8 text-2xl font-bold text-gray-900 dark:text-gray-100">{{ $t('home.addNewCalendar') }}</h2>
      
      <div v-if="appStore.error" class="bg-gradient-to-r from-red-100 to-red-50 dark:from-red-900/30 dark:to-red-800/30 text-red-800 dark:text-red-200 px-6 py-4 rounded-xl mb-6 border-2 border-red-300 dark:border-red-700 relative shadow-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="text-2xl">⚠️</div>
            <span class="font-semibold">{{ appStore.error }}</span>
          </div>
          <button @click="appStore.clearError()" class="bg-transparent border-none text-red-800 dark:text-red-200 cursor-pointer text-xl font-bold hover:text-red-900 dark:hover:text-red-300 transition-all duration-300 hover:scale-110 p-2 rounded-full hover:bg-red-200 dark:hover:bg-red-800/50">&times;</button>
        </div>
      </div>

      <form @submit.prevent="handleAddCalendar" class="flex flex-col sm:grid sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-[1fr_1fr_auto] gap-4 sm:gap-6 lg:items-end">
        <div class="mb-0">
          <label for="calendar-name" class="block mb-2 font-medium text-gray-700 dark:text-gray-300">{{ $t('home.calendarName') }}</label>
          <input
            id="calendar-name"
            v-model="appStore.newCalendar.name"
            type="text"
            class="w-full px-4 py-3.5 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm transition-all duration-300 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/50 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm font-medium placeholder-gray-500 dark:placeholder-gray-400"
            :placeholder="$t('home.calendarNamePlaceholder')"
            required
          />
        </div>

        <div class="mb-0">
          <label for="calendar-url" class="block mb-2 font-medium text-gray-700 dark:text-gray-300">{{ $t('home.icalUrl') }}</label>
          <input
            id="calendar-url"
            v-model="appStore.newCalendar.url"
            type="url"
            class="w-full px-4 py-3.5 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm transition-all duration-300 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/50 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm font-medium placeholder-gray-500 dark:placeholder-gray-400"
            :placeholder="$t('home.icalUrlPlaceholder')"
            required
          />
        </div>

        <button type="submit" class="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white border-none px-6 sm:px-8 py-3 sm:py-3.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-1 shadow-lg hover:shadow-xl w-full lg:w-auto mt-4 lg:mt-0" :disabled="appStore.loading">
          {{ appStore.loading ? $t('home.adding') : $t('home.addCalendar') }}
        </button>
      </form>
    </div>

    <!-- Calendar List -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-8 mb-8">
      <h2 class="mb-8 text-2xl font-bold text-gray-900 dark:text-gray-100">{{ $t('home.yourCalendars') }}</h2>
      
      <div v-if="appStore.loading && appStore.calendars.length === 0" class="text-center py-12 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl border-2 border-blue-200 dark:border-blue-700 shadow-lg">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-6"></div>
        <div class="text-blue-800 dark:text-blue-200 font-semibold text-lg">{{ $t('common.loadingEvents') }}</div>
        <div class="text-blue-600 dark:text-blue-300 text-sm mt-2">{{ $t('common.pleaseWait') }}</div>
      </div>

      <div v-else-if="appStore.calendars.length === 0" class="text-center bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/30 dark:to-amber-900/30 border-2 border-yellow-300 dark:border-yellow-600 rounded-xl py-12 px-8 shadow-lg">
        <div class="text-6xl mb-4">📅</div>
        <p class="text-yellow-800 dark:text-yellow-200 font-semibold text-lg">{{ $t('home.noCalendarsFound') }}</p>
      </div>

      <div v-else>
        <!-- Mobile: Card Layout -->
        <div class="sm:hidden space-y-4">
          <div v-for="calendar in appStore.calendars" :key="calendar.id" class="bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 shadow-sm p-4">
            <div class="flex flex-col space-y-3">
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-gray-100 text-base">{{ calendar.name }}</h3>
                <a :href="calendar.url" target="_blank" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 no-underline font-medium transition-colors duration-200 hover:underline text-xs truncate block">
                  {{ calendar.url.length > 35 ? calendar.url.substring(0, 35) + '...' : calendar.url }}
                </a>
              </div>
              <div class="flex flex-col gap-2">
                <button @click="viewCalendar(calendar.id)" class="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white border-none px-4 py-2.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg">
                  {{ $t('home.viewEvents') }}
                </button>
                <button 
                  v-if="calendar.user_id !== 'default'"
                  @click="deleteCalendar(calendar.id)" 
                  class="bg-red-500 hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white border-none px-4 py-2.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg"
                  :disabled="appStore.loading"
                >
                  {{ $t('common.delete') }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop: Table Layout -->
        <div class="hidden sm:block overflow-x-auto">
          <table class="w-full border-collapse mt-6 bg-white dark:bg-gray-700 rounded-lg overflow-hidden shadow-sm">
            <thead>
              <tr>
                <th class="px-6 py-4 text-left border-b-2 border-gray-200 dark:border-gray-600 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-600 dark:to-gray-700 font-bold text-gray-800 dark:text-gray-200 tracking-wide uppercase text-sm">{{ $t('home.name') }}</th>
                <th class="px-6 py-4 text-left border-b-2 border-gray-200 dark:border-gray-600 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-600 dark:to-gray-700 font-bold text-gray-800 dark:text-gray-200 tracking-wide uppercase text-sm">{{ $t('home.url') }}</th>
                <th class="px-6 py-4 text-left border-b-2 border-gray-200 dark:border-gray-600 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-600 dark:to-gray-700 font-bold text-gray-800 dark:text-gray-200 tracking-wide uppercase text-sm">{{ $t('home.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="calendar in appStore.calendars" :key="calendar.id" class="hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 dark:hover:from-blue-900/30 dark:hover:to-indigo-900/30 transition-all duration-200 border-b border-gray-100 dark:border-gray-600">
                <td class="px-6 py-4">
                  <strong class="text-gray-900 dark:text-gray-100 font-semibold text-base">{{ calendar.name }}</strong>
                </td>
                <td class="px-6 py-4">
                  <a :href="calendar.url" target="_blank" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 no-underline break-all font-medium transition-colors duration-200 hover:underline">
                    {{ calendar.url.length > 60 ? calendar.url.substring(0, 60) + '...' : calendar.url }}
                  </a>
                </td>
                <td class="px-6 py-4">
                  <div class="flex gap-3">
                    <button @click="viewCalendar(calendar.id)" class="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white border-none px-6 py-2.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg whitespace-nowrap">
                      {{ $t('home.viewEvents') }}
                    </button>
                    <button 
                      v-if="calendar.user_id !== 'default'"
                      @click="deleteCalendar(calendar.id)" 
                      class="bg-red-500 hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white border-none px-6 py-2.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg whitespace-nowrap"
                      :disabled="appStore.loading"
                    >
                      {{ $t('common.delete') }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Confirmation Dialog -->
    <ConfirmDialog
      ref="confirmDialog"
      :title="$t('home.deleteCalendar')"
      :message="$t('home.deleteCalendarMessage', { name: calendarToDelete?.name || '' })"
      :confirm-text="$t('home.deleteCalendarConfirm')"
      :cancel-text="$t('home.deleteCalendarCancel')"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import { useRouter } from 'vue-router'
import { onMounted, watch, ref } from 'vue'
import AppHeader from '../components/shared/AppHeader.vue'
import ConfirmDialog from '../components/shared/ConfirmDialog.vue'
import { useDarkMode } from '../composables/useDarkMode'

const appStore = useAppStore()
const router = useRouter()

// Initialize dark mode
const { isDarkMode, toggleDarkMode } = useDarkMode()

// Confirmation dialog refs
const confirmDialog = ref(null)
const calendarToDelete = ref(null)

onMounted(() => {
  console.log('HomeView mounted in public-first mode')
  
  // Public-first access - always try to initialize and fetch calendars
  appStore.initializeApp()
  appStore.fetchCalendars()
})

const handleAddCalendar = async () => {
  const result = await appStore.addCalendar()
  if (!result.success && result.error) {
    // Set error in app store for display
    appStore.setError(result.error)
  }
}

const viewCalendar = async (calendarId) => {
  console.log('viewCalendar called with ID:', calendarId)
  router.push(`/calendar/${calendarId}`)
}

const deleteCalendar = async (calendarId) => {
  console.log('Delete calendar called with ID:', calendarId)
  
  // Find the calendar to show its name in the confirmation
  const calendar = appStore.calendars.find(c => c.id === calendarId)
  if (!calendar) {
    console.error('Calendar not found for deletion')
    return
  }
  
  // Store the calendar for the confirmation dialog
  calendarToDelete.value = calendar
  
  // Open the beautiful confirmation dialog
  confirmDialog.value?.open()
}

// Handle confirmation
const confirmDelete = async () => {
  if (!calendarToDelete.value) return
  
  console.log('User confirmed deletion')
  try {
    const result = await appStore.deleteCalendar(calendarToDelete.value.id)
    console.log('Delete result:', result)
  } catch (error) {
    console.error('Error during deletion:', error)
  } finally {
    calendarToDelete.value = null
  }
}

// Handle cancellation  
const cancelDelete = () => {
  console.log('User cancelled deletion')
  calendarToDelete.value = null
}

</script>