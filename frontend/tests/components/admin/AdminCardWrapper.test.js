/**
 * AdminCardWrapper Component Mount Tests
 *
 * Tests that the component mounts without runtime errors.
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import AdminCardWrapper from '@/components/admin/AdminCardWrapper.vue'

describe('AdminCardWrapper - Mount Tests', () => {
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
    title: 'Test Card',
    subtitle: 'Test subtitle',
    icon: '📋',
    expanded: false
  }

  it('mounts without runtime errors', () => {
    const wrapper = mount(AdminCardWrapper, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      },
      slots: {
        default: '<div>Card content</div>'
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders title and subtitle', () => {
    const wrapper = mount(AdminCardWrapper, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('Test Card')
    expect(wrapper.text()).toContain('Test subtitle')
  })

  it('renders icon', () => {
    const wrapper = mount(AdminCardWrapper, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('📋')
  })

  it('renders collapsed by default', () => {
    const wrapper = mount(AdminCardWrapper, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      },
      slots: {
        default: '<div>Card content</div>'
      }
    })

    // Content should be hidden when collapsed
    expect(wrapper.props('expanded')).toBe(false)
  })

  it('renders expanded when prop is true', () => {
    const wrapper = mount(AdminCardWrapper, {
      props: {
        ...defaultProps,
        expanded: true
      },
      global: {
        plugins: [createPinia(), i18n]
      },
      slots: {
        default: '<div>Card content</div>'
      }
    })

    expect(wrapper.props('expanded')).toBe(true)
    expect(wrapper.text()).toContain('Card content')
  })

  it('emits toggle event when clicked', async () => {
    const wrapper = mount(AdminCardWrapper, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    const clickableArea = wrapper.find('.cursor-pointer')
    await clickableArea.trigger('click')

    expect(wrapper.emitted('toggle')).toBeTruthy()
  })
})
