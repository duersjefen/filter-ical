/**
 * Admin user management composable.
 *
 * Provides functions for managing users in the admin panel following
 * the functional programming principles from CLAUDE.md.
 */

import { ref } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { API_BASE_URL } from '@/constants/api'

export function useAdminUsers() {
  const adminStore = useAdminStore()

  // Reactive state
  const users = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    total: 0,
    page: 1,
    limit: 10,
    totalPages: 0
  })

  /**
   * Get auth headers with admin token
   */
  function getAuthHeaders() {
    return {
      'Authorization': `Bearer ${adminStore.adminToken}`,
      'Content-Type': 'application/json'
    }
  }

  /**
   * Handle authentication errors
   */
  async function handleAuthError(response) {
    if (response.status === 401) {
      adminStore.logout()
      throw new Error('Your session has expired. Please log in again.')
    }
  }

  /**
   * List users with pagination and filters
   * @param {number} page - Page number (1-indexed)
   * @param {number} limit - Items per page
   * @param {string} search - Search query (username or email)
   * @param {string} role - Filter by role ('user' or 'admin')
   */
  async function listUsers(page = 1, limit = 10, search = '', role = '') {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString()
      })

      if (search) {
        params.append('search', search)
      }

      if (role) {
        params.append('role', role)
      }

      const response = await fetch(
        `${API_BASE_URL}/api/admin/users?${params.toString()}`,
        {
          headers: getAuthHeaders()
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to load users')
      }

      const data = await response.json()
      users.value = data.users || []
      pagination.value = {
        total: data.total || 0,
        page: data.page || page,
        limit: data.limit || limit,
        totalPages: Math.ceil((data.total || 0) / limit)
      }

      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Failed to list users:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  /**
   * Get details for a specific user
   * @param {number} userId - User ID
   */
  async function getUserDetails(userId) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${userId}`,
        {
          headers: getAuthHeaders()
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to load user details')
      }

      const data = await response.json()
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Failed to get user details:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  /**
   * Update user details
   * @param {number} userId - User ID
   * @param {Object} updates - Fields to update (email, password, role)
   */
  async function updateUser(userId, updates) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${userId}`,
        {
          method: 'PATCH',
          headers: getAuthHeaders(),
          body: JSON.stringify(updates)
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to update user')
      }

      const data = await response.json()

      // Update local users array if user is in current list
      const userIndex = users.value.findIndex(u => u.id === userId)
      if (userIndex !== -1) {
        users.value[userIndex] = { ...users.value[userIndex], ...data }
      }

      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Failed to update user:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete a user
   * @param {number} userId - User ID
   * @param {Object} options - Deletion options
   * @param {boolean} options.deleteCalendars - Delete user's calendars
   * @param {boolean} options.deleteDomains - Delete owned domains
   */
  async function deleteUser(userId, options = {}) {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (options.deleteCalendars) {
        params.append('delete_calendars', 'true')
      }
      if (options.deleteDomains) {
        params.append('delete_domains', 'true')
      }

      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${userId}?${params.toString()}`,
        {
          method: 'DELETE',
          headers: getAuthHeaders()
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete user')
      }

      // Remove from local users array
      users.value = users.value.filter(u => u.id !== userId)

      // Update pagination total
      if (pagination.value.total > 0) {
        pagination.value.total -= 1
        pagination.value.totalPages = Math.ceil(pagination.value.total / pagination.value.limit)
      }

      return { success: true }
    } catch (err) {
      error.value = err.message
      console.error('Failed to delete user:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  /**
   * Unlock a user account
   * @param {number} userId - User ID
   */
  async function unlockUser(userId) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${userId}/unlock`,
        {
          method: 'POST',
          headers: getAuthHeaders()
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to unlock user')
      }

      const data = await response.json()

      // Update local users array
      const userIndex = users.value.findIndex(u => u.id === userId)
      if (userIndex !== -1) {
        users.value[userIndex] = { ...users.value[userIndex], locked: false, failed_login_attempts: 0 }
      }

      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Failed to unlock user:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    users,
    loading,
    error,
    pagination,

    // API Functions
    listUsers,
    getUserDetails,
    updateUser,
    deleteUser,
    unlockUser
  }
}
