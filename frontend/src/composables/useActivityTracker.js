/**
 * Activity Tracker Composable
 * Tracks user activity to keep sessions fresh
 */
import { onMounted, onUnmounted } from 'vue'
import { useAppStore } from '../stores/app'

export function useActivityTracker() {
  const appStore = useAppStore()
  let activityTimeout = null

  const trackActivity = () => {
    // Clear existing timeout
    if (activityTimeout) {
      clearTimeout(activityTimeout)
    }

    // Update activity immediately if user is logged in
    if (appStore.isLoggedIn) {
      appStore.updateActivity()
    }

    // Set timeout to update activity every 5 minutes of continuous use
    activityTimeout = setTimeout(() => {
      if (appStore.isLoggedIn) {
        appStore.updateActivity()
      }
    }, 5 * 60 * 1000) // 5 minutes
  }

  const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']

  onMounted(() => {
    // Track initial activity
    if (appStore.isLoggedIn) {
      trackActivity()
    }

    // Add event listeners for user activity
    events.forEach(event => {
      document.addEventListener(event, trackActivity, { passive: true })
    })
  })

  onUnmounted(() => {
    // Clean up event listeners
    events.forEach(event => {
      document.removeEventListener(event, trackActivity)
    })

    // Clear timeout
    if (activityTimeout) {
      clearTimeout(activityTimeout)
    }
  })

  return {
    trackActivity
  }
}