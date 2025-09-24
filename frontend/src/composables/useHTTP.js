/**
 * HTTP Client Composable
 * Provides HTTP methods with error handling and loading states
 */
import { ref } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'

export function useHTTP() {
  // State management
  const loading = ref(false)
  const error = ref(null)

  // Error handling
  const clearError = () => {
    error.value = null
  }

  const setError = (message) => {
    error.value = message
  }

  // Core execution with error handling
  const execute = async (httpCall) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await httpCall()
      return result
    } catch (err) {
      const status = err.response?.status
      const detail = err.response?.data?.detail || err.response?.data?.message || 'An error occurred'
      
      error.value = detail
      err.status = status
      err.detail = detail
      
      throw err
    } finally {
      loading.value = false
    }
  }

  // Safe execution (returns result object instead of throwing)
  const safeExecute = async (httpCall) => {
    try {
      const result = await execute(httpCall)
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

  // HTTP method implementation
  const request = async (endpoint, options = {}) => {
    const {
      method = 'GET',
      data = null,
      headers = {}
    } = options

    return await safeExecute(async () => {
      const config = {
        method,
        url: `${API_BASE_URL}${endpoint}`,
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

  // HTTP method helpers
  const get = (endpoint, headers = {}) => 
    request(endpoint, { method: 'GET', headers })

  const post = (endpoint, data, headers = {}) => 
    request(endpoint, { method: 'POST', data, headers })

  const put = (endpoint, data, headers = {}) => 
    request(endpoint, { method: 'PUT', data, headers })

  const del = (endpoint, headers = {}) => 
    request(endpoint, { method: 'DELETE', headers })

  // Raw axios access for advanced usage
  const rawRequest = async (config) => {
    return await execute(async () => {
      const response = await axios(config)
      return response
    })
  }

  return {
    // State
    loading,
    error,
    clearError,
    setError,
    
    // Core functions
    execute,
    safeExecute,
    
    // HTTP methods
    request,
    get,
    post,
    put,
    del,
    
    // Advanced usage
    rawRequest
  }
}