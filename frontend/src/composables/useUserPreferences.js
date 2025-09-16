/**
 * Composable for User Preferences Management
 * Handles saving and loading user preferences including filter state
 */

import { ref } from 'vue'
import axios from 'axios'
import { useAppStore } from '../stores/app'

export function useUserPreferences() {
  const appStore = useAppStore()
  const loading = ref(false)
  const error = ref(null)

  // Get user authentication headers
  const getUserHeaders = () => appStore.getUserHeaders()

  /**
   * Load user preferences from backend
   */
  const loadUserPreferences = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get('/api/user/preferences', {
        headers: getUserHeaders()
      })
      
      if (response.data && response.data.success) {
        return response.data.preferences
      }
      return {}
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load user preferences'
      console.error('Error loading user preferences:', err)
      return {}
    } finally {
      loading.value = false
    }
  }

  /**
   * Save user preferences to backend
   */
  const saveUserPreferences = async (preferences) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.put('/api/user/preferences', preferences, {
        headers: getUserHeaders()
      })
      
      return response.data && response.data.success
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to save user preferences'
      console.error('Error saving user preferences:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Save filter state for a specific calendar using calendar-specific endpoint
   */
  const saveCalendarFilterState = async (calendarId, filterState) => {
    loading.value = true
    error.value = null
    
    try {
      const preferencesData = {
        selected_categories: filterState.selectedCategories || [],
        filter_mode: filterState.filterMode || 'include',
        expanded_categories: filterState.expandedCategories || [],
        show_single_events: filterState.showSingleEvents || false,
        show_categories_section: filterState.showCategoriesSection !== undefined ? filterState.showCategoriesSection : true,
        show_selected_only: filterState.showSelectedOnly || false,
        category_search: filterState.categorySearch || '',
        preview_group: filterState.previewGroup || 'none',
        saved_at: new Date().toISOString()
      }
      
      const response = await axios.put(`/api/calendars/${calendarId}/preferences`, preferencesData, {
        headers: getUserHeaders()
      })
      
      return response.data && response.data.success
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to save calendar filter state'
      console.error('Error saving calendar filter state:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Load filter state for a specific calendar using calendar-specific endpoint
   */
  const loadCalendarFilterState = async (calendarId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get(`/api/calendars/${calendarId}/preferences`, {
        headers: getUserHeaders()
      })
      
      if (response.data && response.data.success && response.data.preferences) {
        const prefs = response.data.preferences
        return {
          selectedCategories: prefs.selected_categories || [],
          filterMode: prefs.filter_mode || 'include',
          expandedCategories: prefs.expanded_categories || [],
          showSingleEvents: prefs.show_single_events || false,
          showCategoriesSection: prefs.show_categories_section !== undefined ? prefs.show_categories_section : true,
          showSelectedOnly: prefs.show_selected_only || false,
          categorySearch: prefs.category_search || '',
          previewGroup: prefs.preview_group || 'none'
        }
      }
      
      // Return default filter state if none saved
      return {
        selectedCategories: [],
        filterMode: 'include',
        expandedCategories: [],
        showSingleEvents: false,
        showCategoriesSection: true,
        showSelectedOnly: false,
        categorySearch: '',
        previewGroup: 'none'
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load calendar filter state'
      console.error('Error loading calendar filter state:', err)
      
      // Return default filter state on error
      return {
        selectedCategories: [],
        filterMode: 'include',
        expandedCategories: [],
        showSingleEvents: false,
        showCategoriesSection: true,
        showSelectedOnly: false,
        categorySearch: '',
        previewGroup: 'none'
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear filter state for a specific calendar
   */
  const clearCalendarFilterState = async (calendarId) => {
    // Save empty preferences to reset the calendar filter state
    return await saveCalendarFilterState(calendarId, {})
  }

  return {
    loading,
    error,
    loadUserPreferences,
    saveUserPreferences,
    saveCalendarFilterState,
    loadCalendarFilterState,
    clearCalendarFilterState
  }
}