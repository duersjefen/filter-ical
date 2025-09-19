<template>
  <!-- Loading State -->
  <div v-if="loading" class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="text-center py-12 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl border-2 border-blue-200 dark:border-blue-700 shadow-lg">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-6"></div>
      <div class="text-blue-800 dark:text-blue-200 font-semibold text-lg">{{ $t('domain.loadingDomainCalendar') }}</div>
      <div class="text-blue-600 dark:text-blue-300 text-sm mt-2">{{ $t('common.pleaseWait') }}</div>
    </div>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="bg-gradient-to-r from-red-100 to-red-50 dark:from-red-900/30 dark:to-red-800/30 text-red-800 dark:text-red-200 px-6 py-4 rounded-xl border-2 border-red-300 dark:border-red-700 relative shadow-lg">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="text-2xl">⚠️</div>
          <span class="font-semibold">{{ error }}</span>
        </div>
      </div>
    </div>
    
    <!-- Link to Personal Calendars on Error -->
    <div class="mt-6 text-center">
      <router-link 
        to="/home" 
        class="inline-flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200"
      >
        {{ $t('domain.goToPersonalCalendars') }}
      </router-link>
    </div>
  </div>

  <!-- Domain Not Found -->
  <div v-else-if="!domainConfig" class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="text-center py-12 bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/30 dark:to-orange-900/30 rounded-xl border-2 border-yellow-200 dark:border-yellow-700 shadow-lg">
      <div class="text-6xl mb-6">🔍</div>
      <div class="text-yellow-800 dark:text-yellow-200 font-semibold text-xl mb-2">{{ $t('domain.notFound') }}</div>
      <div class="text-yellow-600 dark:text-yellow-300 text-sm mb-6">{{ $t('domain.domainNotConfigured', { domain }) }}</div>
      <router-link 
        to="/home" 
        class="inline-flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200"
      >
        {{ $t('domain.goToPersonalCalendars') }}
      </router-link>
    </div>
  </div>

  <!-- Success: Show CalendarView with Domain Context -->
  <CalendarView 
    v-else-if="calendarId" 
    :id="calendarId" 
    :domain-context="domainConfig" 
  />
</template>

<script>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import CalendarView from './CalendarView.vue'
import { useApiCall } from '../composables/useApiCall'

export default {
  name: 'DomainView',
  components: {
    CalendarView
  },
  props: {
    domain: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const { get, post, loading, error } = useApiCall()

    const domainConfig = ref(null)
    const calendarId = ref(null)

    // Find or create calendar for domain
    const findOrCreateDomainCalendar = async (domainConfig) => {
      try {
        // First, try to find the domain calendar with proper ID format
        const expectedDomainCalendarId = `cal_domain_${props.domain}`
        const calendarsResult = await get('/api/calendars')
        if (calendarsResult.success) {
          // Look for domain calendar first (preferred)
          const domainCalendar = calendarsResult.data.calendars.find(
            cal => cal.id === expectedDomainCalendarId
          )
          
          if (domainCalendar) {
            return domainCalendar.id
          }
          
          // Fallback: look for any calendar with this URL
          const existingCalendar = calendarsResult.data.calendars.find(
            cal => cal.url === domainConfig.calendar_url
          )
          
          if (existingCalendar) {
            return existingCalendar.id
          }
        }

        // If not found, create new calendar for this domain
        const createResult = await post('/api/calendars', {
          name: domainConfig.name,
          url: domainConfig.calendar_url
        })

        if (createResult.success) {
          return createResult.data.id
        }
      } catch (err) {
        console.error('Failed to find/create domain calendar:', err)
      }
      
      return null
    }

    // Load domain configuration and find calendar
    const loadDomainData = async () => {
      try {
        // Load domain configuration
        const domainResult = await get(`/api/domains/${props.domain}`)
        if (domainResult.success) {
          domainConfig.value = domainResult.data
          
          // Find or create calendar for this domain
          const foundCalendarId = await findOrCreateDomainCalendar(domainConfig.value)
          calendarId.value = foundCalendarId
        }
      } catch (err) {
        console.error('Failed to load domain data:', err)
      }
    }

    // Load data on mount
    onMounted(() => {
      loadDomainData()
    })

    return {
      domainConfig,
      calendarId,
      loading,
      error,
      domain: props.domain
    }
  }
}
</script>