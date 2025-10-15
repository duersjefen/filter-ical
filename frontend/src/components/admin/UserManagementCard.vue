<template>
  <AdminCardWrapper
    title="User Management"
    subtitle="Manage user accounts, roles, and permissions"
    icon="👥"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
    <!-- Search and Filter Bar -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <div class="flex-1 relative">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search users by username or email..."
          class="w-full px-4 py-2 pl-10 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-200 dark:focus:ring-purple-900/50 transition-all"
          @input="handleSearch"
        />
        <svg
          class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>

      <div class="flex gap-2">
        <select
          v-model="roleFilter"
          class="px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 transition-all"
          @change="handleFilterChange"
        >
          <option value="">All Roles</option>
          <option value="user">Users</option>
          <option value="admin">Admins</option>
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
    </div>

    <!-- Loading State -->
    <div v-if="loading && users.length === 0" class="py-12 text-center">
      <div class="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading users...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && users.length === 0" class="py-12 text-center">
      <div class="w-20 h-20 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
      </div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
        No users found
      </h3>
      <p class="text-gray-600 dark:text-gray-400">
        {{ searchQuery ? 'Try a different search query' : 'No users exist yet' }}
      </p>
    </div>

    <!-- Users Table -->
    <div v-else class="overflow-x-auto -mx-6 px-6">
      <table class="w-full min-w-[800px]">
        <thead>
          <tr class="border-b-2 border-gray-200 dark:border-gray-700">
            <th class="text-left py-3 px-4 text-sm font-bold text-gray-700 dark:text-gray-300">Username</th>
            <th class="text-left py-3 px-4 text-sm font-bold text-gray-700 dark:text-gray-300">Email</th>
            <th class="text-left py-3 px-4 text-sm font-bold text-gray-700 dark:text-gray-300">Role</th>
            <th class="text-center py-3 px-4 text-sm font-bold text-gray-700 dark:text-gray-300">Domains</th>
            <th class="text-center py-3 px-4 text-sm font-bold text-gray-700 dark:text-gray-300">Calendars</th>
            <th class="text-center py-3 px-4 text-sm font-bold text-gray-700 dark:text-gray-300">Status</th>
            <th class="text-right py-3 px-4 text-sm font-bold text-gray-700 dark:text-gray-300">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in users"
            :key="user.id"
            class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
          >
            <td class="py-3 px-4">
              <div class="font-semibold text-gray-900 dark:text-gray-100">{{ user.username }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">ID: {{ user.id }}</div>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
              {{ user.email || '—' }}
            </td>
            <td class="py-3 px-4">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
                :class="user.role === 'admin'
                  ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'"
              >
                {{ user.role }}
              </span>
            </td>
            <td class="py-3 px-4 text-center text-sm text-gray-900 dark:text-gray-100 font-semibold">
              {{ user.owned_domains_count || 0 }}
            </td>
            <td class="py-3 px-4 text-center text-sm text-gray-900 dark:text-gray-100 font-semibold">
              {{ user.calendars_count || 0 }}
            </td>
            <td class="py-3 px-4 text-center">
              <span
                v-if="user.locked"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200"
              >
                Locked
              </span>
              <span
                v-else
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200"
              >
                Active
              </span>
            </td>
            <td class="py-3 px-4">
              <div class="flex items-center justify-end gap-2">
                <button
                  @click="handleEdit(user)"
                  class="p-2 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                  title="Edit user"
                >
                  <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                </button>
                <button
                  v-if="user.locked"
                  @click="handleUnlock(user)"
                  class="p-2 hover:bg-green-50 dark:hover:bg-green-900/30 rounded-lg transition-colors"
                  title="Unlock user"
                >
                  <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"/>
                  </svg>
                </button>
                <button
                  @click="handleDelete(user)"
                  class="p-2 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                  title="Delete user"
                >
                  <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="pagination.totalPages > 1" class="flex items-center justify-between mt-6 pt-4 border-t-2 border-gray-100 dark:border-gray-700">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Showing {{ ((pagination.page - 1) * pagination.limit) + 1 }} to {{ Math.min(pagination.page * pagination.limit, pagination.total) }} of {{ pagination.total }} users
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

    <!-- Edit User Modal -->
    <EditUserModal
      v-if="editingUser"
      :user="editingUser"
      :show="showEditModal"
      @close="handleCloseEdit"
      @save="handleSaveUser"
    />

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
import { ref, onMounted } from 'vue'
import AdminCardWrapper from './AdminCardWrapper.vue'
import EditUserModal from './EditUserModal.vue'
import ConfirmDialog from '../shared/ConfirmDialog.vue'
import { useAdminUsers } from '@/composables/useAdminUsers'
import { useNotification } from '@/composables/useNotification'

const props = defineProps({
  expanded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle'])

const notify = useNotification()
const { users, loading, pagination, listUsers, updateUser, deleteUser, unlockUser } = useAdminUsers()

// Search and filter state
const searchQuery = ref('')
const roleFilter = ref('')
let searchTimeout = null

// Edit modal state
const showEditModal = ref(false)
const editingUser = ref(null)

// Confirm dialog state
const confirmDialog = ref(null)
const confirmDialogData = ref({
  title: '',
  message: '',
  confirmText: '',
  onConfirm: null
})

// Load users on mount
onMounted(() => {
  loadUsersList()
})

async function loadUsersList() {
  await listUsers(pagination.value.page, pagination.value.limit, searchQuery.value, roleFilter.value)
}

function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.value.page = 1 // Reset to first page on new search
    loadUsersList()
  }, 300)
}

function handleFilterChange() {
  pagination.value.page = 1 // Reset to first page on filter change
  loadUsersList()
}

function handleRefresh() {
  loadUsersList()
}

function handlePreviousPage() {
  if (pagination.value.page > 1) {
    pagination.value.page -= 1
    loadUsersList()
  }
}

function handleNextPage() {
  if (pagination.value.page < pagination.value.totalPages) {
    pagination.value.page += 1
    loadUsersList()
  }
}

function handleEdit(user) {
  editingUser.value = { ...user }
  showEditModal.value = true
}

function handleCloseEdit() {
  showEditModal.value = false
  editingUser.value = null
}

async function handleSaveUser(updates) {
  const result = await updateUser(editingUser.value.id, updates)
  if (result.success) {
    notify.success('User updated successfully')
    handleCloseEdit()
    loadUsersList() // Refresh list
  } else {
    notify.error(result.error || 'Failed to update user')
  }
}

function handleUnlock(user) {
  confirmDialogData.value = {
    title: 'Unlock User Account',
    message: `Are you sure you want to unlock the account for "${user.username}"? This will reset their failed login attempts.`,
    confirmText: 'Unlock',
    onConfirm: async () => {
      const result = await unlockUser(user.id)
      if (result.success) {
        notify.success(`User "${user.username}" unlocked successfully`)
        loadUsersList() // Refresh list
      } else {
        notify.error(result.error || 'Failed to unlock user')
      }
    }
  }
  confirmDialog.value.open()
}

function handleDelete(user) {
  confirmDialogData.value = {
    title: 'Delete User',
    message: `Are you sure you want to delete user "${user.username}"? This action cannot be undone.\n\nThis will also delete:\n• ${user.calendars_count || 0} calendar(s)\n• ${user.owned_domains_count || 0} owned domain(s)`,
    confirmText: 'Delete User',
    onConfirm: async () => {
      const result = await deleteUser(user.id, {
        deleteCalendars: true,
        deleteDomains: true
      })
      if (result.success) {
        notify.success(`User "${user.username}" deleted successfully`)
        loadUsersList() // Refresh list
      } else {
        notify.error(result.error || 'Failed to delete user')
      }
    }
  }
  confirmDialog.value.open()
}
</script>
