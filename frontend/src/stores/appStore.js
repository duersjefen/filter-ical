/**
 * App Store - Handles user authentication and basic app state
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAPI } from '../composables/useAPI'

export const useAppStore = defineStore('app', () => {
  // State
  const user = ref({
    username: null,
    loggedIn: false
  })

  // API composable for error handling
  const api = useAPI()

  // Computed
  const isLoggedIn = computed(() => user.value.loggedIn)

  // Actions
  const login = async (username) => {
    const result = await api.safeExecute(async () => {
      // Require actual username - no anonymous fallback
      if (!username || username.trim() === '' || username.trim().toLowerCase() === 'anonymous') {
        throw new Error('Please enter a valid username')
      }
      
      const userData = {
        username: username.trim(),
        loggedIn: true,
        loginTime: new Date().getTime(), // Add timestamp for session tracking
        lastActivity: new Date().getTime()
      }
      
      user.value = userData
      
      // Store in localStorage for persistence
      localStorage.setItem('icalViewer_user', JSON.stringify(userData))
      
      return userData
    })

    return result
  }

  const logout = () => {
    user.value = {
      username: null,
      loggedIn: false
    }
    localStorage.removeItem('icalViewer_user')
  }

  const initializeApp = () => {
    try {
      const savedUser = localStorage.getItem('icalViewer_user')
      if (savedUser) {
        const parsed = JSON.parse(savedUser)
        
        if (parsed && parsed.username && parsed.loggedIn) {
          // Check if session is valid (optional - could add expiration logic here)
          const now = new Date().getTime()
          const sessionAge = now - (parsed.loginTime || now)
          const maxSessionAge = 7 * 24 * 60 * 60 * 1000 // 7 days
          
          if (sessionAge < maxSessionAge) {
            // Update last activity timestamp
            parsed.lastActivity = now
            user.value = parsed
            localStorage.setItem('icalViewer_user', JSON.stringify(parsed))
            return true
          } else {
            // Session expired
            logout()
            return false
          }
        }
      }
    } catch (error) {
      console.warn('Error loading saved user:', error)
      logout()
    }
    return false
  }

  const getUserId = () => {
    if (!user.value.loggedIn || !user.value.username) {
      throw new Error('User not logged in - authentication required')
    }
    return user.value.username
  }

  const updateActivity = () => {
    if (user.value.loggedIn) {
      user.value.lastActivity = new Date().getTime()
      localStorage.setItem('icalViewer_user', JSON.stringify(user.value))
    }
  }

  // Deprecated navigation method (components should use router directly)
  const setView = (view) => {
    console.warn('setView is deprecated - components should use router.push() directly')
  }

  return {
    // State
    user,
    
    // Computed
    isLoggedIn,
    
    // Actions
    login,
    logout,
    initializeApp,
    getUserId,
    updateActivity,
    setView
  }
})