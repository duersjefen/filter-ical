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

const { t } = useI18n()

// Authentication
const isAuthenticated = ref(false)
const password = ref('')
const authenticating = ref(false)
const authError = ref(null)

// Requests data
const requests = ref([])
const loading = ref(false)
const processing = ref(false)

// Computed stats
const pendingCount = computed(() => requests.value.filter(r => r.status === 'pending').length)
const approvedCount = computed(() => requests.value.filter(r => r.status === 'approved').length)
const rejectedCount = computed(() => requests.value.filter(r => r.status === 'rejected').length)

const authenticate = async () => {
  authenticating.value = true
  authError.value = null

  try {
    // Test authentication by fetching requests
    const response = await axios.get(`${API_BASE_URL}/api/admin/domain-requests`, {
      auth: {
        username: 'admin',
        password: password.value
      }
    })

    isAuthenticated.value = true
    requests.value = response.data
  } catch (error) {
    authError.value = t('admin.panel.invalidPassword')
  } finally {
    authenticating.value = false
  }
}

const loadRequests = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/admin/domain-requests`, {
      auth: {
        username: 'admin',
        password: password.value
      }
    })
    requests.value = response.data
  } catch (error) {
    console.error('Failed to load requests:', error)
  } finally {
    loading.value = false
  }
}

const approveRequest = async (requestId) => {
  processing.value = true
  try {
    await axios.patch(
      `${API_BASE_URL}/api/admin/domain-requests/${requestId}/approve`,
      {},
      {
        auth: {
          username: 'admin',
          password: password.value
        }
      }
    )
    await loadRequests()
  } catch (error) {
    alert(t('admin.panel.approvalFailed'))
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
        auth: {
          username: 'admin',
          password: password.value
        }
      }
    )
    await loadRequests()
  } catch (error) {
    alert(t('admin.panel.rejectionFailed'))
  } finally {
    processing.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}
</script>
