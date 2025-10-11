/**
 * AppHeader Component Mount Tests
 *
 * Tests that the component mounts without runtime errors.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import AppHeader from '@/components/shared/AppHeader.vue'

describe('AppHeader - Mount Tests', () => {
  let i18n

  beforeEach(() => {
    setActivePinia(createPinia())
    i18n = createI18n({
      legacy: false,
      locale: 'en',
      messages: {
        en: {
          username: { loginToSaveFilters: 'Login', logout: 'Logout' },
          darkMode: { switchToDark: 'Dark', switchToLight: 'Light' },
          language: { switch: 'EN' },
          common: { welcome: 'Welcome {username}' },
          navigation: { logout: 'Logout' },
          domainAdmin: { adminPanel: 'Admin' }
        }
      }
    })
  })

  const defaultProps = {
    title: 'Test Title',
    subtitle: 'Test Subtitle',
    backButtonText: 'Back',
    showBackButton: true,
    pageContext: 'calendar'
  }

  it('mounts without runtime errors', () => {
    const wrapper = mount(AppHeader, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders title and subtitle', () => {
    const wrapper = mount(AppHeader, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    expect(wrapper.text()).toContain('Test Title')
    expect(wrapper.text()).toContain('Test Subtitle')
  })

  it('renders back button when showBackButton is true', () => {
    const wrapper = mount(AppHeader, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    const backButton = wrapper.find('button[title="Back"]')
    expect(backButton.exists()).toBe(true)
  })

  it('hides back button when showBackButton is false', () => {
    const wrapper = mount(AppHeader, {
      props: {
        ...defaultProps,
        showBackButton: false
      },
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    const backButton = wrapper.find('button[title="Back"]')
    expect(backButton.exists()).toBe(false)
  })

  it('emits navigate-back event when back button clicked', async () => {
    const wrapper = mount(AppHeader, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n]
      }
    })

    const backButton = wrapper.find('button')
    await backButton.trigger('click')

    expect(wrapper.emitted('navigate-back')).toBeTruthy()
  })
})
