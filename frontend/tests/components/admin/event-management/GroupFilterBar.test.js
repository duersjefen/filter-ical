/**
 * GroupFilterBar Component Mount Tests
 *
 * Tests that the component mounts without runtime errors.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import GroupFilterBar from '@/components/admin/event-management/GroupFilterBar.vue'

describe('GroupFilterBar - Mount Tests', () => {
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
    groups: [],
    activeGroupFilters: [],
    totalEventsCount: 0,
    unassignedEventsCount: 0,
    editingGroupId: null,
    editingGroupName: '',
    showAddGroupForm: false,
    newGroupName: '',
    getGroupEventCount: vi.fn(() => 0)
  }

  it('mounts without runtime errors', () => {
    const wrapper = mount(GroupFilterBar, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders all events button', () => {
    const wrapper = mount(GroupFilterBar, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('domainAdmin.allEvents')
  })

  it('renders unassigned button', () => {
    const wrapper = mount(GroupFilterBar, {
      props: {
        ...defaultProps,
        unassignedEventsCount: 5
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('domainAdmin.unassigned')
    expect(wrapper.text()).toContain('(5)')
  })

  it('renders group buttons', () => {
    const wrapper = mount(GroupFilterBar, {
      props: {
        ...defaultProps,
        groups: [
          { id: 1, name: 'Work' },
          { id: 2, name: 'Personal' }
        ]
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('Work')
    expect(wrapper.text()).toContain('Personal')
  })

  it('renders add group button', () => {
    const wrapper = mount(GroupFilterBar, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('controls.addGroup')
  })

  it('shows add group form when requested', () => {
    const wrapper = mount(GroupFilterBar, {
      props: {
        ...defaultProps,
        showAddGroupForm: true,
        newGroupName: 'New Group'
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('emits toggle-group-filter event', async () => {
    const wrapper = mount(GroupFilterBar, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    const allEventsButton = wrapper.findAll('button')[0]
    await allEventsButton.trigger('click')

    expect(wrapper.emitted('toggle-group-filter')).toBeTruthy()
  })
})
