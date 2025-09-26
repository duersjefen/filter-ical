/**
 * Admin panel composable for domain event-to-group management.
 * 
 * Provides specialized functions for admin operations following
 * the functional programming principles from CLAUDE.md.
 */

import { ref, computed } from 'vue'
import { useHTTP } from './useHTTP'

export function useAdmin(domain) {
  const { get, post, put, del } = useHTTP()

  // Reactive state  
  const groups = ref([])
  const recurringEvents = ref([])
  const assignmentRules = ref([])
  
  // Admin-specific loading and error states
  const loading = ref(false)
  const error = ref(null)

  // Computed properties
  const groupsMap = computed(() => {
    const map = {}
    // Defensive programming: ensure groups.value is always an array
    const groupsArray = Array.isArray(groups.value) ? groups.value : []
    groupsArray.forEach(group => {
      map[group.id] = group
    })
    return map
  })

  const availableEvents = computed(() => {
    // Defensive programming: ensure recurringEvents.value is always an array
    const eventsArray = Array.isArray(recurringEvents.value) ? recurringEvents.value : []
    return eventsArray.filter(event => event.event_count > 0)
  })

  // Request tracking to prevent simultaneous calls
  let loadingStates = {
    groups: false,
    events: false,
    rules: false
  }

  // API Functions - Groups Management
  const loadGroups = async () => {
    if (loadingStates.groups) {
      return { success: true, data: groups.value }
    }
    
    loadingStates.groups = true
    try {
      const result = await get(`/domains/${domain}/groups`)
      // Extract the array data from the HTTP response
      const groupsData = result.success ? (result.data || []) : []
      groups.value = Array.isArray(groupsData) ? groupsData : []
      return { success: true, data: groupsData }
    } catch (err) {
      console.error('Failed to load groups:', err)
      groups.value = []
      return { success: false, error: err.message }
    } finally {
      loadingStates.groups = false
    }
  }

  const createGroup = async (name) => {
    try {
      const result = await post(`/domains/${domain}/groups`, { name: name.trim() })
      await loadGroups() // Refresh groups list
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to create group:', err)
      return { success: false, error: err.message }
    }
  }

  const updateGroup = async (groupId, name) => {
    try {
      const result = await put(`/domains/${domain}/groups/${groupId}`, { name: name.trim() })
      await loadGroups() // Refresh groups list
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to update group:', err)
      return { success: false, error: err.message }
    }
  }

  const deleteGroup = async (groupId) => {
    try {
      await del(`/domains/${domain}/groups/${groupId}`)
      await loadGroups() // Refresh groups list
      return { success: true }
    } catch (err) {
      console.error('Failed to delete group:', err)
      return { success: false, error: err.message }
    }
  }

  // API Functions - Recurring Events
  const loadRecurringEvents = async () => {
    try {
      const result = await get(`/domains/${domain}/recurring-events`)
      // Extract the array data from the HTTP response
      const eventsData = result.success ? (result.data || []) : []
      recurringEvents.value = Array.isArray(eventsData) ? eventsData : []
      return { success: true, data: eventsData }
    } catch (err) {
      console.error('Failed to load recurring events:', err)
      recurringEvents.value = []
      return { success: false, error: err.message }
    }
  }

  const loadRecurringEventsWithAssignments = async () => {
    if (loadingStates.events) {
      return { success: true, data: recurringEvents.value }
    }
    
    loadingStates.events = true
    try {
      const result = await get(`/domains/${domain}/recurring-events-with-assignments`)
      // Extract the array data from the HTTP response
      const eventsData = result.success ? (result.data?.data || []) : []
      recurringEvents.value = Array.isArray(eventsData) ? eventsData : []
      return { success: true, data: eventsData }
    } catch (err) {
      console.error('Failed to load recurring events with assignments:', err)
      recurringEvents.value = []
      return { success: false, error: err.message }
    } finally {
      loadingStates.events = false
    }
  }

  const assignEventsToGroup = async (groupId, eventTitles) => {
    try {
      const result = await put(`/domains/${domain}/groups/${groupId}/assign-recurring-events`, {
        recurring_event_titles: Array.isArray(eventTitles) ? eventTitles : [eventTitles]
      })
      // Refresh both groups and events after assignment
      await Promise.all([loadGroups(), loadRecurringEventsWithAssignments()])
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to assign events to group:', err)
      return { success: false, error: err.message }
    }
  }

  const bulkAssignEventsToGroup = async (groupId, eventTitles) => {
    try {
      const result = await put(`/domains/${domain}/bulk-assign-events`, {
        group_id: groupId,
        recurring_event_titles: eventTitles
      })
      // Refresh events after bulk assignment
      await loadRecurringEventsWithAssignments()
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to bulk assign events:', err)
      return { success: false, error: err.message }
    }
  }

  const bulkUnassignEvents = async (eventTitles) => {
    try {
      const result = await put(`/domains/${domain}/bulk-unassign-events`, {
        recurring_event_titles: eventTitles
      })
      // Refresh events after bulk unassignment
      await loadRecurringEventsWithAssignments()
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to bulk unassign events:', err)
      return { success: false, error: err.message }
    }
  }

  const unassignEventFromGroup = async (eventTitle) => {
    try {
      const result = await put(`/domains/${domain}/unassign-event`, {
        recurring_event_title: eventTitle
      })
      // Refresh events after unassignment
      await loadRecurringEventsWithAssignments()
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to unassign event:', err)
      return { success: false, error: err.message }
    }
  }

  // API Functions - Assignment Rules
  const loadAssignmentRules = async () => {
    if (loadingStates.rules) {
      return { success: true, data: assignmentRules.value }
    }
    
    loadingStates.rules = true
    try {
      const result = await get(`/domains/${domain}/assignment-rules`)
      // Extract the array data from the HTTP response
      const rulesData = result.success ? (result.data || []) : []
      assignmentRules.value = Array.isArray(rulesData) ? rulesData : []
      return { success: true, data: rulesData }
    } catch (err) {
      console.error('Failed to load assignment rules:', err)
      assignmentRules.value = []
      return { success: false, error: err.message }
    } finally {
      loadingStates.rules = false
    }
  }

  const createAssignmentRule = async (ruleType, ruleValue, targetGroupId) => {
    try {
      const result = await post(`/domains/${domain}/assignment-rules`, {
        rule_type: ruleType,
        rule_value: ruleValue.trim(),
        target_group_id: parseInt(targetGroupId)
      })
      await loadAssignmentRules() // Refresh rules list
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to create assignment rule:', err)
      return { success: false, error: err.message }
    }
  }

  const deleteAssignmentRule = async (ruleId) => {
    try {
      await del(`/domains/${domain}/assignment-rules/${ruleId}`)
      await loadAssignmentRules() // Refresh rules list
      return { success: true }
    } catch (err) {
      console.error('Failed to delete assignment rule:', err)
      return { success: false, error: err.message }
    }
  }

  // Utility Functions
  const getGroupName = (groupId) => {
    const group = groupsMap.value[groupId]
    return group ? group.name : `Group ${groupId}`
  }

  const getRuleTypeLabel = (ruleType) => {
    const labels = {
      title_contains: 'Title contains',
      description_contains: 'Description contains',
      category_contains: 'Category contains'
    }
    return labels[ruleType] || ruleType
  }

  // Request deduplication to prevent infinite loops
  let loadAllDataPromise = null
  
  // Bulk Operations
  const loadAllAdminData = async () => {
    // If a request is already in progress, return the same promise
    if (loadAllDataPromise) {
      return loadAllDataPromise
    }
    
    loadAllDataPromise = (async () => {
      try {
        loading.value = true
        error.value = null
        
        const results = await Promise.all([
          loadGroups(),
          loadRecurringEventsWithAssignments(),
          loadAssignmentRules()
        ])
        
        const allSuccess = results.every(r => r.success)
        if (!allSuccess) {
          const failedResults = results.filter(r => !r.success)
          error.value = `Failed to load: ${failedResults.map(r => r.error).join(', ')}`
        }
        
        return {
          success: allSuccess,
          results
        }
      } catch (err) {
        error.value = err.message || 'Failed to load admin data'
        return {
          success: false,
          error: error.value
        }
      } finally {
        loading.value = false
        // Clear the promise after completion
        loadAllDataPromise = null
      }
    })()
    
    return loadAllDataPromise
  }

  // Statistics and computed values
  const getEventStatistics = () => {
    const events = recurringEvents.value || []
    const total = events.length
    const assigned = events.filter(event => event.assigned_group_id).length
    const unassigned = total - assigned
    
    return {
      total,
      assigned,
      unassigned
    }
  }

  // Validation Functions (Pure Functions)
  const validateGroupName = (name) => {
    if (!name || typeof name !== 'string' || !name.trim()) {
      return { valid: false, error: 'Group name is required' }
    }
    
    if (name.trim().length > 255) {
      return { valid: false, error: 'Group name must be 255 characters or less' }
    }
    
    return { valid: true }
  }

  const validateAssignmentRule = (ruleType, ruleValue, targetGroupId) => {
    const validRuleTypes = ['title_contains', 'description_contains', 'category_contains']
    
    if (!validRuleTypes.includes(ruleType)) {
      return { valid: false, error: `Rule type must be one of: ${validRuleTypes.join(', ')}` }
    }
    
    if (!ruleValue || typeof ruleValue !== 'string' || !ruleValue.trim()) {
      return { valid: false, error: 'Rule value is required' }
    }
    
    if (!targetGroupId || isNaN(parseInt(targetGroupId)) || parseInt(targetGroupId) <= 0) {
      return { valid: false, error: 'Valid target group must be selected' }
    }
    
    return { valid: true }
  }

  return {
    // State
    groups,
    recurringEvents,
    assignmentRules,
    loading,
    error,

    // Computed
    groupsMap,
    availableEvents,

    // Groups API
    loadGroups,
    createGroup,
    updateGroup,
    deleteGroup,

    // Events API
    loadRecurringEvents,
    loadRecurringEventsWithAssignments,
    assignEventsToGroup,
    bulkAssignEventsToGroup,
    bulkUnassignEvents,
    unassignEventFromGroup,

    // Rules API
    loadAssignmentRules,
    createAssignmentRule,
    deleteAssignmentRule,

    // Utilities
    getGroupName,
    getRuleTypeLabel,
    loadAllAdminData,
    getEventStatistics,
    validateGroupName,
    validateAssignmentRule
  }
}