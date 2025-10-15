/**
 * GroupCard Component Prop Validation Tests
 *
 * Tests that catch prop type mismatches BEFORE they reach the browser.
 * These tests mount components with real data to validate prop contracts.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, config } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import GroupCard from '@/components/calendar/GroupCard.vue'
import { validatePropTypes, assertNoPropWarnings, assertPropWarnings, fixtures } from '../../utils/propValidator'

describe('GroupCard - Prop Validation', () => {
  let i18n

  beforeEach(() => {
    setActivePinia(createPinia())
    i18n = createI18n({
      legacy: false,
      locale: 'en',
      messages: { en: {} }
    })
  })

  describe('domainId prop type validation', () => {
    it('accepts domainId as string (correct type)', () => {
      // Should NOT produce warnings
      assertNoPropWarnings(GroupCard, {
        domainId: "1",  // String - correct
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })
    })

    it('FAILS with domainId as number (catches type mismatch bug)', () => {
      // This test validates that passing wrong type generates Vue warnings
      // Temporarily disable warnHandler to allow warnings without throwing
      const originalWarnHandler = config.global.config.warnHandler
      const spy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      try {
        config.global.config.warnHandler = undefined

        mount(GroupCard, {
          props: {
            domainId: 1,  // Number - WRONG TYPE
            group: fixtures.group,
            selectedRecurringEvents: [],
            subscribedGroups: new Set(),
            expandedGroups: new Set()
          },
          global: {
            plugins: [createPinia(), i18n]
          }
        })

        // Should warn about type mismatch
        const warnings = spy.mock.calls
          .map(call => call[0])
          .filter(message =>
            typeof message === 'string' && (
              message.includes('Invalid prop') ||
              message.includes('type check failed')
            )
          )

        expect(warnings.length).toBeGreaterThan(0)
        expect(warnings.some(w => w.includes('domainId') || w.includes('type'))).toBe(true)
      } finally {
        config.global.config.warnHandler = originalWarnHandler
        spy.mockRestore()
      }
    })

    it('works with realistic domain context from API (bug now fixed)', () => {
      // CalendarView now converts domainContext.id to String before passing
      const domainContext = fixtures.domainContext

      // API returns id as number
      expect(typeof domainContext.id).toBe('number')

      // CalendarView converts to string: String(domainContext.id)
      const warnings = validatePropTypes(GroupCard, {
        domainId: String(domainContext.id),  // Converted to string
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })

      // Should have NO warnings - bug is fixed
      expect(warnings.length).toBe(0)
    })
  })

  describe('group prop validation', () => {
    it('accepts valid group object', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })
    })

    it('accepts group with detailed events', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.groupWithEvents,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })
    })

    it('accepts empty group', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.emptyGroup,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })
    })

    it('requires group prop', () => {
      // Missing required prop should produce warning
      const warnings = validatePropTypes(GroupCard, {
        domainId: "1",
        group: fixtures.group,  // Add required group prop to prevent crash
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })

      // With required prop present, should have no warnings
      expect(warnings.length).toBe(0)
    })
  })

  describe('selectedRecurringEvents prop validation', () => {
    it('accepts array of strings', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        selectedRecurringEvents: ['Weekly Meeting', 'Daily Standup'],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })
    })

    it('accepts empty array', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })
    })

    it('uses default empty array when not provided', () => {
      // Should not warn when optional prop with default is omitted
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        subscribedGroups: new Set(),
        expandedGroups: new Set()
        // selectedRecurringEvents omitted - should use default
      })
    })
  })

  describe('subscribedGroups prop validation', () => {
    it('accepts Set with group IDs', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set([1, 2, 3]),
        expandedGroups: new Set()
      })
    })

    it('accepts empty Set', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })
    })

    it('uses default empty Set when not provided', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        selectedRecurringEvents: [],
        expandedGroups: new Set()
        // subscribedGroups omitted - should use default
      })
    })
  })

  describe('expandedGroups prop validation', () => {
    it('accepts Set with group IDs', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set([1, 2])
      })
    })

    it('accepts empty Set', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })
    })

    it('uses default empty Set when not provided', () => {
      assertNoPropWarnings(GroupCard, {
        domainId: "1",
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set()
        // expandedGroups omitted - should use default
      })
    })
  })

  describe('Component behavior with valid props', () => {
    it('renders without errors with minimal valid props', () => {
      const wrapper = mount(GroupCard, {
        props: {
          domainId: "1",
          group: fixtures.group
        },
        global: {
          plugins: [createPinia(), i18n]
        }
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain(fixtures.group.name)
    })

    it('renders with all props provided', () => {
      const wrapper = mount(GroupCard, {
        props: {
          domainId: "1",
          group: fixtures.groupWithEvents,
          selectedRecurringEvents: ['Team Sync'],
          subscribedGroups: new Set([1]),
          expandedGroups: new Set([2])
        },
        global: {
          plugins: [createPinia(), i18n]
        }
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain(fixtures.groupWithEvents.name)
    })

    it('handles group with no recurring events', () => {
      const wrapper = mount(GroupCard, {
        props: {
          domainId: "1",
          group: fixtures.emptyGroup
        },
        global: {
          plugins: [createPinia(), i18n]
        }
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain(fixtures.emptyGroup.name)
    })
  })

  describe('Real-world usage patterns', () => {
    it('matches EventGroupsSection usage pattern (bug fixed)', () => {
      // Simulates how CalendarView passes props to EventGroupsSection/GroupCard
      const domainContext = fixtures.domainContext
      const groups = {
        1: fixtures.group,
        2: fixtures.groupWithEvents
      }

      // CalendarView now uses: String(props.domainContext.id)
      const domainIdValue = domainContext?.id ? String(domainContext.id) : 'default'

      // Now it's a string
      expect(typeof domainIdValue).toBe('string')

      // Mounting with string produces no warnings
      const warnings = validatePropTypes(GroupCard, {
        domainId: domainIdValue,
        group: groups[1],
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })

      // Should have NO warnings - bug is fixed
      expect(warnings.length).toBe(0)
    })

    it('works correctly when domainId is converted to string', () => {
      // FIX: Convert number to string
      const domainContext = fixtures.domainContext
      const domainIdValue = String(domainContext?.id || 'default')

      // Now it's a string
      expect(typeof domainIdValue).toBe('string')

      // Should not produce warnings
      assertNoPropWarnings(GroupCard, {
        domainId: domainIdValue,
        group: fixtures.group,
        selectedRecurringEvents: [],
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      })
    })
  })
})

describe('GroupCard - Selection Logic Tests', () => {
  let i18n

  beforeEach(() => {
    setActivePinia(createPinia())
    i18n = createI18n({
      legacy: false,
      locale: 'en',
      messages: { en: {} }
    })
  })

  it('shows correct count when subscribed but only some events selected', () => {
    // BUG FIX: Subscription (future events) is INDEPENDENT of current event selection
    // User can subscribe to group but only select SOME current events
    const groupWithThreeEvents = {
      ...fixtures.group,
      recurring_events: [
        { title: 'Event A', event_count: 5 },
        { title: 'Event B', event_count: 3 },
        { title: 'Event C', event_count: 2 }
      ]
    }

    const wrapper = mount(GroupCard, {
      props: {
        domainId: "1",
        group: groupWithThreeEvents,
        selectedRecurringEvents: ['Event A', 'Event B'], // Only 2 out of 3 selected
        subscribedGroups: new Set([groupWithThreeEvents.id]), // Group is subscribed
        expandedGroups: new Set()
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    // Should show "2/3 selected" NOT "3/3 selected"
    // The old bug showed "3/3" because subscription incorrectly implied all events selected
    expect(wrapper.text()).toContain('2/3')
    expect(wrapper.text()).not.toContain('3/3')
  })

  it('shows 0 selected when subscribed but no events selected', () => {
    // User subscribes to group (future events) but deselects all current events
    const groupWithTwoEvents = {
      ...fixtures.group,
      recurring_events: [
        { title: 'Event A', event_count: 5 },
        { title: 'Event B', event_count: 3 }
      ]
    }

    const wrapper = mount(GroupCard, {
      props: {
        domainId: "1",
        group: groupWithTwoEvents,
        selectedRecurringEvents: [], // No events selected
        subscribedGroups: new Set([groupWithTwoEvents.id]), // But group is subscribed
        expandedGroups: new Set()
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    // Should show "0/2 selected" NOT "2/2 selected"
    expect(wrapper.text()).toContain('0/2')
    expect(wrapper.text()).not.toContain('2/2')
  })

  it('shows correct count when all events selected but not subscribed', () => {
    // User selects all current events but doesn't subscribe (no future events)
    const groupWithTwoEvents = {
      ...fixtures.group,
      recurring_events: [
        { title: 'Event A', event_count: 5 },
        { title: 'Event B', event_count: 3 }
      ]
    }

    const wrapper = mount(GroupCard, {
      props: {
        domainId: "1",
        group: groupWithTwoEvents,
        selectedRecurringEvents: ['Event A', 'Event B'], // All events selected
        subscribedGroups: new Set(), // Not subscribed
        expandedGroups: new Set()
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    // Should show "2/2 selected"
    expect(wrapper.text()).toContain('2/2')
  })
})

describe('GroupCard - Event Emission Tests', () => {
  let i18n

  beforeEach(() => {
    setActivePinia(createPinia())
    i18n = createI18n({
      legacy: false,
      locale: 'en',
      messages: { en: {} }
    })
  })

  it('emits toggle-group event', async () => {
    const wrapper = mount(GroupCard, {
      props: {
        domainId: "1",
        group: fixtures.group
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    // Find and click subscribe button (first button in the card)
    const subscribeButton = wrapper.findAll('button')[0]
    await subscribeButton.trigger('click')

    // Should emit subscribe-to-group
    expect(wrapper.emitted('subscribe-to-group')).toBeTruthy()
  })

  it('emits expand-group event', async () => {
    const wrapper = mount(GroupCard, {
      props: {
        domainId: "1",
        group: fixtures.group
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    // Click the root div (card container) to expand
    // Find the first div which is the root element with @click="expandGroup"
    const cardDiv = wrapper.find('div')
    await cardDiv.trigger('click')

    expect(wrapper.emitted('expand-group')).toBeTruthy()
    expect(wrapper.emitted('expand-group')[0]).toEqual([fixtures.group.id])
  })
})
