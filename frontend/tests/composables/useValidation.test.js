import { describe, it, expect } from 'vitest'
import { useValidation } from '../../src/composables/useValidation'

describe('useValidation', () => {
  const { isValidEmail, isValidPassword, isValidURL, isRequired, passwordsMatch } = useValidation()

  describe('isValidEmail', () => {
    it('validates correct email addresses', () => {
      expect(isValidEmail('user@example.com')).toBe(true)
      expect(isValidEmail('test.user@domain.co.uk')).toBe(true)
      expect(isValidEmail('user+tag@example.com')).toBe(true)
    })

    it('rejects invalid email addresses', () => {
      expect(isValidEmail('')).toBe(false)
      expect(isValidEmail('notanemail')).toBe(false)
      expect(isValidEmail('@example.com')).toBe(false)
      expect(isValidEmail('user@')).toBe(false)
      expect(isValidEmail('user@example')).toBe(false)
      expect(isValidEmail('user @example.com')).toBe(false)
    })

    it('handles null and undefined', () => {
      expect(isValidEmail(null)).toBe(false)
      expect(isValidEmail(undefined)).toBe(false)
    })

    it('handles whitespace', () => {
      expect(isValidEmail('  user@example.com  ')).toBe(true)
      expect(isValidEmail('   ')).toBe(false)
    })
  })

  describe('isValidPassword', () => {
    it('validates passwords meeting minimum length', () => {
      expect(isValidPassword('abcd')).toBe(true)
      expect(isValidPassword('12345')).toBe(true)
      expect(isValidPassword('LongPassword123')).toBe(true)
    })

    it('rejects passwords below minimum length', () => {
      expect(isValidPassword('')).toBe(false)
      expect(isValidPassword('abc')).toBe(false)
      expect(isValidPassword('12')).toBe(false)
    })

    it('supports custom minimum length', () => {
      expect(isValidPassword('12345678', 8)).toBe(true)
      expect(isValidPassword('1234567', 8)).toBe(false)
      expect(isValidPassword('short', 10)).toBe(false)
      expect(isValidPassword('longenough', 10)).toBe(true)
    })

    it('handles null and undefined', () => {
      expect(isValidPassword(null)).toBe(false)
      expect(isValidPassword(undefined)).toBe(false)
    })
  })

  describe('isValidURL', () => {
    it('validates correct URLs', () => {
      expect(isValidURL('https://example.com')).toBe(true)
      expect(isValidURL('http://example.com')).toBe(true)
      expect(isValidURL('https://example.com/path')).toBe(true)
      expect(isValidURL('https://example.com/path?query=param')).toBe(true)
    })

    it('rejects invalid URLs', () => {
      expect(isValidURL('')).toBe(false)
      expect(isValidURL('notaurl')).toBe(false)
      expect(isValidURL('example.com')).toBe(false)
      expect(isValidURL('//example.com')).toBe(false)
    })

    it('handles null and undefined', () => {
      expect(isValidURL(null)).toBe(false)
      expect(isValidURL(undefined)).toBe(false)
    })
  })

  describe('isRequired', () => {
    it('validates non-empty values', () => {
      expect(isRequired('value')).toBe(true)
      expect(isRequired('   text   ')).toBe(true)
      expect(isRequired(123)).toBe(true)
      expect(isRequired(true)).toBe(true)
      expect(isRequired(false)).toBe(true)
    })

    it('rejects empty values', () => {
      expect(isRequired('')).toBe(false)
      expect(isRequired('   ')).toBe(false)
      expect(isRequired(null)).toBe(false)
      expect(isRequired(undefined)).toBe(false)
    })
  })

  describe('passwordsMatch', () => {
    it('returns true when passwords match', () => {
      expect(passwordsMatch('password123', 'password123')).toBe(true)
      expect(passwordsMatch('', '')).toBe(true)
    })

    it('returns false when passwords do not match', () => {
      expect(passwordsMatch('password123', 'password456')).toBe(false)
      expect(passwordsMatch('abc', 'ABC')).toBe(false)
    })

    it('is case-sensitive', () => {
      expect(passwordsMatch('Password', 'password')).toBe(false)
    })
  })
})
