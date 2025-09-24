/**
 * Username Management Composable
 * Simple username state with localStorage persistence for UI preferences
 */
import { ref, watch } from 'vue'

// Username state - reactive and persistent
const username = ref('')
const STORAGE_KEY = 'icalViewer_username'

// Username change callbacks for data source switching
const usernameChangeCallbacks = new Set()

// Initialize username from localStorage
const initializeUsername = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && typeof saved === 'string') {
      username.value = saved.trim()
    }
  } catch (error) {
    console.warn('Failed to load username from localStorage:', error)
  }
}

// Validation function for usernames
const isValidUsername = (name) => {
  if (!name || typeof name !== 'string') return false
  
  const trimmed = name.trim()
  // Allow 3-20 characters, alphanumeric plus underscore and hyphen
  const validPattern = /^[a-zA-Z0-9_-]{3,20}$/
  
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
        console.log('🔄 Username changed:', { from: oldUsername, to: newUsername })
        usernameChangeCallbacks.forEach(callback => {
          try {
            callback(newUsername, oldUsername)
          } catch (error) {
            console.error('Username change callback error:', error)
          }
        })
      }
    } catch (error) {
      console.warn('Failed to save username to localStorage:', error)
    }
  }, { immediate: false })

  // Set username with validation
  const setUsername = (newUsername) => {
    if (newUsername && typeof newUsername === 'string') {
      const trimmed = newUsername.trim()
      username.value = trimmed
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