/**
 * Domain authentication composable for password-protected domains.
 *
 * Provides pure functions for client-side auth following functional principles.
 * Handles JWT tokens, localStorage, and authentication state management.
 */

import { ref, computed } from 'vue'
import { useHTTP } from './useHTTP'

const STORAGE_PREFIX = 'domain_auth_'
const TOKEN_EXPIRY_DAYS = 30
const REFRESH_THRESHOLD_DAYS = 25

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

  // Check authentication status on initialization
  const checkAuth = () => {
    isAdminAuthenticated.value = hasValidToken(domain, 'admin')
    isUserAuthenticated.value = hasValidToken(domain, 'user')
  }

  // Initialize
  checkAuth()

  /**
   * Verify password and obtain JWT token.
   *
   * @param {string} password - Plain text password
   * @param {string} level - 'admin' or 'user'
   * @returns {Promise<{success: boolean, error: string}>}
   */
  const verifyPassword = async (password, level) => {
    authLoading.value = true
    authError.value = null

    try {
      const endpoint = `/api/domains/${domain}/auth/verify-${level}`
      const result = await post(endpoint, { password })

      if (result.success && result.data.token) {
        storeToken(domain, level, result.data.token)

        if (level === 'admin') {
          isAdminAuthenticated.value = true
          isUserAuthenticated.value = true // Admin has user access too
        } else {
          isUserAuthenticated.value = true
        }

        return { success: true, error: '' }
      } else {
        authError.value = 'Invalid password'
        return { success: false, error: 'Invalid password' }
      }
    } catch (error) {
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
   * Logout and clear stored token.
   *
   * @param {string} level - 'admin' or 'user'
   */
  const logout = (level) => {
    clearToken(domain, level)

    if (level === 'admin') {
      isAdminAuthenticated.value = false
      isUserAuthenticated.value = false
    } else {
      isUserAuthenticated.value = false
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
    logout,
    checkAuth
  }
}

// Pure utility functions for token management

/**
 * Store JWT token in localStorage.
 *
 * @param {string} domain - Domain key
 * @param {string} level - 'admin' or 'user'
 * @param {string} token - JWT token
 */
export function storeToken(domain, level, token) {
  const key = `${STORAGE_PREFIX}${domain}_${level}`
  localStorage.setItem(key, token)
}

/**
 * Retrieve JWT token from localStorage.
 *
 * @param {string} domain - Domain key
 * @param {string} level - 'admin' or 'user'
 * @returns {string|null} Token or null if not found
 */
export function getToken(domain, level) {
  const key = `${STORAGE_PREFIX}${domain}_${level}`
  return localStorage.getItem(key)
}

/**
 * Clear JWT token from localStorage.
 *
 * @param {string} domain - Domain key
 * @param {string} level - 'admin' or 'user'
 */
export function clearToken(domain, level) {
  const key = `${STORAGE_PREFIX}${domain}_${level}`
  localStorage.removeItem(key)
}

/**
 * Parse JWT token payload (client-side only, no verification).
 *
 * @param {string} token - JWT token
 * @returns {object|null} Decoded payload or null
 */
export function parseTokenPayload(token) {
  if (!token) return null

  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null

    const payload = parts[1]
    const decoded = JSON.parse(atob(payload))
    return decoded
  } catch (error) {
    return null
  }
}

/**
 * Check if token is expired (client-side check).
 *
 * @param {string} token - JWT token
 * @returns {boolean} True if expired
 */
export function isTokenExpired(token) {
  const payload = parseTokenPayload(token)
  if (!payload || !payload.exp) return true

  const now = Math.floor(Date.now() / 1000)
  return now >= payload.exp
}

/**
 * Check if domain has valid authentication token.
 *
 * @param {string} domain - Domain key
 * @param {string} level - 'admin' or 'user'
 * @returns {boolean} True if valid token exists
 */
export function hasValidToken(domain, level) {
  const token = getToken(domain, level)
  if (!token) return false

  return !isTokenExpired(token)
}

/**
 * Calculate token age in days.
 *
 * @param {string} token - JWT token
 * @returns {number} Age in days
 */
export function calculateTokenAgeDays(token) {
  const payload = parseTokenPayload(token)
  if (!payload || !payload.iat) return 0

  const now = Math.floor(Date.now() / 1000)
  const ageSeconds = now - payload.iat
  return ageSeconds / 86400
}

/**
 * Check if token should be refreshed (sliding window).
 *
 * @param {string} token - JWT token
 * @returns {boolean} True if should refresh
 */
export function shouldRefreshToken(token) {
  if (isTokenExpired(token)) return false

  const age = calculateTokenAgeDays(token)
  return age >= REFRESH_THRESHOLD_DAYS
}
