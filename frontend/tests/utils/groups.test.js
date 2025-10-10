/**
 * Tests for groups utilities
 *
 * Following TDD principles from CLAUDE.md:
 * - Unit tests for pure functions
 * - 100% coverage requirement
 * - Test happy paths + edge cases + error cases
 */

import { describe, it, expect } from 'vitest'
import { isAutoGroup, hasCustomGroups, filterAutoGroups, countCustomGroups } from '../../src/utils/groups'

describe('groups', () => {
  describe('isAutoGroup', () => {
    it('returns true for group ID 9998', () => {
      expect(isAutoGroup(9998)).toBe(true)
    })

    it('returns true for group ID 9999', () => {
      expect(isAutoGroup(9999)).toBe(true)
    })

    it('returns true for IDs >= 9998', () => {
      expect(isAutoGroup(10000)).toBe(true)
      expect(isAutoGroup(10001)).toBe(true)
      expect(isAutoGroup(99999)).toBe(true)
    })

    it('returns false for group ID < 9998', () => {
      expect(isAutoGroup(9997)).toBe(false)
      expect(isAutoGroup(1000)).toBe(false)
      expect(isAutoGroup(1)).toBe(false)
      expect(isAutoGroup(0)).toBe(false)
    })

    it('handles string IDs', () => {
      expect(isAutoGroup('9998')).toBe(true)
      expect(isAutoGroup('9999')).toBe(true)
      expect(isAutoGroup('10000')).toBe(true)
      expect(isAutoGroup('100')).toBe(false)
    })

    it('handles negative numbers', () => {
      expect(isAutoGroup(-1)).toBe(false)
      expect(isAutoGroup(-9998)).toBe(false)
    })
  })

  describe('hasCustomGroups', () => {
    it('returns false for null/undefined input', () => {
      expect(hasCustomGroups(null)).toBe(false)
      expect(hasCustomGroups(undefined)).toBe(false)
    })

    it('returns true for array with custom groups', () => {
      const groups = [
        { id: 1, name: 'Custom Group 1' },
        { id: 2, name: 'Custom Group 2' }
      ]
      expect(hasCustomGroups(groups)).toBe(true)
    })

    it('returns false for array with only auto groups', () => {
      const groups = [
        { id: 9998, name: 'Other Recurring Events' },
        { id: 9999, name: 'Special Events' }
      ]
      expect(hasCustomGroups(groups)).toBe(false)
    })

    it('returns true for array with mixed groups', () => {
      const groups = [
        { id: 1, name: 'Custom Group' },
        { id: 9998, name: 'Auto Group' }
      ]
      expect(hasCustomGroups(groups)).toBe(true)
    })

    it('returns false for empty array', () => {
      expect(hasCustomGroups([])).toBe(false)
    })

    it('returns true for object with custom groups', () => {
      const groups = {
        '1': { id: 1, name: 'Custom Group 1' },
        '2': { id: 2, name: 'Custom Group 2' }
      }
      expect(hasCustomGroups(groups)).toBe(true)
    })

    it('returns false for object with only auto groups', () => {
      const groups = {
        '9998': { id: 9998, name: 'Other Recurring Events' },
        '9999': { id: 9999, name: 'Special Events' }
      }
      expect(hasCustomGroups(groups)).toBe(false)
    })

    it('returns true for object with mixed groups', () => {
      const groups = {
        '1': { id: 1, name: 'Custom Group' },
        '9998': { id: 9998, name: 'Auto Group' }
      }
      expect(hasCustomGroups(groups)).toBe(true)
    })

    it('returns false for empty object', () => {
      expect(hasCustomGroups({})).toBe(false)
    })

    it('handles string IDs in array', () => {
      const groups = [
        { id: '1', name: 'Custom Group' },
        { id: '9998', name: 'Auto Group' }
      ]
      expect(hasCustomGroups(groups)).toBe(true)
    })

    it('handles string IDs in object', () => {
      const groups = {
        '1': { id: '1', name: 'Custom Group' },
        '9998': { id: '9998', name: 'Auto Group' }
      }
      expect(hasCustomGroups(groups)).toBe(true)
    })
  })

  describe('filterAutoGroups', () => {
    it('returns input unchanged for null/undefined', () => {
      expect(filterAutoGroups(null)).toBeNull()
      expect(filterAutoGroups(undefined)).toBeUndefined()
    })

    it('filters auto groups from array', () => {
      const groups = [
        { id: 1, name: 'Custom Group 1' },
        { id: 9998, name: 'Auto Group 1' },
        { id: 2, name: 'Custom Group 2' },
        { id: 9999, name: 'Auto Group 2' }
      ]

      const result = filterAutoGroups(groups)

      expect(result).toHaveLength(2)
      expect(result[0].id).toBe(1)
      expect(result[1].id).toBe(2)
    })

    it('returns empty array when all groups are auto', () => {
      const groups = [
        { id: 9998, name: 'Auto Group 1' },
        { id: 9999, name: 'Auto Group 2' }
      ]

      expect(filterAutoGroups(groups)).toEqual([])
    })

    it('returns all groups when none are auto', () => {
      const groups = [
        { id: 1, name: 'Custom Group 1' },
        { id: 2, name: 'Custom Group 2' }
      ]

      const result = filterAutoGroups(groups)

      expect(result).toHaveLength(2)
      expect(result).toEqual(groups)
    })

    it('returns empty array for empty array input', () => {
      expect(filterAutoGroups([])).toEqual([])
    })

    it('filters auto groups from object', () => {
      const groups = {
        '1': { id: 1, name: 'Custom Group 1' },
        '9998': { id: 9998, name: 'Auto Group 1' },
        '2': { id: 2, name: 'Custom Group 2' },
        '9999': { id: 9999, name: 'Auto Group 2' }
      }

      const result = filterAutoGroups(groups)

      expect(Object.keys(result)).toHaveLength(2)
      expect(result['1']).toBeDefined()
      expect(result['2']).toBeDefined()
      expect(result['9998']).toBeUndefined()
      expect(result['9999']).toBeUndefined()
    })

    it('returns empty object when all groups are auto', () => {
      const groups = {
        '9998': { id: 9998, name: 'Auto Group 1' },
        '9999': { id: 9999, name: 'Auto Group 2' }
      }

      expect(filterAutoGroups(groups)).toEqual({})
    })

    it('returns all groups when none are auto (object)', () => {
      const groups = {
        '1': { id: 1, name: 'Custom Group 1' },
        '2': { id: 2, name: 'Custom Group 2' }
      }

      const result = filterAutoGroups(groups)

      expect(Object.keys(result)).toHaveLength(2)
      expect(result).toEqual(groups)
    })

    it('returns empty object for empty object input', () => {
      expect(filterAutoGroups({})).toEqual({})
    })

    it('handles string IDs in array', () => {
      const groups = [
        { id: '1', name: 'Custom Group' },
        { id: '9998', name: 'Auto Group' }
      ]

      const result = filterAutoGroups(groups)

      expect(result).toHaveLength(1)
      expect(result[0].id).toBe('1')
    })

    it('handles string IDs in object', () => {
      const groups = {
        '1': { id: '1', name: 'Custom Group' },
        '9998': { id: '9998', name: 'Auto Group' }
      }

      const result = filterAutoGroups(groups)

      expect(Object.keys(result)).toHaveLength(1)
      expect(result['1']).toBeDefined()
    })

    it('preserves object keys when filtering', () => {
      const groups = {
        'custom-1': { id: 1, name: 'Custom Group' },
        'auto-1': { id: 9998, name: 'Auto Group' }
      }

      const result = filterAutoGroups(groups)

      expect(result['custom-1']).toBeDefined()
      expect(result['auto-1']).toBeUndefined()
    })
  })

  describe('countCustomGroups', () => {
    it('returns 0 for null/undefined input', () => {
      expect(countCustomGroups(null)).toBe(0)
      expect(countCustomGroups(undefined)).toBe(0)
    })

    it('counts custom groups in array', () => {
      const groups = [
        { id: 1, name: 'Custom Group 1' },
        { id: 9998, name: 'Auto Group 1' },
        { id: 2, name: 'Custom Group 2' },
        { id: 9999, name: 'Auto Group 2' },
        { id: 3, name: 'Custom Group 3' }
      ]

      expect(countCustomGroups(groups)).toBe(3)
    })

    it('returns 0 for array with only auto groups', () => {
      const groups = [
        { id: 9998, name: 'Auto Group 1' },
        { id: 9999, name: 'Auto Group 2' }
      ]

      expect(countCustomGroups(groups)).toBe(0)
    })

    it('counts all groups when none are auto', () => {
      const groups = [
        { id: 1, name: 'Custom Group 1' },
        { id: 2, name: 'Custom Group 2' },
        { id: 3, name: 'Custom Group 3' }
      ]

      expect(countCustomGroups(groups)).toBe(3)
    })

    it('returns 0 for empty array', () => {
      expect(countCustomGroups([])).toBe(0)
    })

    it('counts custom groups in object', () => {
      const groups = {
        '1': { id: 1, name: 'Custom Group 1' },
        '9998': { id: 9998, name: 'Auto Group 1' },
        '2': { id: 2, name: 'Custom Group 2' },
        '9999': { id: 9999, name: 'Auto Group 2' },
        '3': { id: 3, name: 'Custom Group 3' }
      }

      expect(countCustomGroups(groups)).toBe(3)
    })

    it('returns 0 for object with only auto groups', () => {
      const groups = {
        '9998': { id: 9998, name: 'Auto Group 1' },
        '9999': { id: 9999, name: 'Auto Group 2' }
      }

      expect(countCustomGroups(groups)).toBe(0)
    })

    it('counts all groups when none are auto (object)', () => {
      const groups = {
        '1': { id: 1, name: 'Custom Group 1' },
        '2': { id: 2, name: 'Custom Group 2' },
        '3': { id: 3, name: 'Custom Group 3' }
      }

      expect(countCustomGroups(groups)).toBe(3)
    })

    it('returns 0 for empty object', () => {
      expect(countCustomGroups({})).toBe(0)
    })

    it('handles string IDs in array', () => {
      const groups = [
        { id: '1', name: 'Custom Group' },
        { id: '2', name: 'Custom Group' },
        { id: '9998', name: 'Auto Group' }
      ]

      expect(countCustomGroups(groups)).toBe(2)
    })

    it('handles string IDs in object', () => {
      const groups = {
        '1': { id: '1', name: 'Custom Group' },
        '2': { id: '2', name: 'Custom Group' },
        '9998': { id: '9998', name: 'Auto Group' }
      }

      expect(countCustomGroups(groups)).toBe(2)
    })

    it('counts single custom group', () => {
      const groups = [{ id: 1, name: 'Custom Group' }]
      expect(countCustomGroups(groups)).toBe(1)
    })

    it('counts single custom group in object', () => {
      const groups = { '1': { id: 1, name: 'Custom Group' } }
      expect(countCustomGroups(groups)).toBe(1)
    })
  })
})
