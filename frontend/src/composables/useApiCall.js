/**
 * Reusable API Call Composable
 * Eliminates the repetitive API call patterns across all stores
 */
import axios from 'axios'
import { useAPI } from './useAPI'

export function useApiCall() {
  const api = useAPI()

  /**
   * Make an API call with standardized error handling (public access)
   * @param {string} endpoint - API endpoint path
   * @param {Object} options - Request options
   * @param {string} options.method - HTTP method (GET, POST, PUT, DELETE)
   * @param {Object} options.data - Request body data
   * @param {Object} options.headers - Additional headers
   * @returns {Promise<{success: boolean, data?: any, error?: string}>}
   */
  const apiCall = async (endpoint, options = {}) => {
    const {
      method = 'GET',
      data = null,
      headers = {}
    } = options

    return await api.safeExecute(async () => {
      const config = {
        method,
        url: endpoint,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      }

      if (data && (method === 'POST' || method === 'PUT')) {
        config.data = data
      }

      const response = await axios(config)
      return response.data
    })
  }

  /**
   * GET request helper
   */
  const get = (endpoint, headers = {}) => 
    apiCall(endpoint, { method: 'GET', headers })

  /**
   * POST request helper
   */
  const post = (endpoint, data, headers = {}) => 
    apiCall(endpoint, { method: 'POST', data, headers })

  /**
   * PUT request helper
   */
  const put = (endpoint, data, headers = {}) => 
    apiCall(endpoint, { method: 'PUT', data, headers })

  /**
   * DELETE request helper
   */
  const del = (endpoint, headers = {}) => 
    apiCall(endpoint, { method: 'DELETE', headers })

  return {
    // Main API call function
    apiCall,
    
    // HTTP method helpers
    get,
    post,
    put,
    del,
    
    // Error state from useAPI composable
    loading: api.loading,
    error: api.error,
    clearError: api.clearError
  }
}