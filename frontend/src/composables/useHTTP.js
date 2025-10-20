/**
 * HTTP Client Composable
 * Provides HTTP methods with error handling and loading states
 * Includes JWT token injection for all authenticated requests
 */
import { ref } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'

// Network status tracking
const isOnline = ref(navigator.onLine)

// Listen for online/offline events
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    isOnline.value = true
  })

  window.addEventListener('offline', () => {
    isOnline.value = false
  })
}

export { isOnline }

// Create axios instance with interceptors
const createHttpClient = () => {
  const client = axios.create({
    baseURL: API_BASE_URL
  })

  // Request interceptor - inject user auth token
  client.interceptors.request.use((config) => {
    // Use user's auth token for all authenticated requests
    const authToken = localStorage.getItem('auth_token')
    if (authToken) {
      config.headers['Authorization'] = `Bearer ${authToken}`
    }

    return config
  })

  // Response interceptor - handle errors
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      // Check if offline FIRST
      if (!navigator.onLine) {
        return Promise.reject({
          response: {
            status: 0,
            data: {
              detail: 'You are offline. Please check your internet connection.',
              type: 'network/offline'
            }
          }
        })
      }

      // Specific error type detection
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        return Promise.reject({
          response: {
            status: 408,
            data: {
              detail: 'Request timed out. The server took too long to respond.',
              type: 'network/timeout'
            }
          }
        })
      }

      if (!error.response) {
        // Network error (DNS, connection refused, etc.)
        return Promise.reject({
          response: {
            status: 0,
            data: {
              detail: 'Unable to connect to server. Please check your internet connection.',
              type: 'network/error'
            }
          }
        })
      }

      // For 401 errors, the app should redirect to login
      // This will be handled by component logic
      return Promise.reject(error)
    }
  )

  return client
}

const httpClient = createHttpClient()

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
          ...headers
        }
      }

      // Only set Content-Type for JSON if not FormData
      // FormData must set Content-Type automatically with boundary
      if (!(data instanceof FormData)) {
        config.headers['Content-Type'] = 'application/json'
      }

      if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        config.data = data
      }

      const response = await httpClient(config)
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

  const patch = (endpoint, data, headers = {}) =>
    request(endpoint, { method: 'PATCH', data, headers })

  const del = (endpoint, headers = {}) =>
    request(endpoint, { method: 'DELETE', headers })

  // Raw axios access for advanced usage
  const rawRequest = async (config) => {
    return await execute(async () => {
      const response = await httpClient(config)
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
    patch,
    del,

    // Advanced usage
    rawRequest
  }
}