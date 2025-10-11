/**
 * Console monitoring for test environment
 * Captures and validates console warnings/errors during tests
 *
 * USAGE:
 *
 * Import utilities in your test:
 *   import { assertNoRuntimeWarnings, getWarnings } from '../setup/consoleMonitor.js'
 *
 * Check for warnings after test actions:
 *   assertNoRuntimeWarnings()  // Throws if Vue/i18n warnings detected
 *
 * Inspect collected warnings:
 *   const warnings = getWarnings()
 *   expect(warnings.some(w => w.includes('specific message'))).toBe(true)
 *
 * Note: Critical Vue warnings (prop validation, type errors) are caught by
 * vueErrorHandler.js BEFORE reaching console monitor - they throw immediately.
 */

const warnings = []
const errors = []

// Store original console methods
const originalWarn = console.warn
const originalError = console.error

// Patterns to match for warnings
const WARNING_PATTERNS = [
  '[Vue warn]',
  '[intlify]',
  'Invalid prop',
  'type check failed',
  'Missing required prop',
  'Failed prop type'
]

// Patterns to match for errors
const ERROR_PATTERNS = [
  '[Vue error]',
  'Uncaught',
  'TypeError',
  'ReferenceError'
]

// Override console.warn to capture warnings
console.warn = (...args) => {
  const message = args.join(' ')
  warnings.push(message)
  // Only log in non-CI environments for debugging
  if (!process.env.CI) {
    originalWarn(...args)
  }
}

// Override console.error to capture errors
console.error = (...args) => {
  const message = args.join(' ')
  errors.push(message)
  // Only log in non-CI environments for debugging
  if (!process.env.CI) {
    originalError(...args)
  }
}

/**
 * Reset warning/error collection before each test
 */
export function resetConsoleMonitor() {
  warnings.length = 0
  errors.length = 0
}

/**
 * Get all collected warnings
 */
export function getWarnings() {
  return [...warnings]
}

/**
 * Get all collected errors
 */
export function getErrors() {
  return [...errors]
}

/**
 * Assert that no runtime warnings occurred during test
 * Filters warnings to only include Vue/prop/i18n related warnings
 * @throws {Error} If relevant warnings were detected
 */
export function assertNoRuntimeWarnings() {
  const relevantWarnings = warnings.filter(w =>
    WARNING_PATTERNS.some(pattern => w.includes(pattern))
  )

  if (relevantWarnings.length > 0) {
    const formatted = relevantWarnings.map((w, i) => `  ${i + 1}. ${w}`).join('\n')
    throw new Error(`Runtime warnings detected:\n${formatted}`)
  }
}

/**
 * Assert that no runtime errors occurred during test
 * @throws {Error} If relevant errors were detected
 */
export function assertNoRuntimeErrors() {
  const relevantErrors = errors.filter(e =>
    ERROR_PATTERNS.some(pattern => e.includes(pattern))
  )

  if (relevantErrors.length > 0) {
    const formatted = relevantErrors.map((e, i) => `  ${i + 1}. ${e}`).join('\n')
    throw new Error(`Runtime errors detected:\n${formatted}`)
  }
}

/**
 * Assert that no warnings or errors occurred
 * @throws {Error} If any issues were detected
 */
export function assertNoRuntimeIssues() {
  assertNoRuntimeWarnings()
  assertNoRuntimeErrors()
}

// Auto-reset before each test
if (typeof beforeEach !== 'undefined') {
  beforeEach(() => {
    resetConsoleMonitor()
  })
}
