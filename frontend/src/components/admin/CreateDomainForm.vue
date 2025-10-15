<template>
  <div v-if="showForm" class="p-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <!-- Domain Key -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Domain Key *</label>
        <input
          v-model="newDomain.domain_key"
          @input="autoFillDisplayName"
          type="text"
          placeholder="company-events"
          class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
        />
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Lowercase, hyphens allowed</p>
      </div>

      <!-- Calendar URL -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Calendar URL *</label>
        <input
          v-model="newDomain.calendar_url"
          @paste="handleCalendarUrlPaste"
          @blur="handleCalendarUrlBlur"
          type="url"
          placeholder="https://example.com/calendar.ics"
          class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
        />
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">iCal feed URL (auto-previews on paste)</p>
      </div>

      <!-- Admin Password -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Admin Password *</label>
        <div class="relative">
          <input
            v-model="newDomain.admin_password"
            :type="showAdminPassword ? 'text' : 'password'"
            placeholder="Min 4 characters"
            class="w-full px-3 py-2.5 pr-10 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          />
          <button
            v-if="newDomain.admin_password"
            type="button"
            @click="showAdminPassword = !showAdminPassword"
            :aria-label="showAdminPassword ? 'Hide password' : 'Show password'" class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            :title="showAdminPassword ? 'Hide' : 'Show'"
          >
            <svg aria-hidden="true" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="showAdminPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- User Password -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">User Password (Optional)</label>
        <div class="relative">
          <input
            v-model="newDomain.user_password"
            :type="showUserPassword ? 'text' : 'password'"
            placeholder="Leave blank if none"
            class="w-full px-3 py-2.5 pr-10 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          />
          <button
            v-if="newDomain.user_password"
            type="button"
            @click="showUserPassword = !showUserPassword"
            :aria-label="showUserPassword ? 'Hide password' : 'Show password'" class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            :title="showUserPassword ? 'Hide' : 'Show'"
          >
            <svg aria-hidden="true" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="showUserPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Preview Button -->
    <button
      v-if="newDomain.calendar_url"
      @click="previewCalendar"
      :disabled="preview.loading"
      class="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-4 py-2.5 rounded-lg font-medium transition-all shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2 mb-3"
    >
      <svg v-if="!preview.loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
      </svg>
      <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      {{ preview.loading ? 'Loading Preview...' : 'Preview Calendar' }}
    </button>

    <!-- Preview Display -->
    <div v-if="preview.data" class="mb-4">
      <!-- Error State -->
      <div v-if="preview.data.error" class="bg-red-50 dark:bg-red-900/30 rounded-lg p-4 border-2 border-red-200 dark:border-red-700">
        <div class="flex items-start gap-3">
          <svg aria-hidden="true" class="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div>
            <p class="font-semibold text-red-800 dark:text-red-200 mb-1">Calendar Error</p>
            <p class="text-sm text-red-700 dark:text-red-300">{{ preview.data.error }}</p>
            <p class="text-xs text-red-600 dark:text-red-400 mt-2">This URL cannot be used to create a domain.</p>
          </div>
        </div>
      </div>

      <!-- Success State -->
      <div v-else class="bg-green-50 dark:bg-green-900/30 rounded-lg p-4 border-2 border-green-200 dark:border-green-700">
        <div class="flex items-start gap-3 mb-3">
          <svg aria-hidden="true" class="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div class="flex-1">
            <p class="font-semibold text-green-800 dark:text-green-200 mb-1">Valid Calendar</p>
            <p class="text-sm text-green-700 dark:text-green-300">Found {{ preview.data.event_count }} event{{ preview.data.event_count !== 1 ? 's' : '' }}</p>
          </div>
        </div>

        <!-- Event Preview -->
        <div class="space-y-2">
          <p class="text-xs font-semibold text-green-700 dark:text-green-300 mb-2">Preview (first {{ Math.min(5, preview.data.events.length) }} events):</p>
          <div v-for="(event, index) in preview.data.events.slice(0, 5)" :key="index" class="bg-white dark:bg-gray-800 rounded p-2 text-sm sm:text-xs">
            <p class="font-semibold text-gray-900 dark:text-gray-100">{{ event.title }}</p>
            <p class="text-gray-600 dark:text-gray-400" v-if="event.start_time">{{ event.start_time }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Button -->
    <button
      @click="createDomain"
      :disabled="creatingDomain || !newDomain.domain_key || !newDomain.calendar_url || !newDomain.admin_password || newDomain.admin_password.length < 4"
      class="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-4 py-3 rounded-lg font-semibold transition-all shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
    >
      <svg v-if="!creatingDomain" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
      </svg>
      <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      {{ creatingDomain ? 'Creating Domain...' : 'Create Domain' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { API_BASE_URL } from '../../constants/api'
import { useNotification } from '../../composables/useNotification'

const { t } = useI18n()
const notify = useNotification()

// Props
defineProps({
  showForm: {
    type: Boolean,
    required: true
  }
})

// Emits
const emit = defineEmits(['domain-created'])

// State
const creatingDomain = ref(false)
const newDomain = ref({
  domain_key: '',
  name: '',
  calendar_url: '',
  admin_password: '',
  user_password: ''
})

const showAdminPassword = ref(false)
const showUserPassword = ref(false)

const preview = ref({
  loading: false,
  data: null
})

// Methods
const autoFillDisplayName = () => {
  const key = newDomain.value.domain_key.trim()
  if (key) {
    newDomain.value.name = key
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }
}

const previewCalendar = async () => {
  if (!newDomain.value.calendar_url || !newDomain.value.calendar_url.startsWith('http')) {
    return
  }

  preview.value.loading = true
  preview.value.data = null

  try {
    const response = await axios.post(`${API_BASE_URL}/api/ical/preview`, {
      calendar_url: newDomain.value.calendar_url
    })
    preview.value.data = response.data
  } catch (error) {
    console.error('Failed to preview calendar:', error)
    preview.value.data = {
      event_count: 0,
      events: [],
      error: error.response?.data?.detail || error.message || 'Failed to load preview'
    }
  } finally {
    preview.value.loading = false
  }
}

let previewTimeout = null

const handleCalendarUrlPaste = () => {
  setTimeout(() => {
    previewCalendar()
  }, 100)
}

const handleCalendarUrlBlur = () => {
  clearTimeout(previewTimeout)
  previewTimeout = setTimeout(() => {
    if (newDomain.value.calendar_url && !preview.value.data) {
      previewCalendar()
    }
  }, 300)
}

const createDomain = async () => {
  // If preview hasn't been run yet, or if URL changed since last preview, run it first
  if (!preview.value.data || preview.value.loading) {
    await previewCalendar()

    // If preview shows an error, don't proceed
    if (preview.value.data?.error) {
      notify.error('Cannot create domain: ' + preview.value.data.error)
      return
    }
  }

  creatingDomain.value = true

  try {
    const token = localStorage.getItem('admin_token')

    // Auto-generate display name if not set
    if (!newDomain.value.name) {
      autoFillDisplayName()
    }

    const payload = {
      domain_key: newDomain.value.domain_key.trim().toLowerCase(),
      name: newDomain.value.name.trim(),
      calendar_url: newDomain.value.calendar_url.trim(),
      admin_password: newDomain.value.admin_password
    }

    // Add optional user password if provided
    if (newDomain.value.user_password) {
      payload.user_password = newDomain.value.user_password
    }

    const response = await axios.post(
      `${API_BASE_URL}/api/admin/domains`,
      payload,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    // Success - reset form
    notify.success(t('admin.domains.createSuccess', { domainKey: response.data.domain_key }))

    // Reset form and preview
    newDomain.value = {
      domain_key: '',
      name: '',
      calendar_url: '',
      admin_password: '',
      user_password: ''
    }
    preview.value = {
      loading: false,
      data: null
    }
    showAdminPassword.value = false
    showUserPassword.value = false

    // Emit event to parent
    emit('domain-created')

  } catch (error) {
    console.error('Failed to create domain:', error)

    if (error.response?.status === 409) {
      notify.error(t('admin.domains.createErrorDuplicate', { domainKey: newDomain.value.domain_key }))
    } else if (error.response?.status === 404) {
      notify.error(t('admin.domains.createErrorUserNotFound', { username: newDomain.value.owner_username }))
    } else if (error.response?.status === 422) {
      notify.error(t('admin.domains.createErrorValidation', { detail: error.response?.data?.detail || t('admin.domains.invalidFormat') }))
    } else {
      notify.error(t('admin.domains.createError', { detail: error.response?.data?.detail || error.message }))
    }
  } finally {
    creatingDomain.value = false
  }
}
</script>
