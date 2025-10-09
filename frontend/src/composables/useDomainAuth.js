/**
 * Domain authentication composable for password-protected domains.
 *
 * Simplified authentication - requires user login.
 * Domain access is saved to user's account in database.
 */

import { ref, computed } from 'vue'
import { useHTTP } from './useHTTP'
import { useAuth } from './useAuth'

/**
 * Main composable for domain authentication.
 *
 * @param {string} domain - Domain key
 * @returns {object} Auth state and functions
 */
export function useDomainAuth(domain) {
  const { post, patch, del, get } = useHTTP()

  // Reactive state
  const isAdminAuthenticated = ref(false)
  const isUserAuthenticated = ref(false)
  const authError = ref(null)
  const authLoading = ref(false)

  /**
   * Verify password - requires user to be logged in.
   * Access is saved to user's account in database.
   *
   * @param {string} password - Plain text password
   * @param {string} level - 'admin' or 'user'
   * @returns {Promise<{success: boolean, error: string}>}
   */
  const verifyPassword = async (password, level) => {
    authLoading.value = true
    authError.value = null

    const { isLoggedIn } = useAuth()

    // Check if user is logged in first
    if (!isLoggedIn.value) {
      authError.value = 'Please log in first to access this domain'
      authLoading.value = false
      return { success: false, error: 'Please log in first to access this domain' }
    }

    try {
      const endpoint = `/api/domains/${domain}/auth/verify-${level}`
      const result = await post(endpoint, { password })

      if (result.success) {
        if (level === 'admin') {
          isAdminAuthenticated.value = true
          isUserAuthenticated.value = true // Admin has user access too
        } else {
          isUserAuthenticated.value = true
        }

        return { success: true, error: '' }
      } else {
        authError.value = result.error || 'Invalid password'
        return { success: false, error: result.error || 'Invalid password' }
      }
    } catch (error) {
      // Handle 401 specifically - user needs to log in
      if (error.response?.status === 401) {
        const errorMsg = 'Please log in first to access this domain'
        authError.value = errorMsg
        return { success: false, error: errorMsg }
      }

      const errorMsg = error.response?.data?.detail || 'Authentication failed'
      authError.value = errorMsg
      return { success: false, error: errorMsg }
    } finally {
      authLoading.value = false
    }
  }

  /**
   * Set admin password for domain.
   *
   * @param {string} password - New password
   * @returns {Promise<{success: boolean, error: string}>}
   */
  const setAdminPassword = async (password) => {
    try {
      const result = await patch(`/api/domains/${domain}/auth/set-admin-password`, { password })
      return { success: result.success, error: result.success ? '' : 'Failed to set password' }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Failed to set password' }
    }
  }

  /**
   * Set user password for domain.
   *
   * @param {string} password - New password
   * @returns {Promise<{success: boolean, error: string}>}
   */
  const setUserPassword = async (password) => {
    try {
      const result = await patch(`/api/domains/${domain}/auth/set-user-password`, { password })
      return { success: result.success, error: result.success ? '' : 'Failed to set password' }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Failed to set password' }
    }
  }

  /**
   * Remove admin password for domain.
   *
   * @returns {Promise<{success: boolean, error: string}>}
   */
  const removeAdminPassword = async () => {
    try {
      const result = await del(`/api/domains/${domain}/auth/remove-admin-password`)
      return { success: result.success, error: result.success ? '' : 'Failed to remove password' }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Failed to remove password' }
    }
  }

  /**
   * Remove user password for domain.
   *
   * @returns {Promise<{success: boolean, error: string}>}
   */
  const removeUserPassword = async () => {
    try {
      const result = await del(`/api/domains/${domain}/auth/remove-user-password`)
      return { success: result.success, error: result.success ? '' : 'Failed to remove password' }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Failed to remove password' }
    }
  }

  /**
   * Get password status for domain (public endpoint).
   *
   * @returns {Promise<{admin_password_set: boolean, user_password_set: boolean}>}
   */
  const getPasswordStatus = async () => {
    try {
      const result = await get(`/api/domains/${domain}/auth/status`)
      return result.data || { admin_password_set: false, user_password_set: false }
    } catch (error) {
      return { admin_password_set: false, user_password_set: false }
    }
  }

  /**
   * Check if currently logged-in user has access to this domain.
   * Queries the user's domain access from the database.
   *
   * @returns {Promise<void>}
   */
  const checkAuth = async () => {
    const { isLoggedIn } = useAuth()

    // If not logged in, no access
    if (!isLoggedIn.value) {
      isUserAuthenticated.value = false
      isAdminAuthenticated.value = false
      return
    }

    try {
      // Query user's domains to check access
      const result = await get('/api/users/me/domains')

      if (result.success && result.data) {
        // Check if this domain is in any of the access lists
        const hasAccess =
          result.data.owned_domains?.some(d => d.domain_key === domain) ||
          result.data.admin_domains?.some(d => d.domain_key === domain) ||
          result.data.password_access_domains?.some(d => d.domain_key === domain)

        if (hasAccess) {
          // Check access level from password_access_domains
          const passwordAccess = result.data.password_access_domains?.find(d => d.domain_key === domain)
          if (passwordAccess?.access_level === 'admin') {
            isAdminAuthenticated.value = true
            isUserAuthenticated.value = true
          } else {
            isUserAuthenticated.value = true
          }
        } else {
          isUserAuthenticated.value = false
          isAdminAuthenticated.value = false
        }
      }
    } catch (error) {
      // On error, assume no access
      isUserAuthenticated.value = false
      isAdminAuthenticated.value = false
    }
  }

  return {
    // State
    isAdminAuthenticated,
    isUserAuthenticated,
    authError,
    authLoading,

    // Functions
    verifyPassword,
    setAdminPassword,
    setUserPassword,
    removeAdminPassword,
    removeUserPassword,
    getPasswordStatus,
    checkAuth
  }
}
