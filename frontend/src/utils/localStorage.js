/**
 * LocalStorage utilities with user isolation
 * Pure functions for managing user-specific data persistence
 */

/**
 * Generate storage key with user isolation
 */
export function getFilterStorageKey(calendarId, userId) {
  return calendarId ? `icalViewer_filters_${calendarId}_${userId}` : `icalViewer_filters_default_${userId}`
}

/**
 * Save filters to localStorage with error handling
 */
export function saveFiltersData(storageKey, filtersData) {
  try {
    const dataWithTimestamp = {
      ...filtersData,
      savedAt: new Date().toISOString()
    }
    localStorage.setItem(storageKey, JSON.stringify(dataWithTimestamp))
    return { success: true }
  } catch (error) {
    return { success: false, error }
  }
}

/**
 * Load and validate filters from localStorage
 */
export function loadFiltersData(storageKey) {
  try {
    const saved = localStorage.getItem(storageKey)
    if (!saved) return { success: false, data: null }
    
    const filtersData = JSON.parse(saved)
    
    // Validate data structure
    if (!filtersData || typeof filtersData !== 'object') {
      return { success: false, data: null }
    }
    
    // Validate individual fields with defaults
    const validatedData = {
      selectedRecurringEvents: Array.isArray(filtersData.selectedRecurringEvents) ? filtersData.selectedRecurringEvents : [],
      recurringEventSearch: typeof filtersData.recurringEventSearch === 'string' ? filtersData.recurringEventSearch : '',
      showSingleEvents: typeof filtersData.showSingleEvents === 'boolean' ? filtersData.showSingleEvents : false,
      showSelectedOnly: typeof filtersData.showSelectedOnly === 'boolean' ? filtersData.showSelectedOnly : false,
      savedAt: filtersData.savedAt
    }
    
    return { success: true, data: validatedData }
  } catch (error) {
    return { success: false, error }
  }
}