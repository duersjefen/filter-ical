/**
 * Username Management Composable
 * Simple username state with localStorage persistence for data segregation
 */
import { ref, watch } from 'vue'

// Username state - reactive and persistent
const username = ref('')
const STORAGE_KEY = 'icalViewer_username'

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
  watch(username, (newUsername) => {
    try {
      if (newUsername && newUsername.trim()) {
        localStorage.setItem(STORAGE_KEY, newUsername.trim())
      } else {
        localStorage.removeItem(STORAGE_KEY)
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

  // Get current user ID (username or 'public' as fallback)
  const getUserId = () => {
    const trimmed = username.value?.trim()
    return trimmed || 'public'
  }


  // Check if user has set a custom username
  const hasCustomUsername = () => {
    const trimmed = username.value?.trim()
    return trimmed && trimmed !== 'public'
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
    isValidUsername
  }
}