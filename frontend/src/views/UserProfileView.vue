<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- Header -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border-2 border-gray-200 dark:border-gray-700 p-6 mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
              My Profile
            </h1>
            <p class="text-gray-600 dark:text-gray-400 mt-1">
              Manage your account and domains
            </p>
          </div>
          <div class="text-right">
            <div class="text-sm text-gray-500 dark:text-gray-400">Username</div>
            <div class="font-semibold text-gray-900 dark:text-gray-100">{{ user?.username || 'Not logged in' }}</div>
            <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Email</div>
            <div class="font-semibold text-gray-900 dark:text-gray-100">{{ user?.email || 'Not set' }}</div>
          </div>
        </div>
      </div>

      <!-- Not Logged In -->
      <div v-if="!isLoggedIn" class="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-300 dark:border-yellow-700 rounded-2xl p-6 text-center">
        <p class="text-yellow-900 dark:text-yellow-200 font-semibold">
          You must be logged in to view your profile
        </p>
        <button
          @click="$router.push('/login')"
          class="mt-4 bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 rounded-xl font-semibold transition"
        >
          Go to Login
        </button>
      </div>

      <!-- Profile Content -->
      <template v-else>
        <!-- Owned Domains -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border-2 border-gray-200 dark:border-gray-700 p-6 mb-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              My Domains ({{ ownedDomains.length }})
            </h2>
          </div>

          <div v-if="loading" class="text-center py-8 text-gray-500 dark:text-gray-400">
            Loading...
          </div>

          <div v-else-if="ownedDomains.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            You don't own any domains yet. Request a domain from the home page!
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="domain in ownedDomains"
              :key="domain.domain_key"
              class="border-2 border-gray-200 dark:border-gray-700 rounded-xl p-4 hover:border-green-400 dark:hover:border-green-600 transition"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="font-bold text-lg text-gray-900 dark:text-gray-100">
                    {{ domain.name || domain.domain_key }}
                  </h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Domain: <span class="font-mono">{{ domain.domain_key }}</span>
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    Status: {{ domain.status }}
                  </p>
                </div>
                <div class="flex gap-2">
                  <button
                    @click="toggleAdminManagement(domain.domain_key)"
                    class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                  >
                    {{ showingAdmins === domain.domain_key ? 'Hide' : 'Manage' }} Admins
                  </button>
                  <button
                    @click="goToDomain(domain.domain_key)"
                    class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                  >
                    View Domain
                  </button>
                </div>
              </div>

              <!-- Admin Management -->
              <div v-if="showingAdmins === domain.domain_key" class="mt-4 pt-4 border-t-2 border-gray-200 dark:border-gray-700">
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">Domain Admins</h4>

                <!-- Loading -->
                <div v-if="loadingAdmins" class="text-sm text-gray-500 dark:text-gray-400">
                  Loading admins...
                </div>

                <!-- Admin List -->
                <div v-else-if="domainAdmins[domain.domain_key]" class="space-y-2">
                  <div
                    v-for="admin in domainAdmins[domain.domain_key]"
                    :key="admin.id"
                    class="flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3"
                  >
                    <div>
                      <div class="font-semibold text-gray-900 dark:text-gray-100">{{ admin.username }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">{{ admin.email }}</div>
                    </div>
                    <button
                      @click="removeAdmin(domain.domain_key, admin.username)"
                      :disabled="removingAdmin"
                      class="bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white px-3 py-1 rounded-lg text-sm font-semibold transition"
                    >
                      Remove
                    </button>
                  </div>

                  <div v-if="domainAdmins[domain.domain_key].length === 0" class="text-sm text-gray-500 dark:text-gray-400 py-2">
                    No admins yet
                  </div>
                </div>

                <!-- Add Admin Form -->
                <div class="mt-4 flex gap-2">
                  <input
                    v-model="newAdminUsername"
                    type="text"
                    placeholder="Username to add as admin"
                    class="flex-1 px-3 py-2 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm"
                    @keyup.enter="addAdmin(domain.domain_key)"
                  />
                  <button
                    @click="addAdmin(domain.domain_key)"
                    :disabled="!newAdminUsername || addingAdmin"
                    class="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                  >
                    Add Admin
                  </button>
                </div>

                <!-- Messages -->
                <div v-if="adminMessage" :class="[
                  'mt-3 px-3 py-2 rounded-lg text-sm font-semibold',
                  adminMessageType === 'success' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
                ]">
                  {{ adminMessage }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Admin Domains (where user is admin but not owner) -->
        <div v-if="adminDomains.length > 0" class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border-2 border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Admin Access ({{ adminDomains.length }})
            </h2>
          </div>

          <div class="space-y-4">
            <div
              v-for="domain in adminDomains"
              :key="domain.domain_key"
              class="border-2 border-gray-200 dark:border-gray-700 rounded-xl p-4 hover:border-blue-400 dark:hover:border-blue-600 transition"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="font-bold text-lg text-gray-900 dark:text-gray-100">
                    {{ domain.name || domain.domain_key }}
                  </h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    Domain: <span class="font-mono">{{ domain.domain_key }}</span>
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    Role: Admin
                  </p>
                </div>
                <button
                  @click="goToDomainAdmin(domain.domain_key)"
                  class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                >
                  Admin Panel
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useHTTP } from '../composables/useHTTP'

const router = useRouter()
const { user, isLoggedIn } = useAuth()
const { get, post, del } = useHTTP()

const loading = ref(false)
const ownedDomains = ref([])
const adminDomains = ref([])

const showingAdmins = ref(null)
const loadingAdmins = ref(false)
const domainAdmins = ref({})
const newAdminUsername = ref('')
const addingAdmin = ref(false)
const removingAdmin = ref(false)
const adminMessage = ref(null)
const adminMessageType = ref('success')

// Fetch user's domains
const fetchDomains = async () => {
  if (!isLoggedIn.value) return

  loading.value = true
  try {
    const result = await get('/api/users/me/domains')
    if (result.success) {
      ownedDomains.value = result.data.owned_domains || []
      adminDomains.value = result.data.admin_domains || []
    }
  } catch (error) {
    console.error('Failed to fetch domains:', error)
  } finally {
    loading.value = false
  }
}

// Toggle admin management panel
const toggleAdminManagement = async (domainKey) => {
  if (showingAdmins.value === domainKey) {
    showingAdmins.value = null
    return
  }

  showingAdmins.value = domainKey
  adminMessage.value = null
  await fetchAdmins(domainKey)
}

// Fetch domain admins
const fetchAdmins = async (domainKey) => {
  loadingAdmins.value = true
  try {
    const result = await get(`/api/domains/${domainKey}/admins`)
    if (result.success) {
      domainAdmins.value[domainKey] = result.data.admins || []
    }
  } catch (error) {
    console.error('Failed to fetch admins:', error)
    adminMessage.value = 'Failed to load admins'
    adminMessageType.value = 'error'
  } finally {
    loadingAdmins.value = false
  }
}

// Add admin
const addAdmin = async (domainKey) => {
  if (!newAdminUsername.value.trim()) return

  addingAdmin.value = true
  adminMessage.value = null

  try {
    const result = await post(`/api/domains/${domainKey}/admins`, {
      username: newAdminUsername.value.trim()
    })

    if (result.success) {
      adminMessage.value = `Successfully added ${newAdminUsername.value} as admin`
      adminMessageType.value = 'success'
      newAdminUsername.value = ''
      await fetchAdmins(domainKey)
    } else {
      adminMessage.value = result.error || 'Failed to add admin'
      adminMessageType.value = 'error'
    }
  } catch (error) {
    adminMessage.value = 'Failed to add admin'
    adminMessageType.value = 'error'
  } finally {
    addingAdmin.value = false
  }
}

// Remove admin
const removeAdmin = async (domainKey, username) => {
  if (!confirm(`Remove ${username} from admins?`)) return

  removingAdmin.value = true
  adminMessage.value = null

  try {
    const result = await del(`/api/domains/${domainKey}/admins/${username}`)

    if (result.success) {
      adminMessage.value = `Successfully removed ${username} from admins`
      adminMessageType.value = 'success'
      await fetchAdmins(domainKey)
    } else {
      adminMessage.value = result.error || 'Failed to remove admin'
      adminMessageType.value = 'error'
    }
  } catch (error) {
    adminMessage.value = 'Failed to remove admin'
    adminMessageType.value = 'error'
  } finally {
    removingAdmin.value = false
  }
}

// Navigation
const goToDomain = (domainKey) => {
  router.push(`/${domainKey}`)
}

const goToDomainAdmin = (domainKey) => {
  router.push(`/${domainKey}/admin`)
}

// Initialize
onMounted(() => {
  fetchDomains()
})
</script>
