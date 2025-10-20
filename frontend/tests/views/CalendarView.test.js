/**
 * CalendarView Component Mount Tests
 *
 * Tests that the view mounts without runtime errors.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import CalendarView from '@/views/CalendarView.vue'

// Mock composables
vi.mock('@/composables/useHTTP', () => ({
  useHTTP: vi.fn(() => ({
    loading: false,
    error: null,
    clearError: vi.fn(),
    setError: vi.fn()
  }))
}))

vi.mock('@/composables/useCalendar', () => ({
  useCalendar: vi.fn(() => ({
    selectedRecurringEvents: { value: [] },
    expandedRecurringEvents: { value: new Set() },
    showSingleEvents: { value: false },
    showRecurringEventsSection: { value: true },
    showGroupsSection: { value: true },
    showSelectedOnly: { value: false },
    recurringEventSearch: { value: '' },
    recurringEventsSortedByCount: { value: [] },
    mainRecurringEvents: { value: [] },
    singleRecurringEvents: { value: [] },
    selectedRecurringEventsCount: { value: 0 },
    getRecurringEventKey: vi.fn(),
    formatDateTime: vi.fn(),
    formatDateRange: vi.fn(),
    toggleRecurringEvent: vi.fn(),
    toggleRecurringEventExpansion: vi.fn(),
    selectAllRecurringEvents: vi.fn(),
    clearAllRecurringEvents: vi.fn(),
    selectAllSingleEvents: vi.fn(),
    clearAllSingleEvents: vi.fn(),
    updateCalendarId: vi.fn()
  }))
}))

vi.mock('@/composables/useSelection', () => ({
  useSelection: vi.fn(() => ({
    subscribeToGroup: vi.fn(),
    unsubscribeFromGroup: vi.fn(),
    subscribedGroups: { value: new Set() },
    selectedRecurringEvents: { value: [] },
    toggleRecurringEvent: vi.fn(),
    selectRecurringEvents: vi.fn(),
    clearSelection: vi.fn(),
    subscribeAndSelectAllGroups: vi.fn(),
    selectAllGroups: vi.fn(),
    unsubscribeFromAllGroups: vi.fn(),
    getGroupBreakdownSummary: vi.fn(() => ''),
    loadFilterSelection: vi.fn()
  }))
}))

// Create a mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/calendar/:id', component: CalendarView }
  ]
})

describe('CalendarView - Mount Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const defaultProps = {
    id: '1',
    domainContext: null
  }

  it('mounts without runtime errors', async () => {
    const wrapper = mount(CalendarView, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), router],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          HeaderSection: true,
          EventGroupsSection: true,
          AdminSetupCard: true,
          RecurringEventsCardsSection: true,
          FilteredCalendarSection: true,
          PreviewEventsSection: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('accepts id prop as string', async () => {
    const wrapper = mount(CalendarView, {
      props: {
        ...defaultProps,
        id: '123'
      },
      global: {
        plugins: [createPinia(), router],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          HeaderSection: true,
          EventGroupsSection: true,
          AdminSetupCard: true,
          RecurringEventsCardsSection: true,
          FilteredCalendarSection: true,
          PreviewEventsSection: true
        }
      }
    })

    expect(wrapper.props('id')).toBe('123')
  })

  it('accepts domainContext as object', async () => {
    const domainContext = {
      id: 1,
      domain_key: 'test',
      name: 'Test Domain'
    }

    const wrapper = mount(CalendarView, {
      props: {
        ...defaultProps,
        domainContext
      },
      global: {
        plugins: [createPinia(), router],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          HeaderSection: true,
          EventGroupsSection: true,
          AdminSetupCard: true,
          RecurringEventsCardsSection: true,
          FilteredCalendarSection: true,
          PreviewEventsSection: true
        }
      }
    })

    expect(wrapper.props('domainContext')).toEqual(domainContext)
  })
})
