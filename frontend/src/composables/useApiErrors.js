/**
 * useApiErrors - API error handling utilities
 *
 * Provides consistent error handling and display logic for API responses.
 */

import { ref, computed } from 'vue'

export function useApiErrors() {
  const error = ref(null)

  /**
   * Computed property to check if error exists
   */
  const hasError = computed(() => error.value !== null)

  /**
   * Sets error from various error formats
   * @param {string|Error|Object} err - Error to set
   */
  const setError = (err) => {
    if (!err) {
      error.value = null
      return
    }

    // Handle string errors
    if (typeof err === 'string') {
      error.value = err
      return
    }

    // Handle API response errors (from useHTTP)
    if (err?.response?.data?.detail) {
      error.value = err.response.data.detail
      return
    }

    // Handle Error objects
    if (err?.message) {
      error.value = err.message
      return
    }

    // Fallback for unknown error types
    error.value = 'An unknown error occurred'
  }

  /**
   * Clears the current error
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * Sets error with a custom message
   * @param {string} message - Custom error message
   */
  const setCustomError = (message) => {
    error.value = message
  }

  /**
   * Wraps an async function with error handling
   * @param {Function} fn - Async function to wrap
   * @returns {Function} - Wrapped function
   */
  const withErrorHandling = (fn) => {
    return async (...args) => {
      clearError()
      try {
        return await fn(...args)
      } catch (err) {
        setError(err)
        throw err // Re-throw so caller can handle if needed
      }
    }
  }

  return {
    error,
    hasError,
    setError,
    clearError,
    setCustomError,
    withErrorHandling
  }
}
