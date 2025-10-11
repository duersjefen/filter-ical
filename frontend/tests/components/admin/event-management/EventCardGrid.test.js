/**
 * EventCardGrid Component Mount Tests
 *
 * Tests that the component mounts without runtime errors.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import EventCardGrid from '@/components/admin/event-management/EventCardGrid.vue'

describe('EventCardGrid - Mount Tests', () => {
  let i18n

  beforeEach(() => {
    setActivePinia(createPinia())
    i18n = createI18n({
      legacy: false,
      locale: 'en',
      messages: { en: {} }
    })
  })

  const defaultProps = {
    filteredEvents: [],
    selectedEvents: [],
    dragSelection: {
      dragging: false,
      startX: 0,
      startY: 0,
      currentX: 0,
      currentY: 0
    },
    cardRefs: {},
    getGroupColorClasses: vi.fn(() => 'bg-blue-100 text-blue-800')
  }

  it('mounts without runtime errors', () => {
    const wrapper = mount(EventCardGrid, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders with no events', () => {
    const wrapper = mount(EventCardGrid, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('domainAdmin.noEventsFound')
  })

  it('renders with events', () => {
    const wrapper = mount(EventCardGrid, {
      props: {
        ...defaultProps,
        filteredEvents: [
          {
            title: 'Team Meeting',
            event_count: 5,
            assigned_groups: [{ id: 1, name: 'Work' }]
          },
          {
            title: 'Daily Standup',
            event_count: 3,
            assigned_groups: []
          }
        ]
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('Team Meeting')
    expect(wrapper.text()).toContain('Daily Standup')
  })

  it('renders with selected events', () => {
    const wrapper = mount(EventCardGrid, {
      props: {
        ...defaultProps,
        filteredEvents: [
          { title: 'Team Meeting', event_count: 5, assigned_groups: [] }
        ],
        selectedEvents: ['Team Meeting']
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders with drag selection active', () => {
    const wrapper = mount(EventCardGrid, {
      props: {
        ...defaultProps,
        filteredEvents: [
          { title: 'Team Meeting', event_count: 5, assigned_groups: [] }
        ],
        dragSelection: {
          dragging: true,
          startX: 10,
          startY: 10,
          currentX: 50,
          currentY: 50
        }
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('emits card-click event', async () => {
    const wrapper = mount(EventCardGrid, {
      props: {
        ...defaultProps,
        filteredEvents: [
          { title: 'Team Meeting', event_count: 5, assigned_groups: [] }
        ]
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    const card = wrapper.find('[data-event-card]')
    await card.trigger('click')

    expect(wrapper.emitted('card-click')).toBeTruthy()
  })
})
