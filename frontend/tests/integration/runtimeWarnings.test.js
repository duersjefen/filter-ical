/**
 * Runtime warnings detection test
 * Demonstrates console monitoring system alongside Vue error handlers
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { assertNoRuntimeWarnings, getWarnings } from '../setup/consoleMonitor.js'

// Test component that expects a required prop
const TestComponent = defineComponent({
  name: 'TestComponent',
  props: {
    requiredProp: {
      type: String,
      required: true
    },
    typedProp: {
      type: Number,
      default: 0
    }
  },
  render() {
    return h('div', `${this.requiredProp} - ${this.typedProp}`)
  }
})

describe('Runtime Warnings Detection', () => {
  it('should fail test on critical Vue warnings via handler', () => {
    // Vue's warnHandler in vueErrorHandler.js catches critical prop warnings
    // and throws immediately before they reach console monitor

    // Type check failure is caught by Vue handler
    expect(() => {
      mount(TestComponent, {
        props: {
          requiredProp: 'test',
          typedProp: 'invalid-type' // Wrong type
        }
      })
    }).toThrow(/Vue warning caused test failure/)

    // The warning never reaches console.warn because the handler throws first
    const warnings = getWarnings()
    expect(warnings.length).toBe(0)
  })

  it('should pass when no warnings occur', () => {
    // Mount component with correct props
    mount(TestComponent, {
      props: {
        requiredProp: 'test',
        typedProp: 42
      }
    })

    // Should not throw - no warnings expected
    expect(() => assertNoRuntimeWarnings()).not.toThrow()
  })

  it('should capture non-critical console warnings', () => {
    // Test console.warn capture for non-Vue warnings
    console.warn('Custom warning message')
    console.warn('[intlify] translation missing: some.key')

    const warnings = getWarnings()
    expect(warnings).toContain('Custom warning message')
    expect(warnings.some(w => w.includes('[intlify]'))).toBe(true)
  })

  it('should reset warnings between tests', () => {
    // This test should start with clean slate
    const warnings = getWarnings()
    expect(warnings).toHaveLength(0)
  })
})
