/**
 * Tests for useAdmin composable
 * 
 * Following TDD principles from CLAUDE.md:
 * - Unit tests for pure functions and business logic
 * - Contract tests for API interactions
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useAdmin } from '../../src/composables/useAdmin'

// Mock the useHTTP composable
vi.mock('../../src/composables/useHTTP', () => ({
  useHTTP: () => ({
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    del: vi.fn(),
    loading: ref(false),
    error: ref(null)
  })
}))

describe('useAdmin', () => {
  let admin
  const mockDomain = 'exter'

  beforeEach(() => {
    admin = useAdmin(mockDomain)
  })

  describe('Validation Functions (Pure Functions)', () => {
    it('validates group names correctly', () => {
      // Valid group name
      const validResult = admin.validateGroupName('Valid Group Name')
      expect(validResult.valid).toBe(true)

      // Empty name
      const emptyResult = admin.validateGroupName('')
      expect(emptyResult.valid).toBe(false)
      expect(emptyResult.error).toContain('required')

      // Null/undefined name
      const nullResult = admin.validateGroupName(null)
      expect(nullResult.valid).toBe(false)

      // Too long name
      const longName = 'a'.repeat(256)
      const longResult = admin.validateGroupName(longName)
      expect(longResult.valid).toBe(false)
      expect(longResult.error).toContain('255 characters')
    })

    it('validates assignment rules correctly', () => {
      // Valid rule
      const validResult = admin.validateAssignmentRule('title_contains', 'Meeting', 1)
      expect(validResult.valid).toBe(true)

      // Invalid rule type
      const invalidTypeResult = admin.validateAssignmentRule('invalid_type', 'Meeting', 1)
      expect(invalidTypeResult.valid).toBe(false)
      expect(invalidTypeResult.error).toContain('Rule type must be one of')

      // Empty rule value
      const emptyValueResult = admin.validateAssignmentRule('title_contains', '', 1)
      expect(emptyValueResult.valid).toBe(false)
      expect(emptyValueResult.error).toContain('Rule value is required')

      // Invalid target group ID
      const invalidGroupResult = admin.validateAssignmentRule('title_contains', 'Meeting', 0)
      expect(invalidGroupResult.valid).toBe(false)
      expect(invalidGroupResult.error).toContain('Valid target group')
    })
  })

  describe('Utility Functions', () => {
    it('formats rule type labels correctly', () => {
      expect(admin.getRuleTypeLabel('title_contains')).toBe('Title contains')
      expect(admin.getRuleTypeLabel('description_contains')).toBe('Description contains')
      expect(admin.getRuleTypeLabel('category_contains')).toBe('Category contains')
      expect(admin.getRuleTypeLabel('unknown_type')).toBe('unknown_type')
    })

    it('gets group names with fallback', () => {
      // Set up mock groups
      admin.groups.value = [
        { id: 1, name: 'Test Group 1' },
        { id: 2, name: 'Test Group 2' }
      ]

      expect(admin.getGroupName(1)).toBe('Test Group 1')
      expect(admin.getGroupName(999)).toBe('Group 999') // Fallback for non-existent group
    })
  })

  describe('Reactive State', () => {
    it('initializes with empty arrays', () => {
      expect(admin.groups.value).toEqual([])
      expect(admin.recurringEvents.value).toEqual([])
      expect(admin.assignmentRules.value).toEqual([])
    })

    it('computes groupsMap correctly', () => {
      admin.groups.value = [
        { id: 1, name: 'Group 1' },
        { id: 2, name: 'Group 2' }
      ]

      expect(admin.groupsMap.value).toEqual({
        1: { id: 1, name: 'Group 1' },
        2: { id: 2, name: 'Group 2' }
      })
    })

    it('filters available events correctly', () => {
      admin.recurringEvents.value = [
        { title: 'Event 1', event_count: 5 },
        { title: 'Event 2', event_count: 0 },
        { title: 'Event 3', event_count: 3 }
      ]

      expect(admin.availableEvents.value).toHaveLength(2)
      expect(admin.availableEvents.value[0].title).toBe('Event 1')
      expect(admin.availableEvents.value[1].title).toBe('Event 3')
    })
  })

  describe('API Integration Tests', () => {
    // Note: These would be expanded with proper mocking for full API testing
    it('provides all expected API functions', () => {
      expect(typeof admin.loadGroups).toBe('function')
      expect(typeof admin.createGroup).toBe('function')
      expect(typeof admin.updateGroup).toBe('function')
      expect(typeof admin.deleteGroup).toBe('function')
      expect(typeof admin.loadRecurringEvents).toBe('function')
      expect(typeof admin.assignEventsToGroup).toBe('function')
      expect(typeof admin.loadAssignmentRules).toBe('function')
      expect(typeof admin.createAssignmentRule).toBe('function')
      expect(typeof admin.deleteAssignmentRule).toBe('function')
      expect(typeof admin.loadAllAdminData).toBe('function')
    })
  })
})