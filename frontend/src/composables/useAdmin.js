/**
 * Admin panel composable for domain event-to-group management.
 * 
 * Provides specialized functions for admin operations following
 * the functional programming principles from CLAUDE.md.
 */

import { ref, computed } from 'vue'
import { useHTTP } from './useHTTP'

export function useAdmin(domain) {
  const { get, post, put, del, loading, error } = useHTTP()

  // Reactive state
  const groups = ref([])
  const recurringEvents = ref([])
  const assignmentRules = ref([])

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

  // API Functions - Groups Management
  const loadGroups = async () => {
    try {
      const result = await get(`/domains/${domain}/groups`)
      groups.value = result.success ? (result.data || []) : []
      return { success: true, data: result.data }
    } catch (err) {
      console.error('Failed to load groups:', err)
      return { success: false, error: err.message }
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
      recurringEvents.value = result.success ? (result.data || []) : []
      return { success: true, data: result.data }
    } catch (err) {
      console.error('Failed to load recurring events:', err)
      return { success: false, error: err.message }
    }
  }

  const loadRecurringEventsWithAssignments = async () => {
    try {
      const result = await get(`/domains/${domain}/recurring-events-with-assignments`)
      recurringEvents.value = result.success ? (result.data || []) : []
      return { success: true, data: result.data }
    } catch (err) {
      console.error('Failed to load recurring events with assignments:', err)
      return { success: false, error: err.message }
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
    try {
      const result = await get(`/domains/${domain}/assignment-rules`)
      assignmentRules.value = result.success ? (result.data || []) : []
      return { success: true, data: result.data }
    } catch (err) {
      console.error('Failed to load assignment rules:', err)
      return { success: false, error: err.message }
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

  // Bulk Operations
  const loadAllAdminData = async () => {
    const results = await Promise.all([
      loadGroups(),
      loadRecurringEventsWithAssignments(),
      loadAssignmentRules()
    ])
    
    return {
      success: results.every(r => r.success),
      results
    }
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