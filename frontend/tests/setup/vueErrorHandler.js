/**
 * Vue Error Handler - Converts Vue warnings to test failures
 *
 * This handler catches Vue runtime warnings (prop validation, reactivity issues, etc.)
 * and converts them into test failures to prevent silent errors.
 */
import { config } from '@vue/test-utils'
import { beforeEach } from 'vitest'

// Store warnings for inspection
export const vueWarnings = []

// Install global Vue warning handler
config.global.config.warnHandler = (msg, vm, trace) => {
  vueWarnings.push({ msg, vm, trace })

  // Fail test immediately on critical Vue warnings
  const criticalPatterns = [
    'Invalid prop',
    'type check failed',
    'Missing required prop',
    'Hydration',
    'Slot default invoked outside',
    'Computed',
    'Extraneous non-props attributes'
  ]

  const isCritical = criticalPatterns.some(pattern =>
    msg.toLowerCase().includes(pattern.toLowerCase())
  )

  if (isCritical) {
    throw new Error(
      `Vue warning caused test failure:\n${msg}\n${trace || ''}`
    )
  }
}

// Install global Vue error handler
config.global.config.errorHandler = (err, vm, info) => {
  throw new Error(
    `Vue error in test:\n${err.message}\nInfo: ${info}`
  )
}

// Clear warnings before each test
beforeEach(() => {
  vueWarnings.length = 0
})
