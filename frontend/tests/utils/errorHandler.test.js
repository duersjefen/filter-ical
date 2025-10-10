/**
 * Tests for errorHandler utilities
 *
 * Following TDD principles from CLAUDE.md:
 * - Unit tests for pure functions
 * - 100% coverage requirement
 * - Test happy paths + edge cases + error cases
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ErrorTypes, getErrorMessage, AppError, parseApiError, createRetryableAction } from '../../src/utils/errorHandler'

// Mock i18n
vi.mock('../../src/i18n', () => ({
  t: vi.fn((key) => {
    const translations = {
      'errors.networkError': 'Network error',
      'errors.validationError': 'Validation error',
      'errors.authenticationError': 'Authentication error',
      'errors.notFoundError': 'Not found error',
      'errors.serverError': 'Server error',
      'errors.calendarError': 'Calendar error',
      'errors.unknownError': 'Unknown error',
      'errors.invalidCalendarFormat': 'Invalid calendar format'
    }
    return translations[key] || key
  })
}))

describe('errorHandler', () => {
  describe('ErrorTypes', () => {
    it('exports all error types', () => {
      expect(ErrorTypes.NETWORK).toBe('network')
      expect(ErrorTypes.VALIDATION).toBe('validation')
      expect(ErrorTypes.AUTHENTICATION).toBe('auth')
      expect(ErrorTypes.NOT_FOUND).toBe('not_found')
      expect(ErrorTypes.SERVER).toBe('server')
      expect(ErrorTypes.CALENDAR).toBe('calendar')
      expect(ErrorTypes.UNKNOWN).toBe('unknown')
    })
  })

  describe('getErrorMessage', () => {
    it('returns network error message', () => {
      expect(getErrorMessage(ErrorTypes.NETWORK)).toBe('Network error')
    })

    it('returns validation error message', () => {
      expect(getErrorMessage(ErrorTypes.VALIDATION)).toBe('Validation error')
    })

    it('returns authentication error message', () => {
      expect(getErrorMessage(ErrorTypes.AUTHENTICATION)).toBe('Authentication error')
    })

    it('returns not found error message', () => {
      expect(getErrorMessage(ErrorTypes.NOT_FOUND)).toBe('Not found error')
    })

    it('returns server error message', () => {
      expect(getErrorMessage(ErrorTypes.SERVER)).toBe('Server error')
    })

    it('returns calendar error message', () => {
      expect(getErrorMessage(ErrorTypes.CALENDAR)).toBe('Calendar error')
    })

    it('returns unknown error message', () => {
      expect(getErrorMessage(ErrorTypes.UNKNOWN)).toBe('Unknown error')
    })

    it('returns unknown error message for invalid type', () => {
      expect(getErrorMessage('invalid_type')).toBe('Unknown error')
    })

    it('returns unknown error message for null type', () => {
      expect(getErrorMessage(null)).toBe('Unknown error')
    })
  })

  describe('AppError', () => {
    it('creates error with message and type', () => {
      const error = new AppError('Test error', ErrorTypes.VALIDATION)

      expect(error.message).toBe('Test error')
      expect(error.type).toBe(ErrorTypes.VALIDATION)
      expect(error.originalError).toBeNull()
      expect(error.timestamp).toBeDefined()
      expect(typeof error.timestamp).toBe('number')
    })

    it('defaults to UNKNOWN type when not specified', () => {
      const error = new AppError('Test error')

      expect(error.type).toBe(ErrorTypes.UNKNOWN)
    })

    it('stores original error when provided', () => {
      const originalError = new Error('Original')
      const error = new AppError('Test error', ErrorTypes.NETWORK, originalError)

      expect(error.originalError).toBe(originalError)
    })

    it('is instance of Error', () => {
      const error = new AppError('Test error')

      expect(error).toBeInstanceOf(Error)
      expect(error).toBeInstanceOf(AppError)
    })

    it('sets timestamp on creation', () => {
      const before = Date.now()
      const error = new AppError('Test error')
      const after = Date.now()

      expect(error.timestamp).toBeGreaterThanOrEqual(before)
      expect(error.timestamp).toBeLessThanOrEqual(after)
    })
  })

  describe('parseApiError', () => {
    it('parses network error (no response)', () => {
      const error = { message: 'Network failed' }
      const result = parseApiError(error)

      expect(result).toBeInstanceOf(AppError)
      expect(result.type).toBe(ErrorTypes.NETWORK)
      expect(result.message).toBe('Network error')
      expect(result.originalError).toBe(error)
    })

    it('parses 400 validation error', () => {
      const error = {
        response: {
          status: 400,
          data: { message: 'Invalid input' }
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.VALIDATION)
      expect(result.message).toBe('Invalid input')
      expect(result.originalError).toBe(error)
    })

    it('parses 400 validation error with default message', () => {
      const error = {
        response: {
          status: 400,
          data: {}
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.VALIDATION)
      expect(result.message).toBe('Validation error')
    })

    it('parses 401 authentication error', () => {
      const error = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.AUTHENTICATION)
      expect(result.message).toBe('Unauthorized')
    })

    it('parses 401 authentication error with default message', () => {
      const error = {
        response: {
          status: 401,
          data: {}
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.AUTHENTICATION)
      expect(result.message).toBe('Authentication error')
    })

    it('parses 403 forbidden error', () => {
      const error = {
        response: {
          status: 403,
          data: { message: 'Forbidden' }
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.AUTHENTICATION)
      expect(result.message).toBe('Forbidden')
    })

    it('parses 404 not found error', () => {
      const error = {
        response: {
          status: 404,
          data: { message: 'Resource not found' }
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.NOT_FOUND)
      expect(result.message).toBe('Resource not found')
    })

    it('parses 404 not found error with default message', () => {
      const error = {
        response: {
          status: 404,
          data: {}
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.NOT_FOUND)
      expect(result.message).toBe('Not found error')
    })

    it('parses 422 calendar error', () => {
      const error = {
        response: {
          status: 422,
          data: { message: 'Bad calendar format' }
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.CALENDAR)
      expect(result.message).toBe('Bad calendar format')
    })

    it('parses 422 calendar error with default message', () => {
      const error = {
        response: {
          status: 422,
          data: {}
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.CALENDAR)
      expect(result.message).toBe('Invalid calendar format')
    })

    it('parses 500 server error', () => {
      const error = {
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.SERVER)
      expect(result.message).toBe('Internal server error')
    })

    it('parses 500 server error with default message', () => {
      const error = {
        response: {
          status: 500,
          data: {}
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.SERVER)
      expect(result.message).toBe('Server error')
    })

    it('parses 502 bad gateway error', () => {
      const error = {
        response: {
          status: 502,
          data: { message: 'Bad gateway' }
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.SERVER)
      expect(result.message).toBe('Bad gateway')
    })

    it('parses 503 service unavailable error', () => {
      const error = {
        response: {
          status: 503,
          data: { message: 'Service unavailable' }
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.SERVER)
      expect(result.message).toBe('Service unavailable')
    })

    it('parses unknown status code as unknown error', () => {
      const error = {
        response: {
          status: 418, // I'm a teapot
          data: { message: 'Custom error' }
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.UNKNOWN)
      expect(result.message).toBe('Custom error')
    })

    it('parses unknown status with default message', () => {
      const error = {
        response: {
          status: 999,
          data: {}
        }
      }
      const result = parseApiError(error)

      expect(result.type).toBe(ErrorTypes.UNKNOWN)
      expect(result.message).toBe('Unknown error')
    })
  })

  describe('createRetryableAction', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    it('returns a function', () => {
      const action = vi.fn()
      const retryable = createRetryableAction(action)

      expect(typeof retryable).toBe('function')
    })

    it('succeeds on first attempt', async () => {
      const action = vi.fn().mockResolvedValue('success')
      const retryable = createRetryableAction(action)

      const result = await retryable('arg1', 'arg2')

      expect(result).toBe('success')
      expect(action).toHaveBeenCalledTimes(1)
      expect(action).toHaveBeenCalledWith('arg1', 'arg2')
    })

    it('retries on failure and eventually succeeds', async () => {
      const action = vi.fn()
        .mockRejectedValueOnce({ response: { status: 500, data: {} } })
        .mockRejectedValueOnce({ response: { status: 500, data: {} } })
        .mockResolvedValue('success')

      const retryable = createRetryableAction(action, 3, 100)

      const promise = retryable()

      // Fast-forward timers for retry delays
      await vi.advanceTimersByTimeAsync(100) // First retry
      await vi.advanceTimersByTimeAsync(200) // Second retry

      const result = await promise

      expect(result).toBe('success')
      expect(action).toHaveBeenCalledTimes(3)
    })

    it('throws after max retries', async () => {
      const action = vi.fn().mockRejectedValue({ response: { status: 500, data: {} } })
      const retryable = createRetryableAction(action, 3, 100)

      const promise = retryable().catch(err => err)

      // Fast-forward timers for all retry delays
      await vi.advanceTimersByTimeAsync(100)  // First retry
      await vi.advanceTimersByTimeAsync(200)  // Second retry
      await vi.advanceTimersByTimeAsync(300)  // Third retry

      const result = await promise
      expect(result).toBeInstanceOf(AppError)
      expect(action).toHaveBeenCalledTimes(3)
    })

    it('does not retry on authentication errors', async () => {
      const action = vi.fn().mockRejectedValue({ response: { status: 401, data: {} } })
      const retryable = createRetryableAction(action, 3, 100)

      await expect(retryable()).rejects.toBeInstanceOf(AppError)
      expect(action).toHaveBeenCalledTimes(1)
    })

    it('does not retry on validation errors', async () => {
      const action = vi.fn().mockRejectedValue({ response: { status: 400, data: {} } })
      const retryable = createRetryableAction(action, 3, 100)

      await expect(retryable()).rejects.toBeInstanceOf(AppError)
      expect(action).toHaveBeenCalledTimes(1)
    })

    it('uses default max retries of 3', async () => {
      const action = vi.fn().mockRejectedValue({ response: { status: 500, data: {} } })
      const retryable = createRetryableAction(action)

      const promise = retryable().catch(err => err)

      await vi.advanceTimersByTimeAsync(1000)
      await vi.advanceTimersByTimeAsync(2000)
      await vi.advanceTimersByTimeAsync(3000)

      const result = await promise
      expect(result).toBeInstanceOf(AppError)
      expect(action).toHaveBeenCalledTimes(3)
    })

    it('uses default delay of 1000ms', async () => {
      const action = vi.fn()
        .mockRejectedValueOnce({ response: { status: 500, data: {} } })
        .mockResolvedValue('success')

      const retryable = createRetryableAction(action)

      const promise = retryable()

      // First delay should be 1000ms * 1 = 1000ms
      await vi.advanceTimersByTimeAsync(1000)

      const result = await promise

      expect(result).toBe('success')
    })

    it('increases delay with each attempt', async () => {
      const action = vi.fn()
        .mockRejectedValueOnce({ response: { status: 500, data: {} } })
        .mockRejectedValueOnce({ response: { status: 500, data: {} } })
        .mockResolvedValue('success')

      const retryable = createRetryableAction(action, 3, 100)

      const promise = retryable()

      // First retry: delay = 100 * 1 = 100ms
      await vi.advanceTimersByTimeAsync(100)

      // Second retry: delay = 100 * 2 = 200ms
      await vi.advanceTimersByTimeAsync(200)

      const result = await promise

      expect(result).toBe('success')
      expect(action).toHaveBeenCalledTimes(3)
    })

    it('passes arguments to retried action', async () => {
      const action = vi.fn()
        .mockRejectedValueOnce({ response: { status: 500, data: {} } })
        .mockResolvedValue('success')

      const retryable = createRetryableAction(action, 3, 100)

      const promise = retryable('arg1', 'arg2', 'arg3')

      await vi.advanceTimersByTimeAsync(100)

      await promise

      expect(action).toHaveBeenCalledWith('arg1', 'arg2', 'arg3')
      expect(action).toHaveBeenCalledTimes(2)
    })

    it('throws last error after max retries', async () => {
      const action = vi.fn().mockRejectedValue({ response: { status: 500, data: { message: 'Server error' } } })
      const retryable = createRetryableAction(action, 2, 100)

      const promise = retryable().catch(err => err)

      await vi.advanceTimersByTimeAsync(100)
      await vi.advanceTimersByTimeAsync(200)

      const error = await promise
      expect(error).toBeInstanceOf(AppError)
      expect(error.type).toBe(ErrorTypes.SERVER)
    })
  })
})
