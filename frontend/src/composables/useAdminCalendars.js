/**
 * Admin calendar permissions composable.
 *
 * Provides functions for managing calendar permissions in the admin panel following
 * the functional programming principles from CLAUDE.md.
 */

import { ref } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { API_BASE_URL } from '@/constants/api'

export function useAdminCalendars() {
  const adminStore = useAdminStore()

  // Reactive state
  const calendars = ref([])
  const permissions = ref({})
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    total: 0,
    page: 1,
    limit: 20,
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
   * List all calendars with pagination and filters
   * @param {number} page - Page number (1-indexed)
   * @param {number} limit - Items per page
   * @param {string} type - Filter by calendar type ('user' or 'domain')
   */
  async function listCalendars(page = 1, limit = 20, type = '') {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString()
      })

      if (type) {
        params.append('type', type)
      }

      const response = await fetch(
        `${API_BASE_URL}/api/admin/calendars?${params.toString()}`,
        {
          headers: getAuthHeaders()
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to load calendars')
      }

      const data = await response.json()
      calendars.value = data.calendars || []
      pagination.value = {
        total: data.total || 0,
        page: data.page || page,
        limit: data.limit || limit,
        totalPages: Math.ceil((data.total || 0) / limit)
      }

      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Failed to list calendars:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  /**
   * Get permissions for a specific calendar
   * @param {number|string} calendarId - Calendar ID (user calendar) or domain key
   */
  async function getCalendarPermissions(calendarId) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/calendars/${calendarId}/permissions`,
        {
          headers: getAuthHeaders()
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to load calendar permissions')
      }

      const data = await response.json()
      permissions.value[calendarId] = data.permissions || []

      return { success: true, data: data.permissions || [] }
    } catch (err) {
      error.value = err.message
      console.error('Failed to get calendar permissions:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  /**
   * Grant permission to a user for a calendar
   * @param {number|string} calendarId - Calendar ID or domain key
   * @param {number} userId - User ID to grant permission to
   * @param {string} level - Permission level ('read' or 'write')
   */
  async function grantPermission(calendarId, userId, level = 'read') {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/calendars/${calendarId}/permissions`,
        {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            user_id: userId,
            permission_level: level
          })
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to grant permission')
      }

      const data = await response.json()

      // Update local permissions cache
      await getCalendarPermissions(calendarId)

      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Failed to grant permission:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  /**
   * Revoke permission from a user for a calendar
   * @param {number|string} calendarId - Calendar ID or domain key
   * @param {number} userId - User ID to revoke permission from
   */
  async function revokePermission(calendarId, userId) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/calendars/${calendarId}/permissions/${userId}`,
        {
          method: 'DELETE',
          headers: getAuthHeaders()
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to revoke permission')
      }

      // Update local permissions cache
      if (permissions.value[calendarId]) {
        permissions.value[calendarId] = permissions.value[calendarId].filter(
          p => p.user_id !== userId
        )
      }

      return { success: true }
    } catch (err) {
      error.value = err.message
      console.error('Failed to revoke permission:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  /**
   * Search users for permission assignment
   * @param {string} query - Search query (username or email)
   */
  async function searchUsers(query) {
    if (!query || query.trim().length === 0) {
      return { success: true, data: [] }
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/search?q=${encodeURIComponent(query)}`,
        {
          headers: getAuthHeaders()
        }
      )

      if (!response.ok) {
        await handleAuthError(response)
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to search users')
      }

      const data = await response.json()
      return { success: true, data: data.users || [] }
    } catch (err) {
      console.error('Failed to search users:', err)
      return { success: false, error: err.message }
    }
  }

  return {
    // State
    calendars,
    permissions,
    loading,
    error,
    pagination,

    // API Functions
    listCalendars,
    getCalendarPermissions,
    grantPermission,
    revokePermission,
    searchUsers
  }
}
