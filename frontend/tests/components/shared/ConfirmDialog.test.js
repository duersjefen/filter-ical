/**
 * ConfirmDialog Component Mount Tests
 *
 * Tests that the component mounts without runtime errors.
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'

describe('ConfirmDialog - Mount Tests', () => {
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
    title: 'Confirm Action',
    message: 'Are you sure?',
    confirmText: 'Confirm',
    cancelText: 'Cancel'
  }

  it('mounts without runtime errors', () => {
    const wrapper = mount(ConfirmDialog, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders title and message', async () => {
    const wrapper = mount(ConfirmDialog, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    // Open dialog and wait for update
    await wrapper.vm.open()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Confirm Action')
    expect(wrapper.text()).toContain('Are you sure?')
  })

  it('renders confirm and cancel buttons', async () => {
    const wrapper = mount(ConfirmDialog, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    await wrapper.vm.open()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Confirm')
    expect(wrapper.text()).toContain('Cancel')
  })
})
