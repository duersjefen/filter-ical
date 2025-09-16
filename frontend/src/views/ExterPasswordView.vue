<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
      
      <!-- Show login form if not authenticated -->
      <div v-if="!isAuthenticated">
        <AppHeader 
          title="BCC Community Calendar"
          :subtitle="$t('community.subtitle')"
        />

        <!-- Login Form -->
        <div class="max-w-md mx-auto w-full">
          <div class="bg-white dark:bg-gray-800 py-8 px-6 shadow-lg rounded-lg border border-gray-200 dark:border-gray-700">
            <form @submit.prevent="checkPassword" class="space-y-6">
              <!-- Error Message -->
              <div v-if="error" class="bg-gradient-to-r from-red-100 to-red-50 dark:from-red-900/30 dark:to-red-800/30 border-2 border-red-300 dark:border-red-700 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg flex items-center gap-3">
                <div class="text-xl">⚠️</div>
                <span class="font-medium">{{ error }}</span>
              </div>

              <!-- Success Message -->
              <div v-if="success" class="bg-gradient-to-r from-green-100 to-green-50 dark:from-green-900/30 dark:to-green-800/30 border-2 border-green-300 dark:border-green-700 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg flex items-center gap-3">
                <div class="text-xl">✅</div>
                <span class="font-medium">{{ success }}</span>
              </div>

              <!-- Password Input -->
              <div>
                <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ $t('community.accessCode') }}
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  v-model="password"
                  required
                  class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all duration-200"
                  :placeholder="$t('community.accessCodePlaceholder')"
                  :disabled="loading"
                />
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                :disabled="loading || !password.trim()"
                class="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5"
              >
                <span v-if="loading" class="flex items-center">
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ $t('community.authenticating') }}
                </span>
                <span v-else class="flex items-center">
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
                  </svg>
                  {{ $t('community.accessButton') }}
                </span>
              </button>
            </form>

            <!-- Info -->
            <div class="mt-6 text-center">
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {{ $t('community.secureAccess') }}
              </p>
            </div>
          </div>

          <!-- Footer Links -->
          <div class="mt-6 text-center">
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ $t('community.needHelp') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Show dashboard if authenticated -->
      <div v-else>
        <AppHeader 
          :title="communityData?.name || 'BCC Community Calendar'"
          :subtitle="$t('community.welcomeBack')"
          :user="sessionData"
          :show-user-info="true"
          @logout="logout"
        />

        <!-- Dashboard Content with Reused Components -->
        <div class="space-y-6">
          <!-- Calendar Stats -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600 dark:text-gray-400">{{ $t('calendar.eventCount', calendarData.events.length) }}</p>
                  <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ calendarData.events.length }}</p>
                </div>
              </div>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600 dark:text-gray-400">{{ $t('calendar.categoryCount', calendarData.categories.length) }}</p>
                  <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ calendarData.categories.length }}</p>
                </div>
              </div>
            </div>
            
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600 dark:text-gray-400">{{ $t('filteredCalendar.mode') }}</p>
                  <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ filterMode === 'include' ? $t('filteredCalendar.includeOnly') : $t('filteredCalendar.excludeOnly') }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Reused Components -->
          <FilteredCalendarSection 
            :selected-calendar="{ id: 'exter', name: communityData?.name || 'BCC Community Calendar' }"
            :selected-categories="selectedCategories"
            :filter-mode="filterMode"
            :main-categories="calendarData.categories"
            :filtered-calendars="filteredCalendars"
            :loading="loadingFiltered"
            @create-filtered="createFilteredCalendar"
            @edit-filtered="editFilteredCalendar"
            @delete-filtered="deleteFilteredCalendar"
          />

          <PreviewEventsSection
            :selected-categories="selectedCategories"
            :events="calendarData.events"
            :filter-mode="filterMode"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '../components/shared/AppHeader.vue'
import FilteredCalendarSection from '../components/FilteredCalendarSection.vue'
import PreviewEventsSection from '../components/calendar/PreviewEventsSection.vue'

export default {
  name: 'ExterPasswordView',
  components: {
    AppHeader,
    FilteredCalendarSection,
    PreviewEventsSection
  },
  setup() {
    const router = useRouter()
    
    // Authentication state
    const password = ref('')
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    const isAuthenticated = ref(false)
    const sessionData = ref(null)
    const communityData = ref(null)
    
    // Calendar data
    const calendarData = ref({ events: [], categories: [] })
    const filteredCalendars = ref([])
    const loadingFiltered = ref(false)
    const filterMode = ref('include')
    const selectedCategories = ref([])

    // Check authentication status and load data
    onMounted(async () => {
      try {
        await checkAuthenticationStatus()
      } catch (err) {
        console.error('Failed to check authentication status:', err)
        // Ensure the page still renders even if auth check fails
        isAuthenticated.value = false
      }
    })

    const checkAuthenticationStatus = async () => {
      const savedSession = localStorage.getItem('bcc_exter_session')
      if (savedSession) {
        try {
          const sessionDataParsed = JSON.parse(savedSession)
          if (sessionDataParsed.session_id && sessionDataParsed.expires_at) {
            const now = new Date()
            const expiresAt = new Date(sessionDataParsed.expires_at)
            if (now < expiresAt) {
              // Session is still valid, load dashboard
              sessionData.value = sessionDataParsed
              isAuthenticated.value = true
              try {
                await loadDashboardData()
              } catch (err) {
                console.error('Failed to load dashboard data on mount:', err)
                // Continue anyway - page should still render even if data fails to load
              }
              return
            }
          }
        } catch (e) {
          // Invalid session data, clear it
          localStorage.removeItem('bcc_exter_session')
        }
      }
      isAuthenticated.value = false
    }

    const loadDashboardData = async () => {
      try {
        // Load community info
        const response = await fetch('/api/v1/community/exter/info')
        if (response.ok) {
          communityData.value = await response.json()
        }

        // Load calendar data from community source
        const calendarResponse = await fetch(`/api/v1/community/exter/events?user_id=${sessionData.value.user_id}`)
        if (calendarResponse.ok) {
          const data = await calendarResponse.json()
          calendarData.value = {
            events: data.events || [],
            categories: data.categories || []
          }
        } else {
          // Try alternative endpoint - load from community info and parse calendar directly
          if (communityData.value?.calendar_url) {
            const directCalendarResponse = await fetch(`/api/parse-calendar?url=${encodeURIComponent(communityData.value.calendar_url)}`)
            if (directCalendarResponse.ok) {
              const data = await directCalendarResponse.json()
              calendarData.value = {
                events: data.events || [],
                categories: data.categories || []
              }
            }
          }
        }

        // Load filtered calendars
        loadingFiltered.value = true
        const filteredResponse = await fetch(`/api/v1/community/exter/subscriptions?user_id=${sessionData.value.user_id}`)
        if (filteredResponse.ok) {
          const data = await filteredResponse.json()
          filteredCalendars.value = data.filtered_calendars || []
        }
      } catch (err) {
        console.error('Failed to load dashboard data:', err)
      } finally {
        loadingFiltered.value = false
      }
    }

    const checkPassword = async () => {
      loading.value = true
      error.value = ''
      success.value = ''

      try {
        // Call the API v1 authentication endpoint
        const response = await fetch('/api/v1/auth/exter/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            password: password.value
          })
        })

        const data = await response.json()

        if (response.ok && data.success) {
          // Store session information
          const newSessionData = {
            session_id: data.session_id,
            user_id: data.user_id,
            community_name: data.community_name,
            logged_in_at: new Date().toISOString(),
            expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours
          }
          
          localStorage.setItem('bcc_exter_session', JSON.stringify(newSessionData))
          sessionData.value = newSessionData
          
          success.value = `Welcome to ${data.community_name}!`
          
          // Set authenticated and load dashboard
          isAuthenticated.value = true
          await loadDashboardData()
          
        } else {
          error.value = data.detail || 'Invalid password'
        }
      } catch (err) {
        console.error('Login error:', err)
        error.value = 'Connection error - please check if the server is running'
      } finally {
        loading.value = false
      }
    }

    const logout = () => {
      localStorage.removeItem('bcc_exter_session')
      isAuthenticated.value = false
      sessionData.value = null
      communityData.value = null
      calendarData.value = { events: [], categories: [] }
      success.value = ''
      error.value = ''
    }

    // Dashboard component functions
    const createFilteredCalendar = async (calendarData) => {
      try {
        const response = await fetch('/api/v1/community/exter/subscriptions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: sessionData.value.user_id,
            name: calendarData.name,
            subscriptions: calendarData.subscriptions
          })
        })
        if (response.ok) {
          await loadDashboardData() // Reload data
        }
      } catch (err) {
        console.error('Failed to create filtered calendar:', err)
      }
    }

    const editFilteredCalendar = async (calendarData) => {
      try {
        const response = await fetch(`/api/v1/community/exter/subscriptions/${calendarData.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(calendarData)
        })
        if (response.ok) {
          await loadDashboardData() // Reload data
        }
      } catch (err) {
        console.error('Failed to edit filtered calendar:', err)
      }
    }

    const deleteFilteredCalendar = async (calendarId) => {
      try {
        const response = await fetch(`/api/v1/community/exter/subscriptions/${calendarId}`, {
          method: 'DELETE'
        })
        if (response.ok) {
          await loadDashboardData() // Reload data
        }
      } catch (err) {
        console.error('Failed to delete filtered calendar:', err)
      }
    }

    return {
      // Authentication
      password,
      loading,
      error,
      success,
      isAuthenticated,
      sessionData,
      communityData,
      checkPassword,
      logout,
      
      // Dashboard data
      calendarData,
      filteredCalendars,
      loadingFiltered,
      filterMode,
      selectedCategories,
      
      // Dashboard functions
      createFilteredCalendar,
      editFilteredCalendar,
      deleteFilteredCalendar
    }
  }
}
</script>

<style scoped>
/* Component-specific styles if needed */
</style>