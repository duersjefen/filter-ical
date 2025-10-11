/**
 * Prop Validation Utility
 *
 * Provides utilities for testing Vue component prop type validation.
 * Catches prop type mismatches before they reach the browser.
 */
import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'

// Create a test i18n instance
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: {}
  },
  globalInjection: true
})

/**
 * Validates that mounting a component with given props produces specific warnings
 *
 * @param {Object} component - Vue component to test
 * @param {Object} props - Props to pass to component
 * @param {Object} options - Additional mount options (slots, global, etc.)
 * @returns {Array} Array of prop validation warning messages
 *
 * @example
 * const warnings = validatePropTypes(GroupCard, {
 *   domainId: 123,  // Wrong type - should be string
 *   group: { id: '1', name: 'Test' }
 * })
 * expect(warnings).toHaveLength(1)
 * expect(warnings[0]).toContain('Invalid prop')
 */
export function validatePropTypes(component, props, options = {}) {
  const spy = vi.spyOn(console, 'warn').mockImplementation(() => {})

  try {
    mount(component, {
      props,
      global: {
        plugins: [createPinia(), i18n],
        ...(options.global || {})
      },
      ...options
    })

    // Filter for Vue prop validation warnings
    const warnings = spy.mock.calls
      .map(call => call[0])
      .filter(message =>
        typeof message === 'string' && (
          message.includes('Invalid prop') ||
          message.includes('type check failed') ||
          message.includes('expected')
        )
      )

    return warnings
  } finally {
    spy.mockRestore()
  }
}

/**
 * Asserts that mounting a component with given props produces NO warnings
 *
 * @param {Object} component - Vue component to test
 * @param {Object} props - Props to pass to component
 * @param {Object} options - Additional mount options
 * @throws {Error} If any prop validation warnings are detected
 *
 * @example
 * // Should not throw
 * assertNoPropWarnings(GroupCard, {
 *   domainId: "123",  // Correct type
 *   group: { id: '1', name: 'Test' }
 * })
 */
export function assertNoPropWarnings(component, props, options = {}) {
  const warnings = validatePropTypes(component, props, options)

  if (warnings.length > 0) {
    throw new Error(
      `Expected no prop warnings but got ${warnings.length}:\n` +
      warnings.map((w, i) => `  ${i + 1}. ${w}`).join('\n')
    )
  }
}

/**
 * Asserts that mounting a component with given props produces expected warnings
 *
 * @param {Object} component - Vue component to test
 * @param {Object} props - Props to pass to component
 * @param {Array<string>} expectedSubstrings - Substrings that should appear in warnings
 * @param {Object} options - Additional mount options
 * @throws {Error} If expected warnings are not found
 *
 * @example
 * assertPropWarnings(GroupCard,
 *   { domainId: 123 },  // Wrong type
 *   ['domainId', 'String']
 * )
 */
export function assertPropWarnings(component, props, expectedSubstrings, options = {}) {
  const warnings = validatePropTypes(component, props, options)

  if (warnings.length === 0) {
    throw new Error(
      `Expected prop warnings containing [${expectedSubstrings.join(', ')}] but got no warnings`
    )
  }

  const allWarningsText = warnings.join('\n')
  const missingSubstrings = expectedSubstrings.filter(
    substring => !allWarningsText.includes(substring)
  )

  if (missingSubstrings.length > 0) {
    throw new Error(
      `Expected warnings to contain: [${missingSubstrings.join(', ')}]\n` +
      `But got warnings:\n${warnings.map((w, i) => `  ${i + 1}. ${w}`).join('\n')}`
    )
  }
}

/**
 * Creates realistic test data fixtures based on API response patterns
 */
export const fixtures = {
  /**
   * Domain context as returned by API (id is number)
   */
  domainContext: {
    id: 1,
    domain_key: 'exter',
    name: 'Exter Calendar',
    description: 'Test domain'
  },

  /**
   * Group as returned by API
   */
  group: {
    id: 1,
    name: 'Test Group',
    description: 'A test group',
    recurring_events: [
      {
        title: 'Weekly Meeting',
        event_count: 12,
        events: []
      },
      {
        title: 'Daily Standup',
        event_count: 30,
        events: []
      }
    ]
  },

  /**
   * Group with detailed events
   */
  groupWithEvents: {
    id: 2,
    name: 'Detailed Group',
    description: 'Group with event details',
    recurring_events: [
      {
        title: 'Team Sync',
        event_count: 5,
        events: [
          {
            id: 'evt-1',
            title: 'Team Sync',
            start: '2025-10-12T09:00:00Z',
            end: '2025-10-12T10:00:00Z',
            is_recurring: true,
            location: 'Conference Room A'
          },
          {
            id: 'evt-2',
            title: 'Team Sync',
            start: '2025-10-19T09:00:00Z',
            end: '2025-10-19T10:00:00Z',
            is_recurring: true,
            location: 'Conference Room A'
          }
        ]
      }
    ]
  },

  /**
   * Empty group
   */
  emptyGroup: {
    id: 3,
    name: 'Empty Group',
    description: 'No events',
    recurring_events: []
  }
}
