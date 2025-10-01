<template>
  <!-- Loading State -->
  <div v-if="loading" class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <!-- Header with gradient background matching admin cards -->
      <div class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center gap-3">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-3 border-blue-600 border-t-transparent"></div>
          <div class="flex-1">
            <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-gray-100 mb-1">
              🌐 {{ $t('domain.loadingDomainCalendar') }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ $t('common.pleaseWait') }}
            </p>
          </div>
        </div>
      </div>
      
      <!-- Content area -->
      <div class="p-6 text-center">
        <div class="text-6xl mb-4">📊</div>
        <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
          Preparing your domain calendar interface...
        </p>
      </div>
    </div>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <!-- Header with gradient background matching admin cards -->
      <div class="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-red-200 dark:border-red-700">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
            <span class="text-red-600 dark:text-red-400 text-xl">⚠️</span>
          </div>
          <div class="flex-1">
            <h3 class="text-lg sm:text-xl font-bold text-red-800 dark:text-red-200 mb-1">
              🌐 Domain Access Error
            </h3>
            <p class="text-sm text-red-600 dark:text-red-300">
              Unable to load domain calendar
            </p>
          </div>
        </div>
      </div>
      
      <!-- Content area -->
      <div class="p-6">
        <div class="text-center mb-6">
          <div class="text-6xl mb-4">🔗</div>
          <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
            <p class="text-red-800 dark:text-red-200 font-medium mb-2">{{ $t('messages.errorDetails') }}</p>
            <p class="text-red-700 dark:text-red-300 text-sm leading-relaxed">{{ error }}</p>
          </div>
        </div>
        
        <!-- Action Button -->
        <div class="text-center">
          <router-link 
            to="/home" 
            class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-sm hover:shadow-md"
          >
            <span class="text-lg">🏠</span>
            {{ $t('domain.goToPersonalCalendars') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>

  <!-- Domain Not Found -->
  <div v-else-if="!domainConfig" class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <!-- Header with gradient background matching admin cards -->
      <div class="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-amber-200 dark:border-amber-700">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
            <span class="text-amber-600 dark:text-amber-400 text-xl">🔍</span>
          </div>
          <div class="flex-1">
            <h3 class="text-lg sm:text-xl font-bold text-amber-800 dark:text-amber-200 mb-1">
              🌐 {{ $t('domain.notFound') }}
            </h3>
            <p class="text-sm text-amber-600 dark:text-amber-300">
              Domain configuration not available
            </p>
          </div>
        </div>
      </div>
      
      <!-- Content area -->
      <div class="p-6 text-center">
        <div class="text-6xl mb-6">🌐</div>
        <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800 mb-6">
          <p class="text-amber-800 dark:text-amber-200 font-medium mb-2">{{ $t('messages.domainStatus') }}</p>
          <p class="text-amber-700 dark:text-amber-300 text-sm leading-relaxed">{{ $t('domain.domainNotConfigured', { domain }) }}</p>
        </div>
        
        <!-- Action Button -->
        <router-link 
          to="/home" 
          class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-sm hover:shadow-md"
        >
          <span class="text-lg">🏠</span>
          {{ $t('domain.goToPersonalCalendars') }}
        </router-link>
      </div>
    </div>
  </div>

  <!-- Success: Show CalendarView with Domain Context -->
  <CalendarView 
    v-else-if="calendarId" 
    :id="calendarId" 
    :domain-context="domainConfig?.data" 
  />
</template>

<script>
import { ref, onMounted, defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHTTP } from '../composables/useHTTP'
import { API_ENDPOINTS } from '../constants/api'

// Preload CalendarView chunk immediately when DomainView loads
// This reduces the waterfall effect and improves LCP
const CalendarView = defineAsyncComponent(() => import('./CalendarView.vue'))

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
    const { get, post, loading, error } = useHTTP()

    const domainConfig = ref(null)
    const calendarId = ref(null)

    // Domain calendars use direct endpoints - no need to search in user calendar lists
    const findDomainCalendar = async (domainConfig) => {
      // Return the correct domain calendar ID format that matches backend database
      const domainCalendarId = `cal_domain_${props.domain}`
      console.log(`✅ Using domain calendar: ${domainCalendarId}`)
      console.log('💡 Domain events loaded directly from domain endpoint')
      return domainCalendarId
    }

    // Load domain configuration and find calendar
    const loadDomainData = async () => {
      try {
        // Load domain configuration
        const domainResult = await get(`/domains/${props.domain}`)
        if (domainResult.success) {
          domainConfig.value = domainResult.data
          
          // Find domain calendar (system-managed)
          const foundCalendarId = await findDomainCalendar(domainConfig.value)
          calendarId.value = foundCalendarId
        }
      } catch (err) {
        console.error('Failed to load domain data:', err)
      }
    }

    // Load data on mount
    onMounted(() => {
      // Start prefetching CalendarView chunk immediately in parallel with domain data
      // This reduces waterfall: DomainView -> domain API -> CalendarView load -> events API
      // to: DomainView -> (domain API || CalendarView load) -> events API
      import('./CalendarView.vue').catch(() => {
        // Prefetch failed, but component will load on demand anyway
      })

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