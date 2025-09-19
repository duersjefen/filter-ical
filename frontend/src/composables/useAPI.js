/**
 * API Error Handling Composable
 * Eliminates repeated try/catch/finally patterns
 */
import { ref } from 'vue'

export function useAPI() {
  const loading = ref(false)
  const error = ref(null)

  /**
   * Execute an API call with standardized error handling
   * @param {Function} apiCall - Async function that makes the API call
   * @returns {Promise} - Result of the API call
   */
  const execute = async (apiCall) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await apiCall()
      return result
    } catch (err) {
      // Create more detailed error information
      const status = err.response?.status
      const detail = err.response?.data?.detail || err.response?.data?.message || 'An error occurred'
      
      error.value = detail
      
      // Enhance error object for better handling
      err.status = status
      err.detail = detail
      
      throw err // Re-throw so caller can handle if needed
    } finally {
      loading.value = false
    }
  }

  /**
   * Execute an API call and return the result without throwing
   * @param {Function} apiCall - Async function that makes the API call  
   * @returns {Promise<{success: boolean, data?: any, error?: string}>}
   */
  const safeExecute = async (apiCall) => {
    try {
      const result = await execute(apiCall)
      return { success: true, data: result }
    } catch (err) {
      return { 
        success: false, 
        error: error.value,
        status: err.status,
        detail: err.detail
      }
    }
  }

  /**
   * Clear the current error state
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * Set an error message manually
   */
  const setError = (message) => {
    error.value = message
  }

  return {
    loading,
    error,
    execute,
    safeExecute,
    clearError,
    setError
  }
}