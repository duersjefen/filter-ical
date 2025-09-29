/**
 * Unified Selection Composable
 * Single interface for all selection operations across the application
 * 
 * Replaces: useCalendar's selection logic, useEventSelection, useUnifiedSelection
 * Uses: selectionStore as single source of truth with app store integration
 */
import { useSelectionStore } from '../stores/selectionStore'
import { useAppStore } from '../stores/app'
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'

export function useSelection() {
  const selectionStore = useSelectionStore()
  const appStore = useAppStore()
  const { t } = useI18n()
  
  // Extract reactive refs properly from stores
  const {
    selectedRecurringEvents,
    subscribedGroups,
    expandedGroups,
    expandedRecurringEvents
  } = storeToRefs(selectionStore)

  // ===============================================
  // COMPUTED PROPERTIES WITH APP STORE INTEGRATION
  // ===============================================
  
  /**
   * Get all effectively selected recurring events
   * Integrates with app store's groups data
   */
  const effectiveSelectedRecurringEvents = computed(() => {
    const selected = [...selectedRecurringEvents.value]
    
    // Add recurring events from subscribed groups
    for (const groupId of subscribedGroups.value) {
      const group = appStore.groups[groupId]
      if (group && group.recurring_events) {
        for (const recurringEvent of group.recurring_events) {
          if (recurringEvent.event_count > 0 && !selected.includes(recurringEvent.title)) {
            selected.push(recurringEvent.title)
          }
        }
      }
    }
    
    return selected
  })
  
  /**
   * Get selection summary with app store integration
   */
  const selectionSummary = computed(() => {
    const summary = selectionStore.getSelectionSummary(appStore.groups || {})
    return {
      ...summary,
      compactText: selectionStore.getGroupBreakdownSummary(appStore.groups || {})
    }
  })
  
  /**
   * Get count of selected recurring events
   */
  const selectedCount = computed(() => selectedRecurringEvents.value.length)

  // ===============================================
  // WRAPPER FUNCTIONS WITH APP STORE CONTEXT
  // ===============================================
  
  const isRecurringEventEffectivelySelected = (recurringEventTitle) => {
    return selectionStore.isRecurringEventEffectivelySelected(recurringEventTitle, appStore.groups || {})
  }
  
  const allEventsSelected = () => {
    return selectionStore.allEventsSelected(appStore.groups || {})
  }
  
  const getSelectionSummaryData = () => {
    return selectionStore.getSelectionSummary(appStore.groups || {})
  }
  
  const getGroupBreakdownSummary = () => {
    // For personal calendars, we need to pass recurring events data too
    const groups = appStore.groups || {}
    const recurringEvents = appStore.recurringEvents || {}
    
    // Check if this is a personal calendar (no groups)
    const isPersonalCalendar = Object.keys(groups).length === 0
    
    if (isPersonalCalendar) {
      // For personal calendars, handle the recurring events directly
      const totalEvents = Object.keys(recurringEvents).length
      const selectedEvents = selectedRecurringEvents.value.length
      
      if (totalEvents === 0) {
        return 'Calendar is empty'
      } else if (selectedEvents === 0) {
        return `0/${totalEvents} Events`
      } else {
        return `${selectedEvents}/${totalEvents} Events`
      }
    }
    
    const result = selectionStore.getGroupBreakdownSummary(groups)
    
    // Handle translation keys that the store returns
    if (result === 'common.noEventsOrGroupsSelected') {
      return t('common.noEventsOrGroupsSelected')
    }
    
    return result
  }
  
  // ===============================================
  // GROUP OPERATIONS WITH APP STORE INTEGRATION
  // ===============================================
  
  const subscribeAndSelectAllGroups = () => {
    selectionStore.subscribeAndSelectAllGroups(appStore.groups || {})
  }
  
  const expandAllGroups = () => {
    selectionStore.expandAllGroups(appStore.groups || {})
  }
  
  const selectAllGroups = () => {
    selectionStore.selectAllGroups(appStore.groups || {})
  }
  
  // ===============================================
  // BULK GROUP ACTIONS
  // ===============================================
  
  /**
   * Handle "Select All Recurring Events" action for a group
   */
  const handleSelectAllRecurringEvents = ({ groupId, recurringEvents, selectAll }) => {
    if (selectAll) {
      // Select all recurring events in this group
      recurringEvents.forEach(recurringEvent => {
        if (!selectedRecurringEvents.value.includes(recurringEvent)) {
          selectionStore.toggleRecurringEvent(recurringEvent)
        }
      })
    } else {
      // Deselect all recurring events in this group
      recurringEvents.forEach(recurringEvent => {
        if (selectedRecurringEvents.value.includes(recurringEvent)) {
          selectionStore.toggleRecurringEvent(recurringEvent)
        }
      })
    }
  }
  
  // ===============================================
  // COMPUTED UI STATE HELPERS
  // ===============================================
  
  const allGroupsExpanded = computed(() => {
    const groups = appStore.groups || {}
    const groupIds = Object.keys(groups)
    return groupIds.length > 0 && 
           groupIds.every(id => selectionStore.isGroupExpanded(id))
  })
  
  const allGroupsCollapsed = computed(() => {
    return expandedGroups.value.size === 0
  })

  // ===============================================
  // RETURN UNIFIED API
  // ===============================================
  
  return {
    // Reactive state from stores
    selectedRecurringEvents,
    subscribedGroups,
    expandedGroups,
    expandedRecurringEvents,
    
    // Computed properties
    effectiveSelectedRecurringEvents,
    selectionSummary,
    selectedCount,
    allGroupsExpanded,
    allGroupsCollapsed,
    
    // Individual recurring event operations
    isRecurringEventSelected: selectionStore.isRecurringEventSelected,
    isRecurringEventEffectivelySelected,
    toggleRecurringEvent: selectionStore.toggleRecurringEvent,
    selectRecurringEvents: selectionStore.selectRecurringEvents,
    deselectRecurringEvents: selectionStore.deselectRecurringEvents,
    
    // Group subscription operations
    isGroupSubscribed: selectionStore.isGroupSubscribed,
    subscribeToGroup: selectionStore.subscribeToGroup,
    unsubscribeFromGroup: selectionStore.unsubscribeFromGroup,
    toggleGroupSubscription: selectionStore.toggleGroupSubscription,
    
    // Combined operations
    subscribeAndSelectGroup: selectionStore.subscribeAndSelectGroup,
    unsubscribeAndDeselectGroup: selectionStore.unsubscribeAndDeselectGroup,
    
    // Bulk operations
    selectAllGroups,
    unsubscribeFromAllGroups: selectionStore.unsubscribeFromAllGroups,
    unsubscribeAndDeselectAllGroups: () => selectionStore.unsubscribeAndDeselectAllGroups(appStore.groups || {}),
    subscribeAndSelectAllGroups,
    clearSelection: selectionStore.clearSelection,
    
    // Expansion operations
    isGroupExpanded: selectionStore.isGroupExpanded,
    toggleGroupExpansion: selectionStore.toggleGroupExpansion,
    expandAllGroups,
    collapseAllGroups: selectionStore.collapseAllGroups,
    
    // UI helper functions
    getGroupRecurringEvents: selectionStore.getGroupRecurringEvents,
    isGroupFullySelected: selectionStore.isGroupFullySelected,
    isGroupPartiallySelected: selectionStore.isGroupPartiallySelected,
    getGroupSelectionState: selectionStore.getGroupSelectionState,
    toggleGroupSelection: selectionStore.toggleGroupSelection,
    
    // Selection checking methods  
    allEventsSelected,
    
    // Summary functions
    getSelectionSummary: getSelectionSummaryData,
    getGroupBreakdownSummary,
    
    // Bulk actions
    handleSelectAllRecurringEvents
  }
}