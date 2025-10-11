/**
 * BulkAssignmentPanel Component Mount Tests
 *
 * Tests that the component mounts without runtime errors.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import BulkAssignmentPanel from '@/components/admin/event-management/BulkAssignmentPanel.vue'

describe('BulkAssignmentPanel - Mount Tests', () => {
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
    selectedEvents: [],
    recurringEvents: [],
    isUpdatingGroups: false,
    dragSelection: {
      dragging: false,
      startX: 0,
      startY: 0,
      currentX: 0,
      currentY: 0
    },
    getSmartGroupAction: vi.fn(() => ({
      type: 'single',
      primaryAction: 'add',
      primaryStyle: 'add',
      primaryLabel: 'Add to',
      primaryCount: 0
    })),
    isGroupUpdating: vi.fn(() => false)
  }

  it('mounts without runtime errors', () => {
    const wrapper = mount(BulkAssignmentPanel, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders with no selected events', () => {
    const wrapper = mount(BulkAssignmentPanel, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('Bulk Actions')
  })

  it('renders with selected events', () => {
    const wrapper = mount(BulkAssignmentPanel, {
      props: {
        ...defaultProps,
        selectedEvents: ['Event 1', 'Event 2'],
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

  it('renders unassign all button', () => {
    const wrapper = mount(BulkAssignmentPanel, {
      props: {
        ...defaultProps,
        selectedEvents: ['Event 1']
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('emits unassign-all event', async () => {
    const wrapper = mount(BulkAssignmentPanel, {
      props: {
        ...defaultProps,
        selectedEvents: ['Event 1']
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    const unassignButton = wrapper.findAll('button').find(btn =>
      btn.attributes('title')?.includes('Remove')
    )
    await unassignButton.trigger('click')

    expect(wrapper.emitted('unassign-all')).toBeTruthy()
  })

  it('renders with groups in updating state', () => {
    const isGroupUpdatingMock = vi.fn((groupId) => groupId === 1)

    const wrapper = mount(BulkAssignmentPanel, {
      props: {
        ...defaultProps,
        selectedEvents: ['Event 1'],
        groups: [{ id: 1, name: 'Work' }],
        isGroupUpdating: isGroupUpdatingMock
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})
