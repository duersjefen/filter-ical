<template>
  <AdminCardWrapper
    title="Calendar Permissions"
    subtitle="Manage user access to calendars and domains"
    icon="🔐"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
    <!-- Filter Bar -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <select
        v-model="typeFilter"
        class="px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 transition-all"
        @change="handleFilterChange"
      >
        <option value="">All Calendars</option>
        <option value="user">User Calendars</option>
        <option value="domain">Domain Calendars</option>
      </select>

      <button
        @click="handleRefresh"
        :disabled="loading"
        class="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg font-semibold transition-all shadow-md hover:shadow-lg disabled:shadow-none flex items-center gap-2"
      >
        <svg
          class="w-5 h-5"
          :class="{ 'animate-spin': loading }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        <span class="hidden sm:inline">Refresh</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && calendars.length === 0" class="py-12 text-center">
      <div class="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading calendars...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && calendars.length === 0" class="py-12 text-center">
      <div class="w-20 h-20 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
      </div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
        No calendars found
      </h3>
      <p class="text-gray-600 dark:text-gray-400">
        {{ typeFilter ? 'Try changing the filter' : 'No calendars exist yet' }}
      </p>
    </div>

    <!-- Calendars List -->
    <div v-else class="space-y-4">
      <div
        v-for="calendar in calendars"
        :key="calendar.id"
        class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-500 transition-all shadow-sm hover:shadow-md overflow-hidden"
      >
        <!-- Calendar Header -->
        <div
          @click="toggleCalendar(calendar.id)"
          class="px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:from-gray-100 hover:to-gray-50 dark:hover:from-gray-700 dark:hover:to-gray-700 transition-all"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <h4 class="text-base font-bold text-gray-900 dark:text-gray-100 truncate">
                {{ calendar.name || calendar.domain_key || `Calendar ${calendar.id}` }}
              </h4>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold flex-shrink-0"
                :class="calendar.type === 'domain'
                  ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'"
              >
                {{ calendar.type }}
              </span>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Owner: {{ calendar.owner_username || 'No owner' }}
              <span class="mx-2">•</span>
              {{ (permissions[calendar.id] || []).length }} permission(s)
            </div>
          </div>
          <svg
            class="w-5 h-5 text-gray-600 dark:text-gray-400 transition-transform flex-shrink-0"
            :class="expandedCalendars[calendar.id] ? 'rotate-90' : ''"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </div>

        <!-- Calendar Permissions (Expandable) -->
        <div v-if="expandedCalendars[calendar.id]" class="p-4">
          <!-- Grant Permission Form -->
          <div class="mb-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-700">
            <h5 class="text-sm font-bold text-gray-900 dark:text-gray-100 mb-3">Grant New Permission</h5>
            <div class="flex flex-col sm:flex-row gap-2">
              <div class="flex-1 relative">
                <input
                  v-model="grantForm[calendar.id].searchQuery"
                  type="text"
                  placeholder="Search for user..."
                  class="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:border-green-500 dark:focus:border-green-400 transition-all"
                  @input="handleUserSearch(calendar.id)"
                />
                <!-- Search Results Dropdown -->
                <div
                  v-if="grantForm[calendar.id].searchResults.length > 0"
                  class="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto"
                >
                  <button
                    v-for="user in grantForm[calendar.id].searchResults"
                    :key="user.id"
                    @click="selectUser(calendar.id, user)"
                    class="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                  >
                    <div class="font-semibold text-gray-900 dark:text-gray-100">{{ user.username }}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">{{ user.email || 'No email' }}</div>
                  </button>
                </div>
              </div>
              <select
                v-model="grantForm[calendar.id].level"
                class="px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="read">Read</option>
                <option value="write">Write</option>
              </select>
              <button
                @click="handleGrantPermission(calendar.id)"
                :disabled="!grantForm[calendar.id].selectedUserId"
                class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-semibold transition-all shadow-md hover:shadow-lg disabled:shadow-none whitespace-nowrap"
              >
                Grant
              </button>
            </div>
            <div v-if="grantForm[calendar.id].selectedUserId" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Selected: <span class="font-semibold">{{ grantForm[calendar.id].selectedUsername }}</span>
            </div>
          </div>

          <!-- Permissions List -->
          <div v-if="loadingPermissions[calendar.id]" class="py-8 text-center">
            <div class="inline-block w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <div v-else-if="(permissions[calendar.id] || []).length === 0" class="py-8 text-center text-gray-500 dark:text-gray-400">
            No permissions granted yet
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="permission in permissions[calendar.id]"
              :key="permission.user_id"
              class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
            >
              <div class="flex-1">
                <div class="font-semibold text-gray-900 dark:text-gray-100">{{ permission.username }}</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">{{ permission.email || 'No email' }}</div>
              </div>
              <div class="flex items-center gap-3">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
                  :class="permission.level === 'write'
                    ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200'
                    : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'"
                >
                  {{ permission.level }}
                </span>
                <button
                  @click="handleRevokePermission(calendar.id, permission.user_id, permission.username)"
                  class="p-2 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                  title="Revoke permission"
                >
                  <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination.totalPages > 1" class="flex items-center justify-between mt-6 pt-4 border-t-2 border-gray-100 dark:border-gray-700">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Showing {{ ((pagination.page - 1) * pagination.limit) + 1 }} to {{ Math.min(pagination.page * pagination.limit, pagination.total) }} of {{ pagination.total }} calendars
      </div>
      <div class="flex gap-2">
        <button
          @click="handlePreviousPage"
          :disabled="pagination.page === 1 || loading"
          class="px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          Previous
        </button>
        <button
          @click="handleNextPage"
          :disabled="pagination.page >= pagination.totalPages || loading"
          class="px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <ConfirmDialog
      ref="confirmDialog"
      :title="confirmDialogData.title"
      :message="confirmDialogData.message"
      :confirmText="confirmDialogData.confirmText"
      @confirm="confirmDialogData.onConfirm"
    />
  </AdminCardWrapper>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AdminCardWrapper from './AdminCardWrapper.vue'
import ConfirmDialog from '../shared/ConfirmDialog.vue'
import { useAdminCalendars } from '@/composables/useAdminCalendars'
import { useNotification } from '@/composables/useNotification'

const props = defineProps({
  expanded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle'])

const notify = useNotification()
const {
  calendars,
  permissions,
  loading,
  pagination,
  listCalendars,
  getCalendarPermissions,
  grantPermission,
  revokePermission,
  searchUsers
} = useAdminCalendars()

// Filter and expand state
const typeFilter = ref('')
const expandedCalendars = reactive({})
const loadingPermissions = reactive({})

// Grant permission form state (per calendar)
const grantForm = reactive({})
let searchTimeouts = {}

// Confirm dialog state
const confirmDialog = ref(null)
const confirmDialogData = ref({
  title: '',
  message: '',
  confirmText: '',
  onConfirm: null
})

// Load calendars on mount
onMounted(() => {
  loadCalendarsList()
})

async function loadCalendarsList() {
  await listCalendars(pagination.value.page, pagination.value.limit, typeFilter.value)

  // Initialize grant forms for all calendars
  calendars.value.forEach(calendar => {
    if (!grantForm[calendar.id]) {
      grantForm[calendar.id] = {
        searchQuery: '',
        searchResults: [],
        selectedUserId: null,
        selectedUsername: '',
        level: 'read'
      }
    }
  })
}

function handleFilterChange() {
  pagination.value.page = 1
  loadCalendarsList()
}

function handleRefresh() {
  loadCalendarsList()
}

function handlePreviousPage() {
  if (pagination.value.page > 1) {
    pagination.value.page -= 1
    loadCalendarsList()
  }
}

function handleNextPage() {
  if (pagination.value.page < pagination.value.totalPages) {
    pagination.value.page += 1
    loadCalendarsList()
  }
}

async function toggleCalendar(calendarId) {
  expandedCalendars[calendarId] = !expandedCalendars[calendarId]

  // Load permissions when expanding
  if (expandedCalendars[calendarId] && !permissions.value[calendarId]) {
    loadingPermissions[calendarId] = true
    await getCalendarPermissions(calendarId)
    loadingPermissions[calendarId] = false
  }
}

function handleUserSearch(calendarId) {
  clearTimeout(searchTimeouts[calendarId])

  searchTimeouts[calendarId] = setTimeout(async () => {
    const query = grantForm[calendarId].searchQuery
    if (query && query.length >= 2) {
      const result = await searchUsers(query)
      if (result.success) {
        grantForm[calendarId].searchResults = result.data
      }
    } else {
      grantForm[calendarId].searchResults = []
    }
  }, 300)
}

function selectUser(calendarId, user) {
  grantForm[calendarId].selectedUserId = user.id
  grantForm[calendarId].selectedUsername = user.username
  grantForm[calendarId].searchQuery = user.username
  grantForm[calendarId].searchResults = []
}

async function handleGrantPermission(calendarId) {
  const form = grantForm[calendarId]

  if (!form.selectedUserId) {
    notify.error('Please select a user')
    return
  }

  const result = await grantPermission(calendarId, form.selectedUserId, form.level)

  if (result.success) {
    notify.success(`Permission granted to ${form.selectedUsername}`)

    // Reset form
    form.searchQuery = ''
    form.searchResults = []
    form.selectedUserId = null
    form.selectedUsername = ''
    form.level = 'read'

    // Reload permissions for this calendar
    await getCalendarPermissions(calendarId)
  } else {
    notify.error(result.error || 'Failed to grant permission')
  }
}

function handleRevokePermission(calendarId, userId, username) {
  confirmDialogData.value = {
    title: 'Revoke Permission',
    message: `Are you sure you want to revoke permission for "${username}"? They will no longer be able to access this calendar.`,
    confirmText: 'Revoke',
    onConfirm: async () => {
      const result = await revokePermission(calendarId, userId)

      if (result.success) {
        notify.success(`Permission revoked for ${username}`)
      } else {
        notify.error(result.error || 'Failed to revoke permission')
      }
    }
  }
  confirmDialog.value.open()
}
</script>
