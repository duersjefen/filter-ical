/**
 * Functional Calendar Store - Rich Hickey Style for Vue 3
 * Demonstrates "Functional Core, Imperative Shell" pattern in frontend
 * 
 * ARCHITECTURE:
 * - Pure functions handle all data transformations
 * - Store only manages I/O and state updates
 * - Clear separation between business logic and side effects
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAPI } from '../composables/useAPI'
import {
  // Pure validation functions
  validateCalendarData,
  normalizeCalendarData,
  // Pure transformation functions
  calendarToDisplayFormat,
  sortCalendarsByName,
  filterCalendars,
  // Pure form functions
  createEmptyCalendar,
  resetCalendarForm,
  // Pure API helpers
  transformApiError,
  createApiHeaders,
  // Pure state functions
  updateCalendarInList,
  removeCalendarFromList,
  addCalendarToList
} from '../composables/useCalendarData'

export const useCalendarStoreFunctional = defineStore('calendars-functional', () => {
  // === STATE (Imperative Shell) ===
  const calendarsRaw = ref([])
  const selectedCalendarId = ref(null)
  const newCalendar = ref(createEmptyCalendar())
  const searchTerm = ref('')
  const currentUserId = ref('anonymous')

  // API composable for I/O operations
  const api = useAPI()

  // === COMPUTED STATE (Pure Transformations) ===
  
  const calendars = computed(() => {
    // Pure function chain: raw data -> display format -> sort -> filter
    const displayCalendars = calendarsRaw.value.map(calendarToDisplayFormat)
    const sortedCalendars = sortCalendarsByName(displayCalendars)
    return filterCalendars(sortedCalendars, searchTerm.value)
  })

  const selectedCalendar = computed(() => {
    return calendars.value.find(cal => cal.id === selectedCalendarId.value) || null
  })

  const formValidation = computed(() => {
    return validateCalendarData(newCalendar.value)
  })

  const canSubmitForm = computed(() => {
    return formValidation.value.isValid && !api.loading.value
  })

  // === ACTIONS (Imperative Shell) ===

  /**
   * Fetch calendars from API - I/O operation
   */
  const fetchCalendars = async () => {
    const result = await api.safeExecute(async () => {
      const headers = createApiHeaders(currentUserId.value)
      const response = await axios.get('/api/calendars', { headers })
      return response.data.calendars
    })

    if (result.success) {
      // Pure function: replace state with new data
      calendarsRaw.value = result.data
    }
    
    return result
  }

  /**
   * Add calendar - combines validation + I/O + state update
   */
  const addCalendar = async () => {
    // Pure function: validate form data
    const validation = validateCalendarData(newCalendar.value)
    if (!validation.isValid) {
      api.error.value = validation.errors.join(', ')
      return { success: false, error: api.error.value }
    }

    // Pure function: normalize data for API
    const normalizedData = normalizeCalendarData(newCalendar.value)

    // I/O operation: send to server
    const result = await api.safeExecute(async () => {
      const headers = createApiHeaders(currentUserId.value)
      const response = await axios.post('/api/calendars', normalizedData, { headers })
      return response.data
    })

    if (result.success) {
      // Pure functions: update state immutably
      calendarsRaw.value = addCalendarToList(calendarsRaw.value, result.data)
      newCalendar.value = resetCalendarForm(newCalendar.value)
    }

    return result
  }

  /**
   * Delete calendar - I/O operation + state update
   */
  const deleteCalendar = async (calendarId) => {
    const result = await api.safeExecute(async () => {
      const headers = createApiHeaders(currentUserId.value)
      await axios.delete(`/api/calendars/${calendarId}`, { headers })
    })

    if (result.success) {
      // Pure function: remove from state immutably
      calendarsRaw.value = removeCalendarFromList(calendarsRaw.value, calendarId)
      
      // Clear selection if deleted calendar was selected
      if (selectedCalendarId.value === calendarId) {
        selectedCalendarId.value = null
      }
    }

    return result
  }

  /**
   * Select calendar - pure state update
   */
  const selectCalendar = (calendar) => {
    selectedCalendarId.value = calendar?.id || null
  }

  /**
   * Clear selection - pure state update
   */
  const clearSelection = () => {
    selectedCalendarId.value = null
  }

  /**
   * Update search term - pure state update
   */
  const updateSearchTerm = (term) => {
    searchTerm.value = term
  }

  /**
   * Reset form - pure state update
   */
  const resetForm = () => {
    newCalendar.value = resetCalendarForm(newCalendar.value)
    api.error.value = null
  }

  /**
   * Set user ID - pure state update
   */
  const setUserId = (userId) => {
    currentUserId.value = userId
  }

  // === ERROR HANDLING (Pure Transformation) ===
  
  const friendlyError = computed(() => {
    if (!api.error.value) return null
    
    // This could use transformApiError for more sophisticated error handling
    return api.error.value
  })

  // === RETURN INTERFACE ===
  
  return {
    // State (computed with pure transformations)
    calendars,
    selectedCalendar,
    newCalendar,
    searchTerm,
    
    // Derived state
    formValidation,
    canSubmitForm,
    
    // Loading and error states
    loading: api.loading,
    error: friendlyError,
    
    // Actions (imperative shell)
    fetchCalendars,
    addCalendar,
    deleteCalendar,
    selectCalendar,
    clearSelection,
    updateSearchTerm,
    resetForm,
    setUserId
  }
})

/**
 * FUNCTIONAL ARCHITECTURE BENEFITS DEMONSTRATED:
 * 
 * 1. TESTABILITY: All business logic is in pure functions
 *    - validateCalendarData() can be tested without Vue/Pinia
 *    - sortCalendarsByName() can be tested with simple arrays
 *    - No mocking of HTTP or store dependencies needed
 * 
 * 2. PREDICTABILITY: Same input always produces same output
 *    - calendarToDisplayFormat() always transforms data consistently
 *    - filterCalendars() never has side effects
 * 
 * 3. COMPOSABILITY: Functions can be combined in any order
 *    - Can easily chain: normalize -> validate -> transform
 *    - Functions work independently of store/component context
 * 
 * 4. DEBUGGING: Clear separation of concerns
 *    - Data transformation bugs are isolated to pure functions
 *    - I/O issues are isolated to store actions
 *    - Stack traces point directly to the problematic transformation
 * 
 * 5. MAINTENANCE: Changes have predictable, local effects
 *    - Adding validation rule only affects validateCalendarData()
 *    - Changing display format only affects calendarToDisplayFormat()
 *    - Business logic changes don't affect I/O operations
 */