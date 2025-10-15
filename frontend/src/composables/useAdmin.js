/**
 * Admin panel composable for domain event-to-group management.
 * 
 * Provides specialized functions for admin operations following
 * the functional programming principles from CLAUDE.md.
 */

import { ref, computed } from 'vue'
import { useHTTP } from './useHTTP'
import { API_ENDPOINTS } from '@/constants/api'
import i18n from '@/i18n'

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
      const result = await get(API_ENDPOINTS.DOMAIN_GROUPS(domain))
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
    // Validation
    if (!name || !name.trim()) {
      return { success: false, error: 'Group name cannot be empty' }
    }
    
    if (groups.value.some(g => g.name.toLowerCase() === name.trim().toLowerCase())) {
      return { success: false, error: 'Group name already exists' }
    }
    
    try {
      const result = await post(API_ENDPOINTS.DOMAIN_GROUPS(domain), { name: name.trim() })
      await loadGroups() // Refresh groups list
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to create group:', err)
      return { success: false, error: err.message }
    }
  }

  const updateGroup = async (groupId, name) => {
    // Validation
    if (!name || !name.trim()) {
      return { success: false, error: 'Group name cannot be empty' }
    }
    
    if (groups.value.some(g => g.id !== groupId && g.name.toLowerCase() === name.trim().toLowerCase())) {
      return { success: false, error: 'Group name already exists' }
    }
    
    try {
      const result = await put(API_ENDPOINTS.DOMAIN_GROUP(domain, groupId), { name: name.trim() })
      await loadGroups() // Refresh groups list
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to update group:', err)
      return { success: false, error: err.message }
    }
  }

  const deleteGroup = async (groupId) => {
    try {
      await del(API_ENDPOINTS.DOMAIN_GROUP(domain, groupId))
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
      const result = await get(API_ENDPOINTS.DOMAIN_RECURRING_EVENTS(domain))
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
      const result = await get(API_ENDPOINTS.DOMAIN_RECURRING_EVENTS_WITH_ASSIGNMENTS(domain))
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
      const result = await put(API_ENDPOINTS.DOMAIN_ASSIGN_RECURRING_EVENTS(domain, groupId), {
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
      const result = await put(API_ENDPOINTS.DOMAIN_BULK_ASSIGN_EVENTS(domain), {
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
      const result = await put(API_ENDPOINTS.DOMAIN_BULK_UNASSIGN_EVENTS(domain), {
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
    const result = await put(API_ENDPOINTS.DOMAIN_REMOVE_EVENTS_FROM_GROUP(domain, groupId), {
      recurring_event_titles: Array.isArray(eventTitles) ? eventTitles : [eventTitles]
    })
    
    if (result.success) {
      // Refresh events after removal
      await loadRecurringEventsWithAssignments()
      return { success: true, data: result.data }
    } else {
      console.error('Failed to remove events from group:', result.error)
      return { success: false, error: result.error }
    }
  }

  const unassignEventFromGroup = async (eventTitle) => {
    try {
      const result = await put(API_ENDPOINTS.DOMAIN_UNASSIGN_EVENT(domain), {
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
      const result = await get(API_ENDPOINTS.DOMAIN_ASSIGNMENT_RULES(domain))
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
      const result = await post(API_ENDPOINTS.DOMAIN_ASSIGNMENT_RULES(domain), {
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

  const createCompoundRule = async (operator, conditions, targetGroupId) => {
    try {
      const result = await post(API_ENDPOINTS.DOMAIN_ASSIGNMENT_RULES_COMPOUND(domain), {
        operator: operator,
        conditions: conditions,
        target_group_id: parseInt(targetGroupId)
      })
      await loadAssignmentRules() // Refresh rules list
      return { success: true, data: result }
    } catch (err) {
      console.error('Failed to create compound rule:', err)
      return { success: false, error: err.message }
    }
  }

  const deleteAssignmentRule = async (ruleId) => {
    try {
      await del(API_ENDPOINTS.DOMAIN_ASSIGNMENT_RULE(domain, ruleId))
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
        // Use enhanced backend data: sample_description
        const description = event.sample_description || ''
        return description.toLowerCase().includes(searchValue)
      
      case 'category_contains':
        // Use enhanced backend data: sample_categories
        const categories = event.sample_categories || []
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
        getGroupName(event.assigned_group_id) : i18n.global.t('admin.unassigned'),
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
    // Use backend's "apply all rules" endpoint
    // This works for both simple and compound rules
    try {
      console.log('[Apply Rules] Sending request to:', API_ENDPOINTS.DOMAIN_ASSIGNMENT_RULES_APPLY(domain))
      console.log('[Apply Rules] Auth token present:', !!localStorage.getItem('auth_token'))

      const result = await post(API_ENDPOINTS.DOMAIN_ASSIGNMENT_RULES_APPLY(domain))

      console.log('[Apply Rules] Success:', result)
      await loadRecurringEventsWithAssignments() // Refresh to show changes
      return {
        success: true,
        message: result.message || 'Rules applied successfully',
        assignedCount: result.assignment_count || 0
      }
    } catch (err) {
      console.error('[Apply Rules] Error:', err)
      console.error('[Apply Rules] Error response:', err.response?.data)
      console.error('[Apply Rules] Error status:', err.response?.status)

      // Provide more detailed error message
      const errorDetail = err.response?.data?.detail || err.message || 'Unknown error'
      return { success: false, error: `Apply failed: ${errorDetail}` }
    }
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
    createCompoundRule,
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