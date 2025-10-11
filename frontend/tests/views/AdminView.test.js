/**
 * AdminView Component Mount Tests
 *
 * Tests that the view mounts without runtime errors.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import AdminView from '@/views/AdminView.vue'

// Mock the composables
vi.mock('@/composables/useAdmin', () => ({
  useAdmin: vi.fn(() => ({
    recurringEvents: [],
    groups: [],
    assignmentRules: [],
    loading: false,
    error: null,
    loadAllAdminData: vi.fn(),
    createGroup: vi.fn(),
    updateGroup: vi.fn(),
    addEventsToGroup: vi.fn(),
    bulkUnassignEvents: vi.fn(),
    createAssignmentRule: vi.fn(),
    deleteAssignmentRule: vi.fn(),
    applyExistingRule: vi.fn(),
    deleteGroup: vi.fn(),
    removeEventsFromGroup: vi.fn()
  }))
}))

vi.mock('@/composables/useHTTP', () => ({
  useHTTP: vi.fn(() => ({
    post: vi.fn(),
    get: vi.fn(),
    del: vi.fn(),
    rawRequest: vi.fn()
  }))
}))

vi.mock('@/composables/useMobileDetection', () => ({
  useMobileDetection: vi.fn(() => ({
    isMobile: false
  }))
}))

vi.mock('@/composables/useNotification', () => ({
  useNotification: vi.fn(() => ({
    success: vi.fn(),
    error: vi.fn()
  }))
}))

vi.mock('@/composables/useDomainAuth', () => ({
  useDomainAuth: vi.fn(() => ({
    isAdminAuthenticated: { value: true },
    getPasswordStatus: vi.fn(() => Promise.resolve({ admin_password_set: false })),
    checkAuth: vi.fn()
  }))
}))

describe('AdminView - Mount Tests', () => {
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
    domain: 'test-domain'
  }

  it('mounts without runtime errors', () => {
    const wrapper = mount(AdminView, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n],
        mocks: {
          $router: {
            push: vi.fn()
          }
        },
        stubs: {
          AppHeader: true,
          AutoRulesCard: true,
          EventManagementCard: true,
          BackupRestoreCard: true,
          PasswordSettingsCard: true,
          PasswordGate: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('validates domain prop', () => {
    const wrapper = mount(AdminView, {
      props: defaultProps,
      global: {
        plugins: [createPinia(), i18n],
        mocks: {
          $router: { push: vi.fn() }
        },
        stubs: {
          AppHeader: true,
          AutoRulesCard: true,
          EventManagementCard: true,
          BackupRestoreCard: true,
          PasswordSettingsCard: true,
          PasswordGate: true
        }
      }
    })

    expect(wrapper.props('domain')).toBe('test-domain')
  })
})
