<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-500 transition-all shadow-sm hover:shadow-md">
    <!-- Request Header -->
    <div class="px-5 py-4 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800 border-b-2 border-gray-100 dark:border-gray-700">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-lg flex items-center justify-center shadow-md">
          <span class="text-white font-bold text-lg">{{ request.username.charAt(0).toUpperCase() }}</span>
        </div>
        <div>
          <h3 class="font-bold text-gray-900 dark:text-gray-100">{{ request.username }}</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ request.email }}</p>
        </div>
      </div>
      <div class="text-xs text-gray-500 dark:text-gray-400">
        {{ formatDate(request.created_at) }}
      </div>
    </div>

    <!-- Request Details -->
    <div class="p-5">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <!-- Requested Domain -->
        <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-200 dark:border-purple-700">
          <p class="text-xs font-semibold text-purple-700 dark:text-purple-300 mb-1">REQUESTED DOMAIN</p>
          <p class="font-mono font-bold text-purple-900 dark:text-purple-100">{{ request.requested_domain_key }}</p>
        </div>

        <!-- Calendar URL -->
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-700">
          <p class="text-xs font-semibold text-blue-700 dark:text-blue-300 mb-1">CALENDAR URL</p>
          <a :href="request.calendar_url" target="_blank" class="text-sm text-blue-600 dark:text-blue-400 hover:underline break-all">
            {{ request.calendar_url }}
          </a>
        </div>
      </div>

      <!-- Description -->
      <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-600">
        <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">DESCRIPTION</p>
        <p class="text-sm text-gray-700 dark:text-gray-300">{{ request.description }}</p>
      </div>

      <!-- iCal Preview -->
      <div class="mb-4">
        <button
          @click="togglePreviewState"
          class="text-sm font-semibold text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 flex items-center gap-2 transition-colors"
        >
          <svg aria-hidden="true" class="w-4 h-4" :class="{ 'rotate-90': previewState.expanded }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
          <span>{{ previewState.expanded ? 'Hide' : 'Show' }} Calendar Preview</span>
        </button>

        <div v-if="previewState.expanded" class="mt-3">
          <!-- Loading State -->
          <div v-if="previewState.loading" class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border-2 border-blue-200 dark:border-blue-700">
            <div class="flex items-center gap-3 sm:gap-2">
              <div class="inline-block w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span class="text-sm font-medium text-blue-700 dark:text-blue-300">Loading events...</span>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="previewState.data?.error" class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border-2 border-red-200 dark:border-red-700">
            <div class="flex items-center gap-2 mb-2">
              <svg aria-hidden="true" class="w-6 h-6 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
              </svg>
              <span class="font-bold text-red-800 dark:text-red-200">Calendar Error</span>
            </div>
            <p class="text-sm text-red-700 dark:text-red-300">{{ previewState.data.error }}</p>
          </div>

          <!-- Success State -->
          <div v-else-if="previewState.data" class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border-2 border-green-200 dark:border-green-700">
            <div class="flex items-center gap-2 mb-3">
              <svg aria-hidden="true" class="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="font-bold text-green-800 dark:text-green-200">Found {{ previewState.data.event_count }} event{{ previewState.data.event_count !== 1 ? 's' : '' }}</span>
            </div>
            <div v-if="previewState.data.events.length > 0" class="space-y-2">
              <p class="text-xs font-bold text-green-700 dark:text-green-300 mb-2">PREVIEW (first {{ Math.min(5, previewState.data.events.length) }} events)</p>
              <div v-for="(event, idx) in previewState.data.events.slice(0, 5)" :key="idx" class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-green-200 dark:border-green-700">
                <p class="font-semibold text-gray-900 dark:text-gray-100 mb-1">{{ event.title }}</p>
                <p v-if="event.start_time" class="text-xs text-gray-600 dark:text-gray-400">{{ new Date(event.start_time).toLocaleDateString() }} {{ new Date(event.start_time).toLocaleTimeString() }}</p>
                <p v-if="event.location" class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">{{ event.location }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-3 pt-4 border-t-2 border-gray-100 dark:border-gray-700">
        <button
          @click="handleApprove"
          :disabled="processing || !canApprove"
          :title="approvalDisabledReason"
          class="flex-1 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-4 py-3 rounded-lg font-bold transition-all disabled:cursor-not-allowed shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
        >
          <svg aria-hidden="true" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <span>{{ $t('admin.panel.approve') || 'Approve' }}</span>
        </button>
        <button
          @click="handleReject"
          :disabled="processing"
          class="flex-1 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-4 py-3 rounded-lg font-bold transition-all disabled:cursor-not-allowed shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
        >
          <svg aria-hidden="true" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
          <span>{{ $t('admin.panel.reject') || 'Reject' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../../constants/api'

const props = defineProps({
  request: {
    type: Object,
    required: true
  },
  formatDate: {
    type: Function,
    required: true
  },
  processing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['approve', 'reject'])

// Preview state
const previewState = ref({
  expanded: false,
  loading: false,
  data: null
})

const togglePreviewState = async () => {
  // Toggle expansion
  previewState.value.expanded = !previewState.value.expanded

  // If expanding and no data loaded yet, fetch it
  if (previewState.value.expanded && !previewState.value.data) {
    previewState.value.loading = true

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ical/preview`, {
        calendar_url: props.request.calendar_url
      })

      previewState.value.data = response.data
    } catch (error) {
      previewState.value.data = {
        event_count: 0,
        events: [],
        error: `Failed to load preview: ${error.response?.data?.detail || error.message}`
      }
    } finally {
      previewState.value.loading = false
    }
  }
}

const canApprove = computed(() => {
  // If preview was checked and has error or 0 events, block approval
  if (previewState.value.data) {
    if (previewState.value.data.error || previewState.value.data.event_count === 0) {
      return false
    }
  }

  return true
})

const approvalDisabledReason = computed(() => {
  if (previewState.value.data?.error) {
    return `Cannot approve: ${previewState.value.data.error}`
  }

  if (previewState.value.data?.event_count === 0) {
    return 'Cannot approve: Calendar has no events'
  }

  return ''
})

const handleApprove = () => {
  emit('approve', props.request.id)
}

const handleReject = () => {
  emit('reject', props.request.id)
}
</script>
