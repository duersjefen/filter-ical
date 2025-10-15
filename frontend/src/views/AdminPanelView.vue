<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <!-- Password Gate -->
    <div v-if="!isAuthenticated" class="min-h-screen flex items-center justify-center">
      <div class="max-w-md w-full">
        <div class="bg-gradient-to-br from-white via-white to-purple-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-purple-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
          <div class="flex items-center justify-center mb-6">
            <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-2xl flex items-center justify-center shadow-lg">
              <svg aria-hidden="true" class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
          <div v-if="authError" role="alert" class="bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-4 py-3 rounded-xl mb-4 border border-red-200 dark:border-red-700">
            <div class="flex items-center gap-3 sm:gap-2">
              <svg aria-hidden="true" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
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

            <button
              type="button"
              @click="showResetRequest = true"
              class="w-full text-sm text-purple-600 dark:text-purple-400 hover:underline mt-2"
            >
              Forgot password?
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Password Reset Request Modal -->
    <PasswordResetModal
      :show="showResetRequest"
      email="info@paiss.me"
      :request-sent="resetRequestSent"
      :requesting="requesting"
      :error="resetError"
      @confirm="requestReset"
      @close="showResetRequest = false; resetRequestSent = false"
    />

    <!-- Approval Modal -->
    <ApprovalModal
      :show="showApproveModal"
      v-model:message="approvalMessage"
      v-model:send-email="sendApprovalEmail"
      :submitting="submittingApproval"
      @confirm="submitApproval"
      @cancel="cancelApproval"
    />

    <!-- Rejection Modal -->
    <RejectionModal
      :show="showRejectModal"
      v-model:reason="rejectionReason"
      v-model:send-email="sendRejectionEmail"
      :submitting="submittingRejection"
      @confirm="submitRejection"
      @cancel="cancelRejection"
    />

    <!-- Admin Panel Content -->
    <div v-if="isAuthenticated">
      <AppHeader
        :title="$t('admin.panel.title')"
        :subtitle="$t('admin.panel.contentSubtitle')"
        :back-button-text="$t('navigation.home')"
        :show-back-button="true"
        page-context="admin"
        @navigate-back="$router.push('/')"
      />

      <div class="space-y-8">
      <!-- Create New Domain (admin shortcut) -->
      <AdminCardWrapper
        title="Create New Domain"
        subtitle="Quickly add a new domain without approval process"
        icon="➕"
        :expanded="showCreateDomainForm"
        @toggle="showCreateDomainForm = !showCreateDomainForm"
      >
        <CreateDomainForm
          :show-form="showCreateDomainForm"
          @domain-created="loadDomains"
        />
      </AdminCardWrapper>

      <!-- Domains Overview (at top) -->
      <AdminCardWrapper
        :title="`All Domains (${domains.length})`"
        subtitle="View and manage all registered domains"
        icon="📁"
        :expanded="showAllDomains"
        @toggle="showAllDomains = !showAllDomains"
      >
        <div v-if="domainsLoading" role="status" aria-live="polite" aria-label="Loading domains" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="i in 6" :key="i" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 overflow-hidden animate-pulse">
            <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 border-b-2 border-gray-100 dark:border-gray-700">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded-xl"></div>
                <div class="flex-1 space-y-2">
                  <div class="h-4 bg-gray-200 dark:bg-gray-600 rounded w-3/4"></div>
                  <div class="h-3 bg-gray-200 dark:bg-gray-600 rounded w-1/2"></div>
                </div>
              </div>
            </div>
            <div class="p-6 space-y-4">
              <div class="h-20 bg-gray-200 dark:bg-gray-600 rounded"></div>
              <div class="h-20 bg-gray-200 dark:bg-gray-600 rounded"></div>
            </div>
          </div>
        </div>

        <div v-else-if="domains.length === 0" class="p-6 text-center">
          <div class="max-w-md mx-auto">
            <div class="w-20 h-20 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg aria-hidden="true" class="w-10 h-10 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
              </svg>
            </div>
            <h3 class="text-2xl sm:text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
              No domains yet
            </h3>
            <p class="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
              Create your first domain using the "Create New Domain" button above to get started.
            </p>
            <button
              @click="showCreateDomainForm = true"
              class="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-all shadow-md hover:shadow-lg"
            >
              <svg aria-hidden="true" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <span>Create Domain</span>
            </button>
          </div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <DomainCard
            v-for="domain in domains"
            :key="domain.domain_key"
            :domain="domain"
            @delete-domain="deleteDomain"
            @refresh-domains="loadDomains"
          />
        </div>
      </AdminCardWrapper>

      <!-- Requests List -->
      <AdminCardWrapper
        :title="`Pending Domain Requests (${pendingRequests.length})`"
        subtitle="Review and approve or reject domain requests from users"
        icon="📥"
        :expanded="showPendingRequests"
        @toggle="showPendingRequests = !showPendingRequests"
      >
        <div v-if="loading" class="p-6 text-center">
          <div class="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">{{ $t('common.loading') }}</p>
        </div>

        <div v-else-if="pendingRequests.length === 0" class="p-6 text-center">
          <div class="max-w-md mx-auto">
            <div class="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg aria-hidden="true" class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 class="text-2xl sm:text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
              All caught up!
            </h3>
            <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
              No pending domain requests at the moment. New requests will appear here for approval.
            </p>
          </div>
        </div>

        <div v-else class="space-y-4">
          <DomainRequestCard
            v-for="request in pendingRequests"
            :key="request.id"
            :request="request"
            :format-date="formatDate"
            @approve="approveRequest"
            @reject="rejectRequest"
          />
        </div>
      </AdminCardWrapper>

      <!-- App Settings - Clean & Spacious -->
      <AdminCardWrapper
        title="App Settings"
        subtitle="Configure global application settings and features"
        icon="⚙️"
        :expanded="showAppSettings"
        @toggle="showAppSettings = !showAppSettings"
      >
        <!-- Settings Grid: Side by Side -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">

          <!-- Footer Visibility -->
          <div>
            <label class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 block">Footer Visibility</label>
            <div class="inline-flex rounded-lg border-2 border-gray-300 dark:border-gray-600 overflow-hidden shadow-sm">
              <button
                @click="appSettings.footer_visibility = 'everywhere'"
                class="px-4 py-2.5 text-sm font-medium transition-all border-r-2 border-gray-300 dark:border-gray-600"
                :class="appSettings.footer_visibility === 'everywhere'
                  ? 'bg-purple-600 text-white shadow-inner'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
              >
                Everywhere
              </button>
              <button
                @click="appSettings.footer_visibility = 'admin_only'"
                class="px-4 py-2.5 text-sm font-medium transition-all border-r-2 border-gray-300 dark:border-gray-600"
                :class="appSettings.footer_visibility === 'admin_only'
                  ? 'bg-purple-600 text-white shadow-inner'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
              >
                Admin
              </button>
              <button
                @click="appSettings.footer_visibility = 'nowhere'"
                class="px-4 py-2.5 text-sm font-medium transition-all"
                :class="appSettings.footer_visibility === 'nowhere'
                  ? 'bg-purple-600 text-white shadow-inner'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
              >
                Hidden
              </button>
            </div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">Control where the PayPal donation footer appears</p>
          </div>

          <!-- Domain Request Card -->
          <div>
            <label class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 block">Domain Request Card</label>
            <div class="flex items-center gap-3">
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="appSettings.show_domain_request" class="sr-only peer" />
                <div class="w-14 h-7 bg-gray-300 dark:bg-gray-600 rounded-full peer-checked:bg-purple-600 dark:peer-checked:bg-purple-500 transition-all shadow-inner"></div>
                <div class="absolute left-1 top-1 w-5 h-5 bg-white rounded-full transition-transform peer-checked:translate-x-7 shadow-md"></div>
              </label>
              <span class="text-sm font-semibold" :class="appSettings.show_domain_request ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400'">
                {{ appSettings.show_domain_request ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">Allow users to request their own custom domains</p>
          </div>

        </div>

        <!-- Save Button -->
        <div class="pt-4 border-t-2 border-gray-100 dark:border-gray-700">
          <button
            @click="saveAppSettings"
            :disabled="settingsSaving"
            class="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-lg font-bold transition-all disabled:cursor-not-allowed shadow-md hover:shadow-lg disabled:shadow-none"
          >
            {{ settingsSaving ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </AdminCardWrapper>

      <!-- Domain YAML Configuration Management -->
      <AdminCardWrapper
        title="Domain YAML Configurations"
        subtitle="Edit domain configuration files directly"
        icon="📄"
        :expanded="showYamlConfig"
        @toggle="showYamlConfig = !showYamlConfig"
      >
        <DomainConfigManager ref="domainConfigManager" />
      </AdminCardWrapper>

      <!-- User Management -->
      <UserManagementCard
        :expanded="showUserManagement"
        @toggle="showUserManagement = !showUserManagement"
      />
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'
import AppHeader from '../components/shared/AppHeader.vue'
import ConfirmDialog from '../components/shared/ConfirmDialog.vue'
import DomainConfigManager from '../components/admin/DomainConfigManager.vue'
import FormInput from '../components/shared/FormInput.vue'
import FormTextarea from '../components/shared/FormTextarea.vue'
import BaseButton from '../components/shared/BaseButton.vue'
import DomainCard from '../components/admin/DomainCard.vue'
import DomainRequestCard from '../components/admin/DomainRequestCard.vue'
import CreateDomainForm from '../components/admin/CreateDomainForm.vue'
import ApprovalModal from '../components/admin/ApprovalModal.vue'
import RejectionModal from '../components/admin/RejectionModal.vue'
import PasswordResetModal from '../components/admin/PasswordResetModal.vue'
import UserManagementCard from '../components/admin/UserManagementCard.vue'
import AdminCardWrapper from '../components/admin/AdminCardWrapper.vue'
import { useNotification } from '../composables/useNotification'

const { t } = useI18n()
const notify = useNotification()

// Authentication
const isAuthenticated = ref(false)
const password = ref('')
const authenticating = ref(false)
const authError = ref(null)

// Password reset
const showResetRequest = ref(false)
const resetRequestSent = ref(false)
const requesting = ref(false)
const resetError = ref(null)

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

// App settings state
const appSettings = ref({
  footer_visibility: 'everywhere',
  show_domain_request: true
})
const settingsSaving = ref(false)

// iCal preview state
const icalPreviews = ref({})  // { [requestId]: { expanded: boolean, loading: boolean, data: {...} } }

// Rejection modal state
const showRejectModal = ref(false)
const rejectingRequestId = ref(null)
const rejectionReason = ref('')
const submittingRejection = ref(false)

// Approval modal state
const showApproveModal = ref(false)
const approvingRequestId = ref(null)
const approvalMessage = ref('')
const sendApprovalEmail = ref(true)
const sendRejectionEmail = ref(true)
const submittingApproval = ref(false)

// Confirm dialog state
const confirmDialog = ref(null)
const confirmDialogData = ref({
  title: '',
  message: '',
  confirmText: '',
  onConfirm: null
})

// Create domain state
const showCreateDomainForm = ref(false)
const creatingDomain = ref(false)

// Card expand/collapse state
const showAllDomains = ref(true)
const showPendingRequests = ref(true)
const showAppSettings = ref(true)
const showYamlConfig = ref(true)
const showUserManagement = ref(false)
const newDomain = ref({
  domain_key: '',
  name: '',
  calendar_url: '',
  admin_password: '',
  user_password: ''
})

// Preview state for new domain creation
const newDomainPreview = ref({
  loading: false,
  data: null
})

// Owner assignment state
const assigningOwner = ref(null)  // domain_key being edited
const ownerSearchQuery = ref('')
const userSearchResults = ref([])
const searchingUsers = ref(false)
let searchTimeout = null

// Computed stats
// Only show pending requests (approved ones become domains, rejected ones are hidden)
const pendingRequests = computed(() => requests.value.filter(r => r.status === 'pending'))

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

const requestReset = async () => {
  requesting.value = true
  resetError.value = null

  try {
    await axios.post(`${API_BASE_URL}/api/admin/request-password-reset`)
    resetRequestSent.value = true
  } catch (error) {
    resetError.value = error.response?.data?.detail || 'Failed to send reset email'
  } finally {
    requesting.value = false
  }
}

const loadRequests = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/admin/domain-requests`, {
      headers: getAuthHeaders()
    })
    requests.value = response.data

    // Auto-expand previews for all pending requests
    await autoExpandPreviews()
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

const removePassword = (domainKey, type) => {
  const passwordType = type === 'admin' ? 'Admin' : 'User'

  confirmDialogData.value = {
    title: `Remove ${passwordType} Password`,
    message: t('admin.domainAuth.passwordSettings.confirm.remove' + (type === 'admin' ? 'Admin' : 'User')) || `Are you sure you want to remove the ${type} password for domain "${domainKey}"? Users will no longer need a password to access this domain.`,
    confirmText: 'Remove Password',
    onConfirm: async () => {
      processing.value = true
      try {
        const endpoint = `/api/admin/domains/${domainKey}/passwords`

        const payload = type === 'admin'
          ? { remove_admin_password: true }
          : { remove_user_password: true }

        await axios.patch(`${API_BASE_URL}${endpoint}`, payload, {
          headers: getAuthHeaders()
        })

        notify.success(t(`admin.domainAuth.passwordSettings.success.${type}Removed`) || `${passwordType} password removed successfully`)
        await loadDomains()  // Refresh the list
      } catch (error) {
        notify.error(t(`admin.domainAuth.passwordSettings.error.${type}Removed`) || `Failed to remove password: ${error.message}`)
      } finally {
        processing.value = false
      }
    }
  }
  confirmDialog.value.open()
}

const approveRequest = (requestId) => {
  // Open approval modal
  approvingRequestId.value = requestId
  approvalMessage.value = ''
  sendApprovalEmail.value = true
  showApproveModal.value = true
}

const cancelApproval = () => {
  showApproveModal.value = false
  approvingRequestId.value = null
  approvalMessage.value = ''
}

const submitApproval = async () => {
  submittingApproval.value = true
  try {
    const requestBody = {
      send_email: sendApprovalEmail.value
    }

    // Only include message if it's not empty
    if (approvalMessage.value.trim()) {
      requestBody.message = approvalMessage.value.trim()
    }

    await axios.patch(
      `${API_BASE_URL}/api/admin/domain-requests/${approvingRequestId.value}/approve`,
      requestBody,
      {
        headers: getAuthHeaders()
      }
    )
    // Reload both requests and domains to show the new domain
    await Promise.all([loadRequests(), loadDomains()])
    notify.success(t('admin.panel.approvalSuccess') || 'Request approved successfully')
    cancelApproval()
  } catch (error) {
    notify.error(t('admin.panel.approvalFailed'))
  } finally {
    submittingApproval.value = false
  }
}

const rejectRequest = (requestId) => {
  // Open rejection modal
  rejectingRequestId.value = requestId
  rejectionReason.value = ''
  sendRejectionEmail.value = true
  showRejectModal.value = true
}

const cancelRejection = () => {
  showRejectModal.value = false
  rejectingRequestId.value = null
  rejectionReason.value = ''
}

const submitRejection = async () => {
  if (!rejectionReason.value.trim()) {
    notify.error('Please provide a rejection reason')
    return
  }

  submittingRejection.value = true
  try {
    await axios.patch(
      `${API_BASE_URL}/api/admin/domain-requests/${rejectingRequestId.value}/reject`,
      {
        reason: rejectionReason.value.trim(),
        send_email: sendRejectionEmail.value
      },
      {
        headers: getAuthHeaders()
      }
    )
    await loadRequests()
    notify.success(t('admin.panel.rejectionSuccess') || 'Request rejected successfully')
    cancelRejection()
  } catch (error) {
    notify.error(t('admin.panel.rejectionFailed'))
  } finally {
    submittingRejection.value = false
  }
}

const deleteDomain = (domainKey) => {
  confirmDialogData.value = {
    title: 'Delete Domain',
    message: `Are you sure you want to delete domain "${domainKey}"? This will delete all associated data (calendar, filters, groups). This action cannot be undone.`,
    confirmText: 'Delete Domain',
    onConfirm: async () => {
      processing.value = true
      try {
        await axios.delete(
          `${API_BASE_URL}/api/admin/domains/${domainKey}`,
          {
            headers: getAuthHeaders()
          }
        )
        await loadDomains()
        notify.success(`Domain "${domainKey}" deleted successfully`)
      } catch (error) {
        notify.error(`Failed to delete domain: ${error.response?.data?.detail || error.message}`)
      } finally {
        processing.value = false
      }
    }
  }
  confirmDialog.value.open()
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const loadAppSettings = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/app-settings`)
    appSettings.value = response.data
  } catch (error) {
    console.error('Failed to load app settings:', error)
  }
}

const saveAppSettings = async () => {
  settingsSaving.value = true
  try {
    await axios.patch(
      `${API_BASE_URL}/api/admin/app-settings`,
      appSettings.value,
      {
        headers: getAuthHeaders()
      }
    )
    notify.success('App settings updated successfully')
  } catch (error) {
    notify.error(`Failed to update settings: ${error.response?.data?.detail || error.message}`)
  } finally {
    settingsSaving.value = false
  }
}

const togglePreview = async (requestId) => {
  // Initialize preview state if not exists
  if (!icalPreviews.value[requestId]) {
    icalPreviews.value[requestId] = { expanded: false, loading: false, data: null }
  }

  // Toggle expansion
  icalPreviews.value[requestId].expanded = !icalPreviews.value[requestId].expanded

  // If expanding and no data loaded yet, fetch it
  if (icalPreviews.value[requestId].expanded && !icalPreviews.value[requestId].data) {
    icalPreviews.value[requestId].loading = true

    try {
      const request = requests.value.find(r => r.id === requestId)
      if (!request) return

      const response = await axios.post(`${API_BASE_URL}/api/ical/preview`, {
        calendar_url: request.calendar_url
      })

      icalPreviews.value[requestId].data = response.data
    } catch (error) {
      icalPreviews.value[requestId].data = {
        event_count: 0,
        events: [],
        error: `Failed to load preview: ${error.response?.data?.detail || error.message}`
      }
    } finally {
      icalPreviews.value[requestId].loading = false
    }
  }
}

const canApproveRequest = (requestId) => {
  const preview = icalPreviews.value[requestId]

  // If preview was checked and has error or 0 events, block approval
  if (preview?.data) {
    if (preview.data.error || preview.data.event_count === 0) {
      return false
    }
  }

  return true
}

const getApprovalDisabledReason = (requestId) => {
  const preview = icalPreviews.value[requestId]

  if (preview?.data?.error) {
    return `Cannot approve: ${preview.data.error}`
  }

  if (preview?.data?.event_count === 0) {
    return 'Cannot approve: Calendar has no events'
  }

  return ''
}

const autoFillDisplayName = () => {
  // Auto-generate display name from domain key (capitalize first letter)
  const key = newDomain.value.domain_key.trim()
  if (key) {
    // Replace hyphens with spaces and capitalize first letter of each word
    newDomain.value.name = key
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  } else {
    newDomain.value.name = ''
  }
}

const previewNewDomainCalendar = async () => {
  // Don't preview if URL is empty or invalid
  if (!newDomain.value.calendar_url || !newDomain.value.calendar_url.startsWith('http')) {
    return
  }

  newDomainPreview.value.loading = true
  newDomainPreview.value.data = null

  try {
    const response = await axios.post(`${API_BASE_URL}/api/ical/preview`, {
      calendar_url: newDomain.value.calendar_url
    })
    newDomainPreview.value.data = response.data
  } catch (error) {
    console.error('Failed to preview calendar:', error)
    newDomainPreview.value.data = {
      event_count: 0,
      events: [],
      error: error.response?.data?.detail || error.message || 'Failed to load preview'
    }
  } finally {
    newDomainPreview.value.loading = false
  }
}

// Auto-preview handlers
let previewTimeout = null

const handleCalendarUrlPaste = () => {
  // Wait a moment for paste to complete, then preview
  setTimeout(() => {
    previewNewDomainCalendar()
  }, 100)
}

const handleCalendarUrlBlur = () => {
  // Debounce preview on blur
  clearTimeout(previewTimeout)
  previewTimeout = setTimeout(() => {
    if (newDomain.value.calendar_url && !newDomainPreview.value.data) {
      previewNewDomainCalendar()
    }
  }, 300)
}

const createDomain = async () => {
  // If preview hasn't been run yet, or if URL changed since last preview, run it first
  if (!newDomainPreview.value.data || newDomainPreview.value.loading) {
    await previewNewDomainCalendar()

    // If preview shows an error, don't proceed
    if (newDomainPreview.value.data?.error) {
      notify.error('Cannot create domain: ' + newDomainPreview.value.data.error)
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
      admin_password: newDomain.value.admin_password  // Required
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

    // Success - reset form and reload domains
    notify.success(t('admin.domains.createSuccess', { domainKey: response.data.domain_key }))

    // Reset form and preview
    newDomain.value = {
      domain_key: '',
      name: '',
      calendar_url: '',
      admin_password: '',
      user_password: ''
    }
    newDomainPreview.value = {
      loading: false,
      data: null
    }

    // Reload domains list
    await loadDomains()

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

const startOwnerAssignment = (domainKey) => {
  assigningOwner.value = domainKey
  ownerSearchQuery.value = ''
  userSearchResults.value = []
}

const cancelOwnerAssignment = () => {
  assigningOwner.value = null
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

    // Update local domain list
    const domain = domains.value.find(d => d.domain_key === domainKey)
    if (domain) {
      domain.owner_username = username
      domain.owner_id = userId
    }

    cancelOwnerAssignment()
  } catch (error) {
    console.error('Failed to assign owner:', error)
    notify.error(t('admin.domains.assignOwnerError', { detail: error.response?.data?.detail || error.message }))
  }
}

const removeOwner = (domainKey) => {
  confirmDialogData.value = {
    title: t('admin.domains.removeOwnerTitle'),
    message: t('admin.domains.removeOwnerConfirm', { domainKey }),
    confirmText: t('common.remove'),
    onConfirm: async () => {
      try {
        const token = localStorage.getItem('admin_token')
        await axios.patch(
          `${API_BASE_URL}/api/admin/domains/${domainKey}/owner`,
          { user_id: null },
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        )

        notify.success(t('admin.domains.removeOwnerSuccess', { domainKey }))

        // Update local domain list
        const domain = domains.value.find(d => d.domain_key === domainKey)
        if (domain) {
          domain.owner_username = null
          domain.owner_id = null
        }
      } catch (error) {
        console.error('Failed to remove owner:', error)
        notify.error(t('admin.domains.removeOwnerError', { detail: error.response?.data?.detail || error.message }))
      }
    }
  }
  confirmDialog.value?.open()
}

const autoExpandPreviews = async () => {
  // Auto-load previews for all pending requests
  for (const request of pendingRequests.value) {
    // Initialize and expand
    icalPreviews.value[request.id] = { expanded: true, loading: true, data: null }

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ical/preview`, {
        calendar_url: request.calendar_url
      })

      icalPreviews.value[request.id].data = response.data

      // Auto-collapse if successful (no errors, has events)
      if (!response.data.error && response.data.event_count > 0) {
        icalPreviews.value[request.id].expanded = false
      }
      // Keep expanded if there's an error or no events (so admin sees it immediately)
    } catch (error) {
      icalPreviews.value[request.id].data = {
        event_count: 0,
        events: [],
        error: `Failed to load preview: ${error.response?.data?.detail || error.message}`
      }
      // Keep expanded to show error
    } finally {
      icalPreviews.value[request.id].loading = false
    }
  }
}

// Check for existing token on mount
onMounted(async () => {
  const token = localStorage.getItem('admin_token')
  const tokenExpires = localStorage.getItem('admin_token_expires')

  if (token && tokenExpires && Date.now() < parseInt(tokenExpires)) {
    // Token exists and hasn't expired
    isAuthenticated.value = true
    await Promise.all([loadRequests(), loadDomains(), loadAppSettings()])
  } else if (token) {
    // Token exists but has expired
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_token_expires')
  }
})
</script>

<style scoped>
/* Enhanced accessibility styles */

/* Focus visible styles for all interactive elements */
button:focus-visible,
input:focus-visible,
textarea:focus-visible,
a:focus-visible,
[role="button"]:focus-visible,
[role="link"]:focus-visible {
  outline: 2px solid rgb(147 51 234); /* purple-600 */
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgb(243 232 255 / 1); /* purple-100 ring */
}

/* Dark mode focus styles */
.dark button:focus-visible,
.dark input:focus-visible,
.dark textarea:focus-visible,
.dark a:focus-visible,
.dark [role="button"]:focus-visible,
.dark [role="link"]:focus-visible {
  outline: 2px solid rgb(147 51 234); /* purple-600 */
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgb(88 28 135 / 0.5); /* purple-900/50 ring */
}

/* Ensure modals trap focus properly */
[role="dialog"] {
  isolation: isolate;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  button:focus-visible,
  input:focus-visible,
  textarea:focus-visible,
  a:focus-visible {
    outline-width: 3px;
    outline-offset: 3px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
