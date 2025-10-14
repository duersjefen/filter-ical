/**
 * Global Notification Store
 * Manages application-wide notifications (success, error, warning, info)
 * Supports multiple simultaneous notifications with auto-dismiss and progress tracking
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  // State: Array of active notifications
  const notifications = ref([])

  // Internal counter for unique notification IDs
  let notificationIdCounter = 0

  /**
   * Add a notification to the queue
   * @param {Object} notification - Notification configuration
   * @param {string} notification.message - Message to display
   * @param {string} notification.type - Type: 'success', 'error', 'warning', 'info'
   * @param {number} notification.duration - Auto-dismiss duration in milliseconds (default: 5000)
   * @returns {number} Notification ID
   */
  const addNotification = ({ message, type = 'info', duration = 5000 }) => {
    // Deduplication: Check if same message+type exists within last 2 seconds
    const now = Date.now()
    const duplicate = notifications.value.find(
      n => n.message === message &&
           n.type === type &&
           (now - n.createdAt) < 2000
    )

    if (duplicate) {
      // Don't add duplicate, return existing ID
      return duplicate.id
    }

    const id = ++notificationIdCounter

    const notification = {
      id,
      message,
      type,
      duration,
      progress: 100, // Progress bar starts at 100%
      timer: null,
      progressTimer: null,
      createdAt: Date.now()
    }

    // Add to notifications array
    notifications.value.push(notification)

    // Start auto-dismiss timer
    if (duration > 0) {
      startAutoDismiss(id, duration)
    }

    return id
  }

  /**
   * Start auto-dismiss timer and progress bar animation
   */
  const startAutoDismiss = (notificationId, duration) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (!notification) return

    // Progress bar update interval (update every 50ms for smooth animation)
    const progressInterval = 50
    const progressDecrement = (100 / duration) * progressInterval

    notification.progressTimer = setInterval(() => {
      notification.progress -= progressDecrement
      if (notification.progress <= 0) {
        notification.progress = 0
        clearInterval(notification.progressTimer)
      }
    }, progressInterval)

    // Auto-dismiss timer
    notification.timer = setTimeout(() => {
      removeNotification(notificationId)
    }, duration)
  }

  /**
   * Remove a notification by ID
   */
  const removeNotification = (notificationId) => {
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index === -1) return

    const notification = notifications.value[index]

    // Clear timers
    if (notification.timer) {
      clearTimeout(notification.timer)
    }
    if (notification.progressTimer) {
      clearInterval(notification.progressTimer)
    }

    // Remove from array
    notifications.value.splice(index, 1)
  }

  /**
   * Clear all notifications
   */
  const clearAll = () => {
    // Clear all timers
    notifications.value.forEach(notification => {
      if (notification.timer) {
        clearTimeout(notification.timer)
      }
      if (notification.progressTimer) {
        clearInterval(notification.progressTimer)
      }
    })

    // Clear array
    notifications.value = []
  }

  /**
   * Pause auto-dismiss for a notification (useful on hover)
   */
  const pauseAutoDismiss = (notificationId) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (!notification) return

    if (notification.timer) {
      clearTimeout(notification.timer)
      notification.timer = null
    }
    if (notification.progressTimer) {
      clearInterval(notification.progressTimer)
      notification.progressTimer = null
    }
  }

  /**
   * Resume auto-dismiss for a notification
   */
  const resumeAutoDismiss = (notificationId) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (!notification) return

    // Calculate remaining time based on progress
    const remainingDuration = (notification.progress / 100) * notification.duration

    if (remainingDuration > 0) {
      startAutoDismiss(notificationId, remainingDuration)
    } else {
      removeNotification(notificationId)
    }
  }

  return {
    // State
    notifications,

    // Actions
    addNotification,
    removeNotification,
    clearAll,
    pauseAutoDismiss,
    resumeAutoDismiss
  }
})
