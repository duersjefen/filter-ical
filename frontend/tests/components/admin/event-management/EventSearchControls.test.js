/**
 * EventSearchControls Component Mount Tests
 *
 * Tests that the component mounts without runtime errors.
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import EventSearchControls from '@/components/admin/event-management/EventSearchControls.vue'

describe('EventSearchControls - Mount Tests', () => {
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
    eventSearch: '',
    showSelectedOnly: false,
    selectedEvents: [],
    filteredEvents: [],
    activeGroupFilters: [],
    isAllEventsSelected: false,
    isSomeEventsSelected: false,
    hasHiddenSelectedEvents: false
  }

  it('mounts without runtime errors', () => {
    const wrapper = mount(EventSearchControls, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders search input', () => {
    const wrapper = mount(EventSearchControls, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
  })

  it('renders with search text', () => {
    const wrapper = mount(EventSearchControls, {
      props: {
        ...defaultProps,
        eventSearch: 'Team Meeting'
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.find('input').element.value).toBe('Team Meeting')
  })

  it('renders with selected events', () => {
    const wrapper = mount(EventSearchControls, {
      props: {
        ...defaultProps,
        selectedEvents: ['Event 1', 'Event 2'],
        filteredEvents: [
          { title: 'Event 1' },
          { title: 'Event 2' },
          { title: 'Event 3' }
        ]
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders show-selected-only indicator', () => {
    const wrapper = mount(EventSearchControls, {
      props: {
        ...defaultProps,
        showSelectedOnly: true,
        selectedEvents: ['Event 1', 'Event 2']
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('Showing only')
  })

  it('emits toggle-select-all event', async () => {
    const wrapper = mount(EventSearchControls, {
      props: {
        ...defaultProps,
        filteredEvents: [{ title: 'Event 1' }]
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    const selectButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Select')
    )
    await selectButton.trigger('click')

    expect(wrapper.emitted('toggle-select-all')).toBeTruthy()
  })
})
