/**
 * Global App Store - Simplified, focused only on global app state
 * Calendar, events, and filter logic moved to dedicated stores
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // Global app state only
  const currentView = ref('login')
  const user = ref({
    loggedIn: false,
    id: 'anonymous'
  })

  // Computed
  const isLoggedIn = computed(() => user.value.loggedIn)

  // Navigation actions
  const setView = (view) => {
    currentView.value = view
  }

  const login = async () => {
    // Simple login simulation - in real app this would authenticate
    user.value = {
      loggedIn: true,
      id: 'anonymous'
    }
    currentView.value = 'home'
    return true
  }

  const logout = () => {
    user.value = {
      loggedIn: false,
      id: 'anonymous'
    }
    currentView.value = 'login'
  }

  // Navigation helpers
  const goToHome = () => {
    setView('home')
  }

  const goToCalendar = () => {
    setView('calendar')
  }

  const goToLogin = () => {
    setView('login')
  }

  // User ID for API calls
  const getUserId = () => {
    return user.value.id
  }

  return {
    // State
    currentView,
    user,

    // Computed
    isLoggedIn,

    // Actions
    setView,
    login,
    logout,
    goToHome,
    goToCalendar,
    goToLogin,
    getUserId
  }
})