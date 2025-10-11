/**
 * Username Management Composable
 * Simple username state with localStorage persistence for UI preferences
 *
 * NOTE: This is a legacy composable. The system now uses JWT authentication.
 * When a username is detected, it auto-registers/logs in to get a JWT token.
 */
import { ref, watch } from 'vue'
import { useAuth } from './useAuth'

// Username state - reactive and persistent
const username = ref('')
const STORAGE_KEY = 'icalViewer_username'

// Username change callbacks for data source switching
const usernameChangeCallbacks = new Set()

// Initialize username from localStorage and auto-login
const initializeUsername = async () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && typeof saved === 'string') {
      username.value = saved.trim()

      // Auto-login with saved username if not already authenticated
      const auth = useAuth()
      if (username.value && !localStorage.getItem('auth_token')) {
        // Try login first (in case account exists)
        const loginResult = await auth.login(username.value)
        if (!loginResult.success) {
          // If login fails, register new account (password-less)
          await auth.register(username.value)
        }
      }
    }
  } catch (error) {
    // Silent fail - username loading is optional
  }
}

// Validation function for usernames
const isValidUsername = (name) => {
  if (!name || typeof name !== 'string') return false

  const trimmed = name.trim()
  // Allow 3-20 characters, alphanumeric plus underscore, hyphen, and spaces
  const validPattern = /^[a-zA-Z0-9_\- ]{3,20}$/

  return validPattern.test(trimmed)
}

// Main username composable
export function useUsername() {
  // Initialize on first use
  if (!username.value) {
    initializeUsername()
  }

  // Watch for changes and persist to localStorage
  watch(username, (newUsername, oldUsername) => {
    try {
      if (newUsername && newUsername.trim()) {
        localStorage.setItem(STORAGE_KEY, newUsername.trim())
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }
      
      // Trigger username change callbacks for data source switching
      if (newUsername !== oldUsername) {
        usernameChangeCallbacks.forEach(callback => {
          try {
            callback(newUsername, oldUsername)
          } catch (error) {
            console.error('Username change callback error:', error)
          }
        })
      }
    } catch (error) {
      // Silent fail - username saving is optional
    }
  }, { immediate: false })

  // Set username with validation and auto-login
  const setUsername = async (newUsername) => {
    if (newUsername && typeof newUsername === 'string') {
      const trimmed = newUsername.trim()
      username.value = trimmed

      // Auto-register/login when username is set
      if (trimmed) {
        const auth = useAuth()
        // Try login first
        const loginResult = await auth.login(trimmed)
        if (!loginResult.success) {
          // If login fails, register new account
          await auth.register(trimmed)
        }
      }
    } else {
      username.value = ''
    }
  }

  // Clear username
  const clearUsername = () => {
    username.value = ''
  }

  // Get current user ID (username or unique anonymous ID as fallback)
  const getUserId = () => {
    const trimmed = username.value?.trim()
    if (trimmed) {
      return trimmed
    }
    
    // For anonymous users, generate a unique browser-specific ID
    // This ensures filters don't persist across different browsers
    const anonymousKey = 'icalViewer_anonymousId'
    try {
      let anonymousId = localStorage.getItem(anonymousKey)
      if (!anonymousId) {
        // Generate unique ID based on timestamp and random number
        anonymousId = `anon_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`
        localStorage.setItem(anonymousKey, anonymousId)
      }
      return anonymousId
    } catch (error) {
      // Fallback if localStorage fails - use session-based ID
      return `anon_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`
    }
  }


  // Check if user has set a custom username
  const hasCustomUsername = () => {
    const trimmed = username.value?.trim()
    return trimmed && trimmed !== 'public'
  }

  // Register callback for username changes (for data source switching)
  const onUsernameChange = (callback) => {
    usernameChangeCallbacks.add(callback)
    
    // Return unregister function
    return () => {
      usernameChangeCallbacks.delete(callback)
    }
  }

  return {
    // State
    username,
    
    // Actions
    setUsername,
    clearUsername,
    
    // Getters
    getUserId,
    hasCustomUsername,
    
    // Utilities
    isValidUsername,
    
    // Username change detection
    onUsernameChange
  }
}