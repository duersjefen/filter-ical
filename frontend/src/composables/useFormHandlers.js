/**
 * useFormHandlers - Form submission and state management utilities
 *
 * Provides reusable form handling logic for loading states, error management,
 * and submission handling.
 */

import { ref } from 'vue'

export function useFormHandlers() {
  const isSubmitting = ref(false)
  const errors = ref({})

  /**
   * Handles form submission with validation and error handling
   * @param {Function} submitFn - Async function to execute on submit
   * @param {Function} [validationFn] - Optional validation function that returns errors object
   * @returns {Promise<void>}
   */
  const handleSubmit = async (submitFn, validationFn = null) => {
    if (isSubmitting.value) return

    // Clear previous errors
    errors.value = {}

    // Run validation if provided
    if (validationFn) {
      const validationErrors = validationFn()
      if (Object.keys(validationErrors).length > 0) {
        errors.value = validationErrors
        return
      }
    }

    isSubmitting.value = true
    try {
      await submitFn()
    } catch (error) {
      errors.value = { general: error.message || 'An error occurred' }
      throw error // Re-throw so caller can handle if needed
    } finally {
      isSubmitting.value = false
    }
  }

  /**
   * Handles form cancellation
   * @param {Function} [resetFn] - Optional function to reset form state
   */
  const handleCancel = (resetFn) => {
    errors.value = {}
    if (resetFn) resetFn()
  }

  /**
   * Clears all errors
   */
  const clearErrors = () => {
    errors.value = {}
  }

  /**
   * Sets a specific error
   * @param {string} field - Field name or 'general' for form-level errors
   * @param {string} message - Error message
   */
  const setError = (field, message) => {
    errors.value[field] = message
  }

  /**
   * Gets error for a specific field
   * @param {string} field - Field name
   * @returns {string|undefined} - Error message if exists
   */
  const getError = (field) => {
    return errors.value[field]
  }

  /**
   * Checks if form has any errors
   * @returns {boolean}
   */
  const hasErrors = () => {
    return Object.keys(errors.value).length > 0
  }

  return {
    isSubmitting,
    errors,
    handleSubmit,
    handleCancel,
    clearErrors,
    setError,
    getError,
    hasErrors
  }
}
