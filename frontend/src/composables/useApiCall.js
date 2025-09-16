/**
 * Reusable API Call Composable
 * Eliminates the repetitive API call patterns across all stores
 */
import axios from 'axios'
import { useAPI } from './useAPI'

export function useApiCall() {
  const api = useAPI()

  /**
   * Make an authenticated API call with standardized error handling
   * @param {string} endpoint - API endpoint path
   * @param {Object} options - Request options
   * @param {string} options.method - HTTP method (GET, POST, PUT, DELETE)
   * @param {Object} options.data - Request body data
   * @param {Object} options.headers - Additional headers
   * @param {Function} options.getUserHeaders - Function to get user auth headers
   * @returns {Promise<{success: boolean, data?: any, error?: string}>}
   */
  const apiCall = async (endpoint, options = {}) => {
    const {
      method = 'GET',
      data = null,
      headers = {},
      getUserHeaders = null
    } = options

    return await api.safeExecute(async () => {
      const config = {
        method,
        url: endpoint,
        headers: {
          ...headers,
          ...(getUserHeaders ? getUserHeaders() : {})
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
  const get = (endpoint, getUserHeaders) => 
    apiCall(endpoint, { method: 'GET', getUserHeaders })

  /**
   * POST request helper
   */
  const post = (endpoint, data, getUserHeaders) => 
    apiCall(endpoint, { method: 'POST', data, getUserHeaders })

  /**
   * PUT request helper
   */
  const put = (endpoint, data, getUserHeaders) => 
    apiCall(endpoint, { method: 'PUT', data, getUserHeaders })

  /**
   * DELETE request helper
   */
  const del = (endpoint, getUserHeaders) => 
    apiCall(endpoint, { method: 'DELETE', getUserHeaders })

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