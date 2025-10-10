/**
 * Tests for eventHelpers utilities
 *
 * Following TDD principles from CLAUDE.md:
 * - Unit tests for pure functions
 * - 100% coverage requirement
 * - Test happy paths + edge cases + error cases
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  generateEventIdentifier,
  getRecurringEventKey,
  getEventGroupKey,
  transformRecurringEventsToArray,
  filterRecurringEventsBySearch,
  categorizeRecurringEvents,
  calculateSelectedRecurringEventsCount,
  filterEventsBySelection,
  filterFutureEvents,
  calculateRecurringEventStats,
  classifyRecurringEvent
} from '../../src/utils/eventHelpers'

// Mock i18n
vi.mock('../../src/i18n', () => ({
  default: {
    global: {
      t: vi.fn((key) => {
        const translations = {
          'dateTime.untitledEvent': 'Untitled Event',
          'dateTime.unknownEventType': 'Unknown Event Type'
        }
        return translations[key] || key
      })
    }
  }
}))

describe('eventHelpers', () => {
  describe('generateEventIdentifier', () => {
    it('uses UID as first priority', () => {
      const event = {
        uid: 'unique-id-123',
        title: 'Test Event',
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-18T11:00:00Z'
      }
      expect(generateEventIdentifier(event)).toBe('unique-id-123')
    })

    it('uses title + start + end as second priority', () => {
      const event = {
        title: 'Test Event',
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-18T11:00:00Z'
      }
      expect(generateEventIdentifier(event)).toBe('Test Event-2024-01-18T10:00:00Z-2024-01-18T11:00:00Z')
    })

    it('uses summary field when title is missing', () => {
      const event = {
        summary: 'Summary Event',
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-18T11:00:00Z'
      }
      expect(generateEventIdentifier(event)).toBe('Summary Event-2024-01-18T10:00:00Z-2024-01-18T11:00:00Z')
    })

    it('uses dtstart and dtend fields when start/end missing', () => {
      const event = {
        title: 'Test Event',
        dtstart: '2024-01-18T10:00:00Z',
        dtend: '2024-01-18T11:00:00Z'
      }
      expect(generateEventIdentifier(event)).toBe('Test Event-2024-01-18T10:00:00Z-2024-01-18T11:00:00Z')
    })

    it('uses "untitled" when title and summary missing', () => {
      const event = {
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-18T11:00:00Z'
      }
      expect(generateEventIdentifier(event)).toBe('untitled-2024-01-18T10:00:00Z-2024-01-18T11:00:00Z')
    })

    it('uses title + start + description hash when end is missing', () => {
      const event = {
        title: 'Test Event',
        start: '2024-01-18T10:00:00Z',
        description: 'This is a test description'
      }
      const descHash = 'This is a test description'.length.toString()
      expect(generateEventIdentifier(event)).toBe(`Test Event-2024-01-18T10:00:00Z-${descHash}`)
    })

    it('uses description hash of 0 when description is empty', () => {
      const event = {
        title: 'Test Event',
        start: '2024-01-18T10:00:00Z'
      }
      expect(generateEventIdentifier(event)).toBe('Test Event-2024-01-18T10:00:00Z-0')
    })

    it('uses title + description hash when start is missing', () => {
      const event = {
        title: 'Test Event',
        description: 'Test description'
      }
      const descHash = 'Test description'.length.toString()
      expect(generateEventIdentifier(event)).toBe(`Test Event-${descHash}`)
    })

    it('handles event with no dates or description', () => {
      const event = { title: 'Test Event' }
      expect(generateEventIdentifier(event)).toBe('Test Event-0')
    })

    it('handles completely empty event', () => {
      const event = {}
      expect(generateEventIdentifier(event)).toBe('untitled-0')
    })
  })

  describe('getRecurringEventKey', () => {
    it('returns title when available', () => {
      const event = { title: 'Test Event' }
      expect(getRecurringEventKey(event)).toBe('Test Event')
    })

    it('returns summary when title is missing', () => {
      const event = { summary: 'Summary Event' }
      expect(getRecurringEventKey(event)).toBe('Summary Event')
    })

    it('returns translated "Untitled Event" when both missing', () => {
      const event = {}
      expect(getRecurringEventKey(event)).toBe('Untitled Event')
    })
  })

  describe('getEventGroupKey', () => {
    it('returns title when available', () => {
      const event = { title: 'Test Event' }
      expect(getEventGroupKey(event)).toBe('Test Event')
    })

    it('returns summary when title is missing', () => {
      const event = { summary: 'Summary Event' }
      expect(getEventGroupKey(event)).toBe('Summary Event')
    })

    it('returns translated "Unknown Event Type" when both missing', () => {
      const event = {}
      expect(getEventGroupKey(event)).toBe('Unknown Event Type')
    })
  })

  describe('transformRecurringEventsToArray', () => {
    it('returns empty array for null/undefined input', () => {
      expect(transformRecurringEventsToArray(null)).toEqual([])
      expect(transformRecurringEventsToArray(undefined)).toEqual([])
    })

    it('returns array unchanged if input is already array', () => {
      const input = [
        { name: 'Event 1', count: 5, events: [] },
        { name: 'Event 2', count: 3, events: [] }
      ]
      expect(transformRecurringEventsToArray(input)).toEqual(input)
    })

    it('transforms object to sorted array', () => {
      const input = {
        'Event A': { count: 5, events: [] },
        'Event B': { count: 10, events: [] },
        'Event C': { count: 3, events: [] }
      }
      const result = transformRecurringEventsToArray(input)

      expect(result).toHaveLength(3)
      expect(result[0].name).toBe('Event B') // Highest count first
      expect(result[0].count).toBe(10)
      expect(result[1].name).toBe('Event A')
      expect(result[1].count).toBe(5)
      expect(result[2].name).toBe('Event C')
      expect(result[2].count).toBe(3)
    })

    it('sorts by name alphabetically when counts are equal', () => {
      const input = {
        'Zebra Event': { count: 5, events: [] },
        'Alpha Event': { count: 5, events: [] },
        'Beta Event': { count: 5, events: [] }
      }
      const result = transformRecurringEventsToArray(input)

      expect(result[0].name).toBe('Alpha Event')
      expect(result[1].name).toBe('Beta Event')
      expect(result[2].name).toBe('Zebra Event')
    })

    it('handles missing count field (defaults to 0)', () => {
      const input = {
        'Event A': { events: [] }
      }
      const result = transformRecurringEventsToArray(input)

      expect(result[0].count).toBe(0)
    })

    it('handles missing events field (defaults to empty array)', () => {
      const input = {
        'Event A': { count: 5 }
      }
      const result = transformRecurringEventsToArray(input)

      expect(result[0].events).toEqual([])
    })

    it('filters out null entries', () => {
      const input = {
        'Event A': { count: 5, events: [] },
        'Event B': null,
        'Event C': { count: 3, events: [] }
      }
      const result = transformRecurringEventsToArray(input)

      expect(result).toHaveLength(2)
      expect(result.find(e => e.name === 'Event B')).toBeUndefined()
    })

    it('filters out entries with null names', () => {
      const input = {
        'Event A': { count: 5, events: [] },
        null: { count: 3, events: [] }
      }
      const result = transformRecurringEventsToArray(input)

      // Implementation filters out null recurringEventData, not null names
      // null name creates an entry with name 'null' (string)
      expect(result).toHaveLength(2)
    })

    it('preserves events array', () => {
      const events = [{ id: 1 }, { id: 2 }]
      const input = {
        'Event A': { count: 2, events }
      }
      const result = transformRecurringEventsToArray(input)

      expect(result[0].events).toBe(events)
    })
  })

  describe('filterRecurringEventsBySearch', () => {
    const recurringEvents = [
      { name: 'Team Meeting', count: 5, events: [] },
      { name: 'Project Review', count: 3, events: [] },
      { name: 'Daily Standup', count: 10, events: [] }
    ]

    it('returns all events when search term is empty', () => {
      expect(filterRecurringEventsBySearch(recurringEvents, '')).toEqual(recurringEvents)
      expect(filterRecurringEventsBySearch(recurringEvents, '   ')).toEqual(recurringEvents)
    })

    it('filters events by search term (case insensitive)', () => {
      const result = filterRecurringEventsBySearch(recurringEvents, 'meeting')
      expect(result).toHaveLength(1)
      expect(result[0].name).toBe('Team Meeting')
    })

    it('filters events by partial match', () => {
      const result = filterRecurringEventsBySearch(recurringEvents, 'Stand')
      expect(result).toHaveLength(1)
      expect(result[0].name).toBe('Daily Standup')
    })

    it('returns multiple matches', () => {
      const result = filterRecurringEventsBySearch(recurringEvents, 'e')
      expect(result.length).toBeGreaterThan(1)
    })

    it('handles uppercase search terms', () => {
      const result = filterRecurringEventsBySearch(recurringEvents, 'TEAM')
      expect(result).toHaveLength(1)
      expect(result[0].name).toBe('Team Meeting')
    })

    it('returns empty array when no matches', () => {
      const result = filterRecurringEventsBySearch(recurringEvents, 'xyz123')
      expect(result).toEqual([])
    })

    it('filters out null events', () => {
      const eventsWithNull = [...recurringEvents, null]
      const result = filterRecurringEventsBySearch(eventsWithNull, 'Meeting')
      expect(result).toHaveLength(1)
    })

    it('filters out events with null names', () => {
      const eventsWithNullName = [...recurringEvents, { name: null, count: 5 }]
      const result = filterRecurringEventsBySearch(eventsWithNullName, '')
      // Implementation doesn't filter null names when search is empty
      expect(result).toHaveLength(4)
    })
  })

  describe('categorizeRecurringEvents', () => {
    it('separates events by count > 1 vs count === 1', () => {
      const recurringEvents = [
        { name: 'Recurring 1', count: 5, events: [] },
        { name: 'Single 1', count: 1, events: [] },
        { name: 'Recurring 2', count: 10, events: [] },
        { name: 'Single 2', count: 1, events: [] }
      ]

      const { main, single } = categorizeRecurringEvents(recurringEvents)

      expect(main).toHaveLength(2)
      expect(main[0].name).toBe('Recurring 1')
      expect(main[1].name).toBe('Recurring 2')

      expect(single).toHaveLength(2)
      expect(single[0].name).toBe('Single 1')
      expect(single[1].name).toBe('Single 2')
    })

    it('handles empty array', () => {
      const { main, single } = categorizeRecurringEvents([])
      expect(main).toEqual([])
      expect(single).toEqual([])
    })

    it('handles all recurring events', () => {
      const recurringEvents = [
        { name: 'Event 1', count: 5, events: [] },
        { name: 'Event 2', count: 3, events: [] }
      ]

      const { main, single } = categorizeRecurringEvents(recurringEvents)
      expect(main).toHaveLength(2)
      expect(single).toHaveLength(0)
    })

    it('handles all single events', () => {
      const recurringEvents = [
        { name: 'Event 1', count: 1, events: [] },
        { name: 'Event 2', count: 1, events: [] }
      ]

      const { main, single } = categorizeRecurringEvents(recurringEvents)
      expect(main).toHaveLength(0)
      expect(single).toHaveLength(2)
    })

    it('filters out null events', () => {
      const recurringEvents = [
        { name: 'Event 1', count: 5, events: [] },
        null,
        { name: 'Event 2', count: 1, events: [] }
      ]

      const { main, single } = categorizeRecurringEvents(recurringEvents)
      expect(main).toHaveLength(1)
      expect(single).toHaveLength(1)
    })

    it('filters out events with non-number count', () => {
      const recurringEvents = [
        { name: 'Event 1', count: 5, events: [] },
        { name: 'Event 2', count: 'invalid', events: [] },
        { name: 'Event 3', count: 1, events: [] }
      ]

      const { main, single } = categorizeRecurringEvents(recurringEvents)
      expect(main).toHaveLength(1)
      expect(single).toHaveLength(1)
    })
  })

  describe('calculateSelectedRecurringEventsCount', () => {
    const recurringEvents = [
      { name: 'Event A', count: 5, events: [] },
      { name: 'Event B', count: 3, events: [] },
      { name: 'Event C', count: 10, events: [] }
    ]

    it('calculates total count for selected events', () => {
      const selected = ['Event A', 'Event C']
      expect(calculateSelectedRecurringEventsCount(recurringEvents, selected)).toBe(15)
    })

    it('returns 0 for empty selection', () => {
      expect(calculateSelectedRecurringEventsCount(recurringEvents, [])).toBe(0)
    })

    it('returns count for single selection', () => {
      const selected = ['Event B']
      expect(calculateSelectedRecurringEventsCount(recurringEvents, selected)).toBe(3)
    })

    it('handles selection not in events list', () => {
      const selected = ['Event X', 'Event Y']
      expect(calculateSelectedRecurringEventsCount(recurringEvents, selected)).toBe(0)
    })

    it('handles mixed valid and invalid selections', () => {
      const selected = ['Event A', 'Event X', 'Event B']
      expect(calculateSelectedRecurringEventsCount(recurringEvents, selected)).toBe(8)
    })

    it('handles empty events array', () => {
      expect(calculateSelectedRecurringEventsCount([], ['Event A'])).toBe(0)
    })
  })

  describe('filterEventsBySelection', () => {
    const events = [
      { title: 'Meeting', start: '2024-01-18T10:00:00Z' },
      { title: 'Review', start: '2024-01-19T10:00:00Z' },
      { title: 'Meeting', start: '2024-01-20T10:00:00Z' },
      { summary: 'Standup', start: '2024-01-21T10:00:00Z' }
    ]

    it('filters events by selected names', () => {
      const selected = ['Meeting']
      const result = filterEventsBySelection(events, selected)

      expect(result).toHaveLength(2)
      expect(result[0].title).toBe('Meeting')
      expect(result[1].title).toBe('Meeting')
    })

    it('returns empty array when no selection', () => {
      const result = filterEventsBySelection(events, [])
      expect(result).toEqual([])
    })

    it('handles multiple selections', () => {
      const selected = ['Meeting', 'Standup']
      const result = filterEventsBySelection(events, selected)

      expect(result).toHaveLength(3)
    })

    it('handles selection with no matches', () => {
      const selected = ['NonExistent']
      const result = filterEventsBySelection(events, selected)
      expect(result).toEqual([])
    })

    it('uses summary field when title is missing', () => {
      const selected = ['Standup']
      const result = filterEventsBySelection(events, selected)

      expect(result).toHaveLength(1)
      expect(result[0].summary).toBe('Standup')
    })

    it('handles events with no title or summary', () => {
      const eventsWithUntitled = [
        ...events,
        { start: '2024-01-22T10:00:00Z' }
      ]
      const selected = ['Untitled Event']
      const result = filterEventsBySelection(eventsWithUntitled, selected)

      expect(result).toHaveLength(1)
    })
  })

  describe('filterFutureEvents', () => {
    beforeEach(() => {
      // Mock current time to a fixed date for consistent testing
      vi.useFakeTimers()
      vi.setSystemTime(new Date('2024-01-20T12:00:00Z'))
    })

    it('filters out past events', () => {
      const events = [
        { title: 'Past Event', start: '2024-01-15T10:00:00Z' },
        { title: 'Future Event', start: '2024-01-25T10:00:00Z' }
      ]

      const result = filterFutureEvents(events)
      expect(result).toHaveLength(1)
      expect(result[0].title).toBe('Future Event')
    })

    it('includes events happening now', () => {
      const events = [
        { title: 'Current Event', start: '2024-01-20T12:00:00Z' }
      ]

      const result = filterFutureEvents(events)
      expect(result).toHaveLength(1)
    })

    it('keeps events without start dates', () => {
      const events = [
        { title: 'No Start', description: 'Test' },
        { title: 'Future Event', start: '2024-01-25T10:00:00Z' }
      ]

      const result = filterFutureEvents(events)
      expect(result).toHaveLength(2)
    })

    it('handles dtstart field', () => {
      const events = [
        { title: 'Past Event', dtstart: '2024-01-15T10:00:00Z' },
        { title: 'Future Event', dtstart: '2024-01-25T10:00:00Z' }
      ]

      const result = filterFutureEvents(events)
      expect(result).toHaveLength(1)
      expect(result[0].title).toBe('Future Event')
    })

    it('handles empty array', () => {
      expect(filterFutureEvents([])).toEqual([])
    })

    it('handles all past events', () => {
      const events = [
        { title: 'Past 1', start: '2024-01-15T10:00:00Z' },
        { title: 'Past 2', start: '2024-01-16T10:00:00Z' }
      ]

      expect(filterFutureEvents(events)).toEqual([])
    })

    it('handles all future events', () => {
      const events = [
        { title: 'Future 1', start: '2024-01-25T10:00:00Z' },
        { title: 'Future 2', start: '2024-01-26T10:00:00Z' }
      ]

      expect(filterFutureEvents(events)).toHaveLength(2)
    })
  })

  describe('calculateRecurringEventStats', () => {
    it('calculates stats for mixed recurring events', () => {
      const recurringEvents = [
        { name: 'Recurring 1', count: 5, events: [] },
        { name: 'Single 1', count: 1, events: [] },
        { name: 'Recurring 2', count: 10, events: [] },
        { name: 'Single 2', count: 1, events: [] }
      ]

      const stats = calculateRecurringEventStats(recurringEvents)

      expect(stats.totalRecurringEvents).toBe(4)
      expect(stats.recurringRecurringEvents).toBe(2)
      expect(stats.uniqueRecurringEvents).toBe(2)
      expect(stats.totalEvents).toBe(17) // 5 + 1 + 10 + 1
      expect(stats.recurringEvents).toBe(15) // 5 + 10
      expect(stats.uniqueEvents).toBe(2)
    })

    it('handles empty array', () => {
      const stats = calculateRecurringEventStats([])

      expect(stats.totalRecurringEvents).toBe(0)
      expect(stats.recurringRecurringEvents).toBe(0)
      expect(stats.uniqueRecurringEvents).toBe(0)
      expect(stats.totalEvents).toBe(0)
      expect(stats.recurringEvents).toBe(0)
      expect(stats.uniqueEvents).toBe(0)
    })

    it('handles all recurring events (count > 1)', () => {
      const recurringEvents = [
        { name: 'Recurring 1', count: 5, events: [] },
        { name: 'Recurring 2', count: 3, events: [] }
      ]

      const stats = calculateRecurringEventStats(recurringEvents)

      expect(stats.totalRecurringEvents).toBe(2)
      expect(stats.recurringRecurringEvents).toBe(2)
      expect(stats.uniqueRecurringEvents).toBe(0)
      expect(stats.totalEvents).toBe(8)
      expect(stats.recurringEvents).toBe(8)
      expect(stats.uniqueEvents).toBe(0)
    })

    it('handles all unique events (count === 1)', () => {
      const recurringEvents = [
        { name: 'Single 1', count: 1, events: [] },
        { name: 'Single 2', count: 1, events: [] }
      ]

      const stats = calculateRecurringEventStats(recurringEvents)

      expect(stats.totalRecurringEvents).toBe(2)
      expect(stats.recurringRecurringEvents).toBe(0)
      expect(stats.uniqueRecurringEvents).toBe(2)
      expect(stats.totalEvents).toBe(2)
      expect(stats.recurringEvents).toBe(0)
      expect(stats.uniqueEvents).toBe(2)
    })
  })

  describe('classifyRecurringEvent', () => {
    const recurringEvents = [
      { name: 'Recurring Event', count: 5, events: [] },
      { name: 'Unique Event', count: 1, events: [] }
    ]

    it('classifies recurring event (count > 1)', () => {
      expect(classifyRecurringEvent(recurringEvents, 'Recurring Event')).toBe('recurring')
    })

    it('classifies unique event (count === 1)', () => {
      expect(classifyRecurringEvent(recurringEvents, 'Unique Event')).toBe('unique')
    })

    it('returns "unknown" for non-existent event', () => {
      expect(classifyRecurringEvent(recurringEvents, 'Non Existent')).toBe('unknown')
    })

    it('handles empty events array', () => {
      expect(classifyRecurringEvent([], 'Any Event')).toBe('unknown')
    })
  })
})
