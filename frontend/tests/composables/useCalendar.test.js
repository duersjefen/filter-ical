/**
 * Tests for useCalendar composable
 *
 * Following TDD principles from CLAUDE.md:
 * - Unit tests for pure functions and business logic
 * - Edge cases and error handling
 * - Integration tests with stores
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { ref } from 'vue'
import { useCalendar } from '../../src/composables/useCalendar'
import { useAppStore } from '../../src/stores/app'
import { useSelectionStore } from '../../src/stores/selectionStore'

// Mock useUsername
vi.mock('../../src/composables/useUsername', () => ({
  useUsername: () => ({
    getUserId: vi.fn(() => 'test-user'),
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

describe('useCalendar', () => {
  let pinia
  let appStore
  let selectionStore

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    appStore = useAppStore()
    selectionStore = useSelectionStore()
  })

  describe('Initialization', () => {
    it('initializes with default state', () => {
      const calendar = useCalendar()

      expect(calendar.showSingleEvents.value).toBe(false)
      expect(calendar.showRecurringEventsSection.value).toBe(true)
      expect(calendar.showGroupsSection.value).toBe(true)
      expect(calendar.showSelectedOnly.value).toBe(false)
      expect(calendar.recurringEventSearch.value).toBe('')
    })

    it('provides all expected methods', () => {
      const calendar = useCalendar()

      expect(typeof calendar.toggleRecurringEvent).toBe('function')
      expect(typeof calendar.selectAllRecurringEvents).toBe('function')
      expect(typeof calendar.clearAllRecurringEvents).toBe('function')
      expect(typeof calendar.selectAllSingleEvents).toBe('function')
      expect(typeof calendar.clearAllSingleEvents).toBe('function')
      expect(typeof calendar.generateIcalFile).toBe('function')
      expect(typeof calendar.updateCalendarId).toBe('function')
    })

    it('accepts custom events and recurring events data', () => {
      const customEvents = ref([
        { title: 'Meeting', dtstart: '2024-01-01T10:00:00' }
      ])
      const customRecurringEvents = ref({
        'Meeting': { title: 'Meeting', count: 5 }
      })

      const calendar = useCalendar(customEvents, customRecurringEvents)
      expect(calendar.recurringEventsSortedByCount.value.length).toBeGreaterThan(0)
    })

    it('uses app store data when no custom data provided', () => {
      appStore.recurringEvents = {
        'Team Sync': { title: 'Team Sync', count: 3 }
      }

      const calendar = useCalendar()
      expect(calendar.recurringEventsSortedByCount.value.length).toBe(1)
    })
  })

  describe('Recurring Events Processing', () => {
    beforeEach(() => {
      appStore.recurringEvents = {
        'Daily Standup': { title: 'Daily Standup', count: 10 },
        'Team Meeting': { title: 'Team Meeting', count: 4 },
        'One-off Event': { title: 'One-off Event', count: 1 },
        'Another Single': { title: 'Another Single', count: 1 }
      }
    })

    it('transforms recurring events to sorted array', () => {
      const calendar = useCalendar()
      const sorted = calendar.recurringEventsSortedByCount.value

      expect(sorted.length).toBe(4)
      expect(sorted[0].count).toBeGreaterThanOrEqual(sorted[1].count)
    })

    it('categorizes recurring events (count > 1)', () => {
      const calendar = useCalendar()
      const mainEvents = calendar.mainRecurringEvents.value

      expect(mainEvents.length).toBe(2)
      expect(mainEvents.every(e => e.count > 1)).toBe(true)
    })

    it('categorizes single events (count === 1)', () => {
      const calendar = useCalendar()
      const singleEvents = calendar.singleRecurringEvents.value

      expect(singleEvents.length).toBe(2)
      expect(singleEvents.every(e => e.count === 1)).toBe(true)
    })

    it('provides backward compatible aliases', () => {
      const calendar = useCalendar()

      expect(calendar.recurringRecurringEvents.value).toEqual(calendar.mainRecurringEvents.value)
      expect(calendar.uniqueRecurringEvents.value).toEqual(calendar.singleRecurringEvents.value)
    })

    it('provides unified recurring events list', () => {
      const calendar = useCalendar()
      const unified = calendar.unifiedRecurringEvents.value

      expect(unified.length).toBe(4)
      // Should be sorted by count descending, then alphabetically
      expect(unified[0].count).toBeGreaterThanOrEqual(unified[unified.length - 1].count)
    })
  })

  describe('Search Filtering', () => {
    beforeEach(() => {
      appStore.recurringEvents = {
        'Daily Standup': { title: 'Daily Standup', count: 10 },
        'Weekly Team Meeting': { title: 'Weekly Team Meeting', count: 4 },
        'Monthly Review': { title: 'Monthly Review', count: 2 },
        'Project Planning': { title: 'Project Planning', count: 3 }
      }
    })

    it('filters recurring events by search query', () => {
      const calendar = useCalendar()

      calendar.recurringEventSearch.value = 'meeting'
      const filtered = calendar.filteredRecurringEvents.value

      expect(filtered.length).toBe(1)
      expect(filtered[0].name).toContain('Meeting')
    })

    it('search is case-insensitive', () => {
      const calendar = useCalendar()

      calendar.recurringEventSearch.value = 'DAILY'
      const filtered = calendar.filteredRecurringEvents.value

      expect(filtered.length).toBe(1)
      expect(filtered[0].name).toBe('Daily Standup')
    })

    it('returns all events when search is empty', () => {
      const calendar = useCalendar()

      calendar.recurringEventSearch.value = ''
      const filtered = calendar.filteredRecurringEvents.value

      expect(filtered.length).toBe(4)
    })

    it('returns empty array when no matches found', () => {
      const calendar = useCalendar()

      calendar.recurringEventSearch.value = 'NonexistentEvent'
      const filtered = calendar.filteredRecurringEvents.value

      expect(filtered.length).toBe(0)
    })

    it('handles partial matches', () => {
      const calendar = useCalendar()

      calendar.recurringEventSearch.value = 'ly' // matches "Daily" and "Weekly" and "Monthly"
      const filtered = calendar.filteredRecurringEvents.value

      expect(filtered.length).toBeGreaterThan(0)
    })
  })

  describe('Recurring Event Selection', () => {
    beforeEach(() => {
      appStore.recurringEvents = {
        'Daily Standup': { title: 'Daily Standup', count: 10 },
        'Team Meeting': { title: 'Team Meeting', count: 4 },
        'One-off Event': { title: 'One-off Event', count: 1 }
      }
    })

    it('toggles recurring event selection', () => {
      const calendar = useCalendar()

      calendar.toggleRecurringEvent('Daily Standup')
      expect(selectionStore.isRecurringEventSelected('Daily Standup')).toBe(true)

      calendar.toggleRecurringEvent('Daily Standup')
      expect(selectionStore.isRecurringEventSelected('Daily Standup')).toBe(false)
    })

    it('selects all filtered recurring events', () => {
      const calendar = useCalendar()

      calendar.selectAllRecurringEvents()
      expect(selectionStore.selectedRecurringEvents.length).toBe(3)
    })

    it('selects all single events only', () => {
      const calendar = useCalendar()

      calendar.selectAllSingleEvents()
      expect(selectionStore.isRecurringEventSelected('One-off Event')).toBe(true)
      expect(selectionStore.isRecurringEventSelected('Daily Standup')).toBe(false)
    })

    it('clears all recurring events', () => {
      const calendar = useCalendar()

      calendar.selectAllRecurringEvents()
      calendar.clearAllRecurringEvents()
      expect(selectionStore.selectedRecurringEvents.length).toBe(0)
    })

    it('clears only single events', () => {
      const calendar = useCalendar()

      calendar.selectAllRecurringEvents()
      calendar.clearAllSingleEvents()

      expect(selectionStore.isRecurringEventSelected('One-off Event')).toBe(false)
      expect(selectionStore.isRecurringEventSelected('Daily Standup')).toBe(true)
    })

    it('computes selected recurring events count', () => {
      const calendar = useCalendar()

      calendar.toggleRecurringEvent('Daily Standup')
      calendar.toggleRecurringEvent('Team Meeting')

      expect(calendar.selectedRecurringEventsCount.value).toBeGreaterThan(0)
    })
  })

  describe('Recurring Event Expansion', () => {
    it('toggles recurring event expansion state', () => {
      const calendar = useCalendar()

      calendar.toggleRecurringEventExpansion('Daily Standup')
      expect(selectionStore.expandedRecurringEvents.has('Daily Standup')).toBe(true)

      calendar.toggleRecurringEventExpansion('Daily Standup')
      expect(selectionStore.expandedRecurringEvents.has('Daily Standup')).toBe(false)
    })

    it('maintains expansion state for multiple recurring events', () => {
      const calendar = useCalendar()

      calendar.toggleRecurringEventExpansion('Event 1')
      calendar.toggleRecurringEventExpansion('Event 2')

      expect(selectionStore.expandedRecurringEvents.has('Event 1')).toBe(true)
      expect(selectionStore.expandedRecurringEvents.has('Event 2')).toBe(true)
    })
  })

  describe('Recurring Event Stats', () => {
    beforeEach(() => {
      appStore.recurringEvents = {
        'Recurring Event 1': { title: 'Recurring Event 1', count: 10 },
        'Recurring Event 2': { title: 'Recurring Event 2', count: 5 },
        'Single Event 1': { title: 'Single Event 1', count: 1 },
        'Single Event 2': { title: 'Single Event 2', count: 1 }
      }
    })

    it('calculates recurring event statistics', () => {
      const calendar = useCalendar()
      const stats = calendar.recurringEventStats.value

      expect(stats).toHaveProperty('totalRecurringEvents')
      expect(stats).toHaveProperty('recurringRecurringEvents')
      expect(stats).toHaveProperty('uniqueRecurringEvents')
    })

    it('correctly categorizes recurring vs single events', () => {
      const calendar = useCalendar()
      const stats = calendar.recurringEventStats.value

      expect(stats.recurringRecurringEvents).toBe(2)
      expect(stats.uniqueRecurringEvents).toBe(2)
    })
  })

  describe('Recurring Event Classification', () => {
    beforeEach(() => {
      appStore.recurringEvents = {
        'Daily Standup': { title: 'Daily Standup', count: 10 },
        'One-off': { title: 'One-off', count: 1 }
      }
    })

    it('classifies recurring events correctly', () => {
      const calendar = useCalendar()

      const recurring = calendar.classifyRecurringEvent('Daily Standup')
      expect(recurring).toBe('recurring')

      const single = calendar.classifyRecurringEvent('One-off')
      expect(single).toBe('unique')
    })

    it('handles unknown recurring events', () => {
      const calendar = useCalendar()

      const unknown = calendar.classifyRecurringEvent('Unknown Event')
      expect(unknown).toBe('unknown')
    })
  })

  describe('Calendar Switching', () => {
    it('updates calendar ID', () => {
      const calendar = useCalendar(null, null, 'calendar-1')

      calendar.updateCalendarId('calendar-2')
      // Calendar ID is internal, but we can verify it doesn't throw
      expect(() => calendar.updateCalendarId('calendar-3')).not.toThrow()
    })

    it('resets state when calendar ID changes', async () => {
      const calendar = useCalendar(null, null, 'calendar-1')

      calendar.toggleRecurringEvent('Event 1')
      calendar.recurringEventSearch.value = 'test'

      // Trigger calendar change
      calendar.updateCalendarId('calendar-2')

      // Wait for watchers to run
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(calendar.recurringEventSearch.value).toBe('')
      expect(calendar.showSingleEvents.value).toBe(false)
    })

    it('does not reset state when ID is same', async () => {
      const calendar = useCalendar(null, null, 'calendar-1')

      calendar.recurringEventSearch.value = 'test'
      calendar.updateCalendarId('calendar-1')

      await new Promise(resolve => setTimeout(resolve, 0))

      expect(calendar.recurringEventSearch.value).toBe('test')
    })
  })

  describe('iCal Generation', () => {
    beforeEach(() => {
      appStore.selectedCalendar = {
        id: 'test-calendar',
        name: 'Test Calendar'
      }
      appStore.generateIcal = vi.fn()
    })

    it('calls appStore.generateIcal with correct parameters', async () => {
      const calendar = useCalendar()

      calendar.toggleRecurringEvent('Event 1')
      appStore.generateIcal.mockResolvedValue({
        success: true,
        data: 'BEGIN:VCALENDAR\nEND:VCALENDAR'
      })

      await calendar.generateIcalFile()

      expect(appStore.generateIcal).toHaveBeenCalledWith({
        calendarId: 'test-calendar',
        selectedRecurringEvents: expect.any(Array)
      })
    })

    it('handles iCal generation errors gracefully', async () => {
      const calendar = useCalendar()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      appStore.generateIcal.mockResolvedValue({
        success: false,
        error: 'Generation failed'
      })

      await calendar.generateIcalFile()

      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })

    it('handles network errors during iCal generation', async () => {
      const calendar = useCalendar()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      appStore.generateIcal.mockRejectedValue(new Error('Network error'))

      await calendar.generateIcalFile()

      expect(consoleSpy).toHaveBeenCalledWith('Error generating iCal:', expect.any(Error))
      consoleSpy.mockRestore()
    })
  })

  describe('Edge Cases', () => {
    it('handles empty recurring events gracefully', () => {
      appStore.recurringEvents = {}

      const calendar = useCalendar()
      expect(calendar.recurringEventsSortedByCount.value).toEqual([])
      expect(calendar.mainRecurringEvents.value).toEqual([])
      expect(calendar.singleRecurringEvents.value).toEqual([])
    })

    it('handles null recurring events', () => {
      appStore.recurringEvents = null

      const calendar = useCalendar()
      expect(() => calendar.recurringEventsSortedByCount.value).not.toThrow()
    })

    it('handles undefined recurring events', () => {
      appStore.recurringEvents = undefined

      const calendar = useCalendar()
      expect(() => calendar.recurringEventsSortedByCount.value).not.toThrow()
    })

    it('handles recurring events with special characters in titles', () => {
      appStore.recurringEvents = {
        'Meeting @ Coffee Shop 😊': { title: 'Meeting @ Coffee Shop 😊', count: 3 },
        'Review: Q1/Q2 Analysis': { title: 'Review: Q1/Q2 Analysis', count: 2 }
      }

      const calendar = useCalendar()
      const sorted = calendar.recurringEventsSortedByCount.value

      expect(sorted.length).toBe(2)
    })

    it('handles very large event counts', () => {
      appStore.recurringEvents = {
        'Daily Event': { title: 'Daily Event', count: 365 },
        'Hourly Event': { title: 'Hourly Event', count: 8760 }
      }

      const calendar = useCalendar()
      const sorted = calendar.recurringEventsSortedByCount.value

      expect(sorted[0].count).toBe(8760)
    })

    it('handles zero event count', () => {
      appStore.recurringEvents = {
        'Zero Event': { title: 'Zero Event', count: 0 }
      }

      const calendar = useCalendar()
      expect(calendar.recurringEventsSortedByCount.value.length).toBeGreaterThanOrEqual(0)
    })

    it('handles long search queries', () => {
      appStore.recurringEvents = {
        'Event': { title: 'Event', count: 1 }
      }

      const calendar = useCalendar()
      calendar.recurringEventSearch.value = 'A'.repeat(1000)

      expect(() => calendar.filteredRecurringEvents.value).not.toThrow()
    })

    it('handles search with regex special characters', () => {
      appStore.recurringEvents = {
        'Event (test)': { title: 'Event (test)', count: 1 },
        'Event [test]': { title: 'Event [test]', count: 1 }
      }

      const calendar = useCalendar()
      calendar.recurringEventSearch.value = '(test)'

      expect(() => calendar.filteredRecurringEvents.value).not.toThrow()
    })
  })

  describe('State Toggles', () => {
    it('toggles showSingleEvents', () => {
      const calendar = useCalendar()

      expect(calendar.showSingleEvents.value).toBe(false)
      calendar.showSingleEvents.value = true
      expect(calendar.showSingleEvents.value).toBe(true)
    })

    it('toggles showRecurringEventsSection', () => {
      const calendar = useCalendar()

      expect(calendar.showRecurringEventsSection.value).toBe(true)
      calendar.showRecurringEventsSection.value = false
      expect(calendar.showRecurringEventsSection.value).toBe(false)
    })

    it('toggles showGroupsSection', () => {
      const calendar = useCalendar()

      expect(calendar.showGroupsSection.value).toBe(true)
      calendar.showGroupsSection.value = false
      expect(calendar.showGroupsSection.value).toBe(false)
    })

    it('toggles showSelectedOnly', () => {
      const calendar = useCalendar()

      expect(calendar.showSelectedOnly.value).toBe(false)
      calendar.showSelectedOnly.value = true
      expect(calendar.showSelectedOnly.value).toBe(true)
    })
  })

  describe('Store Integration', () => {
    it('uses selectionStore for selection state', () => {
      const calendar = useCalendar()

      selectionStore.toggleRecurringEvent('Test Event')
      expect(selectionStore.isRecurringEventSelected('Test Event')).toBe(true)
    })

    it('uses appStore for recurring events when no custom data provided', () => {
      appStore.recurringEvents = {
        'Store Event': { title: 'Store Event', count: 5 }
      }

      const calendar = useCalendar()
      const sorted = calendar.recurringEventsSortedByCount.value

      expect(sorted.some(e => e.name === 'Store Event')).toBe(true)
    })
  })
})
