/**
 * Authentication composable for user account management.
 *
 * Handles:
 * - User registration (username required, email/password optional)
 * - Login (password only if account has one)
 * - JWT token management
 * - Current user state
 */

import { ref, computed } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'

// Global state (persisted across component instances)
const user = ref(null)
const token = ref(localStorage.getItem('auth_token'))

// Function to sync legacy username ref (imported lazily to avoid circular dependency)
let syncUsername = null
const ensureSyncUsername = () => {
  if (!syncUsername) {
    const { useUsername } = require('./useUsername')
    const { username } = useUsername()
    syncUsername = (name) => {
      username.value = name
    }
  }
  return syncUsername
}

export function useAuth() {
  const isLoggedIn = computed(() => !!user.value)
  const hasPassword = computed(() => user.value?.has_password || false)

  /**
   * Register new user account.
   * @param {string} username - Username (required)
   * @param {string|null} email - Email (optional)
   * @param {string|null} password - Password (optional)
   * @returns {Promise<{success: boolean, error: string|null}>}
   */
  const register = async (username, email = null, password = null) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/users/register`, {
        username,
        email: email || null,
        password: password || null
      })

      // Store token and user
      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('auth_token', token.value)

      // Sync legacy username ref
      const sync = ensureSyncUsername()
      sync(response.data.user.username)

      return { success: true, error: null }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      }
    }
  }

  /**
   * Login to existing account.
   * @param {string} username - Username
   * @param {string|null} password - Password (required only if account has one)
   * @returns {Promise<{success: boolean, error: string|null}>}
   */
  const login = async (username, password = null) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/users/login`, {
        username,
        password: password || null
      })

      // Store token and user
      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('auth_token', token.value)

      // Sync legacy username ref
      const sync = ensureSyncUsername()
      sync(response.data.user.username)

      return { success: true, error: null }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  /**
   * Logout current user.
   */
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')

    // Clear legacy username ref
    const sync = ensureSyncUsername()
    sync('')
  }

  /**
   * Fetch current user profile.
   * @returns {Promise<{success: boolean, error: string|null}>}
   */
  const fetchCurrentUser = async () => {
    if (!token.value) {
      return { success: false, error: 'No token' }
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/api/users/me`, {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      user.value = response.data

      // Sync legacy username ref
      const sync = ensureSyncUsername()
      sync(response.data.username)

      return { success: true, error: null }
    } catch (error) {
      // Token might be expired
      if (error.response?.status === 401) {
        logout()
      }
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to fetch user'
      }
    }
  }

  /**
   * Update user profile (add/change email or password).
   * @param {Object} updates - {email, password, current_password}
   * @returns {Promise<{success: boolean, error: string|null}>}
   */
  const updateProfile = async (updates) => {
    if (!token.value) {
      return { success: false, error: 'Not authenticated' }
    }

    try {
      const response = await axios.patch(
        `${API_BASE_URL}/api/users/me`,
        updates,
        {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        }
      )

      user.value = response.data
      return { success: true, error: null }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to update profile'
      }
    }
  }

  /**
   * Request password reset email.
   * @param {string} email - User's email address
   * @returns {Promise<{success: boolean, error: string|null}>}
   */
  const requestPasswordReset = async (email) => {
    try {
      await axios.post(`${API_BASE_URL}/api/auth/request-reset`, { email })
      return { success: true, error: null }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to send reset email'
      }
    }
  }

  /**
   * Reset password with token from email.
   * @param {string} resetToken - Token from email
   * @param {string} newPassword - New password
   * @returns {Promise<{success: boolean, error: string|null}>}
   */
  const resetPassword = async (resetToken, newPassword) => {
    try {
      await axios.post(`${API_BASE_URL}/api/auth/reset-password`, {
        token: resetToken,
        new_password: newPassword
      })
      return { success: true, error: null }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to reset password'
      }
    }
  }

  /**
   * Verify reset token is valid.
   * @param {string} resetToken - Token to verify
   * @returns {Promise<{success: boolean, error: string|null}>}
   */
  const verifyResetToken = async (resetToken) => {
    try {
      await axios.get(`${API_BASE_URL}/api/auth/verify-token/${resetToken}`)
      return { success: true, error: null }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Invalid or expired token'
      }
    }
  }

  /**
   * Get auth headers for API requests.
   * @returns {Object} - Headers object with Authorization
   */
  const getAuthHeaders = () => {
    if (!token.value) {
      return {}
    }
    return {
      Authorization: `Bearer ${token.value}`
    }
  }

  // Auto-fetch user on mount if token exists
  if (token.value && !user.value) {
    fetchCurrentUser()
  }

  return {
    // State
    user,
    token,
    isLoggedIn,
    hasPassword,

    // Actions
    register,
    login,
    logout,
    fetchCurrentUser,
    updateProfile,
    requestPasswordReset,
    resetPassword,
    verifyResetToken,
    getAuthHeaders
  }
}
