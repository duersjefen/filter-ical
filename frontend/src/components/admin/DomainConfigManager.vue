<template>
  <div class="space-y-6">
    <!-- Error/Success Messages -->
    <div v-if="errorMessage" class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg flex items-start gap-3">
      <svg class="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
      </svg>
      <span class="text-sm">{{ errorMessage }}</span>
    </div>

    <div v-if="successMessage" class="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg flex items-start gap-3">
      <svg class="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      <span class="text-sm">{{ successMessage }}</span>
    </div>

    <!-- Upload New Configuration -->
    <div class="bg-gradient-to-br from-white via-white to-blue-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-blue-900/10 rounded-xl shadow-lg border-2 border-gray-200/80 dark:border-gray-700/80 p-6">
      <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
        <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        Upload Configuration
      </h3>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Domain Key
          </label>
          <input
            v-model="uploadDomainKey"
            type="text"
            placeholder="e.g., exter, mydomain"
            pattern="[a-z0-9_-]+"
            class="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:outline-none focus:border-blue-500 dark:focus:border-blue-400"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Only lowercase letters, numbers, underscores, and hyphens</p>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            YAML File
          </label>
          <input
            type="file"
            ref="fileInput"
            accept=".yaml,.yml"
            @change="handleFileSelect"
            class="block w-full text-sm text-gray-900 dark:text-gray-100 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 dark:file:bg-blue-900/30 dark:file:text-blue-400 hover:file:bg-blue-100 dark:hover:file:bg-blue-800/50"
          />
        </div>

        <button
          @click="uploadConfig"
          :disabled="uploading || !uploadDomainKey || !selectedFile"
          class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-lg font-semibold transition-all shadow-md hover:shadow-lg disabled:shadow-none"
        >
          <svg v-if="!uploading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ uploading ? 'Uploading...' : 'Upload Configuration' }}
        </button>
      </div>
    </div>

    <!-- Configurations List -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">
          Available Configurations ({{ configs.length }})
        </h3>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="inline-block w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <div v-else-if="configs.length === 0" class="px-6 py-12 text-center text-gray-600 dark:text-gray-400">
        No configuration files found
      </div>

      <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="config in configs"
          :key="config.domain_key"
          class="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-900/30 transition-colors"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 mb-2">
                <h4 class="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {{ config.domain_key }}.yaml
                </h4>
                <span
                  v-if="config.exists_in_database"
                  class="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded"
                >
                  In Database
                </span>
                <span
                  v-if="config.has_groups"
                  class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-medium rounded"
                >
                  Seeded
                </span>
                <span
                  v-else
                  class="px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-xs font-medium rounded"
                >
                  Not Seeded
                </span>
              </div>

              <div class="flex flex-wrap gap-3 text-sm text-gray-600 dark:text-gray-400">
                <span>📦 {{ formatFileSize(config.file_size) }}</span>
                <span v-if="config.modified_at">
                  🕒 {{ formatDate(config.modified_at) }}
                </span>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <!-- Download -->
              <button
                @click="downloadConfig(config.domain_key)"
                class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Download YAML"
              >
                <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </button>

              <!-- Seed -->
              <button
                @click="seedConfig(config.domain_key, config.has_groups)"
                :disabled="seeding === config.domain_key"
                class="p-2 bg-green-50 hover:bg-green-100 dark:bg-green-900/30 dark:hover:bg-green-800/50 rounded-lg transition-colors disabled:opacity-50"
                :title="config.has_groups ? 'Re-seed (force)' : 'Seed Database'"
              >
                <svg v-if="seeding !== config.domain_key" class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <svg v-else class="w-5 h-5 text-green-600 dark:text-green-400 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </button>

              <!-- Delete -->
              <button
                @click="deleteConfig(config.domain_key)"
                :disabled="deleting === config.domain_key"
                class="p-2 bg-red-50 hover:bg-red-100 dark:bg-red-900/30 dark:hover:bg-red-800/50 rounded-lg transition-colors disabled:opacity-50"
                title="Delete YAML File"
              >
                <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useRouter } from 'vue-router'

const adminStore = useAdminStore()
const router = useRouter()

const configs = ref([])
const loading = ref(false)
const uploading = ref(false)
const seeding = ref(null)
const deleting = ref(null)
const errorMessage = ref('')
const successMessage = ref('')
const uploadDomainKey = ref('')
const selectedFile = ref(null)
const fileInput = ref(null)

onMounted(() => {
  // Check if token is expired before loading
  if (adminStore.isTokenExpired()) {
    adminStore.logout()
    errorMessage.value = 'Your session has expired. Please log in again.'
    setTimeout(() => {
      router.push('/admin/login')
    }, 2000)
    return
  }
  loadConfigs()
})

async function loadConfigs() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await adminStore.listDomainConfigs()
    configs.value = response.configs || []
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load configurations'

    // Redirect to login if session expired
    if (error.message.includes('session has expired')) {
      setTimeout(() => {
        router.push('/admin/login')
      }, 2000)
    }
  } finally {
    loading.value = false
  }
}

async function refreshConfigs() {
  await loadConfigs()
  successMessage.value = 'Configurations refreshed'
  setTimeout(() => successMessage.value = '', 3000)
}

function handleFileSelect(event) {
  selectedFile.value = event.target.files[0]
}

async function uploadConfig() {
  if (!uploadDomainKey.value || !selectedFile.value) return

  uploading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await adminStore.uploadDomainConfig(uploadDomainKey.value, selectedFile.value)
    successMessage.value = `Configuration '${uploadDomainKey.value}.yaml' uploaded successfully`
    uploadDomainKey.value = ''
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    await loadConfigs()
  } catch (error) {
    errorMessage.value = error.message || 'Failed to upload configuration'

    // Redirect to login if session expired
    if (error.message.includes('session has expired')) {
      setTimeout(() => {
        router.push('/admin/login')
      }, 2000)
    }
  } finally {
    uploading.value = false
  }
}

async function downloadConfig(domainKey) {
  errorMessage.value = ''

  try {
    await adminStore.downloadDomainConfig(domainKey)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to download configuration'

    // Redirect to login if session expired
    if (error.message.includes('session has expired')) {
      setTimeout(() => {
        router.push('/admin/login')
      }, 2000)
    }
  }
}

async function seedConfig(domainKey, hasGroups) {
  const forceReseed = hasGroups

  if (forceReseed && !confirm(`Domain '${domainKey}' is already seeded. This will overwrite existing groups. Continue?`)) {
    return
  }

  seeding.value = domainKey
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await adminStore.seedDomainFromConfig(domainKey, forceReseed)
    if (response.success) {
      successMessage.value = response.message
      await loadConfigs()
    } else {
      errorMessage.value = response.message || 'Seeding failed'
    }
  } catch (error) {
    errorMessage.value = error.message || 'Failed to seed database'

    // Redirect to login if session expired
    if (error.message.includes('session has expired')) {
      setTimeout(() => {
        router.push('/admin/login')
      }, 2000)
    }
  } finally {
    seeding.value = null
  }
}

async function deleteConfig(domainKey) {
  if (!confirm(`Delete configuration file '${domainKey}.yaml'? This cannot be undone (but a backup will be created).`)) {
    return
  }

  deleting.value = domainKey
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await adminStore.deleteDomainConfig(domainKey)
    successMessage.value = `Configuration '${domainKey}.yaml' deleted`
    await loadConfigs()
  } catch (error) {
    errorMessage.value = error.message || 'Failed to delete configuration'

    // Redirect to login if session expired
    if (error.message.includes('session has expired')) {
      setTimeout(() => {
        router.push('/admin/login')
      }, 2000)
    }
  } finally {
    deleting.value = null
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleString()
}

// Expose methods for parent component
defineExpose({
  refreshConfigs
})
</script>
