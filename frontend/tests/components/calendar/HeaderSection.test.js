/**
 * HeaderSection Component Mount Tests
 *
 * Tests that the component mounts without runtime errors.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import HeaderSection from '@/components/calendar/HeaderSection.vue'

describe('HeaderSection - Mount Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('mounts without runtime errors - no calendar selected', () => {
    const wrapper = mount(HeaderSection, {
      props: {
        selectedCalendar: null,
        error: null,
        domainContext: null
      },
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          AppHeader: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('mounts with calendar selected', () => {
    const wrapper = mount(HeaderSection, {
      props: {
        selectedCalendar: {
          id: 1,
          name: 'My Calendar',
          url: 'https://example.com/calendar.ics'
        },
        error: null,
        domainContext: null
      },
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          AppHeader: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('mounts with domain context', () => {
    const wrapper = mount(HeaderSection, {
      props: {
        selectedCalendar: {
          id: 'cal_domain_test',
          name: 'Domain Calendar'
        },
        error: null,
        domainContext: {
          id: 1,
          domain_key: 'test',
          name: 'Test Domain'
        }
      },
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          AppHeader: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('mounts with error', () => {
    const wrapper = mount(HeaderSection, {
      props: {
        selectedCalendar: null,
        error: 'Failed to load calendar',
        domainContext: null
      },
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          AppHeader: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('emits navigate-home event', async () => {
    const wrapper = mount(HeaderSection, {
      props: {
        selectedCalendar: null,
        error: null,
        domainContext: null
      },
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          AppHeader: {
            template: '<div><button @click="$emit(\'navigate-back\')">Back</button></div>'
          }
        }
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')

    expect(wrapper.emitted('navigate-home')).toBeTruthy()
  })
})
