/**
 * Activity Tracker Composable
 * No-op for public access mode - no session tracking needed
 */
import { onMounted, onUnmounted } from 'vue'

export function useActivityTracker() {
  // No activity tracking needed for public access
  const trackActivity = () => {
    // No-op - public access doesn't need session tracking
  }

  onMounted(() => {
    // No activity tracking setup needed for public access
  })

  onUnmounted(() => {
    // No cleanup needed for public access
  })

  return {
    trackActivity
  }
}