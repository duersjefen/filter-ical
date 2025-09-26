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

  const addEventsToGroup = async (groupId, eventTitles) => {
    try {
      const newEventTitles = Array.isArray(eventTitles) ? eventTitles : [eventTitles]
      
      // Make sure we have the latest events data
      await loadRecurringEventsWithAssignments()
      
      // Get current events assigned to this group
      const currentEvents = recurringEvents.value.filter(event => 
        event.assigned_group_ids && event.assigned_group_ids.includes(parseInt(groupId))
      ).map(event => event.title)
      
      // Merge new events with existing ones (avoiding duplicates)
      const allEvents = [...new Set([...currentEvents, ...newEventTitles])]
      
      // Use existing assignEventsToGroup with complete list
      const result = await assignEventsToGroup(groupId, allEvents)
      
      return result
    } catch (err) {
      console.error('Failed to add events to group:', err)
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

  const removeEventsFromGroup = async (groupId, eventTitles) => {
    try {
      // Since the backend doesn't have "remove from specific group" yet,
      // we'll implement this using the existing assign functionality
      // by reassigning events to their other groups (excluding the target group)
      
      // First, get current assignments for these events
      await loadRecurringEventsWithAssignments()
      
      const updatedAssignments = []
      
      eventTitles.forEach(eventTitle => {
        const event = recurringEvents.value.find(e => e.title === eventTitle)
        if (event && event.assigned_group_ids) {
          // Remove the target group from the event's group assignments
          const remainingGroupIds = event.assigned_group_ids.filter(id => id !== parseInt(groupId))
          
          if (remainingGroupIds.length > 0) {
            // Event still has other groups, reassign to first remaining group
            updatedAssignments.push({
              eventTitle: eventTitle,
              targetGroupId: remainingGroupIds[0],
              allGroupIds: remainingGroupIds
            })
          } else {
            // Event has no other groups, unassign completely
            updatedAssignments.push({
              eventTitle: eventTitle,
              targetGroupId: null,
              allGroupIds: []
            })
          }
        }
      })

      // Process the assignments
      const results = []
      for (const assignment of updatedAssignments) {
        if (assignment.targetGroupId === null) {
          // Unassign completely
          const result = await unassignEventFromGroup(assignment.eventTitle)
          results.push(result)
        } else {
          // For now, we can only assign to one group at a time with current backend
          // This is a limitation - we need a proper "remove from specific group" API
          const result = await assignEventsToGroup(assignment.targetGroupId, [assignment.eventTitle])
          results.push(result)
        }
      }

      // Check if all operations succeeded
      const allSucceeded = results.every(result => result.success)
      
      if (allSucceeded) {
        return { success: true, data: { removedCount: eventTitles.length } }
      } else {
        const errors = results.filter(r => !r.success).map(r => r.error)
        return { success: false, error: `Some operations failed: ${errors.join(', ')}` }
      }
      
    } catch (err) {
      console.error('Failed to remove events from group:', err)
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

  // Preview and Apply Functions (Pure client-side logic)
  const eventMatchesRule = (event, ruleType, ruleValue) => {
    const searchValue = ruleValue.toLowerCase().trim()
    
    switch (ruleType) {
      case 'title_contains':
        return event.title?.toLowerCase().includes(searchValue) || false
      
      case 'description_contains':
        return event.description?.toLowerCase().includes(searchValue) || false
      
      case 'category_contains':
        // For now, we'll check if categories exist in event data
        // This could be enhanced if we have category data available
        const categories = event.categories || []
        return Array.isArray(categories) && 
               categories.some(cat => cat.toLowerCase().includes(searchValue))
      
      default:
        return false
    }
  }

  const previewAssignmentRule = (ruleType, ruleValue, targetGroupId) => {
    // Validate inputs first
    const validation = validateAssignmentRule(ruleType, ruleValue, targetGroupId)
    if (!validation.valid) {
      return {
        success: false,
        error: validation.error,
        affectedEvents: [],
        summary: { total: 0, willChange: 0, noChange: 0 }
      }
    }

    const events = Array.isArray(recurringEvents.value) ? recurringEvents.value : []
    const targetGroup = groupsMap.value[parseInt(targetGroupId)]
    
    if (!targetGroup) {
      return {
        success: false,
        error: 'Target group not found',
        affectedEvents: [],
        summary: { total: 0, willChange: 0, noChange: 0 }
      }
    }

    // Find events that match the rule
    const affectedEvents = events.filter(event => 
      eventMatchesRule(event, ruleType, ruleValue)
    ).map(event => ({
      ...event,
      currentGroupName: event.assigned_group_id ? 
        getGroupName(event.assigned_group_id) : 'Unassigned',
      willChange: event.assigned_group_id !== parseInt(targetGroupId)
    }))

    const summary = {
      total: affectedEvents.length,
      willChange: affectedEvents.filter(e => e.willChange).length,
      noChange: affectedEvents.filter(e => !e.willChange).length
    }

    return {
      success: true,
      affectedEvents,
      summary,
      targetGroupName: targetGroup.name
    }
  }

  const previewExistingRule = (rule) => {
    return previewAssignmentRule(rule.rule_type, rule.rule_value, rule.target_group_id)
  }

  const applyAssignmentRule = async (ruleType, ruleValue, targetGroupId) => {
    // First get the preview to see what events would be affected
    const preview = previewAssignmentRule(ruleType, ruleValue, targetGroupId)
    
    if (!preview.success) {
      return { success: false, error: preview.error }
    }

    // Filter to only events that will actually change
    const eventsToAssign = preview.affectedEvents
      .filter(event => event.willChange)
      .map(event => event.title)

    if (eventsToAssign.length === 0) {
      return { 
        success: true, 
        message: 'No events need to be reassigned - all matching events are already in the target group',
        assignedCount: 0
      }
    }

    // Use smart frontend approach via addEventsToGroup
    try {
      const result = await addEventsToGroup(parseInt(targetGroupId), eventsToAssign)
      
      if (result.success) {
        return {
          success: true,
          message: `${eventsToAssign.length} events added to ${preview.targetGroupName}`,
          assignedCount: eventsToAssign.length
        }
      } else {
        return { success: false, error: result.error || 'Failed to add events' }
      }
    } catch (error) {
      return { success: false, error: `Failed to apply rule: ${error.message}` }
    }
  }

  const applyExistingRule = async (rule) => {
    return await applyAssignmentRule(rule.rule_type, rule.rule_value, rule.target_group_id)
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
    addEventsToGroup,
    bulkAssignEventsToGroup,
    bulkUnassignEvents,
    unassignEventFromGroup,
    removeEventsFromGroup,

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
    validateAssignmentRule,

    // Preview and Apply Functions
    previewAssignmentRule,
    previewExistingRule,
    applyAssignmentRule,
    applyExistingRule
  }
}