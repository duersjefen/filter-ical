<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <!-- Password Gate -->
    <div v-if="!isAuthenticated" class="min-h-screen flex items-center justify-center">
      <div class="max-w-md w-full">
        <div class="bg-gradient-to-br from-white via-white to-purple-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-purple-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
          <div class="flex items-center justify-center mb-6">
            <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-2xl flex items-center justify-center shadow-lg">
              <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
          </div>

          <h1 class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
            {{ $t('admin.panel.title') }}
          </h1>
          <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
            {{ $t('admin.panel.subtitle') }}
          </p>

          <!-- Error Message -->
          <div v-if="authError" class="bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-4 py-3 rounded-xl mb-4 border border-red-200 dark:border-red-700">
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <span class="font-semibold text-sm">{{ authError }}</span>
            </div>
          </div>

          <form @submit.prevent="authenticate" class="space-y-4">
            <div>
              <label for="admin-password" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
                {{ $t('admin.panel.password') }}
              </label>
              <input
                id="admin-password"
                v-model="password"
                type="password"
                class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-4 focus:ring-purple-100 dark:focus:ring-purple-900/50"
                :placeholder="$t('admin.panel.passwordPlaceholder')"
                required
                autofocus
              />
            </div>

            <button
              type="submit"
              :disabled="authenticating || !password"
              class="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 dark:from-purple-600 dark:to-purple-700 dark:hover:from-purple-700 dark:hover:to-purple-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none"
            >
              {{ authenticating ? $t('admin.panel.authenticating') : $t('admin.panel.login') }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Admin Panel Content -->
    <div v-else>
      <AppHeader
        :title="$t('admin.panel.domainRequests')"
        :subtitle="$t('admin.panel.manageRequests')"
        :back-button-text="$t('navigation.home')"
        :show-back-button="true"
        page-context="admin"
        @navigate-back="$router.push('/')"
      />

      <!-- Domains Overview (at top) -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800">
          <h2 class="text-lg font-bold text-gray-900 dark:text-gray-100">📋 All Domains</h2>
        </div>

        <div v-if="domainsLoading" class="p-8 text-center">
          <div class="inline-block w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
        </div>

        <div v-else-if="domains.length === 0" class="p-8 text-center">
          <p class="text-gray-600 dark:text-gray-400 text-sm">No domains found</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700">
              <tr>
                <th class="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300">Domain</th>
                <th class="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300">Admin Password</th>
                <th class="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300">User Password</th>
                <th class="px-4 py-2 text-center font-semibold text-gray-700 dark:text-gray-300">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="domain in domains" :key="domain.domain_key" class="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                <!-- Domain Name -->
                <td class="px-4 py-3">
                  <div class="font-semibold text-gray-900 dark:text-gray-100">{{ domain.domain_key }}</div>
                  <a :href="`/${domain.domain_key}`" target="_blank" class="text-xs text-purple-600 dark:text-purple-400 hover:underline">
                    View Calendar →
                  </a>
                </td>

                <!-- Admin Password -->
                <td class="px-4 py-3">
                  <div v-if="editingDomain !== domain.domain_key || editingType !== 'admin'">
                    <span v-if="domain.admin_password_set" class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-200">
                      🔐 {{ viewingPassword === `${domain.domain_key}-admin` && viewedPassword ? viewedPassword : 'Protected' }}
                    </span>
                    <span v-else class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                      No password
                    </span>
                    <button
                      v-if="domain.admin_password_set"
                      @click="viewPassword(domain.domain_key, 'admin')"
                      class="ml-2 text-xs text-green-600 dark:text-green-400 hover:underline"
                    >
                      {{ viewingPassword === `${domain.domain_key}-admin` ? 'Hide' : 'View' }}
                    </button>
                    <button
                      @click="startEditing(domain.domain_key, 'admin', domain.admin_password_set)"
                      class="ml-2 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      {{ domain.admin_password_set ? 'Change' : 'Set' }}
                    </button>
                  </div>
                  <div v-else class="flex gap-2">
                    <div class="flex-1 flex gap-1">
                      <input
                        v-model="newPassword"
                        :type="showPassword ? 'text' : 'password'"
                        placeholder="New password"
                        class="flex-1 px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
                      />
                      <button
                        @click="showPassword = !showPassword"
                        class="px-2 py-1 text-xs bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
                        :title="showPassword ? 'Hide password' : 'Show password'"
                      >
                        {{ showPassword ? '🙈' : '👁️' }}
                      </button>
                    </div>
                    <button @click="savePassword(domain.domain_key, 'admin')" class="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700">
                      Save
                    </button>
                    <button @click="cancelEditing" class="px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600">
                      Cancel
                    </button>
                  </div>
                  <button
                    v-if="domain.admin_password_set && editingDomain !== domain.domain_key"
                    @click="removePassword(domain.domain_key, 'admin')"
                    class="ml-2 text-xs text-red-600 dark:text-red-400 hover:underline"
                  >
                    Remove
                  </button>
                </td>

                <!-- User Password -->
                <td class="px-4 py-3">
                  <div v-if="editingDomain !== domain.domain_key || editingType !== 'user'">
                    <span v-if="domain.user_password_set" class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200">
                      👤 {{ viewingPassword === `${domain.domain_key}-user` && viewedPassword ? viewedPassword : 'Protected' }}
                    </span>
                    <span v-else class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                      No password
                    </span>
                    <button
                      v-if="domain.user_password_set"
                      @click="viewPassword(domain.domain_key, 'user')"
                      class="ml-2 text-xs text-green-600 dark:text-green-400 hover:underline"
                    >
                      {{ viewingPassword === `${domain.domain_key}-user` ? 'Hide' : 'View' }}
                    </button>
                    <button
                      @click="startEditing(domain.domain_key, 'user', domain.user_password_set)"
                      class="ml-2 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      {{ domain.user_password_set ? 'Change' : 'Set' }}
                    </button>
                  </div>
                  <div v-else class="flex gap-2">
                    <div class="flex-1 flex gap-1">
                      <input
                        v-model="newPassword"
                        :type="showPassword ? 'text' : 'password'"
                        placeholder="New password"
                        class="flex-1 px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
                      />
                      <button
                        @click="showPassword = !showPassword"
                        class="px-2 py-1 text-xs bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
                        :title="showPassword ? 'Hide password' : 'Show password'"
                      >
                        {{ showPassword ? '🙈' : '👁️' }}
                      </button>
                    </div>
                    <button @click="savePassword(domain.domain_key, 'user')" class="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700">
                      Save
                    </button>
                    <button @click="cancelEditing" class="px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600">
                      Cancel
                    </button>
                  </div>
                  <button
                    v-if="domain.user_password_set && editingDomain !== domain.domain_key"
                    @click="removePassword(domain.domain_key, 'user')"
                    class="ml-2 text-xs text-red-600 dark:text-red-400 hover:underline"
                  >
                    Remove
                  </button>
                </td>

                <!-- Actions -->
                <td class="px-4 py-3 text-center">
                  <a
                    :href="`/${domain.domain_key}/admin`"
                    target="_blank"
                    class="inline-flex items-center gap-1 px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-xs font-medium transition-colors"
                  >
                    ⚙️ Manage
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-xl p-6 border-2 border-yellow-200 dark:border-yellow-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold text-yellow-800 dark:text-yellow-200">{{ $t('admin.panel.pending') }}</p>
              <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100 mt-1">{{ pendingCount }}</p>
            </div>
            <div class="w-12 h-12 bg-yellow-200 dark:bg-yellow-700 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-yellow-700 dark:text-yellow-200" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 border-2 border-green-200 dark:border-green-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold text-green-800 dark:text-green-200">{{ $t('admin.panel.approved') }}</p>
              <p class="text-3xl font-bold text-green-900 dark:text-green-100 mt-1">{{ approvedCount }}</p>
            </div>
            <div class="w-12 h-12 bg-green-200 dark:bg-green-700 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-green-700 dark:text-green-200" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-xl p-6 border-2 border-red-200 dark:border-red-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold text-red-800 dark:text-red-200">{{ $t('admin.panel.rejected') }}</p>
              <p class="text-3xl font-bold text-red-900 dark:text-red-100 mt-1">{{ rejectedCount }}</p>
            </div>
            <div class="w-12 h-12 bg-red-200 dark:bg-red-700 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-red-700 dark:text-red-200" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Requests List -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border-2 border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">{{ $t('admin.panel.allRequests') }}</h2>
        </div>

        <div v-if="loading" class="p-12 text-center">
          <div class="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">{{ $t('common.loading') }}</p>
        </div>

        <div v-else-if="requests.length === 0" class="p-12 text-center">
          <div class="text-6xl mb-4">📭</div>
          <p class="text-gray-600 dark:text-gray-400 font-semibold">{{ $t('admin.panel.noRequests') }}</p>
        </div>

        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <div v-for="request in requests" :key="request.id" class="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-2">
                  <span class="font-bold text-lg text-gray-900 dark:text-gray-100">{{ request.username }}</span>
                  <span
                    class="px-3 py-1 rounded-full text-xs font-bold"
                    :class="{
                      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200': request.status === 'pending',
                      'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200': request.status === 'approved',
                      'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200': request.status === 'rejected'
                    }"
                  >
                    {{ $t(`admin.panel.status.${request.status}`) }}
                  </span>
                </div>

                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2 break-all">
                  <strong>{{ $t('admin.panel.calendarUrl') }}:</strong>
                  <a :href="request.calendar_url" target="_blank" class="text-purple-600 dark:text-purple-400 hover:underline">
                    {{ request.calendar_url }}
                  </a>
                </p>

                <p class="text-sm text-gray-700 dark:text-gray-300 mb-3 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
                  {{ request.description }}
                </p>

                <p class="text-xs text-gray-500 dark:text-gray-400">
                  {{ $t('admin.panel.submitted') }}: {{ formatDate(request.created_at) }}
                </p>

                <p v-if="request.domain_key" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {{ $t('admin.panel.domainKey') }}: <span class="font-mono font-bold">{{ request.domain_key }}</span>
                </p>
              </div>

              <div v-if="request.status === 'pending'" class="flex flex-col gap-2">
                <button
                  @click="approveRequest(request.id)"
                  :disabled="processing"
                  class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold text-sm transition-colors disabled:opacity-50 whitespace-nowrap"
                >
                  ✓ {{ $t('admin.panel.approve') }}
                </button>
                <button
                  @click="rejectRequest(request.id)"
                  :disabled="processing"
                  class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold text-sm transition-colors disabled:opacity-50 whitespace-nowrap"
                >
                  ✗ {{ $t('admin.panel.reject') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'
import AppHeader from '../components/shared/AppHeader.vue'
import { useNotification } from '../composables/useNotification'

const { t } = useI18n()
const notify = useNotification()

// Authentication
const isAuthenticated = ref(false)
const password = ref('')
const authenticating = ref(false)
const authError = ref(null)

// Requests data
const requests = ref([])
const loading = ref(false)
const processing = ref(false)

// Domains data
const domains = ref([])
const domainsLoading = ref(false)

// Password editing state
const editingDomain = ref(null)
const editingType = ref(null)  // 'admin' or 'user'
const newPassword = ref('')
const showPassword = ref(false)

// Password viewing state
const viewingPassword = ref(null)  // Format: 'domainKey-type'
const viewedPassword = ref('')

// Computed stats
const pendingCount = computed(() => requests.value.filter(r => r.status === 'pending').length)
const approvedCount = computed(() => requests.value.filter(r => r.status === 'approved').length)
const rejectedCount = computed(() => requests.value.filter(r => r.status === 'rejected').length)

const authenticate = async () => {
  authenticating.value = true
  authError.value = null

  try {
    // Login to get JWT token
    const response = await axios.post(`${API_BASE_URL}/api/admin/login`, {
      password: password.value
    })

    // Store token in localStorage (30-day expiry)
    const token = response.data.token
    localStorage.setItem('admin_token', token)
    localStorage.setItem('admin_token_expires', Date.now() + (30 * 24 * 60 * 60 * 1000))

    isAuthenticated.value = true

    // Load data after successful authentication
    await Promise.all([loadRequests(), loadDomains()])
  } catch (error) {
    authError.value = t('admin.panel.invalidPassword')
  } finally {
    authenticating.value = false
  }
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('admin_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const loadRequests = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/admin/domain-requests`, {
      headers: getAuthHeaders()
    })
    requests.value = response.data
  } catch (error) {
    console.error('Failed to load requests:', error)
    // Token might be expired, logout
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_token_expires')
      isAuthenticated.value = false
    }
  } finally {
    loading.value = false
  }
}

const loadDomains = async () => {
  domainsLoading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/admin/domains-auth`, {
      headers: getAuthHeaders()
    })
    domains.value = response.data
  } catch (error) {
    console.error('Failed to load domains:', error)
  } finally {
    domainsLoading.value = false
  }
}

const startEditing = (domainKey, type) => {
  editingDomain.value = domainKey
  editingType.value = type
  newPassword.value = ''
  showPassword.value = false
}

const cancelEditing = () => {
  editingDomain.value = null
  editingType.value = null
  newPassword.value = ''
  showPassword.value = false
}

const savePassword = async (domainKey, type) => {
  if (!newPassword.value || newPassword.value.length < 4) {
    notify.error(t('admin.domainAuth.passwordSettings.error.minLength') || 'Password must be at least 4 characters')
    return
  }

  try {
    const endpoint = type === 'admin'
      ? `/api/admin/domains/${domainKey}/passwords`
      : `/api/admin/domains/${domainKey}/passwords`

    const payload = type === 'admin'
      ? { admin_password: newPassword.value }
      : { user_password: newPassword.value }

    await axios.patch(`${API_BASE_URL}${endpoint}`, payload, {
      headers: getAuthHeaders()
    })

    notify.success(t(`admin.domainAuth.passwordSettings.success.${type}Set`) || `${type === 'admin' ? 'Admin' : 'User'} password updated successfully`)
    cancelEditing()
    await loadDomains()  // Refresh the list
  } catch (error) {
    notify.error(t(`admin.domainAuth.passwordSettings.error.${type}Set`) || `Failed to set password: ${error.message}`)
  }
}

const removePassword = async (domainKey, type) => {
  if (!confirm(t('admin.domainAuth.passwordSettings.confirm.remove' + (type === 'admin' ? 'Admin' : 'User')) || `Remove ${type} password for ${domainKey}?`)) {
    return
  }

  try {
    const endpoint = `/api/admin/domains/${domainKey}/passwords`

    const payload = type === 'admin'
      ? { remove_admin_password: true }
      : { remove_user_password: true }

    await axios.patch(`${API_BASE_URL}${endpoint}`, payload, {
      headers: getAuthHeaders()
    })

    notify.success(t(`admin.domainAuth.passwordSettings.success.${type}Removed`) || `${type === 'admin' ? 'Admin' : 'User'} password removed successfully`)
    await loadDomains()  // Refresh the list
  } catch (error) {
    notify.error(t(`admin.domainAuth.passwordSettings.error.${type}Removed`) || `Failed to remove password: ${error.message}`)
  }
}

const viewPassword = async (domainKey, type) => {
  const key = `${domainKey}-${type}`

  // If already viewing this password, hide it
  if (viewingPassword.value === key) {
    viewingPassword.value = null
    viewedPassword.value = ''
    return
  }

  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/admin/domains/${domainKey}/password/${type}`,
      { headers: getAuthHeaders() }
    )

    viewingPassword.value = key
    viewedPassword.value = response.data.password
  } catch (error) {
    notify.error(`Failed to retrieve password: ${error.response?.data?.detail || error.message}`)
  }
}

const approveRequest = async (requestId) => {
  processing.value = true
  try {
    await axios.patch(
      `${API_BASE_URL}/api/admin/domain-requests/${requestId}/approve`,
      {},
      {
        headers: getAuthHeaders()
      }
    )
    await loadRequests()
    notify.success(t('admin.panel.approvalSuccess') || 'Request approved successfully')
  } catch (error) {
    notify.error(t('admin.panel.approvalFailed'))
  } finally {
    processing.value = false
  }
}

const rejectRequest = async (requestId) => {
  const reason = prompt(t('admin.panel.rejectionReason'))
  if (!reason) return

  processing.value = true
  try {
    await axios.patch(
      `${API_BASE_URL}/api/admin/domain-requests/${requestId}/reject`,
      { reason },
      {
        headers: getAuthHeaders()
      }
    )
    await loadRequests()
    notify.success(t('admin.panel.rejectionSuccess') || 'Request rejected successfully')
  } catch (error) {
    notify.error(t('admin.panel.rejectionFailed'))
  } finally {
    processing.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

// Check for existing token on mount
onMounted(async () => {
  const token = localStorage.getItem('admin_token')
  const tokenExpires = localStorage.getItem('admin_token_expires')

  if (token && tokenExpires && Date.now() < parseInt(tokenExpires)) {
    // Token exists and hasn't expired
    isAuthenticated.value = true
    await Promise.all([loadRequests(), loadDomains()])
  } else if (token) {
    // Token exists but has expired
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_token_expires')
  }
})
</script>
