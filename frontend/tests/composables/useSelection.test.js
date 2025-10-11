/**
 * Tests for useSelection composable
 *
 * Following TDD principles from CLAUDE.md:
 * - Unit tests for pure functions and business logic
 * - Integration tests with stores
 * - Edge cases and error handling
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSelection } from '../../src/composables/useSelection'
import { useSelectionStore } from '../../src/stores/selectionStore'
import { useAppStore } from '../../src/stores/app'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key) => key // Return translation key as-is for testing
  })
}))

// Mock useUsername
vi.mock('../../src/composables/useUsername', () => ({
  useUsername: () => ({
    getUserId: vi.fn(),
    onUsernameChange: vi.fn()
  })
}))

// Mock useHTTP
vi.mock('../../src/composables/useHTTP', () => ({
  useHTTP: () => ({
    loading: { value: false },
    error: { value: null },
    clearError: vi.fn(),
    setError: vi.fn()
  })
}))

describe('useSelection', () => {
  let selection
  let selectionStore
  let appStore

  beforeEach(() => {
    setActivePinia(createPinia())
    selection = useSelection()
    selectionStore = useSelectionStore()
    appStore = useAppStore()
  })

  describe('Initialization', () => {
    it('provides all expected API methods and properties', () => {
      expect(selection).toHaveProperty('selectedRecurringEvents')
      expect(selection).toHaveProperty('subscribedGroups')
      expect(selection).toHaveProperty('expandedGroups')
      expect(selection).toHaveProperty('effectiveSelectedRecurringEvents')
      expect(selection).toHaveProperty('selectionSummary')
      expect(selection).toHaveProperty('selectedCount')
      expect(selection).toHaveProperty('isRecurringEventSelected')
      expect(selection).toHaveProperty('toggleRecurringEvent')
      expect(selection).toHaveProperty('selectRecurringEvents')
      expect(selection).toHaveProperty('deselectRecurringEvents')
      expect(selection).toHaveProperty('subscribeToGroup')
      expect(selection).toHaveProperty('unsubscribeFromGroup')
      expect(selection).toHaveProperty('clearSelection')
    })

    it('initializes with empty state', () => {
      expect(selection.selectedRecurringEvents.value.length).toBe(0)
      expect(selection.subscribedGroups.value.size).toBe(0)
      expect(selection.expandedGroups.value.size).toBe(0)
    })
  })

  describe('Individual Recurring Event Operations', () => {
    it('selects a recurring event', () => {
      selection.toggleRecurringEvent('Meeting')
      expect(selection.isRecurringEventSelected('Meeting')).toBe(true)
    })

    it('deselects a recurring event', () => {
      selection.toggleRecurringEvent('Meeting')
      expect(selection.isRecurringEventSelected('Meeting')).toBe(true)
      selection.toggleRecurringEvent('Meeting')
      expect(selection.isRecurringEventSelected('Meeting')).toBe(false)
    })

    it('selects multiple recurring events at once', () => {
      selection.selectRecurringEvents(['Meeting', 'Lunch', 'Workout'])
      expect(selection.isRecurringEventSelected('Meeting')).toBe(true)
      expect(selection.isRecurringEventSelected('Lunch')).toBe(true)
      expect(selection.isRecurringEventSelected('Workout')).toBe(true)
    })

    it('deselects multiple recurring events at once', () => {
      selection.selectRecurringEvents(['Meeting', 'Lunch', 'Workout'])
      selection.deselectRecurringEvents(['Meeting', 'Workout'])
      expect(selection.isRecurringEventSelected('Meeting')).toBe(false)
      expect(selection.isRecurringEventSelected('Lunch')).toBe(true)
      expect(selection.isRecurringEventSelected('Workout')).toBe(false)
    })

    it('does not add duplicate recurring events', () => {
      // Note: The underlying store doesn't filter duplicates when adding
      // This test verifies that when we call with duplicates, they are added
      // The store's selectRecurringEvents filters already-selected events
      selection.selectRecurringEvents(['Meeting', 'Lunch'])
      selection.selectRecurringEvents(['Meeting']) // Try to add Meeting again
      expect(selection.selectedRecurringEvents.value.length).toBe(2)
    })

    it('handles empty recurring event list', () => {
      selection.selectRecurringEvents([])
      expect(selection.selectedRecurringEvents.value.length).toBe(0)
    })
  })

  describe('Group Subscription Operations', () => {
    it('subscribes to a group', () => {
      selection.subscribeToGroup('1')
      expect(selection.isGroupSubscribed('1')).toBe(true)
    })

    it('unsubscribes from a group', () => {
      selection.subscribeToGroup('1')
      selection.unsubscribeFromGroup('1')
      expect(selection.isGroupSubscribed('1')).toBe(false)
    })

    it('toggles group subscription', () => {
      selection.toggleGroupSubscription('1')
      expect(selection.isGroupSubscribed('1')).toBe(true)
      selection.toggleGroupSubscription('1')
      expect(selection.isGroupSubscribed('1')).toBe(false)
    })

    it('handles multiple group subscriptions', () => {
      selection.subscribeToGroup('1')
      selection.subscribeToGroup('2')
      selection.subscribeToGroup('3')
      expect(selection.subscribedGroups.value.size).toBe(3)
    })
  })

  describe('Effective Selection (Individual + Group)', () => {
    beforeEach(() => {
      // Setup app store with groups containing recurring events
      appStore.groups = {
        '1': {
          id: 1,
          name: 'Work',
          recurring_events: [
            { title: 'Daily Standup', event_count: 5 },
            { title: 'Team Meeting', event_count: 3 }
          ]
        },
        '2': {
          id: 2,
          name: 'Personal',
          recurring_events: [
            { title: 'Workout', event_count: 4 },
            { title: 'Lunch', event_count: 7 }
          ]
        }
      }
    })

    it('recognizes individually selected recurring events as effectively selected', () => {
      selection.toggleRecurringEvent('Daily Standup')
      expect(selection.isRecurringEventEffectivelySelected('Daily Standup')).toBe(true)
    })

    it('recognizes recurring events from subscribed groups as effectively selected', () => {
      selection.subscribeToGroup('1')
      expect(selection.isRecurringEventEffectivelySelected('Daily Standup')).toBe(true)
      expect(selection.isRecurringEventEffectivelySelected('Team Meeting')).toBe(true)
    })

    it('does not recognize unselected recurring events as effectively selected', () => {
      expect(selection.isRecurringEventEffectivelySelected('Daily Standup')).toBe(false)
    })

    it('handles effectiveSelectedRecurringEvents computation correctly', () => {
      selection.toggleRecurringEvent('Workout')
      selection.subscribeToGroup('1')

      const effective = selection.effectiveSelectedRecurringEvents.value
      expect(effective).toContain('Workout')
      expect(effective).toContain('Daily Standup')
      expect(effective).toContain('Team Meeting')
    })
  })

  describe('Combined Operations (Subscribe & Select)', () => {
    beforeEach(() => {
      appStore.groups = {
        '1': {
          id: 1,
          name: 'Work',
          recurring_events: [
            { title: 'Daily Standup', event_count: 5 },
            { title: 'Team Meeting', event_count: 3 }
          ]
        }
      }
    })

    it('subscribes and selects all recurring events in a group', () => {
      selection.subscribeAndSelectGroup('1', appStore.groups['1'])
      expect(selection.isGroupSubscribed('1')).toBe(true)
      expect(selection.isRecurringEventSelected('Daily Standup')).toBe(true)
      expect(selection.isRecurringEventSelected('Team Meeting')).toBe(true)
    })

    it('unsubscribes and deselects all recurring events in a group', () => {
      selection.subscribeAndSelectGroup('1', appStore.groups['1'])
      selection.unsubscribeAndDeselectGroup('1', appStore.groups['1'])
      expect(selection.isGroupSubscribed('1')).toBe(false)
      expect(selection.isRecurringEventSelected('Daily Standup')).toBe(false)
      expect(selection.isRecurringEventSelected('Team Meeting')).toBe(false)
    })
  })

  describe('Bulk Operations', () => {
    beforeEach(() => {
      appStore.groups = {
        '1': {
          id: 1,
          name: 'Work',
          recurring_events: [
            { title: 'Daily Standup', event_count: 5 },
            { title: 'Team Meeting', event_count: 3 }
          ]
        },
        '2': {
          id: 2,
          name: 'Personal',
          recurring_events: [
            { title: 'Workout', event_count: 4 },
            { title: 'Lunch', event_count: 7 }
          ]
        }
      }
    })

    it('subscribes to all groups at once', () => {
      selection.selectAllGroups()
      expect(selection.subscribedGroups.value.size).toBe(2)
      expect(selection.isGroupSubscribed('1')).toBe(true)
      expect(selection.isGroupSubscribed('2')).toBe(true)
    })

    it('unsubscribes from all groups at once', () => {
      selection.selectAllGroups()
      selection.unsubscribeFromAllGroups()
      expect(selection.subscribedGroups.value.size).toBe(0)
    })

    it('subscribes and selects all groups', () => {
      selection.subscribeAndSelectAllGroups()
      expect(selection.subscribedGroups.value.size).toBe(2)
      expect(selection.isRecurringEventSelected('Daily Standup')).toBe(true)
      expect(selection.isRecurringEventSelected('Workout')).toBe(true)
    })

    it('unsubscribes and deselects all groups', () => {
      selection.subscribeAndSelectAllGroups()
      selection.unsubscribeAndDeselectAllGroups()
      expect(selection.subscribedGroups.value.size).toBe(0)
      expect(selection.selectedRecurringEvents.value.length).toBe(0)
    })

    it('clears all selections', () => {
      selection.toggleRecurringEvent('Daily Standup')
      selection.subscribeToGroup('1')
      selection.clearSelection()
      expect(selection.selectedRecurringEvents.value.length).toBe(0)
      expect(selection.subscribedGroups.value.size).toBe(0)
    })
  })

  describe('Expansion State Operations', () => {
    beforeEach(() => {
      appStore.groups = {
        '1': { id: 1, name: 'Work', recurring_events: [] },
        '2': { id: 2, name: 'Personal', recurring_events: [] },
        '3': { id: 3, name: 'Hobbies', recurring_events: [] }
      }
    })

    it('toggles group expansion', () => {
      selection.toggleGroupExpansion('1')
      expect(selection.isGroupExpanded('1')).toBe(true)
      selection.toggleGroupExpansion('1')
      expect(selection.isGroupExpanded('1')).toBe(false)
    })

    it('expands all groups', () => {
      selection.expandAllGroups()
      expect(selection.allGroupsExpanded.value).toBe(true)
      expect(selection.expandedGroups.value.size).toBe(3)
    })

    it('collapses all groups', () => {
      selection.expandAllGroups()
      selection.collapseAllGroups()
      expect(selection.allGroupsCollapsed.value).toBe(true)
      expect(selection.expandedGroups.value.size).toBe(0)
    })

    it('detects when all groups are expanded', () => {
      expect(selection.allGroupsExpanded.value).toBe(false)
      selection.expandAllGroups()
      expect(selection.allGroupsExpanded.value).toBe(true)
    })

    it('detects when all groups are collapsed', () => {
      expect(selection.allGroupsCollapsed.value).toBe(true)
      selection.toggleGroupExpansion('1')
      expect(selection.allGroupsCollapsed.value).toBe(false)
    })
  })

  describe('Selection Summary', () => {
    beforeEach(() => {
      appStore.groups = {
        '1': {
          id: 1,
          name: 'Work',
          recurring_events: [
            { title: 'Daily Standup', event_count: 5 },
            { title: 'Team Meeting', event_count: 3 }
          ]
        },
        '2': {
          id: 2,
          name: 'Personal',
          recurring_events: [
            { title: 'Workout', event_count: 4 }
          ]
        }
      }
    })

    it('generates correct selection summary', () => {
      selection.toggleRecurringEvent('Daily Standup')
      const summary = selection.getSelectionSummary()
      expect(summary.selected).toBe(1)
      expect(summary.total).toBe(3)
    })

    it('counts no double-counting when recurring event is in subscribed group', () => {
      selection.subscribeToGroup('1')
      selection.toggleRecurringEvent('Daily Standup')
      const summary = selection.getSelectionSummary()
      expect(summary.selected).toBe(2) // Both events in group 1
    })

    it('returns "Calendar is empty" for empty personal calendar', () => {
      appStore.groups = {}
      appStore.recurringEvents = {}
      const breakdown = selection.getGroupBreakdownSummary()
      expect(breakdown).toBe('Calendar is empty')
    })

    it('generates compact group breakdown summary', () => {
      selection.toggleRecurringEvent('Daily Standup')
      selection.subscribeToGroup('2')
      const breakdown = selection.getGroupBreakdownSummary()
      expect(breakdown).toContain('Events')
      expect(breakdown).toContain('Groups')
    })

    it('shows "No groups" when no groups are subscribed', () => {
      // First select at least one event to avoid the "no events or groups" message
      selection.toggleRecurringEvent('Daily Standup')
      const breakdown = selection.getGroupBreakdownSummary()
      expect(breakdown).toContain('No groups')
    })

    it('shows "All groups" when all groups are subscribed', () => {
      selection.subscribeToGroup('1')
      selection.subscribeToGroup('2')
      const breakdown = selection.getGroupBreakdownSummary()
      expect(breakdown).toContain('All groups')
    })
  })

  describe('All Events Selected Check', () => {
    beforeEach(() => {
      appStore.groups = {
        '1': {
          id: 1,
          name: 'Work',
          recurring_events: [
            { title: 'Daily Standup', event_count: 5 },
            { title: 'Team Meeting', event_count: 3 }
          ]
        }
      }
    })

    it('returns false when no events selected', () => {
      expect(selection.allEventsSelected()).toBe(false)
    })

    it('returns false when some events selected', () => {
      selection.toggleRecurringEvent('Daily Standup')
      expect(selection.allEventsSelected()).toBe(false)
    })

    it('returns true when all events effectively selected', () => {
      selection.subscribeToGroup('1')
      expect(selection.allEventsSelected()).toBe(true)
    })

    it('returns false for empty groups', () => {
      appStore.groups = {}
      expect(selection.allEventsSelected()).toBe(false)
    })
  })

  describe('Handle Bulk Recurring Event Selection', () => {
    beforeEach(() => {
      appStore.groups = {
        '1': {
          id: 1,
          name: 'Work',
          recurring_events: [
            { title: 'Daily Standup', event_count: 5 },
            { title: 'Team Meeting', event_count: 3 }
          ]
        }
      }
    })

    it('selects all recurring events in a group', () => {
      selection.handleSelectAllRecurringEvents({
        groupId: '1',
        recurringEvents: ['Daily Standup', 'Team Meeting'],
        selectAll: true
      })
      expect(selection.isRecurringEventSelected('Daily Standup')).toBe(true)
      expect(selection.isRecurringEventSelected('Team Meeting')).toBe(true)
    })

    it('deselects all recurring events in a group', () => {
      selection.selectRecurringEvents(['Daily Standup', 'Team Meeting'])
      selection.handleSelectAllRecurringEvents({
        groupId: '1',
        recurringEvents: ['Daily Standup', 'Team Meeting'],
        selectAll: false
      })
      expect(selection.isRecurringEventSelected('Daily Standup')).toBe(false)
      expect(selection.isRecurringEventSelected('Team Meeting')).toBe(false)
    })
  })

  describe('Edge Cases', () => {
    it('handles null/undefined group data gracefully', () => {
      appStore.groups = null
      expect(() => selection.getSelectionSummary()).not.toThrow()
    })

    it('handles groups with no recurring events', () => {
      appStore.groups = {
        '1': { id: 1, name: 'Empty Group', recurring_events: [] }
      }
      const summary = selection.getSelectionSummary()
      expect(summary.total).toBe(0)
    })

    it('handles recurring events with zero event_count', () => {
      appStore.groups = {
        '1': {
          id: 1,
          name: 'Work',
          recurring_events: [
            { title: 'Old Event', event_count: 0 },
            { title: 'Active Event', event_count: 5 }
          ]
        }
      }
      const summary = selection.getSelectionSummary()
      expect(summary.total).toBe(1) // Only Active Event counts
    })

    it('handles unicode in recurring event titles', () => {
      selection.toggleRecurringEvent('会議 (Meeting)')
      expect(selection.isRecurringEventSelected('会議 (Meeting)')).toBe(true)
    })

    it('handles very long recurring event titles', () => {
      const longTitle = 'A'.repeat(500)
      selection.toggleRecurringEvent(longTitle)
      expect(selection.isRecurringEventSelected(longTitle)).toBe(true)
    })

    it('handles large number of recurring events', () => {
      const events = []
      for (let i = 0; i < 1000; i++) {
        events.push(`Event ${i}`)
      }
      selection.selectRecurringEvents(events)
      expect(selection.selectedRecurringEvents.value.length).toBe(1000)
    })

    it('handles concurrent group subscription/unsubscription', () => {
      selection.subscribeToGroup('1')
      selection.subscribeToGroup('2')
      selection.unsubscribeFromGroup('1')
      selection.subscribeToGroup('3')
      expect(selection.subscribedGroups.value.size).toBe(2)
      expect(selection.isGroupSubscribed('1')).toBe(false)
      expect(selection.isGroupSubscribed('2')).toBe(true)
      expect(selection.isGroupSubscribed('3')).toBe(true)
    })
  })

  describe('Personal Calendar Support', () => {
    it('handles personal calendars with no groups', () => {
      appStore.groups = {}
      appStore.recurringEvents = {
        'Meeting': { title: 'Meeting', event_count: 5 },
        'Lunch': { title: 'Lunch', event_count: 3 }
      }

      const breakdown = selection.getGroupBreakdownSummary()
      expect(breakdown).toContain('0/2 Events')
    })

    it('shows selected count for personal calendars', () => {
      appStore.groups = {}
      appStore.recurringEvents = {
        'Meeting': { title: 'Meeting', event_count: 5 },
        'Lunch': { title: 'Lunch', event_count: 3 }
      }

      selection.toggleRecurringEvent('Meeting')
      const breakdown = selection.getGroupBreakdownSummary()
      expect(breakdown).toContain('1/2 Events')
    })

    it('handles empty personal calendar', () => {
      appStore.groups = {}
      appStore.recurringEvents = {}

      const breakdown = selection.getGroupBreakdownSummary()
      expect(breakdown).toBe('Calendar is empty')
    })
  })

  describe('Computed Properties', () => {
    it('computes selectedCount correctly', () => {
      expect(selection.selectedCount.value).toBe(0)
      selection.toggleRecurringEvent('Meeting')
      expect(selection.selectedCount.value).toBe(1)
      selection.toggleRecurringEvent('Lunch')
      expect(selection.selectedCount.value).toBe(2)
    })

    it('computes selectionSummary with compactText', () => {
      appStore.groups = {
        '1': {
          id: 1,
          name: 'Work',
          recurring_events: [
            { title: 'Daily Standup', event_count: 5 }
          ]
        }
      }

      selection.toggleRecurringEvent('Daily Standup')
      const summary = selection.selectionSummary.value
      expect(summary).toHaveProperty('selected')
      expect(summary).toHaveProperty('total')
      expect(summary).toHaveProperty('compactText')
    })
  })

  describe('Store Integration', () => {
    it('delegates to selectionStore correctly', () => {
      // The composable returns the store function directly, so we check behavior
      selection.toggleRecurringEvent('Meeting')
      expect(selection.isRecurringEventSelected('Meeting')).toBe(true)
      selection.toggleRecurringEvent('Meeting')
      expect(selection.isRecurringEventSelected('Meeting')).toBe(false)
    })

    it('integrates with appStore for group data', () => {
      appStore.groups = {
        '1': {
          id: 1,
          name: 'Work',
          recurring_events: [
            { title: 'Meeting', event_count: 5 }
          ]
        }
      }

      const summary = selection.getSelectionSummary()
      expect(summary.total).toBe(1)
    })
  })
})
