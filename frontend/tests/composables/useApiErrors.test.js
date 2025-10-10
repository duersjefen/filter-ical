import { describe, it, expect, vi } from 'vitest'
import { useApiErrors } from '../../src/composables/useApiErrors'

describe('useApiErrors', () => {
  describe('setError', () => {
    it('sets string errors', () => {
      const { error, setError } = useApiErrors()

      setError('Simple error message')

      expect(error.value).toBe('Simple error message')
    })

    it('extracts error from API response format', () => {
      const { error, setError } = useApiErrors()

      setError({
        response: {
          data: {
            detail: 'API error message'
          }
        }
      })

      expect(error.value).toBe('API error message')
    })

    it('extracts error from Error object', () => {
      const { error, setError } = useApiErrors()

      setError(new Error('Error object message'))

      expect(error.value).toBe('Error object message')
    })

    it('uses fallback message for unknown error types', () => {
      const { error, setError } = useApiErrors()

      setError({ unknown: 'format' })

      expect(error.value).toBe('An unknown error occurred')
    })

    it('clears error when passed null', () => {
      const { error, setError } = useApiErrors()

      setError('Initial error')
      expect(error.value).toBe('Initial error')

      setError(null)
      expect(error.value).toBeNull()
    })

    it('clears error when passed undefined', () => {
      const { error, setError } = useApiErrors()

      setError('Initial error')
      setError(undefined)

      expect(error.value).toBeNull()
    })
  })

  describe('hasError', () => {
    it('returns true when error exists', () => {
      const { hasError, setError } = useApiErrors()

      setError('Error message')

      expect(hasError.value).toBe(true)
    })

    it('returns false when no error exists', () => {
      const { hasError } = useApiErrors()

      expect(hasError.value).toBe(false)
    })

    it('updates reactively when error changes', () => {
      const { hasError, setError, clearError } = useApiErrors()

      expect(hasError.value).toBe(false)

      setError('Error')
      expect(hasError.value).toBe(true)

      clearError()
      expect(hasError.value).toBe(false)
    })
  })

  describe('clearError', () => {
    it('clears existing error', () => {
      const { error, setError, clearError } = useApiErrors()

      setError('Error message')
      expect(error.value).toBe('Error message')

      clearError()
      expect(error.value).toBeNull()
    })

    it('works when no error exists', () => {
      const { error, clearError } = useApiErrors()

      clearError()
      expect(error.value).toBeNull()
    })
  })

  describe('setCustomError', () => {
    it('sets custom error message', () => {
      const { error, setCustomError } = useApiErrors()

      setCustomError('Custom error message')

      expect(error.value).toBe('Custom error message')
    })

    it('overwrites existing error', () => {
      const { error, setError, setCustomError } = useApiErrors()

      setError('First error')
      setCustomError('Second error')

      expect(error.value).toBe('Second error')
    })
  })

  describe('withErrorHandling', () => {
    it('wraps successful function calls', async () => {
      const { error, withErrorHandling } = useApiErrors()
      const successFn = vi.fn().mockResolvedValue('success')

      const wrappedFn = withErrorHandling(successFn)
      const result = await wrappedFn('arg1', 'arg2')

      expect(result).toBe('success')
      expect(successFn).toHaveBeenCalledWith('arg1', 'arg2')
      expect(error.value).toBeNull()
    })

    it('captures and sets errors from failed function calls', async () => {
      const { error, withErrorHandling } = useApiErrors()
      const errorObj = new Error('Function failed')
      const failFn = vi.fn().mockRejectedValue(errorObj)

      const wrappedFn = withErrorHandling(failFn)

      await expect(wrappedFn()).rejects.toThrow('Function failed')
      expect(error.value).toBe('Function failed')
    })

    it('clears previous errors before execution', async () => {
      const { error, setError, withErrorHandling } = useApiErrors()
      const successFn = vi.fn().mockResolvedValue('success')

      setError('Previous error')
      expect(error.value).toBe('Previous error')

      const wrappedFn = withErrorHandling(successFn)
      await wrappedFn()

      expect(error.value).toBeNull()
    })

    it('handles multiple wrapped functions independently', async () => {
      const { error, withErrorHandling } = useApiErrors()
      const fn1 = vi.fn().mockResolvedValue('result1')
      const fn2 = vi.fn().mockRejectedValue(new Error('Error2'))

      const wrapped1 = withErrorHandling(fn1)
      const wrapped2 = withErrorHandling(fn2)

      await wrapped1()
      expect(error.value).toBeNull()

      await expect(wrapped2()).rejects.toThrow('Error2')
      expect(error.value).toBe('Error2')
    })
  })
})
