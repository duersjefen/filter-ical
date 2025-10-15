<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-500 transition-all shadow-sm hover:shadow-md">

    <!-- Header with Domain Name & Actions -->
    <div class="px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800 border-b-2 border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 truncate">{{ domain.domain_key }}</h3>
      <div class="flex items-center gap-3 sm:gap-2">
        <a :href="`/${domain.domain_key}`" target="_blank" :aria-label="`View calendar for ${domain.domain_key}`" class="p-3 sm:p-2 min-w-[44px] min-h-[44px] touch-manipulation hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors flex items-center justify-center" title="View Calendar">
          <svg aria-hidden="true" class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
          </svg>
        </a>
        <a :href="`/${domain.domain_key}/admin`" target="_blank" :aria-label="`Open admin panel for ${domain.domain_key}`" class="p-3 sm:p-2 min-w-[44px] min-h-[44px] touch-manipulation bg-purple-50 hover:bg-purple-100 dark:bg-purple-900/30 dark:hover:bg-purple-800/50 rounded-lg transition-colors flex items-center justify-center" title="Manage Domain">
          <svg aria-hidden="true" class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </a>
        <button @click="$emit('delete-domain')" :disabled="processing" :aria-label="`Delete domain ${domain.domain_key}`" class="p-3 sm:p-2 min-w-[44px] min-h-[44px] touch-manipulation bg-red-50 hover:bg-red-100 dark:bg-red-900/30 dark:hover:bg-red-800/50 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center" title="Delete Domain">
          <svg aria-hidden="true" class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Password Management: Side by Side -->
    <div class="p-4 sm:p-6 grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">

      <!-- Admin Password -->
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
            <svg aria-hidden="true" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
            Admin
          </span>
          <span v-if="domain.admin_password_set" class="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded">Protected</span>
          <span v-else class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs font-medium rounded">None</span>
        </div>

        <div v-if="editingDomain !== domain.domain_key || editingType !== 'admin'">
          <div class="flex flex-col gap-1.5">
            <button @click="startEditing(domain.domain_key, 'admin')" class="px-3 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all">
              {{ domain.admin_password_set ? 'Change' : 'Set Password' }}
            </button>
            <button v-if="domain.admin_password_set" @click="removePassword(domain.domain_key, 'admin')" class="px-3 py-2 text-sm font-medium bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all">
              Remove
            </button>
          </div>
        </div>

        <div v-else class="space-y-2">
          <div class="relative">
            <input v-model="newPassword" :type="showPassword ? 'text' : 'password'" placeholder="Enter password" class="w-full px-3 py-2 pr-12 text-sm border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 dark:focus:ring-purple-800" />
            <button
              v-if="newPassword"
              type="button"
              @click="showPassword = !showPassword"
              :aria-label="showPassword ? 'Hide password' : 'Show password'" class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              :title="showPassword ? 'Hide password' : 'Show password'"
            >
              <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
          </div>
          <div class="flex gap-1.5">
            <button @click="savePassword(domain.domain_key, 'admin')" class="flex-1 px-3 py-2 text-sm font-medium bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all">Save</button>
            <button @click="cancelEditing" class="flex-1 px-3 py-2 text-sm font-medium bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-all">Cancel</button>
          </div>
        </div>
      </div>

      <!-- User Password -->
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
            <svg aria-hidden="true" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            User
          </span>
          <span v-if="domain.user_password_set" class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-medium rounded">Protected</span>
          <span v-else class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs font-medium rounded">None</span>
        </div>

        <div v-if="editingDomain !== domain.domain_key || editingType !== 'user'">
          <div class="flex flex-col gap-1.5">
            <button @click="startEditing(domain.domain_key, 'user')" class="px-3 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all">
              {{ domain.user_password_set ? 'Change' : 'Set Password' }}
            </button>
            <button v-if="domain.user_password_set" @click="removePassword(domain.domain_key, 'user')" class="px-3 py-2 text-sm font-medium bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all">
              Remove
            </button>
          </div>
        </div>

        <div v-else class="space-y-2">
          <div class="relative">
            <input v-model="newPassword" :type="showPassword ? 'text' : 'password'" placeholder="Enter password" class="w-full px-3 py-2 pr-12 text-sm border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:focus:ring-blue-800" />
            <button
              v-if="newPassword"
              type="button"
              @click="showPassword = !showPassword"
              :aria-label="showPassword ? 'Hide password' : 'Show password'" class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              :title="showPassword ? 'Hide password' : 'Show password'"
            >
              <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
          </div>
          <div class="flex gap-1.5">
            <button @click="savePassword(domain.domain_key, 'user')" class="flex-1 px-3 py-2 text-sm font-medium bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all">Save</button>
            <button @click="cancelEditing" class="flex-1 px-3 py-2 text-sm font-medium bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-all">Cancel</button>
          </div>
        </div>
      </div>

    </div>

    <!-- Owner Management -->
    <div class="px-4 pb-4 border-t-2 border-gray-100 dark:border-gray-700 pt-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
          <svg aria-hidden="true" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          Owner
        </span>
        <span v-if="domain.owner_username" class="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 text-xs font-medium rounded">
          {{ domain.owner_username }}
        </span>
        <span v-else class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs font-medium rounded">
          No owner
        </span>
      </div>

      <!-- Owner Search & Assign -->
      <div v-if="assigningOwner === domain.domain_key" class="space-y-2">
        <div class="relative">
          <input
            v-model="ownerSearchQuery"
            @input="searchUsers"
            type="text"
            placeholder="Search users..."
            class="w-full px-3 py-2 pr-8 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-indigo-500"
          />
          <svg v-if="searchingUsers" class="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 animate-spin text-gray-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <!-- Search Results -->
        <div v-if="userSearchResults.length > 0" class="max-h-40 overflow-y-auto bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-600">
          <button
            v-for="user in userSearchResults"
            :key="user.id"
            @click="assignOwner(domain.domain_key, user.id, user.username)"
            class="w-full px-3 py-2 text-left hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition text-sm"
          >
            <div class="font-semibold text-gray-900 dark:text-gray-100">{{ user.username }}</div>
            <div class="text-xs text-gray-500 dark:text-gray-400">{{ user.email || 'No email' }}</div>
          </button>
        </div>

        <div class="flex gap-2">
          <button
            @click="cancelOwnerAssignment"
            class="flex-1 px-3 py-2 text-sm font-medium bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition"
          >
            Cancel
          </button>
        </div>
      </div>

      <!-- Owner Actions -->
      <div v-else class="flex gap-2">
        <button
          @click="startOwnerAssignment(domain.domain_key)"
          class="flex-1 px-3 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
        >
          {{ domain.owner_username ? 'Change' : 'Assign' }}
        </button>
        <button
          v-if="domain.owner_username"
          @click="removeOwner(domain.domain_key)"
          class="flex-1 px-3 py-2 text-sm font-medium bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
        >
          Remove
        </button>
      </div>
    </div>
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
const props = defineProps({
  domain: {
    type: Object,
    required: true
  },
  processing: {
    type: Boolean,
    default: false
  },
  editingDomain: {
    type: String,
    default: null
  },
  editingType: {
    type: String,
    default: null
  },
  assigningOwner: {
    type: String,
    default: null
  }
})

// Emits
const emit = defineEmits(['delete-domain', 'refresh-domains', 'start-editing', 'cancel-editing', 'save-password', 'remove-password', 'start-owner-assignment', 'cancel-owner-assignment', 'assign-owner', 'remove-owner'])

// Local state
const newPassword = ref('')
const showPassword = ref(false)
const ownerSearchQuery = ref('')
const userSearchResults = ref([])
const searchingUsers = ref(false)
let searchTimeout = null

// Helper to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('admin_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

// Password management methods
const startEditing = (domainKey, type) => {
  emit('start-editing', domainKey, type)
  newPassword.value = ''
  showPassword.value = false
}

const cancelEditing = () => {
  emit('cancel-editing')
  newPassword.value = ''
  showPassword.value = false
}

const savePassword = async (domainKey, type) => {
  if (!newPassword.value || newPassword.value.length < 4) {
    notify.error(t('admin.domainAuth.passwordSettings.error.minLength') || 'Password must be at least 4 characters')
    return
  }

  try {
    const endpoint = `/api/admin/domains/${domainKey}/passwords`

    const payload = type === 'admin'
      ? { admin_password: newPassword.value }
      : { user_password: newPassword.value }

    await axios.patch(`${API_BASE_URL}${endpoint}`, payload, {
      headers: getAuthHeaders()
    })

    notify.success(t(`admin.domainAuth.passwordSettings.success.${type}Set`) || `${type === 'admin' ? 'Admin' : 'User'} password updated successfully`)
    cancelEditing()
    emit('refresh-domains')
  } catch (error) {
    notify.error(t(`admin.domainAuth.passwordSettings.error.${type}Set`) || `Failed to set password: ${error.message}`)
  }
}

const removePassword = (domainKey, type) => {
  emit('remove-password', domainKey, type)
}

// Owner management methods
const startOwnerAssignment = (domainKey) => {
  emit('start-owner-assignment', domainKey)
  ownerSearchQuery.value = ''
  userSearchResults.value = []
}

const cancelOwnerAssignment = () => {
  emit('cancel-owner-assignment')
  ownerSearchQuery.value = ''
  userSearchResults.value = []
}

const searchUsers = async () => {
  const query = ownerSearchQuery.value.trim()

  if (!query || query.length < 1) {
    userSearchResults.value = []
    return
  }

  // Debounce search
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    searchingUsers.value = true
    try {
      const token = localStorage.getItem('admin_token')
      const response = await axios.get(
        `${API_BASE_URL}/api/admin/users/search?q=${encodeURIComponent(query)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      userSearchResults.value = response.data.users
    } catch (error) {
      console.error('Failed to search users:', error)
      userSearchResults.value = []
    } finally {
      searchingUsers.value = false
    }
  }, 300)
}

const assignOwner = async (domainKey, userId, username) => {
  try {
    const token = localStorage.getItem('admin_token')
    await axios.patch(
      `${API_BASE_URL}/api/admin/domains/${domainKey}/owner`,
      { user_id: userId },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    notify.success(t('admin.domains.assignOwnerSuccess', { domainKey, username }))
    emit('assign-owner', domainKey, userId, username)
    cancelOwnerAssignment()
  } catch (error) {
    console.error('Failed to assign owner:', error)
    notify.error(t('admin.domains.assignOwnerError', { detail: error.response?.data?.detail || error.message }))
  }
}

const removeOwner = (domainKey) => {
  emit('remove-owner', domainKey)
}
</script>
