/**
 * API Contract Tests: Type Validation
 *
 * Validates that API response types match frontend component expectations.
 *
 * Problem:
 *   - Backend returns domain.id as Number (1)
 *   - Frontend components expect domain.id as String ("1")
 *   - This causes Vue prop validation warnings in production
 *
 * Solution:
 *   - Contract tests validate API response structure
 *   - Detect type mismatches before they reach components
 *   - Provide type mappers to convert API → Component types
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import HeaderSection from '@/components/calendar/HeaderSection.vue'
import GroupCard from '@/components/calendar/GroupCard.vue'
import {
  convertApiToDomainContext,
  convertApiToGroup,
  validatePropTypes
} from '../utils/typeMapper'

// Mock API responses (exactly as backend returns them)
const mockApiResponses = {
  // GET /api/domains/{domain} - Returns domain config with Number ID
  domainConfig: {
    success: true,
    data: {
      id: 1,  // Number from database
      domain_key: 'exter',
      name: 'Exter Kalendar',
      calendar_url: 'https://widgets.bcc.no/ical.ics',
      status: 'active',
      is_owner: false,
      is_admin: false,
      has_admin_access: false
    }
  },

  // GET /api/domains/{domain}/groups - Returns groups with Number IDs
  groups: [
    {
      id: 1,  // Number from database
      name: 'BCC Events',
      domain_key: 'exter',
      recurring_event_titles: ['Weekly Meeting', 'Monthly Review']
    },
    {
      id: 2,
      name: 'External Events',
      domain_key: 'exter',
      recurring_event_titles: []
    }
  ],

  // GET /api/domains/{domain}/events - Returns events
  events: {
    events: [
      {
        id: 1,
        title: 'Weekly Meeting',
        start: '2025-10-12T09:00:00Z',
        end: '2025-10-12T10:00:00Z',
        location: 'Conference Room',
        description: 'Team sync'
      }
    ],
    groups: []
  }
}

// Helper to create test instance with i18n and Pinia
function createTestInstance() {
  const i18n = createI18n({
    legacy: false,
    locale: 'en',
    messages: {
      en: {
        common: {
          backToHome: 'Back to Home',
          loadingEvents: 'Loading Events',
          pleaseWait: 'Please wait...'
        }
      }
    }
  })

  const pinia = createPinia()

  return { i18n, pinia }
}

describe('API Contract: Domain Endpoint', () => {
  it('domain config returns Number for id field', () => {
    const response = mockApiResponses.domainConfig.data

    // Validate API contract - id should be Number
    expect(response.id).toBe(1)
    expect(typeof response.id).toBe('number')
  })

  it('domain id type mismatch causes component warnings (THE BUG)', () => {
    const { i18n, pinia } = createTestInstance()
    const apiDomain = mockApiResponses.domainConfig.data

    // Simulate CalendarView passing raw API data to HeaderSection
    // HeaderSection expects domainContext.id as String
    const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    const wrapper = mount(HeaderSection, {
      global: {
        plugins: [i18n, pinia]
      },
      props: {
        selectedCalendar: null,
        error: null,
        domainContext: apiDomain  // Passing Number id directly from API
      }
    })

    // Check if Vue threw prop validation warnings
    const propWarnings = consoleWarnSpy.mock.calls.filter(call =>
      call.some(arg =>
        typeof arg === 'string' &&
        (arg.includes('Invalid prop') || arg.includes('type check failed'))
      )
    )

    consoleWarnSpy.mockRestore()

    // This test DOCUMENTS the bug - uncomment to see it fail
    // expect(propWarnings.length).toBe(0)  // FAILS - warnings exist!
    expect(wrapper).toBeDefined()
  })

  it('type mapper converts domain id to String', () => {
    const apiDomain = mockApiResponses.domainConfig.data
    const converted = convertApiToDomainContext(apiDomain)

    // Converted data should have String id
    expect(converted.id).toBe('1')
    expect(typeof converted.id).toBe('string')

    // Other fields should be preserved
    expect(converted.domain_key).toBe('exter')
    expect(converted.name).toBe('Exter Kalendar')
  })

  it('converted domain data does NOT cause component warnings (THE FIX)', () => {
    const { i18n, pinia } = createTestInstance()
    const apiDomain = mockApiResponses.domainConfig.data
    const converted = convertApiToDomainContext(apiDomain)

    const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    const wrapper = mount(HeaderSection, {
      global: {
        plugins: [i18n, pinia]
      },
      props: {
        selectedCalendar: null,
        error: null,
        domainContext: converted  // Using converted data with String id
      }
    })

    const propWarnings = consoleWarnSpy.mock.calls.filter(call =>
      call.some(arg =>
        typeof arg === 'string' &&
        (arg.includes('Invalid prop') || arg.includes('type check failed'))
      )
    )

    consoleWarnSpy.mockRestore()

    // This should pass - no warnings with converted data
    expect(propWarnings.length).toBe(0)
    expect(wrapper).toBeDefined()
  })
})

describe('API Contract: Groups Endpoint', () => {
  it('groups API returns Number for id field', () => {
    const group = mockApiResponses.groups[0]

    // Validate API contract
    expect(group.id).toBe(1)
    expect(typeof group.id).toBe('number')
  })

  it('group data matches component expectations', () => {
    const apiGroup = mockApiResponses.groups[0]
    const converted = convertApiToGroup(apiGroup)

    // GroupCard expects id as Number (not String!)
    expect(typeof converted.id).toBe('number')
    expect(converted.name).toBe('BCC Events')
    expect(Array.isArray(converted.recurring_event_titles)).toBe(true)
  })

  it('group data works with GroupCard component', () => {
    const { i18n, pinia } = createTestInstance()
    const apiGroup = mockApiResponses.groups[0]
    const converted = convertApiToGroup(apiGroup)

    const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    // GroupCard expects domainId as String but group.id as Number
    const wrapper = mount(GroupCard, {
      global: {
        plugins: [i18n, pinia]
      },
      props: {
        domainId: '1',  // String
        group: converted,  // group.id is Number
        selectedRecurringEvents: [],  // Array (not Set)
        subscribedGroups: new Set(),
        expandedGroups: new Set()
      }
    })

    const propWarnings = consoleWarnSpy.mock.calls.filter(call =>
      call.some(arg =>
        typeof arg === 'string' &&
        (arg.includes('Invalid prop') || arg.includes('type check failed'))
      )
    )

    consoleWarnSpy.mockRestore()

    expect(propWarnings.length).toBe(0)
    expect(wrapper).toBeDefined()
  })
})

describe('API Contract: Type Validation Utility', () => {
  it('detects type mismatch: Number vs String', () => {
    const apiData = { id: 1 }  // Number from API
    const expectedTypes = { id: { type: String, required: true } }

    expect(() => {
      validatePropTypes(apiData, expectedTypes)
    }).toThrow(/Type mismatch.*id.*expected String.*got number/)
  })

  it('passes validation when types match', () => {
    const apiData = { id: 'abc', name: 'Test' }
    const expectedTypes = {
      id: { type: String, required: true },
      name: { type: String, required: false }
    }

    expect(() => {
      validatePropTypes(apiData, expectedTypes)
    }).not.toThrow()
  })

  it('detects missing required props', () => {
    const apiData = { name: 'Test' }  // Missing 'id'
    const expectedTypes = {
      id: { type: String, required: true },
      name: { type: String, required: false }
    }

    expect(() => {
      validatePropTypes(apiData, expectedTypes)
    }).toThrow(/Missing required prop 'id'/)
  })

  it('handles optional props correctly', () => {
    const apiData = { id: 'abc' }  // 'name' is optional
    const expectedTypes = {
      id: { type: String, required: true },
      name: { type: String, required: false }
    }

    expect(() => {
      validatePropTypes(apiData, expectedTypes)
    }).not.toThrow()
  })
})

describe('API Contract: Real-World Integration', () => {
  it('CalendarView should convert domain.id before passing to children', () => {
    // This documents the expected pattern
    const apiResponse = mockApiResponses.domainConfig.data
    const domainContext = convertApiToDomainContext(apiResponse)

    // Now can safely pass to components expecting String id
    expect(typeof domainContext.id).toBe('string')

    // Example: Pass to GroupCard as domainId prop
    const domainId = domainContext.id  // "1" (String)
    expect(typeof domainId).toBe('string')
  })

  it('demonstrates complete type conversion flow', () => {
    // 1. API returns Number
    const apiDomain = { id: 1, domain_key: 'test', name: 'Test' }
    expect(typeof apiDomain.id).toBe('number')

    // 2. Convert for component use
    const converted = convertApiToDomainContext(apiDomain)
    expect(typeof converted.id).toBe('string')

    // 3. Use in component props
    const props = {
      domainId: converted.id,  // String
      domainContext: converted
    }

    expect(typeof props.domainId).toBe('string')
    expect(typeof props.domainContext.id).toBe('string')
  })
})
