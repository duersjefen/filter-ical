/**
 * EventGroupsSection Component Mount Tests
 *
 * Tests that the component mounts without runtime errors.
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import EventGroupsSection from '@/components/calendar/EventGroupsSection.vue'

describe('EventGroupsSection - Mount Tests', () => {
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
    hasGroups: false,
    groups: {},
    domainId: 'default',
    showGroupsSection: true
  }

  it('mounts without runtime errors - no groups', () => {
    const wrapper = mount(EventGroupsSection, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          GroupsHeader: true,
          GroupsControlBar: true,
          GroupCard: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('mounts with groups', () => {
    const wrapper = mount(EventGroupsSection, {
      props: {
        ...defaultProps,
        hasGroups: true,
        groups: {
          1: {
            id: 1,
            name: 'Work',
            recurring_events: []
          },
          2: {
            id: 2,
            name: 'Personal',
            recurring_events: []
          }
        }
      },
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          GroupsHeader: true,
          GroupsControlBar: true,
          GroupCard: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('accepts domainId as string', () => {
    const wrapper = mount(EventGroupsSection, {
      props: {
        ...defaultProps,
        domainId: 'test-domain'
      },
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          GroupsHeader: true,
          GroupsControlBar: true,
          GroupCard: true
        }
      }
    })

    expect(wrapper.props('domainId')).toBe('test-domain')
    expect(typeof wrapper.props('domainId')).toBe('string')
  })

  it('mounts with section collapsed', () => {
    const wrapper = mount(EventGroupsSection, {
      props: {
        ...defaultProps,
        showGroupsSection: false
      },
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          GroupsHeader: true,
          GroupsControlBar: true,
          GroupCard: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})
