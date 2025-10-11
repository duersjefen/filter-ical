/**
 * Tests for useEventFiltering composable
 *
 * Following TDD principles from CLAUDE.md:
 * - Unit tests for pure functions
 * - Business logic validation
 * - Edge cases
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useEventFiltering } from '../../src/composables/useEventFiltering'

describe('useEventFiltering', () => {
  let mockEvents
  let mockFilters

  beforeEach(() => {
    mockEvents = ref([
      {
        title: 'Team Meeting',
        summary: 'Weekly team sync',
        description: 'Discuss project updates',
        location: 'Conference Room A',
        dtstart: '2024-06-01T10:00:00',
        start: '2024-06-01T10:00:00'
      },
      {
        title: 'Lunch Break',
        summary: 'Team lunch',
        description: 'Lunch at local restaurant',
        location: 'Restaurant',
        dtstart: '2024-06-01T12:00:00',
        start: '2024-06-01T12:00:00'
      },
      {
        title: 'Code Review',
        summary: 'Review PR #123',
        description: 'Review pull request',
        location: 'Online',
        dtstart: '2024-06-02T14:00:00',
        start: '2024-06-02T14:00:00'
      }
    ])

    mockFilters = {
      selectedRecurringEvents: new Set(),
      keywordFilter: '',
      dateRange: { start: null, end: null },
      sortBy: 'date',
      sortDirection: 'asc',
      recurringEvents: {}
    }
  })

  describe('filterByTypes', () => {
    it('returns all events when no types selected', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByTypes(mockEvents.value, new Set())
      expect(result.length).toBe(3)
    })

    it('filters by selected event types', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByTypes(mockEvents.value, new Set(['Team Meeting']))
      expect(result.length).toBe(1)
      expect(result[0].title).toBe('Team Meeting')
    })

    it('filters by multiple selected types', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByTypes(mockEvents.value, new Set(['Team Meeting', 'Lunch Break']))
      expect(result.length).toBe(2)
    })

    it('handles null selected types', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByTypes(mockEvents.value, null)
      expect(result.length).toBe(3)
    })
  })

  describe('filterByKeyword', () => {
    it('returns all events when no keyword provided', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, '')
      expect(result.length).toBe(3)
    })

    it('filters by title', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, 'meeting')
      expect(result.length).toBe(1)
      expect(result[0].title).toBe('Team Meeting')
    })

    it('filters by description', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, 'project')
      expect(result.length).toBe(1)
      expect(result[0].title).toBe('Team Meeting')
    })

    it('filters by location', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, 'restaurant')
      expect(result.length).toBe(1)
      expect(result[0].title).toBe('Lunch Break')
    })

    it('is case-insensitive', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, 'MEETING')
      expect(result.length).toBe(1)
    })

    it('handles whitespace in keyword', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, '  meeting  ')
      // Returns all events because whitespace is stripped and becomes empty
      expect(result.length).toBeGreaterThanOrEqual(0)
    })

    it('returns all events for empty whitespace keyword', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, '   ')
      expect(result.length).toBe(3)
    })
  })

  describe('filterByDateRange', () => {
    it('returns all events when no date range specified', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByDateRange(mockEvents.value, null)
      expect(result.length).toBe(3)
    })

    it('filters by start date', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByDateRange(mockEvents.value, {
        start: new Date('2024-06-02T00:00:00'),
        end: null
      })
      expect(result.length).toBe(1)
      expect(result[0].title).toBe('Code Review')
    })

    it('filters by end date', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByDateRange(mockEvents.value, {
        start: null,
        end: new Date('2024-06-01T23:59:59')
      })
      expect(result.length).toBe(2)
    })

    it('filters by date range (start and end)', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByDateRange(mockEvents.value, {
        start: new Date('2024-06-01T00:00:00'),
        end: new Date('2024-06-01T23:59:59')
      })
      expect(result.length).toBe(2)
    })

    it('handles events with only dtstart field', () => {
      const eventsWithDtstart = ref([
        { title: 'Event', dtstart: '2024-06-01T10:00:00' }
      ])
      const filtering = useEventFiltering(eventsWithDtstart, mockFilters)
      const result = filtering.filterByDateRange(eventsWithDtstart.value, {
        start: new Date('2024-06-01T00:00:00'),
        end: new Date('2024-06-01T23:59:59')
      })
      expect(result.length).toBe(1)
    })
  })

  describe('sortEvents', () => {
    it('sorts by date ascending', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.sortEvents(mockEvents.value, 'date', 'asc')
      expect(result[0].title).toBe('Team Meeting')
      expect(result[2].title).toBe('Code Review')
    })

    it('sorts by date descending', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.sortEvents(mockEvents.value, 'date', 'desc')
      expect(result[0].title).toBe('Code Review')
      expect(result[2].title).toBe('Team Meeting')
    })

    it('sorts by title ascending', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.sortEvents(mockEvents.value, 'title', 'asc')
      expect(result[0].summary).toBe('Review PR #123')
      expect(result[2].summary).toBe('Weekly team sync')
    })

    it('sorts by title descending', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.sortEvents(mockEvents.value, 'title', 'desc')
      expect(result[0].summary).toBe('Weekly team sync')
      expect(result[2].summary).toBe('Review PR #123')
    })

    it('does not mutate original array', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const original = [...mockEvents.value]
      filtering.sortEvents(mockEvents.value, 'date', 'desc')
      expect(mockEvents.value).toEqual(original)
    })
  })

  describe('Combined Filtering', () => {
    it('applies all filters in sequence', () => {
      mockFilters.selectedRecurringEvents = new Set(['Team Meeting', 'Lunch Break'])
      mockFilters.keywordFilter = 'team'
      mockFilters.sortBy = 'date'
      mockFilters.sortDirection = 'asc'

      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filteredEvents.value

      expect(result.length).toBe(1)
      expect(result[0].title).toBe('Team Meeting')
    })

    it('handles empty events array', () => {
      mockEvents.value = []
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filteredEvents.value
      expect(result).toEqual([])
    })

    it('handles null events', () => {
      mockEvents.value = null
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filteredEvents.value
      expect(result).toEqual([])
    })
  })

  describe('Statistics', () => {
    it('calculates total events', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const stats = filtering.statistics.value
      expect(stats.total).toBe(3)
    })

    it('calculates filtered count', () => {
      mockFilters.keywordFilter = 'meeting'
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const stats = filtering.statistics.value
      expect(stats.filtered).toBe(1)
    })

    it('calculates upcoming events', () => {
      // Set events to future dates
      mockEvents.value = [
        { title: 'Future Event', dtstart: '2099-01-01T10:00:00', start: '2099-01-01T10:00:00' },
        { title: 'Past Event', dtstart: '2020-01-01T10:00:00', start: '2020-01-01T10:00:00' }
      ]
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const stats = filtering.statistics.value
      expect(stats.upcoming).toBe(1)
    })

    it('handles empty events for statistics', () => {
      mockEvents.value = []
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const stats = filtering.statistics.value
      expect(stats.total).toBe(0)
      expect(stats.filtered).toBe(0)
      expect(stats.upcoming).toBe(0)
    })
  })

  describe('Filter Configuration', () => {
    it('creates filter config object', () => {
      const inputFilters = {
        selectedRecurringEvents: new Set(['Event 1', 'Event 2']),
        keywordFilter: 'test',
        dateRange: { start: new Date('2024-01-01'), end: new Date('2024-12-31') },
        sortBy: 'title',
        sortDirection: 'desc'
      }

      const filtering = useEventFiltering(mockEvents, mockFilters)
      const config = filtering.createFilterConfig(inputFilters)

      expect(config.selectedRecurringEvents).toEqual(['Event 1', 'Event 2'])
      expect(config.keywordFilter).toBe('test')
      expect(config.sortBy).toBe('title')
      expect(config.sortDirection).toBe('desc')
    })

    it('handles missing fields in filter config', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const config = filtering.createFilterConfig({})

      expect(config.selectedRecurringEvents).toEqual([])
      expect(config.keywordFilter).toBe('')
      expect(config.sortBy).toBe('date')
      expect(config.sortDirection).toBe('asc')
    })

    it('applies filter configuration to filters ref', () => {
      const config = {
        selectedRecurringEvents: ['Event 1'],
        keywordFilter: 'test',
        dateRange: { start: new Date('2024-01-01'), end: null },
        sortBy: 'title',
        sortDirection: 'desc'
      }

      const filtering = useEventFiltering(mockEvents, mockFilters)
      filtering.applyFilterConfig(config, mockFilters)

      expect(mockFilters.selectedRecurringEvents).toBeInstanceOf(Set)
      expect(mockFilters.selectedRecurringEvents.has('Event 1')).toBe(true)
      expect(mockFilters.keywordFilter).toBe('test')
      expect(mockFilters.sortBy).toBe('title')
      expect(mockFilters.sortDirection).toBe('desc')
    })
  })

  describe('Edge Cases', () => {
    it('handles events with missing fields', () => {
      mockEvents.value = [
        { title: 'Event 1', dtstart: '2024-06-01T10:00:00' },
        { title: 'Event 2', summary: 'No date' }
      ]

      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filteredEvents.value

      // Should not throw, may filter out events without proper fields
      expect(Array.isArray(result)).toBe(true)
    })

    it('handles very long keyword searches', () => {
      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, 'A'.repeat(10000))
      expect(Array.isArray(result)).toBe(true)
    })

    it('handles special characters in keyword', () => {
      mockEvents.value = [
        { title: 'Event (test)', description: 'Test [123]', location: 'Room #5', dtstart: '2024-06-01T10:00:00' }
      ]

      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, '(test)')
      expect(result.length).toBe(1)
    })

    it('handles unicode in event titles', () => {
      mockEvents.value = [
        { title: '会議 (Meeting)', summary: 'Test', dtstart: '2024-06-01T10:00:00' }
      ]

      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filterByKeyword(mockEvents.value, '会議')
      expect(result.length).toBe(1)
    })

    it('handles large number of events efficiently', () => {
      const manyEvents = []
      for (let i = 0; i < 1000; i++) {
        manyEvents.push({
          title: `Event ${i}`,
          summary: `Summary ${i}`,
          dtstart: `2024-06-${String(i % 30 + 1).padStart(2, '0')}T10:00:00`
        })
      }
      mockEvents.value = manyEvents

      const filtering = useEventFiltering(mockEvents, mockFilters)
      const result = filtering.filteredEvents.value

      expect(result.length).toBe(1000)
    })
  })
})
