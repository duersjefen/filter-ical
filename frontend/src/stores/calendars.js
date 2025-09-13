/**
 * Calendar Store - Focused on calendar CRUD operations
 * Uses composable for clean error handling
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { useAPI } from '../composables/useAPI'

export const useCalendarStore = defineStore('calendars', () => {
  // State
  const calendars = ref([])
  const selectedCalendar = ref(null)
  const newCalendar = ref({
    name: '',
    url: ''
  })

  // API composable for error handling
  const api = useAPI()

  // User authentication helpers
  const getUserHeaders = () => {
    // This should be imported from a shared auth composable in the future
    return {
      'x-user-id': 'anonymous' // TODO: Implement proper user management
    }
  }

  // Actions
  const fetchCalendars = async () => {
    const result = await api.safeExecute(async () => {
      const response = await axios.get('/api/calendars', {
        headers: getUserHeaders()
      })
      return response.data.calendars
    })

    if (result.success) {
      calendars.value = result.data
    }
    
    return result
  }

  const addCalendar = async () => {
    if (!newCalendar.value.name.trim() || !newCalendar.value.url.trim()) {
      api.error.value = 'Please provide both calendar name and URL'
      return { success: false, error: api.error.value }
    }

    const result = await api.safeExecute(async () => {
      const response = await axios.post('/api/calendars', {
        name: newCalendar.value.name,
        url: newCalendar.value.url
      }, {
        headers: getUserHeaders()
      })
      return response.data
    })

    if (result.success) {
      // Refresh calendars list
      await fetchCalendars()
      
      // Reset form
      newCalendar.value = {
        name: '',
        url: ''
      }
    }

    return result
  }

  const deleteCalendar = async (calendarId) => {
    const result = await api.safeExecute(async () => {
      await axios.delete(`/api/calendars/${calendarId}`, {
        headers: getUserHeaders()
      })
    })

    if (result.success) {
      // Refresh calendars list
      await fetchCalendars()
    }

    return result
  }

  const selectCalendar = (calendar) => {
    selectedCalendar.value = calendar
  }

  const clearSelection = () => {
    selectedCalendar.value = null
  }

  return {
    // State
    calendars,
    selectedCalendar,
    newCalendar,
    
    // Loading and error from composable
    loading: api.loading,
    error: api.error,
    
    // Actions  
    fetchCalendars,
    addCalendar,
    deleteCalendar,
    selectCalendar,
    clearSelection
  }
})