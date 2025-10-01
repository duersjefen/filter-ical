/**
 * Notification Composable
 * Provides a simple API for showing notifications throughout the application
 *
 * Usage:
 * import { useNotification } from '@/composables/useNotification'
 *
 * const notify = useNotification()
 * notify.success('Operation completed!')
 * notify.error('Something went wrong')
 * notify.warning('Please be careful')
 * notify.info('New update available')
 */
import { useNotificationStore } from '../stores/notification'

export function useNotification() {
  const notificationStore = useNotificationStore()

  /**
   * Show a success notification
   * @param {string} message - Message to display
   * @param {Object} options - Additional options
   * @param {number} options.duration - Auto-dismiss duration in ms (default: 5000)
   * @returns {number} Notification ID
   */
  const success = (message, options = {}) => {
    return notificationStore.addNotification({
      message,
      type: 'success',
      duration: options.duration ?? 5000
    })
  }

  /**
   * Show an error notification
   * @param {string} message - Message to display
   * @param {Object} options - Additional options
   * @param {number} options.duration - Auto-dismiss duration in ms (default: 7000)
   * @returns {number} Notification ID
   */
  const error = (message, options = {}) => {
    return notificationStore.addNotification({
      message,
      type: 'error',
      duration: options.duration ?? 7000 // Errors stay longer by default
    })
  }

  /**
   * Show a warning notification
   * @param {string} message - Message to display
   * @param {Object} options - Additional options
   * @param {number} options.duration - Auto-dismiss duration in ms (default: 6000)
   * @returns {number} Notification ID
   */
  const warning = (message, options = {}) => {
    return notificationStore.addNotification({
      message,
      type: 'warning',
      duration: options.duration ?? 6000
    })
  }

  /**
   * Show an info notification
   * @param {string} message - Message to display
   * @param {Object} options - Additional options
   * @param {number} options.duration - Auto-dismiss duration in ms (default: 5000)
   * @returns {number} Notification ID
   */
  const info = (message, options = {}) => {
    return notificationStore.addNotification({
      message,
      type: 'info',
      duration: options.duration ?? 5000
    })
  }

  /**
   * Remove a specific notification
   * @param {number} notificationId - ID of notification to remove
   */
  const remove = (notificationId) => {
    notificationStore.removeNotification(notificationId)
  }

  /**
   * Clear all notifications
   */
  const clearAll = () => {
    notificationStore.clearAll()
  }

  return {
    success,
    error,
    warning,
    info,
    remove,
    clearAll
  }
}
