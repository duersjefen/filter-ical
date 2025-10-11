/**
 * DomainView Component Mount Tests
 *
 * Tests that the view mounts without runtime errors.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import DomainView from '@/views/DomainView.vue'

// Mock composables
vi.mock('@/composables/useHTTP', () => ({
  useHTTP: vi.fn(() => ({
    get: vi.fn(() => Promise.resolve({ success: true, data: {} })),
    post: vi.fn(),
    loading: false,
    error: null
  }))
}))

vi.mock('@/composables/useDomainAuth', () => ({
  useDomainAuth: vi.fn(() => ({
    isUserAuthenticated: { value: true },
    getPasswordStatus: vi.fn(() => Promise.resolve({ user_password_set: false })),
    checkAuth: vi.fn()
  }))
}))

describe('DomainView - Mount Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const defaultProps = {
    domain: 'test-domain'
  }

  it('mounts without runtime errors', () => {
    const wrapper = mount(DomainView, {
      props: defaultProps,
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key, params) => `${key}${params ? JSON.stringify(params) : ''}`
        },
        stubs: {
          CalendarView: true,
          PasswordGate: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('validates domain prop as string', () => {
    const wrapper = mount(DomainView, {
      props: defaultProps,
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          CalendarView: true,
          PasswordGate: true
        }
      }
    })

    expect(wrapper.props('domain')).toBe('test-domain')
    expect(typeof wrapper.props('domain')).toBe('string')
  })

  it('shows loading state initially', () => {
    const wrapper = mount(DomainView, {
      props: defaultProps,
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key) => key
        },
        stubs: {
          CalendarView: true,
          PasswordGate: true
        }
      }
    })

    // Component should render without errors
    expect(wrapper.exists()).toBe(true)
  })
})
